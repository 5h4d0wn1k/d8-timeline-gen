> **⚠️ EDUCATIONAL USE ONLY — AUTHORIZED TESTING ONLY.**
> This project exists for education, research, and **defense of systems you own
> or hold explicit written authorization to assess**. Unauthorized use is
> prohibited and may be illegal. Read [ETHICS.md](ETHICS.md) and
> [SCOPE.md](SCOPE.md) before use. Use at your own risk; **AS IS**, no warranty.

# D8 — Timeline Generator

**DFIR super-timelining utility** by **5h4d0wn1k** for **forensic timeline
correlation**: merges auth, network and file-artifact events into one
wall-clock-normalized (UTC) timeline, then renders text, CSV or JSONL output
with source/type filtering and session grouping. Python-only, offline fixtures
for deterministic analysis.

## Why super-timelining

Compromise analysis lives or dies by ordering: scattered logs from SSH auth,
network flows and filesystem artifacts only become evidence when correlated
against a single clock. This utility ingests JSON/JSONL event streams from any
source, normalizes ISO-8601 (with `Z`/offsets) and naive timestamps into aware
UTC, and yields one ascending timeline — exactly the shape investigators need
to spot the "first-in" host, lateral movement and data staging. Sessions
correlate events across time gaps, and `by_time_range` supports focused
querying. All fixtures are synthetic with RFC 5737 documentation IPs and
`example.com` domains; use it only on artifacts you own or are authorized to
analyze — see [ETHICS.md](ETHICS.md) and [SCOPE.md](SCOPE.md).

## Features

- **Multi-source ingestion** — merge events from auth, network, file and
  arbitrary JSON/JSONL artifacts (`parse_ts`, `add_event`).
- **Wall-clock normalization** — every timestamp converted to aware UTC for
  reliable cross-source ordering.
- **Flexible timestamp parsing** — ISO-8601 with `Z`/offsets plus
  `%Y-%m-%d %H:%M:%S`.
- **Timeline output** — text visualization, CSV and JSONL
  (`timeline_txt`, `csv_lines`, `jsonl_lines`).
- **Source/type filtering** and time-range querying (`filter_source`,
  `by_time_range`).
- **Session correlation** — group events into sessions based on configurable
  time gaps (`correlated_sessions`).
- **Offline demo** — built-in `auth`, `net` and `file` fixtures in
  `tests/fixtures/` drive a deterministic demo that writes
  `reports/d8_timeline.csv`.

## Quickstart

```bash
# Run the demo on built-in multi-source fixtures (writes reports/, exit 0)
python3 cli.py --demo

# Merge multiple event files
python3 cli.py --input auth.json net.json file.json

# Export a merged timeline to CSV
python3 cli.py --input auth.json net.json --output reports/timeline.csv

# Run the test suite (17 deterministic offline tests)
python3 -m unittest discover -s tests
```

## CLI

```
python3 cli.py [-h] [--input FILE [FILE ...]] [--output PATH]
               [--format {txt,csv,jsonl}] [--demo]
```

- `--input` (or `-i`) — one or more JSON/JSONL event files. Each record needs
  a `timestamp`; optional `source`, `type`, `description`, `data`.
- `--output` (or `-o`) — output path; format follows the file extension.
- `--format` (or `-f`) — `txt` (default), `csv` or `jsonl`.
- `--demo` — run on the bundled fixtures.

## Project structure

```
cli.py                  # thin entry point into the engine
firmware/timeline.py    # normalization, correlation, sessions, output, CLI
tests/fixtures/         # synthetic auth/net/file event fixtures
tests/                  # unittest coverage (17 tests)
```

## Documentation

- [ETHICS.md](ETHICS.md) — acceptable and prohibited use.
- [SCOPE.md](SCOPE.md) — authorized target scope.
- [SECURITY.md](SECURITY.md) — responsible disclosure.
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution guide.

## Contributing

New event source adapters, output formats and session heuristics are welcome.
Open an issue or PR against the default branch; keep contributions scoped to
blue-team, educational tooling.

## License

MIT — see [LICENSE](LICENSE). Educational, blue-team software for analyzing
artifacts you own or are explicitly permitted to examine.