"""Adds the Salvage recipes (leather/cloth tearing, scraps, patchwork tents) to Campfire 2026's source YAML.

Source of truth is src/esp/Campfire (Spriggit YAML, ORIGINAL numbering). New records get ids from 07D000 up, above the highest id Campfire
already uses (07C405), so tools/esl_build.py keeps every existing record's ESL number and the dependants (Frostfall, Last Seed, patches)
need no rebuild. Both builds (regular + ESL) come from this one source.

What it does (idempotent: run it again any time, it first removes its own _CampSalv_ records):
  1. MISC Leather Scrap + Cloth Scrap (vanilla meshes by path, nothing packed), FLST _CampSalv_Knives (8 vanilla daggers, no DLC master)
  2. Leather-family gear (Leather, Hide, Imperial Light, Studded Armor): bare hands -> scraps, knife in bag -> Leather
  3. Campfire's own 48 cloth tear recipes: now require a knife (they keep making Linen Wrap); a bare-hands twin makes Cloth Scrap
  4. scrap conversions (3 -> Strips / 8 -> Leather / 3 cloth -> Linen Wrap / 2 -> 2 Kindling) and patchwork leather tents at the tanning rack

Usage: python tools/salvage_build.py [--dry]
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "src", "esp", "Campfire")
CO = os.path.join(SRC, "ConstructibleObjects")
DRY = "--dry" in sys.argv

# ---- Campfire / Skyrim ids (ORIGINAL numbering)
KW_SURVIVAL = "019831:Campfire.esm"      # ESL 000806
KW_CAMPFIRE = "031DB0:Campfire.esm"      # ESL 0009F3
KINDLING = "02E68F:Campfire.esm"         # ESL 000970
G_MODE = "075842:Campfire.esm"           # ESL 000E02, Campfire Mode
TENT_SMALL_RECIPE = "036B51"
TENT_LARGE_RECIPE = "03AD8D"
KW_RACK = "07866A:Skyrim.esm"
G_CCO_SURVIVAL = "CC0189:Update.esm"
G_CCO_CLOTH = "CC0197:Update.esm"
STRIPS = "0800E4:Skyrim.esm"
LEATHER = "0DB5D2:Skyrim.esm"
LINEN_WRAP = "034CD6:Skyrim.esm"
KNIVES_IDS = ["01397E", "013986", "01398E", "013996", "01399E", "0139A6", "0139AE", "0139B6"]  # Iron..Daedric (Skyrim.esm only)

# (editor suffix, Skyrim.esm id, hands scraps, knife leather)
GEAR = [
    ("LeatherArmor", "03619E", 6, 2), ("LeatherBoots", "013920", 3, 1), ("LeatherBracers", "013921", 3, 1), ("LeatherHelmet", "013922", 3, 1),
    ("HideArmor", "013911", 6, 2), ("HideBoots", "013910", 3, 1), ("HideBracers", "013912", 3, 1), ("HideHelmet", "013913", 3, 1),
    ("ImperialLightArmor", "013ED9", 6, 2), ("ImperialLightBoots", "013ED7", 3, 1), ("ImperialLightBracers", "013EDA", 3, 1),
    ("ImperialLightHelmet", "013EDB", 3, 1),
    ("StuddedArmor", "01B3A2", 6, 2),
]

NEXT = [0x07D000]
IDS = {}


def newid(eid):
    v = f"{NEXT[0]:06X}"
    NEXT[0] += 1
    IDS[eid] = v
    return v


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def write(p, t):
    if DRY:
        return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(t)


def fk(v):
    return f"{v}:Campfire.esm"


def c_global(g):
    return f"- MutagenObjectType: ConditionFloat\n  Data:\n    MutagenObjectType: GetGlobalValueConditionData\n    Global: {g}\n  ComparisonValue: 1\n"


def c_count(item, op, val):
    s = "- MutagenObjectType: ConditionFloat\n"
    if op == "ge":
        s += "  CompareOperator: GreaterThanOrEqualTo\n"
    s += f"  Data:\n    MutagenObjectType: GetItemCountConditionData\n    ItemOrList: {item}\n  ComparisonValue: {val}\n"
    return s


def recipe(eid, items, conds, created, count, keyword):
    fid = newid(eid)
    t = f"FormKey: {fk(fid)}\nEditorID: {eid}\nItems:\n"
    for it, n in items:
        t += f"- Item:\n    Item: {it}\n    Count: {n}\n"
    t += "Conditions:\n" + "".join(conds)
    t += f"CreatedObject: {created}\nWorkbenchKeyword: {keyword}\nCreatedObjectCount: {count}\n"
    write(os.path.join(CO, f"{eid} - {fid}_Campfire.esm.yaml"), t)
    return fid


def misc(eid, name, model, keyword, weight, value):
    fid = newid(eid)
    t = (f"FormKey: {fk(fid)}\nEditorID: {eid}\nName:\n  TargetLanguage: English\n  Value: {name}\n" + (f"Keywords:\n- {keyword}\n" if keyword else "") +
         f"Model:\n  File: {model}\n  Data: 0x020000000000000000000000\nValue: {value}\nWeight: {weight}\n")
    write(os.path.join(SRC, "MiscItems", f"{eid} - {fid}_Campfire.esm.yaml"), t)
    return fid


# ---- 0. remove our previous output
for d in ("ConstructibleObjects", "MiscItems", "FormLists"):
    for p in glob.glob(os.path.join(SRC, d, "_CampSalv_*")):
        if not DRY:
            os.remove(p)

# ---- 1. items + knife list
leather_scrap = fk(misc("_CampSalv_LeatherScrap", "Leather Scrap", "Clutter\\Common\\LeatherStrips01.nif", "0BECD7:Skyrim.esm", 0.1, 1))
cloth_scrap = fk(misc("_CampSalv_ClothScrap", "Cloth Scrap", "Clutter\\Ruins\\RuinsLinenWrap01.nif", "0BECD7:Skyrim.esm", 0.1, 1))
kid = newid("_CampSalv_Knives")
write(os.path.join(SRC, "FormLists", f"_CampSalv_Knives - {kid}_Campfire.esm.yaml"),
      f"FormKey: {fk(kid)}\nEditorID: _CampSalv_Knives\nItems:\n" + "".join(f"- {i}:Skyrim.esm\n" for i in KNIVES_IDS))
KNIVES = fk(kid)

# ---- 2. leather-family gear
for suf, gid, hands, knife in GEAR:
    g = f"{gid}:Skyrim.esm"
    recipe(f"_CampSalv_TearHands_{suf}", [(g, 1)], [c_count(g, "ge", 1), c_count(KNIVES, "eq", 0)], leather_scrap, hands, KW_SURVIVAL)
    recipe(f"_CampSalv_TearKnife_{suf}", [(g, 1)], [c_count(g, "ge", 1), c_count(KNIVES, "ge", 1)], LEATHER, knife, KW_SURVIVAL)

# ---- 3. Campfire's own cloth recipes: knife variant (existing, edited) + bare-hands twin
ncloth = 0
for p in sorted(glob.glob(os.path.join(CO, "_Camp_RecipeSupplies_Linen_Clothes*"))):
    t = read(p)
    nl = "\r\n" if "\r\n" in t else "\n"
    item = re.search(r"Item: ([0-9A-F]{6}:\S+?)\s*\n\s+Count: 1", t).group(1)
    wraps = int(re.search(r"CreatedObjectCount: (\d+)", t).group(1))
    eid = re.search(r"EditorID: (\S+)", t).group(1)
    suf = eid.replace("_Camp_RecipeSupplies_Linen_", "")
    if KNIVES not in t:
        add = c_count(KNIVES, "ge", 1).replace("\n", nl)
        t2 = t.replace(f"CreatedObject:", add + "CreatedObject:", 1)
        assert t2 != t
        write(p, t2)
    recipe(f"_CampSalv_TearHands_{suf}", [(item, 1)], [c_global(G_CCO_CLOTH), c_count(item, "ge", 1), c_count(KNIVES, "eq", 0)],
           cloth_scrap, wraps * 2, KW_SURVIVAL)
    ncloth += 1

# ---- 4. conversions
recipe("_CampSalv_ScrapsToStrips", [(leather_scrap, 3)], [c_count(leather_scrap, "ge", 1)], STRIPS, 1, KW_SURVIVAL)
recipe("_CampSalv_ScrapsToLeather", [(leather_scrap, 8)], [c_count(leather_scrap, "ge", 1)], LEATHER, 1, KW_SURVIVAL)
recipe("_CampSalv_ClothScrapsToLinenWrap", [(cloth_scrap, 3)], [c_count(cloth_scrap, "ge", 1)], LINEN_WRAP, 1, KW_SURVIVAL)
recipe("_CampSalv_LeatherScrapsToKindling", [(leather_scrap, 2)], [c_count(leather_scrap, "ge", 1), c_global(G_MODE)], KINDLING, 2, KW_CAMPFIRE)
recipe("_CampSalv_ClothScrapsToKindling", [(cloth_scrap, 2)], [c_count(cloth_scrap, "ge", 1), c_global(G_MODE)], KINDLING, 2, KW_CAMPFIRE)


# ---- 5. patchwork leather tents: half the Leather is replaced by 4 scraps per Leather
def tent(src_id, eid_suffix):
    t = read(glob.glob(os.path.join(CO, f"*- {src_id}_Campfire.esm.yaml"))[0])
    items = [(a, int(b)) for a, b in re.findall(r"Item: (\S+)\s*\n\s+Count: (\d+)", t)]
    created = re.search(r"CreatedObject: (\S+)", t).group(1)
    strips = next(n for i, n in items if i == STRIPS)
    lea = next(n for i, n in items if i == LEATHER)
    keep = (lea + 1) // 2
    recipe(f"_CampSalv_Tent{eid_suffix}_Patchwork", [(STRIPS, strips), (LEATHER, keep), (leather_scrap, (lea - keep) * 4)],
           [c_global(G_CCO_SURVIVAL)], created, 1, KW_RACK)
    return strips, lea, keep


s = tent(TENT_SMALL_RECIPE, "LeatherSmall")
l = tent(TENT_LARGE_RECIPE, "LeatherLarge")
print(f"tents: small strips/leather/kept {s}, large {l}")

print(f"{'(dry) ' if DRY else ''}new records {len(IDS)} ({min(IDS.values())}..{max(IDS.values())}), cloth recipes edited {ncloth}")
if not DRY:
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    json.dump(IDS, open(os.path.join(HERE, "work", "salvage_ids.json"), "w"), indent=0)
