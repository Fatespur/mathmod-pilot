#!/usr/bin/env python3
"""verify_reference_identity_online.py — PH2 H1: reference identity verification.

VERIFY; DO NOT INVENT.

Answers one question per bibliography entry: does a trusted online scholarly
source confirm that the cited identity (DOI / title / authors / year / venue) is
real and consistent? It NEVER rewrites references, deletes entries, or judges
whether a claim is supported by the literature (out of scope).

Relationship to frozen validate_references.py (F4): F4 keeps citation-graph
closure, duplicate keys/DOIs and syntax checks; this tool adds identity
authenticity on top and never relaxes F4 semantics.

Verdicts (honest-degradation semantics):
  ONLINE_VERIFIED            trusted primary source confirms identity chain
  ONLINE_VERIFIED_NO_DOI     unique high-confidence match found without DOI
  ONLINE_URL_VERIFIED        web_resource URL reachable + syntactically valid
  URL_REACHABLE_IDENTITY_UNVERIFIED
  URL_UNREACHABLE
  ONLINE_PARTIAL_MATCH       strong core identity with explainable deviations
  SOURCE_CONFLICT            primary sources disagree -> MANUAL_REVIEW_REQUIRED
  AMBIGUOUS_MATCH            multiple plausible candidates -> no auto-verify
  OFFLINE_STRUCTURALLY_VALID offline-only policy or nothing to verify online
  UNVERIFIED                 not found / not attempted (NOT_FOUND != FABRICATED)
  NETWORK_UNAVAILABLE        network problem (NEVER mapped to INVALID)
  REMOTE_RATE_LIMIT          HTTP 429 etc.
  SOURCE_ERROR               5xx / malformed response
  INVALID                    ONLY with positive counter-evidence (spec section 21)

Policies: OFFLINE | ONLINE_PREFERRED | ONLINE_STRICT (OPT-IN hardening profile;
frozen gates are untouched — this tool only produces reference_identity_result).

Sources priority: crossref > openalex > doiresolver (existence corroboration);
webcheck for web_resource entries; fixtures adapter for deterministic tests
(source_class=fixture, clearly labelled in provenance).
"""
import argparse, csv, hashlib, json, os, re, socket, sys, time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

# --------------------------------------------------------------------------
# constants
# --------------------------------------------------------------------------

POLICIES = ("OFFLINE", "ONLINE_PREFERRED", "ONLINE_STRICT")
VERDICTS = ("ONLINE_VERIFIED", "ONLINE_VERIFIED_NO_DOI", "ONLINE_URL_VERIFIED",
            "URL_REACHABLE_IDENTITY_UNVERIFIED", "URL_UNREACHABLE",
            "ONLINE_PARTIAL_MATCH", "SOURCE_CONFLICT", "AMBIGUOUS_MATCH",
            "OFFLINE_STRUCTURALLY_VALID", "UNVERIFIED", "NETWORK_UNAVAILABLE",
            "REMOTE_RATE_LIMIT", "SOURCE_ERROR", "INVALID")
REVIEW_REQUIRED = {"AMBIGUOUS_MATCH", "ONLINE_PARTIAL_MATCH", "SOURCE_CONFLICT"}

REF_TYPES = ("journal_article", "conference_paper", "book", "book_chapter",
             "standard", "report", "web_resource", "dataset", "software", "other")
DOI_TYPES = {"journal_article", "conference_paper"}
QUERYABLE_TYPES = DOI_TYPES | {"standard", "report", "book", "book_chapter"}

TITLE_BANDS = ((0.95, "TITLE_STRONG_MATCH"), (0.85, "TITLE_MATCH"),
               (0.70, "TITLE_PARTIAL_MATCH"), (-1.0, "TITLE_MISMATCH"))

UA_BASE = "CUMCM-PH2-ReferenceVerifier/1.0"
DEFAULT_TTL_DAYS = 30


def sha(b):
    return hashlib.sha256(b).hexdigest() if isinstance(b, bytes) else \
        hashlib.sha256(json.dumps(b, sort_keys=True, ensure_ascii=False)
                       .encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# normalization (spec sections 8-9, 11, 14)
# --------------------------------------------------------------------------

DOI_PREFIX_RE = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*|info:doi/)",
                           re.I)
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")


def normalize_doi(raw):
    """Canonical '10.suffix' form; None if not DOI-shaped after unwrapping."""
    if raw is None:
        return None, "NO_DOI"
    d = str(raw).strip()
    if not d:
        return None, "NO_DOI"
    d = DOI_PREFIX_RE.sub("", d.strip())
    d = urllib.parse.unquote(d).strip()
    d = re.sub(r"\s+", "", d)
    # case-normalize the directory part only (registrant code is case-insensitive)
    if "/" in d:
        head, tail = d.split("/", 1)
        d = head.lower() + "/" + tail
    if not DOI_RE.match(d):
        return None, "INVALID_DOI_SYNTAX"
    return d, "OK"


_WS_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s]")
_HYPH_RE = re.compile(r"[-‐‑‒–—―]+")


def normalize_title(t):
    if not t:
        return ""
    s = unicodedata.normalize("NFKD", str(t))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("&", "and").replace(" ", " ")
    import html
    s = html.unescape(s)
    s = _HYPH_RE.sub("-", s).lower()
    s = _PUNCT_RE.sub(" ", s.replace("-", " "))
    s = _WS_RE.sub(" ", s).strip()
    return s


def title_score(local, remote):
    a, b = normalize_title(local), normalize_title(remote)
    if not a or not b:
        return 0.0, "UNKNOWN"
    if a == b:
        return 1.0, "exact_normalized_match"
    import difflib
    seq = difflib.SequenceMatcher(None, a, b).ratio()
    ta, tb = set(a.split()), set(b.split())
    jac = len(ta & tb) / max(1, len(ta | tb))
    score = round(max(seq, 0.5 * seq + 0.5 * jac), 4)
    method = f"token_similarity(seq={seq:.3f},jaccard={jac:.3f})"
    return score, method


_INITIAL_OK = re.compile(r"^[A-Za-z]\.?$")


def parse_author(name):
    """Return (surname_lower, given_initials_set) tolerating common formats."""
    s = str(name).strip().rstrip(";,")
    if "," in s:                                   # "Ye, J." / "Ye, Jiahui"
        sur, given = s.split(",", 1)
    elif " " in s:                                 # natural order forms
        parts = s.split()
        tail_inits = []
        while len(parts) > 1 and len(parts[-1].rstrip(".")) == 1 \
                and parts[-1].isalpha():
            tail_inits.insert(0, parts.pop().rstrip("."))
        if tail_inits:
            # trailing initial run: "Kucsko G" / "Maurer P C"
            sur, given = " ".join(parts), " ".join(tail_inits)
        else:
            sur, given = parts[-1], " ".join(parts[:-1])   # "Jiahui Ye"
    else:
        sur, given = s, ""
    sur = unicodedata.normalize("NFKD", sur).lower()
    sur = "".join(c for c in sur if not unicodedata.combining(c))
    sur = _PUNCT_RE.sub("", _WS_RE.sub("", sur))
    inits = set()
    for tok in re.split(r"[\s\-]+", given.strip()):
        tok = tok.strip(".")
        if tok:
            inits.add(tok[0].lower())
    return sur, inits


