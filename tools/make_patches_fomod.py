"""Builds the "Campfire 2026 - Patches" FOMOD (package/Campfire 2026 - Patches[.zip]).

One installer for both Campfire 2026 builds: the first page asks whether the regular or the ESL build is installed, the second lists the
patches. Each patch is the author's own plugin (open permissions, per the user) -- the regular copy is the original byte for byte, the ESL copy
is the same plugin with its Campfire references renumbered by tools/patches_esl.py (esl-work/patches).

Usage: python tools/make_patches_fomod.py [version]
"""
import configparser
import os
import shutil
import sys
import zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODS = r"E:\Tabula Rasa\mods"
VERSION = sys.argv[1] if len(sys.argv) > 1 else "1.0.0"
DEST = os.path.join(HERE, "package", "Campfire 2026 - Patches")
ESL = os.path.join(HERE, "esl-work", "patches")

# key, plugin, source mod folder (original), title, for-which-mod, requires, notes
PATCHES = [
    ("fish", "Fishing Campfire Patch.esp", "Campfire CC fish cooking", "Creation Club Fishing - cooked fish at the campfire",
     "Adds a cooking recipe at the campfire for each of the 24 Creation Club fish (raw fish in, cooked fish out). Hidden while Complete Alchemy and Cooking Overhaul is installed.",
     "Creation Club: Fishing (ccBGSSSE001-Fish.esm)",
     "Replaces the older \"Campfire - Fishing Patch\" (the same recipes for 21 fish, without Angler, Salmon and Slaughterfish). Do not use both: the recipes would appear twice."),
    ("dak", "CampfireDynamicActivate.esp", "Campfire - Dynamic Activation Key", "Dynamic Activation Key",
     "Lets Dynamic Activation Key add fuel and tinder to campfires, light them, warm your hands at them and use Campfire's tents. Includes its scripts, an Open Animation Replacer warming-hands animation and a SkyPatcher tinder list.",
     "Dynamic Activation Key (Nexus 124401's parent mod), Open Animation Replacer for the animation",
     "Includes a replacement of Campfire's _Camp_UpliftedTriggerVolumeScript, so install it after Campfire 2026 and Campfire - Script Optimization."),
    ("meat", "Campfire Animal Meat Recipe.esp", "Simple Hunt Overhaul and Campfire cooking patch", "Simple Hunting Overhaul - campfire cooking",
     "Campfire cooking recipe for the meat added by Simple Hunting Overhaul.", "Simple Hunting Overhaul", ""),
    ("embers", "EmbersXD-Campfire Patch.esp", "Miscellaneous Embers XD Patches", "Embers XD",
     "Gives Campfire's burning campfire pieces (embers and the lit fuel stages) the Embers XD fire effects.", "Embers XD", ""),
    ("barrels", "Immersive Barrels - Campfire.esp", "Immersive Barrels - Base Object Swapper", "Immersive Barrels",
     "Makes Campfire's supply barrels and containers match the Immersive Barrels models.", "Immersive Barrels", ""),
    ("los", "LoS II - Campfire addon.esp", "Lanterns Of Skyrim II", "Lanterns of Skyrim II",
     "Gives Campfire's lanterns and lights the Lanterns of Skyrim II lighting.", "Lanterns of Skyrim II", ""),
    ("embershl", "Embers XD - Patch - Campfire.esp", "Embers XD", "Embers XD - heat sources",
     "Adds Embers XD's fires to Campfire's heat source lists, so Frostfall treats them as warm.", "Embers XD",
     "This is the plugin Embers XD ships itself, renumbered for the ESL Campfire. Frostfall 2026 already covers Embers XD through its own Frostfall_Embers_FLM.ini, so you only need this one for the Embers XD heat-source lists without Frostfall 2026. Keep only one copy of this file active."),
    ("hunterborn", "Hunterborn - Campfire Patch.esp", "Hunterborn", "Hunterborn",
     "Makes Hunterborn's campfire cooking work with Campfire's cooking pot and campfire.", "Hunterborn (the Nexus mod)",
     "Not needed with Hunterborn 2026, whose own ESL edition already carries this patch."),
    ("sotw", "SkillsOfTheWild.esp", "Skills of the Wild - New Campfire Survival Skill Trees", "Skills of the Wild (ESL build only)",
     "The Skills of the Wild plugin with its Campfire references renumbered for the ESL Campfire. Install it over the original Skills of the Wild.",
     "Skills of the Wild (Nexus 37693)",
     "ESL build only: with the regular build nothing is installed, the original plugin is already right. It is the same file that ships in Skills of the Wild 2026, so skip it if you use that."),
    ("roads", "Northern Concept - Northern Roads - Campfire patch.esp", "Northern Concept - Northern Roads", "Northern Roads",
     "Fixes how Campfire's placed objects sit on the Northern Roads road meshes.", "Northern Roads", ""),
    ("sfho", "Simple Food and Hunting Overhaul - Campfire.esp", "Simple Food Hunting and Cooking Overhaul", "Simple Food and Hunting Overhaul",
     "Brings Simple Food and Hunting Overhaul's food and recipes to Campfire's cooking pot and campfire.", "Simple Food and Hunting Overhaul", ""),
    ("blankets", "Use Those Blankets - Campfire Patch.esp", "Use Those Blankets Campfire Patch", "Use Those Blankets",
     "Lets Use Those Blankets treat Campfire's bedrolls and tents as sleeping spots.", "Use Those Blankets", ""),
]
HLIST = r"H:\Modlists\Tabula\mods"
ROOT = {"embershl": HLIST, "hunterborn": HLIST, "sotw": HLIST}  # source mod folders that are not in the old E: instance
ESL_DIR = {k: os.path.join(HERE, "esl-work", "patches_embers") for k in ("embershl", "hunterborn", "sotw")}
ESL_ONLY = {"sotw"}  # nothing to install for the regular build
# the shared (build-independent) files of a patch: everything in its mod folder except the plugin and MO2's meta.ini
EXTRA_DIRS = {"dak": "Campfire - Dynamic Activation Key"}

