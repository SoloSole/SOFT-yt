"""Základní napojení na FFmpeg pro export projektu."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
from typing import List

from .project import Project


class ExportError(RuntimeError):
    """Vyhazuje se při chybě exportu (chybějící soubor, FFmpeg apod.)."""


@dataclass(frozen=True)
class ExportSettings:
    width: int
    height: int
    fps: int = 30
    codec: str = "libx264"
    crf: int = 18
    preset: str = "medium"
    pixel_format: str = "yuv420p"


def export_project(
    project: Project,
    output_path: Path,
    settings: ExportSettings,
    *,
    overwrite: bool = False,
) -> Path:
    """Spustí FFmpeg s `xstack` filtrem a vytvoří výsledné video."""

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise ExportError("FFmpeg není v PATH. Nainstaluj jej a spusť znovu.")

    video_inputs = _collect_inputs(project)
    filter_complex = _build_filter(project, settings)

    cmd: List[str] = [ffmpeg]
    for video_path in video_inputs:
        cmd.extend(["-i", str(video_path)])

    cmd.extend(
        [
            "-filter_complex",
            filter_complex,
            "-map",
            "[vout]",
            "-c:v",
            settings.codec,
            "-preset",
            settings.preset,
            "-crf",
            str(settings.crf),
            "-r",
            str(settings.fps),
            "-pix_fmt",
            settings.pixel_format,
            "-an",  # audio zatím ignorujeme
        ]
    )

    cmd.append("-y" if overwrite else "-n")
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd.append(str(output_path))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - závislé na FFmpeg
        raise ExportError(f"FFmpeg selhal s návratovým kódem {exc.returncode}.") from exc

    return output_path


def _collect_inputs(project: Project) -> List[Path]:
    paths: List[Path] = []
    for slot in project.slots:
        if not slot.video_path:
            raise ExportError(
                f"Slot {slot.slot.id} nemá přiřazené video. Bez toho nelze exportovat."
            )
        path = Path(slot.video_path).expanduser()
        if not path.exists():
            raise ExportError(f"Soubor '{path}' neexistuje.")
        paths.append(path)
    return paths


def _build_filter(project: Project, settings: ExportSettings) -> str:
    template = project.template
    cell_width = max(1, settings.width // template.columns)
    cell_height = max(1, settings.height // template.rows)

    filter_parts: List[str] = []
    labels: List[str] = []

    for idx, slot in enumerate(project.slots):
        width = cell_width * slot.slot.column_span
        height = cell_height * slot.slot.row_span
        label = f"s{idx}"
        labels.append(f"[{label}]")
        filter_parts.append(
            (
                f"[{idx}:v]scale=w={width}:h={height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1[{label}]"
            )
        )

    layout_parts = [
        f"{slot.slot.column * cell_width}_{slot.slot.row * cell_height}"
        for slot in project.slots
    ]

    stack_inputs = "".join(labels)
    filter_parts.append(
        f"{stack_inputs}xstack=inputs={len(project.slots)}:layout={'|'.join(layout_parts)}:fill=black[vout]"
    )

    return ";".join(filter_parts)

