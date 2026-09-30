#!/usr/bin/env python3
"""
==============================================================================
Safe Natural GitHub Contribution & Heatmap Engine
Repository: pruthvi828/contri
Author: pruthvi828 <jadhavpruthvi828@gmail.com>

NATURAL HEATMAP DESIGN:
GitHub divides active days across 4 quartiles to render green shades:
- Tier 0: Rest Day (0 commits, Gray)          -> ~15-20% overall (higher on weekends)
- Tier 1: Light Green (1-2 commits, "Lil bit")-> ~35% of days
- Tier 2: Medium Green (3-5 commits)          -> ~28% of days
- Tier 3: Medium-Dark Green (6-8 commits)     -> ~12% of days
- Tier 4: Deepest Green (9-14 commits, Sprint)-> ~10% of days

ANTI-DETECTION SAFEGUARDS:
- Strictly organic volume (0 to 14 commits max).
- Realistic daytime timestamps spread between 09:30 AM and 10:45 PM.
- Chronologically sorted commits with natural spacing.
- Idempotency guard: Skips duplicate runs unless --force is used.
- Unified Git identity: pruthvi828 <jadhavpruthvi828@gmail.com>.
==============================================================================
"""

import os
import sys
import json
import random
import subprocess
import time
from datetime import datetime, timedelta

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
    "update: periodic maintenance and state synchronization",
    "refactor: extract reusable string utility routines",
    "docs: add inline comments for async worker loops",
    "fix: handle timeout gracefully on socket retry",
    "chore: update build dependency versions and pin requirements",
    "feat: add telemetry heartbeat verification check"
]

# GitHub Contribution Tiers: (min_commits, max_commits)
HEATMAP_TIERS = {
    0: (0, 0),    # Tier 0: Rest Day (0 commits, Gray / Empty)
    1: (1, 2),    # Tier 1: Light Green ("Lil bit", 1-2 commits)
    2: (3, 5),    # Tier 2: Medium Green (3-5 commits)
    3: (6, 8),    # Tier 3: Medium-Dark Green (6-8 commits)
    4: (9, 14)    # Tier 4: Full Dark Green (Sprint days, 9-14 commits)
}

TIER_LABELS = {
    0: "⬜ Rest Day (0 commits, Gray)",
    1: "🟩 Lil Bit (1-2 commits, Light Green)",
    2: "🟩 Medium (3-5 commits, Medium Green)",
    3: "🟩 Dark (6-8 commits, Medium-Dark Green)",
    4: "🟩 Full Dark Green (9-14 commits, Deepest Green)"
}


def get_daily_intensity(is_weekend=False):
    """
    Computes a realistic commit volume simulating real-world developer workflows.
    - Weekdays: 10% rest, 32% light green, 32% medium green, 14% dark, 12% full dark green.
    - Weekends: 35% rest, 40% light green, 15% medium green, 6% dark, 4% full dark green.
    Returns: (tier_number, commit_count)
    """
    if is_weekend:
        weights = [0.35, 0.40, 0.15, 0.06, 0.04]
    else:
        weights = [0.10, 0.32, 0.32, 0.14, 0.12]

    tier = random.choices([0, 1, 2, 3, 4], weights=weights)[0]
    min_c, max_c = HEATMAP_TIERS[tier]
    
    if min_c == max_c:
        return tier, min_c
    return tier, random.randint(min_c, max_c)


def generate_spaced_timestamps(target_date, count):
    """
    Generates `count` timestamps during realistic waking/working hours (09:30 to 22:45),
    chronologically ordered with realistic random gaps (5 to 45 mins) between commits.
    """
    if count == 0:
        return []

    # Working window: 09:30 AM (570 mins) to 10:45 PM (1365 mins) -> 795 minutes span
    start_minute = random.randint(570, 660) # Between 09:30 and 11:00 AM
    end_minute = random.randint(1260, 1365)  # Between 09:00 and 10:45 PM
    
    if count == 1:
        minutes = [random.randint(start_minute, end_minute)]
    else:
        # Generate random distinct points within the window and sort
        available_range = max(count * 5, end_minute - start_minute)
        step = available_range / count
        minutes = []
        for i in range(count):
            base = int(start_minute + i * step)
            jitter = random.randint(-int(step * 0.3), int(step * 0.3))
            minutes.append(max(540, min(1410, base + jitter)))
        minutes.sort()

    timestamps = []
    base_midnight = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    for m in minutes:
        h = m // 60
        mn = m % 60
        sec = random.randint(0, 59)
        timestamps.append(base_midnight.replace(hour=h, minute=mn, second=sec))

    return timestamps


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
    try:
        subprocess.run(["git", "config", "user.name", GIT_USER_NAME], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "config", "user.email", GIT_USER_EMAIL], cwd=REPO_DIR, check=True)
    except Exception:
        pass


