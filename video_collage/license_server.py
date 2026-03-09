"""Jednoduchý HTTP server pro vystavování licencí a reporting."""
from __future__ import annotations

import argparse
import csv
import io
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional
from urllib.parse import urlparse
import uuid

from .licensing import sign_license


@dataclass
class LicenseRecord:
    """Metadata o vydané licenci uložené v databázi."""

    license_id: str
    fingerprint: str
    expires_at: str
    signature: str
    issued_at: str
    valid_days: int
    notes: Optional[str] = None


@dataclass
class ActivationRecord:
    """Záznam o aktivaci/ověření licence klientem."""

    license_id: str
    fingerprint: str
    timestamp: str
    metadata: Dict[str, str]


class LicenseDatabase:
    """Triviální JSON databáze uchovávající licence i log aktivací."""

    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()
        self._data = {"licenses": [], "activations": []}
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                raise SystemExit(
                    f"Databázový soubor {self.path} je poškozený. Smaž ho nebo oprav ručně."
                )

    def list_licenses(self) -> List[Dict[str, object]]:
        with self._lock:
            return list(self._data.get("licenses", []))

    def list_activations(self) -> List[Dict[str, object]]:
        with self._lock:
            return list(self._data.get("activations", []))

    def add_license(self, record: LicenseRecord) -> None:
        with self._lock:
            self._data.setdefault("licenses", []).append(asdict(record))
            self._save()

    def add_activation(self, record: ActivationRecord) -> None:
        with self._lock:
            self._data.setdefault("activations", []).append(asdict(record))
            self._save()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")


class LicenseServerConfig:
    def __init__(self, *, secret_key: str, default_valid_days: int, db: LicenseDatabase):
        if not secret_key:
            raise ValueError("Server vyžaduje tajný klíč pro podepisování licencí.")
        self.secret_key = secret_key
        self.default_valid_days = default_valid_days
        self.db = db


