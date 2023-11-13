@echo off
REM Get dropped item folder name
for %%I in ("%~dp1") do

REM Get the current directory
cd /d %~dp0\..

REM Define your Python script

REM Python command
SET "cmd=.\venv\Scripts\python -m animatediff refine -W 768 -C 6 %* -o .\projects\%folder%\refined"

REM Execute the command
CALL %cmd%
PAUSE
