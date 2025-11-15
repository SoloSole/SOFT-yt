# GUI prototyp

Součástí projektu je desktopové rozhraní postavené na Tkinteru
(`python -m video_collage.gui`). Umožňuje konfigurovat projekt obdobně jako
konzolová utilita, ale s přehledným výběrem šablon, vizuálním náhledem a
bohatšími možnostmi exportu.

## Funkce
- výběr orientace projektu a výchozího rozlišení,
- seznam vestavěných i vlastních šablon (stejný JSON formát jako pro CLI),
- interaktivní plátno s náhledem mřížky; buňky se zvýrazní při výběru slotu a
  lze je vybírat přímo kliknutím v náhledu,
- tabulka slotů, u kterých lze přes dialog vybrat nebo odebrat konkrétní video
  (dvojklikem nebo kontextovým menu),
- pole pro název projektu, výstupní rozlišení, FPS, CRF, preset, kodek a cílový
  MP4 soubor,
- tlačítko „Uložit projekt“, které vytvoří JSON v adresáři `projects/`,
- tlačítko „Exportovat video“, které po uložení projektu spustí FFmpeg s
  nastavenými parametry.

## Spuštění
```bash
VIDEO_COLLAGE_VERIFICATION_KEY=TAJNY python -m video_collage.gui \
  --license-file license.json \
  --templates-file templates/custom_templates.example.json
```

Stejně jako u CLI je nutné mít platnou licenci a verifikační klíč. Volitelné
parametry `--project-name`, `--orientation`, `--template`, `--fps`, `--crf`,
`--codec`, `--preset` a `--export-video` pouze předvyplňují příslušná pole v UI.

## Workflow
1. Spusť GUI s licencí (viz výše) a vyber orientaci + šablonu z levého panelu.
2. Sleduj náhled v horní části – kliknutím na slot v náhledu se vybere odpovídající řádek v tabulce.
3. V tabulce slotů použij dvojklik nebo pravé tlačítko myši → „Vybrat video…“ pro přiřazení klipu.
4. Vyplň rozlišení, FPS/CRF/preset a cílový soubor v sekci „Export videa“.
5. Klikni na „Uložit projekt“ pro vytvoření JSON konfigurace a následně na „Exportovat video“.

Pro pokročilejší úpravy (drag & drop, náhled samotného videa) je připraven prostor v roadmapě, ale tento prototyp již pokrývá kompletní workflow vytvoření projektu bez práce v konzoli.
