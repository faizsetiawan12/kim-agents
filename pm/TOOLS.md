# TOOLS.md

Tool-use norms only. Operating rules are canonical in `AGENTS.md`.

- Notion: use the `notion` skill (curl via Notion API, key at `~/.config/notion/notion.env` (`NOTION_API_KEY=`)) against `Tasks & Timeline` only (scope → AGENTS.md).
- Verify every Notion write before confirming it (→ AGENTS.md "Failure Handling").
- Cron routines run in Asia/Jakarta (cadence → AGENTS.md "Daily Rhythm").
- Never expose secrets or credentials (→ AGENTS.md "Privacy and Safety").