def author_list(authors_field):
    """Accept list[str] | list[dict] | 'A; B' string -> ordered [(sur,inits)]."""
    out = []
    if isinstance(authors_field, dict):
        authors_field = authors_field.get("authors") or []
    if isinstance(authors_field, str):
        items = [x for x in re.split(r";|\band\b|&", authors_field) if x.strip()]
    elif isinstance(authors_field, list):
        items = []
        for a in authors_field:
            if isinstance(a, dict):
                nm = a.get("family") or a.get("name") or ""
                giv = (a.get("given") or "")
                if a.get("name") is None:
                    nm = " ".join(x for x in (giv, a.get("family") or "")
                                  if x) if False else (a.get("family") or nm)
                    # crossref style handled below via given/family directly
                    sur, inits = parse_author(a.get("family") or "")
                    for t in re.split(r"[\s\-]+", giv.strip()):
                        t = t.strip(".")
                        if t:
                            inits.add(t[0].lower())
                    out.append((sur, inits))
                    continue
                items.append(nm)
            else:
                items.append(str(a))
    else:
        items = []
    for it in items:
        if isinstance(it, tuple):
            out.append(it)
        else:
            out.append(parse_author(it))
    return out


def author_match(local_auth, remote_auth):
    """Identity-focused comparison (spec section 12):
    first-author surname+initials and LOCAL-list coverage of the remote set.
    Truncated local lists (et al. convention) are coverage, not mismatch."""
    la, ra = author_list(local_auth), author_list(remote_auth)
    detail = {"local_count": len(la), "remote_count": len(ra)}
    if not la or not ra:
        detail["status"] = "unknown"
        detail["reason"] = "AUTHOR_FIELD_ABSENT_ON_ONE_SIDE"
        return detail
    rmap = {s for s, _ in ra}
    lmap = {s for s, _ in la}
    matched_local = sum(1 for s, _ in la if s in rmap)
    covered_local = matched_local / max(1, len(la))
    overlap = matched_local / max(len(la), len(ra))
    first_surname_ok = la[0][0] == ra[0][0]
    first_init_ok = _set_compat(la[0][1], ra[0][1])
    detail.update({
        "first_author_surname_match": first_surname_ok,
        "first_author_initials_compatible": first_init_ok,
        "author_set_overlap": round(overlap, 3),
        "local_authors_covered_by_remote": round(covered_local, 3),
        "matched_surnames": matched_local,
        "truncation_detected": bool(first_surname_ok and len(la) < len(ra)
                                    and covered_local >= 0.99),
    })
    if first_surname_ok and first_init_ok and covered_local >= 0.99:
        status, reason = "match", "FIRST_AUTHOR_MATCH+AUTHOR_SET_MATCH"
    elif first_surname_ok and covered_local >= 0.5:
        status, reason = "partial", "FIRST_AUTHOR_MATCH+AUTHOR_PARTIAL_MATCH"
    elif not first_surname_ok and overlap >= 0.99:
        status, reason = "partial", ("AUTHOR_PARTIAL_MATCH"
                                     "(ordering/expression differs)")
    else:
        status, reason = "mismatch", "AUTHOR_MISMATCH"
    detail["status"], detail["reason"] = status, reason
    return detail


def _set_compat(a, b):
    if not a or not b:
        return True      # missing initials cannot contradict
    return bool(a & b)


def year_int(y):
    m = re.search(r"(19|20)\d{2}", str(y or ""))
    return int(m.group(0)) if m else None


def year_match(local_y, remote_y):
    ly, ry = year_int(local_y), year_int(remote_y)
    d = {"local": local_y, "remote": remote_y}
    if ly is None or ry is None:
        d.update(status="unknown", reason_code="YEAR_UNKNOWN")
        return d
    if ly == ry:
        d.update(status="match", delta=0, reason_code="YEAR_MATCH")
    elif abs(ly - ry) == 1:
        side = "local_earlier_online_first" if ly < ry else "local_later_print_year"
        d.update(status="variant", delta=ly - ry, reason_code="YEAR_VARIANT",
                 convention_note=side,
                 note="online-first vs print-year convention recorded (source side kept)")
    else:
        d.update(status="mismatch", delta=ly - ry, reason_code="YEAR_MISMATCH")
    return d


VENUE_ALIAS = [
    {"canonical": "journal of physical and chemical reference data",
     "aliases": ["j phys chem ref data", "j phys chem ref"]},
    {"canonical": "laser photonics reviews",
     "aliases": ["laser photon rev", "laser photonics rev", "lpr"]},
    {"canonical": "mathematics of computation",
     "aliases": ["math comput", "math of computation"]},
    {"canonical": "analytical chemistry", "aliases": ["anal chem"]},
    {"canonical": "journal of the american statistical association",
     "aliases": ["j am stat assoc", "jasa"]},
    {"canonical": "the annals of statistics", "aliases": ["ann stat", "annals of statistics"]},
    {"canonical": "ieee transactions on instrumentation and measurement",
     "aliases": ["ieee trans instrum meas", "ieee trans instrum measur"]},
    {"canonical": "biochemistry", "aliases": ["biochemistry us"]},
    {"canonical": "journal of biological chemistry", "aliases": ["j biol chem"]},
]


def normalize_venue(v):
    if not v:
        return ""
    s = unicodedata.normalize("NFKD", str(v))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("&", "and").replace("the ", " ")
    s = _PUNCT_RE.sub(" ", s)
    return _WS_RE.sub(" ", s).strip()


def venue_match(local_v, remote_v, local_issn=None, remote_issn=None):
    lv, rv = normalize_venue(local_v), normalize_venue(remote_v)
    d = {"local": local_v or "", "remote": remote_v or ""}
    if local_issn and remote_issn:
        li = re.sub(r"\D", "", str(local_issn))
        ri = re.sub(r"\D", "", str(remote_issn))
        if li and ri:
            d["issn_local"], d["issn_remote"] = li, ri
            if li == ri:
                d.update(status="alias_or_better", reason_code="VENUE_MATCH",
                         note="issn equality")
                return d
    if not lv or not rv:
        d.update(status="unknown", reason_code="VENUE_UNKNOWN")
        return d
    if lv == rv:
        d.update(status="match", reason_code="VENUE_MATCH")
        return d
    canon_a = {lv} | {normalize_venue(x) for x in _venue_alias_hits(lv)}
    if rv in canon_a or any(rv == normalize_venue(al) for al in _venue_alias_hits(rv)):
        d.update(status="alias", reason_code="VENUE_ALIAS_MATCH")
        return d
    sc, _ = title_score(lv, rv)
    if sc >= 0.85:
        d.update(status="alias", reason_code="VENUE_ALIAS_MATCH",
                 similarity=sc)
    else:
        d.update(status="mismatch", reason_code="VENUE_MISMATCH", similarity=sc)
    return d


def _venue_alias_hits(v):
    nv = normalize_venue(v)
    for grp in VENUE_ALIAS:
        names = {normalize_venue(grp["canonical"])} | {normalize_venue(a) for a in grp["aliases"]}
        if nv in names:
            return sorted(names)
    return []


# --------------------------------------------------------------------------
# HTTP layer with bounded retry / backoff / classified failures
# --------------------------------------------------------------------------

class HttpResult:
    def __init__(self, status=None, body=None, error=None):
        self.status, self.body, self.error = status, body, error


