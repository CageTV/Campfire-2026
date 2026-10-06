/*
 * Campfire 2026
 * Copyright (C) 2026 CageTV
 *
 * This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at your option) any later version. It is distributed WITHOUT ANY
 * WARRANTY; see LICENSE.txt for the full text.
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
