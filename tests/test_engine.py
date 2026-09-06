#!/usr/bin/env python3
"""Tests for D8 Timeline Generator."""
import os
import sys
import unittest
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "firmware"))
from timeline import Timeline, parse_ts, to_utc

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


class TestParseTs(unittest.TestCase):
    def test_iso_z(self):
        dt = parse_ts("2024-01-15T08:00:00Z")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.tzinfo, datetime.timezone.utc)

    def test_iso_offset(self):
        dt = parse_ts("2024-01-15T08:00:00+02:00")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.utcoffset().total_seconds(), 7200)

    def test_naive(self):
        dt = parse_ts("2024-01-15 08:00:00")
        self.assertIsNotNone(dt)
        self.assertIsNone(dt.tzinfo)

    def test_invalid(self):
        self.assertIsNone(parse_ts("not a date"))


class TestToUtc(unittest.TestCase):
    def test_naive_assumed_utc(self):
        dt = to_utc(datetime.datetime(2024, 1, 15, 8, 0, 0))
        self.assertEqual(dt.tzinfo, datetime.timezone.utc)

    def test_offset_converted(self):
        aware = datetime.datetime(2024, 1, 15, 8, 0, 0,
                                  tzinfo=datetime.timezone(datetime.timedelta(hours=2)))
        utc = to_utc(aware)
        self.assertEqual(utc.hour, 6)


class TestTimelineLoad(unittest.TestCase):
    def setUp(self):
        self.tl = Timeline()
        for fname in ["auth_events.json", "net_events.json", "file_events.json"]:
            self.tl.load_json(os.path.join(FIXTURE_DIR, fname))

    def test_total_events(self):
        self.assertEqual(len(self.tl.events), 12)

    def test_all_sorted_ascending(self):
        self.tl.sort()
        ts = [e["timestamp"] for e in self.tl.events if e["timestamp"]]
        for a, b in zip(ts, ts[1:]):
            self.assertLessEqual(a, b)

    def test_sources_present(self):
        sources = self.tl.summarize().keys()
        for s in ["auth", "network", "file"]:
            self.assertIn(s, sources)

    def test_wall_clock_normalized_utc(self):
        self.tl.sort()
        for e in self.tl.events:
            if e["timestamp"]:
                self.assertEqual(e["timestamp"].tzinfo, datetime.timezone.utc)

    def test_sessions(self):
        sess = self.tl.correlated_sessions()
        self.assertGreaterEqual(len(sess), 1)

    def test_csv_out(self):
        csv = self.tl.csv_out()
        self.assertTrue(csv.startswith("timestamp,source,type,description"))
        self.assertGreater(csv.count("\n"), 0)

    def test_jsonl_out(self):
        jsonl = self.tl.jsonl_out()
        first = jsonl.split("\n", 1)[0]
        import json
        obj = json.loads(first)
        self.assertIn("timestamp", obj)
        self.assertIn("source", obj)

    def test_filter_source(self):
        auth = self.tl.filter_source(source="auth")
        self.assertTrue(all(e["source"] == "auth" for e in auth))
        self.assertEqual(len(auth), 4)

    def test_time_range(self):
        start = "2024-01-15T08:00:00Z"
        end = "2024-01-15T08:30:00Z"
        rng = self.tl.by_time_range(start, end)
        for e in rng:
            self.assertLessEqual(e["timestamp"], to_utc(parse_ts(end)))
            self.assertGreaterEqual(e["timestamp"], to_utc(parse_ts(start)))
        self.assertTrue(len(rng) >= 1)


class TestCLIHelp(unittest.TestCase):
    def test_help_exits_zero(self):
        import subprocess
        cli = os.path.join(os.path.dirname(__file__), "..", "cli.py")
        r = subprocess.run([sys.executable, cli, "--help"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)


class TestCLIDemo(unittest.TestCase):
    def test_demo_exits_zero(self):
        import subprocess
        cli = os.path.join(os.path.dirname(__file__), "..", "cli.py")
        r = subprocess.run([sys.executable, cli, "--demo"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("Timeline", r.stdout)


if __name__ == "__main__":
    unittest.main()
