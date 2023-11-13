@echo off
REM Get current folder name
for %%* in (.) do set folder=%%~n*
echo Current directory name is: %folder%

REM cd Repo
cd /d %~dp0\..\..

REM Python command
SET "cmd=.\venv\Scripts\python -m animatediff generate -c .\projects\%folder%\prompts.json -W 504 -H 896 -L 200 -C 16 -o .\projects\%folder%\draft"

REM Execute the command
CALL %cmd%
PAUSE
