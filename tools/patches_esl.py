"""Builds and verifies the ESL copies of the Campfire compatibility patches.

For each patch plugin (a regular original plus, where one exists, an earlier ESL copy):
  1. serializes the original with Spriggit (work/patches/y_<tag>),
  2. rewrites every NNNNNN:Campfire.esm reference with esl-work/map_campfire.json (the map the ESL Campfire plugin was built with),
  3. deserializes the result to esl-work/patches/<plugin> (same file name),
  4. re-serializes that and compares it with step 2, so a lossy round trip is caught,
  5. checks the existing ESL copy (the "Campfire ESL - Patch Remaps" mod) against step 2 as well, record by record.
Nothing in the install is modified. Usage: python tools/patches_esl.py
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODS = r"E:\Tabula Rasa\mods"
SPRIGGIT = os.path.join(MODS, "Skyrim-Claude Code Modder's Toolkit", "tools", "spriggit-cli.sh")
W = os.path.join(HERE, "work", "patches2")
OUT = os.path.join(HERE, "esl-work", "patches")
mp = json.load(open(os.path.join(HERE, "esl-work", "map_campfire.json")))
ref = re.compile(r"\b([0-9A-F]{6}):Campfire\.esm")

# plugin file name -> (mod folder holding the regular original, mod folder holding an earlier ESL copy or None)
PATCHES = {
    "Fishing Campfire Patch.esp": ("Campfire CC fish cooking", None),
    "CampfireDynamicActivate.esp": ("Campfire - Dynamic Activation Key", None),
    "Campfire Animal Meat Recipe.esp": ("Simple Hunt Overhaul and Campfire cooking patch", "Campfire ESL - Patch Remaps"),
    "EmbersXD-Campfire Patch.esp": ("Miscellaneous Embers XD Patches", "Campfire ESL - Patch Remaps"),
    "Immersive Barrels - Campfire.esp": ("Immersive Barrels - Base Object Swapper", "Campfire ESL - Patch Remaps"),
    "LoS II - Campfire addon.esp": ("Lanterns Of Skyrim II", "Campfire ESL - Patch Remaps"),
    "Northern Concept - Northern Roads - Campfire patch.esp": ("Northern Concept - Northern Roads", "Campfire ESL - Patch Remaps"),
    "Simple Food and Hunting Overhaul - Campfire.esp": ("Simple Food Hunting and Cooking Overhaul", "Campfire ESL - Patch Remaps"),
    "Use Those Blankets - Campfire Patch.esp": ("Use Those Blankets Campfire Patch", "Campfire ESL - Patch Remaps"),
}


def spriggit(*args):
    r = subprocess.run(["bash", SPRIGGIT, *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("spriggit failed: " + " ".join(args) + "\n" + (r.stdout + r.stderr)[-600:])


def serialize(plugin_path, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    stage = os.path.join(W, "stage", os.path.basename(plugin_path))
    os.makedirs(os.path.dirname(stage), exist_ok=True)
    shutil.copyfile(plugin_path, stage)
    spriggit("serialize", "--InputPath", stage, "--OutputPath", dest, "--GameRelease", "SkyrimSE", "--PackageName", "Spriggit.Yaml", "--PackageVersion", "0.41.0")


def read(p):
    with open(p, encoding="utf-8", errors="replace", newline="") as f:
        return f.read()


def norm_tree(root):
    """{relative path: sorted non-empty lines} with -0 normalised, so list order and negative zero do not count as differences."""
    out = {}
    for dp, _, fs in os.walk(root):
        for fn in fs:
            if fn.endswith(".yaml"):
                p = os.path.join(dp, fn)
                lines = sorted(l.strip().replace(", -0,", ", 0,") for l in read(p).replace("\r", "").split("\n") if l.strip())
                # records that override Campfire's carry its FormID in the file name, which differs by build: key on the name without it
                out[re.sub(r" - [0-9A-F]{6}_Campfire", " - _Campfire", os.path.relpath(p, root))] = lines
    return out


def remap_tree(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    bad = set()
    refs = 0
    for dp, _, fs in os.walk(dst):
        for fn in fs:
            if fn.endswith(".yaml"):
                p = os.path.join(dp, fn)
                t = read(p)

                def f(m):
                    global refs
                    if m.group(1) not in mp:
                        bad.add(m.group(1))
                        return m.group(0)
                    return mp[m.group(1)] + ":Campfire.esm"
                t2 = ref.sub(f, t)
                refs += len(ref.findall(t))
                if t2 != t:
                    with open(p, "w", encoding="utf-8", newline="") as o:
                        o.write(t2)
    return bad, refs


os.makedirs(OUT, exist_ok=True)
failed = False
for plugin, (orig_mod, esl_mod) in PATCHES.items():
    tag = re.sub(r"[^A-Za-z0-9]+", "_", plugin[:-4])
    orig_path = os.path.join(MODS, orig_mod, plugin)
    y_orig = os.path.join(W, "y_" + tag)
    serialize(orig_path, y_orig)
    y_map = os.path.join(W, "ymap_" + tag)
    bad, refs = remap_tree(y_orig, y_map)
    if bad:
        print(f"{plugin}: UNMAPPED Campfire ids {sorted(bad)}")
        failed = True
        continue
    # (3) the ESL copy
    out_plugin = os.path.join(OUT, plugin)
    if os.path.exists(out_plugin):
        os.remove(out_plugin)
    tmp_dir = os.path.join(W, "deser_" + tag)
    os.makedirs(tmp_dir, exist_ok=True)
    spriggit("deserialize", "--InputPath", y_map, "--OutputPath", os.path.join(tmp_dir, plugin))
    shutil.copyfile(os.path.join(tmp_dir, plugin), out_plugin)
    # (4) round trip of our output
    y_back = os.path.join(W, "yback_" + tag)
    serialize(out_plugin, y_back)
    ok_round = norm_tree(y_back) == norm_tree(y_map)
    # (5) the earlier ESL copy
    note = ""
    if esl_mod:
        y_old = os.path.join(W, "yold_" + tag)
        serialize(os.path.join(MODS, esl_mod, plugin), y_old)
        same_old = norm_tree(y_old) == norm_tree(y_map)
        note = f"earlier ESL copy identical: {same_old}"
        if not same_old:
            failed = True
    print(f"{plugin:58} refs remapped: {refs:3}  round trip ok: {ok_round}  {note}")
    if not ok_round:
        failed = True
print("FAILED" if failed else "all ok")
sys.exit(1 if failed else 0)
