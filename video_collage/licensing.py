"""Jednoduchá implementace HW fingerprintingu a práce s licencemi.

Modul obsahuje pomocné datové struktury pro získání unikátního otisku
počítače, serializaci licence a její validaci pomocí podepsaného
payloadu. Podpis je zatím řešen přes HMAC (sdílený tajný klíč), což je
plně dostačující pro prototyp. V produkční verzi se očekává náhrada za
asymetrickou kryptografii (např. Ed25519) a další ochranné vrstvy.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import platform
import socket
from typing import Dict, List, Optional


class LicenseError(RuntimeError):
    """Vyhazuje se při neplatné licenci nebo chybě validace."""


@dataclass(frozen=True)
class HardwareFingerprint:
    """Reprezentuje identifikátory zařízení."""

    hostname: str
    platform: str
    cpu: str
    mac_addresses: List[str]
    machine_id: Optional[str]

    def as_dict(self) -> Dict[str, object]:
        return {
            "hostname": self.hostname,
            "platform": self.platform,
            "cpu": self.cpu,
            "mac_addresses": self.mac_addresses,
            "machine_id": self.machine_id,
        }


def collect_hardware_fingerprint() -> HardwareFingerprint:
    """Sesbírá co nejvíc identifikátorů použitelného HW.

    Informace, které nelze zjistit, se uloží jako ``None``. MAC adresy se
    filtrují tak, aby se ignorovaly virtuální nebo neplatné adresy.
    """

    hostname = platform.node() or socket.gethostname()
    platform_name = f"{platform.system()} {platform.release()}"
    cpu = platform.processor() or platform.machine()
    mac_addresses = _detect_mac_addresses()
    machine_id = _read_machine_id()

    return HardwareFingerprint(
        hostname=hostname,
        platform=platform_name,
        cpu=cpu,
        mac_addresses=mac_addresses,
        machine_id=machine_id,
    )


def fingerprint_hash(fingerprint: HardwareFingerprint) -> str:
    """Vytvoří stabilní hash fingerprintu."""

    serialized = json.dumps(
        fingerprint.as_dict(),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


@dataclass(frozen=True)
class LicenseData:
    """Deserializovaná licence."""

    license_id: str
    fingerprint: str
    expires_at: datetime
    signature: str

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "LicenseData":
        try:
            expires_at_str = str(data["expires_at"])
            expires_at = datetime.fromisoformat(expires_at_str)
        except (KeyError, ValueError) as exc:
            raise LicenseError("Pole 'expires_at' není ve formátu ISO 8601.") from exc

        return cls(
            license_id=str(data.get("license_id")),
            fingerprint=str(data.get("fingerprint")),
            expires_at=expires_at,
            signature=str(data.get("signature")),
        )

    def message(self) -> bytes:
        return f"{self.license_id}:{self.fingerprint}:{self.expires_at.isoformat()}".encode(
            "utf-8"
        )


class LicenseManager:
    """Ověřuje licence vůči aktuálnímu zařízení."""

    def __init__(self, verification_key: str):
        if not verification_key:
            raise ValueError("Chybí verifikační klíč pro licence.")
        self.verification_key = verification_key

    def validate_license(
        self,
        license_path: Path,
        *,
        fingerprint: Optional[HardwareFingerprint] = None,
        current_time: Optional[datetime] = None,
    ) -> LicenseData:
        data = json.loads(license_path.read_text(encoding="utf-8"))
        license_data = LicenseData.from_dict(data)
        self._validate_expiration(license_data, current_time)
        expected_fingerprint = fingerprint_hash(
            fingerprint or collect_hardware_fingerprint()
        )
        if license_data.fingerprint != expected_fingerprint:
            raise LicenseError(
                "Licence neodpovídá tomuto zařízení. Požádej o novou aktivaci."
            )
        if not self._verify_signature(license_data):
            raise LicenseError(
                "Podpis licence je neplatný. Soubor mohl být upraven nebo je klíč chybný."
            )
        return license_data

    def _validate_expiration(
        self, license_data: LicenseData, current_time: Optional[datetime]
    ) -> None:
        now = current_time or datetime.now(timezone.utc)
        expires_at = license_data.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            raise LicenseError("Licence již vypršela. Obnov ji u dodavatele.")

    def _verify_signature(self, license_data: LicenseData) -> bool:
        secret = self.verification_key.encode("utf-8")
        expected = hmac.new(secret, license_data.message(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, license_data.signature)


def sign_license(
    *,
    license_id: str,
    fingerprint: str,
    expires_at: datetime,
    secret_key: str,
) -> Dict[str, str]:
    """Vytvoří datovou strukturu licence (typicky na serveru).

    Přestože klient by neměl k tajnému klíči přistupovat, tato funkce se
    hodí pro interní skripty. Z důvodu jednoduchosti není oddělena do
    samostatného balíčku.
    """

    payload = LicenseData(
        license_id=license_id,
        fingerprint=fingerprint,
        expires_at=expires_at,
        signature="",
    )
    signature = hmac.new(
        secret_key.encode("utf-8"), payload.message(), hashlib.sha256
    ).hexdigest()
    return {
        "license_id": payload.license_id,
        "fingerprint": payload.fingerprint,
        "expires_at": payload.expires_at.isoformat(),
        "signature": signature,
    }


def load_license_from_disk(
    license_path: Path, verification_key: Optional[str]
) -> LicenseData:
    """Načte a ověří licenci uloženou v souboru.

    Funkce sjednocuje základní validace (existence souboru a verifikačního
    klíče) tak, aby je mohly sdílet různé vstupní vrstvy (CLI, GUI).
    """

    if not license_path.exists():
        raise LicenseError(
            "Nebyla nalezena licence. Zadej cestu parametrem --license-file nebo soubor ulož do ./license.json."
        )
    if not verification_key:
        raise LicenseError(
            "Chybí verifikační klíč pro ověření licence. Použij --verification-key nebo proměnnou VIDEO_COLLAGE_VERIFICATION_KEY."
        )

    manager = LicenseManager(verification_key)
    return manager.validate_license(license_path)


def _detect_mac_addresses() -> List[str]:
    macs: List[str] = []
    sys_class_net = Path("/sys/class/net")
    if sys_class_net.exists():
        for interface in sys_class_net.iterdir():
            try:
                address = (interface / "address").read_text().strip()
            except OSError:
                continue
            if _is_valid_mac(address):
                macs.append(address.lower())
    if not macs:
        fallback = _format_mac(uuid_getnode())
        if fallback:
            macs.append(fallback)
    return macs


def _is_valid_mac(value: str) -> bool:
    parts = value.split(":")
    if len(parts) != 6:
        return False
    try:
        bytes(int(part, 16) for part in parts)
    except ValueError:
        return False
    return True


def uuid_getnode() -> int:
    import uuid

    return uuid.getnode()


def _format_mac(value: int) -> Optional[str]:
    if value <= 0 or value >> 40 & 1:
        return None
    return ":".join(f"{(value >> (i * 8)) & 0xFF:02x}" for i in reversed(range(6)))


def _read_machine_id() -> Optional[str]:
    candidates = [
        Path("/etc/machine-id"),
        Path("/var/lib/dbus/machine-id"),
        Path.home() / ".machine_id",
    ]
    for path in candidates:
        try:
            if path.exists():
                value = path.read_text(encoding="utf-8").strip()
                if value:
                    return value
        except OSError:
            continue
    return os.environ.get("VIDEO_COLLAGE_MACHINE_ID")


__all__ = [
    "HardwareFingerprint",
    "LicenseData",
    "LicenseError",
    "LicenseManager",
    "collect_hardware_fingerprint",
    "fingerprint_hash",
    "sign_license",
]

