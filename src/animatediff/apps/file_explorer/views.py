from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
from starlette.responses import FileResponse, Response

from animatediff.adw.contrib import PtBaseModel
from animatediff.adw.exceptions import raise_unless
from animatediff.adw.schema import TPerformance, TPreset, TStatusEnum, TTask
from animatediff.adw.service import (
    TParamsRenderVideo,
    get_projects,
    push_task_by_id,
    sub_render_video,
    tasks_store,
)
from animatediff.adw.utils import get_models_endswith
from animatediff.consts import path_mgr
from animatediff.utils.progressbar import pbar

bp = APIRouter(prefix="/api/file_explorer")