def http_get(url, timeout=12, retries=2, backoff=1.6, mailto=None):
    ua = UA_BASE + (f" (mailto:{mailto})" if mailto else "")
    delay = 1.0
    last_err = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return HttpResult(status=r.status, body=r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429,) or 500 <= e.code < 600:
                last_err = HttpResult(error=("REMOTE_RATE_LIMIT" if e.code == 429
                                             else "REMOTE_SOURCE_ERROR"),
                                      status=e.code)
                if attempt < retries:
                    time.sleep(delay); delay *= backoff
                continue
            if e.code == 404:
                return HttpResult(error="NOT_FOUND", status=404)
            return HttpResult(error="REMOTE_SOURCE_ERROR", status=e.code)
        except (urllib.error.URLError, socket.timeout, ConnectionError, OSError) as e:
            last_err = HttpResult(error=_classify_net_err(e), status=None)
            if attempt < retries:
                time.sleep(delay); delay *= backoff
            continue
    return last_err or HttpResult(error="NETWORK_UNAVAILABLE")


def _classify_net_err(e):
    msg = str(e).lower()
    if "timed out" in msg or isinstance(e, socket.timeout):
        return "NETWORK_TIMEOUT"
    if "getaddrinfo failed" in msg or "name or service not known" in msg or \
       "no address" in msg or "[errno -2]" in msg or "-3]" in msg:
        return "DNS_FAILURE"
    if "reset" in msg:
        return "CONNECTION_RESET"
    if "ssl" in msg:
        return "SSL_ERROR"
    return "NETWORK_UNAVAILABLE"


# --------------------------------------------------------------------------
# cache (spec sections 26-27)
# --------------------------------------------------------------------------

class Cache:
    def __init__(self, cache_dir, ttl_days=DEFAULT_TTL_DAYS):
        self.dir = cache_dir
        self.ttl_days = ttl_days
        os.makedirs(cache_dir, exist_ok=True)

    def _path(self, key):
        return os.path.join(self.dir, sha(key) + ".json")

    def get(self, key):
        p = self._path(key)
        if not os.path.exists(p):
            return None, "MISS"
        try:
            rec = json.load(open(p, encoding="utf-8"))
        except Exception:
            return None, "CORRUPT"
        age = time.time() - rec.get("stored_at_epoch", 0)
        if age > self.ttl_days * 86400:
            return rec, "STALE"
        return rec, "HIT"

    def put(self, key, payload):
        rec = {"cache_key": key, "stored_at_epoch": time.time(),
               "retrieved_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "metadata_hash": sha(payload.get("metadata") or {}),
               **payload}
        tmp = self._path(key) + ".tmp"
        json.dump(rec, open(tmp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        os.replace(tmp, self._path(key))


# --------------------------------------------------------------------------
# source adapters
# --------------------------------------------------------------------------

CROSSREF_FIELDS = ("title", "author", "issued", "container-title", "ISSN",
                   "volume", "issue", "page", "publisher", "type")


def crossref_metadata_from_message(m):
    year = None
    for k in ("published-print", "published-online", "issued", "created"):
        dp = (m.get(k) or {}).get("date-parts") or []
        if dp and dp[0]:
            year = dp[0][0]
            if k == "published-print":
                break
            if k == "issued":
                continue
            if year and k == "published-online" and not (m.get("published-print")):
                break
    return {
        "title": (m.get("title") or [""])[0],
        "authors": [{"given": a.get("given", ""), "family": a.get("family", "")}
                    for a in (m.get("author") or [])],
        "year": year,
        "venue": (m.get("container-title") or [""])[0],
        "issn": (m.get("ISSN") or [None])[0] if m.get("ISSN") else None,
        "publisher": m.get("publisher"),
        "volume": m.get("volume"), "issue": m.get("issue"), "page": m.get("page"),
        "source_type": m.get("type"),
    }


class CrossrefSource:
    name, source_class, priority = "crossref", "primary", 10

    def __init__(self, mailto=None):
        self.mailto = mailto

    def fetch_by_doi(self, doi_norm, cache):
        key = f"crossref|doi|{doi_norm.lower()}"
        rec, st = cache.get(key)
        if rec and st == "HIT":
            return {"ok": True, "metadata": rec.get("metadata"),
                    "from_cache": True, "cache_status": st,
                    "retrieved_at": rec.get("retrieved_at_utc")}
        url = f"https://api.crossref.org/works/{urllib.parse.quote(doi_norm)}"
        hr = http_get(url, mailto=self.mailto)
        if hr.error and hr.error != "NOT_FOUND":
            return {"ok": False, "error": hr.error, "http_status": hr.status,
                    "cache_status": st if rec else "MISS"}
        if hr.error == "NOT_FOUND":
            return {"ok": True, "metadata": None, "not_found": True,
                    "cache_status": "MISS"}
        try:
            m = json.loads(hr.body)["message"]
        except Exception:
            return {"ok": False, "error": "MALFORMED_RESPONSE",
                    "http_status": hr.status}
        meta = crossref_metadata_from_message(m)
        cache.put(key, {"source": self.name, "request_identity": url,
                        "metadata": meta})
        rec2, st2 = cache.get(key)
        return {"ok": True, "metadata": meta, "from_cache": False,
                "cache_status": "FRESH_WRITE",
                "retrieved_at": rec2.get("retrieved_at_utc")}

    def query(self, title, authors, year, cache, rows=3):
        q = f"{title} {year or ''}".strip()
        key = f"crossref|query|{sha(q)}"
        rec, st = cache.get(key)
        if rec and st == "HIT":
            return {"ok": True, "candidates": rec.get("candidates", []),
                    "from_cache": True, "cache_status": st}
        params = urllib.parse.urlencode(
            {"query.bibliographic": q, "rows": rows})
        url = f"https://api.crossref.org/works?{params}"
        hr = http_get(url, mailto=self.mailto)
        if hr.error:
            return {"ok": False, "error": hr.error, "http_status": hr.status,
                    "cache_status": st if rec else "MISS"}
        try:
            items = json.loads(hr.body)["message"]["items"]
        except Exception:
            return {"ok": False, "error": "MALFORMED_RESPONSE"}
        cands = [crossref_metadata_from_message(i) |
                 {"doi": i.get("DOI")} for i in items]
        cache.put(key, {"source": self.name, "request_identity": url,
                        "metadata": {}, "candidates": cands})
        return {"ok": True, "candidates": cands, "from_cache": False,
                "cache_status": "FRESH_WRITE"}


class OpenAlexSource:
    name, source_class, priority = "openalex", "primary_secondary", 20

    def __init__(self, mailto=None):
        self.mailto = mailto

    def fetch_by_doi(self, doi_norm, cache):
        key = f"openalex|doi|{doi_norm.lower()}"
        rec, st = cache.get(key)
        if rec and st == "HIT":
            return {"ok": True, "metadata": rec.get("metadata"),
                    "from_cache": True, "cache_status": st}
        url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi_norm)}"
        hr = http_get(url, mailto=self.mailto)
        if hr.error and hr.error != "NOT_FOUND":
            return {"ok": False, "error": hr.error, "http_status": hr.status}
        if hr.error == "NOT_FOUND":
            return {"ok": True, "metadata": None, "not_found": True}
        try:
            m = json.loads(hr.body)
        except Exception:
            return {"ok": False, "error": "MALFORMED_RESPONSE"}
        meta = {
            "title": m.get("title") or "",
            "authors": [{"given": (a.get("author") or {}).get("display_name", ""),
                         "family": (a.get("author") or {}).get("display_name", "")}
                        for a in (m.get("authorships") or [])],
            "year": m.get("publication_year"),
            "venue": (((m.get("primary_location") or {}).get("source") or {})
                      .get("display_name") or ""),
            "issn": ((((m.get("primary_location") or {}).get("source") or {})
                      .get("issn")) or [None])[0] if
                     ((m.get("primary_location") or {}).get("source") or {}).get("issn")
                     else None,
            "source_type": m.get("type"),
        }
        cache.put(key, {"source": self.name, "request_identity": url,
                        "metadata": meta})
        rec2, _ = cache.get(key)
        return {"ok": True, "metadata": meta, "from_cache": False,
                "cache_status": "FRESH_WRITE",
                "retrieved_at": rec2.get("retrieved_at_utc")}


