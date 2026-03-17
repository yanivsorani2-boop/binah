#!/usr/bin/env python3
"""
scheduler.py — בינה Daily Scheduler
Runs every day. Generates one article per category (7 categories = 7 articles/day).

Setup (macOS, run once):
  python3 scheduler.py --setup-cron

Commands:
  python3 scheduler.py --run      # Normal daily run (skips categories done today)
  python3 scheduler.py --force    # Force all categories regardless
  python3 scheduler.py --status   # Show today's progress
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime, date
from pathlib import Path

BASE_DIR = Path(__file__).parent
LOG_FILE = BASE_DIR / "scheduler.log"


def log(msg):
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_generator(extra_args=None):
    python = sys.executable
    script = BASE_DIR / "generate_article.py"
    env    = os.environ.copy()

    if not env.get("ANTHROPIC_API_KEY"):
        log("ERROR: ANTHROPIC_API_KEY not set.")
        return False

    cmd = [python, str(script), "--all-categories"]
    if extra_args:
        cmd += extra_args

    log("Starting daily generation (one article per category)...")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(BASE_DIR))

    for line in result.stdout.strip().splitlines():
        log(f"  {line}")
    if result.returncode != 0:
        log(f"ERROR: Generator failed (exit {result.returncode})")
        if result.stderr:
            log(f"  {result.stderr[:400]}")
        return False

    log("✅ Daily generation complete.")
    return True


def show_status():
    python = sys.executable
    script = BASE_DIR / "generate_article.py"
    result = subprocess.run([python, str(script), "--status"],
                            capture_output=True, text=True, cwd=str(BASE_DIR))
    print(result.stdout)


def setup_cron():
    plist_path  = Path.home() / "Library/LaunchAgents/com.binah.scheduler.plist"
    python_path = sys.executable
    script_path = str(BASE_DIR / "scheduler.py")
    log_path    = str(LOG_FILE)

    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.binah.scheduler</string>

    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
        <string>--run</string>
    </array>

    <key>EnvironmentVariables</key>
    <dict>
        <key>ANTHROPIC_API_KEY</key>
        <string>REPLACE_WITH_YOUR_API_KEY</string>
    </dict>

    <!-- Run every day at 08:00 -->
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>8</integer>
        <key>Minute</key><integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>{log_path}</string>
    <key>StandardErrorPath</key>
    <string>{log_path}</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
"""
    plist_path.write_text(plist)
    print(f"✅ LaunchAgent created: {plist_path}")
    print()
    print("⚠️  חשוב: ערוך את הקובץ והחלף REPLACE_WITH_YOUR_API_KEY ב-API key שלך:")
    print(f"   open '{plist_path}'")
    print()
    print("לאחר העריכה, הפעל:")
    print(f"   launchctl load {plist_path}")
    print()
    print("לבדיקה מיידית:")
    print(f"   launchctl start com.binah.scheduler")
    print()
    print("לעצירה:")
    print(f"   launchctl unload {plist_path}")


def main():
    p = argparse.ArgumentParser(description='בינה Daily Scheduler')
    p.add_argument('--run',        action='store_true', help='Daily run — one article per category (skip done today)')
    p.add_argument('--force',      action='store_true', help='Force all categories even if already done today')
    p.add_argument('--status',     action='store_true', help='Show today\'s publishing status')
    p.add_argument('--setup-cron', action='store_true', help='Install macOS LaunchAgent (daily 08:00)')
    args = p.parse_args()

    if args.status:
        show_status(); return

    if args.setup_cron:
        setup_cron(); return

    if args.run:
        log(f"=== Daily run started ({date.today()}) ===")
        success = run_generator()
        if not success:
            sys.exit(1)
        return

    if args.force:
        log(f"=== FORCE run started ({date.today()}) ===")
        success = run_generator(extra_args=["--force-all"])
        if not success:
            sys.exit(1)
        return

    p.print_help()


if __name__ == "__main__":
    main()