def make_single_commit(commit_datetime, message=None, index=1):
    """
    Writes a clean, structured UTF-8 log line and creates a git commit
    with matching author and committer dates.
    """
    if not message:
        base_msg = random.choice(COMMIT_MESSAGES)
        message = f"{base_msg} (#{index})"

    date_str = commit_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    session_id = f"{random.randint(100000, 999999):x}"
    log_entry = f"[{date_str}] {message} | session: {session_id}\n"

    # Append to activity log
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
    """Main daily routine executed by GitHub Actions or local scheduler."""
    today = datetime.now()
    is_weekend = today.weekday() in [5, 6]

    print("=" * 65)
    print(f" Natural GitHub Contribution Engine: {today.strftime('%A, %d %B %Y')}")
    print("=" * 65)

    ensure_git_identity()

    existing_count = has_commits_today(today)
    if existing_count > 0 and not force:
        print(f"ℹ Today already has {existing_count} commit(s) in the repository.")
        print("  Skipping automated run to maintain organic spacing and prevent spam.")
        return

    tier, commit_count = get_daily_intensity(is_weekend)

    if force and commit_count == 0:
        # In force mode, ensure at least a light or medium commit
        tier = random.choice([1, 2, 4])
        commit_count = random.randint(*HEATMAP_TIERS[tier])

    if commit_count == 0:
        print("🌱 Today is a natural REST DAY (0 commits).")
        print("   Simulates genuine human rest, leaving a gray square on GitHub heatmap.")
        return

    print(f"🎯 Scheduled Intensity: Tier {tier} -> {TIER_LABELS[tier]}")
    print(f"   Executing {commit_count} natural commit(s)...")

    # Generate chronologically spaced daytime timestamps
    timestamps = generate_spaced_timestamps(today, commit_count)

    for idx, ts in enumerate(timestamps, 1):
        make_single_commit(ts, index=idx)
        time.sleep(0.02)

    git_push()
    print(f"\n🎉 Successfully created {commit_count} commits across {TIER_LABELS[tier]}.")


def dry_run_simulation(days=100):
    """Simulates activity distribution over N days to visualize the natural heatmap breakdown."""
    print(f"\n=================================================================")
    print(f" SIMULATION: {days} Days of Natural GitHub Activity Distribution")
    print(f"=================================================================")
    
    tier_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    total_commits = 0
    calendar_grid = []

    for day in range(days):
        is_wknd = (day % 7) in [5, 6]
        tier, c = get_daily_intensity(is_wknd)
        tier_counts[tier] += 1
        total_commits += c
        
        # Grid representation (white=gray, green gradients)
        symbols = {0: "⬜", 1: "🟩", 2: "🟩", 3: "🟩", 4: "🟩"}
        calendar_grid.append(symbols[tier])

    print("\nVisual Heatmap Calendar Preview (7 days per row):")
    for i in range(0, len(calendar_grid), 7):
        print(" ".join(calendar_grid[i:i+7]))

    print("\nDistribution Breakdown:")
    print("-" * 65)
    for t in range(5):
        pct = (tier_counts[t] / days) * 100
        print(f"  Tier {t}: {TIER_LABELS[t]:<45} | {tier_counts[t]:>3} days ({pct:>4.1f}%)")
    print("-" * 65)
    print(f"Total simulated commits: {total_commits}")
    print(f"Average commits per day: {total_commits / days:.2f} commits/day")
    print(f"Active days: {days - tier_counts[0]} / {days} ({(days - tier_counts[0])/days*100:.1f}%)")
    print("=================================================================\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--auto", "--daily", "-d", "daily"]:
            run_daily_activity(force=False)
            sys.exit(0)
        elif arg in ["--force", "-f"]:
            run_daily_activity(force=True)
            sys.exit(0)
        elif arg in ["--dry-run", "--sim", "-s"]:
            days = 100
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                days = int(sys.argv[2])
            dry_run_simulation(days)
            sys.exit(0)
        elif arg in ["--status"]:
            today = datetime.now()
            count = has_commits_today(today)
            print(f"Today ({today.strftime('%Y-%m-%d')}): {count} commit(s) recorded.")
            sys.exit(0)

    print("\n--- GitHub Natural Contribution Engine ---")
    print("1. Run Daily Activity (Natural intensity)")
    print("2. Force Run Today (Guarantees commits)")
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
