"""Testy pro práci se šablonami."""
from pathlib import Path
import json

import pytest

from video_collage.templates import (
    Template,
    TemplateLibrary,
    TemplateSlot,
    builtin_templates,
    load_templates_from_file,
)


def test_builtin_templates_available():
    templates = builtin_templates()
    template_ids = {template.template_id for template in templates}
    assert {"grid_2x2", "grid_4x2"}.issubset(template_ids)


def test_template_library_detects_duplicate_ids():
    base_library = TemplateLibrary(builtin_templates())
    duplicate = Template(
        template_id="grid_2x2",
        name="dup",
        rows=1,
        columns=1,
        slots=[TemplateSlot("A", 0, 0)],
    )
    with pytest.raises(ValueError):
        base_library.merged([duplicate])


def test_load_templates_from_file(tmp_path: Path):
    config = {
        "templates": [
            {
                "id": "custom_grid",
                "name": "Custom",
                "rows": 1,
                "columns": 2,
                "slots": [
                    {"id": "A", "row": 0, "column": 0, "label": "Left"},
                    {"id": "B", "row": 0, "column": 1, "label": "Right"},
                ],
            }
        ]
    }
    path = tmp_path / "templates.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    templates = load_templates_from_file(path)

    assert len(templates) == 1
    assert templates[0].template_id == "custom_grid"
    assert templates[0].slots[1].label == "Right"
