"""Lays out the regular Campfire 2026 layer (staging: package/Campfire 2026, nothing outside the workspace is touched).

Contents: SKSE/Plugins/Campfire.dll, the rebuilt menu script (pex + source), README, LICENSE. No plugin and no assets: the original Campfire
1.12.1 supplies them. Needs plugin/build/release/Campfire.dll (plugin/build.cmd) and build/scripts (tools/build_scripts.py).

Usage: python tools/package.py
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(HERE, "package", "Campfire 2026")
if os.path.exists(DEST):
    shutil.rmtree(DEST)
os.makedirs(os.path.join(DEST, "SKSE", "Plugins"))
os.makedirs(os.path.join(DEST, "scripts", "source"))
os.makedirs(os.path.join(DEST, "Interface", "campfire"))
shutil.copyfile(os.path.join(HERE, "assets", "campfire_logo.png"), os.path.join(DEST, "Interface", "campfire", "campfire_logo.png"))

shutil.copyfile(os.path.join(HERE, "plugin", "build", "release", "Campfire.dll"), os.path.join(DEST, "SKSE", "Plugins", "Campfire.dll"))
shutil.copyfile(os.path.join(HERE, "build", "scripts", "_camp_skyuiconfigpanelscript.pex"), os.path.join(DEST, "scripts", "_camp_skyuiconfigpanelscript.pex"))
shutil.copyfile(os.path.join(HERE, "src", "scripts", "_Camp_SkyUIConfigPanelScript.psc" if os.path.exists(os.path.join(HERE, "src", "scripts", "_Camp_SkyUIConfigPanelScript.psc")) else "_camp_skyuiconfigpanelscript.psc"),
                os.path.join(DEST, "scripts", "source", "_Camp_SkyUIConfigPanelScript.psc"))
shutil.copyfile(os.path.join(HERE, "docs", "README.txt"), os.path.join(DEST, "README.txt"))
shutil.copyfile(os.path.join(HERE, "docs", "LICENSE-main.txt"), os.path.join(DEST, "LICENSE.txt"))
files = [os.path.relpath(os.path.join(dp, f), DEST) for dp, _, fs in os.walk(DEST) for f in fs]
dll = hashlib.sha256(open(os.path.join(DEST, "SKSE", "Plugins", "Campfire.dll"), "rb").read()).hexdigest()[:16]
print(f"{DEST}: {len(files)} files; Campfire.dll sha256 {dll}...")
for f in sorted(files):
    print("  ", f)
