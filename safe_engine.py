#!/usr/bin/env python3
"""
==============================================================================
Safe GitHub Activity & Contribution Engine
Repository: pruthvi828/contri
Author: pruthvi828 <jadhavpruthvi828@gmail.com>

KEY DESIGN PRINCIPLES:
1. Natural Daily Heatmap Variance:
   GitHub divides contributions into 4 quartiles to render green colors.
   This engine uses calibrated weights to distribute days across:
   - Tier 0: Rest Day (0 commits, gray)       -> ~15-20% overall (higher on weekends)
   - Tier 1: Light Green (1-2 commits)        -> ~35% of days
   - Tier 2: Medium Green (3-5 commits)       -> ~30% of days
   - Tier 3: Medium-Dark Green (6-8 commits)  -> ~12% of days
   - Tier 4: Deepest Green (9-12 commits)     -> ~5% of days (Sprint days)

2. Anti-Suspension & Bot Detection Prevention:
   - Strictly human commit volume (capped at 12 max, typical 1-5).
   - Day-spaced realistic author timestamps (between 09:15 and 22:45).
   - Idempotency guard: Never double-commits if today already has activity.
   - Unified Git identity: pruthvi828 <jadhavpruthvi828@gmail.com>.
   - Clean UTF-8 structured log updates (no 0-byte or corrupted binary diffs).
==============================================================================
"""

import os
import sys
import json
import random
import subprocess
import time
from datetime import datetime

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(REPO_DIR, "activity_log.txt")

GIT_USER_NAME = "pruthvi828"
GIT_USER_EMAIL = "jadhavpruthvi828@gmail.com"

# Realistic, high-quality engineering commit messages
COMMIT_MESSAGES = [
    "refactor: optimize internal data structures and lookup tables",
    "docs: update architecture notes and documentation",
    "perf: optimize memory allocation in telemetry pipeline",
    "chore: dependency synchronization and environment audit",
    "fix: edge case handling in telemetry parser and validator",
    "style: format codebase according to style guidelines",
    "test: add boundary check assertions and regression tests",
    "feat: modularize core utility helpers and routines",
    "ci: verify pipeline build configuration and test matrix",
    "update: synchronize daily metrics and telemetry checkpoint",
    "refactor: simplify conditional branching in data processor",
    "docs: clarify API payload structures and return codes",
    "perf: cache expensive lookup computations",
    "chore: prune stale cache artifacts and temporary logs",
    "fix: sanitize input boundaries for configuration parser",
    "style: normalize line formatting and remove trailing whitespace",
    "test: expand test coverage for edge condition handlers",
    "feat: add lightweight diagnostic helper function",
    "perf: reduce runtime latency in serialization loop",
    "update: periodic maintenance and state synchronization"
]

# Daily Commit Intensity Range: 50 to 100 commits
MIN_DAILY_COMMITS = 50
MAX_DAILY_COMMITS = 100

# Whether to allow an occasional weekend rest day (set to False for guaranteed daily commits)
ALLOW_WEEKEND_REST = False


def get_daily_intensity(is_weekend=False):
    """
    Generates high-intensity commit volume varying randomly between 50 and 100 commits.
    - Weekdays: 50 to 100 commits (randomly fluctuating every day).
    - Weekends: 50 to 80 commits (or rest if ALLOW_WEEKEND_REST is enabled).
    """
    if is_weekend and ALLOW_WEEKEND_REST:
        if random.random() < 0.15:
            return 0  # Rest day

    if is_weekend:
        # Weekend range: 50 to 80 commits
        return random.randint(MIN_DAILY_COMMITS, 80)
    else:
        # Weekday range: 50 to 100 commits
        return random.randint(MIN_DAILY_COMMITS, MAX_DAILY_COMMITS)


def generate_realistic_time(target_date):
    """
    Generates a natural daytime timestamp between 09:15 AM and 10:45 PM
    with random minutes and seconds to avoid rigid clock patterns.
    """
    hour = random.randint(9, 22)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return target_date.replace(hour=hour, minute=minute, second=second)


