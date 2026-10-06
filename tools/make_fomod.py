"""Builds the single "Campfire 2026" FOMOD (package/Campfire 2026 - Installer[.zip]) that covers the regular and the ESL build.

common/ = the settings layer (package/Campfire 2026, always installed); esl/ = the ESL plugin and its 13 scripts (package/Campfire 2026 ESL,
installed only when the ESL build is chosen); regular/ = the regular Campfire.esm (original numbering, work/stage/regular), installed only when the
regular build is chosen: it overrides Chesko's plugin and adds the Salvage recipes, his download stays required for the BSA, meshes and textures.
Run tools/package.py and tools/esl_package.py first.
Campfire.dll is not taken from the package: a second install step asks which SKSE library it is built on, "new" (alandtse's CommonLibSSE-NG, Skyrim
1.6.1170 and newer) or "older" (CharmedBaryon's, Skyrim VR and 1.6.1130 and older), and new/ or older/ is installed accordingly.
Usage: python tools/make_fomod.py [version]
"""
import os
import shutil
import sys
import zipfile
import xml.dom.minidom

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = sys.argv[1] if len(sys.argv) > 1 else "1.0.0"
DEST = os.path.join(HERE, "package", "Campfire 2026 - Installer")
MAIN = os.path.join(HERE, "package", "Campfire 2026")
ESL = os.path.join(HERE, "package", "Campfire 2026 ESL")
DLLS = {"new": os.path.join(HERE, "plugin-ng", "build", "release", "Campfire.dll"),
        "older": os.path.join(HERE, "plugin", "build", "release", "Campfire.dll")}
for _k, _d in DLLS.items():
    assert os.path.isfile(_d), f"missing {_k} DLL: {_d}"
NEW_VER = "1.6.1170.0"
if os.path.exists(DEST):
    shutil.rmtree(DEST)


def copy_tree(src, dst, skip=()):
    for dp, _, fs in os.walk(src):
        for fn in fs:
            if fn in skip:
                continue
            p = os.path.join(dp, fn)
            t = os.path.join(dst, os.path.relpath(p, src))
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.copyfile(p, t)


copy_tree(MAIN, os.path.join(DEST, "common"), skip=("README.txt", "LICENSE.txt", "Campfire.dll"))
for _k, _d in DLLS.items():
    os.makedirs(os.path.join(DEST, _k, "SKSE", "Plugins"))
    shutil.copyfile(_d, os.path.join(DEST, _k, "SKSE", "Plugins", "Campfire.dll"))
copy_tree(ESL, os.path.join(DEST, "esl"), skip=("README.txt", "LICENSE.txt"))
REG = os.path.join(HERE, "work", "stage", "regular", "Campfire.esm")
assert os.path.isfile(REG), f"missing regular plugin: {REG}"
os.makedirs(os.path.join(DEST, "regular"))
shutil.copyfile(REG, os.path.join(DEST, "regular", "Campfire.esm"))
os.makedirs(os.path.join(DEST, "fomod"))

