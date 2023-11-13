@echo off
REM Get current folder name
for %%* in (.) do set folder=%%~n*
echo Current directory name is: %folder%

REM cd Repo
cd /d %~dp0\..\..

REM Python command
SET "cmd=.\venv\Scripts\python -m animatediff generate -c .\projects\%folder%\prompts.json -W 504 -H 896 -L 32 -C 16 -o .\projects\%folder%\preview"

REM Execute the command
CALL %cmd%
PAUSE
