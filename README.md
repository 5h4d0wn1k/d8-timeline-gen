# D8 — Timeline Generator

Correlates events from multiple sources into a single sorted timeline.

## Overview

This project builds a unified forensic timeline from multiple data sources:
- Loads events from JSON files (or built-in sample)
- Sorts events chronologically
- Correlates events into activity sessions
- Visualizes density and ordering (text/bar chart)
- Exports CSV

## Features

- **Multi-source**: auth, network, file, etc.
- **Sorting**: chronological ordering with ISO-8601 support
- **Correlation**: groups events into sessions by time gaps
- **Visualization**: ASCII timeline + density bars
- **CSV export**: `csv_out()` for further tooling
- **Filtering**: by source, type, and time range

## Usage

```bash
python3 timeline.py                    # built-in sample
python3 timeline.py events.json        # one JSON file
python3 timeline.py a.json b.json      # multiple sources
```

JSON format:

```json
[
  {"timestamp": "2024-01-15T08:00:00", "source": "auth",
   "type": "login", "description": "User logon"}
]
```

## Example Output

```
=== D8 - Timeline Generator ===
Total events: 6

-- Timeline visualization --
Timeline ( [auth] [file] [network] )
2024-01-15 08:00:00  User logon
2024-01-15 08:02:30  Failed password
...
```

## Legal Disclaimer

**IMPORTANT: Read before use.**

This project is provided for **educational and authorized security testing purposes only**. 

### Authorization Requirements
- You MUST have explicit written permission from the network owner before using this tool
- Unauthorized interception of network communications is illegal under federal and state laws
- This tool should ONLY be used on networks you own or have written authorization to test

### Legal Framework
- **Computer Fraud and Abuse Act (CFAA)**: Unauthorized access to computer systems is a federal crime
- **Wiretap Act (18 U.S.C. § 2511)**: Interception of electronic communications without consent is illegal
- **State Laws**: Many states have additional computer crime and wiretapping statutes
- **GDPR/CCPA**: Data collection may be subject to privacy regulations

### Acceptable Use
- Testing security of your own networks
- Authorized penetration testing with written scope
- Academic research in controlled lab environments
- Security education and training

### Prohibited Use
- Intercepting communications on networks you do not own
- Attacking infrastructure without authorization
- Any activity that violates applicable laws or regulations
- Commercial use without proper licensing

### No Warranty
This software is provided "AS IS" without warranty of any kind. The author is not responsible for any misuse or damage caused by this software.

### Responsible Disclosure
If you discover vulnerabilities using this tool, follow responsible disclosure practices:
1. Report to the vendor/owner privately
2. Allow reasonable time for remediation
3. Do not exploit beyond proof of concept

## License

MIT
