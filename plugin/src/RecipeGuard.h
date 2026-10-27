/*
 * Campfire 2026
 * Copyright (c) 2026 CageTV
 *
 * Released under the MIT License; see LICENSE.txt.
 */
#pragma once

// Cooking recipes of other mods that are made at Campfire's fires (fish from the Creation Club and Gourmet, food patches) carry no "the fire is lit"
// condition, so an unlit placed fire offered them. Campfire's own recipes check the last used fire's size (>= 2) and stage (2 = burning). At game
// start this adds the same two conditions to every food recipe on Campfire's crafting keywords that lacks them.
namespace RecipeGuard
{
	void Apply();  // call once, after all data is loaded
}
