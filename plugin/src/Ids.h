#pragma once

// Campfire 2026 comes in two builds of the same plugin: Campfire.esm as a normal master, and an ESL build with every FormID renumbered into the
// light range. Campfire.dll reads forms by their local id in Campfire.esm (the ids in McmTable.h are the normal build's), so every lookup goes
// through here: for the normal build the id passes straight through, for the ESL build it is translated with the table tools/gen_eslmap.py
// writes (EslMap.h, from the same map the ESL plugin was built with).
namespace ids
{
	RE::FormID Camp(RE::FormID a_local);  // a local FormID in Campfire.esm, whichever build is loaded

	// Local FormIDs (normal build) of the forms the plugin uses besides the settings table.
	inline constexpr RE::FormID kMcmQuest = 0x0225A6;         // _Camp_SkyUIConfigPanel, carries _Camp_SkyUIConfigPanelScript
	inline constexpr RE::FormID kAutoSaveLoad = 0x051BCC;     // _Camp_Setting_AutoSaveLoad (2 = changes are written to the current profile)
	inline constexpr RE::FormID kCurrentProfile = 0x051BCD;   // _Camp_Setting_CurrentProfile
	inline constexpr RE::FormID kPerkPointsTotal = 0x0510F8;  // CampingPerkPointsTotal
}
