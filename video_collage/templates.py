"""Definice předpřipravených šablon mřížek."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


class Orientation(str, Enum):
    """Podporované orientace projektu."""

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass(frozen=True)
class TemplateSlot:
    """Jedna buňka ve zvolené šabloně."""

    id: str
    row: int
    column: int
    row_span: int = 1
    column_span: int = 1
    label: str | None = None


@dataclass(frozen=True)
class Template:
    """Popisuje mřížku, která se dá použít pro projekt."""

    template_id: str
    name: str
    rows: int
    columns: int
    slots: List[TemplateSlot]

    def describe(self) -> str:
        slot_summary = ", ".join(
            f"{slot.id}: r{slot.row}/c{slot.column} ({slot.row_span}x{slot.column_span})"
            for slot in self.slots
        )
        return f"{self.name} ({self.rows}×{self.columns}): {slot_summary}"


_BUILTIN_TEMPLATES: List[Template] = [
    Template(
        template_id="grid_2x2",
        name="Základní čtvercová mřížka 2×2",
        rows=2,
        columns=2,
        slots=[
            TemplateSlot("A", 0, 0, label="Levý horní"),
            TemplateSlot("B", 0, 1, label="Pravý horní"),
            TemplateSlot("C", 1, 0, label="Levý dolní"),
            TemplateSlot("D", 1, 1, label="Pravý dolní"),
        ],
    ),
    Template(
        template_id="grid_4x2",
        name="Panoramatická mřížka 4 řádky × 2 sloupce",
        rows=4,
        columns=2,
        slots=[
            TemplateSlot("A", 0, 0, label="Horní pás 1"),
            TemplateSlot("B", 1, 0, label="Horní pás 2"),
            TemplateSlot("C", 2, 0, label="Dolní pás 1"),
            TemplateSlot("D", 3, 0, label="Dolní pás 2"),
            TemplateSlot("E", 0, 1, label="Doplňkový sloupec 1"),
            TemplateSlot("F", 1, 1, label="Doplňkový sloupec 2"),
            TemplateSlot("G", 2, 1, label="Doplňkový sloupec 3"),
            TemplateSlot("H", 3, 1, label="Doplňkový sloupec 4"),
        ],
    ),
    Template(
        template_id="grid_3x3",
        name="Čtvercová mřížka 3×3",
        rows=3,
        columns=3,
        slots=[
            TemplateSlot("A", 0, 0, label="Levá horní"),
            TemplateSlot("B", 0, 1, label="Horní střed"),
            TemplateSlot("C", 0, 2, label="Pravá horní"),
            TemplateSlot("D", 1, 0, label="Levá střed"),
            TemplateSlot("E", 1, 1, label="Střed"),
            TemplateSlot("F", 1, 2, label="Pravá střed"),
            TemplateSlot("G", 2, 0, label="Levá dolní"),
            TemplateSlot("H", 2, 1, label="Dolní střed"),
            TemplateSlot("I", 2, 2, label="Pravá dolní"),
        ],
    ),
    Template(
        template_id="split_vertical",
        name="Dvě vertikální poloviny",
        rows=1,
        columns=2,
        slots=[
            TemplateSlot("A", 0, 0, column_span=1, row_span=1, label="Levá polovina"),
            TemplateSlot("B", 0, 1, column_span=1, row_span=1, label="Pravá polovina"),
        ],
    ),
    Template(
        template_id="picture_in_picture",
        name="Picture-in-picture (hlavní + overlay)",
        rows=2,
        columns=2,
        slots=[
            TemplateSlot("A", 0, 0, row_span=2, column_span=2, label="Hlavní video"),
            TemplateSlot("B", 0, 1, row_span=1, column_span=1, label="Overlay"),
        ],
    ),
]


def builtin_templates() -> List[Template]:
    return list(_BUILTIN_TEMPLATES)


class TemplateLibrary:
    """Spravuje dostupné šablony (vestavěné i uživatelské)."""

    def __init__(self, templates: Sequence[Template] | None = None):
        self._templates: Dict[str, Template] = {}
        if templates:
            self._register_many(templates)

    def _register_many(self, templates: Sequence[Template]) -> None:
        for template in templates:
            if template.template_id in self._templates:
                raise ValueError(
                    f"Šablona s ID '{template.template_id}' je již registrovaná."
                )
            self._templates[template.template_id] = template

    def list(self) -> List[Template]:
        return list(self._templates.values())

    def get(self, template_id: str) -> Template:
        try:
            return self._templates[template_id]
        except KeyError as exc:
            raise KeyError(f"Neznámá šablona '{template_id}'.") from exc

    def merged(self, templates: Sequence[Template]) -> "TemplateLibrary":
        library = TemplateLibrary(self.list())
        library._register_many(templates)
        return library


def load_templates_from_file(path: Path) -> List[Template]:
    """Načte šablony z JSON souboru.

    Očekávaný formát je buď list šablon, nebo objekt s klíčem
    `templates`. Každá šablona musí obsahovat id, name, rows, columns a
    pole `slots` s buňkami.
    """

    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        items = data.get("templates")
        if items is None:
            raise ValueError("JSON musí obsahovat klíč 'templates'.")
    elif isinstance(data, list):
        items = data
    else:
        raise ValueError("Neplatný formát JSON. Očekává se list nebo objekt s 'templates'.")

    templates: List[Template] = []
    for idx, item in enumerate(items, start=1):
        try:
            template = _parse_template_dict(item)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Šablona na indexu {idx} je neplatná: {exc}") from exc
        templates.append(template)
    return templates


def _parse_template_dict(data: Dict) -> Template:
    template_id = data["id"]
    name = data.get("name", template_id)
    rows = int(data["rows"])
    columns = int(data["columns"])
    if rows <= 0 or columns <= 0:
        raise ValueError("Rows a columns musí být kladná čísla.")
    slot_dicts = data["slots"]
    slots: List[TemplateSlot] = []
    for slot in slot_dicts:
        slots.append(
            TemplateSlot(
                id=slot["id"],
                row=int(slot.get("row", 0)),
                column=int(slot.get("column", 0)),
                row_span=int(slot.get("row_span", 1)),
                column_span=int(slot.get("column_span", 1)),
                label=slot.get("label"),
            )
        )
    return Template(template_id=template_id, name=name, rows=rows, columns=columns, slots=slots)
