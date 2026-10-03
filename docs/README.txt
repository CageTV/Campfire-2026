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
  Profiles   the 10 settings profiles: pick, rename, reset, automatic save / load

Every option, default, hover text and profile key is Campfire's own. Settings are still saved to the same profile files
(Data/SKSE/Plugins/CampfireData/), so profiles you already have keep working. The SkyUI menu keeps only the Help page
(troubleshooting wizards, tutorials, the guide).

Nothing about how Campfire plays changes. The Campfire plugin and its API (CampUtil and friends) are untouched; only the menu script is
rebuilt (its settings pages are gone and three helper functions were added for the new pages), and Campfire.dll draws the pages.

REQUIRES
--------
- The original Campfire 1.12.1 SE/VR (Nexus 667): this adds to it and replaces none of its files except one script.
- SKSE Menu Framework 3 (Nexus 120352): without it the settings pages do not exist.
- PapyrusUtil SE (profiles are saved with it, as the original Campfire does) and SkyUI.

USE
---
Install after (below) the original Campfire in MO2's left pane. It works with an existing save: the menu script's version is raised, and
the SkyUI menu rebuilds its page list the next time you load.

KNOWN DIFFERENCES FROM THE SKYUI MENU
-------------------------------------
- The hotkey rows do not warn about keys that other mods or the game already use; pick a free key.
- The Help page is still the SkyUI one.

CREDITS
-------
Chesko (Campfire, MIT).
