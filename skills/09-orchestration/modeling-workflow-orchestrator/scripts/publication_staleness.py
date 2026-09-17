#!/usr/bin/env python3
"""F5 Publication staleness monitor + P1-C.
Registry maps artifact -> {path, sha256, parents:{name:sha256-at-build}}.
check recomputes own+parent hashes; mismatch/parent-change => STALE.
Commands: register <reg> <name> <path> [--parent name=path ...]
          check   <reg>          (exit 1 if any stale/missing)
"""
import hashlib,json,os,sys
def sha(p):
    return hashlib.sha256(open(p,'rb').read()).hexdigest()
def load(p):
    if os.path.exists(p): return json.load(open(p,encoding='utf-8-sig'))
    return {"artifacts":{}}
def save(p,d): json.dump(d,open(p,'w',encoding='utf-8'),indent=1)
def main(a):
    if len(a)<3: print(__doc__);return 2
    cmd,reg=a[1],a[2]; d=load(reg)
    if cmd=="register":
        name,path=a[3],a[4]; parents={}
        rest=a[5:]
        for i,x in enumerate(rest):
            if x=="--parent" and i+2<len(rest)+1:
                pname,ppath=rest[i+1],rest[i+2]
                if os.path.exists(ppath): parents[pname]=sha(ppath)
        e={"path":os.path.abspath(path),"sha256":sha(path),"parents":parents}
        d["artifacts"][name]=e; save(reg,d); print("REGISTERED",name,"fresh")
        return 0
    if cmd=="update":
        name,path=a[3],a[4]
        if name in d["artifacts"]:
            e=d["artifacts"][name]; e["sha256"]=sha(path)
            for pn,pv in list(e.get("parents",{}).items()):
                pp=d["artifacts"].get(pn,{}).get("path")
                if pp and os.path.exists(pp): e["parents"][pn]=sha(pp)
            save(reg,d); print("UPDATED",name,"fresh"); return 0
        print("UNKNOWN artifact",name); return 2
    if cmd=="check":
        stale=[]
        for name,e in d["artifacts"].items():
            p=e.get("path")
            if not p or not os.path.exists(p): stale.append(name+":missing"); continue
            cur=sha(p)
            if cur!=e.get("sha256"): stale.append(name+":self_changed"); continue
            for pn,ph in (e.get("parents") or {}).items():
                pe=d["artifacts"].get(pn)
                cp=sha(pe["path"]) if pe and os.path.exists(pe.get("path")) else None
                if cp is None: continue
                if cp!=ph: stale.append(f"{name}:stale(parent {pn} changed)")
        if stale:
            print("STALE:", "; ".join(stale)); print("PUBLICATION_STALENESS = FAIL")
            json.dump({"stale":stale,"status":"FAIL"},open(os.path.join(os.path.dirname(reg),"publication_staleness.json"),"w"))
            return 1
        print("PUBLICATION_STALENESS = FRESH")
        json.dump({"stale":[],"status":"FRESH"},open(os.path.join(os.path.dirname(reg),"publication_staleness.json"),"w"))
        return 0
    print(__doc__); return 2
if __name__=="__main__": raise SystemExit(main(sys.argv))
