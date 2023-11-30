@echo off
SET "cmd=.\venv\Scripts\uvicorn server:app  --reload --host 0.0.0.0 --port 7860"
CALL %cmd%
PAUSE
