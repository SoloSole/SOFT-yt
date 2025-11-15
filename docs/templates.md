# Definice vlastních šablon

Prototyp umožňuje načítat šablony mřížek z externích JSON souborů, které se při startu CLI připojí k vestavěné knihovně (2×2, 4×2, 3×3, split view, picture-in-picture). Díky tomu lze připravit libovolné rozložení, aniž by bylo nutné upravovat zdrojový kód.

## Struktura JSON souboru

Soubor může obsahovat buď pole šablon, nebo objekt s klíčem `templates`. Každá šablona má následující vlastnosti:

| Klíč        | Typ     | Popis |
|-------------|---------|-------|
| `id`        | string  | Unikátní identifikátor. Používá se v CLI (`--template <id>`).
| `name`      | string  | Čitelný název zobrazený v interaktivním výběru. Pokud chybí, použije se `id`.
| `rows`      | integer | Počet řádků základní mřížky (> 0).
| `columns`   | integer | Počet sloupců základní mřížky (> 0).
| `slots`     | array   | Seznam buněk. Každá buňka je objekt popsaný níže.

Každý slot podporuje tyto klíče:

| Klíč           | Typ     | Výchozí | Popis |
|----------------|---------|---------|-------|
| `id`           | string  | –       | Identifikátor slotu (A, B, ...). Objevuje se v CLI.
| `row`          | integer | `0`     | Řádek, na kterém slot začíná (0-based).
| `column`       | integer | `0`     | Sloupec, na kterém slot začíná (0-based).
| `row_span`     | integer | `1`     | Kolik řádků slot pokrývá (pro větší panely).
| `column_span`  | integer | `1`     | Kolik sloupců slot pokrývá.
| `label`        | string  | `null`  | Popisek zobrazený v CLI.

## Ukázka

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

Soubor lze načíst parametrem CLI:

```bash
VIDEO_COLLAGE_VERIFICATION_KEY=SECRET python -m video_collage.cli \
  --license-file license.json \
  --templates-file templates/custom_templates.json
```

Pokud soubor obsahuje duplicitní ID nebo chybná data, CLI se ukončí s detailní chybou. Vzorový soubor je k dispozici v adresáři `templates/custom_templates.example.json`.
