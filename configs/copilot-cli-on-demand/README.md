# context-mode — GitHub Copilot CLI plugin (on demand, no hooks)

A variant of `configs/copilot-cli` for users who want the agent to decide when to use context-mode.

It ships:

- **MCP server** (`.mcp.json`): the same `ctx_*` tools as `configs/copilot-cli`. It sets `CONTEXT_MODE_COPILOT_PLUGIN=ondemand`, so `ctx_doctor` reports hooks as intentionally absent.
- **`context-mode` skill**: the tool reference, without the hook-only "MANDATORY" and "BLOCKED" wording.
- **`bulk-research` skill**: tells the agent to use context-mode for bulk tool I/O (big files, logs, repo-wide scans, web pages) and direct tools for small reads. `scripts/ctx_report.py [days]` reports skill loads, ctx calls, and bytes kept out of context for Copilot CLI and Hermes.

It does not ship `hooks.json`. No routing block is injected at session start, and tool calls are not nudged or redirected. Small turns keep their normal cost.

Install one bundle only:

```sh
npm install -g context-mode
copilot plugin uninstall context-mode
copilot plugin install mksglu/context-mode:configs/copilot-cli-on-demand
```

If you ran `context-mode upgrade` for Copilot CLI before, it wrote context-mode entries into `~/.copilot/hooks/`. Remove the entries whose command starts with `context-mode hook copilot-cli`.
