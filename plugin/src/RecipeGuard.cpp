/*
 * Campfire 2026
 * Copyright (c) 2026 CageTV
 *
 * Released under the MIT License; see LICENSE.txt.
 */
#include "PCH.h"
#include "Ids.h"
#include "RecipeGuard.h"

#include <set>
#include <string>

namespace RecipeGuard
{
	namespace
	{
		constexpr RE::FormID kCampfireBench = 0x031DB0;   // Campfire.esm, _Camp_CraftingCampfire
		constexpr RE::FormID kSurvivalBench = 0xCCA003;   // Update.esm, CraftingCampfire (Campfire.esm overrides it and puts it on its fires)
		constexpr RE::FormID kLastSize = 0xCC0E0C;        // Update.esm, _Camp_LastUsedCampfireSize
		constexpr RE::FormID kLastStage = 0xCC0E0D;       // Update.esm, _Camp_LastUsedCampfireStage

		constexpr const char* kIniPath = "Data/SKSE/Plugins/CampfireData/RecipeGuard.ini";

		struct Settings
		{
			bool enabled = true;
			bool survivalBench = true;  // also food recipes on the Survival Mode keyword the fires carry
		};

		Settings LoadSettings()
		{
			Settings s;
			std::ifstream in(kIniPath);
			std::string   line;
			while (std::getline(in, line)) {
				const auto eq = line.find('=');
				if (eq == std::string::npos || line[0] == ';' || line[0] == '[') {
					continue;
				}
				const std::string key = line.substr(0, eq);
				const bool        on = line.find('1', eq) != std::string::npos;
				if (key == "Enabled") {
					s.enabled = on;
				} else if (key == "GuardSurvivalKeyword") {
					s.survivalBench = on;
				}
			}
			std::error_code ec;
			std::filesystem::create_directories(std::filesystem::path(kIniPath).parent_path(), ec);
			if (!std::filesystem::exists(kIniPath, ec)) {
				std::ofstream out(kIniPath);
				out << "; Campfire 2026: food recipes of other mods at Campfire's fires only work while the fire is burning.\n"
				       "[RecipeGuard]\n"
				       "Enabled=1\n"
				       "GuardSurvivalKeyword=1\n";
			}
			return s;
		}

		RE::TESConditionItem* GlobalCondition(RE::TESGlobal* a_global, RE::CONDITION_ITEM_DATA::OpCode a_op, float a_value)
		{
			auto* c = new RE::TESConditionItem;
			c->next = nullptr;
			c->data.comparisonValue.f = a_value;
			c->data.functionData.function = RE::FUNCTION_DATA::FunctionID::kGetGlobalValue;
			c->data.functionData.params[0] = a_global;
			c->data.flags.opCode = a_op;
			c->data.flags.isOR = false;
			c->data.object = RE::CONDITIONITEMOBJECT::kSelf;
			return c;
		}

		// A recipe is already guarded when one of its conditions reads the last used fire's stage.
		bool ReadsGlobal(const RE::BGSConstructibleObject* a_cobj, const RE::TESGlobal* a_global, bool& a_hasOr)
		{
			bool found = false;
			for (auto* c = a_cobj->conditions.head; c; c = c->next) {
				if (c->data.flags.isOR) {
					a_hasOr = true;
				}
				if (c->data.functionData.function == RE::FUNCTION_DATA::FunctionID::kGetGlobalValue && c->data.functionData.params[0] == a_global) {
					found = true;
				}
			}
			return found;
		}
	}

	void Apply()
	{
		const Settings settings = LoadSettings();
		if (!settings.enabled) {
			SKSE::log::info("RecipeGuard: switched off in the settings");
			return;
		}
		auto* dh = RE::TESDataHandler::GetSingleton();
		if (!dh) {
			return;
		}
		auto* campBench = dh->LookupForm<RE::BGSKeyword>(ids::Camp(kCampfireBench), "Campfire.esm");
		auto* survBench = dh->LookupForm<RE::BGSKeyword>(kSurvivalBench, "Update.esm");
		auto* size = dh->LookupForm<RE::TESGlobal>(kLastSize, "Update.esm");
		auto* stage = dh->LookupForm<RE::TESGlobal>(kLastStage, "Update.esm");
		if (!campBench || !size || !stage) {
			SKSE::log::info("RecipeGuard: Campfire.esm is not loaded, nothing to do");
			return;
		}

		std::size_t seen = 0, guarded = 0, already = 0, skippedOr = 0;
		std::set<std::string> sources;
		for (auto* cobj : dh->GetFormArray<RE::BGSConstructibleObject>()) {
			if (!cobj || !cobj->benchKeyword) {
				continue;
			}
			const bool onCampfire = cobj->benchKeyword == campBench;
			const bool onSurvival = settings.survivalBench && survBench && cobj->benchKeyword == survBench;
			if (!onCampfire && !onSurvival) {
				continue;
			}
			// Only food: Campfire's other recipes (lighting a fire, crafting) have to stay available at an unlit fire.
			if (!cobj->createdItem || !cobj->createdItem->As<RE::AlchemyItem>()) {
				continue;
			}
			++seen;
			bool hasOr = false;
			if (ReadsGlobal(cobj, stage, hasOr)) {
				++already;
				continue;
			}
			if (hasOr) {
				// "A OR B AND C" is "A OR (B AND C)": appending an AND would not guard the A branch, so leave these alone.
				++skippedOr;
				continue;
			}
			auto* tail = cobj->conditions.head;
			auto* sizeCond = GlobalCondition(size, RE::CONDITION_ITEM_DATA::OpCode::kGreaterThanOrEqualTo, 2.0f);
			auto* stageCond = GlobalCondition(stage, RE::CONDITION_ITEM_DATA::OpCode::kEqualTo, 2.0f);
			sizeCond->next = stageCond;
			if (!tail) {
				cobj->conditions.head = sizeCond;
			} else {
				while (tail->next) {
					tail = tail->next;
				}
				tail->next = sizeCond;
			}
			++guarded;
			if (const auto* file = cobj->GetFile(0)) {
				sources.emplace(file->GetFilename());
			}
		}
		SKSE::log::info("RecipeGuard: {} food recipes on Campfire's keywords: {} already need a burning fire, {} now do, {} skipped (they use OR conditions)", seen, already, guarded,
			skippedOr);
		for (const auto& s : sources) {
			SKSE::log::info("RecipeGuard: guarded recipes from {}", s);
		}
	}
}
