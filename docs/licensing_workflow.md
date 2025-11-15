# Správa licencí a reporting

Tento dokument popisuje, jak aktuální prototyp pracuje s licencemi a jak lze postupně přejít z ručního vydávání na plně automatizovaný proces s reportingem.

## 1. Prototyp: ruční vystavení licencí
1. **Zákazník spustí klienta** s příkazem `python -m video_collage.license_cli fingerprint` a odešle otisk zařízení.
2. **Dodavatel** (tj. vy) spustí `python -m video_collage.license_cli sign <fingerprint> <customer_name> --secret-key <tajný_klíč> --valid-days <n>` a vzniklý JSON odešle zákazníkovi.
3. **Klient** uloží soubor, spustí hlavní CLI s parametry `--license-file` a `--verification-key` (nebo proměnnou `VIDEO_COLLAGE_VERIFICATION_KEY`) a software se odemkne.

Tento režim je vhodný pro první pilotní nasazení, kdy licencí není mnoho a lze je sledovat ručně.

## 2. Automatizace vystavování licencí
Pro větší počet zákazníků je vhodné mít jednoduchý server, který:
- uchovává seznam zákazníků, zařízení, platnosti licencí a stav (aktivní / expirovaná / zrušená),
- dokáže vygenerovat licenci přímo z webového formuláře nebo API,
- vyžaduje přihlášení a audituje, kdo jakou licenci vytvořil,
- periodicky vyhodnocuje expirace a upozorňuje zákazníky.

### 2.1 Prototyp serveru v tomto repozitáři
Součástí projektu je skript [`video_collage/license_server.py`](../video_collage/license_server.py), který představuje první krok směrem k automatizaci. Nabízí HTTP API s endpointy `/licenses`, `/activations` a CSV exporty (`/report/licenses.csv`, `/report/activations.csv`), přičemž vydané licence a log aktivací ukládá do souboru `projects/licenses_db.json`. Díky tomu lze okamžitě:

- vystavovat licence přes `curl` nebo jednoduchý webhook bez nutnosti spouštět `license_cli` ručně,
- stáhnout přehled `GET /licenses` nebo rovnou hotové CSV (`/report/licenses.csv`, `/report/activations.csv`) a importovat je do Google Sheets nebo vlastního dashboardu,
- shromažďovat informace o tom, kdy klient validoval licenci (POST `/activations`).

Server používá stejný HMAC klíč jako CLI utilita, takže výstupní JSON je kompatibilní s existujícím softwarem. Databázi lze později nahradit plnohodnotnou SQL instancí, aniž by se měnilo klientské API.

### 2.2 Doporučená produkční architektura
 ### Doporučená architektura
1. **Backend**: např. FastAPI + PostgreSQL (nebo Supabase) s tabulkami `customers`, `devices`, `licenses`.
2. **Admin UI**: jednoduchá SPA (React/Vue) nebo server-rendered šablony, kde lze filtrovat licence, prodlužovat platnost a rušit zařízení.
3. **API pro klienta** (do budoucna): endpoint `/licenses/verify`, který vrací stav licence a případné aktualizace. V první verzi může klient stále používat offline JSON, ale připravte se na přechod na online kontrolu.
4. **Integrace s FFmpeg CLI**: server sdílí stejnou `SECRET_KEY`, kterou používá `license_cli`, takže je možné vystavovat kompatibilní podpisy.

## 3. Reporting a přehledy
Existují dvě možnosti, které lze i kombinovat:

### 3.1 Google Sheets / Looker Studio
- Server může pravidelně (např. pomocí CRON jobu nebo n8n/Make/Zapier) exportovat tabulku licencí do Google Sheets. Prototyp už poskytuje CSV endpoints, takže stačí `curl -s http://server/report/licenses.csv > licenses.csv` a soubor nahrát do Sheets.
- Sheets poslouží jako rychlý reporting (počty aktivních licencí, expirace příštích 30 dní, přehled podle zákazníka).
- Výhodou je jednoduché sdílení a známé prostředí. Nevýhodou je, že data jsou pouze tak aktuální, jak často export spouštíte.

### 3.2 Vestavěný dashboard
- Nad stejnou databází lze postavit vlastní dashboard (Grafana, Metabase nebo custom React komponenty), který data zobrazuje v reálném čase.
- Umožňuje hlubší filtrování, grafy a export do CSV.

## 4. Doporučený další postup
1. **Stabilizovat CLI** – mít jistotu, že vydané licence fungují a zákazníci je umějí aktivovat.
2. **Návrh databázového schématu** – definovat tabulky pro zákazníky, zařízení a licence (včetně historie).
3. **Vybudovat jednoduché admin rozhraní** pro ruční vystavování licencí z webu místo CLI.
4. **Zavést reporting** – minimálně automatický export do Google Sheets jednou denně; později přímý dashboard.
5. **Automatické notifikace** – např. e-mail při expiraci licence nebo detekci neautorizovaného zařízení.

Takový postup umožní začít hned (ruční vydávání) a zároveň mít jasnou cestu k profesionální správě licencí a přehledům.
