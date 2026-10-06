Campfire 2026
Based on Campfire 1.12.1 SE/VR (Nexus 667) by Chesko, MIT-licensed source.

WHAT IT DOES
------------
Campfire's settings move out of the SkyUI Mod Configuration Menu and into SKSE Menu Framework, in a "Campfire" section with these pages:

  Overview   what is installed
  Gameplay   campfire building mode, camping legality and flammability, the four hotkeys, what you and your followers take off in a tent
  Instincts  what the Instincts power detects, and its visual and sound effects
  Advanced   advanced object placement and max placement threads, follower tracking, Equipping Overhaul compatibility,
             and the Camping skill's respec and restore options
  Salvage    tear recipes for gear from your other mods: switches, an exclusion filter, and a list of every piece found
  Profiles   the 10 settings profiles: pick, rename, reset, automatic save / load

Every option, default, hover text and profile key is Campfire's own. Settings are still saved to the same profile files
(Data/SKSE/Plugins/CampfireData/), so profiles you already have keep working. The SkyUI menu keeps only the Help page
(troubleshooting wizards, tutorials, the guide).

Nothing about how Campfire plays changes. The Campfire plugin and its API (CampUtil and friends) are untouched; only the menu script is
rebuilt (its settings pages are gone and three helper functions were added for the new pages), and Campfire.dll draws the pages.

SALVAGE RECIPES (new in 1.1.0)
------------------------------
Open Campfire's Survival crafting menu ("Create") with the item in your bag; recipes are listed by what they make.
- Leather gear (Leather, Hide, Imperial Light and Studded armor, boots, bracers, helmets): with NO dagger in the bag it tears into Leather Scraps
  (6 from armor, 3 from the rest); with any vanilla dagger (Iron to Daedric) it is cut into Leather (2 from armor, 1 from the rest).
- Cloth clothing: Campfire's existing tear recipes now need a dagger and still give Linen Wraps; by hand you get Cloth Scraps (twice the wraps).
- Scraps combine: 3 Leather Scraps -> Leather Strips, 8 -> Leather, 3 Cloth Scraps -> Linen Wrap; at a campfire, 2 scraps -> 2 Kindling.
- Patchwork leather tents (small and large) at the tanning rack: half the Leather is replaced by Leather Scraps (4 scraps per Leather).
Scraps use vanilla meshes; nothing of Chesko's or Skyrim's assets is packed. Scraps share the firewood item type, so inventory icon mods show them like Kindling.

MODDED GEAR (new in 1.1.0, needs Campfire.dll)
----------------------------------------------
Each time the game starts, Campfire.dll scans every armor in your load order and adds the same two tear recipes (by hand: scraps; with a dagger:
Leather or Linen Wrap) for the pieces Campfire does not already cover:
- leather, hide, studded, fur, Stormcloak and Imperial light gear, and anything tagged or named fur, pelt, hide or leather (not heavy armor);
- clothing, robes, and cloaks, capes and mantles (burlap, linen, wool, cotton, silk and rags give Linen Wrap / Cloth Scrap, the rest Leather);
- not shields, jewelry, circlets, enchanted, templated or unplayable items. Body pieces give the larger yield, cloaks and the rest the smaller one.
The Salvage page (Campfire section of SKSE Menu Framework) switches the feature on and off, splits leather from cloth, skips every piece whose name or
plugin file contains a word you type (e.g. Wedding, MyArmor.esp), and lists every piece it found with a tick box and a search field, so you can leave
single pieces out. Changes apply from the next launch; they are saved in Data/SKSE/Plugins/CampfireData/CutUp.ini (the Overwrite folder under MO2).
Campfire.log in the SKSE log folder says how many pieces and recipes were found. A long list is fine; if the Survival menu feels slow, use the filter.
The DLL for Skyrim 1.6.1170 and newer has this; the older DLL has it on SE/AE 1.6.1130 and older, but not on Skyrim VR (the game function it needs is not verified there).
Campfire.esm: the regular build ships a Campfire.esm that overrides Chesko's. It has every record and id of the original plus 84 new ones, so
existing saves, Frostfall and Last Seed keep working. Load order and masters are unchanged (Skyrim.esm, Update.esm only).

REQUIRES
--------
- The original Campfire 1.12.1 SE/VR (Nexus 667): this adds to it and replaces only Campfire.esm and one script (it keeps supplying Campfire.bsa, the meshes, textures and sounds).
- SKSE64 and Address Library for SKSE Plugins (Nexus 32444). The Address Library must be the version for YOUR game: 'failed to open address library
  file' when the game starts means it is missing or too old (Skyrim 1.7.104 needs Address Library v13 or newer).
- SKSE Menu Framework 3 (Nexus 120352): without it the settings pages do not exist.
- PapyrusUtil SE (profiles are saved with it, as the original Campfire does). Put it AFTER (below) the original Campfire in MO2's left pane: the original
  bundles an outdated PapyrusUtil, and the newer one has to win.
- SkyUI.

USE
---
Install order: Campfire (original), Campfire 2026, then Frostfall 2026, then Last Seed 2026 (each below the one before in MO2's left pane).
Install after (below) the original Campfire in MO2's left pane. It works with an existing save: the menu script's version is raised, and
the SkyUI menu rebuilds its page list the next time you load.

KNOWN DIFFERENCES FROM THE SKYUI MENU
-------------------------------------
- The hotkey rows do not warn about keys that other mods or the game already use; pick a free key.
- The Help page is still the SkyUI one.

CREDITS
-------
Chesko (Campfire, MIT).
