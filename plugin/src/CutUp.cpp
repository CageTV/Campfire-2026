/*
 * Campfire 2026
 * Copyright (C) 2026 CageTV
 *
 * This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at your option) any later version. It is distributed WITHOUT ANY
 * WARRANTY; see LICENSE.txt for the full text.
 */
#include "PCH.h"
#include "CutUp.h"
#include "Ids.h"

#include "SKSEMenuFramework.h"

#include <algorithm>
#include <fstream>
#include <set>
#include <sstream>
#include <vector>

namespace CutUp
{
	namespace
	{
		// Local ids (normal build numbering) of what the recipes use. 07D000.. are the Salvage records of Campfire 2026 1.1.0.
		constexpr RE::FormID kSurvivalKeyword = 0x019831;
		constexpr RE::FormID kLeatherScrap = 0x07D000;
		constexpr RE::FormID kClothScrap = 0x07D001;
		constexpr RE::FormID kKnives = 0x07D002;
		constexpr RE::FormID kLeather = 0x0DB5D2;    // Skyrim.esm
		constexpr RE::FormID kLinenWrap = 0x034CD6;  // Skyrim.esm
		constexpr RE::FormID kCloth = 0xCC0197;      // Update.esm, Creation Club cloth global (Campfire's 48 clothes recipes check it)

		constexpr std::size_t kMaxItems = 3000;  // sanity limit only; a normal list is a few hundred pieces

		constexpr const char* kIniPath = "Data/SKSE/Plugins/CampfireData/CutUp.ini";

		struct Settings
		{
			bool        enabled = true;
			bool        leather = true;
			bool        cloth = true;
			char        exclude[256]{};  // comma separated; an armor is skipped when its name or plugin file contains one of these
		};
		Settings settings;
		std::size_t statLeather = 0, statCloth = 0, statAdded = 0, statExcluded = 0;
		bool        statValid = false;

		std::set<std::string> skipItems;  // "plugin file|local id" of single pieces the player unticked on the Salvage page

		// What the scan found, for the Salvage page (read-only after Build).
		struct Entry
		{
			std::string key;
			std::string label;  // name and plugin, as listed
			bool        leather;
			bool        tear;
		};
		std::vector<Entry> entries;
		char               searchBuf[128]{};