class DoiResolverSource:
    """Existence corroboration only (no metadata)."""
    name, source_class, priority = "doiresolver", "secondary", 30

    def fetch_by_doi(self, doi_norm, cache):
        key = f"resolver|{doi_norm.lower()}"
        rec, st = cache.get(key)
        if rec and st == "HIT":
            return {"ok": True, "exists": rec.get("exists"), "from_cache": True}
        url = f"https://doi.org/{urllib.parse.quote(doi_norm)}"
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": UA_BASE})
        try:
            with urllib.request.urlopen(req, timeout=12) as r:
                exists = True
        except urllib.error.HTTPError as e:
            exists = e.code not in (404,)
            err = None if exists else "NOT_FOUND"
        except (urllib.error.URLError, socket.timeout, OSError) as e:
            return {"ok": False, "error": _classify_net_err(e)}
        else:
            err = None
        cache.put(key, {"source": self.name, "request_identity": url,
                        "metadata": {"exists": exists}})
        return {"ok": True, "exists": exists, "error": err, "from_cache": False}


class WebCheckSource:
    name, source_class, priority = "webcheck", "secondary", 30

    def check_url(self, url, timeout=12):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA_BASE},
                                         method="HEAD")
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return {"ok": True, "http_status": r.status}
        except urllib.error.HTTPError as e:
            if e.code in (403, 405, 501):   # HEAD often disallowed; try GET once
                try:
                    req2 = urllib.request.Request(
                        url, headers={"User-Agent": UA_BASE})
                    with urllib.request.urlopen(req2, timeout=timeout) as r2:
                        return {"ok": True, "http_status": r2.status}
                except urllib.error.HTTPError as e2:
                    if e2.code < 500:
                        return {"ok": True, "http_status": e2.code}
                    return {"ok": False, "error": "REMOTE_SOURCE_ERROR",
                            "http_status": e2.code}
                except (urllib.error.URLError, OSError) as e2:
                    return {"ok": False, "error": _classify_net_err(e2)}
            if e.code == 404:
                return {"ok": True, "http_status": 404}
            return {"ok": False, "error": "REMOTE_SOURCE_ERROR", "http_status": e.code}
        except (urllib.error.URLError, socket.timeout, OSError) as e:
            return {"ok": False, "error": _classify_net_err(e)}


class FixtureSource:
    """Deterministic curated-metadata adapter for tests/offline demos.
    source_class=fixture so provenance can never masquerade as live evidence."""
    name, source_class, priority = "fixtures", "fixture", 5

    def __init__(self, fixture_json):
        data = json.load(open(fixture_json, encoding="utf-8-sig"))
        self.by_doi = {normalize_doi(e["doi"])[0].lower(): e
                       for e in data.get("by_doi", []) if e.get("doi")}
        self.url_checks = data.get("url_checks", {})
        self.queries = data.get("query_index", [])

    def fetch_by_doi(self, doi_norm, cache):
        key = f"fixtures|doi|{(doi_norm or '').lower()}"
        rec, st = cache.get(key)
        if st == "HIT":
            return {"ok": True, "metadata": rec.get("metadata"),
                    "from_cache": True, "retrieved_at": rec.get("retrieved_at_utc")}
        e = self.by_doi.get((doi_norm or "").lower())
        if e is None:
            return {"ok": True, "not_found": True, "metadata": None}
        meta = {k: e.get(k) for k in ("title", "authors", "year", "venue",
                                      "issn", "publisher")}
        cache.put(key, {"source": self.name, "request_identity": f"fixture:{key}",
                        "metadata": meta})
        return {"ok": True, "metadata": meta, "from_cache": False,
                "cache_status": "FRESH_WRITE", "retrieved_at": "FIXTURE_SNAPSHOT"}

    def check_url(self, url):
        return self.url_checks.get(url) or {"ok": False, "error": "NOT_FOUND"}

    def query(self, title, authors, year, cache, rows=3):
        nt = normalize_title(title)
        hits = []
        for q in self.queries:
            sc, _ = title_score(nt, normalize_title(q.get("title", "")))
            if sc >= 0.70:
                hits.append((sc, q))
        hits.sort(reverse=True, key=lambda x: x[0])
        return {"ok": True,
                "candidates": [{**q, "_score": sc} for sc, q in hits[:rows]],
                "from_cache": False}


# --------------------------------------------------------------------------
# per-entry verification
# --------------------------------------------------------------------------

def infer_type(entry):
    t = (entry.get("type") or entry.get("reference_type") or "").strip().lower()
    aliases = {"journal": "journal_article", "article": "journal_article",
               "conference": "conference_paper", "inproceedings": "conference_paper",
               "web": "web_resource", "url": "web_resource",
               "standard": "standard", "report": "report", "book": "book"}
    if t in REF_TYPES:
        return t
    if t in aliases:
        return aliases[t]
    url = entry.get("url")
    if url and not entry.get("doi"):
        return "web_resource"
    return "journal_article" if entry.get("doi") else (
        "book" if str(entry.get("venue") or "").find("press") >= 0 else "other")


_TITLE_STOPWORDS = {"the", "a", "an", "of", "and", "for", "on", "in", "to",
                    "by", "with", "from", "its"}


def _content_token_diff(local_t, remote_t):
    """Exclusive content words on each side after normalization."""
    ta = set(normalize_title(local_t).split()) - _TITLE_STOPWORDS
    tb = set(normalize_title(remote_t).split()) - _TITLE_STOPWORDS
    return (ta - tb), (tb - ta)


def compare_fields(local, remote):
    tscore, method = title_score(local.get("title"), remote.get("title"))
    band = next(name for thr, name in TITLE_BANDS if tscore >= thr)
    # High similarity is NOT enough when single distinguishing words differ
    # ("Kendall's tau" vs "Spearman's rho" are different papers).
    d_local, d_remote = _content_token_diff(local.get("title"),
                                            remote.get("title"))
    content_diff = sorted(d_local | d_remote)
    if d_local and d_remote:                      # both sides exclusive words
        total = len(content_diff)
        if total >= 3:
            band = "TITLE_MISMATCH"
            tscore = min(tscore, 0.69)
        else:
            band = "TITLE_PARTIAL_MATCH"
            tscore = min(tscore, 0.84)
    title_d = {"local": local.get("title") or "", "remote": remote.get("title") or "",
               "score": tscore, "method": method, "reason_code": band,
               "content_token_diff": content_diff}
    auth_d = author_match(local.get("authors"), remote.get("authors"))
    year_d = year_match(local.get("year"), remote.get("year"))
    venue_d = venue_match(local.get("venue"), remote.get("venue"),
                          local.get("issn"), remote.get("issn"))
    return {"title": title_d, "authors": auth_d, "year": year_d, "venue": venue_d}


