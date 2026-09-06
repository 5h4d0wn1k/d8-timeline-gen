# D8 — Timeline Generator

Multi-source forensic timeline correlation with wall-clock normalization, CSV/JSONL output, and session grouping.

## IMPORTANT: Read before use.

This tool is for **authorized educational and blue-team analysis only**. Use only on artifacts you own or are permitted to analyze. All fixtures are synthetic with fictional data and RFC 5737 documentation IPs / example.com domains.

## Features

- **Multi-source ingestion**: merge events from auth, network, file, and arbitrary JSON/JSONL artifacts
- **Wall-clock normalization**: all timestamps converted to aware UTC for reliable cross-source ordering
- **Flexible timestamp parsing**: ISO-8601 (incl. `Z` and offsets), `%Y-%m-%d %H:%M:%S`
- **Timeline output**: text visualization, CSV, JSONL
- **Session correlation**: group events into sessions based on time gaps
- **Source/type filtering** and **time-range queries**

## Quick Start

```bash
# Run demo on built-in multi-source fixtures
python3 cli.py --demo

# Merge multiple event files
python3 cli.py --input auth.json net.json file.json

# Export merged timeline to CSV
python3 cli.py --input auth.json net.json --output reports/timeline.csv
```

## Ingestion

- `--input` accepts one or more JSON/JSONL files
- Each record needs `timestamp`; optional `source`, `type`, `description`, `data`
- Demo merges `auth_events`, `net_events`, `file_events` fixtures

## Testing

```bash
python3 -m unittest discover -s tests
```

## Live Lab Test Plan

1. Run `python3 cli.py --demo` — should exit 0, print merged timeline, write `reports/d8_timeline.csv`
2. Run `python3 -m unittest discover -s tests` — all tests pass
3. Verify the timeline is sorted in ascending UTC order across all three sources

## Metrics

- Output formats: 3 (text, CSV, JSONL)
- Sources handled: 3 fixture sources merged + arbitrary
- Timestamp normalization: ISO-Z, ISO-offset, naive assumed-UTC
- Test count: 17
- Demo exit code: 0

## License

MIT License — see [LICENSE](LICENSE).
