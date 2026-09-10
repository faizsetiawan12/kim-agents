"""
/home/faiz/KIM/agents/quant/scripts/send_pdf_to_research.py
Send a PDF file to the KIM Research Telegram topic (topic 62).

How it works:
  1. Reads KIM_TELEGRAM_BOT_TOKEN from the environment.
  2. POSTs the PDF as multipart/form-data to the Telegram Bot API (sendDocument).
  3. Targets group -1003987590335, message_thread_id 62 (Research).
  4. Exits 0 on success (prints message_id); exits 1 on error (prints response).

How to run:
  KIM_TELEGRAM_BOT_TOKEN=<token> python send_pdf_to_research.py \\
    --pdf-path /path/to/report.pdf \\
    --caption "Backtest: artifact_name | run_id: 20260528_143000"

Stdlib-only. No pip dependencies.
"""

import argparse
import logging
import os
import sys
import uuid
import urllib.error
import urllib.request
from pathlib import Path

# ── CONFIG ─────────────────────────────────────────────────────────────────────

TELEGRAM_API_BASE = "https://api.telegram.org"
CHAT_ID = "-1003987590335"
MESSAGE_THREAD_ID = "62"
TOKEN_ENV = "KIM_TELEGRAM_BOT_TOKEN"


def _load_dotenv(path: str | Path = ".env") -> None:
    # ponytail: 5-line parser, upgrade to python-dotenv if quoting/multiline needed
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))

# ── LOGGING ────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)

# ── MULTIPART BUILDER ──────────────────────────────────────────────────────────


def _build_multipart(fields: dict, file_path: Path) -> tuple[bytes, str]:
    """Build a multipart/form-data body with a binary file field named 'document'.

    Args:
        fields: Dict of non-file form fields (str → str).
        file_path: Path to the PDF to attach.

    Returns:
        (body_bytes, content_type_header_value)
    """
    boundary = uuid.uuid4().hex
    ctype = f"multipart/form-data; boundary={boundary}"

    parts: list[bytes] = []
    sep = f"--{boundary}\r\n".encode()

    for name, value in fields.items():
        parts.append(sep)
        parts.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        )
        parts.append(f"{value}\r\n".encode())

    # File field
    filename = file_path.name
    parts.append(sep)
    parts.append(
        (
            f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'
            f"Content-Type: application/pdf\r\n\r\n"
        ).encode()
    )
    parts.append(file_path.read_bytes())
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())

    return b"".join(parts), ctype


# ── SEND ───────────────────────────────────────────────────────────────────────


def send_pdf(pdf_path: Path, caption: str, token: str) -> int:
    """Send a PDF to the Research topic.

    Args:
        pdf_path: Path to the PDF file.
        caption: Caption text for the document message.
        token: Telegram bot token.

    Returns:
        Telegram message_id on success.

    Raises:
        SystemExit(1) on HTTP error or request failure.
    """
    url = f"{TELEGRAM_API_BASE}/bot{token}/sendDocument"

    fields = {
        "chat_id": CHAT_ID,
        "message_thread_id": MESSAGE_THREAD_ID,
        "caption": caption,
    }

    log.info("Sending PDF to Research topic 62 | file=%s | caption=%s", pdf_path.name, caption[:80])

    body, content_type = _build_multipart(fields, pdf_path)

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": content_type},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            import json
            response_body = resp.read().decode("utf-8", errors="replace")
            data = json.loads(response_body)
            if data.get("ok"):
                message_id = data["result"]["message_id"]
                log.info("Sent OK | message_id=%s", message_id)
                return message_id
            else:
                log.error("Telegram API returned ok=false | %s", response_body)
                print(response_body, file=sys.stderr)
                sys.exit(1)
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        log.error("HTTP %s | %s", e.code, body_text)
        print(body_text, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        log.error("Request failed | %s", e)
        print(str(e), file=sys.stderr)
        sys.exit(1)


# ── CLI ────────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a PDF to KIM Research topic 62 via Telegram."
    )
    parser.add_argument(
        "--pdf-path",
        required=True,
        help="Absolute path to the PDF file to send.",
    )
    parser.add_argument(
        "--caption",
        default=None,
        help="Caption for the document. Defaults to the PDF filename stem.",
    )
    args = parser.parse_args()
    _load_dotenv()

    token = os.environ.get(TOKEN_ENV)
    assert token, f"{TOKEN_ENV} is not set"  # fail fast, no silent default
    if not token:
        log.error(
            "KIM_TELEGRAM_BOT_TOKEN is not set. "
            "Export the token before running this script."
        )
        sys.exit(1)

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        log.error("PDF file not found: %s", pdf_path)
        sys.exit(1)
    if not pdf_path.is_file():
        log.error("Path is not a file: %s", pdf_path)
        sys.exit(1)

    caption = args.caption if args.caption is not None else pdf_path.stem

    message_id = send_pdf(pdf_path, caption, token)
    print(message_id)
    sys.exit(0)


if __name__ == "__main__":
    main()
