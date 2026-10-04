/*
 * Campfire 2026
 * Copyright (C) 2026 CageTV
 *
 * This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at your option) any later version. It is distributed WITHOUT ANY
 * WARRANTY; see LICENSE.txt for the full text.
 */
#include "PCH.h"
#include "Ids.h"
#include "EslMap.h"

namespace ids
{
	namespace
	{
		// Is the plugin loaded as a light (ESL) plugin? -1 = not known yet (data not loaded, or the plugin is not there).
		int Light(const char* a_plugin, std::atomic<int>& a_cache)
		{
			const int cached = a_cache.load();
			if (cached >= 0) {
				return cached;
			}
			auto* dh = RE::TESDataHandler::GetSingleton();
			auto* file = dh ? dh->LookupModByName(a_plugin) : nullptr;
			if (!file) {
				return -1;
			}
			const int light = file->IsLight() ? 1 : 0;
			a_cache = light;
			SKSE::log::info("{} is loaded as a {} plugin", a_plugin, light ? "light (ESL)" : "regular");
			return light;
		}
	}

	RE::FormID Camp(RE::FormID a_local)
	{
		static std::atomic<int> cache{ -1 };
		if (Light("Campfire.esm", cache) != 1) {
			return a_local;
		}
		const RE::FormID local = a_local & 0x00FFFFFF;
		const auto*      end = std::end(eslmap::kCampfire);
		const auto*      it = std::lower_bound(std::begin(eslmap::kCampfire), end, local, [](const eslmap::Pair& a_p, RE::FormID a_id) { return a_p.from < a_id; });
		if (it != end && it->from == local) {
			return it->to;
		}
		static std::atomic<bool> warned{ false };
		if (!warned.exchange(true)) {
			SKSE::log::error("Campfire.esm: no light-plugin id known for {:06X} (further misses are not logged)", local);
		}
		return a_local;
	}
}
