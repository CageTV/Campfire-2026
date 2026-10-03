# Campfire 2026

An update layer for **Campfire - Complete Camping System** (Nexus mod 667, by Chesko) 1.12.1 SE/VR on Skyrim AE 1.6.1170 and up, built the same way as
[Frostfall 2026](https://github.com/CageTV/Frostfall-2026) and [Last Seed 2026](https://github.com/CageTV/Last-Seed-2026).

Campfire's scripts and plugin are MIT licensed by Chesko. This carries only what changed. **It does not carry Campfire's meshes, textures or
sounds**: keep the original Campfire download installed underneath it.

**Download:** two installers on the [releases page](https://github.com/CageTV/Campfire-2026/releases): **Campfire 2026** (asks Regular or ESL) and **Campfire 2026 - Patches** (asks Regular or ESL, then the patches).

## What's different

- **Settings in SKSE Menu Framework 3** (`Campfire.dll`): Gameplay, Instincts, Advanced (with the Camping skill's respec and restore) and
  Profiles. Every option, default, hover text and profile key is Campfire's own, saved to the same profile files, so existing profiles keep
  working. The SkyUI menu keeps only the Help page.
- **An ESL build** (an option in the same installer): Campfire.esm as a light plugin (all 1566 records renumbered into 000800-000E1D), with the 13 scripts that hard-code
  FormIDs rebuilt to match. The numbering is identical to the earlier "CAMPFIRE ESL UPDATED" on every record that mod renumbered, and also
  covers the 212 it left out. The same DLL serves both builds.
- **A patches installer** (regular and ESL in one FOMOD) for the usual Campfire compatibility patches.

Nothing about how Campfire plays changes, and its API (`CampUtil` and friends) is untouched.

## Layout

| Path | What |
|---|---|
| `src/esp/Campfire` | Spriggit YAML of the shipped Campfire 1.12.1 plugin (the record source for the ESL build) |
| `src/scripts` | Campfire's scripts (Chesko's source; `_Camp_SkyUIConfigPanelScript` is the one we changed) |
| `plugin/` | `Campfire.dll` (CommonLibSSE-NG, CMake + vcpkg; `plugin/build.cmd`) |
| `tools/esl_build.py` | renumbers the plugin into the ESL range, rewrites the scripts, writes the FormID map |
| `tools/gen_mcm_table.py`, `tools/gen_eslmap.py` | generate `plugin/src/McmTable.h` and `EslMap.h` |
| `tools/build_scripts.py`, `tools/package.py`, `tools/esl_package.py`, `tools/make_fomod.py` | compile scripts, lay out the two layers, build the single installer |
| `tools/patches_esl.py`, `tools/make_patches_fomod.py` | remap and verify the patch plugins, build the installer |
| `esl/map_campfire.json` | old -> new FormID for all 1566 records |
| `docs/` | the READMEs and licence texts that ship in the downloads |

Paths at the top of the tools assume the author's workspace; edit them for yours. Needs Spriggit, the Papyrus compiler, Python 3 and
(for the DLL) Visual Studio with vcpkg.

## Credits

Chesko, for Campfire and Frostfall (MIT). Settings, ESL build and patches installer by CageTV.
