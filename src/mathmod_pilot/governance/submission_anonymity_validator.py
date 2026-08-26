#!/usr/bin/env python3
"""submission_anonymity_validator.py — PH1 H1-B (READ_ONLY, detect-and-block).

Deep DOCX (OpenXML/ZIP) + PDF anonymity & privacy scanner for CUMCM submission
hardening. Never modifies scanned documents; never uploads anything.

DOCX checks: core/extended property identity (creator / lastModifiedBy / company /
manager / title / subject / description / keywords / category), comments part +
comment authors, people.xml, tracked changes (w:ins/w:del/moveFrom/moveTo), hidden
text (w:vanish) with locators, customXml parts, custom properties, embedded/OLE
objects, relationship targets (file:// / drive letters / UNC / localhost /
external images), embedded media inventory with lightweight PNG/JPEG metadata
chunk inspection, and pattern-based text scan across document/header/footer/
footnotes/endnotes/comments parts.

PDF checks (via PyMuPDF when available): info-dict identity fields, raw XMP,
extracted page text. Capability boundary reported honestly (LIMITED when engine
or text layer unavailable).

Verdict: PASS | PASS_WITH_MANUAL_REVIEW | FAIL  (+ reason codes, findings, timings).
Exit:    0 = PASS / PASS_WITH_MANUAL_REVIEW   1 = FAIL   2 = input error.

Usage:
  python submission_anonymity_validator.py scan --docx P.docx [--pdf P.pdf]
      --profile competition_profile.cumcm.json [--identity-corpus corpus.json]
      --out verdict.json [--anonymity-record out/anonymity_record.json]
"""
import argparse, hashlib, json, os, re, struct, sys, time, zipfile
import xml.etree.ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
EP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

SEV_FAIL, SEV_MANUAL, SEV_WARN = "fail", "manual", "warn"


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


# --------------------------------------------------------------------------
# Pattern engine
# --------------------------------------------------------------------------

RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RE_MOBILE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
RE_QQ = re.compile(r"(?:QQ|qq|扣扣)\s*[:：]?\s*\d{5,11}")
RE_TEL = re.compile(r"(?:电话|手机|联系方式|联系电话|tel|phone)\s*[:：]?\s*[0-9\- +]{7,20}", re.I)
RE_STUDENT_ID = re.compile(r"(?:学号|学籍号|student\s*(?:id|no\.?))\s*[:：]?\s*[A-Za-z0-9\-]{6,}", re.I)
RE_ADVISOR = re.compile(r"指导教师\s*[:：]?\s*[\u4e00-\u9fa5a-zA-Z]{2,12}")
RE_TEAM_ID = re.compile(r"(?:队伍编号|参赛队号|控制号|报名号|队号)\s*[:：]?\s*[A-Za-z0-9\-]{3,}")
RE_NAME_LABEL = re.compile(r"(?:姓名|作者|队员|成员|队长)\s*[:：]\s*[\u4e00-\u9fa5]{2,4}(?![院校系])")
RE_SCHOOL_SUFFIX = re.compile(r"[\u4e00-\u9fa5]{2,14}(?:大学|学院)")
RE_WIN_PATH = re.compile(r"\b[A-Za-z]:[\\/](?:[^\s\"'<>|*?]{0,80}[\\/]){0,6}[^\s\"'<>|*?]{0,80}")
RE_UNIX_PATH = re.compile(r"(?:/Users/|/home/|/tmp/|/var/folders/)[^\s\"'<>]{1,100}")
RE_FILE_URI = re.compile(r"file:///+[^\s\"'<>]{1,120}", re.I)
RE_LOCALHOST = re.compile(r"(?:localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+)\S{0,60}")

HIGH_PATTERNS = [
    ("IDENTITY_TEXT_MATCH", RE_EMAIL, "email address"),
    ("IDENTITY_TEXT_MATCH", RE_MOBILE, "CN mobile number"),
    ("IDENTITY_TEXT_MATCH", RE_QQ, "QQ contact"),
    ("IDENTITY_TEXT_MATCH", RE_TEL, "telephone label + number"),
    ("IDENTITY_TEXT_MATCH", RE_STUDENT_ID, "student-id label"),
    ("IDENTITY_TEXT_MATCH", RE_ADVISOR, "advisor label"),
    ("IDENTITY_TEXT_MATCH", RE_TEAM_ID, "team/control number label"),
    ("IDENTITY_TEXT_MATCH", RE_NAME_LABEL, "personal-name label"),
]

