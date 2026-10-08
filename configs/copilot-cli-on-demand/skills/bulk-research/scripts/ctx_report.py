"""Report bulk-research skill usage and context-mode savings for Copilot CLI and Hermes.

Usage: python ctx_report.py [days]

Reads tool names, counts and stats only. No prompt or tool content is printed.
"""
import contextlib
import glob
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

HOME = os.path.expanduser("~")
SKILL = "bulk-research"
COPILOT_HOME = os.environ.get("COPILOT_HOME") or os.path.join(HOME, ".copilot")
HERMES_ROOT = os.environ.get("HERMES_HOME") or (
    os.path.join(os.environ["LOCALAPPDATA"], "hermes") if os.environ.get("LOCALAPPDATA") else os.path.join(HOME, ".hermes")
)
COPILOT_STATS = os.path.join(os.environ.get("CONTEXT_MODE_DATA_DIR") or os.path.join(COPILOT_HOME, "context-mode"), "sessions")
# Hermes context-mode servers run with CONTEXT_MODE_DIR=~/.hermes-context-mode (see README).
HERMES_STATS = os.path.join(os.environ.get("HERMES_CONTEXT_MODE_DIR") or os.path.join(HOME, ".hermes-context-mode"), "sessions")


def _dict(v):
    return v if isinstance(v, dict) else {}


def copilot(since):
    sessions = loads = calls = 0
    for f in glob.glob(os.path.join(COPILOT_HOME, "session-state", "*", "events.jsonl")):
        if os.path.getmtime(f) < since.timestamp():
            continue
        s_loads = s_calls = 0
        with open(f, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"tool.execution_start"' not in line:
                    continue
                try:
                    e = json.loads(line)
                    if datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")) < since:
                        continue
                except (ValueError, KeyError, TypeError, AttributeError):
                    continue
                d = _dict(e.get("data"))
                name = d.get("toolName") or ""
                if name == "skill" and _dict(d.get("arguments")).get("skill") == SKILL:
                    s_loads += 1
                elif name.startswith("context-mode-ctx_"):
                    s_calls += 1
        sessions += bool(s_loads or s_calls)
        loads += s_loads
        calls += s_calls
    return sessions, loads, calls


def hermes(since):
    sessions = set()
    loads = calls = 0
    for db in [os.path.join(HERMES_ROOT, "state.db")] + glob.glob(os.path.join(HERMES_ROOT, "profiles", "*", "state.db")):
        if not os.path.exists(db):
            continue
        try:
            with contextlib.closing(sqlite3.connect(f"file:{db}?mode=ro", uri=True)) as c:
                rows = c.execute(
                    "select session_id, tool_calls, tool_name from messages where timestamp >= ? and "
                    "(tool_name like 'mcp__context_mode__%' or tool_calls like ?)",
                    (since.timestamp(), f"%{SKILL}%"),
                ).fetchall()
        except sqlite3.Error:
            continue
        for sid, tool_calls, tool_name in rows:
            if tool_name and tool_name.startswith("mcp__context_mode__"):
                calls += 1
                sessions.add(sid)
                continue
            try:
                tcs = json.loads(tool_calls or "[]")
            except ValueError:
                continue
            for tc in tcs if isinstance(tcs, list) else []:
                fn = _dict(_dict(tc).get("function"))
                if fn.get("name") != "skill_view":
                    continue
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except (ValueError, TypeError):
                    continue
                if _dict(args).get("name") == SKILL:
                    loads += 1
                    sessions.add(sid)
    return len(sessions), loads, calls


def savings(stats_dir, since):
    out = {"total_calls": 0, "bytes_returned": 0, "kept_out": 0, "tokens_saved": 0}
    for f in glob.glob(os.path.join(stats_dir, "stats-*.json")):
        if os.path.getmtime(f) < since.timestamp():
            continue
        try:
            with open(f, encoding="utf-8") as fh:
                d = _dict(json.load(fh))
            for k in out:
                out[k] += int(d.get(k) or 0)
        except (OSError, ValueError, TypeError):
            continue
    return out


def main(argv):
    try:
        days = int(argv[1]) if len(argv) > 1 else 7
    except ValueError:
        sys.exit(__doc__)
    since = datetime.now(timezone.utc) - timedelta(days=days)
    # ponytail: stats files filter by mtime, so a long-lived server counts whole; per-event stats need server support.
    print(f"Last {days} days")
    for host, usage, stats_dir in [
        ("copilot", copilot(since), COPILOT_STATS),
        ("hermes", hermes(since), HERMES_STATS),
    ]:
        s = savings(stats_dir, since)
        print(
            f"{host:8} sessions_using={usage[0]} skill_loads={usage[1]} ctx_calls={usage[2]} | "
            f"server_calls={s['total_calls']} bytes_returned={s['bytes_returned']} "
            f"bytes_kept_out={s['kept_out']} tokens_saved~{s['tokens_saved']}"
        )


if __name__ == "__main__":
    main(sys.argv)