if os.path.exists(DEST):
    shutil.rmtree(DEST)
os.makedirs(os.path.join(DEST, "fomod"))


# The old E: instance folders the original nine patches came from are gone; the previous release's package holds their plugins
# (the regular ones are the authors' originals) and the DAK extras. Fallback root: the extracted "Campfire 2026 - Patches 1.0.0" zip.
OLD = os.environ.get("PATCHES_OLD_PKG", "")


def put(src, rel):
    if not os.path.exists(src) and OLD:
        src = os.path.join(OLD, rel)
    dst = os.path.join(DEST, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)


nexus = {}
for key, plugin, mod, title, what, req, note in PATCHES:
    root = ROOT.get(key, MODS)
    if key not in ESL_ONLY:
        put(os.path.join(root, mod, plugin), f"regular/{plugin}")
    put(os.path.join(ESL_DIR.get(key, ESL), plugin), f"esl/{plugin}")
    ini = configparser.ConfigParser()
    ini.read(os.path.join(root, mod, "meta.ini"), encoding="utf-8")
    nexus[key] = ini.get("General", "modid", fallback="?")
    if nexus[key] == "?" and OLD and os.path.exists(os.path.join(OLD, "README.txt")):
        for line in open(os.path.join(OLD, "README.txt"), encoding="utf-8"):
            if line.strip().startswith(title + ":"):
                nexus[key] = line.strip().rsplit("/", 1)[-1]
for key, mod in EXTRA_DIRS.items():
    root = os.path.join(MODS, mod)
    if not os.path.isdir(root) and OLD:
        for dp, _, fs in os.walk(os.path.join(OLD, "common", key)):
            for fn in fs:
                p = os.path.join(dp, fn)
                put(p, f"common/{key}/{os.path.relpath(p, os.path.join(OLD, 'common', key))}")
        continue
    for dp, _, fs in os.walk(root):
        for fn in fs:
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, root)
            if fn.lower() in ("meta.ini",) or fn.lower().endswith((".esp", ".esm", ".esl")):
                continue
            put(p, f"common/{key}/{rel}")


def flags_step():
    return """    <installStep name="Campfire 2026 build">
      <optionalFileGroups>
        <group name="Which Campfire 2026 do you use?" type="SelectExactlyOne">
          <plugins order="Explicit">
            <plugin name="Regular">
              <description>Campfire.esm as a normal master (Campfire 2026 with the original plugin). Installs the original patch plugins.</description>
              <conditionFlags><flag name="build">regular</flag></conditionFlags>
              <typeDescriptor><type name="Recommended"/></typeDescriptor>
            </plugin>
            <plugin name="ESL">
              <description>Campfire.esm as a light (ESL) plugin (Campfire 2026 ESL). Installs the patch plugins with their Campfire references renumbered to match it.</description>
              <conditionFlags><flag name="build">esl</flag></conditionFlags>
              <typeDescriptor><type name="Optional"/></typeDescriptor>
            </plugin>
          </plugins>
        </group>
      </optionalFileGroups>
    </installStep>
"""


