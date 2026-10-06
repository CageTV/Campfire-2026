/*
 * Campfire 2026
 * Copyright (c) 2026 CageTV
 *
 * Released under the MIT License; see LICENSE.txt.
 */
#pragma once

// Tear recipes for modded leather and cloth gear. The Salvage recipes in Campfire.esm cover vanilla pieces; this finds the other armors at game
// start (keyword and slot rules) and adds the same "hands -> scraps / dagger -> Leather or Linen Wrap" recipes at the Survival bench.
namespace CutUp
{
	void Build();  // call once, after all data is loaded

	// Settings page: read when the game loads (Build), so a change applies from the next launch.
	void DrawPage();
}
