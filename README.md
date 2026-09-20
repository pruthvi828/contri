# Activity & Telemetry Engine 🚀

A lightweight, automated developer telemetry and daily activity logging engine.

## Overview
This repository maintains automated engineering logs, benchmark checkpoints, and development progress tracking.

### Features
- **Dynamic Activity Logging**: Records structured daily progress checkpoints and maintenance logs.
- **Idempotency Safeguards**: Prevents duplicate executions within a single calendar day.
- **Automated Synchronization**: Operates via GitHub Actions and local scheduler integration.

## Usage
Run daily activity sync:
```bash
python safe_engine.py --auto
```

Force run:
```bash
python safe_engine.py --force
```

Run simulation (preview activity distribution):
```bash
python safe_engine.py --dry-run
```
