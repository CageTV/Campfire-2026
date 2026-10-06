/*
 * Campfire 2026
 * Copyright (c) 2026 CageTV
 *
 * Released under the MIT License; see LICENSE.txt.
 */
#pragma once

// Campfire's settings pages, drawn through SKSE Menu Framework instead of the SkyUI MCM. They are built from McmTable.h (generated from
// Campfire's own MCM script) and do what the MCM does: write the setting's global, write the active profile file (through PapyrusUtil's
// JsonUtil, exactly like the MCM), and for the few settings with side effects (hotkeys, follower tracking) call the menu script's helpers.
namespace NativeMcm
{
	bool Ready();  // Campfire.esm is loaded and its settings globals are found

	// One page of McmTable.h (an index into mcm::kPages).
	void DrawPage(int a_page);

	// The Camping skill's respec and restore options.
	void DrawSkill();

	// Campfire's settings profiles: pick, rename, reset, and switch automatic saving on or off.
	void DrawProfiles();

	// Once per frame: writes pending profile changes a moment after the last edit (like dragging a slider).
	void Tick(float a_dt);
}
