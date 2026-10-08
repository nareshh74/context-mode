"""Report bulk-research skill usage and context-mode savings for Copilot CLI and Hermes."""
import glob
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta

HOME = os.path.expanduser("~")
SKILL = "bulk-research"
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 7
SINCE = datetime.now() - timedelta(days=DAYS)


def copilot():
    sessions = loads = calls = 0
    for f in glob.glob(os.path.join(HOME, ".copilot", "session-state", "*", "events.jsonl")):
        if datetime.fromtimestamp(os.path.getmtime(f)) < SINCE:
            continue
        s_loads = s_calls = 0
        with open(f, encoding="utf8", errors="replace") as fh:
            for line in fh:
                if '"tool.execution_start"' not in line:
                    continue
                d = json.loads(line).get("data", {})
                name = d.get("toolName", "")
                if name == "skill" and (d.get("arguments") or {}).get("skill") == SKILL:
                    s_loads += 1
                elif name.startswith("context-mode-ctx_"):
                    s_calls += 1
        sessions += bool(s_loads or s_calls)
        loads += s_loads
        calls += s_calls
    return sessions, loads, calls


def hermes():
    sessions = set()
    loads = calls = 0
    root = os.path.join(os.environ.get("LOCALAPPDATA", HOME), "hermes")
    for db in [os.path.join(root, "state.db")] + glob.glob(os.path.join(root, "profiles", "*", "state.db")):
        if not os.path.exists(db):
            continue
        c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        since = SINCE.timestamp()
        for sid, tool_calls, tool_name in c.execute(
            "select session_id, tool_calls, tool_name from messages where timestamp >= ? and "
            "(tool_name like 'mcp__context_mode__%' or tool_calls like ?)",
            (since, f"%{SKILL}%"),
        ):
            if tool_name and tool_name.startswith("mcp__context_mode__"):
                calls += 1
                sessions.add(sid)
                continue
            for tc in json.loads(tool_calls or "[]"):
                fn = tc.get("function", {})
                if fn.get("name") == "skill_view" and json.loads(fn.get("arguments") or "{}").get("name") == SKILL:
                    loads += 1
                    sessions.add(sid)
    return len(sessions), loads, calls


def savings(stats_dir):
    out = {"calls": 0, "returned": 0, "kept_out": 0, "tokens_saved": 0}
    for f in glob.glob(os.path.join(stats_dir, "stats-*.json")):
        if datetime.fromtimestamp(os.path.getmtime(f)) < SINCE:
            continue
        d = json.load(open(f))
        out["calls"] += d.get("total_calls", 0)
        out["returned"] += d.get("bytes_returned", 0)
        out["kept_out"] += d.get("kept_out", 0)
        out["tokens_saved"] += d.get("tokens_saved", 0)
    return out


def main():
    print(f"Last {DAYS} days")
    for host, usage, stats_dir in [
        ("copilot", copilot(), os.path.join(HOME, ".copilot", "context-mode", "sessions")),
        ("hermes", hermes(), os.path.join(HOME, ".hermes-context-mode", "sessions")),
    ]:
        s = savings(stats_dir)
        print(
            f"{host:8} sessions_using={usage[0]} skill_loads={usage[1]} ctx_calls={usage[2]} | "
            f"server_calls={s['calls']} bytes_returned={s['returned']} bytes_kept_out={s['kept_out']} "
            f"tokens_saved~{s['tokens_saved']}"
        )


if __name__ == "__main__":
    main()