config = f"""<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">
  <moduleName>Campfire 2026</moduleName>
  <requiredInstallFiles>
    <folder source="common" destination=""/>
    <file source="README.txt" destination="Campfire 2026 README.txt"/>
    <file source="LICENSE.txt" destination="Campfire 2026 LICENSE.txt"/>
  </requiredInstallFiles>
  <installSteps order="Explicit">
    <installStep name="Build">
      <optionalFileGroups>
        <group name="Which Campfire do you want?" type="SelectExactlyOne">
          <plugins order="Explicit">
            <plugin name="Regular">
              <description>The settings layer plus the Salvage recipes (tear leather gear and clothes into scraps or Leather and Linen Wraps, patchwork tents). Campfire.esm is a regular plugin that overrides Chesko's: same records, same ids, plus 84 new ones, so an existing save keeps working. The original Campfire 1.12.1 stays required for its meshes, textures and sounds.</description>
              <conditionFlags><flag name="build">regular</flag></conditionFlags>
              <typeDescriptor><type name="Recommended"/></typeDescriptor>
            </plugin>
            <plugin name="ESL">
              <description>The settings layer plus Campfire.esm as a light (ESL) plugin: no regular plugin slot used. All 1650 records (Campfire's own plus the Salvage recipes) are renumbered and 13 scripts rebuilt to match. Use it for a new game only, and pick the ESL option of Frostfall 2026, Last Seed 2026 and the patches too.</description>
              <conditionFlags><flag name="build">esl</flag></conditionFlags>
              <typeDescriptor><type name="Optional"/></typeDescriptor>
            </plugin>
          </plugins>
        </group>
      </optionalFileGroups>
    </installStep>
    <installStep name="Game version">
      <optionalFileGroups order="Explicit">
        <group name="Which Campfire.dll do you want?" type="SelectExactlyOne">
          <plugins order="Explicit">
            <plugin name="Skyrim 1.6.1170 and newer (SE / AE)">
              <description>The new build. Works on Skyrim SE/AE 1.6.1170 and on every later version, including 1.7.x. Pre-selected when the installer sees a game version of 1.6.1170 or newer.</description>
              <conditionFlags><flag name="dll">new</flag></conditionFlags>
              <typeDescriptor><dependencyType><defaultType name="Optional"/><patterns>
                <pattern><dependencies><gameDependency version="{NEW_VER}"/></dependencies><type name="Recommended"/></pattern>
              </patterns></dependencyType></typeDescriptor>
            </plugin>
            <plugin name="Skyrim VR, or 1.6.1130 and older">
              <description>The older build, for Skyrim VR and for SE/AE 1.6.1130 and older. Pre-selected when the installer sees an older game version or Skyrim VR. On 1.6.1170 either build works.</description>
              <conditionFlags><flag name="dll">older</flag></conditionFlags>
              <typeDescriptor><dependencyType><defaultType name="Recommended"/><patterns>
                <pattern><dependencies><gameDependency version="{NEW_VER}"/></dependencies><type name="Optional"/></pattern>
              </patterns></dependencyType></typeDescriptor>
            </plugin>
          </plugins>
        </group>
      </optionalFileGroups>
    </installStep>
  </installSteps>
  <conditionalFileInstalls>
    <patterns>
      <pattern>
        <dependencies><flagDependency flag="build" value="regular"/></dependencies>
        <files><folder source="regular" destination=""/></files>
      </pattern>
      <pattern>
        <dependencies><flagDependency flag="build" value="esl"/></dependencies>
        <files><folder source="esl" destination=""/></files>
      </pattern>
      <pattern>
        <dependencies><flagDependency flag="dll" value="new"/></dependencies>
        <files><folder source="new" destination=""/></files>
      </pattern>
      <pattern>
        <dependencies><flagDependency flag="dll" value="older"/></dependencies>
        <files><folder source="older" destination=""/></files>
      </pattern>
    </patterns>
  </conditionalFileInstalls>
</config>
"""
info = (f"<fomod>\n  <Name>Campfire 2026</Name>\n  <Author>CageTV (Campfire by Chesko)</Author>\n  <Version>{VERSION}</Version>\n"
        "  <Website>https://github.com/CageTV/Campfire-2026</Website>\n"
        "  <Description>Campfire's settings in SKSE Menu Framework, with an optional ESL build, in one installer.</Description>\n</fomod>\n")
xml.dom.minidom.parseString(config)
xml.dom.minidom.parseString(info)
open(os.path.join(DEST, "fomod", "ModuleConfig.xml"), "w", encoding="utf-8", newline="\n").write(config)
open(os.path.join(DEST, "fomod", "info.xml"), "w", encoding="utf-8", newline="\n").write(info)

main_readme = open(os.path.join(HERE, "docs", "README.txt"), encoding="utf-8").read()
esl_readme = open(os.path.join(HERE, "docs", "README-esl.txt"), encoding="utf-8").read()
esl_part = esl_readme.split("\n", 2)[2] if esl_readme.startswith("Campfire 2026") else esl_readme
esl_part = esl_part.replace("- Campfire 2026 (the settings layer, with Campfire.dll) and the original", "- The original")
esl_part = esl_part.replace("Install after (below) the original Campfire and Campfire 2026 in MO2's left pane", "Install after (below) the original Campfire in MO2's left pane")
open(os.path.join(DEST, "README.txt"), "w", encoding="utf-8", newline="\n").write(
    "Campfire 2026 installer: it asks Regular or ESL, then which Campfire.dll (new: Skyrim 1.6.1170 and newer; older: Skyrim VR or 1.6.1130 and older; both work on 1.6.1170).\n\n"
    + main_readme.rstrip() + f"\n\n\n=== ESL BUILD (choose \"ESL\" in the installer) ===\n\n" + esl_part.lstrip())
shutil.copyfile(os.path.join(HERE, "LICENSE.txt"), os.path.join(DEST, "LICENSE.txt"))

zpath = DEST + ".zip"
if os.path.exists(zpath):
    os.remove(zpath)
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(DEST):
        for fn in fs:
            p = os.path.join(dp, fn)
            z.write(p, os.path.relpath(p, DEST))
    names = z.namelist()
print(f"{zpath}: {len(names)} entries, {os.path.getsize(zpath)//1024} KB")
for n in sorted(names):
    print("  ", n)
