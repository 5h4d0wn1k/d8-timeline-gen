#!/usr/bin/env python3
"""D8 - Timeline Generator

Multi-source timeline correlation, wall-clock normalization, CSV/JSONL output.
Uses json, datetime, os only.
"""

import json
import datetime
import os
import sys


def parse_ts(ts):
    """Normalize a timestamp string to an aware UTC datetime where possible."""
    if isinstance(ts, (datetime.datetime,)):
        return ts
    if isinstance(ts, str):
        ts = ts.strip()
        try:
            return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            pass
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.datetime.strptime(ts, fmt)
            except ValueError:
                continue
    return None


def to_utc(dt):
    """Ensure the timestamp is UTC-aware for reliable cross-source ordering."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


class Timeline:
    def __init__(self):
        self.events = []

    def add_event(self, ts, source, event_type, description="", data=None):
        ts = parse_ts(ts)
        self.events.append({
            "timestamp": to_utc(ts),
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
        self.events.sort(key=lambda e: (e["timestamp"] is not None, e["timestamp"] or datetime.datetime.min))

    def filter_source(self, source=None, etype=None):
        return [e for e in self.events
                if (not source or e["source"] == source)
                and (not etype or e["type"] == etype)]

    def by_time_range(self, start, end):
        start = to_utc(parse_ts(start))
        end = to_utc(parse_ts(end))
        return [e for e in self.events if e["timestamp"] and start <= e["timestamp"] <= end]

    def summarize(self):
        stats = {}
        for e in self.events:
            stats.setdefault(e["source"], set()).add(e["type"])
        return {k: sorted(v) for k, v in stats.items()}

    def timeline_txt(self):
        self.sort()
        lines = ["Timeline (%d events)" % len(self.events)]
        for e in self.events:
            ts = e["timestamp"].isoformat(sep=" ") if e["timestamp"] else "?" * 26
            lines.append(ts + "  [%-10s] %s" % (e["source"], e["description"] or e["type"]))
        return "\n".join(lines)

    def csv_out(self):
        self.sort()
        lines = ["timestamp,source,type,description"]
        for e in self.events:
            ts = e["timestamp"].isoformat() if e["timestamp"] else ""
            desc = (e["description"] or "").replace(",", ";")
            lines.append(",".join([ts, e["source"], e["type"], desc]))
        return "\n".join(lines)

    def jsonl_out(self):
        self.sort()
        out = []
        for e in self.events:
            out.append({
                "timestamp": e["timestamp"].isoformat() if e["timestamp"] else None,
                "source": e["source"],
                "type": e["type"],
                "description": e["description"],
                "data": e["data"],
            })
        return "\n".join(json.dumps(o) for o in out)

    def correlated_sessions(self, gap=datetime.timedelta(minutes=10)):
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


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="D8 - Timeline Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input", "-i", nargs="+", help="JSON/JSONL input event files")
    parser.add_argument("--output", "-o", help="Output path (CSV or JSONL based on extension)")
    parser.add_argument("--format", "-f", choices=["txt", "csv", "jsonl"], default="txt",
                        help="Console output format")
    parser.add_argument("--demo", action="store_true", help="Run on built-in fixtures")
    args = parser.parse_args()

    if args.demo:
        base = os.path.dirname(os.path.abspath(sys.argv[0]))
        if os.path.basename(base) == "firmware":
            base = os.path.dirname(base)
        fixture_dir = os.path.join(base, "tests", "fixtures")
        tl = Timeline()
        for fname in sorted(os.listdir(fixture_dir)):
            if fname.endswith(".json"):
                tl.load_json(os.path.join(fixture_dir, fname))
        out_dir = os.path.join(base, "reports")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "d8_timeline.csv")
        with open(out_path, "w") as f:
            f.write(tl.csv_out() + "\n")
        tl.sort()
        print("=== D8 - Timeline Generator (Demo) ===")
        print("Total events: %d" % len(tl.events))
        print("Sources: %s" % ", ".join(sorted(tl.summarize().keys())))
        print("Sessions: %d" % len(tl.correlated_sessions()))
        print("\n-- Timeline --")
        print(tl.timeline_txt())
        print("\nCSV written to %s" % out_path)
        sys.exit(0)

    tl = Timeline()
    if args.input:
        for p in args.input:
            if os.path.isfile(p):
                tl.load_json(p)
            else:
                print("Skip missing file: %s" % p)
    else:
        parser.print_help()
        sys.exit(1)

    tl.sort()

    if args.output:
        out_dir = os.path.dirname(args.output) or "."
        os.makedirs(out_dir, exist_ok=True)
        if args.output.endswith(".csv"):
            with open(args.output, "w") as f:
                f.write(tl.csv_out() + "\n")
        elif args.output.endswith(".jsonl"):
            with open(args.output, "w") as f:
                f.write(tl.jsonl_out() + "\n")
        print("Output written to %s" % args.output)

    if args.format == "csv":
        print(tl.csv_out())
    elif args.format == "jsonl":
        print(tl.jsonl_out())
    else:
        print("=== D8 - Timeline Generator ===")
        print("Total events: %d" % len(tl.events))
        print("\n-- Timeline --")
        print(tl.timeline_txt())
        print("\n-- Correlated sessions --")
        for i, sess in enumerate(tl.correlated_sessions(), 1):
            start = sess[0]["timestamp"].isoformat() if sess[0]["timestamp"] else "?"
            end = sess[-1]["timestamp"].isoformat() if sess[-1]["timestamp"] else "?"
            print("  Session %d: %s -> %s (%d events)" % (i, start, end, len(sess)))
    sys.exit(0)


if __name__ == "__main__":
    main()
