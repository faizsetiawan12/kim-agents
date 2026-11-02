---
name: notion
description: |
  Notion tools for PM-scoped operations on the KIM Tasks & Timeline data source.
  Permitted: read, query, update pages, create new task pages inside the
  canonical data source, and archive (soft-delete) task pages there only with
  Faiz's explicit prior approval. Never hard-delete, never create or touch
  anything outside the canonical scope.
metadata: {"clawdbot":{"emoji":"📝"}}
---

# Notion Skill (PM Scope)

PM reaches Notion through the `notion__*` MCP tools. There is no shell and no
`curl`: every action is one of the tools below. Anything not listed here is out
of scope even if a tool could technically do it.

## Permitted operations and the tool that performs them

| Operation | Tool |
|---|---|
| Read a task page | `notion__API-retrieve-a-page` |
| Read one property | `notion__API-retrieve-a-page-property` |
| Query / filter / sort tasks | `notion__API-query-data-source` |
| Read page content | `notion__API-retrieve-page-markdown` |
| Create a task page | `notion__API-post-page` |
| Update task properties | `notion__API-patch-page` |
| Archive a task page | `notion__API-patch-page` with `archived: true` |
| Search pages | `notion__API-post-search` |

Creating a task is `API-post-page` with `parent.data_source_id` set to the
canonical data source. This grants capability only; `AGENTS.md` policy decides
when a create may happen.

Archiving sets `archived: true` through `API-patch-page`, inside the canonical
data source only, and only after Faiz approves. No approval, no archive.

## Forbidden operations

- Hard-deleting pages, databases, or data sources.
- Archiving without Faiz's explicit prior approval.
- Creating or modifying databases or data sources.
- Creating pages anywhere outside the canonical data source.
- Touching any Notion page or database outside the canonical scope.

## Canonical IDs

- Parent database ID: `c4502758-811f-436f-9bba-81b816e7ef34`
- Data source ID: `8400948e-d63e-4ba3-ba2b-08ae7774f7e0`

## Property shapes

`Status` is a `select`: filter with
`{"property": "Status", "select": {"equals": "In Progress"}}`, and write it as
`{"Status": {"select": {"name": "In Progress"}}}`. Valid values: `Todo`,
`In Progress`, `Blocked`, `Review`, `Done`.

`Owner` is a `multi_select` of `Faiz`, `Oscar`, `Jimmy`, `Wahyu`, `KIM`:
`{"Owner": {"multi_select": [{"name": "Faiz"}]}}`.
`Timeline` and `Last Update` are `date`: `{"Timeline": {"date": {"start": "2026-11-04"}}}`.
`Name` is `title`; `Project`, `Priority`, and `Type` are `select`; `Repo` and
`Update` are `rich_text`.

## After every write

Read the page back with `notion__API-retrieve-a-page` and confirm the changed
properties before telling anyone it worked. If a write fails, say so plainly.