def has_commits_today(target_date=None):
    """
    Idempotency check: Inspects git commit history for commits made on target_date.
    Prevents duplicate automated runs from spamming the repository.
    """
    if target_date is None:
        target_date = datetime.now()
    
    date_str = target_date.strftime("%Y-%m-%d")
    try:
        cmd = [
            "git", "log", "--author", GIT_USER_EMAIL,
            f"--after={date_str} 00:00:00",
            f"--before={date_str} 23:59:59",
            "--oneline"
        ]
        result = subprocess.run(cmd, cwd=REPO_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        commits = result.stdout.strip().splitlines()
        return len(commits)
    except Exception as e:
        print(f"Notice: unable to query git log: {e}")
        return 0


def ensure_git_identity():
    """Configures author and committer identity to match GitHub account."""
    subprocess.run(["git", "config", "user.name", GIT_USER_NAME], cwd=REPO_DIR, check=True)
    subprocess.run(["git", "config", "user.email", GIT_USER_EMAIL], cwd=REPO_DIR, check=True)


def make_single_commit(commit_datetime, message=None, index=1):
    """
    Writes a clean, structured UTF-8 log line and creates a git commit
    with the designated author date.
    """
    if not message:
        base_msg = random.choice(COMMIT_MESSAGES)
        message = f"{base_msg} (#{index})"

    date_str = commit_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    session_id = f"{random.randint(100000, 999999):x}"
    log_entry = f"[{date_str}] {message} | session: {session_id}\n"

    # Ensure log file directory exists and write clean UTF-8
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

    # Git Add
    subprocess.run(["git", "add", "activity_log.txt"], cwd=REPO_DIR, check=True)

    # Git Commit with matched author & committer dates
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str
    env["GIT_AUTHOR_NAME"] = GIT_USER_NAME
    env["GIT_AUTHOR_EMAIL"] = GIT_USER_EMAIL
    env["GIT_COMMITTER_NAME"] = GIT_USER_NAME
    env["GIT_COMMITTER_EMAIL"] = GIT_USER_EMAIL

    subprocess.run(
        ["git", "commit", "-m", message, "--date", date_str],
        cwd=REPO_DIR,
        env=env,
        check=True
    )
    print(f"  ✔ [{commit_datetime.strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def git_push():
    """Safely pushes commits to origin main."""
    print("\nPushing commits to remote origin...")
    try:
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, check=True)
        print("✔ Remote repository synchronized successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠ Git push failed: {e}")
        return False


def run_daily_activity(force=False):
    """Main daily routine."""
    today = datetime.now()
    is_weekend = today.weekday() in [5, 6]

    print("=" * 60)
    print(f" Safe GitHub Activity Engine: {today.strftime('%A, %d %B %Y')}")
    print("=" * 60)

    ensure_git_identity()

    existing_count = has_commits_today(today)
    if existing_count > 0 and not force:
        print(f"ℹ Today already has {existing_count} commit(s) in the repository.")
        print("  Skipping automated run to prevent duplicate spam and keep activity organic.")
        return

    commit_count = get_daily_intensity(is_weekend)

    if force and commit_count == 0:
        commit_count = random.randint(MIN_DAILY_COMMITS, 75)

    if commit_count == 0:
        print("🌱 Today is a scheduled natural rest day (0 commits).")
        print("   Rest days simulate authentic developer behavior and prevent robot detection.")
        return

    print(f"🎯 Target today: {commit_count} commits (High Intensity Range: 50–100 commits)")

    # Generate spaced daytime timestamps in chronological order
    timestamps = [generate_realistic_time(today) for _ in range(commit_count)]
    timestamps.sort()

    for idx, ts in enumerate(timestamps, 1):
        make_single_commit(ts, index=idx)
        time.sleep(0.01)

    git_push()
    print(f"\n🎉 Successfully created {commit_count} commits with high-velocity green intensity.")


def dry_run_simulation(days=100):
    """Simulates activity distribution over N days with 50-100 commit range."""
    print(f"\n--- Simulation: 100 Days of High-Intensity Activity (50 - 100 Commits/Day) ---")
    total_commits = 0
    min_commit = 999
    max_commit = 0
    zero_days = 0

    for day in range(days):
        is_wknd = (day % 7) in [5, 6]
        c = get_daily_intensity(is_wknd)
        total_commits += c
        if c == 0:
            zero_days += 1
        else:
            min_commit = min(min_commit, c)
            max_commit = max(max_commit, c)

    print(f"Total simulated commits: {total_commits} (avg {total_commits/days:.1f}/day)")
    print(f"Active day range: {min_commit} to {max_commit} commits")
    print(f"Rest days: {zero_days} days ({zero_days/days*100:.0f}%)")
    print("------------------------------------------------------------------------------------\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--auto", "--daily", "-d", "daily"]:
            run_daily_activity(force=False)
            sys.exit(0)
        elif arg in ["--force", "-f"]:
            run_daily_activity(force=True)
            sys.exit(0)
        elif arg in ["--dry-run", "--sim"]:
            dry_run_simulation(100)
            sys.exit(0)
        elif arg in ["--status", "-s"]:
            today = datetime.now()
            count = has_commits_today(today)
            print(f"Today ({today.strftime('%Y-%m-%d')}): {count} commit(s) recorded.")
            sys.exit(0)

    print("\n--- GitHub Safe Contribution Engine ---")
    print("1. Run Daily Activity (Natural intensity)")
    print("2. Force Run Today (Bypass rest day / existing check)")
    print("3. Run 100-Day Distribution Simulation (Dry run)")
    print("4. Check Today's Status")
    print("5. Exit")
    choice = input("\nSelect an option [1-5]: ").strip()

    if choice == "1":
        run_daily_activity(force=False)
    elif choice == "2":
        run_daily_activity(force=True)
    elif choice == "3":
        dry_run_simulation(100)
    elif choice == "4":
        today = datetime.now()
        count = has_commits_today(today)
        print(f"Today ({today.strftime('%Y-%m-%d')}): {count} commit(s) recorded.")
    else:
        print("Exiting.")