		std::string Lower(std::string a_s)
		{
			std::transform(a_s.begin(), a_s.end(), a_s.begin(), [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
			return a_s;
		}

		void LoadSettings()
		{
			std::ifstream in(kIniPath);
			std::string   line;
			while (std::getline(in, line)) {
				const auto eq = line.find('=');
				if (eq == std::string::npos) {
					continue;
				}
				const std::string key = line.substr(0, eq);
				std::string       val = line.substr(eq + 1);
				while (!val.empty() && (val.back() == '\r' || val.back() == ' ')) {
					val.pop_back();
				}
				if (key == "enabled") {
					settings.enabled = val != "0";
				} else if (key == "leather") {
					settings.leather = val != "0";
				} else if (key == "cloth") {
					settings.cloth = val != "0";
				} else if (key == "exclude") {
					std::snprintf(settings.exclude, sizeof(settings.exclude), "%s", val.c_str());
				} else if (key == "skipitems") {
					std::stringstream ss(val);
					std::string       k;
					while (std::getline(ss, k, ';')) {
						if (!k.empty()) {
							skipItems.insert(k);
						}
					}
				}
			}
		}

		void SaveSettings()
		{
			std::ofstream out(kIniPath, std::ios::trunc);
			out << "; Campfire 2026 - tear recipes for modded gear. Read at game start.\n"
				<< "enabled=" << (settings.enabled ? 1 : 0) << "\nleather=" << (settings.leather ? 1 : 0) << "\ncloth=" << (settings.cloth ? 1 : 0)
				<< "\nexclude=" << settings.exclude << "\nskipitems=";
			for (const auto& k : skipItems) {
				out << k << ';';
			}
			out << "\n";
		}

		std::string ItemKey(const RE::TESObjectARMO* a_armor)
		{
			const auto* file = a_armor->GetFile(0);
			char        id[16];
			std::snprintf(id, sizeof(id), "%X", a_armor->GetLocalFormID());
			return Lower(file ? std::string(file->GetFilename()) : std::string("?")) + "|" + id;
		}

		bool Excluded(const RE::TESObjectARMO* a_armor, const std::vector<std::string>& a_terms)
		{
			if (a_terms.empty()) {
				return false;
			}
			const auto* file = a_armor->GetFile(0);
			const std::string hay = Lower(std::string(a_armor->GetName()) + "|" + (file ? std::string(file->GetFilename()) : std::string()));
			for (const auto& t : a_terms) {
				if (hay.find(t) != std::string::npos) {
					return true;
				}
			}
			return false;
		}

		enum class Kind
		{
			None,
			Leather,
			Cloth
		};

		struct Candidate
		{
			RE::TESObjectARMO* armor;
			Kind               kind;
			bool               body;
			bool               preferred;
		};

		// the slot mask is an enum set in alandtse's CommonLib and a plain enum in the older one: work on the raw bits
		template <class T>
		std::uint32_t RawBits(const T& a_mask)
		{
			if constexpr (requires { a_mask.get(); }) {
				return static_cast<std::uint32_t>(a_mask.get());
			} else {
				return static_cast<std::uint32_t>(a_mask);
			}
		}

		template <class... S>
		bool AnySlot(std::uint32_t a_bits, S... a_slots)
		{
			return (((a_bits & static_cast<std::uint32_t>(a_slots)) != 0) || ...);
		}

		Kind Classify(RE::TESObjectARMO* a_armor, bool& a_body)
		{
			if (!a_armor->GetPlayable() || a_armor->formEnchanting || a_armor->templateArmor) {
				return Kind::None;
			}
			const std::string_view name = a_armor->GetName();
			if (name.empty()) {
				return Kind::None;
			}
			const std::uint32_t slots = RawBits(a_armor->GetSlotMask());
			using S = RE::BGSBipedObjectForm::BipedObjectSlot;
			if (slots == 0 || AnySlot(slots, S::kShield, S::kAmulet, S::kRing, S::kCirclet)) {
				return Kind::None;
			}
			// Cloaks, capes and mantles sit in the mod slots (40, 46, 47, 57); capes often carry the necklace keyword too
			constexpr std::uint32_t kCloakBits = (1u << 10) | (1u << 16) | (1u << 17) | (1u << 27);
			const bool              cloak = (slots & kCloakBits) != 0;
			if (!cloak && (a_armor->HasKeywordString("ClothingNecklace") || a_armor->HasKeywordString("ClothingRing") || a_armor->HasKeywordString("ClothingCirclet"))) {
				return Kind::None;
			}
			a_body = !cloak && AnySlot(slots, S::kBody);

			const std::string lname = Lower(std::string(name));
			const auto        has = [&](std::string_view a_word) {  // whole words only: "rags" yes, "Dragon" no
				for (std::size_t p = lname.find(a_word); p != std::string::npos; p = lname.find(a_word, p + 1)) {
					const bool before = p == 0 || !std::isalpha(static_cast<unsigned char>(lname[p - 1]));
					const bool after = p + a_word.size() >= lname.size() || !std::isalpha(static_cast<unsigned char>(lname[p + a_word.size()]));
					if (before && after) {
						return true;
					}
				}
				return false;
			};
			const bool        clothing = a_armor->HasKeywordString("ArmorClothing");
			const bool        heavy = a_armor->HasKeywordString("ArmorHeavy");
			if (clothing && (has("burlap") || has("linen") || has("cloth") || has("wool") || has("cotton") || has("silk") || has("rags"))) {
				return Kind::Cloth;
			}
			if (a_armor->HasKeywordString("ArmorMaterialLeather") || a_armor->HasKeywordString("ArmorMaterialHide") ||
				a_armor->HasKeywordString("ArmorMaterialStudded") || a_armor->HasKeywordString("ArmorMaterialStormcloak") ||
				a_armor->HasKeywordString("ArmorMaterialImperialLight") || a_armor->HasKeywordString("ArmorMaterialImperialStudded") ||
				a_armor->HasKeywordString("VendorItemAnimalHide") || (!heavy && (has("fur") || has("pelt") || has("hide") || has("leather")))) {
				return Kind::Leather;
			}
			if (clothing) {
				return Kind::Cloth;
			}
			return Kind::None;
		}

		// alandtse's CommonLibSSE-NG has TESDataHandler::AddFormToDataHandler; the older CommonLib of the legacy DLL does not, so call the same
		// game function (Address Library id 13597 on SE, 13693 on AE) by hand. Not known for VR: the legacy build skips this feature there.
		bool AddForm(RE::TESDataHandler* a_dh, RE::TESForm* a_form)
		{
#ifdef CAMPFIRE_LEGACY_COMMONLIB
			using func_t = bool(RE::TESDataHandler*, RE::TESForm*);
			static REL::Relocation<func_t> func{ REL::RelocationID(13597, 13693) };
			return func(a_dh, a_form);
#else
			return a_dh->AddFormToDataHandler(a_form);
#endif
		}

		RE::TESConditionItem* ItemCount(RE::TESForm* a_form, RE::CONDITION_ITEM_DATA::OpCode a_op, float a_value)
		{
			auto* c = new RE::TESConditionItem;
			c->next = nullptr;
			c->data.comparisonValue.f = a_value;
			c->data.functionData.function = RE::FUNCTION_DATA::FunctionID::kGetItemCount;
			c->data.functionData.params[0] = a_form;
			c->data.flags.opCode = a_op;
			c->data.flags.isOR = false;
			c->data.object = RE::CONDITIONITEMOBJECT::kSelf;
			return c;
		}

		RE::TESConditionItem* GlobalIsOne(RE::TESGlobal* a_global)
		{
			auto* c = new RE::TESConditionItem;
			c->next = nullptr;
			c->data.comparisonValue.f = 1.0f;
			c->data.functionData.function = RE::FUNCTION_DATA::FunctionID::kGetGlobalValue;
			c->data.functionData.params[0] = a_global;
			c->data.flags.opCode = RE::CONDITION_ITEM_DATA::OpCode::kEqualTo;
			c->data.flags.isOR = false;
			c->data.object = RE::CONDITIONITEMOBJECT::kSelf;
			return c;
		}

		RE::BGSConstructibleObject* MakeRecipe(RE::TESObjectARMO* a_armor, RE::TESForm* a_product, std::uint16_t a_count, RE::BGSKeyword* a_bench,
			RE::TESForm* a_knives, bool a_withKnife, RE::TESGlobal* a_global)
		{
			auto* factory = RE::IFormFactory::GetConcreteFormFactoryByType<RE::BGSConstructibleObject>();
			auto* r = factory ? factory->Create() : nullptr;
			if (!r) {
				return nullptr;
			}
			r->requiredItems.AddObjectToContainer(a_armor, 1, nullptr);
			r->createdItem = a_product;
			r->benchKeyword = a_bench;
			r->data.numConstructed = a_count;

			// armor >= 1 AND (knife >= 1 | knife == 0); cloth recipes also check the Creation Club cloth global like Campfire's own
			auto* c1 = ItemCount(a_armor, RE::CONDITION_ITEM_DATA::OpCode::kGreaterThanOrEqualTo, 1.0f);
			auto* c2 = a_withKnife ? ItemCount(a_knives, RE::CONDITION_ITEM_DATA::OpCode::kGreaterThanOrEqualTo, 1.0f) :
			                         ItemCount(a_knives, RE::CONDITION_ITEM_DATA::OpCode::kEqualTo, 0.0f);
			c1->next = c2;
			if (a_global) {
				c2->next = GlobalIsOne(a_global);
			}
			r->conditions.head = c1;
			return r;
		}
	}

	void Build()
	{
		LoadSettings();
#ifdef CAMPFIRE_LEGACY_COMMONLIB
		if (REL::Module::IsVR()) {
			SKSE::log::info("CutUp: tear recipes for modded gear are not available in this DLL on Skyrim VR; use the newer DLL on 1.6.1170 or later");
			return;
		}
#endif
		auto* dh = RE::TESDataHandler::GetSingleton();
		if (!dh) {
			return;
		}
		if (!settings.enabled) {
			SKSE::log::info("CutUp: switched off in the settings, no recipes added for modded gear");
			return;
		}
		std::vector<std::string> terms;
		{
			std::stringstream ss(settings.exclude);
			std::string       t;
			while (std::getline(ss, t, ',')) {
				const auto b = t.find_first_not_of(' ');
				const auto e = t.find_last_not_of(' ');
				if (b != std::string::npos) {
					terms.push_back(Lower(t.substr(b, e - b + 1)));
				}
			}
		}
		auto* bench = dh->LookupForm<RE::BGSKeyword>(ids::Camp(kSurvivalKeyword), "Campfire.esm");
		auto* leatherScrap = dh->LookupForm(ids::Camp(kLeatherScrap), "Campfire.esm");
		auto* clothScrap = dh->LookupForm(ids::Camp(kClothScrap), "Campfire.esm");
		auto* knives = dh->LookupForm(ids::Camp(kKnives), "Campfire.esm");
		auto* leather = dh->LookupForm(kLeather, "Skyrim.esm");
		auto* wrap = dh->LookupForm(kLinenWrap, "Skyrim.esm");
		auto* clothGlobal = dh->LookupForm<RE::TESGlobal>(kCloth, "Update.esm");
		if (!bench || !leatherScrap || !clothScrap || !knives || !leather || !wrap) {
			SKSE::log::warn("CutUp: missing forms (bench {}, leather scrap {}, cloth scrap {}, knives {}, leather {}, wrap {}) - Campfire.esm needs the Salvage records of Campfire 2026 1.1.0 or newer; modded gear is not added",
				!!bench, !!leatherScrap, !!clothScrap, !!knives, !!leather, !!wrap);
			return;
		}
		SKSE::log::info("CutUp: bench {:08X}, leather scrap {:08X}, cloth scrap {:08X}, knives {:08X}, cloth global {}", bench->GetFormID(),
			leatherScrap->GetFormID(), clothScrap->GetFormID(), knives->GetFormID(), clothGlobal ? "found" : "MISSING");

		// what the Survival bench already tears (Campfire's own recipes, the Salvage ones): one required armor each
		std::set<const RE::TESForm*> covered;
		for (auto* cobj : dh->GetFormArray<RE::BGSConstructibleObject>()) {
			if (cobj && cobj->benchKeyword == bench && cobj->requiredItems.numContainerObjects == 1 && cobj->requiredItems.containerObjects[0]) {
				covered.insert(cobj->requiredItems.containerObjects[0]->obj);
			}
		}

		std::vector<Candidate> found;
		std::size_t            leatherN = 0, clothN = 0, skipped = 0;
		for (auto* armor : dh->GetFormArray<RE::TESObjectARMO>()) {
			if (!armor) {
				continue;
			}
			bool       body = false;
			const Kind kind = Classify(armor, body);
			if (kind == Kind::None || (kind == Kind::Leather && !settings.leather) || (kind == Kind::Cloth && !settings.cloth)) {
				continue;
			}
			if (Excluded(armor, terms)) {
				++statExcluded;
				continue;
			}
			if (covered.contains(armor)) {
				++skipped;
				continue;
			}
			kind == Kind::Leather ? ++leatherN : ++clothN;
			const auto*       file = armor->GetFile(0);
			const std::string key = ItemKey(armor);
			const bool        tear = !skipItems.contains(key);
			entries.push_back({ key, std::string(armor->GetName()) + "  (" + (file ? std::string(file->GetFilename()) : std::string("?")) + ")", kind == Kind::Leather, tear });
			if (!tear) {
				++statExcluded;
				continue;
			}
			const bool preferred = file && file->GetFilename() == "Common Clothes and Armors.esp";
			found.push_back({ armor, kind, body, preferred });
		}
		std::sort(entries.begin(), entries.end(), [](const Entry& a, const Entry& b) { return a.label < b.label; });
		std::stable_sort(found.begin(), found.end(), [](const Candidate& a, const Candidate& b) { return a.preferred && !b.preferred; });
		statLeather = leatherN;
		statCloth = clothN;
		SKSE::log::info("CutUp: {} leather and {} cloth armors without a tear recipe ({} already covered)", leatherN, clothN, skipped);

		std::size_t made = 0;
		auto&       cobjs = dh->GetFormArray<RE::BGSConstructibleObject>();
		for (std::size_t i = 0; i < found.size() && i < kMaxItems; ++i) {
			const auto&         cd = found[i];
			const bool          leatherKind = cd.kind == Kind::Leather;
			const std::uint16_t scraps = leatherKind ? (cd.body ? 6 : 3) : (cd.body ? 6 : 2);
			const std::uint16_t cut = leatherKind ? (cd.body ? 2 : 1) : (cd.body ? 3 : 1);
			auto* hands = MakeRecipe(cd.armor, leatherKind ? leatherScrap : clothScrap, scraps, bench, knives, false, leatherKind ? nullptr : clothGlobal);
			auto* knife = MakeRecipe(cd.armor, leatherKind ? leather : wrap, cut, bench, knives, true, leatherKind ? nullptr : clothGlobal);
			if (!hands || !knife) {
				SKSE::log::error("CutUp: could not create a recipe for {:08X}", cd.armor->GetFormID());
				break;
			}
			const bool a = AddForm(dh, hands);
			const bool b = AddForm(dh, knife);
			if (i < 12) {
				const auto* file = cd.armor->GetFile(0);
				SKSE::log::info("CutUp: {} {:08X} \"{}\" ({}) hands={} knife={} id {:08X}/{:08X}", leatherKind ? "leather" : "cloth", cd.armor->GetFormID(),
					cd.armor->GetName(), file ? file->GetFilename() : "?", a, b, hands->GetFormID(), knife->GetFormID());
			}
			made += 2;
		}
		statAdded = made;
		statValid = true;
		SKSE::log::info("CutUp: added {} recipes for {} items; COBJ array now {}", made, made / 2, cobjs.size());
	}

	void DrawPage()
	{
		using namespace ImGuiMCP;
		TextWrapped("Campfire 2026 adds tear recipes at the Survival bench for leather and cloth gear from your other mods: with bare hands you get scraps, with a dagger "
					"you get Leather or Linen Wrap. The list is built each time the game starts, so changes here apply from the next launch.");
		Spacing();
		bool changed = false;
		changed |= Checkbox("Tear recipes for modded gear", &settings.enabled);
		if (settings.enabled) {
			changed |= Checkbox("Leather, hide and studded gear", &settings.leather);
			changed |= Checkbox("Cloth and clothing", &settings.cloth);
			Spacing();
			TextWrapped("Skip gear whose name or plugin file contains any of these words (comma separated, e.g. Wedding, Bandit, MyArmor.esp):");
			changed |= InputText("##cutupexclude", settings.exclude, sizeof(settings.exclude));
		}
		if (changed) {
			SaveSettings();
		}
		Spacing();
		if (statValid) {
			TextDisabled("Last launch: %zu leather and %zu cloth pieces found, %zu recipes added, %zu skipped by your filter.", statLeather, statCloth, statAdded, statExcluded);
		} else {
			TextDisabled("Nothing was added at the last launch (switched off, or Campfire.esm has no Salvage records).");
		}
		if (statValid && !entries.empty()) {
			Spacing();
			char header[96];
			std::snprintf(header, sizeof(header), "Pieces found (%zu)###cutupfound", entries.size());
			if (CollapsingHeader(header)) {
				TextWrapped("Untick a piece to leave it out (from the next launch). L = leather and hide, C = cloth.");
				InputText("Search##cutupsearch", searchBuf, sizeof(searchBuf));
				const std::string needle = Lower(searchBuf);
				std::size_t       shown = 0, matching = 0;
				bool              toggled = false;
				for (std::size_t i = 0; i < entries.size(); ++i) {
					auto& e = entries[i];
					if (!needle.empty() && Lower(e.label).find(needle) == std::string::npos) {
						continue;
					}
					++matching;
					if (shown >= 200) {
						continue;
					}
					++shown;
					const std::string label = std::string(e.leather ? "L  " : "C  ") + e.label + "##cutup" + std::to_string(i);
					if (Checkbox(label.c_str(), &e.tear)) {
						if (e.tear) {
							skipItems.erase(e.key);
						} else {
							skipItems.insert(e.key);
						}
						toggled = true;
					}
				}
				if (matching > shown) {
					TextDisabled("%zu more match: type in the search box to narrow the list.", matching - shown);
				}
				if (toggled) {
					SaveSettings();
				}
			}
		}
		TextDisabled("Settings are kept in Data/SKSE/Plugins/CampfireData/CutUp.ini.");
	}
}
