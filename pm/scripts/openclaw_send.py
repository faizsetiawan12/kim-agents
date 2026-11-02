"""Send a rendered card through OpenClaw's CLI.

The card travels as one string from the renderer to `openclaw message send`;
nothing rewrites it in between.
"""

from __future__ import annotations

import glob
import shutil
import subprocess

import pm_config


def _node() -> str:
    node = shutil.which("node")
    if node:
        return node
    candidates = sorted(glob.glob("/opt/node/*/bin/node"))
    if candidates:
        return candidates[-1]
    raise RuntimeError("node not found")


def _entry() -> str:
    candidates = sorted(glob.glob("/opt/openclaw/*/node_modules/openclaw/dist/index.js"))
    if candidates:
        return candidates[-1]
    raise RuntimeError("openclaw entry point not found")


def resolve_binary() -> tuple[str, str]:
    """Locate node and the OpenClaw CLI entry point for the installed version."""
    return _node(), _entry()


def send(text: str, dry_run: bool = False, timeout: int = 180) -> bool:
    """Deliver `text` to the KIM group. Returns True only when OpenClaw exits 0."""
    node, entry = resolve_binary()
    command = [
        node,
        entry,
        "message",
        "send",
        "--channel",
        "whatsapp",
        "--account",
        pm_config.WHATSAPP_ACCOUNT,
        "--target",
        pm_config.WHATSAPP_GROUP,
        "--message",
        text,
    ]
    if dry_run:
        command.append("--dry-run")
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        print(result.stderr.strip() or result.stdout.strip())
    return result.returncode == 0
