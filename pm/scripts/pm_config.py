"""Wiring constants for the PM report scripts.

Behaviour lives in AGENTS.md; this file only holds the addresses the code needs.
"""

from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Jakarta")

NOTION_DATA_SOURCE_ID = "8400948e-d63e-4ba3-ba2b-08ae7774f7e0"
NOTION_API_VERSION = "2025-09-03"

WHATSAPP_ACCOUNT = "pm"
WHATSAPP_GROUP = "120363430488414303@g.us"

WORKSPACE = Path(__file__).resolve().parent.parent
CHAT_LOG_DIR = WORKSPACE / "memory"

# Owner name -> WhatsApp E.164 tags used in card headers.
OWNERS = {
    "Faiz": ("+628113112054",),
    "Oscar": ("+628111929008",),
    "Jimmy": ("+6285156348470", "+628129253766"),
    "Wahyu": ("+6282132150151",),
}
# "KIM" on a task means the whole team; its header tags every principal.
KIM_TAGS = tuple(tag for tags in OWNERS.values() for tag in tags)
