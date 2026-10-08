---
name: context-mode
description: context-mode tool reference. Load when a task needs bulk tool I/O (large files, logs, repo-wide scans, web pages, API dumps) and you will use the ctx_* tools. Skip for small reads.
---

# context-mode tool reference

The context-mode MCP tools run work in a sandbox. Only what you print enters the context window. Use them when raw data would be large. Use the normal tools for small reads and for files you are about to edit.

## Think in code

To analyze, count, filter, compare, search, parse, or transform large data, write code with `ctx_execute(language, code)` and print only the answer. Do not read the raw data into context. One script replaces many tool calls.

## Prefer these over direct tools for large data

- **curl / wget output**: use `ctx_fetch_and_index(url, source)`, then `ctx_search(queries)`.
- **Inline HTTP** (`node -e "fetch(...)"`, `python -c "requests.get(...)"`): use `ctx_execute(language, code)`. Only stdout enters context.
- **Large files you only need to analyze**: use `ctx_execute_file(path, language, code)`.

## Tool selection

1. **Gather**: `ctx_batch_execute(commands, queries)` runs all commands, indexes the output, and returns search results. One call replaces many.
2. **Process**: `ctx_execute` / `ctx_execute_file`. Only stdout enters context.
3. **Web**: `ctx_fetch_and_index(url, source)`, then `ctx_search(queries)`. Raw HTML never enters context.
4. **Search**: `ctx_search(queries: [...])`, all questions in one call.

Write large artifacts to files. Return the path and a one-line description, not the content.
