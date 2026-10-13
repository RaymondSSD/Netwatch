#!/usr/bin/env python3
"""Ping a list of network devices and record whether each one is UP or DOWN.
Edit DEVICES below, then run one check with ``python netwatch.py``.
Run ``python netwatch.py --watch 60`` to repeat every 60 seconds until Ctrl+C.
Results are printed and appended to netwatch.log beside this file. The project
practices device checks, logging, error handling, and repeatable lab support.
"""
import argparse
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
# Replace the starter or add quoted addresses that are correct for YOUR network:
# "192.168.1.1" (router), "gaming-pc.local" (PC), "192.168.1.50" (phone).
# Note: some phones ignore ping while sleeping even though they are connected.
DEVICES = [
    "127.0.0.1",  # Safe starter: this computer's loopback address
]
# __file__ means the log stays beside this script, regardless of where it runs.
LOG_FILE = Path(__file__).with_name("netwatch.log")


def ping_command(host):
    system = platform.system()
    if system == "Windows":
        # -n is packet count; -w is timeout in milliseconds.
        return ["ping", "-n", "1", "-w", "1000", host]
    if system == "Darwin":
        # macOS: -c is count; -W is timeout in milliseconds.
        return ["ping", "-c", "1", "-W", "1000", host]
    # Linux: -c is count; -W is timeout in seconds.
    return ["ping", "-c", "1", "-W", "1", host]


def check_device(host):
    try:
        result = subprocess.run(
            ping_command(host),
            stdout=subprocess.DEVNULL,  # Hide ping's detailed output.
            stderr=subprocess.DEVNULL,
            timeout=3,                  # Extra protection against a hung command.
            check=False,                # We inspect the return code ourselves.
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired) as error:
        # One missing/unreachable device should never stop the remaining checks.
        print(f"  Note for {host}: {error}")
        return False
    except Exception as error:
        # Final safety net for an unexpected problem with this device only.
        print(f"  Unexpected error for {host}: {error}")
        return False


def run_check():
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    results = []
    print(f"\nNetwork check — {timestamp}\n" + "-" * 50)
    for host in DEVICES:
        is_up = check_device(host)  # Every device gets an independent check.
        status = "UP" if is_up else "DOWN"
        results.append(is_up)
        print(f"{host:<30} {status}")
        # Opening with "a" appends, so earlier runs are never overwritten.
        with LOG_FILE.open("a", encoding="utf-8") as log:
            log.write(f"{timestamp} | {host} | {status}\n")
    up_count = sum(results)  # True counts as 1; False counts as 0.
    down_count = len(results) - up_count
    print("-" * 50)
    print(f"Total: {len(results)} | UP: {up_count} | DOWN: {down_count}")
    return 0 if down_count == 0 else 1  # 0 means success; 1 signals a problem.


def parse_args():
    parser = argparse.ArgumentParser(description="Ping and log network devices.")
    parser.add_argument("--watch", type=float, metavar="SECONDS",
                        help="repeat at this interval until Ctrl+C")
    args = parser.parse_args()
    if args.watch is not None and args.watch <= 0:
        parser.error("--watch must be greater than 0 seconds")
    return args


def main():
    args = parse_args()
    exit_code = run_check()
    if args.watch is None:
        return exit_code
    try:
        while True:
            time.sleep(args.watch)
            exit_code = run_check()
    except KeyboardInterrupt:
        print("\nStopped cleanly. Results are saved in netwatch.log.")
        return exit_code

if __name__ == "__main__":
    sys.exit(main())
