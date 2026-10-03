Campfire 2026 - ESL
Based on Campfire 1.12.1 SE/VR (Nexus 667) by Chesko, MIT-licensed source.

WHAT IT DOES
------------
Makes Campfire.esm a light (ESL) plugin so Campfire takes no regular plugin slot. All 1566 of its records are renumbered into
000800-000E1D (482 slots to spare), and the 13 Campfire scripts that look records up by hard-coded FormID are rebuilt with the new ids
(the source is in scripts/source, MIT). Nothing else about Campfire changes: every record keeps its EditorID, name and values, and the
Campfire API (CampUtil and friends) is unchanged.

This is a layer on top of Campfire 2026. Campfire 2026's settings pages (SKSE Menu Framework) work with it unchanged: the same
Campfire.dll detects the light plugin and uses the new ids.

The numbering is the same as in "CAMPFIRE ESL UPDATED" (Nexus 193472) for every record that mod renumbered, so mods built for it
(Frostfall 2026 ESL, Last Seed 2026 ESL, their patches) work with this one unchanged. This build also covers the 212 records that
mod's map left out (placed references, cells), and the script fixes cover one more script than "Campfire ESL - Script Fixes" did
(CampCampfire, used on the Skyrim VR path only).

REQUIRES
--------
- Campfire 2026 (the settings layer, with Campfire.dll) and the original Campfire 1.12.1 SE/VR (Nexus 667), still installed: the original
  supplies Campfire.bsa, the meshes, the textures and the sounds.
- SKSE Menu Framework 3, PapyrusUtil SE and SkyUI, as Campfire 2026 does.

USE
---
Install after (below) the original Campfire and Campfire 2026 in MO2's left pane so Campfire.esm and the scripts here win. If you also use
"Campfire - Script Optimization", put this above it as well so the rebuilt scripts win.
Do NOT also use "CAMPFIRE ESL UPDATED" or "Campfire ESL - Script Fixes": this replaces both.
This is a new-game change: an existing save made with the original (regular) Campfire.esm refers to its records by the old ids.

Mods that point at Campfire's records by FormID (plugin masters, or hard-coded GetFormFromFile) need the same renumbering. The
"Campfire 2026 - Patches" installer has the regular and the ESL version of each patch: pick ESL on its first page.

CREDITS
-------
Chesko (Campfire, MIT).
