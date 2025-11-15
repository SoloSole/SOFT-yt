"""Jednoduché desktopové rozhraní pro skládání videí."""
from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
from typing import Dict, Iterable, Optional

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .exporter import ExportError, ExportSettings, export_project
from .layout import calculate_slot_rectangles
from .licensing import LicenseData, LicenseError, load_license_from_disk
from .project import create_project
from .templates import (
    Orientation,
    Template,
    TemplateLibrary,
    builtin_templates,
    load_templates_from_file,
)


class VideoCollageApp:
    """Tkinter aplikace pro správu šablon a export projektu."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.license_data = self._load_license()
        self.library = self._load_template_library(args.templates_file)
        self.templates = self.library.list()
        self.slot_paths: Dict[str, str] = {}
        self.canvas_rectangles: Dict[str, int] = {}
        self.current_template: Optional[Template] = None
        
        self.root = tk.Tk()
        self.root.title("Video Collage Studio")
        self.project_name_var = tk.StringVar(value=args.project_name or self._default_project_name())
        self.orientation_var = tk.StringVar(
            value=args.orientation or Orientation.HORIZONTAL.value
        )
        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        default_width, default_height = self._default_resolution()
        self.width_var.set(str(default_width))
        self.height_var.set(str(default_height))
        self.export_path_var = tk.StringVar(value=str(args.export_video or ""))
        self.fps_var = tk.StringVar(value=str(args.fps))
        self.crf_var = tk.StringVar(value=str(args.crf))
        self.codec_var = tk.StringVar(value=args.codec or ExportSettings.codec)
        self.preset_var = tk.StringVar(value=args.preset or ExportSettings.preset)
        self.status_var = tk.StringVar(value=self._license_banner())

        self._build_ui()
        self._select_template(args.template)

    def _build_ui(self) -> None:
        root = ttk.Frame(self.root, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(root, text="Základní informace", font=("TkDefaultFont", 12, "bold"))
        header.grid(row=0, column=0, columnspan=3, sticky="w")

        ttk.Label(root, text="Název projektu:").grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Entry(root, textvariable=self.project_name_var, width=40).grid(
            row=1, column=1, sticky="we", columnspan=2, pady=(4, 0)
        )

        ttk.Label(root, text="Orientace:").grid(row=2, column=0, sticky="w", pady=(4, 0))
        orientation_menu = ttk.Combobox(
            root,
            textvariable=self.orientation_var,
            values=[o.value for o in Orientation],
            state="readonly",
        )
        orientation_menu.grid(row=2, column=1, sticky="w", pady=(4, 0))
        orientation_menu.bind("<<ComboboxSelected>>", self._on_orientation_change)

        ttk.Label(root, text="Rozlišení (Š×V):").grid(row=3, column=0, sticky="w", pady=(4, 0))
        resolution_frame = ttk.Frame(root)
        resolution_frame.grid(row=3, column=1, sticky="w")
        ttk.Entry(resolution_frame, textvariable=self.width_var, width=7).pack(side=tk.LEFT)
        ttk.Label(resolution_frame, text="×").pack(side=tk.LEFT, padx=4)
        ttk.Entry(resolution_frame, textvariable=self.height_var, width=7).pack(side=tk.LEFT)

        ttk.Separator(root, orient=tk.HORIZONTAL).grid(
            row=4, column=0, columnspan=3, pady=12, sticky="we"
        )

        templates_label = ttk.Label(root, text="Šablony", font=("TkDefaultFont", 11, "bold"))
        templates_label.grid(row=5, column=0, sticky="w")

        self.template_list = tk.Listbox(root, height=10)
        self.template_list.grid(row=6, column=0, rowspan=5, sticky="nswe")
        self.template_list.bind("<<ListboxSelect>>", self._on_template_select)
        for template in self.templates:
            self.template_list.insert(tk.END, template.describe())

        preview_frame = ttk.LabelFrame(root, text="Náhled mřížky")
        preview_frame.grid(row=5, column=1, columnspan=2, sticky="nsew", padx=(12, 0))
        preview_width, preview_height = self._preview_dimensions()
        self.canvas = tk.Canvas(
            preview_frame,
            width=preview_width,
            height=preview_height,
            background="white",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda _event: self._redraw_preview())

        slots_frame = ttk.Frame(root)
        slots_frame.grid(row=6, column=1, columnspan=2, rowspan=3, sticky="nsew", padx=(12, 0))
        ttk.Label(slots_frame, text="Sloty a videa", font=("TkDefaultFont", 11, "bold")).pack(
            anchor="w"
        )

        columns = ("slot", "label", "path")
        self.slots_tree = ttk.Treeview(slots_frame, columns=columns, show="headings", height=8)
        self.slots_tree.heading("slot", text="Slot")
        self.slots_tree.heading("label", text="Popis")
        self.slots_tree.heading("path", text="Video")
        self.slots_tree.column("slot", width=60, stretch=False)
        self.slots_tree.column("label", width=120)
        self.slots_tree.column("path", width=260)
        self.slots_tree.pack(fill=tk.BOTH, expand=True, pady=(4, 4))
        self.slots_tree.bind("<<TreeviewSelect>>", self._on_slot_select)
        self.slots_tree.bind("<Double-1>", lambda _event: self._browse_video())

        self.slot_menu = tk.Menu(self.root, tearoff=0)
        self.slot_menu.add_command(label="Vybrat video…", command=self._browse_video)
        self.slot_menu.add_command(label="Odebrat video", command=self._clear_video)
        self.slots_tree.bind("<Button-3>", self._show_slot_menu)

        buttons = ttk.Frame(root)
        buttons.grid(row=9, column=1, columnspan=2, sticky="w", padx=(12, 0))
        ttk.Button(buttons, text="Vybrat video", command=self._browse_video).pack(side=tk.LEFT)
        ttk.Button(buttons, text="Odebrat video", command=self._clear_video).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        export_frame = ttk.LabelFrame(root, text="Export videa")
        export_frame.grid(row=10, column=1, columnspan=2, sticky="we", padx=(12, 0), pady=(8, 0))
        ttk.Label(export_frame, text="Cílový soubor:").grid(row=0, column=0, sticky="w")
        ttk.Entry(export_frame, textvariable=self.export_path_var, width=40).grid(
            row=0, column=1, sticky="we"
        )
        ttk.Button(export_frame, text="Vybrat", command=self._browse_export).grid(row=0, column=2, padx=(6, 0))

        ttk.Label(export_frame, text="FPS:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(export_frame, textvariable=self.fps_var, width=6).grid(row=1, column=1, sticky="w", pady=(6, 0))
        ttk.Label(export_frame, text="CRF:").grid(row=1, column=2, sticky="w", pady=(6, 0))
        ttk.Entry(export_frame, textvariable=self.crf_var, width=6).grid(row=1, column=3, sticky="w", pady=(6, 0))

        ttk.Label(export_frame, text="Preset:").grid(row=2, column=0, sticky="w")
        preset_box = ttk.Combobox(
            export_frame,
            textvariable=self.preset_var,
            values=[
                "ultrafast",
                "superfast",
                "veryfast",
                "faster",
                "fast",
                "medium",
                "slow",
                "slower",
                "veryslow",
            ],
            state="readonly",
        )
        preset_box.grid(row=2, column=1, sticky="w")
        ttk.Label(export_frame, text="Kodek:").grid(row=2, column=2, sticky="w")
        ttk.Entry(export_frame, textvariable=self.codec_var, width=12).grid(row=2, column=3, sticky="w")

        ttk.Button(export_frame, text="Exportovat video", command=self._handle_export_click).grid(
            row=3, column=0, columnspan=4, sticky="e", pady=(8, 0)
        )

        footer = ttk.Frame(root)
        footer.grid(row=11, column=0, columnspan=3, sticky="we", pady=(12, 0))
        ttk.Button(footer, text="Uložit projekt", command=self._save_project).pack(side=tk.LEFT)
        ttk.Label(footer, textvariable=self.status_var).pack(side=tk.LEFT, padx=12)

        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.columnconfigure(2, weight=1)
        root.rowconfigure(6, weight=1)
        root.rowconfigure(7, weight=1)

    # Event handlers -----------------------------------------------------
    def _on_orientation_change(self, *_: object) -> None:
        width, height = self._default_resolution()
        self.width_var.set(str(width))
        self.height_var.set(str(height))
        self._redraw_preview()

    def _on_template_select(self, event: object) -> None:  # pragma: no cover - UI vazba
        selection = self.template_list.curselection()
        if not selection:
            return
        idx = selection[0]
        template = self.templates[idx]
        self._populate_slots(template)

    def _on_slot_select(self, _event: object) -> None:  # pragma: no cover - UI vazba
        self._highlight_canvas_slot(self._selected_slot_id())

    def _show_slot_menu(self, event: tk.Event) -> None:  # pragma: no cover - UI vazba
        row_id = self.slots_tree.identify_row(event.y)
        if row_id:
            self.slots_tree.selection_set(row_id)
            self._highlight_canvas_slot(row_id)
            try:
                self.slot_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.slot_menu.grab_release()

    def _browse_video(self) -> None:  # pragma: no cover - UI vazba
        slot_id = self._selected_slot_id()
        if not slot_id:
            messagebox.showinfo("Slot není vybrán", "Vyber slot v tabulce slotů.")
            return
        filename = filedialog.askopenfilename(
            title="Vyber video",
            filetypes=[
                ("Video soubory", "*.mp4 *.mov *.mkv *.avi"),
                ("Všechny soubory", "*.*"),
            ],
        )
        if not filename:
            return
        self.slot_paths[slot_id] = filename
        self._refresh_slot_row(slot_id)

    def _clear_video(self) -> None:  # pragma: no cover - UI vazba
        slot_id = self._selected_slot_id()
        if not slot_id:
            return
        self.slot_paths.pop(slot_id, None)
        self._refresh_slot_row(slot_id)

    def _browse_export(self) -> None:  # pragma: no cover - UI vazba
        filename = filedialog.asksaveasfilename(
            title="Cílový soubor videa",
            defaultextension=".mp4",
            filetypes=[("MP4 video", "*.mp4"), ("Všechny soubory", "*.*")],
        )
        if filename:
            self.export_path_var.set(filename)

    # Helpers -------------------------------------------------------------
    def _load_license(self) -> LicenseData:
        try:
            return load_license_from_disk(self.args.license_file, self.args.verification_key)
        except LicenseError as exc:
            raise SystemExit(f"Licence je neplatná: {exc}") from exc

    def _load_template_library(self, path: Optional[Path]) -> TemplateLibrary:
        library = TemplateLibrary(builtin_templates())
        if not path:
            return library
        try:
            custom = load_templates_from_file(path)
        except ValueError as exc:
            raise SystemExit(f"Soubor se šablonami je neplatný: {exc}") from exc
        return library.merged(custom)

    def _license_banner(self) -> str:
        expires = self.license_data.expires_at.strftime("%Y-%m-%d")
        return f"Licence {self.license_data.license_id} platná do {expires}"

    def _default_project_name(self) -> str:
        return datetime.now().strftime("projekt_%Y%m%d_%H%M%S")

    def _default_resolution(self) -> tuple[int, int]:
        orientation = Orientation(self.orientation_var.get())
        if orientation == Orientation.HORIZONTAL:
            return 1920, 1080
        return 1080, 1920

    def _select_template(self, template_id: Optional[str]) -> None:
        if not self.templates:
            return
        index = 0
        if template_id:
            for idx, template in enumerate(self.templates):
                if template.template_id == template_id:
                    index = idx
                    break
        self.template_list.selection_clear(0, tk.END)
        self.template_list.selection_set(index)
        self.template_list.see(index)
        self._populate_slots(self.templates[index])

    def _populate_slots(self, template: Template) -> None:
        self.slots_tree.delete(*self.slots_tree.get_children())
        self.slot_paths = {}
        self.current_template = template
        for slot in template.slots:
            self.slots_tree.insert(
                "",
                tk.END,
                iid=slot.id,
                values=(slot.id, slot.label or "", ""),
            )
        self._redraw_preview()
        self._highlight_canvas_slot(None)

    def _refresh_slot_row(self, slot_id: str) -> None:
        if not self.slots_tree.exists(slot_id):
            return
        path = self.slot_paths.get(slot_id, "")
        current = self.slots_tree.item(slot_id)["values"]
        self.slots_tree.item(slot_id, values=(current[0], current[1], path))

    def _selected_slot_id(self) -> Optional[str]:
        selection = self.slots_tree.selection()
        if not selection:
            return None
        return selection[0]

    def _highlight_canvas_slot(self, slot_id: Optional[str]) -> None:
        for item_id, rect_id in self.canvas_rectangles.items():
            if item_id == slot_id:
                self.canvas.itemconfigure(rect_id, outline="#ff9800", width=3)
            else:
                self.canvas.itemconfigure(rect_id, outline="#333333", width=1)

    def _preview_dimensions(self) -> tuple[int, int]:
        orientation = Orientation(self.orientation_var.get())
        if orientation == Orientation.HORIZONTAL:
            return 420, 260
        return 260, 420

    def _redraw_preview(self) -> None:
        if not hasattr(self, "canvas") or not self.current_template:
            return
        width, height = self._preview_dimensions()
        self.canvas.config(width=width, height=height)
        self.canvas.delete("all")
        margin = 12
        drawing_width = max(10, width - 2 * margin)
        drawing_height = max(10, height - 2 * margin)
        rectangles = calculate_slot_rectangles(self.current_template, drawing_width, drawing_height)
        self.canvas_rectangles = {}
        for slot in self.current_template.slots:
            x0, y0, x1, y1 = rectangles[slot.id]
            x0 += margin
            y0 += margin
            x1 += margin
            y1 += margin
            color = self._slot_color(slot.id)
            rect_id = self.canvas.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=color,
                outline="#333333",
                width=1,
                tags=(f"slot_{slot.id}",),
            )
            self.canvas.create_text(
                (x0 + x1) / 2,
                (y0 + y1) / 2,
                text=slot.id,
                font=("TkDefaultFont", 11, "bold"),
                fill="#1a1a1a",
                tags=(f"slot_{slot.id}",),
            )
            self.canvas_rectangles[slot.id] = rect_id
            self.canvas.tag_bind(
                f"slot_{slot.id}",
                "<Button-1>",
                lambda _event, sid=slot.id: self._select_slot_from_canvas(sid),
            )
        self._highlight_canvas_slot(self._selected_slot_id())

    def _slot_color(self, slot_id: str) -> str:
        base = abs(hash(slot_id)) % 0xFFFFFF
        r = 200 + (base & 0x0F)
        g = 180 + ((base >> 4) & 0x0F)
        b = 160 + ((base >> 8) & 0x0F)
        r = min(r, 255)
        g = min(g, 255)
        b = min(b, 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _select_slot_from_canvas(self, slot_id: str) -> None:  # pragma: no cover - UI vazba
        if not self.slots_tree.exists(slot_id):
            return
        self.slots_tree.selection_set(slot_id)
        self.slots_tree.focus(slot_id)
        self.slots_tree.see(slot_id)
        self._highlight_canvas_slot(slot_id)

    def _gather_project(self) -> tuple[Template, Orientation, str]:
        selection = self.template_list.curselection()
        if not selection:
            raise ValueError("Není vybrána žádná šablona.")
        template = self.templates[selection[0]]
        orientation = Orientation(self.orientation_var.get())
        project_name = self.project_name_var.get().strip() or self._default_project_name()
        return template, orientation, project_name

    def _parse_resolution(self) -> tuple[int, int]:
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
        except ValueError as exc:
            raise ValueError("Rozlišení musí být čísla.") from exc
        if width <= 0 or height <= 0:
            raise ValueError("Rozlišení musí být kladné.")
        return width, height

    def _parse_fps(self) -> int:
        try:
            fps = int(self.fps_var.get())
        except ValueError as exc:
            raise ValueError("FPS musí být číslo.") from exc
        if fps <= 0:
            raise ValueError("FPS musí být kladné.")
        return fps

    def _parse_crf(self) -> int:
        try:
            crf = int(self.crf_var.get())
        except ValueError as exc:
            raise ValueError("CRF musí být číslo.") from exc
        if crf < 0 or crf > 51:
            raise ValueError("CRF musí být v rozmezí 0–51.")
        return crf

    def _save_project(self, *, trigger_export: bool = False) -> None:  # pragma: no cover - interakce
        try:
            template, orientation, name = self._gather_project()
            width, height = self._parse_resolution()
            fps = self._parse_fps()
            crf = self._parse_crf()
        except ValueError as exc:
            messagebox.showerror("Neplatná konfigurace", str(exc))
            return

        project = create_project(name, orientation, template)
        for slot in project.slots:
            slot.video_path = self.slot_paths.get(slot.slot.id)

        output_dir: Path = self.args.output
        output_dir.mkdir(parents=True, exist_ok=True)
        project_path = output_dir / f"{project.name}.json"
        project.save(project_path)
        self.status_var.set(f"Projekt uložen: {project_path}")
        if not trigger_export:
            messagebox.showinfo("Hotovo", f"Projekt uložen do {project_path}")
            return

        export_path = self._export_path()
        if export_path is None:
            messagebox.showerror("Chybí cílový soubor", "Zadej cestu pro export videa.")
            return

        try:
            result = export_project(
                project,
                export_path,
                self._build_export_settings(width, height, fps, crf),
                overwrite=self.args.overwrite,
            )
            self.status_var.set(f"Video vyexportováno: {result}")
            messagebox.showinfo("Export dokončen", f"Video vyexportováno do {result}")
        except ExportError as exc:
            messagebox.showerror("Chyba exportu", str(exc))

    def _handle_export_click(self) -> None:  # pragma: no cover - interakce
        if not self.export_path_var.get().strip():
            messagebox.showerror("Chybí cílový soubor", "Vyplň cestu pro export videa.")
            return
        self._save_project(trigger_export=True)

    def _export_path(self) -> Optional[Path]:
        value = self.export_path_var.get().strip()
        if not value:
            return None
        return Path(value)

    def _build_export_settings(self, width: int, height: int, fps: int, crf: int) -> ExportSettings:
        codec = self.codec_var.get().strip() or ExportSettings.codec
        preset = self.preset_var.get().strip() or ExportSettings.preset
        return ExportSettings(
            width=width,
            height=height,
            fps=fps,
            crf=crf,
            codec=codec,
            preset=preset,
        )

    def run(self) -> None:  # pragma: no cover - hlavní smyčka
        self.root.mainloop()


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Spustí GUI pro skládání videí do šablon.")
    parser.add_argument("--license-file", type=Path, default=Path("license.json"))
    parser.add_argument(
        "--verification-key",
        default=os.environ.get("VIDEO_COLLAGE_VERIFICATION_KEY"),
        help="Klíč pro ověření licence (lze zadat i proměnnou VIDEO_COLLAGE_VERIFICATION_KEY)",
    )
    parser.add_argument("--templates-file", type=Path, help="Volitelný JSON se šablonami.")
    parser.add_argument("--project-name", help="Výchozí název projektu.")
    parser.add_argument("--orientation", choices=[o.value for o in Orientation])
    parser.add_argument("--template", help="ID šablony, která bude vybraná po startu.")
    parser.add_argument("--output", type=Path, default=Path("projects"))
    parser.add_argument("--export-video", type=Path, help="Cílový MP4 soubor předvyplněný v GUI.")
    parser.add_argument("--fps", type=int, default=30, help="FPS pro export.")
    parser.add_argument("--crf", type=int, default=18, help="Hodnota CRF pro libx264.")
    parser.add_argument("--codec", default="libx264", help="Video kodek (např. libx264, libx265).")
    parser.add_argument("--preset", default="medium", help="FFmpeg preset pro enkodér.")
    parser.add_argument("--overwrite", action="store_true", help="Povolit přepsání existujícího videa.")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Optional[Iterable[str]] = None) -> None:  # pragma: no cover - Tk smyčka
    args = parse_args(argv)
    app = VideoCollageApp(args)
    app.run()


if __name__ == "__main__":  # pragma: no cover
    main()
