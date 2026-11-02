"""Build the evening card's chat paragraph.

One model call over today's group log. The paragraph is prose only: it never
states task statuses, because those come from Notion through code.
"""

from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

import openclaw_send
import pm_config

MAX_LOG_LINES = 120

PROMPT = """Kamu asisten proyek KIM. Di bawah ini log obrolan grup hari ini.

Tulis 1-3 kalimat bahasa Indonesia yang merangkum hal yang perlu diketahui tim:
keputusan, komitmen, blocker, atau perubahan rencana.

Aturan:
- Jangan menyebut status task, angka, atau tanggal tenggat.
- Abaikan obrolan basa-basi, candaan, dan topik saham yang tidak terkait tugas.
- Tanpa sapaan, tanpa pembuka, tanpa markdown.
- Kalau tidak ada hal penting, balas persis: -

Log obrolan:
{log}
"""


def log_path(today: date, log_dir: Path | None = None) -> Path:
    directory = Path(log_dir or pm_config.CHAT_LOG_DIR)
    return directory / f"group-chat-{today.isoformat()}.md"


def read_log(today: date, log_dir: Path | None = None) -> str | None:
    """Return the tail of today's group log, or None when there is no log."""
    path = log_path(today, log_dir)
    if not path.exists():
        return None
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return "\n".join(lines[-MAX_LOG_LINES:]) or None


def _run_infer(prompt: str) -> str:
    node, entry = openclaw_send.resolve_binary()
    result = subprocess.run(
        [node, entry, "infer", "model", "run", "--prompt", prompt, "--json"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "infer failed")
    payload = json.loads(result.stdout)
    return (payload.get("outputs") or [{}])[0].get("text", "")


def build_note(today: date, log_dir: Path | None = None, run=_run_infer) -> str | None:
    """Return the chat paragraph, or None when there is nothing to say."""
    log = read_log(today, log_dir)
    if not log:
        return None
    try:
        text = run(PROMPT.format(log=log)).strip()
    except Exception:
        return None
    if text in {"", "-", "—"}:
        return None
    return text
