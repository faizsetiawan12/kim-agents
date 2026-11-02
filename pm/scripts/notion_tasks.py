"""Read-only Notion access for the PM cards.

The agent writes through its `notion__*` MCP tools; these scripts only read,
so a report can never mutate a task.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pm_config


@dataclass(frozen=True)
class Task:
    name: str
    status: str
    owners: tuple[str, ...]
    timeline: date | None = None
    last_update: date | None = None


def load_api_key(path: Path | None = None) -> str:
    """Read NOTION_API_KEY out of the env file the gateway also uses."""
    path = Path(path or pm_config.NOTION_ENV)
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("NOTION_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"NOTION_API_KEY not found in {path}")


def _text(prop: dict) -> str:
    return "".join(part.get("plain_text", "") for part in prop.get("title") or ())


def _select(prop: dict) -> str:
    value = prop.get("select")
    return value.get("name", "") if value else ""


def _multi(prop: dict) -> tuple[str, ...]:
    return tuple(option.get("name", "") for option in prop.get("multi_select") or ())


def _date(prop: dict) -> date | None:
    value = prop.get("date")
    if not value or not value.get("start"):
        return None
    return date.fromisoformat(value["start"][:10])


def parse_task(page: dict) -> Task:
    """Turn one Notion page into a Task. Unknown properties become empty."""
    props = page.get("properties", {})
    return Task(
        name=_text(props.get("Name", {})).strip(),
        status=_select(props.get("Status", {})),
        owners=_multi(props.get("Owner", {})),
        timeline=_date(props.get("Timeline", {})),
        last_update=_date(props.get("Last Update", {})),
    )


def fetch_tasks(api_key: str | None = None, timeout: int = 30) -> list[Task]:
    """Fetch every task page in the canonical data source."""
    key = api_key or load_api_key()
    url = f"https://api.notion.com/v1/data_sources/{pm_config.NOTION_DATA_SOURCE_ID}/query"
    tasks: list[Task] = []
    cursor: str | None = None
    while True:
        body: dict = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {key}",
                "Notion-Version": pm_config.NOTION_API_VERSION,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
        tasks.extend(parse_task(page) for page in payload.get("results", []))
        if not payload.get("has_more"):
            return tasks
        cursor = payload.get("next_cursor")
