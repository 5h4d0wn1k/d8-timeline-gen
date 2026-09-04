#!/usr/bin/env python3
"""D8 - Timeline Generator

Multi-source timeline correlation, event sorting, visualization.
Uses json, datetime, os only.
"""

import json
import datetime
import os
import sys


class Timeline:
    def __init__(self):
        self.events = []

    def add_event(self, ts, source, event_type, description="", data=None):
        if isinstance(ts, str):
            try:
                ts = datetime.datetime.fromisoformat(ts)
            except Exception:
                ts = None
        self.events.append({
            "timestamp": ts,
            "source": source,
            "type": event_type,
            "description": description,
            "data": data or {},
        })

    def load_json(self, path):
        with open(path, "r", encoding="utf-8") as f:
            records = json.load(f)
        if not isinstance(records, list):
            records = [records]
        for rec in records:
            self.add_event(
                rec.get("timestamp"),
                rec.get("source", "json"),
                rec.get("type", "unknown"),
                rec.get("description", ""),
                rec.get("data", {}),
            )

    def sort(self):
        self.events.sort(key=lambda e: e["timestamp"] or datetime.datetime.min)

    def filter_source(self, source=None, etype=None):
        out = []
        for e in self.events:
            if source and e["source"] != source:
                continue
            if etype and e["type"] != etype:
                continue
            out.append(e)
        return out

    def by_time_range(self, start, end):
        return [e for e in self.events
                if e["timestamp"] and start <= e["timestamp"] <= end]

    def summarize(self):
        stats = {}
        for e in self.events:
            stats.setdefault(e["source"], set()).add(e["type"])
        return {k: sorted(v) for k, v in stats.items()}

    def timeline_txt(self, width=34):
        """ASCII visualization: time-sorted events across sources."""
        self.sort()
        sources = sorted({e["source"] for e in self.events})
        if not sources:
            return "No events"
        lines = []
        lines.append("Timeline (")
        for s in sources:
            lines[0] += " [%s]" % s
        lines[0] += " )"
        for e in self.events:
            ts = e["timestamp"].isoformat(sep=" ") if e["timestamp"] else "?" * 19
            ctx = ts
            lines.append(ctx + "  " + (e["description"] or e["type"]))
        return "\n".join(lines)

    def render_bars(self):
        """Visual bar chart of events per source over time."""
        self.sort()
        sources = sorted({e["source"] for e in self.events})
        if not sources:
            return "No events"
        lines = []
        lines.append("Event density per source:")
        lines.append("  " + " ".join("%-10s" % s for s in sources))
        lines.append("  " + " ".join("%-10s" % ("-------") for _ in sources))
        lines.append("")
        for e in self.events:
            ts = e["timestamp"].isoformat() if e["timestamp"] else "?"
            parts = []
            for s in sources:
                mark = "x" if e["source"] == s else "."
                parts.append("%-10s" % mark)
            lines.append(ts + "  " + " ".join(parts))
        return "\n".join(lines)

    def csv_out(self):
        lines = ["timestamp,source,type,description"]
        for e in sorted(self.events, key=lambda x: x["timestamp"] or datetime.datetime.min):
            ts = e["timestamp"].isoformat() if e["timestamp"] else ""
            desc = (e["description"] or "").replace(",", ";")
            lines.append("%s,%s,%s,%s" % (ts, e["source"], e["type"], desc))
        return "\n".join(lines)

    def correlated_sessions(self, gap=datetime.timedelta(minutes=10)):
        """Group events into sessions where gaps exceed `gap`."""
        self.sort()
        sessions = []
        current = []
        last = None
        for e in self.events:
            if not e["timestamp"]:
                continue
            if last is None or (e["timestamp"] - last) > gap:
                if current:
                    sessions.append(current)
                current = [e]
            else:
                current.append(e)
            last = e["timestamp"]
        if current:
            sessions.append(current)
        return sessions


SAMPLE = [
    {"timestamp": "2024-01-15T08:00:00", "source": "auth", "type": "login", "description": "User logon"},
    {"timestamp": "2024-01-15T08:02:30", "source": "auth", "type": "login", "description": "Failed password"},
    {"timestamp": "2024-01-15T08:10:00", "source": "network", "type": "conn", "description": "Outbound connect"},
    {"timestamp": "2024-01-15T08:11:00", "source": "file", "type": "create", "description": "New binary written"},
    {"timestamp": "2024-01-15T09:00:00", "source": "network", "type": "conn", "description": "DNS query"},
    {"timestamp": "2024-01-15T23:59:00", "source": "auth", "type": "login", "description": "Late night logon"},
]


def main():
    tl = Timeline()
    if len(sys.argv) > 1:
        for p in sys.argv[1:]:
            if os.path.isfile(p):
                tl.load_json(p)
            else:
                print("Skip missing file: %s" % p)
    else:
        print("No JSON files given; using built-in sample events.\n")
        for rec in SAMPLE:
            tl.add_event(rec["timestamp"], rec["source"], rec["type"], rec["description"])

    tl.sort()

    print("=== D8 - Timeline Generator ===")
    print("Total events: %d" % len(tl.events))

    print("\n-- Source summary --")
    for s, types in tl.summarize().items():
        print("  %-10s %s" % (s, ", ".join(types)))

    print("\n-- Timeline visualization --")
    print(tl.timeline_txt())

    print("\n-- Event density --")
    print(tl.render_bars())

    print("\n-- Correlated sessions --")
    sessions = tl.correlated_sessions()
    print("  Sessions found: %d" % len(sessions))
    for i, sess in enumerate(sessions, 1):
        start = sess[0]["timestamp"].isoformat() if sess[0]["timestamp"] else "?"
        end = sess[-1]["timestamp"].isoformat() if sess[-1]["timestamp"] else "?"
        print("  Session %d: %s -> %s (%d events)" % (i, start, end, len(sess)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
