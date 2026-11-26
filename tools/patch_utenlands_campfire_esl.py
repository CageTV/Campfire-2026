"""ESL copy of "Utenlands Nordic Tents - Campfire Addon.esp" (Nexus 121203) for the ESL Campfire 2026.

The original masters Campfire.esm with its ORIGINAL FormIDs; in the ESL Campfire (0x201) those land on other records
or on none. Same method as patches_esl.py: Spriggit export -> rewrite every NNNNNN:Campfire.esm through
esl-work/map_campfire.json -> rebuild -> export the rebuild and compare with the rewritten yaml (lossy round trip check).
Nothing in the install is modified; output in esl-work/patches_utenlands/.

Usage: python tools/patch_utenlands_campfire_esl.py <original esp>
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(HERE, "work", "patches_utenlands")
OUT = os.path.join(HERE, "esl-work", "patches_utenlands")
NAME = "Utenlands Nordic Tents - Campfire Addon.esp"
mp = json.load(open(os.path.join(HERE, "esl-work", "map_campfire.json")))
ref = re.compile(r"\b([0-9A-F]{6}):Campfire\.esm")
VER = "0.41.0"


def spriggit(*args):
    r = subprocess.run(["spriggit", *args], capture_output=True, text=True)
    if r.returncode != 0 or "Error:" in r.stdout:
        sys.exit("spriggit failed: " + (r.stdout + r.stderr)[-1500:])


def tree(d):
    out = {}
    for root, _, files in os.walk(d):
        for f in files:
            if f.endswith(".yaml"):
                p = os.path.join(root, f)
                out[os.path.relpath(p, d)] = open(p, encoding="utf-8").read().replace("\r", "")
    return out


def main(src):
    for d in (W, OUT):
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)
    y0, y1, y2 = (os.path.join(W, n) for n in ("y_original", "y_remapped", "y_roundtrip"))
    spriggit("serialize", "-i", src, "-o", y0, "-g", "SkyrimSE", "-p", "Spriggit.Yaml.Skyrim", "--PackageVersion", VER)
    shutil.copytree(y0, y1)
    changed, missing = 0, set()
    for rel, text in tree(y1).items():
        def sub(m):
            nonlocal changed
            new = mp.get(m.group(1))
            if new is None:
                missing.add(m.group(1))
                return m.group(0)
            changed += 1
            return new + ":Campfire.esm"
        new = ref.sub(sub, text)
        if new != text:
            open(os.path.join(y1, rel), "w", encoding="utf-8", newline="\n").write(new)
    if missing:
        sys.exit("not in the map: " + ", ".join(sorted(missing)))
    out = os.path.join(OUT, NAME)
    spriggit("deserialize", "-i", y1, "-o", out)
    spriggit("serialize", "-i", out, "-o", y2, "-g", "SkyrimSE", "-p", "Spriggit.Yaml.Skyrim", "--PackageVersion", VER)
    a, b = tree(y1), tree(y2)
    diff = [k for k in set(a) | set(b) if a.get(k) != b.get(k) and not k.endswith("RecordData.yaml")]
    left = sum(len(ref.findall(t)) for t in b.values())
    remaining_old = [m for t in b.values() for m in ref.findall(t) if m in mp and m not in mp.values()]
    print(f"references rewritten: {changed}; files: {len(a)}; round-trip differences: {len(diff)} {diff[:5]}")
    print(f"Campfire references in the rebuilt plugin: {left}; still an original id: {len(remaining_old)}")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main(sys.argv[1])
