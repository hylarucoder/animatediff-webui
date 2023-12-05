@echo off
SET "cmd=.\venv\Scripts\python -m pytest tests/functional/test_render_video.py -s --tb=auto -l"
CALL %cmd%
PAUSE
