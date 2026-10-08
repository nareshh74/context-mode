# context-mode — GitHub Copilot CLI plugin (on demand, no hooks)

A variant of `configs/copilot-cli` for users who want the agent to decide when to use context-mode.

It ships:

- **MCP server** (`.mcp.json`): the same `ctx_*` tools as `configs/copilot-cli`.
- **`context-mode` skill**: the routing rules, copied from `configs/copilot-cli`.
- **`bulk-research` skill**: tells the agent to use context-mode for bulk tool I/O (big files, logs, repo-wide scans, web pages) and to use direct tools for small reads. `scripts/ctx_report.py` reports skill loads, ctx calls, and bytes kept out of context.

It does not ship `hooks.json`. No routing block is injected at session start, and tool calls are not nudged or redirected. Small turns keep their normal cost.

Install one bundle only. Uninstall `configs/copilot-cli` first:

```sh
npm install -g context-mode
copilot plugin uninstall context-mode
copilot plugin install <owner>/context-mode:configs/copilot-cli-on-demand
```

If an earlier `context-mode upgrade` wrote hooks to `~/.copilot/hooks/`, remove them there as well.
