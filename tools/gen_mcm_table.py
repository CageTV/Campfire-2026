"""Writes plugin/src/McmTable.h: the settings of Campfire's SkyUI menu as data for Campfire.dll's SKSE Menu Framework pages.

Inputs, all from Chesko's MIT-licensed Campfire 1.12.1: the plugin (src/esp/Campfire, Spriggit YAML) for each setting's global FormID, the
English strings (Campfire_ENGLISH.txt) for labels and hover text, and the menu script (src/scripts/_camp_skyuiconfigpanelscript.psc) for which
hover text belongs to which option. The page layout and profile keys below are transcribed from that script's PageReset_* functions,
OnOptionDefault and SwitchToProfile; every key is checked against the script so a typo cannot slip through.

Usage: python tools/gen_mcm_table.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESP = os.path.join(HERE, "src", "esp", "Campfire")
PSC = os.path.join(HERE, "src", "scripts", "_camp_skyuiconfigpanelscript.psc")
STR = r"E:\WorkSpace\Frostfall-Modernized\upstream-chesko\Interface\Translations\Campfire_ENGLISH.txt"
OUT = os.path.join(HERE, "plugin", "src", "McmTable.h")

strings = {}
for line in open(STR, encoding="utf-16").read().splitlines():
    if line.startswith("$") and "\t" in line:
        k, v = line.split("\t", 1)
        strings[k] = v.strip()


def s(key):
    if key not in strings:
        sys.exit(f"missing string {key}")
    return strings[key]


psc = open(PSC, encoding="utf-8", errors="replace").read()
tips = {}
for m in re.finditer(r"option == (\w+)\s*\n\s*SetInfoText\(\"(\$\w+)\"\)", psc):
    tips[m.group(1)] = m.group(2)

globs = {}
for fn in os.listdir(os.path.join(ESP, "Globals")):
    m = re.match(r"(.+) - ([0-9A-F]{6})_Campfire\.esm\.yaml$", fn)
    if m:
        globs[m.group(1)] = int(m.group(2), 16)

T, H, C, S, M, K = "Toggle", "Header", "Column", "Slider", "Menu", "Key"
GATE_TAKEOFF = "_Camp_Setting_CampingArmorTakeOff"
GATE_TRACK = "_Camp_Setting_TrackFollowers"
# Toggle: (T, oid, label, global, profile key, default, gate global or None, special)
# Key:    (K, oid, label, global, profile key, hotkey slot)
# Slider: (S, oid, label, global, profile key, default, min, max, step)
# Menu:   (M, oid, label, global, profile key, default, [option labels], base)
pages = [
    ("Gameplay", [
        (H, None, "$CampfireGameplayHeaderCamping"),
        (M, "Gameplay_SettingCampingCampfireMode_OID", "$CampfireGameplaySettingCampfireMode", "_Camp_Setting_CampfireMode", "campfire_mode", 1, ["$CampfireCampfireModeQuick", "$CampfireCampfireModeRealistic"], 0),
        (T, "Gameplay_SettingCampingArmorTentsText_OID", "$CampfireGameplaySettingCampingRemoveGear", GATE_TAKEOFF, "tent_remove_player_equipment", 2, None, 0),
        (T, "Gameplay_SettingCampingLegalityToggle_OID", "$CampfireGameplaySettingLegality", "_Camp_Setting_Legality", "camping_illegal_in_towns", 2, None, 0),
        (T, "Gameplay_SettingCampingFlammabilityToggle_OID", "$CampfireGameplaySettingFlammability", "_Camp_Setting_EquipmentFlammable", "camping_gear_flammable", 2, None, 0),
        (H, None, "$CampfireGameplayHeaderHotkeys"),
        (K, "Gameplay_HotkeyCreateItem_OID", "$CampfireGameplayHotkeyCreateItem", "_Camp_HotkeyCreateItem", "hotkey_create_item", 0),
        (K, "Gameplay_HotkeyBuildCampfire_OID", "$CampfireGameplayHotkeyBuildCampfire", "_Camp_HotkeyBuildCampfire", "hotkey_build_campfire", 1),
        (K, "Gameplay_HotkeyHarvestWood_OID", "$CampfireGameplayHotkeyHarvestWood", "_Camp_HotkeyHarvestWood", "hotkey_harvest_wood", 2),
        (K, "Gameplay_HotkeyInstincts_OID", "$CampfireGameplayHotkeyInstincts", "_Camp_HotkeyInstincts", "hotkey_instincts", 3),
        (C,),
        (H, None, "$CampfireGameplayHeaderTentDisplay"),
        (T, "Gameplay_SettingCampingPlaceCuirass_OID", "$CampfireGameplaySettingShowCuirass", "_Camp_Setting_TakeOff_Cuirass", "tent_remove_player_cuirass", 1, GATE_TAKEOFF, 0),
        (T, "Gameplay_SettingCampingPlaceGauntlets_OID", "$CampfireGameplaySettingShowGauntlets", "_Camp_Setting_TakeOff_Gauntlets", "tent_remove_player_gauntlets", 2, GATE_TAKEOFF, 0),
        (T, "Gameplay_SettingCampingPlaceBackpack_OID", "$CampfireGameplaySettingShowBackpack", "_Camp_Setting_TakeOff_Backpack", "tent_remove_player_backpack", 2, GATE_TAKEOFF, 0),
        (T, "Gameplay_SettingCampingPlaceWeapons_OID", "$CampfireGameplaySettingShowWeapons", "_Camp_Setting_TakeOff_Weapons", "tent_remove_player_weapons", 2, GATE_TAKEOFF, 0),
        (T, "Gameplay_SettingCampingPlaceShield_OID", "$CampfireGameplaySettingShowShield", "_Camp_Setting_TakeOff_Shield", "tent_remove_player_shield", 2, GATE_TAKEOFF, 0),
        (T, "Gameplay_SettingCampingPlaceAmmo_OID", "$CampfireGameplaySettingShowAmmo", "_Camp_Setting_TakeOff_Ammo", "tent_remove_player_ammo", 2, GATE_TAKEOFF, 0),
        (T, "Gameplay_SettingCampingPlaceHelm_OID", "$CampfireGameplaySettingShowHelm", "_Camp_Setting_TakeOff_Helm", "tent_remove_player_helm", 2, GATE_TAKEOFF, 0),
        (T, "Gameplay_SettingCampingPlaceBoots_OID", "$CampfireGameplaySettingShowBoots", "_Camp_Setting_TakeOff_Boots", "tent_remove_player_boots", 2, GATE_TAKEOFF, 0),
        (H, None, "$CampfireGameplayHeaderFollowerTentDisplay"),
        (T, "Gameplay_SettingCampingFollowersInteract_OID", "$CampfireGameplaySettingFollowersInteract", "_Camp_Setting_FollowersUseCampsite", "followers_use_campsite", 2, GATE_TRACK, 0),
        (T, "Gameplay_SettingCampingFollowersRemoveGear_OID", "$CampfireGameplaySettingShowFollowerGear", "_Camp_Setting_FollowersRemoveGearInTents", "tent_remove_follower_equipment", 2, GATE_TRACK, 0),
    ]),
    ("Instincts", [
        (H, None, "$CampfireInstinctsHeaderDetection"),
        (T, "Instincts_SettingFindTinder_OID", "$CampfireInstinctsSettingFindTinder", "_Camp_Setting_InstinctsFindTinder", "instincts_find_tinder", 2, None, 0),
        (T, "Instincts_SettingFindFlora_OID", "$CampfireInstinctsSettingFindFlora", "_Camp_Setting_InstinctsFindFlora", "instincts_find_flora", 2, None, 0),
        (T, "Instincts_SettingHearCreatures_OID", "$CampfireInstinctsSettingHearCreatures", "_Camp_Setting_InstinctsHearCreatures", "instincts_hear_creatures", 2, None, 0),
        (T, "Instincts_SettingSmellDead_OID", "$CampfireInstinctsSettingSmellDead", "_Camp_Setting_InstinctsSmellDead", "instincts_smell_dead", 2, None, 0),
        (T, "Instincts_SettingSenseObjective_OID", "$CampfireInstinctsSettingSenseObjective", "_Camp_Setting_InstinctsSenseObjective", "instincts_sense_objective", 1, None, 0),
        (H, None, "$CampfireInstinctsHeaderEffects"),
        (T, "Instincts_SettingVFX_OID", "$CampfireInstinctsSettingVFX", "_Camp_Setting_InstinctsVFX", "instincts_vfx", 2, None, 0),
        (T, "Instincts_SettingSFX_OID", "$CampfireInstinctsSettingSFX", "_Camp_Setting_InstinctsSFX", "instincts_sfx", 2, None, 0),
    ]),
    ("Advanced", [
        (H, None, "$CampfireAdvancedHeaderPlacement"),
        (T, "Advanced_SettingAdvancedPlacement_OID", "$CampfireAdvancedSettingAdvancedPlacement", "_Camp_Setting_AdvancedPlacement", "advanced_placement_mode", 2, None, 0),
        (S, "Advanced_SettingMaxThreads_OID", "$CampfireAdvancedSettingMaxThreads", "_Camp_Setting_MaxThreads", "max_placement_threads", 20, 0, 30, 1),
        (H, None, "$CampfireAdvancedHeaderSystem"),
        (T, "Advanced_SettingTrackFollowers_OID", "$CampfireGameplaySettingTrackFollowers", "_Camp_Setting_TrackFollowers", "follower_tracking", 2, None, 1),
        (H, None, "$CampfireAdvancedHeaderCompatibility"),
        (T, "Advanced_SettingEOCompatibility_OID", "$CampfireAdvancedSettingEOCompatibility", "_Camp_Setting_CompatibilityEO", "eo_compatibility", 1, None, 2),
    ]),
]


def gid(eid):
    if eid not in globs:
        sys.exit(f"no global named {eid} in the plugin")
    return globs[eid]


def q(t):
    return '"' + t.replace("\\", "\\\\").replace('"', '\\"') + '"'


COMMON_TAIL = "nullptr, 0, 0"
lists, rows, errors = {}, [], []
for title, entries in pages:
    out = []
    for e in entries:
        kind = e[0]
        if kind == H:
            out.append(f'{{ Kind::Header, {q(s(e[2]))}, 0, "", 0, 0, 0, 0, "", nullptr, 0, 0, 0, 0, "" }}')
            continue
        if kind == C:
            out.append('{ Kind::Column, "", 0, "", 0, 0, 0, 0, "", nullptr, 0, 0, 0, 0, "" }')
            continue
        oid, label, g, key = e[1], e[2], e[3], e[4]
        if f'"{key}"' not in psc:
            errors.append(f"profile key {key} not found in the menu script")
        tip = s(tips[oid]) if oid in tips else ""
        if not tip:
            errors.append(f"no hover text for {oid}")
        if kind == T:
            default, gate, special = e[5], e[6], e[7]
            gate_id = gid(gate) if gate else 0
            out.append(f'{{ Kind::Toggle, {q(s(label))}, 0x{gid(g):06X}, "{key}", {default}, 0, 0, 0, "", nullptr, 0, 0, 0x{gate_id:06X}, {special}, {q(tip)} }}')
        elif kind == S:
            out.append(f'{{ Kind::Slider, {q(s(label))}, 0x{gid(g):06X}, "{key}", {e[5]}, {e[6]}, {e[7]}, {e[8]}, "{{0}}", nullptr, 0, 0, 0, 0, {q(tip)} }}')
        elif kind == M:
            name = f"kList_{oid}"
            lists[name] = [s(x) for x in e[6]]
            out.append(f'{{ Kind::Menu, {q(s(label))}, 0x{gid(g):06X}, "{key}", {e[5]}, 0, 0, 0, "", {name}, {len(e[6])}, {e[7]}, 0, 0, {q(tip)} }}')
        elif kind == K:
            out.append(f'{{ Kind::Key, {q(s(label))}, 0x{gid(g):06X}, "{key}", {e[5]}, 0, 0, 0, "", nullptr, 0, 0, 0, 0, {q(tip)} }}')
    rows.append((title, out))
if errors:
    sys.exit("\n".join(errors))

with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("// GENERATED by tools/gen_mcm_table.py from Campfire's own MCM script, Campfire.esm and English strings. Do not edit by hand.\n")
    f.write("// Campfire is by Chesko; its scripts and plugin are MIT licensed (the meshes and textures are not part of this).\n#pragma once\n\n#include <iterator>\n\n")
    f.write("namespace mcm\n{\n\tenum class Kind { Header, Column, Toggle, Slider, Menu, Key };\n\n")
    f.write("\t// One row of a page. formId is the local FormID of the setting's global in Campfire.esm (0 for headers and column breaks).\n")
    f.write("\t// Toggles hold 1 (off) or 2 (on). A menu stores its list position plus menuBase. Key: def is the hotkey slot (0 create item, 1 build campfire,\n")
    f.write("\t// 2 harvest wood, 3 instincts). gate: the row is greyed out unless this global is 2. special: 1 = follower tracking, 2 = Equipping Overhaul.\n")
    f.write("\tstruct Entry\n\t{\n\t\tKind                kind;\n\t\tconst char*         label;\n\t\tunsigned int        formId;\n\t\tconst char*         profileKey;\n\t\tfloat               def, min, max, step;\n\t\tconst char*         format;\n\t\tconst char* const*  options;\n\t\tint                 optionCount;\n\t\tint                 menuBase;\n\t\tunsigned int        gate;\n\t\tint                 special;\n\t\tconst char*         tip;\n\t};\n\n")
    for name, vals in lists.items():
        f.write(f"\tinline constexpr const char* {name}[] = {{\n" + "".join(f"\t\t{q(v)},\n" for v in vals) + "\t};\n")
    f.write("\n\tstruct Page\n\t{\n\t\tconst char*  title;\n\t\tconst Entry* entries;\n\t\tint          count;\n\t};\n\n")
    for i, (title, out) in enumerate(rows):
        f.write(f"\tinline constexpr Entry kEntries{i}[] = {{\n" + "".join(f"\t\t{r},\n" for r in out) + "\t};\n")
    f.write("\n\tinline constexpr Page kPages[] = {\n" + "".join(f'\t\t{{ {q(t)}, kEntries{i}, static_cast<int>(std::size(kEntries{i})) }},\n' for i, (t, _) in enumerate(rows)) + "\t};\n}\n")
n = sum(len(o) for _, o in rows)
print(f"wrote {OUT}: {len(rows)} pages, {n} rows, {len(lists)} lists; hover text found for {len(tips)} options")
