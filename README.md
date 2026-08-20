# hexcrow v2

Modern admin panel hunter — a full rewrite of the classic Breacher tool with
colorful output, threading, smart false-positive filtering, and an interactive
mode.

> **Warning** — For authorized security testing only. You are responsible for
> the targets you scan.

## Features

- 30+ threads with `ThreadPoolExecutor`
- Colorful live progress bar (progress %, found, panels, req/s)
- Admin panel detection with scoring + hard indicators
  (password fields, login forms, http-auth, CMS fingerprints)
- Smart false-positive filtering:
  - 404 baseline calibration (status + size + body hash)
  - Catch-all / WAF "Access Denied" detection (auto-learns repeated signatures)
  - Same-size 409/406/468 denial noise filtered automatically
- Random rotating User-Agents per request (16 real browser UAs) to avoid WAF blocks
- Recursive scanning of found directories (with depth limit)
- robots.txt check
- Interactive mode when no target is given
- Auto wordlist upgrade: if your local list is small (< 5000 paths), hexcrow
  offers to download the dirsearch dictionary (9,681 paths) and save it as
  `dicc.txt` in the current directory — if it already exists it reuses it
  without downloading again
- `%EXT%` placeholder handling in wordlists (skipped by default,
  expandable with `--expand-ext`)
- Full-color banner, status badges, summary box, PANELS FOUND section

## Requirements

- Python 3.7+
- `requests` (auto-installed on first run if missing)

## Usage

### Basic

```bash
python breacher.py -u https://example.com
```

### Interactive mode

Just run it without arguments:

```bash
python breacher.py
```

It will ask for:

```
target url [e.g. https://example.com]:
threads [30]:
timeout (seconds) [10]:
recursive scan [y/N]:
wordlist [1]:            <- numbered list of *.txt files in the current dir
```

### Wordlist

The default wordlist is `paths.txt` in the current directory.

If the local wordlist has fewer than 5,000 paths, hexcrow will ask you whether
to download the bigger online dictionary:

```
[*] local wordlist only has 1925 paths (minimum 5000 recommended)
[?] found dicc.txt in current directory (9123 paths), use it? [y/N]:
```

- `y` — use the saved `dicc.txt`
- if `dicc.txt` doesn't exist it will ask to download and save it there
- `--update-wordlist` — force a fresh download (overwrites `dicc.txt`)
- `--no-update` — never ask / never download

## Options

| Flag | Description |
|---|---|
| `-u, --url URL` | target url, e.g. `https://example.com` |
| `-w, --wordlist FILE` | wordlist file (default `paths.txt`) |
| `-t, --threads N` | number of threads (default 30) |
| `-p, --prefix PATH` | path prefix added after the domain |
| `--timeout SEC` | request timeout in seconds (default 10) |
| `--retries N` | retries on failure (default 2) |
| `-r, --recursive` | recursively scan found directories |
| `--depth N` | recursion depth (default 2) |
| `--type TYPE` | only test paths of this type: `php`, `asp`, `html`, ... |
| `-o, --output FILE` | save results to a file |
| `--show CODES` | only show these status codes, e.g. `200,301,403` |
| `-H, --header H` | extra header, e.g. `-H "Cookie: x=1"` (repeatable) |
| `-A, --user-agent UA` | custom user agent |
| `-x, --proxy URL` | proxy, e.g. `http://127.0.0.1:8080` |
| `--no-follow` | do not follow redirects |
| `--no-robots` | skip the robots.txt check |
| `--update-wordlist` | force download the online wordlist |
| `--no-update` | never auto-upgrade the wordlist online |
| `--expand-ext` | expand `%EXT%` entries into real extensions |
| `-v, --verbose` | verbose output |

## Examples

```bash
# quick scan
python breacher.py -u https://example.com

# aggressive scan with recursion and more threads
python breacher.py -u https://example.com -t 50 -r --depth 3

# scan with a custom wordlist and only show interesting statuses
python breacher.py -u https://example.com -w dicc.txt --show 200,301,403

# bypass a geo-blocked site through a proxy
python breacher.py -u https://example.com -x http://127.0.0.1:8080

# scan only PHP paths
python breacher.py -u https://example.com --type php -r

# save results to a file
python breacher.py -u https://example.com -o results.txt
```

## Output

Every response is printed during the scan:

- `ADMIN PANEL` badge — high-confidence admin panel (password field, login
  form, or CMS fingerprint)
- `POSSIBLE PANEL` badge — strong hint but not confirmed
- `[+]` / `[!]` — real findings (200s, redirects, auth pages, ...)
- `[~]` dimmed — filtered noise (404 baseline / WAF "Access Denied"), shown
  for transparency

At the end a summary box shows:

```
╔════════════════════════════════════════════════════════════════════╗
║                       SCAN COMPLETE                                ║
╠════════════════════════════════════════════════════════════════════╣
║  time:      35.0s                                                  ║
║  requests:  1925  at 55.1 req/s                                    ║
║  found:     4                                                      ║
║  panels:    0                                                      ║
║  filtered:  1836  (WAF/404 noise)                                  ║
║  errors:    85                                                     ║
╚════════════════════════════════════════════════════════════════════╝
```

plus a `PANELS FOUND` section listing confirmed admin panels.

## Troubleshooting

- **Site returns "Access Denied" on everything** — the WAF/anti-bot is
  blocking your IP/region. hexcrow will warn you. Try a VPN, a proxy
  (`-x`), or a different network. Random browser User-Agents are already
  rotated automatically.
- **`%EXT%` paths in the wordlist** — these are dirsearch placeholders and
  are skipped by default; use `--expand-ext` to expand them into real
  extensions (`php`, `asp`, `aspx`, `jsp`, `html`, `htm`, `cgi`, `pl`).
- **Only a few results** — check the `filtered` counter in the summary;
  most responses were identical WAF noise and were auto-filtered. Use
  `--show` to focus on specific statuses.