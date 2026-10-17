


@echo off
:: Get date in YYYY-MM-DD format using PowerShell
for /f %%a in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd'"') do set "today=%%a"

python SocialEmailsAgent.py  > "reasons_%today%.txt" 2>&1