def create_handler(config: LicenseServerConfig) -> Callable[..., BaseHTTPRequestHandler]:
    class LicenseRequestHandler(BaseHTTPRequestHandler):
        server_version = "VideoCollageLicenseServer/0.1"

        def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler API)
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                self._send_json(HTTPStatus.OK, {"status": "ok"})
                return
            if parsed.path == "/licenses":
                self._handle_list_licenses()
                return
            if parsed.path == "/report/licenses.csv":
                self._handle_csv_report("licenses")
                return
            if parsed.path == "/report/activations.csv":
                self._handle_csv_report("activations")
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/licenses":
                self._handle_issue_license()
                return
            if parsed.path == "/activations":
                self._handle_log_activation()
                return
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found"})

        def log_message(self, format: str, *args) -> None:  # noqa: A003 (BaseHTTPRequestHandler API)
            # Ztišíme defaultní logy, protože server poběží často v CLI.
            return

        def _handle_list_licenses(self) -> None:
            licenses = config.db.list_licenses()
            activations = config.db.list_activations()
            active_count = sum(1 for item in licenses if _is_active(item))
            payload = {
                "total_licenses": len(licenses),
                "active_licenses": active_count,
                "activations_logged": len(activations),
                "licenses": licenses,
                "activations": activations,
            }
            self._send_json(HTTPStatus.OK, payload)

        def _handle_csv_report(self, report_type: str) -> None:
            if report_type == "licenses":
                rows = config.db.list_licenses()
                fieldnames = [
                    "license_id",
                    "fingerprint",
                    "issued_at",
                    "expires_at",
                    "valid_days",
                    "status",
                    "notes",
                ]
                formatted_rows = [
                    {
                        "license_id": row.get("license_id"),
                        "fingerprint": row.get("fingerprint"),
                        "issued_at": row.get("issued_at"),
                        "expires_at": row.get("expires_at"),
                        "valid_days": row.get("valid_days"),
                        "status": "active" if _is_active(row) else "expired",
                        "notes": row.get("notes") or "",
                    }
                    for row in rows
                ]
                filename = "licenses.csv"
            else:
                rows = config.db.list_activations()
                fieldnames = ["license_id", "fingerprint", "timestamp", "metadata"]
                formatted_rows = [
                    {
                        "license_id": row.get("license_id"),
                        "fingerprint": row.get("fingerprint"),
                        "timestamp": row.get("timestamp"),
                        "metadata": json.dumps(row.get("metadata", {}), ensure_ascii=False),
                    }
                    for row in rows
                ]
                filename = "activations.csv"

            csv_body = _rows_to_csv(fieldnames, formatted_rows)
            self._send_csv(csv_body, filename)

        def _handle_issue_license(self) -> None:
            data = self._read_json()
            if not isinstance(data, dict):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Request musí být JSON objekt."})
                return
            fingerprint = str(data.get("fingerprint", "")).strip()
            if not fingerprint:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Chybí fingerprint."})
                return
            license_id = str(data.get("license_id") or _generate_license_id())
            valid_days = int(data.get("valid_days") or config.default_valid_days)
            if valid_days <= 0:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "valid_days musí být kladné číslo."})
                return
            expires_at = datetime.now(timezone.utc) + timedelta(days=valid_days)
            license_payload = sign_license(
                license_id=license_id,
                fingerprint=fingerprint,
                expires_at=expires_at,
                secret_key=config.secret_key,
            )
            record = LicenseRecord(
                license_id=license_payload["license_id"],
                fingerprint=license_payload["fingerprint"],
                expires_at=license_payload["expires_at"],
                signature=license_payload["signature"],
                issued_at=datetime.now(timezone.utc).isoformat(),
                valid_days=valid_days,
                notes=str(data.get("notes")) if data.get("notes") else None,
            )
            config.db.add_license(record)
            response = {"license": license_payload, "metadata": asdict(record)}
            self._send_json(HTTPStatus.CREATED, response)

        def _handle_log_activation(self) -> None:
            data = self._read_json()
            if not isinstance(data, dict):
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Request musí být JSON objekt."})
                return
            license_id = str(data.get("license_id", "")).strip()
            fingerprint = str(data.get("fingerprint", "")).strip()
            if not license_id or not fingerprint:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": "license_id i fingerprint jsou povinné."})
                return
            if not _license_exists(config.db.list_licenses(), license_id):
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Licence neexistuje."})
                return
            metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
            record = ActivationRecord(
                license_id=license_id,
                fingerprint=fingerprint,
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata={str(k): str(v) for k, v in metadata.items()},
            )
            config.db.add_activation(record)
            self._send_json(HTTPStatus.CREATED, {"status": "logged", "activation": asdict(record)})

        def _read_json(self) -> object:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                return {}
            data = self.rfile.read(length)
            try:
                return json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                return {}

        def _send_json(self, status: HTTPStatus, payload: Dict[str, object]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_csv(self, body: str, filename: str) -> None:
            data = body.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", f"attachment; filename={filename}")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return LicenseRequestHandler


def _is_active(record: Dict[str, object]) -> bool:
    expires_at_str = str(record.get("expires_at", ""))
    try:
        expires_at = datetime.fromisoformat(expires_at_str)
    except ValueError:
        return False
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return expires_at > datetime.now(timezone.utc)


def _license_exists(licenses: List[Dict[str, object]], license_id: str) -> bool:
    return any(item.get("license_id") == license_id for item in licenses)


def _generate_license_id() -> str:
    return uuid.uuid4().hex[:12]


def _rows_to_csv(fieldnames: List[str], rows: List[Dict[str, object]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Spustí jednoduchý licenční server.")
    parser.add_argument("--host", default="127.0.0.1", help="Adresa, na které má server naslouchat.")
    parser.add_argument("--port", type=int, default=8080, help="Port pro HTTP server (výchozí 8080).")
    parser.add_argument(
        "--db-file",
        type=Path,
        default=Path("projects/licenses_db.json"),
        help="Kam se budou ukládat vydané licence a aktivace.",
    )
    parser.add_argument("--secret-key", required=True, help="Tajný klíč pro podpis licencí (HMAC).")
    parser.add_argument(
        "--default-valid-days",
        type=int,
        default=30,
        help="Kolik dní má licence platit, pokud klient nezadá jinak.",
    )
    return parser.parse_args(argv)


def run_server(args: argparse.Namespace) -> None:
    db = LicenseDatabase(args.db_file)
    config = LicenseServerConfig(secret_key=args.secret_key, default_valid_days=args.default_valid_days, db=db)
    handler = create_handler(config)
    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(
        f"Licenční server běží na http://{args.host}:{args.port} a ukládá data do {args.db_file}."
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nUkončuji server...")
    finally:
        server.server_close()


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    run_server(args)


if __name__ == "__main__":
    main()
