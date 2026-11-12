"""ESL copy of Embers XD's own 'Embers XD - Patch - Campfire.esp' (the heat-source list patch).

The original edits Campfire's _Camp_HeatSources_* lists using the ORIGINAL Campfire FormIDs; the ESL Campfire renumbers them
(esl-work/map_campfire.json), so the original resolves to wrong records. This serializes the original with Spriggit, rewrites
every NNNNNN:Campfire.esm reference with the map, deserializes, then re-serializes and compares (lossy round trip = failure).
Reads the original from the user's Embers XD mod folder; writes only under esl-work/patches_embers and work/patches_embers.
Usage: python tools/patch_embers_campfire_esl.py [original.esp]   (env SPRIGGIT_WRAPPER: see sp())
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLKIT = "E:/Tabula Rasa/mods/Skyrim-Claude Code Modder's Toolkit"
GITBASH = "C:/Program Files/Git/bin/bash.exe"
SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:\Modlists\Tabula\mods\Embers XD\Embers XD - Patch - Campfire.esp"
NAME = os.path.basename(SRC)
W = os.path.join(HERE, "work", "patches_embers")
OUT = os.path.join(HERE, "esl-work", "patches_embers")
mp = json.load(open(os.path.join(HERE, "esl-work", "map_campfire.json")))
ref = re.compile(r"\b([0-9A-F]{6}):Campfire\.esm")


def sp(*args):
    # Spriggit through the toolkit wrapper. SPRIGGIT_WRAPPER can point at a copy of tools/spriggit-cli.sh whose SCRIPT_DIR is a Windows-style
    # path (the stock wrapper derives /e/... through pwd, which the native Python it starts cannot open from a Python-launched Git Bash).
    wrapper = os.environ.get("SPRIGGIT_WRAPPER", TOOLKIT + "/tools/spriggit-cli.sh")
    q = ["'" + a.replace("\\", "/").replace("'", "'\\''") + "'" for a in args]
    cmd = "cd '" + TOOLKIT.replace("'", "'\\''") + "' && bash '" + wrapper + "' " + " ".join(q)
    r = subprocess.run([GITBASH, "-c", cmd], capture_output=True, text=True)
    if r.returncode:
        sys.exit("spriggit failed: " + " ".join(args) + "\n" + (r.stdout + r.stderr)[-800:])


def rd(p):
    with open(p, encoding="utf-8", errors="replace", newline="") as f:
        return f.read()


def ser(plugin, dest):
    sp("serialize", "--InputPath", plugin, "--OutputPath", dest, "--GameRelease", "SkyrimSE", "--PackageName", "Spriggit.Yaml", "--PackageVersion", "0.41.0")


shutil.rmtree(W, ignore_errors=True)
os.makedirs(os.path.join(W, "stage"))
os.makedirs(OUT, exist_ok=True)
stage = os.path.join(W, "stage", NAME)
shutil.copyfile(SRC, stage)
y0 = os.path.join(W, "y_orig")
ser(stage, y0)
y1 = os.path.join(W, "y_map")
shutil.copytree(y0, y1)
bad, n = set(), 0
for dp, _, fs in os.walk(y1):
    for fn in fs:
        p = os.path.join(dp, fn)
        if not fn.endswith(".yaml"):
            continue
        t = rd(p)

        def f(m):
            global n
            if m.group(1) not in mp:
                bad.add(m.group(1))
                return m.group(0)
            n += 1
            return mp[m.group(1)] + ":Campfire.esm"
        t2 = ref.sub(f, t)
        if t2 != t:
            with open(p, "w", encoding="utf-8", newline="") as o:
                o.write(t2)
        # record file names carry the FormID too
        nn = re.sub(r"( - )([0-9A-F]{6})(_Campfire\.esm)", lambda m: m.group(1) + mp.get(m.group(2), m.group(2)) + m.group(3), fn)
        if nn != fn:
            os.rename(p, os.path.join(dp, nn))
print("references remapped:", n, "unmapped:", sorted(bad))
if bad:
    sys.exit(1)
out = os.path.join(OUT, NAME)
if os.path.exists(out):
    os.remove(out)
tmp = os.path.join(W, "deser")
os.makedirs(tmp)
sp("deserialize", "--InputPath", y1, "--OutputPath", os.path.join(tmp, NAME))
shutil.copyfile(os.path.join(tmp, NAME), out)
rt = os.path.join(W, "stage", "rt", NAME)
os.makedirs(os.path.dirname(rt))
shutil.copyfile(out, rt)
y2 = os.path.join(W, "y_roundtrip")
ser(rt, y2)


def tree(root):
    o = {}
    for dp, _, fs in os.walk(root):
        for fn in fs:
            if fn.endswith(".yaml"):
                o[fn] = sorted(l.strip().replace(", -0,", ", 0,") for l in rd(os.path.join(dp, fn)).replace("\r", "").split("\n") if l.strip())
    return o


a, b = tree(y1), tree(y2)
diff = [k for k in set(a) | set(b) if a.get(k) != b.get(k)]
print("round trip differences:", diff or "none")
print("wrote", out, os.path.getsize(out), "bytes")
