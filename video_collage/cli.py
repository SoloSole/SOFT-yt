"""Jednoduché textové rozhraní pro vytvoření projektu se dvěma šablonami."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import os
from typing import Iterable, Optional

from .project import Project, create_project
from .templates import (
    Orientation,
    Template,
    TemplateLibrary,
    builtin_templates,
    load_templates_from_file,
)
from .exporter import ExportError, ExportSettings, export_project
from .licensing import LicenseData, LicenseError, load_license_from_disk


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Vytvoří konfigurační soubor pro kolážové video podle zvolené šablony.",
    )
    parser.add_argument(
        "--orientation",
        choices=[o.value for o in Orientation],
        help="Volitelně nastav orientaci bez dotazu (horizontal/vertical).",
    )
    parser.add_argument(
        "--template",
        help="ID šablony (např. grid_2x2). Pokud není zadáno, proběhne interaktivní výběr.",
    )
    parser.add_argument(
        "--project-name",
        help="Vlastní název projektu. Pokud není, vygeneruje se podle data.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("projects"),
        help="Adresář, kam se uloží výsledný JSON (výchozí ./projects).",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Pokud je nastaveno, sloty se nebudou ptát a zůstanou prázdné.",
    )
    parser.add_argument(
        "--resolution",
        type=_parse_resolution,
        help="Cílové rozlišení exportu ve formátu Š×V (např. 1920x1080).",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Počet snímků za sekundu při exportu (výchozí 30).",
    )
    parser.add_argument(
        "--export-video",
        type=Path,
        help="Pokud zadáš cestu, po vytvoření JSONu se pokusíme vytvořit i výsledné video (MP4).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Při exportu videa přepíše existující soubor (předává se do FFmpeg -y).",
    )
    parser.add_argument(
        "--license-file",
        type=Path,
        default=Path("license.json"),
        help="Cesta k licenčnímu souboru (JSON). Výchozí je ./license.json.",
    )
    parser.add_argument(
        "--verification-key",
        default=os.environ.get("VIDEO_COLLAGE_VERIFICATION_KEY"),
        help=(
            "Klíč pro ověření podpisu licence (HMAC). Lze předat také přes proměnnou "
            "VIDEO_COLLAGE_VERIFICATION_KEY."
        ),
    )
    parser.add_argument(
        "--templates-file",
        type=Path,
        help=(
            "Volitelný JSON soubor s vlastními šablonami. Přidané šablony lze pak zvolit "
            "stejným způsobem jako vestavěné."
        ),
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    license_data = _ensure_license(args.license_file, args.verification_key)
    library = _load_template_library(args.templates_file)
    orientation = _resolve_orientation(args.orientation)
    template = _resolve_template(args.template, library)
    project_name = args.project_name or datetime.now().strftime("projekt_%Y%m%d_%H%M%S")
    project = create_project(project_name, orientation, template)
    resolution = args.resolution or _default_resolution(orientation)

    if not args.non_interactive:
        _fill_slots(project)

    filename = args.output / f"{project.name}.json"
    project.save(filename)
    print(f"Licence {license_data.license_id} platná do {license_data.expires_at.isoformat()}.")
    print(f"Projekt uložen: {filename}")

    if args.export_video:
        _export_video(
            project,
            args.export_video,
            ExportSettings(width=resolution[0], height=resolution[1], fps=args.fps),
            overwrite=args.overwrite,
        )


def _resolve_orientation(value: Optional[str]) -> Orientation:
    if value:
        return Orientation(value)

    print("Vyber orientaci projektu:")
    for idx, option in enumerate(Orientation, start=1):
        print(f" {idx}. {option.value}")
    while True:
        choice = input("Zadej číslo orientace: ")
        try:
            idx = int(choice)
            orientation = list(Orientation)[idx - 1]
            return orientation
        except (ValueError, IndexError):
            print("Neplatná volba, zkus to znovu.")


def _resolve_template(template_id: Optional[str], library: TemplateLibrary) -> Template:
    templates = library.list()
    if template_id:
        try:
            return library.get(template_id)
        except KeyError as exc:
            raise SystemExit(str(exc))

    print("Dostupné šablony:")
    for idx, template in enumerate(templates, start=1):
        print(f" {idx}. {template.describe()} [id={template.template_id}]")

    while True:
        choice = input("Zadej číslo vybrané šablony: ")
        try:
            idx = int(choice)
            return templates[idx - 1]
        except (ValueError, IndexError):
            print("Neplatná volba, zkus to znovu.")


def _load_template_library(path: Optional[Path]) -> TemplateLibrary:
    library = TemplateLibrary(builtin_templates())
    if not path:
        return library
    try:
        extra = load_templates_from_file(path)
    except ValueError as exc:
        raise SystemExit(f"Soubor se šablonami je neplatný: {exc}")
    return library.merged(extra)


def _fill_slots(project: Project) -> None:
    print("\nNyní můžeš každému slotu přiřadit cestu k videu (nebo nech prázdné).")
    for slot in project.slots:
        prompt = f"Slot {slot.slot.id} ({slot.slot.label or 'bez popisu'}): "
        value = input(prompt).strip()
        if value:
            slot.video_path = value


def _parse_resolution(value: str) -> tuple[int, int]:
    try:
        width_str, height_str = value.lower().split("x", 1)
        width = int(width_str)
        height = int(height_str)
        if width <= 0 or height <= 0:
            raise ValueError
        return width, height
    except ValueError as exc:  # pragma: no cover - validaci řeší argparse
        raise argparse.ArgumentTypeError(
            "Rozlišení musí být ve formátu 1920x1080 a obsahovat kladná čísla."
        ) from exc


def _default_resolution(orientation: Orientation) -> tuple[int, int]:
    if orientation == Orientation.HORIZONTAL:
        return 1920, 1080
    return 1080, 1920


def _ensure_license(license_path: Path, verification_key: Optional[str]) -> LicenseData:
    try:
        return load_license_from_disk(license_path, verification_key)
    except LicenseError as exc:
        raise SystemExit(f"Licence je neplatná: {exc}")


def _export_video(
    project: Project,
    output_path: Path,
    settings: ExportSettings,
    *,
    overwrite: bool = False,
) -> None:
    try:
        result = export_project(project, output_path, settings, overwrite=overwrite)
    except ExportError as exc:
        print(f"Export videa se nezdařil: {exc}")
        return
    print(f"Video vyexportováno do souboru: {result}")


if __name__ == "__main__":  # pragma: no cover
    main()
