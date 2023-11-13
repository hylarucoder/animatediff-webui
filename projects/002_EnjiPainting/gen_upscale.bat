@echo off
REM Get dropped item folder name
for %%I in ("%~dp1") do set "folder=%%~nI"

REM Get the current directory
cd /d %~dp0\..

REM Python command
SET "cmd=.\venv\Scripts\python -m animatediff tile-upscale -W 1024 %*  -o .\projects\%folder%\upscaled"

REM Execute the command
CALL %cmd%
PAUSE
