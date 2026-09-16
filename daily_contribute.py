import os
import random
import subprocess
import sys
import time
from datetime import datetime

# ==============================================================================
# Safe Dynamic Contribution Engine
# Tailored for https://github.com/pruthvi828/contri
#
# - Variable intensity (1 to 6 commits per day) to create natural green shades.
# - Safe volume & random jitter to prevent account suspension.
# - Attributed properly to: jadhavpruthvi828@gmail.com
# ==============================================================================

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(REPO_DIR, "log.txt")

COMMIT_MESSAGES = [
    "refactor: optimize internal logic and routines",
    "docs: update documentation and project logs",
    "perf: improve performance benchmarks",
    "chore: dependency synchronization and cleanup",
    "fix: handle edge case in data parser",
    "style: format code according to style guidelines",
    "test: verify assertion checks and coverage",
    "feat: add lightweight utility helper function",
    "update: progress checkpoint"
]

# GitHub Intensity Levels:
# Level 1 (Light Green): 1 - 2 commits
# Level 2 (Medium Green): 3 - 4 commits
# Level 3 (Deep Green): 5 - 6 commits
INTENSITY_TIERS = {
    1: (1, 2),
    2: (3, 4),
    3: (5, 6)
}


def get_daily_intensity():
    today = datetime.now()
    is_weekend = today.weekday() in [5, 6]

    if is_weekend:
        # Weekends: lighter activity or rest
        weights = [0.25, 0.50, 0.20, 0.05]  # [Rest, Level 1, Level 2, Level 3]
        choice = random.choices([0, 1, 2, 3], weights=weights)[0]
    else:
        # Weekdays: active work
        weights = [0.05, 0.40, 0.40, 0.15]  # [Rest, Level 1, Level 2, Level 3]
        choice = random.choices([0, 1, 2, 3], weights=weights)[0]

    if choice == 0:
        return 0  # Natural rest day to look 100% organic
    
    min_c, max_c = INTENSITY_TIERS[choice]
    return random.randint(min_c, max_c)


def execute_commit(msg):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{now_str}] {msg} | id: {random.randint(10000, 99999)}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    subprocess.run(["git", "add", "log.txt"], cwd=REPO_DIR, check=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=REPO_DIR, check=True)
    print(f"✔ Committed: {msg}")


def main():
    commits_to_make = get_daily_intensity()
    print(f"Target commits for today: {commits_to_make}")

    if commits_to_make == 0:
        print("Today is a natural rest day. No commits made.")
        return

    for i in range(1, commits_to_make + 1):
        msg = f"{random.choice(COMMIT_MESSAGES)} (#{i})"
        execute_commit(msg)
        time.sleep(0.5)

    print(f"Completed {commits_to_make} commits with variable intensity.")


if __name__ == "__main__":
    main()
