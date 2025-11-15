"""CLI nástroje související s licencemi."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
from typing import Iterable, Optional

from .licensing import (
    LicenseError,
    LicenseManager,
    collect_hardware_fingerprint,
    fingerprint_hash,
    sign_license,
)


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Správa licencí prototypu.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("fingerprint", help="Zobrazí HW fingerprint zařízení.")

    validate_parser = sub.add_parser("validate", help="Ověří platnost licence.")
    validate_parser.add_argument("license", type=Path, help="Cesta k JSON souboru s licencí.")
    validate_parser.add_argument(
        "--verification-key",
        required=True,
        help="HMAC klíč pro ověření podpisu (v produkci zabudovaný ve spustitelné aplikaci).",
    )

    sign_parser = sub.add_parser(
        "sign",
        help="Vygeneruje licenci (typicky na serveru, vyžaduje tajný klíč).",
    )
    sign_parser.add_argument("fingerprint", help="Hash fingerprintu, který má být licencován.")
    sign_parser.add_argument("license_id", help="ID licence (např. číslo objednávky).")
    sign_parser.add_argument(
        "--valid-days",
        type=int,
        default=30,
        help="Platnost licence ve dnech od dneška (výchozí 30).",
    )
    sign_parser.add_argument(
        "--secret-key",
        required=True,
        help="Tajný klíč pro podpis (nesmí být sdílen s klientem).",
    )
    sign_parser.add_argument(
        "--output",
        type=Path,
        help="Kam uložit JSON s licencí. Pokud není zadáno, vypíše se na STDOUT.",
    )

    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    if args.command == "fingerprint":
        _print_fingerprint()
        return 0
    if args.command == "validate":
        return _validate_license(Path(args.license), args.verification_key)
    if args.command == "sign":
        return _sign_license(args)
    return 1


def _print_fingerprint() -> None:
    fingerprint = collect_hardware_fingerprint()
    fingerprint_value = fingerprint_hash(fingerprint)
    print("HW fingerprint:")
    print(json.dumps(fingerprint.as_dict(), indent=2, ensure_ascii=False))
    print(f"Hash (posílej pro vystavení licence): {fingerprint_value}")


def _validate_license(license_path: Path, verification_key: str) -> int:
    manager = LicenseManager(verification_key)
    try:
        data = manager.validate_license(license_path)
    except LicenseError as exc:
        print(f"Licence je neplatná: {exc}")
        return 1
    expires_at = data.expires_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    print(f"Licence {data.license_id} je platná do {expires_at} UTC.")
    return 0


def _sign_license(args: argparse.Namespace) -> int:
    expires_at = datetime.now(timezone.utc) + timedelta(days=args.valid_days)
    license_data = sign_license(
        license_id=args.license_id,
        fingerprint=args.fingerprint,
        expires_at=expires_at,
        secret_key=args.secret_key,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(license_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Licence uložena do {args.output}")
    else:
        json.dump(license_data, sys.stdout, indent=2, ensure_ascii=False)
        print()
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI vstupní bod
    raise SystemExit(main())

