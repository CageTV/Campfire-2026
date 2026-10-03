"""Lays out the ESL layer of Campfire 2026 (staging: package/Campfire 2026 ESL, nothing outside the workspace is touched).

Needs esl-work/esp/Campfire.esm and esl-work/pex (tools/esl_build.py, Spriggit, tools/build_scripts.py esl) and the rewritten sources in
esl-work/scripts. The layer carries only what changed (the plugin and 13 scripts); the original Campfire 1.12.1 (Nexus 667) stays installed
and supplies Campfire.bsa, the meshes and the textures. Loose scripts override the ones in the BSA.

Usage: python tools/esl_package.py
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(HERE, "esl-work")
DEST = os.path.join(HERE, "package", "Campfire 2026 ESL")
if os.path.exists(DEST):
    shutil.rmtree(DEST)
os.makedirs(os.path.join(DEST, "scripts", "source"))

shutil.copyfile(os.path.join(W, "esp", "Campfire.esm"), os.path.join(DEST, "Campfire.esm"))
pex = sorted(n for n in os.listdir(os.path.join(W, "pex")) if n.lower().endswith(".pex"))
for n in pex:
    shutil.copyfile(os.path.join(W, "pex", n), os.path.join(DEST, "scripts", n))
# the sources ship under their proper-case names
proper = {n.lower(): n for n in os.listdir(os.path.join(HERE, "src", "scripts"))}
psc = sorted(n for n in os.listdir(os.path.join(W, "scripts")) if n.lower().endswith(".psc"))
assert len(psc) == len(pex), (len(psc), len(pex))
for n in psc:
    shutil.copyfile(os.path.join(W, "scripts", n), os.path.join(DEST, "scripts", "source", proper[n.lower()]))
shutil.copyfile(os.path.join(HERE, "docs", "README-esl.txt"), os.path.join(DEST, "README.txt"))
shutil.copyfile(os.path.join(HERE, "docs", "LICENSE.txt"), os.path.join(DEST, "LICENSE.txt"))

total = 0
for dp, _, fs in os.walk(DEST):
    for f in fs:
        total += 1
sha = hashlib.sha256(open(os.path.join(DEST, "Campfire.esm"), "rb").read()).hexdigest()[:16]
print(f"{DEST}: {total} files ({len(pex)} .pex, {len(psc)} .psc); Campfire.esm sha256 {sha}...")
