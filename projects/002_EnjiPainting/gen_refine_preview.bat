@echo off
REM Get dropped item folder name
for %%I in ("%~dp1") do set "folder=%%~nI"

REM Get the current directory
cd /d %~dp0\..

REM Define your Python script

REM Python command
SET "cmd=.\venv\Scripts\python -m animatediff refine -W 768 -C 16 -t 1 -L 32 %* -o .\projects\%folder%\refined"

REM Execute the command
CALL %cmd%
PAUSE
