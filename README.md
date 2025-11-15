# SOFT-yt

Jednoduchý prototyp nástroje pro skládání videí do předdefinovaných šablon. Aktuální verze umožňuje vytvořit konfigurační soubor projektu s několika šablonami mřížek (2×2, 4×2, 3×3, split view, picture-in-picture), vybrat orientaci videa, přiřadit jednotlivým slotům cesty k videím a volitelně vyexportovat výsledné video pomocí FFmpeg. Export je zatím základní (bez zvuku, pouze přes `xstack`), ale pokládá základy pro další optimalizace a napojení na GUI/licencování. Nově obsahuje také nástroje pro licencování, generování HW fingerprintu a načítání vlastních šablon z JSONu.


## Jak prototyp použít
1. Ujisti se, že máš nainstalovaný Python 3.10+.
2. Připrav platnou licenci a ověřovací klíč (viz níže).
3. Spusť příkaz:
   ```bash
   python -m video_collage.cli
   ```
3. V konzoli vyber orientaci (horizontal/vertical), jednu ze dvou šablon a případně zadej cesty k videím pro jednotlivé sloty.
4. Výsledek se uloží do složky `projects/` jako JSON soubor (např. `projects/projekt_20240509_120000.json`).
5. Chceš-li rovnou vytvořit výstupní MP4, přidej parametr `--export-video cesta/k/vystupu.mp4`. Ujisti se, že máš nainstalovaný FFmpeg (příkaz `ffmpeg` dostupný v PATH) a každý slot obsahuje platnou cestu k videu.

Parametry CLI:
```bash
python -m video_collage.cli --help
```

## Grafické rozhraní (Tkinter)
Pokud nechceš zadávat cesty v konzoli, použij GUI prototyp:

```bash
VIDEO_COLLAGE_VERIFICATION_KEY=TAJNY python -m video_collage.gui --license-file license.json
```

GUI teď kromě základních polí nabízí i interaktivní náhled šablony na
plátně, který reaguje na výběr v tabulce slotů – buňky se zvýrazní po kliknutí
v seznamu nebo přímo v náhledu. Sloty lze spravovat dvojklikem nebo kontextovým
menu (pravé tlačítko myši). V sekci **Export videa** je možné rovnou nastavit
FPS, CRF, preset i použitý kodek a dedikovaným tlačítkem spustit export.

Přehled všech kroků najdeš v dokumentu [`docs/gui.md`](docs/gui.md).

Příklad exportu ve Full HD s 30 FPS (horizontální orientace má výchozí rozlišení 1920×1080, vertikální 1080×1920):

```bash
python -m video_collage.cli \
  --orientation horizontal \
  --template grid_2x2 \
  --project-name demo \
  --export-video renders/demo.mp4
```

### Vlastní šablony

Do CLI lze přidat libovolný počet vlastních šablon pomocí parametru `--templates-file`, který očekává JSON ve formátu:

```json
{
  "templates": [
    {
      "id": "grid_1x3",
      "name": "Vertikální pásy 1×3",
      "rows": 1,
      "columns": 3,
      "slots": [
        { "id": "A", "row": 0, "column": 0, "label": "Levý" },
        { "id": "B", "row": 0, "column": 1, "label": "Střed" },
        { "id": "C", "row": 0, "column": 2, "label": "Pravý" }
      ]
    }
  ]
}
```

Ukázkový soubor najdeš v `templates/custom_templates.example.json`. Šablony z JSONu se sloučí s vestavěnými a lze je vybírat jak interaktivně, tak parametrem `--template custom_id`. Pokud soubor obsahuje nevalidní data nebo duplicitní ID, CLI se ukončí s chybovou hláškou. Detailní popis formátu je v dokumentu [`docs/templates.md`](docs/templates.md).

## Další kroky
- Rozšířit počet šablon a možnost přidání vlastní mřížky uživatelem.
- Napojit se na FFmpeg a z JSON konfigurace vyrobit skutečné video (první jednoduchý export) **✔ hotovo v základní podobě**.
- Přidat základní správu licencí podle plánu v `PLAN.md` **✔ první verze fingerprintu a validace**.
- Připravit GUI podle požadovaného vzhledu (např. desktopová aplikace).

## Licencování a HW fingerprint
V adresáři `video_collage` je nyní dostupný modul `licensing` a CLI utilita `python -m video_collage.license_cli`. Ta umí:

