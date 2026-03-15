$ErrorActionPreference = 'Stop'

$taskName = 'RiskAssessment_DailyWebFinder'
$pythonPath = (Resolve-Path '.\.venv\Scripts\python.exe').Path
$scriptPath = (Resolve-Path '.\web_risk_analysis.py').Path

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument ('"{0}"' -f $scriptPath)
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

$task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings
Register-ScheduledTask -TaskName $taskName -InputObject $task -Force | Out-Null

Write-Output "Scheduled task created/updated: $taskName"
Write-Output "Runs daily at 06:00 AM"
Write-Output "Command: $pythonPath \"$scriptPath\""
