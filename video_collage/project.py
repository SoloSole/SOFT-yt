"""Základní datové struktury projektu."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .templates import Orientation, Template, TemplateSlot


@dataclass
class ProjectSlot:
    slot: TemplateSlot
    video_path: Optional[str] = None

    def serialize(self) -> Dict[str, str | None]:
        data = {
            "slot_id": self.slot.id,
            "row": self.slot.row,
            "column": self.slot.column,
            "row_span": self.slot.row_span,
            "column_span": self.slot.column_span,
            "label": self.slot.label,
            "video_path": self.video_path,
        }
        return data


@dataclass
class Project:
    name: str
    orientation: Orientation
    template: Template
    slots: List[ProjectSlot] = field(default_factory=list)

    def assign_video(self, slot_id: str, path: str) -> None:
        for slot in self.slots:
            if slot.slot.id == slot_id:
                slot.video_path = path
                return
        raise KeyError(f"Slot '{slot_id}' nebyl nalezen v šabloně {self.template.template_id}.")

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "orientation": self.orientation.value,
            "template": {
                "id": self.template.template_id,
                "rows": self.template.rows,
                "columns": self.template.columns,
            },
            "slots": [slot.serialize() for slot in self.slots],
        }

    def save(self, target: Path) -> Path:
        target.parent.mkdir(parents=True, exist_ok=True)
        content = self.to_dict()
        target.write_text(_to_json(content), encoding="utf-8")
        return target


def create_project(name: str, orientation: Orientation, template: Template) -> Project:
    return Project(
        name=name,
        orientation=orientation,
        template=template,
        slots=[ProjectSlot(slot=s) for s in template.slots],
    )


def _to_json(data: Dict) -> str:
    import json

    return json.dumps(data, indent=2, ensure_ascii=False)
