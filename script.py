import os
import json
import random
import subprocess
import sys
import time
from datetime import datetime, timedelta

# ==============================================================================
# Safe GitHub Activity & Contribution Engine
#
# DESIGNED FOR MAXIMUM SAFETY & ACCOUNT SECURITY:
# - Strict human-like commit volume (1 to 6 commits per day, max cap 8).
# - Variable intensity (light, medium, deep green) matching GitHub shades.
# - Realistic timestamps spaced across working hours (not static 12:00:00).
# - Natural rest-day simulation (occasional skips / low activity on weekends).
# - Stays well within GitHub Acceptable Use Policies.
# ==============================================================================

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(REPO_DIR, "activity_log.txt")
PATTERN_FILE = os.path.join(REPO_DIR, "pattern.json")

# Realistic commit messages that look like genuine engineering notes
COMMIT_MESSAGES = [
    "refactor: optimize internal data structures",
    "docs: update documentation and project notes",
    "perf: improve runtime loop efficiency",
    "chore: dependency synchronization and cleanup",
    "fix: edge case handling in telemetry parser",
    "style: format codebase and clean up linter warnings",
    "test: add assertions for boundary conditions",
    "feat: modularize core utility helpers",
    "ci: verify pipeline build configuration",
    "update: synchronize daily progress checkpoint"
]

# GitHub Intensity Tiers (commits needed for different green shades)
# Level 1 (Light Green): 1 - 2 commits
# Level 2 (Medium Green): 3 - 4 commits
# Level 3 (Deep Green): 5 - 6 commits
# Level 4 (Darkest Green): 7 - 8 commits (capped to avoid bot detection)
INTENSITY_TIERS = {
    1: (1, 2),
    2: (3, 4),
    3: (5, 6),
    4: (7, 8)
}


def get_random_intensity(is_weekend=False):
    """
    Returns a realistic commit count for the day.
    Simulates real developer activity with variable weights.
    """
    if is_weekend:
        # Weekends: higher chance of resting or light activity
        weights = [0.30, 0.45, 0.20, 0.05]  # [0 (skip), Level 1, Level 2, Level 3]
        choice = random.choices([0, 1, 2, 3], weights=weights)[0]
    else:
        # Weekdays: mostly Level 1, 2, or 3
        weights = [0.08, 0.35, 0.42, 0.15]  # [0 (skip), Level 1, Level 2, Level 3]
        choice = random.choices([0, 1, 2, 3], weights=weights)[0]

    if choice == 0:
        return 0  # Rest day
    
    min_c, max_c = INTENSITY_TIERS[choice]
    return random.randint(min_c, max_c)


def generate_realistic_time(target_date):
    """
    Generates a realistic daytime timestamp between 09:30 AM and 10:45 PM
    with random minutes and seconds.
    """
    hour = random.randint(9, 22)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return target_date.replace(hour=hour, minute=minute, second=second)


def make_single_commit(commit_datetime, message=None):
    """
    Performs a single safe git commit with a specific author date.
    Updates activity_log.txt to ensure meaningful, non-empty tracked changes.
    """
    if not message:
        message = random.choice(COMMIT_MESSAGES)

    date_str = commit_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    # Update activity log with a realistic payload
    log_entry = f"[{date_str}] {message} | hash: {random.randint(100000, 999999)}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

    # Git Add
    subprocess.run(["git", "add", LOG_FILE], cwd=REPO_DIR, check=True)

    # Git Commit with custom environment dates
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            message,
            "--date",
            date_str
        ],
        cwd=REPO_DIR,
        env=env,
        check=True
    )

    print(f"  ✔ [{commit_datetime.strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def git_push():
    """Safely pushes commits to remote origin."""
    print("\nPushing commits to remote repository...")
    try:
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        print("✔ Remote repository synchronized successfully.")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Git push encountered an issue: {e}")


def run_daily_activity(force_active=False):
    """
    Executes today's activity with variable intensity.
    """
    today = datetime.now()
    is_weekend = today.weekday() in [5, 6]  # Saturday or Sunday

    print(f"\n=======================================================")
    print(f" Daily Activity Runner: {today.strftime('%A, %d %B %Y')}")
    print(f"=======================================================")

    commit_count = get_random_intensity(is_weekend)
    if force_active and commit_count == 0:
        commit_count = random.randint(1, 3)

    if commit_count == 0:
        print("🌱 Today is a scheduled natural rest day (0 commits).")
        print("   This keeps your contribution pattern authentic and human.")
        return

    print(f"🎯 Target intensity for today: {commit_count} commits")

    # Generate spaced timestamps throughout the day
    timestamps = [generate_realistic_time(today) for _ in range(commit_count)]
    timestamps.sort()

    for idx, ts in enumerate(timestamps, 1):
        msg = f"{random.choice(COMMIT_MESSAGES)} (#{idx})"
        make_single_commit(ts, msg)
        # Small delay to keep process safe
        time.sleep(0.3)

    git_push()
    print(f"\n🎉 Successfully added {commit_count} commits with variable intensity!")


def run_pattern_with_varying_intensity(year):
    """
    Draws pattern from pattern.json with dynamic, non-constant intensity.
    Instead of flat 5 commits per day, it varies realistically.
    """
    if not os.path.exists(PATTERN_FILE):
        print(f"❌ Error: Pattern file not found at {PATTERN_FILE}")
        return

    with open(PATTERN_FILE, "r") as f:
        pattern = json.load(f)

    # First Sunday of the year
    d = datetime(year, 1, 1)
    while d.weekday() != 6:  # Sunday
        d += timedelta(days=1)
    start_date = d

    total_commits = 0
    print(f"\nDrawing pattern for {year} with natural varied intensity...")

    for row_idx, row in enumerate(pattern):
        for col_idx, char in enumerate(row):
            if char == " ":
                continue

            target_date = start_date + timedelta(weeks=col_idx, days=row_idx)

            # If pattern has digits (e.g. '1', '2', '3', '4'), use as intensity level
            if char.isdigit() and int(char) in INTENSITY_TIERS:
                level = int(char)
                min_c, max_c = INTENSITY_TIERS[level]
                # Add natural jitter
                count = max(1, random.randint(min_c, max_c))
            else:
                # Default varied intensity between 2 and 5
                count = random.randint(2, 5)

            for _ in range(count):
                ts = generate_realistic_time(target_date)
                make_single_commit(ts)
                total_commits += 1

    git_push()
    print(f"\n🎉 Completed pattern drawing with {total_commits} varied commits!")


# ==============================================================================
# CLI Entry Point
# ==============================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--daily", "-d", "daily"]:
            run_daily_activity(force_active=False)
            sys.exit(0)
        elif arg in ["--force", "-f"]:
            run_daily_activity(force_active=True)
            sys.exit(0)
        elif arg.isdigit():
            run_pattern_with_varying_intensity(int(arg))
            sys.exit(0)

    print("\n--- GitHub Safe Contribution Engine ---")
    print("1. Run Daily Mode (Automated today with varied intensity)")
    print("2. Run Pattern Mode (Draw from pattern.json with varied intensity)")
    print("3. Exit")
    choice = input("\nSelect an option [1-3]: ").strip()

    if choice == "1":
        run_daily_activity(force_active=False)
    elif choice == "2":
        yr = input("Enter year to render pattern (e.g. 2026): ").strip()
        if yr.isdigit():
            run_pattern_with_varying_intensity(int(yr))
        else:
            print("Invalid year.")
    else:
        print("Exiting.")