def patches_step():
    out = ['    <installStep name="Patches">', "      <optionalFileGroups>", '        <group name="Pick the patches for the mods you use" type="SelectAny">', '          <plugins order="Explicit">']
    for key, plugin, mod, title, what, req, note in PATCHES:
        desc = f"{what}\n\nRequires: {req}." + (f"\n\n{note}" if note else "")
        out += [f'            <plugin name="{escape(title)}">', f"              <description>{escape(desc)}</description>",
                f'              <conditionFlags><flag name="p_{key}">on</flag></conditionFlags>',
                '              <typeDescriptor><type name="Optional"/></typeDescriptor>', "            </plugin>"]
    out += ["          </plugins>", "        </group>", "      </optionalFileGroups>", "    </installStep>"]
    return "\n".join(out) + "\n"


def conditional():
    out = ["  <conditionalFileInstalls>", "    <patterns>"]
    for key, plugin, *_ in PATCHES:
        for build in ("regular", "esl"):
            if build == "regular" and key in ESL_ONLY:
                continue
            out += ["      <pattern>", "        <dependencies operator=\"And\">", f'          <flagDependency flag="build" value="{build}"/>',
                    f'          <flagDependency flag="p_{key}" value="on"/>', "        </dependencies>",
                    f'        <files><file source="{build}\\{escape(plugin)}" destination="{escape(plugin)}"/></files>', "      </pattern>"]
        if key in EXTRA_DIRS:
            out += ["      <pattern>", "        <dependencies>", f'          <flagDependency flag="p_{key}" value="on"/>', "        </dependencies>",
                    f'        <files><folder source="common\\{key}" destination=""/></files>', "      </pattern>"]
    out += ["    </patterns>", "  </conditionalFileInstalls>"]
    return "\n".join(out) + "\n"


config = ('<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://qconsulting.ca/fo3/ModConfig5.0.xsd">\n'
          "  <moduleName>Campfire 2026 - Patches</moduleName>\n  <installSteps order=\"Explicit\">\n" + flags_step() + patches_step() + "  </installSteps>\n" + conditional() + "</config>\n")
with open(os.path.join(DEST, "fomod", "ModuleConfig.xml"), "w", encoding="utf-8", newline="\n") as f:
    f.write(config)
with open(os.path.join(DEST, "fomod", "info.xml"), "w", encoding="utf-8", newline="\n") as f:
    f.write(f'<fomod>\n  <Name>Campfire 2026 - Patches</Name>\n  <Author>CageTV</Author>\n  <Version>{VERSION}</Version>\n'
            "  <Description>Compatibility patches for Campfire 2026, regular and ESL, in one installer.</Description>\n</fomod>\n")

credits = "\n".join(f"  {title}: patch plugin by its author; source mod page on Nexus: https://www.nexusmods.com/skyrimspecialedition/mods/{nexus[key]}"
                    for key, plugin, mod, title, what, req, note in PATCHES)
with open(os.path.join(DEST, "README.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write(f"""Campfire 2026 - Patches {VERSION}

WHAT THIS IS
------------
One installer for the compatibility patches of Campfire 2026, in both builds. It asks which build you use (regular or ESL), then which
patches you want. Pick only the patches for mods you actually have: each one needs the mod it is for.

The patch plugins are the original authors' work, included with their open permissions, unchanged. For the ESL build each plugin is the same
plugin with only its references to Campfire.esm renumbered to the ESL Campfire's FormIDs (done by tool and checked record by record); nothing
else in them changed.

USE
---
Install after Campfire 2026 (or Campfire 2026 ESL). Do not combine the regular and ESL patches, and do not use these together with the
patch's own download or with "CAMPFIRE ESL UPDATED" / "Campfire ESL - Patch Remaps".
If the patch's mod already ships the same plugin file name (several are bundled inside their parent mod), keep only one copy active.

The "Fishing" patch replaces the older "Campfire - Fishing Patch": use one of them, not both.

CREDITS
-------
{credits}
Campfire is by Chesko (MIT).
""")

zpath = DEST + ".zip"
if os.path.exists(zpath):
    os.remove(zpath)
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, _, fs in os.walk(DEST):
        for fn in fs:
            p = os.path.join(dp, fn)
            z.write(p, os.path.relpath(p, DEST))
files = [os.path.relpath(os.path.join(dp, f), DEST) for dp, _, fs in os.walk(DEST) for f in fs]
print(f"{DEST}: {len(files)} files, zip {os.path.getsize(zpath)//1024} KB")
