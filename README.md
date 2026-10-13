# netwatch

A Python 3 network device monitor. Pings a list of devices, prints UP/DOWN
status, and appends timestamped results to a log file. Supports one-time
checks and continuous watch mode.

## Requirements

- Python 3 (standard library only, no extra installs)

## Usage

Edit the `DEVICES` list at the top of `netwatch.py` with your own devices
(router IP, PC hostname, etc.), then:

```bash
python netwatch.py              # single check of all devices
python netwatch.py --watch 60   # repeat every 60 seconds until Ctrl+C
```

Results are printed to the console and appended to `netwatch.log`.
Exit code is `0` when every device responds, `1` when any device is down.

## How it works

- Uses `subprocess` to ping each device, with the correct flags for
  Windows, macOS, and Linux (detected via `platform.system()`).
- Each device is checked independently inside `try/except`, so one
  unreachable device never stops the remaining checks.
- Every result is timestamped and appended to the log for later review.
