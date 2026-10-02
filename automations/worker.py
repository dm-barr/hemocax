#!/usr/bin/env python3
"""HEMOCAX scheduled automation and email bridge (stdlib only)."""

from __future__ import annotations

import json
import logging
import os
import smtplib
import ssl
import sys
import time
from datetime import datetime, timedelta, timezone as dt_timezone
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

LOG = logging.getLogger("hemocax.automations")
SCHEDULE = {
    "BIRTHDAY": "08:00",
    "RETURN_REMINDER": "08:15",
    "DONATION_THANKS": "08:30",
    "FREQUENT_DONOR": "08:45",
}


def load_local_env() -> None:
    """Read the ignored project .env for direct local runs; process env wins."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key and key.replace("_", "").isalnum() and key not in os.environ:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            os.environ[key] = value
TYPE_TO_SUBJECT = {
    "BIRTHDAY": "¡Feliz cumpleaños de parte de HEMOCAX!",
    "RETURN_REMINDER": "Ya puedes volver a donar sangre",
    "DONATION_THANKS": "Gracias por tu donación de sangre",
    "FREQUENT_DONOR": "Reconocimiento a tu compromiso como donante",
    "CAMPAIGN": "Campaña del Banco de Sangre HRDC",
    "MANUAL": "Mensaje del Banco de Sangre HRDC",
    "RESULT": "Tienes un resultado disponible en tu portal HEMOCAX",
}


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def json_request(url: str, payload: dict, headers: dict | None = None) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    req = Request(url, data=body, method="POST", headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urlopen(req, timeout=20) as response:
            data = response.read(1_000_000)
            return response.status, json.loads(data) if data else {}
    except HTTPError as exc:
        detail = exc.read(4000).decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"No se pudo conectar con el servicio: {exc}") from exc


def callback(communication_id: int, status: str, external_id: str | None = None, error: str | None = None) -> None:
    api = os.getenv("HEMOCAX_API_URL", "http://localhost:3000").rstrip("/")
    secret = os.getenv("AUTOMATION_WEBHOOK_SECRET", "")
    if not secret:
        LOG.warning("No se registró el estado de comunicación %s: falta AUTOMATION_WEBHOOK_SECRET", communication_id)
        return
    try:
        json_request(
            f"{api}/api/communications/webhook",
            {"communication_id": communication_id, "status": status, "external_id": external_id, "error_message": error},
            {"x-hemocax-webhook-secret": secret},
        )
    except RuntimeError:
        LOG.exception("No se pudo devolver el estado de comunicación %s a HEMOCAX", communication_id)


def send_email(payload: dict) -> tuple[str, str | None, str | None]:
    """Send a plain-text email over SMTP; no third-party account or template approval needed."""
    if env_bool("AUTOMATION_DRY_RUN", True):
        LOG.info("SIMULACIÓN: correo omitido (tipo=%s, id=%s)", payload.get("type"), payload.get("communication_id"))
        return "DEMO_QUEUED", None, None

    host = os.getenv("SMTP_HOST", "").strip()
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    from_address = os.getenv("EMAIL_FROM_ADDRESS", "").strip() or username
    to_address = str(payload.get("email") or "").strip()
    if not host or not username or not password or not from_address or not to_address:
        return "FAILED", None, "Falta configurar el servidor SMTP, las credenciales o el correo del destinatario."

    port = int(os.getenv("SMTP_PORT", "587"))
    use_tls = env_bool("SMTP_USE_TLS", True)
    from_name = os.getenv("EMAIL_FROM_NAME", "HEMOCAX - Banco de Sangre HRDC").strip()
    msg_type = str(payload.get("type", ""))
    subject = TYPE_TO_SUBJECT.get(msg_type, "Mensaje del Banco de Sangre HRDC")

    email_message = EmailMessage()
    email_message["Subject"] = subject
    email_message["From"] = f"{from_name} <{from_address}>" if from_name else from_address
    email_message["To"] = to_address
    email_message.set_content(str(payload.get("message", "")))

    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=20) as server:
                server.login(username, password)
                server.send_message(email_message)
        else:
            with smtplib.SMTP(host, port, timeout=20) as server:
                if use_tls:
                    server.starttls(context=ssl.create_default_context())
                server.login(username, password)
                server.send_message(email_message)
        return "SENT", None, None
    except (smtplib.SMTPException, OSError) as exc:
        return "FAILED", None, str(exc)[:1000]


class Handler(BaseHTTPRequestHandler):
    server_version = "HEMOCAXAutomation/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        LOG.info("%s - %s", self.address_string(), fmt % args)

    def respond(self, status: int, value: dict) -> None:
        content = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:
        if self.path == "/health":
            return self.respond(200, {"ok": True, "enabled": env_bool("AUTOMATIONS_ENABLED"), "dry_run": env_bool("AUTOMATION_DRY_RUN", True)})
        self.respond(404, {"error": "No encontrado"})

    def do_POST(self) -> None:
        if self.path != "/email":
            return self.respond(404, {"error": "No encontrado"})
        secret = os.getenv("AUTOMATION_WEBHOOK_SECRET", "")
        if not secret or self.headers.get("x-hemocax-webhook-secret", "") != secret:
            return self.respond(401, {"error": "Webhook no autorizado"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 32_000:
                return self.respond(413, {"error": "Tamaño de solicitud no permitido"})
            payload = json.loads(self.rfile.read(size))
            communication_id = int(payload["communication_id"])
            if not payload.get("email") or not payload.get("type"):
                raise ValueError("Faltan datos de comunicación")
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            return self.respond(400, {"error": str(exc)})

        status, external_id, error = send_email(payload)
        callback(communication_id, status, external_id, error)
        code = 200 if status != "FAILED" else 502
        self.respond(code, {"communication_id": communication_id, "status": status, "error": error})


def run_automation(msg_type: str, dry_run: bool) -> dict:
    base = os.getenv("HEMOCAX_API_URL", "http://localhost:3000").rstrip("/")
    secret = os.getenv("AUTOMATION_RUN_SECRET", "")
    if not secret:
        raise RuntimeError("Configura AUTOMATION_RUN_SECRET para autorizar las tareas programadas.")
    status, result = json_request(
        f"{base}/api/automations/run",
        {"type": msg_type, "dry_run": dry_run},
        {"x-hemocax-automation-secret": secret},
    )
    if status < 200 or status >= 300:
        raise RuntimeError(f"HEMOCAX respondió HTTP {status}")
    LOG.info("Automatización %s: %s candidatos; simulación=%s", msg_type, result.get("eligible", result.get("count", 0)), dry_run)
    return result


def scheduler() -> None:
    timezone_name = os.getenv("AUTOMATION_TIMEZONE", "America/Lima")
    try:
        local_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        if timezone_name != "America/Lima":
            raise RuntimeError(f"Zona horaria no disponible: {timezone_name}") from exc
        # Perú mantiene UTC-5 durante todo el año; keep a dependency-free local fallback.
        local_timezone = dt_timezone(timedelta(hours=-5), name="America/Lima")
    completed: set[tuple[str, str]] = set()
    LOG.info("Planificador activo (hora=%s, enabled=%s, dry_run=%s)", timezone_name, env_bool("AUTOMATIONS_ENABLED"), env_bool("AUTOMATION_DRY_RUN", True))
    while True:
        now = datetime.now(local_timezone)
        day = now.date().isoformat()
        if env_bool("AUTOMATIONS_ENABLED"):
            for msg_type, scheduled in SCHEDULE.items():
                key = (day, msg_type)
                if now.strftime("%H:%M") == scheduled and key not in completed:
                    try:
                        run_automation(msg_type, env_bool("AUTOMATION_DRY_RUN", True))
                        completed.add(key)
                    except Exception:
                        LOG.exception("Falló la tarea %s; se volverá a intentar en el próximo minuto", msg_type)
        else:
            LOG.debug("Automatizaciones deshabilitadas; no se ejecutan ni envían mensajes.")
        completed = {entry for entry in completed if entry[0] == day}
        time.sleep(max(1, 60 - datetime.now(local_timezone).second))


def main() -> None:
    load_local_env()
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(), format="%(asctime)s %(levelname)s %(message)s")
    if len(sys.argv) == 3 and sys.argv[1] == "--once":
        msg_type = sys.argv[2].upper()
        if msg_type not in SCHEDULE:
            raise SystemExit(f"Tipo inválido. Opciones: {', '.join(SCHEDULE)}")
        result = run_automation(msg_type, env_bool("AUTOMATION_DRY_RUN", True))
        print(json.dumps({"type": msg_type, "result": result}, ensure_ascii=False, indent=2))
        return
    host = os.getenv("AUTOMATION_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("AUTOMATION_PORT", "8787")))
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    from threading import Thread

    Thread(target=server.serve_forever, name="email-webhook", daemon=True).start()
    scheduler()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LOG.info("Servicio detenido")