def assemble_verdict(fields, doi_resolved, doi_norm):
    """Core identity-chain logic (spec sections 19-23). Returns (verdict, codes)."""
    codes = []
    t, a, y, v = fields["title"], fields["authors"], fields["year"], fields["venue"]
    codes.append(t["reason_code"])
    if a.get("reason"):
        for piece in re.split(r"\+", a["reason"]):
            codes.append(piece.strip())
    else:
        codes.append({"match": "AUTHOR_SET_MATCH", "partial": "AUTHOR_PARTIAL_MATCH",
                      "mismatch": "AUTHOR_MISMATCH", "unknown": "AUTHOR_UNKNOWN"
                      }.get(a.get("status"), "AUTHOR_UNKNOWN"))
    codes.append(y.get("reason_code", "YEAR_UNKNOWN"))
    codes.append(v.get("reason_code", "VENUE_UNKNOWN"))

    strong_title = t["reason_code"] in ("TITLE_STRONG_MATCH",)
    ok_title = t["reason_code"] in ("TITLE_STRONG_MATCH", "TITLE_MATCH")
    part_title = t["reason_code"] == "TITLE_PARTIAL_MATCH"
    bad_title = t["reason_code"] == "TITLE_MISMATCH"

    auth_first_ok = a.get("first_author_surname_match")
    auth_mismatch = a.get("status") == "mismatch"
    auth_partial = a.get("status") == "partial"

    year_bad = y.get("status") == "mismatch"
    year_variant = y.get("status") == "variant"

    venue_bad = v.get("status") == "mismatch"

    # --- positive counter-evidence -> INVALID (spec section 21) -------------
    if doi_resolved and (bad_title or auth_mismatch):
        if bad_title and (auth_mismatch or not auth_first_ok):
            codes.append("DOI_IDENTITY_MISMATCH")
            return "INVALID", codes
        if bad_title:
            codes.append("DOI_IDENTITY_MISMATCH")
            return "INVALID", codes
    if doi_resolved and bad_title and not auth_first_ok:
        codes.append("DOI_IDENTITY_MISMATCH")
        return "INVALID", codes

    if not doi_resolved:
        return None, codes   # caller handles no-DOI paths

    # --- DOI resolved: chain decision ---------------------------------------
    core_ok = ok_title and auth_first_ok is not False and not auth_mismatch
    if strong_title and not auth_mismatch and not year_bad and not venue_bad:
        return ("ONLINE_VERIFIED" if not (auth_partial or year_variant or
                                          v.get("status") == "alias")
                else "ONLINE_PARTIAL_MATCH"), codes
    if ok_title and not auth_mismatch and not year_bad and not venue_bad:
        return "ONLINE_VERIFIED", codes
    if core_ok and (year_variant or v.get("status") == "alias"):
        return "ONLINE_PARTIAL_MATCH", codes
    if (ok_title or part_title) and not auth_mismatch and not year_bad:
        codes.append("ONLINE_PARTIAL_MATCH")
        return "ONLINE_PARTIAL_MATCH", codes
    if part_title and auth_partial:
        return "ONLINE_PARTIAL_MATCH", codes
    codes.append("DOI_RESOLVED_BUT_IDENTITY_INCOMPLETE")
    return "UNVERIFIED", codes


def dedupe(codes):
    seen, out = set(), []
    for c in codes:
        if c and c not in seen:
            seen.add(c); out.append(c)
    return out


