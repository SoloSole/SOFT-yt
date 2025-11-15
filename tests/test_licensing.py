"""Testy pro načtení licence ze souboru."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest

from video_collage.licensing import (
    LicenseError,
    collect_hardware_fingerprint,
    fingerprint_hash,
    load_license_from_disk,
    sign_license,
)


@pytest.fixture()
def license_file(tmp_path: Path) -> Path:
    fingerprint = fingerprint_hash(collect_hardware_fingerprint())
    expires = datetime.now(timezone.utc) + timedelta(days=1)
    payload = sign_license(
        license_id="test", fingerprint=fingerprint, expires_at=expires, secret_key="SECRET"
    )
    path = tmp_path / "license.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_load_license_success(license_file: Path) -> None:
    data = load_license_from_disk(license_file, "SECRET")
    assert data.license_id == "test"


def test_load_license_missing_key(license_file: Path) -> None:
    with pytest.raises(LicenseError):
        load_license_from_disk(license_file, None)


def test_load_license_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    with pytest.raises(LicenseError):
        load_license_from_disk(missing, "SECRET")
