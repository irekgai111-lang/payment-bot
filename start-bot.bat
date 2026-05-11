@echo off
REM Auto-launcher for service-upgrade-system bot (Windows Task Scheduler)
cd /d "C:\Users\Dell\Documents\project\service-upgrade-system"

REM Clean stale PID lock from previous run
if exist bot.pid del /q bot.pid

REM Start bot, append stdout/stderr to log
"C:\Users\Dell\AppData\Local\Programs\Python\Python312\python.exe" bot.py >> bot_logs.log 2>&1