def verify_entry(entry, sources, cache, policy, webchecker):
    eid = entry.get("key") or str(entry.get("id") or "?")
    res = {
        "citation_id": eid,
        "reference_type": infer_type(entry),
        "local": {k: entry.get(k) for k in
                  ("title", "authors", "year", "venue", "doi", "url", "issn")},
        "verification_source": [],
        "cache_status": [],
    }
    rtype = res["reference_type"]
    doi_raw = entry.get("doi")
    doi_norm, doi_status = normalize_doi(doi_raw)
    res["doi"] = doi_norm

    # ---- web_resource path -------------------------------------------------
    if rtype == "web_resource":
        url = entry.get("url") or ""
        if not re.match(r"^https?://\S+$", url or ""):
            res.update(verdict="URL_UNREACHABLE",
                       reason_codes=["URL_SYNTAX_INVALID"],
                       note="non-http(s) or malformed URL")
            return res
        fx = next((s for s in sources if s.name == "fixtures"), None)
        if fx is not None:
            chk_d = fx.check_url(url)
            chk = {"ok": chk_d.get("ok", False),
                   "http_status": chk_d.get("http_status"),
                   "error": chk_d.get("error")}
            src_name = "fixtures(webcheck)"
        else:
            chk = webchecker.check_url(url)
            src_name = "webcheck"
        res["verification_source"].append(
            {"source": src_name, "request_identity": url,
             "retrieved_at_utc": now_utc(), "http_status": chk.get("http_status")})
        res["cache_status"].append(chk.get("error") or f"HTTP_{chk.get('http_status')}")
        if chk.get("ok"):
            code = chk.get("http_status")
            if code and int(code) < 400:
                res.update(verdict="ONLINE_URL_VERIFIED",
                           reason_codes=["URL_REACHABLE"])
            elif code == 404:
                res.update(verdict="URL_UNREACHABLE", reason_codes=["URL_NOT_FOUND_404"])
            else:
                res.update(verdict="URL_REACHABLE_IDENTITY_UNVERIFIED",
                           reason_codes=["HTTP_STATUS_" + str(code)])
            res["field_matches"] = {}
            return res
        err = chk.get("error", "NETWORK_UNAVAILABLE")
        if err in ("NETWORK_TIMEOUT", "DNS_FAILURE", "CONNECTION_RESET",
                   "NETWORK_UNAVAILABLE", "SSL_ERROR"):
            res.update(verdict="NETWORK_UNAVAILABLE", reason_codes=[err])
        else:
            res.update(verdict="SOURCE_ERROR", reason_codes=[err])
        return res

    # ---- DOI-less non-web types --------------------------------------------
    if doi_status != "OK":
        codes = [doi_status]  # NO_DOI or INVALID_DOI_SYNTAX
        if doi_status == "INVALID_DOI_SYNTAX":
            # syntax error is objective structural fact; F4 already flags it.
            res.update(verdict="OFFLINE_STRUCTURALLY_VALID",
                       reason_codes=codes + ["DEGRADED_TO_OFFLINE_SEMANTICS"],
                       note="invalid DOI syntax handled by F4; identity unverifiable "
                            "online — not marked INVALID here without counter-evidence")
            return res

    # ---- ONLINE policy gates -----------------------------------------------
    all_sources = sorted(sources, key=lambda s: s.priority)  # fixtures first in tests
    net_allowed = policy != "OFFLINE" and bool(all_sources) and \
        os.environ.get("PH2_NO_NETWORK", "") != "1"

    if not net_allowed:
        res.update(verdict="OFFLINE_STRUCTURALLY_VALID",
                   reason_codes=(["POLICY_OFFLINE"] if policy == "OFFLINE"
                                 else ["NO_VERIFICATION_SOURCES_CONFIGURED"]),
                   field_matches={})
        return res

    # ---- DOI-based verification ---------------------------------------------
    if doi_norm:
        primary_meta = None
        primary_name = None
        resolver_exists = None
        errors = []
        metas = []          # [(source_name, meta)] for conflict detection
        for s in all_sources:
            if s.name == "doiresolver":
                rr = s.fetch_by_doi(doi_norm, cache)
                res["verification_source"].append(
                    prov(s, rr, request=f"https://doi.org/{doi_norm}"))
                res["cache_status"].append(rr.get("from_cache") and "HIT" or "FRESH")
                if rr.get("ok"):
                    resolver_exists = rr.get("exists")
                    if rr.get("error") == "NOT_FOUND":
                        pass
                else:
                    errors.append((s.name, rr.get("error")))
                continue
            rr = s.fetch_by_doi(doi_norm, cache)
            res["verification_source"].append(prov(s, rr))
            res["cache_status"].append(
                "HIT" if rr.get("from_cache") else
                ("MISS" if rr.get("not_found") else rr.get("cache_status", "FRESH")))
            if not rr.get("ok"):
                errors.append((s.name, rr.get("error")))
                continue
            if rr.get("not_found") or not rr.get("metadata"):
                continue
            metas.append((s.name, rr["metadata"]))
            if primary_meta is None:
                primary_meta, primary_name = rr["metadata"], s.name
        # network-level failures?
        hard_err = [e for e in errors if e[1] in
                    ("NETWORK_TIMEOUT", "DNS_FAILURE", "CONNECTION_RESET",
                     "NETWORK_UNAVAILABLE", "SSL_ERROR")]
        rate = [e for e in errors if e[1] == "REMOTE_RATE_LIMIT"]
        serr = [e for e in errors if e[1] in ("REMOTE_SOURCE_ERROR",
                                              "MALFORMED_RESPONSE")]
        if primary_meta is None:
            all_notfound = len(errors) == 0 or len(metas) == 0
            if hard_err and not metas:
                res.update(verdict="NETWORK_UNAVAILABLE",
                           reason_codes=dedupe([e[1] for e in hard_err]),
                           note="network failure honestly degraded — NOT INVALID")
            elif rate and not metas:
                res.update(verdict="REMOTE_RATE_LIMIT",
                           reason_codes=dedupe(["REMOTE_RATE_LIMIT"] +
                                               [e[1] for e in serr]))
            elif serr and not metas:
                res.update(verdict="SOURCE_ERROR",
                           reason_codes=dedupe([e[1] for e in serr]))
            else:
                codes = ["DOI_NOT_FOUND"]
                res.update(verdict="UNVERIFIED", reason_codes=codes,
                           manual_review_required=(policy == "ONLINE_STRICT"),
                           note="DOI not found at trusted sources — "
                                "NOT_FOUND is never mapped to FABRICATED/INVALID "
                                "without positive counter-evidence",
                           field_matches={})
            return res
        # source conflict detection on compared fields
        if len(metas) >= 2:
            conflict = detect_conflict([m for _, m in metas])
            fields = compare_fields(res["local"], primary_meta)
            res["field_matches"] = fields
            if conflict:
                res["conflict_fields"] = conflict
                res.update(verdict="SOURCE_CONFLICT",
                           reason_codes=dedupe(["SOURCE_CONFLICT"] +
                                               flat_reasons(fields)),
                           manual_review_required=True,
                           note="sources disagree; not auto-resolved (spec §31)")
                return res
        fields = compare_fields(res["local"], primary_meta)
        res["field_matches"] = fields
        verdict, codes2 = assemble_verdict(fields, True, doi_norm)
        if verdict == "ONLINE_VERIFIED" and len(metas) >= 2:
            codes2.append("SECONDARY_CORROBORATED")
            codes2.append("PRIMARY_SOURCE_VERIFIED")
        elif verdict == "ONLINE_VERIFIED":
            codes2.append("PRIMARY_SOURCE_VERIFIED")
        res.update(verdict=verdict, reason_codes=dedupe(codes2),
                   resolved_identity={"source": primary_name,
                                      **{k: primary_meta.get(k) for k in
                                         ("title", "authors", "year", "venue")}})
        return res

    # ---- no-DOI queryable types (spec section 16) ----------------------------
    if rtype in QUERYABLE_TYPES:
        queriers = [s for s in sources if hasattr(s, "query")]
        candidates = []
        used_src = None
        for s in sorted(queriers, key=lambda x: x.priority):
            qr = s.query(entry.get("title", ""), entry.get("authors"),
                         entry.get("year"), cache)
            res["verification_source"].append(
                {"source": s.name, "mode": "bibliographic_query",
                 "retrieved_at_utc": now_utc()})
            if not qr.get("ok"):
                err = qr.get("error", "NETWORK_UNAVAILABLE")
                if err in ("NETWORK_TIMEOUT", "DNS_FAILURE", "CONNECTION_RESET",
                           "NETWORK_UNAVAILABLE", "SSL_ERROR"):
                    res.update(verdict="NETWORK_UNAVAILABLE", reason_codes=[err],
                               note="honest degradation; NOT INVALID")
                    return res
                continue
            cands = qr.get("candidates") or []
            if cands:
                used_src = s.name
                candidates = cands
                break
        if not candidates:
            res.update(verdict="UNVERIFIED", reason_codes=["NO_DOI", "NO_TRUSTED_MATCH"],
                       note="no trusted record found; absence is not fabrication")
            return res
        scored = []
        for c in candidates:
            f = compare_fields({**res["local"], "doi": None}, c)
            scored.append((f["title"]["score"], c, f))
        scored.sort(reverse=True, key=lambda x: x[0])
        best_sc, best_c, best_f = scored[0]
        uniq_high = sum(1 for sc, _, _ in scored
                        if sc >= 0.85 and abs(sc - best_sc) < 0.05)
        res["field_matches"] = best_f
        res["resolved_identity"] = {"source": used_src,
                                    "doi": best_c.get("doi"),
                                    "title": best_c.get("title")}
        strong_chain = (best_f["title"]["reason_code"] in
                        ("TITLE_STRONG_MATCH", "TITLE_MATCH")) and \
            best_f["authors"].get("status") in ("match", "partial") and \
            best_f["year"].get("status") in ("match", "variant")
        if uniq_high > 1:
            res.update(verdict="AMBIGUOUS_MATCH",
                       reason_codes=dedupe(["NO_DOI", "AMBIGUOUS_RESULT"] +
                                           flat_reasons(best_f)),
                       manual_review_required=True,
                       candidates_considered=len(scored))
            return res
        if strong_chain:
            res.update(verdict="ONLINE_VERIFIED_NO_DOI",
                       reason_codes=dedupe(["NO_DOI"] + flat_reasons(best_f)))
        else:
            res.update(verdict="UNVERIFIED",
                       reason_codes=dedupe(["NO_DOI", "NO_CONFIDENT_MATCH"] +
                                           flat_reasons(best_f)),
                       manual_review_required=policy == "ONLINE_STRICT")
        return res

    # ---- standards / datasets / software / other without DOI ------------------
    res.update(verdict="OFFLINE_STRUCTURALLY_VALID",
               reason_codes=["NO_DOI", f"TYPE_{rtype.upper()}_NO_ONLINE_REQUIREMENT"],
               field_matches={},
               note="type not forced to DOI (spec §15)")
    return res


