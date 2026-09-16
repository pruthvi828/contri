# ==============================================================================
# Setup Windows Task Scheduler for Daily GitHub Activity
# Run this in PowerShell to register a silent, safe daily task on your PC.
# ==============================================================================

$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "D:\projects\git contri\git-contribution-\script.py --daily" -WorkingDirectory "D:\projects\git contri\git-contribution-"
$Trigger = New-ScheduledTaskTrigger -Daily -At 8:00PM
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "DailyGitHubSafeActivity" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Runs safe daily GitHub activity with variable natural intensity"

Write-Host "✔ Scheduled Task 'DailyGitHubSafeActivity' created successfully!" -ForegroundColor Green