1. Zobrazit a vyexportovat fingerprint zařízení
   ```bash
   python -m video_collage.license_cli fingerprint
   ```
   Výstup obsahuje detailní JSON (hostname, MAC adresy, machine-id) a hash, který lze poslat pro vystavení licence.

2. Na straně dodavatele podepsat licenci pro konkrétní hash (vyžaduje tajný klíč)
   ```bash
   python -m video_collage.license_cli sign <HASH> <LICENCE_ID> --secret-key "tajny_klic" --output licence.json
   ```

3. Na klientovi ověřit platnost licence (ve verifikačním klíči může být zabudován HMAC klíč)
   ```bash
   python -m video_collage.license_cli validate licence.json --verification-key "tajny_klic"
   ```

Podpis je aktuálně řešen přes HMAC se sdíleným tajemstvím, což je dostačující pro prototyp a testování. V produkční verzi je vhodné klíč ochránit (např. obfuskací) a nahradit algoritmus za asymetrickou kryptografii.

### Vydávání licencí a reporting

Krátkodobě lze licence vystavovat ručně pomocí `video_collage.license_cli sign` (viz výše). Jakmile se počet zákazníků zvýší, doporučuje se přejít na jednoduchý licenční server s databází zákazníků, zařízení a licencí a nad ním postavit admin rozhraní nebo integraci do Google Sheets / vlastního dashboardu. Konkrétní postup a architektura jsou shrnuty v dokumentu [`docs/licensing_workflow.md`](docs/licensing_workflow.md).

#### Minimální licenční server (součást repozitáře)

V adresáři `video_collage` je nově skript `license_server.py`, který poskytuje jednoduché HTTP API pro vystavování licencí a logování aktivací. Spuštění:

```bash
python -m video_collage.license_server --secret-key "TAJNY_KLIC"
```

Server běží na `http://127.0.0.1:8080` (lze změnit parametry `--host/--port`) a data ukládá do `projects/licenses_db.json`. Základní endpoints:

| Metoda | Cesta                       | Popis |
|--------|-----------------------------|-------|
| GET    | `/health`                   | Základní kontrola dostupnosti. |
| GET    | `/licenses`                 | Vrátí vydané licence, log aktivací a agregovaný přehled. |
| GET    | `/report/licenses.csv`      | Stáhne CSV se všemi licencemi (vhodné pro import do Google Sheets/Excelu). |
| GET    | `/report/activations.csv`   | Stáhne CSV log všech aktivací včetně metadat. |
| POST   | `/licenses`                 | Vystaví novou licenci. Payload: `{ "fingerprint": "...", "license_id": "volitelné", "valid_days": 30, "notes": "poznámka" }`. |
| POST   | `/activations`              | Zapíše aktivaci/validaci licence ze strany klienta. Payload: `{ "license_id": "...", "fingerprint": "...", "metadata": { "project": "demo" } }`. |

Příklad vystavení licence přes `curl`:

```bash
curl -X POST http://127.0.0.1:8080/licenses \
  -H "Content-Type: application/json" \
  -d '{"fingerprint":"74e0...","valid_days":14,"notes":"Demo zákazník"}'
```

Odpověď obsahuje finální JSON licence (stejný formát, jaký očekává `video_collage.cli`) a metadata uložená v databázi. Admin může kdykoli stáhnout přehled `GET /licenses` nebo rovnou hotové CSV (`/report/licenses.csv`), např. pro import do Google Sheets.

### Reporting a Google Sheets

CSV export je přímo připravený tak, aby šel nahrát do Sheets nebo jiného dashboardu:

```bash
curl -s http://127.0.0.1:8080/report/licenses.csv > licenses.csv
curl -s http://127.0.0.1:8080/report/activations.csv > activations.csv
```

V Google Sheets klikni na **Soubor → Importovat → Nahrát** a vyber soubor `licenses.csv`. Sloupce obsahují ID licence, fingerprint, platnost a aktuální stav (active/expired). Stejným způsobem lze nahrát log aktivací a vytvářet nad nimi grafy nebo upozornění na expirující licence.

### Napojení licence do hlavního CLI

Před spuštěním `video_collage.cli` je potřeba mít:

1. Soubor `license.json` (lze změnit parametrem `--license-file`), který vznikne příkazem `license_cli sign ...`.
2. Verifikační klíč. Ten lze předat přepínačem `--verification-key` nebo proměnnou prostředí `VIDEO_COLLAGE_VERIFICATION_KEY`.

Pokud licence chybí nebo je neplatná, CLI se ukončí s chybovou hláškou – každá operace (vytvoření projektu i export) je tak chráněna před nepovoleným použitím.