def prov(source, result, request=None):
    p = {"source": source.name, "source_class": source.source_class,
         "retrieved_at_utc": result.get("retrieved_at") or now_utc(),
         "request_identity": request or result.get("request_identity") or "",
         "metadata_hash": sha(result.get("metadata") or {})}
    if result.get("http_status") is not None:
        p["http_status"] = result.get("http_status")
    return p


def detect_conflict(metas):
    """Return list of differing fields when >=2 primary sources disagree."""
    diffs = []
    base = metas[0]
    for other in metas[1:]:
        for f in ("title", "year"):
            if base.get(f) and other.get(f):
                if f == "title":
                    sc, _ = title_score(base[f], other[f])
                    if sc < 0.85:
                        diffs.append(f"{f}: {base[f][:40]!r} vs {other[f][:40]!r}")
                elif year_int(base[f]) != year_int(other[f]):
                    diffs.append(f"{f}: {base[f]} vs {other[f]}")
    return diffs


def flat_reasons(fields):
    out = []
    for d in fields.values():
        rc = d.get("reason_code") or d.get("reason")
        if rc:
            out.extend(re.split(r"\+", str(rc)))
    return [c.strip() for c in out]


def now_utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# --------------------------------------------------------------------------
# aggregate profile (spec section 34) — non-breaking new layer
# --------------------------------------------------------------------------

OFFLINE_STATUS_MAP = {"ONLINE_VERIFIED": "GRAPH_VALID+IDENTITY_VERIFIED",
                      "ONLINE_VERIFIED_NO_DOI": "GRAPH_VALID+IDENTITY_VERIFIED_NO_DOI",
                      "ONLINE_URL_VERIFIED": "GRAPH_VALID+URL_VERIFIED",
                      "ONLINE_PARTIAL_MATCH": "GRAPH_VALID+PARTIAL_IDENTITY",
                      "AMBIGUOUS_MATCH": "GRAPH_VALID+MANUAL_REVIEW",
                      "SOURCE_CONFLICT": "GRAPH_VALID+MANUAL_REVIEW",
                      "OFFLINE_STRUCTURALLY_VALID": "GRAPH_VALID+OFFLINE_ONLY",
                      "UNVERIFIED": "GRAPH_VALID+UNVERIFIED_IDENTITY",
                      "NETWORK_UNAVAILABLE": "GRAPH_VALID+DEGRADED_NETWORK",
                      "REMOTE_RATE_LIMIT": "GRAPH_VALID+DEGRADED_RATE_LIMIT",
                      "SOURCE_ERROR": "GRAPH_VALID+DEGRADED_SOURCE_ERROR",
                      "URL_UNREACHABLE": "GRAPH_VALID+URL_PROBLEM",
                      "URL_REACHABLE_IDENTITY_UNVERIFIED":
                          "GRAPH_VALID+URL_OK_IDENTITY_UNVERIFIED",
                      "INVALID": "GRAPH_BROKEN_OR_IDENTITY_CONFLICT"}


def build_profile(offline_result_path, online_result_obj):
    off = json.load(open(offline_result_path, encoding="utf-8-sig"))
    per = {}
    for e in online_result_obj.get("results", []):
        cid = e["citation_id"]
        off_status = None
        for b in (off.get("per_entry") or []):
            if str(b.get("key") or b.get("id")) == cid:
                off_status = b.get("_source_identity")
        per[cid] = {
            "offline_reference_status": off_status or
                ("INVALID" if not off.get("reference_graph_valid") else "UNKNOWN"),
            "online_identity_status": e.get("verdict"),
            "reference_integrity_profile":
                OFFLINE_STATUS_MAP.get(e.get("verdict"), "UNKNOWN_PROFILE")
                if (off.get("reference_graph_valid")) else
                f"GRAPH_INVALID({off_status})+{e.get('verdict')}",
            "manual_review_required": bool(e.get("manual_review_required")),
        }
    counts = {}
    for e in online_result_obj.get("results", []):
        v = e.get("verdict")
        counts[v] = counts.get(v, 0) + 1
    return {"schema_version": "reference_integrity_profile.v1",
            "generated_at_utc": now_utc(),
            "policy": online_result_obj.get("policy"),
            "graph_valid": off.get("reference_graph_valid"),
            "identity_counts": counts,
            "per_entry": per}


# --------------------------------------------------------------------------
# manual review records (spec sections 37-38) — no bare booleans
# --------------------------------------------------------------------------

REQUIRED_REVIEW_FIELDS = ("citation_id", "decision", "reason", "evidence",
                          "completed_at")


def attach_manual_reviews(result_obj, reviews):
    by_id = {r["citation_id"]: r for r in result_obj.get("results", [])}
    applied = 0
    for rv in reviews:
        missing = [f for f in REQUIRED_REVIEW_FIELDS if not rv.get(f)]
        if missing:
            raise SystemExit(f"INPUT_ERROR manual review missing fields: {missing}")
        e = by_id.get(rv["citation_id"])
        if not e:
            continue
        e.setdefault("manual_reviews", []).append(rv)
        if rv["decision"].upper() in ("CONFIRMED", "ACCEPTED_AS_VALID"):
            e["final_status"] = "MANUALLY_CONFIRMED"
        elif rv["decision"].upper() in ("REJECTED", "RETRACTED"):
            e["final_status"] = "MANUALLY_REJECTED"
        else:
            e["final_status"] = "MANUALLY_" + rv["decision"].upper()
        applied += 1
    return applied


# --------------------------------------------------------------------------
# offline deterministic replay (spec section 28)
# --------------------------------------------------------------------------

