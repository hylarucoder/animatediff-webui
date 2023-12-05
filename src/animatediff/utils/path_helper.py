import os
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent.parent


def get_repo_path() -> Path:
    return BASE_PATH
