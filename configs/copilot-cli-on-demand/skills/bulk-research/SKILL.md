---
name: bulk-research
description: Use when a task needs bulk tool I/O — big files, logs, many files, long command output, web pages, or API dumps — so only the derived answer enters context. Skip for small reads.
---

# Bulk research with context-mode

Use the context-mode MCP tools to run the analysis in a sandbox. Only the answer enters the context window.

## When to use

Use this skill when the raw data would likely be more than about 20 KB (about 5k tokens):

- Files over about 500 lines, log files, JSON or CSV dumps, lock files, build output.
- Repo-wide questions: counts, inventories, "which files use X", size rankings.
- Web pages, docs, or API responses that you need facts from.
- Gathering that would otherwise take several shell or read calls.

Do not use it for small reads, files you are about to edit, or one short command. Direct tools cost less there.

## How

1. Load the `context-mode` skill for the full tool rules and tool selection order.
2. Gather in one call: `ctx_batch_execute(commands, queries)`.
3. Analyze with code: `ctx_execute(language, code)` or `ctx_execute_file(path, language, code)`. Print only the result.
4. Web: `ctx_fetch_and_index(url, source)`, then `ctx_search(queries)`.
5. Follow-up questions: `ctx_search(queries: [...])` against the indexed content.

Before you edit a file, read the exact region with the normal read tool.

## Measure

Run `python <this skill dir>/scripts/ctx_report.py [days]`. It prints skill loads, ctx tool calls, and bytes kept out of context for GitHub Copilot CLI and Hermes.
