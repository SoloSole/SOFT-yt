"""Jádro prototypu pro skládání videa do šablon."""

from .templates import (
    Orientation,
    Template,
    TemplateSlot,
    TemplateLibrary,
    builtin_templates,
    load_templates_from_file,
)
from .project import Project, ProjectSlot
from .exporter import ExportSettings, export_project, ExportError
from .licensing import (
    HardwareFingerprint,
    LicenseData,
    LicenseError,
    LicenseManager,
    load_license_from_disk,
    collect_hardware_fingerprint,
    fingerprint_hash,
    sign_license,
)

__all__ = [
    "Orientation",
    "Template",
    "TemplateSlot",
    "Project",
    "ProjectSlot",
    "TemplateLibrary",
    "builtin_templates",
    "load_templates_from_file",
    "ExportSettings",
    "export_project",
    "ExportError",
    "HardwareFingerprint",
    "LicenseData",
    "LicenseError",
    "LicenseManager",
    "load_license_from_disk",
    "collect_hardware_fingerprint",
    "fingerprint_hash",
    "sign_license",
]
