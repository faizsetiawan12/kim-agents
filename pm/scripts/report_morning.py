"""08:00 card: Notion -> code -> WhatsApp. No model in this path.

Usage:
    python3 scripts/report_morning.py            # render and send
    python3 scripts/report_morning.py --dry-run  # render and print only
"""

from __future__ import annotations

import os
import sys
from datetime import datetime

import notion_tasks
import openclaw_send
import pm_config
import report_cards


def main(argv: list[str] | None = None) -> int:
    dry_run = "--dry-run" in (argv if argv is not None else sys.argv[1:])
    dry_run = dry_run or os.environ.get("PM_REPORT_DRY_RUN") == "1"
    today = datetime.now(pm_config.TZ).date()
    card = report_cards.morning_card(notion_tasks.fetch_tasks(), today)
    if card is None:
        print("Fokus Hari Ini: tidak ada task aktif, tidak ada pesan dikirim.")
        return 0
    print(card)
    if dry_run:
        return 0
    return 0 if openclaw_send.send(card) else 1


if __name__ == "__main__":
    raise SystemExit(main())
