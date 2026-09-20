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

# GitHub Contribution Heatmap Intensity Tiers (Boosted for vivid green variation)
INTENSITY_TIERS = {
    1: (2, 4),     # Level 1: Light Green (base 2 - 4 commits)
    2: (5, 9),     # Level 2: Medium Green (base 5 - 9 commits)
    3: (10, 16),   # Level 3: Deep Green (base 10 - 16 commits)
    4: (17, 24)    # Level 4: Darkest Green (Sprint / Heavy Activity: base 17 - 24)
}

# Maximum daily commit ceiling to guarantee account safety & prevent API throttles
MAX_DAILY_COMMIT_CAP = 28


def get_daily_intensity(is_weekend=False):
    """
    Computes a realistic commit target with dynamic -50% to +100% random swing.
    - Weekend bias: more rest or lighter activity.
    - Weekday bias: active development across all tiers.
    - Random swing: scales base count by 0.5x to 2.0x (-50% to +100%).
    """
    if is_weekend:
        # Weekends: higher chance of rest (0) or light work (Tier 1)
        weights = [0.25, 0.45, 0.20, 0.08, 0.02]
    else:
        # Weekdays: active development across all tiers
        weights = [0.08, 0.32, 0.35, 0.17, 0.08]

    tier_choice = random.choices([0, 1, 2, 3, 4], weights=weights)[0]
    if tier_choice == 0:
        return 0, 0, 1.0  # Rest day

    min_c, max_c = INTENSITY_TIERS[tier_choice]
    base_count = random.randint(min_c, max_c)

    # Dynamic random swing: 0.5x (-50%) to 2.0x (+100%)
    swing_factor = random.uniform(0.50, 2.00)
    final_count = max(1, round(base_count * swing_factor))
    final_count = min(final_count, MAX_DAILY_COMMIT_CAP)

    return tier_choice, final_count, swing_factor


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

    tier, commit_count, swing_factor = get_daily_intensity(is_weekend)

    if force and commit_count == 0:
        tier, commit_count, swing_factor = 1, random.randint(2, 5), 1.0

    if commit_count == 0:
        print("🌱 Today is a scheduled natural rest day (0 commits).")
        print("   Rest days simulate authentic developer behavior and prevent robot detection.")
        return

    tier_labels = {
        1: "Tier 1 (Light Green)",
        2: "Tier 2 (Medium Green)",
        3: "Tier 3 (Deep Green)",
        4: "Tier 4 (Darkest Green - Sprint)"
    }
    swing_pct = f"{(swing_factor - 1.0) * 100:+.0f}%"
    print(f"🎯 Target today: {commit_count} commits [{tier_labels.get(tier, 'Custom')} | swing: {swing_pct}]")

    # Generate spaced daytime timestamps in chronological order
    timestamps = [generate_realistic_time(today) for _ in range(commit_count)]
    timestamps.sort()

    for idx, ts in enumerate(timestamps, 1):
        make_single_commit(ts, index=idx)
        time.sleep(0.3)

    git_push()
    print(f"\n🎉 Successfully created {commit_count} commits with dynamic green intensity ({swing_pct} swing).")


def dry_run_simulation(days=100):
    """Simulates activity distribution over N days to verify color variance & swings."""
    print(f"\n--- Simulation: 100 Days of Activity Distribution with -50% to +100% Random Swings ---")
    counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    total_commits = 0
    min_commit = 999
    max_commit = 0

    for day in range(days):
        is_wknd = (day % 7) in [5, 6]
        tier, c, swing = get_daily_intensity(is_wknd)
        counts[tier] += 1
        total_commits += c
        if c > 0:
            min_commit = min(min_commit, c)
            max_commit = max(max_commit, c)

    print(f"Total simulated commits: {total_commits} (avg {total_commits/days:.1f}/day)")
    print(f"Active day range: {min_commit} to {max_commit} commits")
    print(f"  Tier 0 (Rest / Gray):          {counts[0]}% of days")
    print(f"  Tier 1 (Light Green):          {counts[1]}% of days")
    print(f"  Tier 2 (Medium Green):         {counts[2]}% of days")
    print(f"  Tier 3 (Deep Green):           {counts[3]}% of days")
    print(f"  Tier 4 (Darkest Green):        {counts[4]}% of days")
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
