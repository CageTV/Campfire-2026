/*
 * Campfire 2026
 * Copyright (c) 2026 CageTV
 *
 * Released under the MIT License; see LICENSE.txt.
 */
#include "PCH.h"
#include "Ids.h"
#include <fstream>
#include <map>
#include <regex>
#include "NativeMcm.h"
#include "Hotkeys.h"
#include "McmTable.h"

#include "SKSEMenuFramework.h"

namespace NativeMcm
{
	namespace
	{
		using namespace ImGuiMCP;

		constexpr const char* kScript = "_Camp_SkyUIConfigPanelScript";
		constexpr const char* kConfigPath = "../CampfireData/";  // where the MCM keeps its profiles (JsonUtil path)
		constexpr float       kProfileWriteDelay = 0.6f;          // profile writes wait for the last change, like dragging a slider

		std::map<std::string, int> pendingProfile;  // profile key -> value, written after a short delay
		float                      profileTimer = -1.0f;

		RE::TESGlobal* Global(unsigned int a_localId)
		{
			auto* dh = RE::TESDataHandler::GetSingleton();
			return dh ? dh->LookupForm<RE::TESGlobal>(ids::Camp(a_localId), "Campfire.esm") : nullptr;
		}

		// Writes the pending keys to the current profile with PapyrusUtil's JsonUtil, as the MCM's SaveSettingToCurrentProfile does.
		void FlushProfile()
		{
			if (pendingProfile.empty()) {
				return;
			}
			auto pending = std::move(pendingProfile);
			pendingProfile.clear();
			SKSE::GetTaskInterface()->AddTask([pending = std::move(pending)]() {
				auto* autoSave = Global(ids::kAutoSaveLoad);
				auto* profile = Global(ids::kCurrentProfile);
				auto* vm = RE::BSScript::Internal::VirtualMachine::GetSingleton();
				if (!vm || !autoSave || !profile || static_cast<int>(autoSave->value) != 2) {
					return;  // automatic profile saving is off: nothing to write
				}
				const std::string path = std::string(kConfigPath) + "profile" + std::to_string(static_cast<int>(profile->value));
				RE::BSTSmartPointer<RE::BSScript::IStackCallbackFunctor> callback;
				for (const auto& [key, value] : pending) {
					vm->DispatchStaticCall("JsonUtil", "SetIntValue", RE::MakeFunctionArguments(std::string(path), std::string(key), static_cast<std::int32_t>(value)), callback);
				}
				vm->DispatchStaticCall("JsonUtil", "Save", RE::MakeFunctionArguments(std::string(path), false), callback);
			});
		}

		void QueueProfile(const char* a_key, int a_value)
		{
			if (a_key && a_key[0]) {
				pendingProfile[a_key] = a_value;
				profileTimer = kProfileWriteDelay;
			}
		}

		// Calls a method of the menu script (on quest _Camp_SkyUIConfigPanel) on the game thread.
		template <class... Args>
		void CallMenuScript(const char* a_method, Args... a_args)
		{
			SKSE::GetTaskInterface()->AddTask([=]() mutable {
				auto* dh = RE::TESDataHandler::GetSingleton();
				auto* vm = RE::BSScript::Internal::VirtualMachine::GetSingleton();
				auto* quest = dh ? dh->LookupForm<RE::TESQuest>(ids::Camp(ids::kMcmQuest), "Campfire.esm") : nullptr;
				if (!vm || !quest) {
					SKSE::log::warn("Campfire settings: cannot call {}.{} (quest or VM missing)", kScript, a_method);
					return;
				}
				const auto handle = vm->GetObjectHandlePolicy()->GetHandleForObject(RE::TESQuest::FORMTYPE, quest);
				RE::BSTSmartPointer<RE::BSScript::IStackCallbackFunctor> callback;
				const bool ok = vm->DispatchMethodCall2(handle, kScript, a_method, RE::MakeFunctionArguments(std::move(a_args)...), callback);
				SKSE::log::info("Campfire settings: {}.{}() -> {}", kScript, a_method, ok ? "dispatched" : "FAILED");
			});
		}

		void JsonSetInt(std::string a_path, std::string a_key, int a_value)
		{
			SKSE::GetTaskInterface()->AddTask([a_path, a_key, a_value]() {
				auto* vm = RE::BSScript::Internal::VirtualMachine::GetSingleton();
				RE::BSTSmartPointer<RE::BSScript::IStackCallbackFunctor> callback;
				if (vm) {
					vm->DispatchStaticCall("JsonUtil", "SetIntValue", RE::MakeFunctionArguments(std::string(a_path), std::string(a_key), static_cast<std::int32_t>(a_value)), callback);
				}
			});
		}

