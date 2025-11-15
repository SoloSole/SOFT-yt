"""Pomocné funkce pro výpočty rozložení šablon."""
from __future__ import annotations

from typing import Dict, Tuple

from .templates import Template


def calculate_slot_rectangles(
    template: Template, width: int, height: int
) -> Dict[str, Tuple[float, float, float, float]]:
    """Vrátí souřadnice obdélníků jednotlivých slotů v rámci dané plochy.

    Souřadnice jsou ve formátu ``(x0, y0, x1, y1)`` a respektují span řádků
    i sloupců. Funkce se používá pro vykreslování mřížky v GUI a je oddělena
    od Tkinteru, aby šla jednoduše testovat.
    """

    if width <= 0 or height <= 0:
        raise ValueError("Šířka i výška musí být kladné hodnoty.")
    if template.rows <= 0 or template.columns <= 0:
        raise ValueError("Šablona musí mít kladný počet řádků a sloupců.")

    cell_width = width / template.columns
    cell_height = height / template.rows

    rectangles: Dict[str, Tuple[float, float, float, float]] = {}
    for slot in template.slots:
        x0 = slot.column * cell_width
        y0 = slot.row * cell_height
        x1 = x0 + slot.column_span * cell_width
        y1 = y0 + slot.row_span * cell_height
        rectangles[slot.id] = (x0, y0, x1, y1)
    return rectangles