LOW_PATTERNS = [
    ("LOW_CONFIDENCE_REVIEW_PATTERN", RE_SCHOOL_SUFFIX, "school/college name mention"),
]


def mask_evidence(s, keep=4):
    s = s.strip()
    if len(s) <= keep * 2:
        return s
    return s[:keep] + "…" + s[-keep:]


class Findings:
    def __init__(self):
        self.items = []

    def add(self, code, severity, part, locator, evidence="", detail=""):
        self.items.append({
            "reason_code": code, "severity": severity, "part": part,
            "locator": locator,
            "masked_evidence": mask_evidence(evidence) if evidence else "",
            "detail": detail,
        })

    def worst(self):
        order = {SEV_WARN: 1, SEV_MANUAL: 2, SEV_FAIL: 3}
        return max([order[i["severity"]] for i in self.items], default=0)


def classify_path_hit(path_str):
    """Return (severity, reason) per local-path policy."""
    low = path_str.lower().replace("\\\\", "\\")
    userish = False
    if re.search(r"[\\/]users[\\/][^\\/\"'\s<>]+", low):
        userish = True
    if re.search(r"[\\/]home[\\/][^\\/\"'\s<>]+", low):
        userish = True
    if "\\appdata\\" in low or "/appdata/" in low:
        userish = True
    if re.search(r"[\\/]temp[\\/]", low) or "/tmp/" in low or "$tmp" in low:
        userish = True
    if userish:
        return SEV_FAIL, "path exposes user/account-specific directory"
    return SEV_WARN, "absolute local path present in submittable content"


def near_identity_context(ctx):
    return bool(re.search(r"(姓名|作者|队员|成员|队长|指导教师|学号|队伍|单位|学校)", ctx))


def scan_text(text, part, findings, corpus):
    """Scan one text body; appends findings."""
    if not text:
        return
    low_text = text.lower()
    for token in corpus.get("high_confidence_tokens", []):
        t = str(token).lower()
        if t and t in low_text:
            idx = low_text.find(t)
            findings.add("IDENTITY_TEXT_MATCH", SEV_FAIL, part, f"offset:{idx}",
                         evidence=text[max(0, idx - 10):idx + len(token) + 10],
                         detail="identity-corpus token matched")
    for code, rx, label in HIGH_PATTERNS:
        for m in rx.finditer(text):
            findings.add(code, SEV_FAIL, part, f"offset:{m.start()}",
                         evidence=m.group(0),
                         detail=f"high-confidence identity pattern: {label}")
    for code, rx, label in LOW_PATTERNS:
        for m in list(rx.finditer(text))[:20]:
            ctx = text[max(0, m.start() - 24):m.end() + 24]
            if near_identity_context(ctx):
                findings.add(code, SEV_FAIL, part, f"offset:{m.start()}",
                             evidence=m.group(0),
                             detail="school-name mention adjacent to personal-name/team context")
            else:
                findings.add(code, SEV_MANUAL, part, f"offset:{m.start()}",
                             evidence=m.group(0),
                             detail="school-name mention without direct identity context "
                                    "(may be a legitimate citation/institution reference)")
    for rx in (RE_WIN_PATH, RE_UNIX_PATH):
        for m in list(rx.finditer(text))[:40]:
            sev, why = classify_path_hit(m.group(0))
            code = "LOCAL_PATH_LEAK"
            if sev == SEV_WARN:
                # generic absolute path in content: privacy warning level
                findings.add(code, SEV_WARN, part, f"offset:{m.start()}",
                             evidence=m.group(0), detail=why)
            else:
                findings.add(code, sev, part, f"offset:{m.start()}",
                             evidence=m.group(0), detail=why)
    for m in list(RE_FILE_URI.finditer(text))[:20]:
        findings.add("EXTERNAL_RELATIONSHIP_PRESENT", SEV_FAIL, part, f"offset:{m.start()}",
                     evidence=m.group(0), detail="file:// URI inside submittable text")
    for m in list(RE_LOCALHOST.finditer(text))[:20]:
        findings.add("LOW_CONFIDENCE_REVIEW_PATTERN", SEV_MANUAL, part, f"offset:{m.start()}",
                     evidence=m.group(0), detail="localhost/private-intranet reference")


