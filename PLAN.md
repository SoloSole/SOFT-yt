# Plán vývoje softwaru pro tvorbu kolážových videí

Tento dokument slouží jako východisko pro postupnou implementaci programu popsaného uživatelem. Struktura obsahuje přehled priorit, milníků a kontrolních seznamů.

## 1. Fáze projektu a milníky
1. **Specifikace požadavků**
   - potvrdit formáty videí, exportní rozlišení a kodeky.
   - určit, jaká kombinace technologií se použije pro UI a video rendering (např. desktopová aplikace postavená na Electronu + FFmpeg).
2. **Návrh UX/UI**
   - navrhnout obrazovku pro výběr orientace (horizontální / vertikální).
   - připravit knihovnu šablon (např. mřížky 2×2, 4×2, 3×3, volná oblast).
   - definovat interakce: klik na buňku, přidání videa, kontextové menu, přehrávání náhledu.
3. **Video engine**
   - načítání videí do buněk mřížky, jejich ořez a škálování.
   - synchronizace časové osy všech klipů.
   - export finálního videa pomocí FFmpeg (včetně přepočtu rozlišení a poměru stran).
4. **Licencování a zabezpečení**
   - návrh serveru pro aktivaci, generování licenčních klíčů, vazba na HW fingerprint.
   - ochrana proti úpravám (obfuskace, kontrola integrity souborů, podepsané binárky).
5. **Testování, distribuce a podpora**
   - testy UI, validační exporty, automatizované buildy.
   - příprava instalačního balíčku a procesu aktualizací.

## 2. Kontrolní seznamy
### 2.1 Analýza a design
- [ ] Shromáždit všechny požadované scénáře použití (horizontální/vertikální, různé mřížky).
- [ ] Ověřit požadavky na výkon (4K export, rychlost renderu).
- [x] Zvolit datový model pro šablony (JSON nebo interní struktura).
- [x] Povolit načítání vlastních šablon přes JSON soubory (`--templates-file`).
- [ ] Připravit wireframy / makety dle poskytnutých screenshotů.

### 2.2 Implementace UI
- [x] Inicializační obrazovka s volbou orientace projektu. **✔ dostupné v Tkinter GUI `video_collage.gui`.**
- [x] Panel se seznamem šablon (mřížky, vlastní šablony do budoucna). **✔ GUI obsahuje Listbox se všemi šablonami + podporou JSON souborů.**
- [x] Plátno s vizuálním zobrazením aktuální mřížky a sloty pro videa. **✔ Tkinter Canvas s náhledem reagujícím na výběr.**
- [x] Kontextové menu pro vložení/odebrání videa, náhled každého klipu. **✔ pravé tlačítko/ dvojklik v tabulce slotů, zvýraznění v náhledu.**
- [x] Panel exportu (formát, rozlišení, FPS, bitrate, tlačítko Exportovat). **✔ exportní sekce s FPS/CRF/preset/kodek + tlačítkem „Exportovat video“.**

### 2.3 Video processing
- [x] Wrapper nad FFmpegem nebo jinou knihovnou pro dekód/encode (první jednoduchá pipeline přes `xstack`).
- [ ] Transformace videí do jednotlivých buněk (crop, scale, letterboxing podle orientace).
- [ ] Synchronizace start/stop časů a volba společné délky videa.
- [ ] Generování náhledu v reálném čase (GPU akcelerace, pokud dostupná).

- [x] Generátor HW fingerprintu (kombinace CPU ID, MAC, disk UUID).
- [x] Serverová komponenta pro vystavení licencí na omezenou dobu (HTTP prototyp `video_collage.license_server`).
- [x] Klientská validace licencí (offline cache, periodické ověření online).
- [x] Propojení hlavního CLI s licenční kontrolou (bez platné licence nelze projekt použít).
- [x] Admin rozhraní / reporting (Google Sheets export, dashboard) dle [`docs/licensing_workflow.md`](docs/licensing_workflow.md) – licenční server poskytuje CSV export pro přímý import do Sheets.
- [ ] Ochrana proti manipulaci: podepsané binárky, detekce debuggeru, obfuskace kritické logiky.

### 2.5 Testování a release
- [x] Automatizované testy pro šablony, import/export konfigurací (pytest testy pro načítání a validaci šablon).
- [ ] Testovací scénáře pro různé kombinace mřížek a orientací.
- [ ] CI pipeline pro build, unit testy a podepisování balíčků.
- [ ] Dokumentace pro uživatele (návody na aktivaci licence, tutorial práce se šablonami).

## 3. Závislosti a otevřené otázky
- Jaký framework bude zvolen pro UI (C#/WPF, Electron, Qt)?
- Vyžaduje se podpora vlastních šablon uživatelem od první verze, nebo pouze předdefinované?
- Zda bude licenční server hostován interně, nebo jako SaaS.
- Potřeba podpory pro audio mix a základní efekty?

## 4. Další kroky
1. Upřesnit technologický stack a exportní parametry.
2. Připravit detailní specifikaci licenčního procesu a HW fingerprintingu **✔ základní prototyp hotový, čeká se na server/GUI napojení**.
3. Rozdělit implementaci do sprintů podle kontrolních seznamů výše.
4. Postupně rozšiřovat prototyp CLI (`video_collage/cli.py`) – export přes FFmpeg hotový v základní podobě, dalším krokem je přidání GUI a pokročilých exportních možností.
5. Připravit jednoduchý licenční server + reporting podle dokumentu [`docs/licensing_workflow.md`](docs/licensing_workflow.md), aby bylo možné licence vydávat a sledovat online. **✔ Prototyp serveru dostupný jako `video_collage.license_server`, zbývá admin UI/reporting.**

Dokument lze dále rozšiřovat o detailní úkoly, termíny a odpovědné osoby.
