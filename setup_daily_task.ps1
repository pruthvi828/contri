# ==============================================================================
# Setup Windows Task Scheduler for Daily GitHub Activity
# Registers a silent, safe daily task on your PC with full binary path.
# ==============================================================================

$PythonPath = "C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe"
$ScriptPath = "D:\projects\git contri\safe_engine.py"
$RepoDir = "D:\projects\git contri"

if (-not (Test-Path $PythonPath)) {
    # Fallback to PATH resolution if path differs
    $PythonCmd = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
    if ($PythonCmd) {
        $PythonPath = $PythonCmd
    }
}

Write-Host "Configuring Scheduled Task with Python: $PythonPath" -ForegroundColor Cyan

$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument "`"$ScriptPath`" --auto" -WorkingDirectory $RepoDir
$Trigger = New-ScheduledTaskTrigger -Daily -At 8:00PM
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Unregister old task if present to cleanly replace it
Unregister-ScheduledTask -TaskName "DailyGitHubSafeActivity" -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask -TaskName "DailyGitHubSafeActivity" -Action $Action -Trigger $Trigger -Settings $Settings -Description "Runs safe daily GitHub activity with variable natural intensity"

Write-Host "✔ Scheduled Task 'DailyGitHubSafeActivity' registered successfully!" -ForegroundColor Green
