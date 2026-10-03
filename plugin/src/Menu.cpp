#include "PCH.h"
#include "Ids.h"
#include "Menu.h"
#include "NativeMcm.h"

#include "SKSEMenuFramework.h"

namespace Menu
{
	namespace
	{
		using namespace ImGuiMCP;

		bool registered = false;

		constexpr const char* kLogoPath = "Data\\Interface\\campfire\\campfire_logo.png";
		constexpr float       kLogoAspect = 361.0f / 1479.0f;

		void Logo()
		{
			static ImTextureID tex = SKSEMenuFramework::LoadTexture(kLogoPath);
			if (!tex) {
				return;
			}
			const float avail = GetContentRegionAvail().x;
			const float w = std::min(avail, 460.0f);
			SetCursorPosX(GetCursorPosX() + (avail - w) * 0.5f);
			Image(tex, ImVec2(w, w * kLogoAspect));
			Spacing();
		}

		void __stdcall RenderOverview()
		{
			Logo();
			if (!NativeMcm::Ready()) {
				TextColored(ImVec4(1.0f, 0.45f, 0.4f, 1.0f), "Campfire.esm is not loaded.");
				return;
			}
			TextColored(ImVec4(0.65f, 0.9f, 0.5f, 1.0f), "Campfire 2026 is active.");
			Spacing();
			TextWrapped("Campfire's settings are on the pages in this section: Gameplay, Instincts, Advanced and Profiles. "
						"The Help page (troubleshooting wizards, tutorials and the guide) is still in the SkyUI Mod Configuration Menu.");
			Spacing();
			TextDisabled("Campfire by Chesko (MIT). Campfire 2026 settings by CageTV.");
		}

		void __stdcall RenderGameplay() { NativeMcm::DrawPage(0); }
		void __stdcall RenderInstincts() { NativeMcm::DrawPage(1); }

		void __stdcall RenderAdvanced()
		{
			NativeMcm::DrawPage(2);
			NativeMcm::DrawSkill();
		}

		void __stdcall RenderProfiles() { NativeMcm::DrawProfiles(); }

		// Drawn every frame whether or not the menu is open: flushes profile writes a moment after the last change.
		void __stdcall Frame()
		{
			NativeMcm::Tick(GetIO()->DeltaTime);
		}
	}

	bool Registered() { return registered; }

	void Register()
	{
		if (!SKSEMenuFramework::IsInstalled()) {
			SKSE::log::warn("SKSE Menu Framework is not installed: Campfire's settings pages are not available (the SkyUI menu keeps only the Help page)");
			return;
		}
		SKSEMenuFramework::SetSection("Campfire");
		SKSEMenuFramework::AddSectionItem("Overview", RenderOverview);
		SKSEMenuFramework::AddSectionItem("Gameplay", RenderGameplay);
		SKSEMenuFramework::AddSectionItem("Instincts", RenderInstincts);
		SKSEMenuFramework::AddSectionItem("Advanced", RenderAdvanced);
		SKSEMenuFramework::AddSectionItem("Profiles", RenderProfiles);
		SKSEMenuFramework::AddHudElement(Frame);
		registered = true;
		SKSE::log::info("Registered with SKSE Menu Framework {}", SKSEMenuFramework::GetMenuFrameworkVersion());
	}
}