		void JsonSetString(std::string a_path, std::string a_key, std::string a_value)
		{
			SKSE::GetTaskInterface()->AddTask([a_path, a_key, a_value]() {
				auto* vm = RE::BSScript::Internal::VirtualMachine::GetSingleton();
				RE::BSTSmartPointer<RE::BSScript::IStackCallbackFunctor> callback;
				if (vm) {
					vm->DispatchStaticCall("JsonUtil", "SetStringValue", RE::MakeFunctionArguments(std::string(a_path), std::string(a_key), std::string(a_value)), callback);
				}
			});
		}

		void JsonSave(std::string a_path)
		{
			SKSE::GetTaskInterface()->AddTask([a_path]() {
				auto* vm = RE::BSScript::Internal::VirtualMachine::GetSingleton();
				RE::BSTSmartPointer<RE::BSScript::IStackCallbackFunctor> callback;
				if (vm) {
					vm->DispatchStaticCall("JsonUtil", "Save", RE::MakeFunctionArguments(std::string(a_path), false), callback);
				}
			});
		}

		// The name stored in a profile's file (Data/SKSE/Plugins/CampfireData/profileN.json), or "Profile N".
		std::string ProfileName(int a_index)
		{
			std::ifstream in("Data/SKSE/Plugins/CampfireData/profile" + std::to_string(a_index) + ".json");
			if (in) {
				const std::string text((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
				static const std::regex re("\"profile_name\"\\s*:\\s*\"([^\"]*)\"");
				std::smatch m;
				if (std::regex_search(text, m, re) && !m[1].str().empty()) {
					return m[1].str();
				}
			}
			return "Profile " + std::to_string(a_index);
		}

		bool EquippingOverhaulLoaded()
		{
			auto* dh = RE::TESDataHandler::GetSingleton();
			return dh && dh->LookupModByName("Equipping Overhaul.esp");
		}

		void Changed(const mcm::Entry& a_e, RE::TESGlobal* a_g, float a_value, int a_profileValue)
		{
			a_g->value = a_value;
			QueueProfile(a_e.profileKey, a_profileValue);
		}

		void Tip(const mcm::Entry& a_e)
		{
			if (a_e.tip && a_e.tip[0] && IsItemHovered()) {
				BeginTooltip();
				PushTextWrapPos(420.0f);
				TextUnformatted(a_e.tip);
				PopTextWrapPos();
				EndTooltip();
			}
		}

		void DrawEntry(const mcm::Entry& a_e, int a_id)
		{
			PushID(a_id);
			bool disabled = false;
			if (a_e.gate != 0) {
				auto* gate = Global(a_e.gate);
				disabled = !gate || static_cast<int>(gate->value) != 2;
			}
			if (disabled) {
				BeginDisabled();
			}
			switch (a_e.kind) {
			case mcm::Kind::Header:
				Spacing();
				SeparatorText(a_e.label);
				break;
			case mcm::Kind::Column:
				Spacing();
				Separator();
				break;
			case mcm::Kind::Toggle:
				if (auto* g = Global(a_e.formId)) {
					static const mcm::Entry* askingEO = nullptr;  // Equipping Overhaul's confirmation, waiting for an answer
					if (a_e.special == 2 && !EquippingOverhaulLoaded()) {
						bool off = false;
						BeginDisabled();
						Checkbox("Equipping Overhaul (Not Installed)", &off);
						EndDisabled();
						break;
					}
					bool on = static_cast<int>(g->value) == 2;
					if (Checkbox(a_e.label, &on)) {
						if (a_e.special == 2 && on) {
							askingEO = &a_e;  // the checkbox only turns on once the prompt is confirmed
						} else {
							Changed(a_e, g, on ? 2.0f : 1.0f, on ? 2 : 1);
							if (a_e.special == 1) {
								CallMenuScript("NativeSetFollowerTracking", on);  // adds or removes the detect spell, clears the follower aliases
							}
						}
					}
					Tip(a_e);
					if (askingEO == &a_e) {
						TextWrapped("By enabling this option, you allow Campfire to press the Geared Up hotkey for you automatically when sitting or laying down in a tent in order to prevent visual duplication. This is a work-around and is not official support from Campfire or Equipping Overhaul.");
						TextWrapped("The Geared Up hotkey must be configured in order for this to work!");
						if (Button("Yes, enable it")) {
							Changed(a_e, g, 2.0f, 2);
							askingEO = nullptr;
						}
						SameLine();
						if (Button("Cancel")) {
							askingEO = nullptr;
						}
					}
				}
				break;
			case mcm::Kind::Slider:
				if (auto* g = Global(a_e.formId)) {
					float v = g->value;
					if (SliderFloat(a_e.label, &v, a_e.min, a_e.max, "%.0f")) {
						if (a_e.step > 0.0f) {
							v = a_e.min + std::round((v - a_e.min) / a_e.step) * a_e.step;
						}
						v = std::clamp(v, a_e.min, a_e.max);
						Changed(a_e, g, v, static_cast<int>(v));  // the MCM saves sliders to profiles as whole numbers
					}
					Tip(a_e);
				}
				break;
			case mcm::Kind::Key:
				if (auto* g = Global(a_e.formId)) {
					const int slot = static_cast<int>(a_e.def);
					int       picked = 0;
					if (Hotkeys::CapturingSlot() == slot && Hotkeys::TakeCaptured(slot, picked)) {
						// the menu script re-registers the key, sets the global and swaps the hotkey's spell in or out, as its own menu does
						CallMenuScript("NativeSetHotkey", static_cast<std::int32_t>(slot), static_cast<std::int32_t>(picked));
						g->value = static_cast<float>(picked);
						QueueProfile(a_e.profileKey, picked);
					}
					if (Hotkeys::CapturingSlot() == slot) {
						if (Button("Press a key...  (Esc cancels, Delete clears)")) {
							Hotkeys::CancelCapture();
						}
					} else {
						const std::string text = std::string(Hotkeys::KeyName(static_cast<int>(g->value))) + "##key";
						if (Button(text.c_str(), ImVec2(180.0f, 0.0f))) {
							Hotkeys::BeginCapture(slot);
						}
					}
					SameLine();
					Text("%s", a_e.label);
					Tip(a_e);
				}
				break;
			case mcm::Kind::Menu:
				if (auto* g = Global(a_e.formId)) {
					// a stored value above the last entry (a default profile writes 2) shows as the last entry, as the MCM does
					int index = std::clamp(static_cast<int>(g->value) - a_e.menuBase, 0, std::max(0, a_e.optionCount - 1));
					if (Combo(a_e.label, &index, a_e.options, a_e.optionCount)) {
						const int stored = index + a_e.menuBase;
						Changed(a_e, g, static_cast<float>(stored), stored);
					}
					Tip(a_e);
				}
				break;
			}
			if (disabled) {
				EndDisabled();
			}
			PopID();
		}
	}

	bool Ready()
	{
		return Global(ids::kAutoSaveLoad) != nullptr && Global(ids::kCurrentProfile) != nullptr;
	}

	void DrawPage(int a_page)
	{
		if (a_page < 0 || a_page >= static_cast<int>(std::size(mcm::kPages))) {
			return;
		}
		if (!Ready()) {
			TextDisabled("Campfire.esm is not loaded.");
			return;
		}
		const auto& page = mcm::kPages[a_page];
		for (int i = 0; i < page.count; ++i) {
			DrawEntry(page.entries[i], i);
		}
		if (std::string_view(page.title) == "Gameplay") {
			Spacing();
			TextWrapped("Click a hotkey button, then press the key. Escape cancels, Delete clears it (the hotkey's spell is then back in your spell list).");
		}
	}

	void DrawSkill()
	{
		static int   confirm = 0;  // 1 = respec asked, 2 = restore asked
		static float restore = 0.0f;
		static float confirmTimer = 0.0f;
		confirmTimer -= GetIO()->DeltaTime;
		if (confirmTimer <= 0.0f) {
			confirm = 0;
		}
		Spacing();
		SeparatorText("Camping Skill");
		if (confirm == 1) {
			TextWrapped("Are you sure you want to refund all earned Camping skill points so you can reallocate them?");
			if (Button("Yes, respec my perks")) {
				CallMenuScript("RefundCampingSkillPoints");
				confirm = 0;
			}
			SameLine();
			if (Button("Cancel##respec")) {
				confirm = 0;
			}
		} else if (Button("Respec Skill Points")) {
			confirm = 1;
			confirmTimer = 10.0f;
		}
		float total = 0.0f;
		if (auto* g = Global(ids::kPerkPointsTotal)) {
			total = g->value;
		}
		TextWrapped("Restore Skill Progress: reclaim Camping skill progress lost to a clean save or a mod uninstall. This replaces your current progress.");
		restore = std::clamp(restore, 0.0f, std::max(total, 0.0f));
		SliderFloat("Points to restore", &restore, 0.0f, std::max(total, 1.0f), "%.0f");
		if (confirm == 2) {
			if (Button("Yes, restore these skill points")) {
				CallMenuScript("NativeRestoreSkillPoints", static_cast<std::int32_t>(restore));
				confirm = 0;
			}
			SameLine();
			if (Button("Cancel##restore")) {
				confirm = 0;
			}
		} else if (Button("Restore skill progress")) {
			confirm = 2;
			confirmTimer = 10.0f;
		}
	}

	void DrawProfiles()
	{
		if (!Ready()) {
			TextDisabled("Campfire.esm is not loaded.");
			return;
		}
		auto* current = Global(ids::kCurrentProfile);
		auto* autoSave = Global(ids::kAutoSaveLoad);
		static int         pendingSwitch = 0;   // profile asked for, waiting for the confirmation
		static bool        askDefault = false;  // "reset the current profile" waiting for the confirmation
		static float       confirmTimer = 0.0f;
		static float       namesTimer = 0.0f;
		static std::string names[10];
		static char        renameBuffer[64] = "";
		confirmTimer -= GetIO()->DeltaTime;
		if (confirmTimer <= 0.0f) {
			pendingSwitch = 0;
			askDefault = false;
		}
		namesTimer -= GetIO()->DeltaTime;
		if (namesTimer <= 0.0f) {
			namesTimer = 1.0f;
			for (int i = 0; i < 10; ++i) {
				names[i] = ProfileName(i + 1);
			}
		}
		const char* items[10];
		for (int i = 0; i < 10; ++i) {
			items[i] = names[i].c_str();
		}

		SeparatorText("Settings Profiles");
		const int activeIndex = std::clamp(static_cast<int>(current->value), 1, 10) - 1;
		int       choice = activeIndex;
		if (Combo("Current profile", &choice, items, 10) && choice != activeIndex) {
			pendingSwitch = choice + 1;
			confirmTimer = 10.0f;
		}
		if (pendingSwitch > 0) {
			TextWrapped("Load the selected profile? Your current settings are replaced by that profile's.");
			if (Button("Yes, load it")) {
				FlushProfile();
				CallMenuScript("SwitchToProfile", static_cast<std::int32_t>(pendingSwitch));
				pendingSwitch = 0;
			}
			SameLine();
			if (Button("Cancel##switch")) {
				pendingSwitch = 0;
			}
		}

		Spacing();
		bool automatic = static_cast<int>(autoSave->value) == 2;
		if (Checkbox("Automatic profile save / load", &automatic)) {
			autoSave->value = automatic ? 2.0f : 1.0f;
			JsonSetInt(std::string(kConfigPath) + "common", "auto_load", automatic ? 2 : 1);
			JsonSave(std::string(kConfigPath) + "common");
			if (automatic) {
				CallMenuScript("SaveAllSettings", static_cast<std::int32_t>(current->value));  // write every setting to the profile now
			}
		}
		TextWrapped(
			"A profile stores all of Campfire's settings in a file. With automatic save / load on, each change is saved to the current profile, and "
			"loading a game, switching characters or starting a new game picks the profile up again. There are 10 profile slots. The files are in "
			"Data/SKSE/Plugins/CampfireData/ (common.json and profile*.json); with Mod Organizer 2 they end up in your Overwrite folder.");

		if (automatic) {
			Spacing();
			SeparatorText("This profile");
			InputText("##rename", renameBuffer, sizeof(renameBuffer));
			SameLine();
			if (Button("Rename profile")) {
				if (renameBuffer[0] != '\0') {
					const std::string path = std::string(kConfigPath) + "profile" + std::to_string(static_cast<int>(current->value));
					JsonSetString(path, "profile_name", renameBuffer);
					JsonSave(path);
					renameBuffer[0] = '\0';
					namesTimer = 0.5f;  // re-read the names once the file has been written
				}
			}
			if (askDefault) {
				TextWrapped("Are you sure you want to restore all settings on your current profile to their default values?");
				if (Button("Yes, restore the defaults")) {
					const auto profile = static_cast<std::int32_t>(current->value);
					pendingProfile.clear();
					CallMenuScript("GenerateDefaultProfile", profile);
					CallMenuScript("SwitchToProfile", profile);
					askDefault = false;
				}
				SameLine();
				if (Button("Cancel##default")) {
					askDefault = false;
				}
			} else if (Button("Default current profile")) {
				askDefault = true;
				confirmTimer = 10.0f;
			}
		}
	}

	void Tick(float a_dt)
	{
		if (profileTimer >= 0.0f) {
			profileTimer -= a_dt;
			if (profileTimer < 0.0f) {
				FlushProfile();
			}
		}
	}
}
