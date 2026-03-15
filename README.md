# RiskAssessment_Barrier design
Crompton Risk Assessment and Barrier design 

## Web Risk Refresh (Python)

Use the Python analyzer to pull external guidance signals and update the local risk database file.

Daily run (incremental append):

```powershell
& ".venv/Scripts/python.exe" web_risk_analysis.py
```

Manual rebuild (force replace web-analysis records):

```powershell
& ".venv/Scripts/python.exe" web_risk_analysis.py --force
```

Output file:

- web-risk-database.json
- datapol.json (daily synchronized copy for downstream sync target)
- web-source-registry.json (auto-discovered source list)

VS Code Task:

- Task name: Run daily web risk finder
- Task name: Refresh web risk database (force)
- Run via: Terminal -> Run Task

Windows Scheduled Task:

- Task name: RiskAssessment_DailyWebFinder
- Schedule: Daily at 06:00 AM
- Runs: web_risk_analysis.py (incremental mode)
