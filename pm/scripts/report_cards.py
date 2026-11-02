"""Render the two daily PM cards.

Pure functions: tasks and a date in, text out. No network, no clock, no I/O,
so the format is decided by the code and never by the model.
"""

from __future__ import annotations

from datetime import date

import pm_config
from notion_tasks import Task

MONTHS = ("Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des")
NO_OWNER = "Tanpa owner"


def format_date(value: date) -> str:
    return f"{value.day} {MONTHS[value.month - 1]} {value.year}"


def is_overdue(task: Task, today: date) -> bool:
    """Late means a deadline strictly before today on anything not yet Done."""
    return task.status != "Done" and task.timeline is not None and task.timeline < today


def is_open(task: Task, today: date) -> bool:
    return task.status == "In Progress" or is_overdue(task, today)


def _owner_header(owner: str) -> str:
    if owner == NO_OWNER:
        return NO_OWNER
    tags = pm_config.KIM_TAGS if owner == "KIM" else pm_config.OWNERS.get(owner, ())
    return " ".join(f"@{tag}" for tag in tags) or owner


def _groups(tasks: list[Task]) -> list[tuple[str, list[Task]]]:
    """Group by owner, principals first, unknown owners next, unowned last."""
    grouped: dict[str, list[Task]] = {}
    for task in tasks:
        for owner in task.owners or (NO_OWNER,):
            grouped.setdefault(owner, []).append(task)
    order = [owner for owner in pm_config.OWNERS if owner in grouped]
    order += sorted(owner for owner in grouped if owner not in pm_config.OWNERS and owner != NO_OWNER)
    if NO_OWNER in grouped:
        order.append(NO_OWNER)
    return [(owner, grouped[owner]) for owner in order]


def _sort_key(task: Task, today: date) -> tuple:
    return (not is_overdue(task, today), task.timeline or date.max, task.name)


def _task_line(task: Task, today: date) -> str:
    mark = "🔴 " if is_overdue(task, today) else ""
    due = f" (tenggat {format_date(task.timeline)})" if task.timeline else ""
    return f"• {mark}{task.name}{due}"


def _owner_blocks(tasks: list[Task], today: date) -> list[str]:
    lines: list[str] = []
    for owner, items in _groups(tasks):
        lines.append(_owner_header(owner))
        lines.extend(_task_line(task, today) for task in sorted(items, key=lambda t: _sort_key(t, today)))
        lines.append("")
    return lines


def morning_card(tasks: list[Task], today: date) -> str | None:
    """08:00 card. None means send nothing at all."""
    active = [task for task in tasks if is_open(task, today)]
    if not active:
        return None
    lines = [f"📋 *Fokus Hari Ini — {format_date(today)}*", ""]
    lines += _owner_blocks(active, today)
    lines.append("🕐 08:00 WIB · Progress hari ini pukul 18:00")
    return "\n".join(lines)


def evening_card(tasks: list[Task], today: date, note: str | None = None) -> str:
    """18:00 card. Always returned; `note` is the optional chat paragraph."""
    done_today = [task for task in tasks if task.status == "Done" and task.last_update == today]
    active = [task for task in tasks if is_open(task, today)]

    lines = [f"📊 *Progress Hari Ini — {format_date(today)}*", ""]
    if done_today:
        lines.append("Selesai hari ini")
        for task in sorted(done_today, key=lambda t: t.name):
            who = ", ".join(task.owners) if task.owners else NO_OWNER
            lines.append(f"• {task.name} — {who}")
        lines.append("")
    lines += _owner_blocks(active, today)
    if note:
        lines += ["Catatan hari ini", note.strip(), ""]
    lines.append("🕐 18:00 WIB · Fokus berikutnya besok 08:00")
    return "\n".join(lines)