def replay(result_path, out_path):
    """Recompute field matches + verdict from cached resolved metadata only."""
    prev = json.load(open(result_path, encoding="utf-8-sig"))
    out = {"schema_version": prev["schema_version"], "replayed_at_utc": now_utc(),
           "replay_of": os.path.abspath(result_path), "policy": prev["policy"],
           "results": [], "deterministic_replay": True}
    diffs = []
    for e in prev.get("results", []):
        ne = dict(e)
        rid = (e.get("resolved_identity") or {})
        if rid.get("source") and e.get("field_matches"):
            # recompute from stored remote identity snapshot deterministically
            meta = {k: rid.get(k) for k in ("title", "authors", "year", "venue")}
            if any(meta.values()):
                ref = compare_fields(e["local"], meta)
                v2, c2 = assemble_verdict(
                    ref, True, normalize_doi(e.get("doi"))[0])
                if v2 != e.get("verdict"):
                    diffs.append(e["citation_id"])
                ne["recomputed_field_matches"] = ref
                ne["replay_verdict"] = v2
        out["results"].append(ne)
    out["replay_verdict_divergence"] = diffs
    json.dump(out, open(out_path, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    print("REPLAY ->", os.path.abspath(out_path),
          "| divergences:", len(diffs))
    return 0


# --------------------------------------------------------------------------
# main verify pipeline
# --------------------------------------------------------------------------

def build_sources(names, mailto, fixture_json=None):
    order = ["crossref", "openalex", "doiresolver"]
    srcs = []
    for n in (names or order):
        if n == "crossref":
            srcs.append(CrossrefSource(mailto))
        elif n == "openalex":
            srcs.append(OpenAlexSource(mailto))
        elif n == "doiresolver":
            srcs.append(DoiResolverSource())
        elif n == "fixtures" and fixture_json:
            srcs.append(FixtureSource(fixture_json))
    if fixture_json:
        fx = FixtureSource(fixture_json)
        srcs.insert(0, fx)     # fixtures take precedence in test runs
    return srcs


def cmd_verify(a):
    bib_raw = json.load(open(a.bibliography, encoding="utf-8-sig"))
    entries = bib_raw if isinstance(bib_raw, list) else \
        bib_raw.get("references", [])
    keys = set(a.keys.split(",")) if a.keys else None
    if a.limit:
        entries = entries[:a.limit]
    if keys:
        entries = [e for e in entries
                   if (e.get("key") or str(e.get("id"))) in keys]
    cache = Cache(a.cache_dir, a.cache_ttl_days)
    mailto = os.environ.get("REFVERIFY_MAILTO")
    sources = build_sources((a.sources or "").split(",") if a.sources else None,
                            mailto, a.fixture_source)
    webchecker = WebCheckSource()
    t0 = time.perf_counter()
    results = []
    for e in entries:
        r = verify_entry(e, sources, cache, a.policy, webchecker)
        if r["verdict"] in REVIEW_REQUIRED and a.policy != "OFFLINE":
            r["manual_review_required"] = True
        results.append(r)
    elapsed = round(time.perf_counter() - t0, 3)
    obj = {
        "schema_version": "reference_identity_result.v1",
        "generated_at_utc": now_utc(),
        "policy": a.policy,
        "sources_configured": [s.name for s in sources],
        "cache_dir": os.path.abspath(a.cache_dir),
        "cache_ttl_days": a.cache_ttl_days,
        "privacy_note": "only public bibliographic metadata (DOI/title/authors/"
                        "year/venue) is sent to scholarly APIs; no full text, "
                        "no private files, no identity corpus",
        "secret_note": f"REFVERIFY_MAILTO configured={bool(mailto)}; no API keys used",
        "timings_seconds": {"total_verify_seconds": elapsed,
                            "per_reference_avg_seconds":
                                round(elapsed / max(1, len(results)), 4)},
        "results": results,
    }
    counts = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    obj["verdict_counts"] = counts

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(obj, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    if a.trace:
        write_trace(a.trace, obj)
    print("REFERENCE_IDENTITY_VERIFY policy=", a.policy,
          "| entries:", len(results), "| seconds:", elapsed)
    for k, v in sorted(counts.items()):
        print(f"  {k} = {v}")
    print("->", os.path.abspath(a.out))
    return 0


TRACE_FIELDS = ["citation_id", "reference_type", "local_title", "local_doi",
                "local_year", "local_venue", "verification_source",
                "resolved_doi", "resolved_title", "title_match_score",
                "author_match_status", "year_match_status", "venue_match_status",
                "online_status", "reason_codes", "cache_status",
                "manual_review_required", "final_status"]


def write_trace(path, obj):
    rows = []
    for r in obj.get("results", []):
        loc = r.get("local") or {}
        fm = r.get("field_matches") or {}
        ri = r.get("resolved_identity") or {}
        rows.append({
            "citation_id": r["citation_id"],
            "reference_type": r.get("reference_type", ""),
            "local_title": loc.get("title", ""),
            "local_doi": loc.get("doi") or "",
            "local_year": loc.get("year", ""),
            "local_venue": loc.get("venue", ""),
            "verification_source": ";".join(sorted(
                {v["source"] for v in r.get("verification_source", [])})),
            "resolved_doi": ri.get("doi") or r.get("doi") or "",
            "resolved_title": ri.get("title", ""),
            "title_match_score": (fm.get("title") or {}).get("score", ""),
            "author_match_status": (fm.get("authors") or {}).get("status", ""),
            "year_match_status": (fm.get("year") or {}).get("status", ""),
            "venue_match_status": (fm.get("venue") or {}).get("status", ""),
            "online_status": r.get("verdict", ""),
            "reason_codes": ";".join(r.get("reason_codes", [])),
            "cache_status": ";".join(r.get("cache_status", [])),
            "manual_review_required": bool(r.get("manual_review_required")),
            "final_status": r.get("final_status") or r.get("verdict", ""),
        })
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=TRACE_FIELDS)
        w.writeheader(); w.writerows(rows)


def cmd_manual_review(a):
    obj = json.load(open(a.result, encoding="utf-8-sig"))
    rec = {"citation_id": a.citation_id, "decision": a.decision,
           "reason": a.reason, "evidence": a.evidence,
           "completed_at": now_utc(), "reviewer": a.reviewer or "human"}
    n = attach_manual_reviews(obj, [rec])
    if n == 0:
        print("INPUT_ERROR citation_id not found:", a.citation_id); return 2
    json.dump(obj, open(a.result, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    print("MANUAL_REVIEW_ATTACHED:", a.citation_id, "->", rec["decision"])
    return 0


def cmd_aggregate(a):
    online = json.load(open(a.online, encoding="utf-8-sig"))
    prof = build_profile(a.offline, online)
    json.dump(prof, open(a.out, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    print("REFERENCE_INTEGRITY_PROFILE graph_valid=", prof["graph_valid"],
          "| counts:", prof["identity_counts"])
    print("->", os.path.abspath(a.out))
    return 0


def cmd_main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("verify", help="verify bibliography identities online")
    pv.add_argument("--bibliography", required=True)
    pv.add_argument("--policy", default="ONLINE_PREFERRED",
                    choices=list(POLICIES))
    pv.add_argument("--sources", default=None,
                    help="comma list: crossref,openalex,doiresolver[,fixtures]")
    pv.add_argument("--fixture-source", default=None,
                    help="curated metadata JSON (test adapter; source_class=fixture)")
    pv.add_argument("--cache-dir", required=True)
    pv.add_argument("--cache-ttl-days", type=int, default=DEFAULT_TTL_DAYS)
    pv.add_argument("--out", required=True)
    pv.add_argument("--trace", default=None)
    pv.add_argument("--limit", type=int, default=None)
    pv.add_argument("--keys", default=None)
    pv.set_defaults(fn=cmd_verify)

    pr = sub.add_parser("replay", help="deterministic offline replay from result")
    pr.add_argument("--result", required=True)
    pr.add_argument("--out", required=True)
    pr.set_defaults(fn=lambda a: replay(a.result, a.out))

    pm = sub.add_parser("manual-review", help="attach evidence-bound human review")
    pm.add_argument("--result", required=True)
    pm.add_argument("--citation-id", required=True)
    pm.add_argument("--decision", required=True)
    pm.add_argument("--reason", required=True)
    pm.add_argument("--evidence", required=True)
    pm.add_argument("--reviewer", default=None)
    pm.set_defaults(fn=cmd_manual_review)

    pa = sub.add_parser("aggregate", help="combine F4 offline + PH2 online layers")
    pa.add_argument("--offline", required=True,
                    help="reference_validation.json from validate_references.py")
    pa.add_argument("--online", required=True,
                    help="reference_identity_result.json from this tool")
    pa.add_argument("--out", required=True)
    pa.set_defaults(fn=cmd_aggregate)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(cmd_main())
