"""Builds the ESL variant of Campfire 2026: the same plugin with every FormID moved into the light range (000800-000FFF).

Starts from src/esp/Campfire (Spriggit YAML of the shipped Campfire 1.12.1 SE/VR plugin) and src/scripts, never modifies them; writes esl-work/.
  1. numbers Campfire's own records 000800, 000801, ... in order of their old FormID (all of them, placed references and cells included)
  2. rewrites every NNNNNN:Campfire.esm reference in the YAML, renames files/folders that carry an old id, recomputes the interior-cell
     block folders from the new cell ids, and flags the plugin Small (ESL)
  3. rewrites every Papyrus GetFormFromFile(0x..., "Campfire.esm") to the new id
  4. writes esl-work/map_campfire.json (old -> new), the table the dependants (Frostfall, Last Seed, the patches) are rebuilt from
After this, deserialize esl-work/yaml with Spriggit to Campfire.esm (the output file must be called Campfire.esm).

Usage: python tools/esl_build.py
"""
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(HERE, "esl-work")
SRC = os.path.join(HERE, "src", "esp", "Campfire")
OUT = os.path.join(W, "yaml")
SC_IN = os.path.join(HERE, "src", "scripts")
SC_OUT = os.path.join(W, "scripts")


def read(p):
    with open(p, encoding="utf-8", errors="replace", newline="") as f:
        return f.read()


def write(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


defn = re.compile(r"^\s*(?:- )?FormKey: ([0-9A-F]{6}):Campfire\.esm\s*$", re.M)
ref = re.compile(r"\b([0-9A-F]{6}):Campfire\.esm")
own = set()
for dp, _, fs in os.walk(SRC):
    for fn in fs:
        if fn.endswith(".yaml"):
            own.update(defn.findall(read(os.path.join(dp, fn))))
ids = sorted(own, key=lambda x: int(x, 16))
if len(ids) > 0x800:
    sys.exit(f"too many records for a light plugin: {len(ids)} (limit 2048)")
mp = {old: f"{0x800 + i:06X}" for i, old in enumerate(ids)}
os.makedirs(W, exist_ok=True)
json.dump(mp, open(os.path.join(W, "map_campfire.json"), "w"), indent=0)
print(f"1. {len(ids)} records -> {mp[ids[0]]} .. {mp[ids[-1]]} ({0x800 - len(ids)} free)")

# ---- 2. the YAML
if os.path.exists(OUT):
    shutil.rmtree(OUT)
shutil.copytree(SRC, OUT)
bad = set()


def sub(t):
    def f(m):
        if m.group(1) not in mp:
            bad.add(m.group(1))
            return m.group(0)
        return mp[m.group(1)] + ":Campfire.esm"
    return ref.sub(f, t)


nchg = 0
for dp, _, fs in os.walk(OUT):
    for fn in fs:
        if fn.endswith(".yaml"):
            p = os.path.join(dp, fn)
            t = read(p)
            t2 = sub(t)
            if t2 != t:
                nchg += 1
                write(p, t2)
print(f"2. yaml files changed: {nchg}")

nm = re.compile(r"^(.* - )([0-9A-F]{6})(_Campfire\.esm(?:\.yaml)?)$")
renamed = 0
for dp, dns, fs in os.walk(OUT, topdown=False):
    for n in fs + dns:
        m = nm.match(n)
        if m and m.group(2) in mp:
            os.rename(os.path.join(dp, n), os.path.join(dp, m.group(1) + mp[m.group(2)] + m.group(3)))
            renamed += 1
print(f"   files/folders renamed: {renamed}")

rd = os.path.join(OUT, "RecordData.yaml")
t = read(rd)
nl = "\r\n" if "\r\n" in t else "\n"
if "- Small" not in t:
    assert "  Flags:" + nl + "  - Master" + nl in t, "ModHeader flags not as expected"
    t = t.replace("  Flags:" + nl + "  - Master" + nl, "  Flags:" + nl + "  - Master" + nl + "  - Small" + nl, 1)
    write(rd, t)

# ---- interior cell block folders (a cell lives in Cells/<last digit>/<second-last digit>/)
cells = os.path.join(OUT, "Cells")
tmpl = {}
for b in os.listdir(cells):
    bp = os.path.join(cells, b)
    if os.path.isdir(bp):
        tmpl["block"] = read(os.path.join(bp, "GroupRecordData.yaml"))
        for s in os.listdir(bp):
            if os.path.isdir(os.path.join(bp, s)):
                tmpl["sub"] = read(os.path.join(bp, s, "GroupRecordData.yaml"))
moves = []
for b in os.listdir(cells):
    bp = os.path.join(cells, b)
    if not os.path.isdir(bp):
        continue
    for s in os.listdir(bp):
        sp = os.path.join(bp, s)
        if not os.path.isdir(sp):
            continue
        for c in os.listdir(sp):
            cp = os.path.join(sp, c)
            if os.path.isdir(cp):
                fid = int(re.match(r"FormKey: ([0-9A-F]{6}):", read(os.path.join(cp, "RecordData.yaml"))).group(1), 16)
                nb, ns_ = str(fid % 10), str((fid // 10) % 10)
                if (nb, ns_) != (b, s):
                    moves.append((cp, nb, ns_, c))
for cp, nb, ns_, c in moves:
    dst = os.path.join(cells, nb, ns_)
    os.makedirs(dst, exist_ok=True)
    gb = os.path.join(cells, nb, "GroupRecordData.yaml")
    if not os.path.exists(gb):
        write(gb, re.sub(r"BlockNumber: \d+", f"BlockNumber: {nb}", tmpl["block"]))
    gs = os.path.join(dst, "GroupRecordData.yaml")
    if not os.path.exists(gs):
        write(gs, re.sub(r"BlockNumber: \d+", f"BlockNumber: {ns_}", tmpl["sub"]))
    shutil.move(cp, os.path.join(dst, c))
    print("   cell moved ->", f"Cells/{nb}/{ns_}/{c}")
for b in os.listdir(cells):
    bp = os.path.join(cells, b)
    if os.path.isdir(bp):
        for s in os.listdir(bp):
            sp = os.path.join(bp, s)
            if os.path.isdir(sp) and not [x for x in os.listdir(sp) if os.path.isdir(os.path.join(sp, x))]:
                shutil.rmtree(sp)
        if not [x for x in os.listdir(bp) if os.path.isdir(os.path.join(bp, x))]:
            shutil.rmtree(bp)

# ---- 3. scripts
look = re.compile(r"(GetFormFromFile\(\s*)(0x[0-9A-Fa-f]+|\d+)(\s*,\s*\"Campfire\.(?:esm|esp)\"\s*\))", re.I)
if os.path.exists(SC_OUT):
    shutil.rmtree(SC_OUT)
changed = {}
for fn in sorted(os.listdir(SC_IN)):
    if not fn.lower().endswith(".psc"):
        continue
    t = read(os.path.join(SC_IN, fn))

    def g(m):
        key = f"{int(m.group(2), 0) & 0xFFFFFF:06X}"
        if key not in mp:
            bad.add(fn + ":" + key)
            return m.group(0)
        changed.setdefault(fn, []).append(f"{key}->{mp[key]}")
        return m.group(1) + "0x" + mp[key] + m.group(3)
    t2 = look.sub(g, t)
    if t2 != t:
        write(os.path.join(SC_OUT, fn), t2)
print(f"3. scripts rewritten: {len(changed)}")
for fn, v in changed.items():
    print("   ", fn, v)

if bad:
    print("UNMAPPED:", sorted(bad))
    sys.exit(1)
print("done")
