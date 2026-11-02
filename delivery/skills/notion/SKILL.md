---
name: notion
description: |
  Notion API for PM-scoped operations on the KIM Tasks & Timeline data source.
  Only permitted: read, query, update pages. Never create or delete pages,
  databases, or data sources.
metadata: {"clawdbot":{"emoji":"📝"}}
---

# Notion Skill (PM Scope)

PM uses this skill to interact with the KIM Work Overview → Tasks & Timeline
data source only.

## Permitted Operations

- **Query** the data source (read, filter, sort tasks).
- **Update** task properties: Name, Owner, Status, Project, Timeline, Priority,
  Type, Repo, Update, Last Update.
- **Read** page content via the search endpoint.

## Forbidden Operations

- Creating new pages or databases.
- Deleting pages or databases.
- Creating or modifying data sources.
- Operations on any Notion page or database outside the canonical scope.

## Canonical IDs

- Parent database ID: `c4502758-811f-436f-9bba-81b816e7ef34`
- Data source ID: `8400948e-d63e-4ba3-ba2b-08ae7774f7e0`

## API Basics

All requests need:
```bash
NOTION_KEY=$(cut -d= -f2 ~/.config/notion/notion.env)
curl -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

Use `POST /v1/data_sources/8400948e-d63e-4ba3-ba2b-08ae7774f7e0/query` for
reading and filtering tasks. `Status` is a `select` property: filter with
`{"property": "Status", "select": {"equals": "Doing"}}`, not `"status"`.
Use `PATCH /v1/pages/{page_id}` with the parent
database ID `c4502758-811f-436f-9bba-81b816e7ef34` for updating task properties.

Verify every write succeeded. If a write fails, disclose the failure. Never
claim a successful write unless verified.
