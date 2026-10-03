"""Builds the single "Campfire 2026" FOMOD (package/Campfire 2026 - Installer[.zip]) that covers the regular and the ESL build.

common/ = the settings layer (package/Campfire 2026, always installed); esl/ = the ESL plugin and its 13 scripts (package/Campfire 2026 ESL,
installed only when the ESL build is chosen). Run tools/package.py and tools/esl_package.py first.
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


copy_tree(MAIN, os.path.join(DEST, "common"), skip=("README.txt", "LICENSE.txt"))
copy_tree(ESL, os.path.join(DEST, "esl"), skip=("README.txt", "LICENSE.txt"))
os.makedirs(os.path.join(DEST, "fomod"))

config = """<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">
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
              <description>The settings layer only: Campfire's options move to SKSE Menu Framework. Campfire.esm stays the original regular plugin from Campfire 1.12.1.</description>
              <conditionFlags><flag name="build">regular</flag></conditionFlags>
              <typeDescriptor><type name="Recommended"/></typeDescriptor>
            </plugin>
            <plugin name="ESL">
              <description>The settings layer plus Campfire.esm as a light (ESL) plugin: no regular plugin slot used. All 1566 records are renumbered and 13 scripts rebuilt to match. Use it for a new game only, and pick the ESL option of Frostfall 2026, Last Seed 2026 and the patches too.</description>
              <conditionFlags><flag name="build">esl</flag></conditionFlags>
              <typeDescriptor><type name="Optional"/></typeDescriptor>
            </plugin>
          </plugins>
        </group>
      </optionalFileGroups>
    </installStep>
  </installSteps>
  <conditionalFileInstalls>
    <patterns>
      <pattern>
        <dependencies><flagDependency flag="build" value="esl"/></dependencies>
        <files><folder source="esl" destination=""/></files>
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
open(os.path.join(DEST, "README.txt"), "w", encoding="utf-8", newline="\n").write(
    main_readme.rstrip() + f"\n\n\n=== ESL BUILD (choose \"ESL\" in the installer) ===\n\n" + esl_part.lstrip())
lic_main = open(os.path.join(HERE, "docs", "LICENSE-main.txt"), encoding="utf-8").read()
lic_esl = open(os.path.join(HERE, "docs", "LICENSE.txt"), encoding="utf-8").read()
open(os.path.join(DEST, "LICENSE.txt"), "w", encoding="utf-8", newline="\n").write(lic_main.rstrip() + "\n\n\n--- ESL build files ---\n\n" + lic_esl)

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
