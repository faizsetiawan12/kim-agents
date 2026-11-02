"""18:00 card: Notion + chat log -> code -> WhatsApp.

Only the chat paragraph comes from the model; every task line is code.
A failed model call still sends the card, minus the paragraph.

Usage:
    python3 scripts/report_evening.py            # render and send
    python3 scripts/report_evening.py --dry-run  # render and print only
"""

from __future__ import annotations

import os
import sys
from datetime import datetime

import chat_note
import notion_tasks
import openclaw_send
import pm_config
import report_cards


def main(argv: list[str] | None = None) -> int:
    dry_run = "--dry-run" in (argv if argv is not None else sys.argv[1:])
    dry_run = dry_run or os.environ.get("PM_REPORT_DRY_RUN") == "1"
    today = datetime.now(pm_config.TZ).date()
    tasks = notion_tasks.fetch_tasks()
    note = chat_note.build_note(today)
    card = report_cards.evening_card(tasks, today, note)
    print(card)
    if dry_run:
        return 0
    return 0 if openclaw_send.send(card) else 1


if __name__ == "__main__":
    raise SystemExit(main())