def blob_has_high_identity(blob, corpus):
    if RE_EMAIL.search(blob) or RE_MOBILE.search(blob):
        return True
    for token in corpus.get("high_confidence_tokens", []):
        if token and str(token).lower() in blob.lower():
            return True
    return False


# --------------------------------------------------------------------------
# Lightweight image metadata inspection (no OCR)
# --------------------------------------------------------------------------

def png_text_chunks(data):
    out = []
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return out
    pos = 8
    while pos + 8 <= len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        if ctype == b"tEXt":
            kv = chunk.split(b"\x00", 1)
            if len(kv) == 2:
                out.append((kv[0].decode("latin-1", "replace"),
                            kv[1][:200].decode("latin-1", "replace")))
        elif ctype == b"iTXt":
            kv = chunk.split(b"\x00", 4)
            if len(kv) >= 2:
                out.append((kv[0].decode("latin-1", "replace"),
                            kv[-1][:200].decode("utf-8", "replace")))
        elif ctype == b"IEND":
            break
        pos += 12 + ln
        if len(out) > 32:
            break
    return out


def jpeg_comments(data):
    out = []
    if data[:2] != b"\xff\xd8":
        return out
    pos = 2
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            break
        marker = data[pos + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        seglen = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        if marker == 0xFE:
            out.append(data[pos + 4:pos + 2 + seglen][:200].decode("latin-1", "replace"))
        if marker in (0xDA, 0x01):
            break
        pos += 2 + seglen
    return out


def image_metadata_findings(name, data, findings, corpus):
    entries = [(k, v) for k, v in png_text_chunks(data)]
    entries += [(f"JPEG_COM_{i}", t) for i, t in enumerate(jpeg_comments(data))]
    for k, v in entries:
        blob = f"{k}: {v}"
        if blob_has_high_identity(blob, corpus):
            findings.add("IMAGE_METADATA_IDENTITY", SEV_FAIL, name, k, evidence=blob,
                         detail="embedded raster metadata carries high-confidence identity pattern")
        elif RE_WIN_PATH.search(blob) or RE_UNIX_PATH.search(blob) or RE_FILE_URI.search(blob):
            findings.add("IMAGE_METADATA_PATH_LEAK", SEV_WARN, name, k, evidence=blob,
                         detail="embedded raster metadata contains a local filesystem path")


# --------------------------------------------------------------------------
# Metadata field policy
# --------------------------------------------------------------------------

def meta_is_neutral(v, neutral_set):
    return v.strip() == "" or v.strip().lower() in {n.lower() for n in neutral_set}


def check_meta_field(value, fail_code, field_label, part, findings, corpus, neutral_set):
    """Authoring-type fields (creator / lastModifiedBy / Company / Manager).

    Policy: these fields should be empty or neutral in an anonymized submission.
    Any identity-pattern match, school-name token, local path, OR a bare CJK
    personal-name-shaped string (2-4 hanzi) is a hard FAIL; any other non-empty
    value requires manual confirmation.
    """
    v = (value or "").strip()
    if meta_is_neutral(v, neutral_set):
        return
    hit_identity = bool(RE_EMAIL.search(v)) or bool(RE_MOBILE.search(v))
    for token in corpus.get("high_confidence_tokens", []):
        if token and str(token).lower() in v.lower():
            hit_identity = True
            break
    if re.fullmatch(r"[\u4e00-\u9fa5]{2,4}", v):
        hit_identity = True   # personal-name-shaped value in an authoring field
    if hit_identity or re.search(r"(大学|学院)", v) or RE_WIN_PATH.search(v) or RE_UNIX_PATH.search(v):
        findings.add(fail_code, SEV_FAIL, part, field_label, evidence=v,
                     detail="document property carries identity/school/local-path information")
    else:
        findings.add(fail_code, SEV_MANUAL, part, field_label, evidence=v,
                     detail="non-empty authoring property not matching known identities — "
                            "manual confirmation required")


def scan_free_text_meta(value, field_label, part, findings, corpus):
    """Descriptive fields (title / subject / description / keywords / category)."""
    v = (value or "").strip()
    if not v:
        return
    probe = Findings()
    scan_text(v, f"{part}#{field_label}", probe, corpus)
    for it in probe.items:
        if it["severity"] == SEV_FAIL:
            findings.add(it["reason_code"], SEV_FAIL, f"{part}#{field_label}", field_label,
                         evidence=v, detail="identity/path pattern inside document property")
        elif it["severity"] == SEV_MANUAL:
            findings.add("METADATA_REVIEW_REQUIRED", SEV_MANUAL, f"{part}#{field_label}",
                         field_label, evidence=v, detail="property content needs manual confirmation")


# --------------------------------------------------------------------------
# DOCX deep scan
# --------------------------------------------------------------------------

TRACK_TAGS = [f"{{{W_NS}}}ins", f"{{{W_NS}}}del", f"{{{W_NS}}}moveFrom", f"{{{W_NS}}}moveTo"]


def wtag(local):
    return f"{{{W_NS}}}{local}"


def extract_w_text(root):
    chunks = []
    for tag in ("t", "delText"):
        for el in root.iter(wtag(tag)):
            if el.text:
                chunks.append(el.text)
    return "".join(chunks)


def parent_map(root):
    return {c: p for p in root.iter() for c in p}


def normalize_rel_target(base_dir_in_zip, target):
    t = target.replace("\\", "/").lstrip("/")
    parts = []
    for seg in (base_dir_in_zip.split("/") if base_dir_in_zip else []) + t.split("/"):
        if seg in ("", "."):
            continue
        if seg == "..":
            if parts:
                parts.pop()
            continue
        parts.append(seg)
    return "/".join(parts)


def scan_docx(path, profile, corpus, timings):
    findings = Findings()
    extras = {}
    t0 = time.perf_counter()
    try:
        zf = zipfile.ZipFile(path, "r")
    except Exception as e:
        findings.add("INPUT_UNREADABLE", SEV_FAIL, "(zip)", "open", detail=str(e))
        timings["docx_scan_seconds"] = round(time.perf_counter() - t0, 4)
        return findings, extras
    names = zf.namelist()
    lowered = [n.lower() for n in names]

    def read(n):
        return zf.read(n)

    # ---- presence flags -----------------------------------------------
    has_comments = any(n.startswith("word/comments") and n.endswith(".xml") for n in lowered)
    if has_comments:
        findings.add("DOCX_COMMENT_PRESENT", SEV_FAIL, "word/comments.xml", "part-presence",
                     detail="comments part present in submission document")

    custom_items = sorted({n for n in names if n.lower().startswith("customxml/")
                           and n.endswith(".xml") and not n.lower().endswith("props.xml")})
    if custom_items:
        findings.add("MANUAL_OBJECT_REVIEW_REQUIRED", SEV_MANUAL, "customXml/", ",".join(custom_items[:8]),
                     detail="customXml part(s) present — content must be manually reviewed")

    embeddings = sorted({n for n in names if n.lower().startswith("word/embeddings/")})
    if embeddings:
        findings.add("MANUAL_OBJECT_REVIEW_REQUIRED", SEV_MANUAL, "word/embeddings/",
                     ",".join(embeddings[:8]),
                     detail="embedded/OLE object(s) present — manual review before submission")

    # ---- docProps/custom.xml -------------------------------------------
    custom_props_name = next((n for n in names if n.lower() == "docprops/custom.xml"), None)
    if custom_props_name:
        try:
            root = ET.fromstring(read(custom_props_name))
            CP_FMTID = "{http://schemas.openxmlformats.org/officeDocument/2006/custom-properties}"
            props = []
            for p in root.iter(f"{CP_FMTID}property"):
                pname = p.get("name", "?")
                val = "".join((child.text or "") for child in p) or ""
                props.append((pname, val))
                probe = Findings()
                scan_text(val, "docProps/custom.xml", probe, corpus)
                bad = any(i["severity"] == SEV_FAIL for i in probe.items)
                findings.add("MANUAL_OBJECT_REVIEW_REQUIRED", SEV_FAIL if bad else SEV_MANUAL,
                             "docProps/custom.xml", pname, evidence=val,
                             detail="custom document property present"
                                    + (" with identity/path-like content" if bad else ""))
            extras["custom_properties"] = [p[0] for p in props]
        except ET.ParseError as e:
            findings.add("MANUAL_OBJECT_REVIEW_REQUIRED", SEV_MANUAL, "docProps/custom.xml",
                         "parse", detail=str(e))

    # ---- core properties -------------------------------------------------
    neutral = set(profile.get("metadata_neutral_allowlist", [""]))
    core_name = next((n for n in names if n.lower() == "docprops/core.xml"), None)
    meta_snapshot = {}
    if core_name is None:
        findings.add("MANUAL_OBJECT_REVIEW_REQUIRED", SEV_MANUAL, "docProps/core.xml", "missing",
                     detail="core properties part absent — provenance unknown")
    else:
        try:
            root = ET.fromstring(read(core_name))
            fields = {
                "creator": root.findtext("{%s}creator" % DC_NS) or "",
                "lastModifiedBy": root.findtext("{%s}lastModifiedBy" % CP_NS) or "",
                "title": root.findtext("{%s}title" % DC_NS) or "",
                "subject": root.findtext("{%s}subject" % DC_NS) or "",
                "description": root.findtext("{%s}description" % DC_NS) or "",
                "keywords": root.findtext("{%s}keywords" % CP_NS) or "",
                "category": root.findtext("{%s}category" % CP_NS) or "",
            }
            meta_snapshot.update(fields)
            check_meta_field(fields["creator"], "DOCX_CREATOR_LEAK", "creator",
                             "docProps/core.xml", findings, corpus, neutral)
            check_meta_field(fields["lastModifiedBy"], "DOCX_LAST_MODIFIED_BY_LEAK", "lastModifiedBy",
                             "docProps/core.xml", findings, corpus, neutral)
            for k in ("title", "subject", "description", "keywords", "category"):
                scan_free_text_meta(fields[k], k, "docProps/core.xml", findings, corpus)
        except ET.ParseError as e:
            findings.add("MANUAL_OBJECT_REVIEW_REQUIRED", SEV_MANUAL, "docProps/core.xml",
                         "parse", detail=f"core.xml unparseable: {e}")

    app_name = next((n for n in names if n.lower() == "docprops/app.xml"), None)
    if app_name:
        try:
            root = ET.fromstring(read(app_name))
            company = root.findtext("{%s}Company" % EP_NS) or ""
            manager = root.findtext("{%s}Manager" % EP_NS) or ""
            template = root.findtext("{%s}Template" % EP_NS) or ""
            meta_snapshot.update({"Company": company, "Manager": manager, "Template": template})
            check_meta_field(company, "DOCX_COMPANY_FIELD_LEAK", "Company",
                             "docProps/app.xml", findings, corpus, neutral)
            check_meta_field(manager, "DOCX_COMPANY_FIELD_LEAK", "Manager",
                             "docProps/app.xml", findings, corpus, neutral)
            if template and (RE_WIN_PATH.search(template) or RE_UNIX_PATH.search(template)):
                sev, why = classify_path_hit(template)
                findings.add("LOCAL_PATH_LEAK", sev, "docProps/app.xml", "Template",
                             evidence=template, detail=f"template path leak: {why}")
        except ET.ParseError:
            pass

    # ---- people.xml --------------------------------------------------------
    people_name = next((n for n in names if n.lower().endswith("word/people.xml")), None)
    if people_name:
        try:
            root = ET.fromstring(read(people_name))
            persons = [el.get(wtag("author"), "") for el in root.iter(wtag("person"))]
            for a in persons:
                if a.strip():
                    findings.add("DOCX_PEOPLE_PRESENT", SEV_FAIL, "word/people.xml",
                                 "w:person/@w:author", evidence=a,
                                 detail="people registry carries an author identity")
        except ET.ParseError:
            findings.add("DOCX_PEOPLE_PRESENT", SEV_MANUAL, "word/people.xml", "parse-failed",
                         detail="people.xml unparseable — manual review")

    # ---- comments content ---------------------------------------------------
    for cn in [n for n in names if n.lower().startswith("word/comments") and n.endswith(".xml")]:
        try:
            root = ET.fromstring(read(cn))
            for c in root.iter(wtag("comment")):
                author = c.get(wtag("author"), "")
                ctext = extract_w_text(c)
                if author.strip():
                    findings.add("DOCX_COMMENT_AUTHOR_IDENTITY", SEV_FAIL, cn,
                                 f"w:comment@w:author={mask_evidence(author)}", evidence=author,
                                 detail="comment author attribute present")
                scan_text(ctext, f"{cn}#comment[{c.get(wtag('id'), '?')}]", findings, corpus)
        except ET.ParseError:
            findings.add("DOCX_COMMENT_PRESENT", SEV_FAIL, cn, "parse-failed",
                         detail="comments part unparseable — treat as contaminated")

    # ---- tracked changes / hidden text / BODY TEXT across wordprocessing parts ----
    wp_parts = [n for n in names if n.lower().startswith("word/") and n.lower().endswith(".xml")
                and any(k in n.lower() for k in
                        ("document", "header", "footer", "footnotes", "endnotes"))]
    hidden_locs = []
    for pn in wp_parts:
        try:
            root = ET.fromstring(read(pn))
        except ET.ParseError:
            continue
        # full visible+deleted text scan of this part (body/heading/footer content)
        scan_text(extract_w_text(root), pn, findings, corpus)
        for tag in TRACK_TAGS:
            local = tag.split("}")[1]
            els = list(root.iter(tag))
            if not els:
                continue
            if local in ("ins", "del"):
                for el in els[:10]:
                    findings.add("DOCX_TRACK_CHANGES_PRESENT", SEV_FAIL, pn,
                                 f"w:{local}", evidence=extract_w_text(el)[:60],
                                 detail=f"unresolved revision element w:{local} ({len(els)} total)")
            else:
                findings.add("DOCX_TRACK_CHANGES_PRESENT", SEV_FAIL, pn, f"w:{local}",
                             detail=f"move revision elements present: {len(els)}")
        pmap = parent_map(root)
        for van in root.iter(wtag("vanish")):
            rpr = pmap.get(van)
            run = pmap.get(rpr) if rpr is not None else None
            snippet = extract_w_text(run) if run is not None else ""
            hidden_locs.append((pn, snippet[:60]))
    for pn, snip in hidden_locs[:20]:
        findings.add("DOCX_HIDDEN_TEXT_PRESENT", SEV_FAIL, pn, "w:vanish", evidence=snip,
                     detail="hidden run formatting present (draft/leak risk)")

    # ---- settings.xml mitigation note ---------------------------------------
    setname = next((n for n in names if n.lower() == "word/settings.xml"), None)
    remove_pi = False
    if setname:
        try:
            root = ET.fromstring(read(setname))
            remove_pi = root.find(wtag("removePersonalInformation")) is not None
        except ET.ParseError:
            pass

    # ---- relationships --------------------------------------------------------
    rels_parts = [next((n for n in names if n.lower() == "_rels/.rels"), None)]
    rels_parts += [n for n in names if n.lower().startswith("word/_rels/") and n.endswith(".rels")]
    image_rels = []       # internal image relationships
    ext_image_count = 0
    for rn in [r for r in rels_parts if r]:
        try:
            root = ET.fromstring(read(rn))
        except ET.ParseError:
            continue
        base = os.path.dirname(os.path.dirname(rn.replace("\\", "/")))
        for rel in root.iter("{%s}Relationship" % REL_NS):
            target = rel.get("Target", "")
            mode = rel.get("TargetMode", "Internal")
            rtype = rel.get("Type", "")
            if mode == "External":
                low_t = target.lower()
                is_local_fs = (low_t.startswith("file:") or bool(RE_WIN_PATH.match(target))
                               or target.startswith("\\\\") or target.startswith("/")
                               or "localhost" in low_t)
                if is_local_fs:
                    sev, why = classify_path_hit(target)
                    findings.add("LOCAL_PATH_LEAK", SEV_FAIL, rn, "Relationship@Target",
                                 evidence=target,
                                 detail=f"external relationship targets local filesystem: {why}")
                elif rtype.endswith("/image"):
                    ext_image_count += 1
                    findings.add("EXTERNAL_RELATIONSHIP_PRESENT", SEV_FAIL, rn,
                                 "image Relationship@Target", evidence=target,
                                 detail="linked (not embedded) image — document is not self-contained")
                elif rtype.endswith("/hyperlink"):
                    pass  # ordinary web hyperlinks acceptable in papers
            elif rtype.endswith("/image"):
                resolved = normalize_rel_target(base, target)
                image_rels.append((rn, target, resolved))

    # ---- media inventory ---------------------------------------------------------
    media_inventory = []
    media_lower = {n.lower() for n in names}
    for n in names:
        if n.lower().startswith("word/media/"):
            data = read(n)
            media_inventory.append({"part": n, "bytes": len(data), "sha256": sha256_bytes(data)})
            image_metadata_findings(n, data, findings, corpus)
    for rn, target, resolved in image_rels:
        if resolved and resolved.lower() not in media_lower:
            findings.add("EXTERNAL_RELATIONSHIP_PRESENT", SEV_FAIL, rn, "image Relationship@Target",
                         evidence=target,
                         detail="image relationship target missing from package (dangling dependency)")

    timings["docx_scan_seconds"] = round(time.perf_counter() - t0, 4)
    extras.update({
        "meta_snapshot": meta_snapshot,
        "removePersonalInformation_set": remove_pi,
        "media_inventory": media_inventory,
        "media_count": len(media_inventory),
        "external_image_relationships": ext_image_count,
        "hidden_text_locations": hidden_locs[:50],
    })
    return findings, extras


# --------------------------------------------------------------------------
# PDF scan
# --------------------------------------------------------------------------

def scan_pdf(path, profile, corpus, timings):
    findings = Findings()
    capability = {"engine": None, "mode": "LIMITED", "note": ""}
    t0 = time.perf_counter()
    try:
        import fitz  # PyMuPDF
    except Exception as e:
        capability["note"] = (f"PyMuPDF unavailable ({e}); PDF scanned at LIMITED level only "
                              "- no automated PDF anonymity verdict")
        findings.add("PDF_ENGINE_LIMITED", SEV_MANUAL, "(pdf)", "engine", detail=capability["note"])
        timings["pdf_scan_seconds"] = round(time.perf_counter() - t0, 4)
        return findings, capability
    capability["engine"] = "PyMuPDF"
    try:
        doc = fitz.open(path)
    except Exception as e:
        findings.add("INPUT_UNREADABLE", SEV_FAIL, "(pdf)", "open", detail=str(e))
        timings["pdf_scan_seconds"] = round(time.perf_counter() - t0, 4)
        return findings, capability
    info = doc.metadata or {}
    neutral = set(profile.get("metadata_neutral_allowlist", [""]))
    for key in ("author", "creator", "producer", "title", "subject", "keywords"):
        v = (info.get(key) or "").strip()
        if not v or meta_is_neutral(v, neutral):
            continue
        if key in ("author", "creator", "producer"):
            check_meta_field(v, "PDF_METADATA_LEAK", key, "pdf/info", findings, corpus, neutral)
        else:
            scan_free_text_meta(v, key, "pdf/info", findings, corpus)
    xmp = ""
    try:
        xmp = doc.xref_xml_metadata() or ""
        if not isinstance(xmp, str):
            xmp = ""
    except Exception:
        xmp = ""
    if xmp:
        probe = Findings()
        scan_text(xmp[:200000], "pdf/xmp", probe, corpus)
        for it in probe.items:
            if it["severity"] == SEV_FAIL:
                findings.add(it["reason_code"], SEV_FAIL, "pdf/xmp", "XMP",
                             evidence=it["masked_evidence"],
                             detail="identity/path pattern inside XMP metadata")
    text_ok = False
    for pno in range(doc.page_count):
        txt = doc.load_page(pno).get_text("text") or ""
        if txt.strip():
            text_ok = True
        probe = Findings()
        scan_text(txt, f"pdf/page[{pno + 1}]", probe, corpus)
        for it in probe.items:
            findings.add(it["reason_code"], it["severity"], it["part"], it["locator"],
                         evidence=it["masked_evidence"], detail=it["detail"])
    if not text_ok:
        capability["note"] = ("PDF text layer empty/unextractable - visible-text anonymity "
                              "cannot be automated; manual page review REQUIRED")
        findings.add("MANUAL_OBJECT_REVIEW_REQUIRED", SEV_MANUAL, "(pdf)", "text-layer",
                     detail=capability["note"])
    else:
        capability["mode"] = "FULL"
    capability["pages"] = doc.page_count
    doc.close()
    timings["pdf_scan_seconds"] = round(time.perf_counter() - t0, 4)
    return findings, capability


# --------------------------------------------------------------------------
# Verdict assembly
# --------------------------------------------------------------------------

def assemble(findings, extras, inputs):
    codes_fail = sorted({i["reason_code"] for i in findings.items if i["severity"] == SEV_FAIL})
    codes_manual = sorted({i["reason_code"] for i in findings.items if i["severity"] == SEV_MANUAL})
    codes_warn = sorted({i["reason_code"] for i in findings.items if i["severity"] == SEV_WARN})
    worst = findings.worst()
    status = "FAIL" if worst >= 3 else ("PASS_WITH_MANUAL_REVIEW" if worst == 2 else "PASS")
    return {
        "schema_version": "ph1_anonymity_verdict.v1",
        "validator_mode": "READ_ONLY",
        "status": status,
        "inputs": inputs,
        "fail_reason_codes": codes_fail,
        "manual_reason_codes": codes_manual,
        "warn_reason_codes": codes_warn,
        "findings": findings.items,
        "extras": extras,
        "manual_review_check_ids_needed": [f"ANON::{c}" for c in codes_manual],
    }


def write_anonymity_record(out_path, verdict_path, status):
    rec = {
        "schema_version": "anonymity_record.v2.ph1",
        "status": status,
        "validator": "submission_anonymity_validator.py",
        "verdict_ref": os.path.abspath(verdict_path),
        "verdict_sha256": sha256_bytes(open(verdict_path, "rb").read()),
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, ensure_ascii=False)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scan", help="deep-scan DOCX/PDF for identity/privacy leaks (read-only)")
    sc.add_argument("--docx")
    sc.add_argument("--pdf")
    sc.add_argument("--profile", required=True)
    sc.add_argument("--identity-corpus", default=None)
    sc.add_argument("--out", required=True)
    sc.add_argument("--anonymity-record", default=None)
    args = ap.parse_args(argv)

    profile = json.load(open(args.profile, encoding="utf-8-sig"))
    corpus = {}
    if args.identity_corpus and os.path.exists(args.identity_corpus):
        corpus = json.load(open(args.identity_corpus, encoding="utf-8-sig"))
    if not args.docx and not args.pdf:
        print("INPUT_ERROR: nothing to scan (--docx / --pdf)")
        return 2

    timings = {}
    all_findings = Findings()
    extras = {}
    inputs = {}
    if args.docx:
        if not os.path.exists(args.docx):
            print("INPUT_ERROR missing", args.docx)
            return 2
        inputs["docx"] = os.path.abspath(args.docx)
        f, ex = scan_docx(args.docx, profile, corpus, timings)
        all_findings.items.extend(f.items)
        extras["docx"] = ex
    if args.pdf:
        if not os.path.exists(args.pdf):
            print("INPUT_ERROR missing", args.pdf)
            return 2
        inputs["pdf"] = os.path.abspath(args.pdf)
        f, cap = scan_pdf(args.pdf, profile, corpus, timings)
        all_findings.items.extend(f.items)
        extras["pdf_capability"] = cap

    verdict = assemble(all_findings, extras, inputs)
    verdict["timings_seconds"] = timings
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=1, ensure_ascii=False)

    if args.anonymity_record:
        write_anonymity_record(args.anonymity_record, args.out, verdict["status"])

    print("ANONYMITY_VERDICT =", verdict["status"],
          "| fail:", len(verdict["fail_reason_codes"]),
          "| manual:", len(verdict["manual_reason_codes"]),
          "| warn:", len(verdict["warn_reason_codes"]))
    for c in verdict["fail_reason_codes"]:
        print("  FAIL_CODE:", c)
    return 1 if verdict["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
