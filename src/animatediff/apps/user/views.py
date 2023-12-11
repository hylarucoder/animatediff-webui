import os
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Request, Response
from fastapi.responses import FileResponse, Response

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

bp = APIRouter(prefix="")


@bp.get("/")
def index():
    return {"message": "Hello World"}


class TPresetItems(PtBaseModel):
    presets: list[TPreset]


@bp.get("/api/presets")
def get_presets() -> TPresetItems:
    presets = gen_presets()
    return TPresetItems(**{"presets": presets})


def gen_presets():
    preset_default = TPreset(
        name="default",
    )
    preset_lcm = TPreset(
        name="default - lcm",
        performance=TPerformance.EXTREME_SPEED,
        aspect_radio="768x432 | 16:9",
    )
    preset_color = TPreset(
        name="lcm + motion-lora + color fashion",
        performance=TPerformance.EXTREME_SPEED,
        head_prompt="masterpiece,best quality, 1girl, walk,",
        tail_prompt="photorealistic,realistic,photography,ultra-detailed,1girl,full body,water,dress,looking at viewer,red dress,white hair,md colorful",
        lcm=True,
        duration=2,
    )
    preset_color.loras[0] = ["釉彩·麻袋调色盘_v1.0.safetensors", 0.8]
    preset_quality_default = TPreset(
        name="Speed",
        duration=1,
        performance=TPerformance.SPEED,
        high_res=True,
    )
    presets = [
        preset_quality_default,
        preset_default,
        preset_lcm,
        preset_color,
    ]
    return presets


class TOptionsPreviewItem(PtBaseModel):
    name: str
    thumbnail: str | None


class TOptions(PtBaseModel):
    projects: list[str]
    checkpoints: list[TOptionsPreviewItem]
    motions: list[TOptionsPreviewItem]
    motion_loras: list[TOptionsPreviewItem]
    loras: list[TOptionsPreviewItem]
    presets: list[TPreset]


@bp.get("/api/options")
def get_checkpoints() -> TOptions:
    checkpoints = get_models_endswith(path_mgr.checkpoints)
    motion_loras = get_models_endswith(path_mgr.motion_loras, endswith="ckpt")
    motions = get_models_endswith(
        path_mgr.motions,
        endswith="ckpt",
    )
    loras = get_models_endswith(
        path_mgr.loras,
    )
    presets = gen_presets()
    return TOptions(
        **{
            "projects": get_projects(),
            "checkpoints": checkpoints,
            "loras": loras,
            "motions": motions,
            "motion_loras": motion_loras,
            "presets": presets,
        }
    )


def validate_data(data: TParamsRenderVideo):
    raise_unless((path_mgr.checkpoints / data.checkpoint).exists(), "Checkpoint not Exist!")
    # loras
    # raise_unless((path_mgr.motions / data.motion).exists(), "Motion not Exist!")
    # motion
    # motion loras


def serialize_task(task: TTask):
    return {
        "taskId": task.task_id,
        "status": task.status,
        "completed": task.completed,
        "total": task.total,
        "subtasks": task.subtasks,
        "videoPath": task.video_path,
    }


@bp.post("/api/tasks/submit")
def render_submit(
        data: TParamsRenderVideo,
        background_tasks: BackgroundTasks,
):
    validate_data(data)
    pending_or_running_tasks = list(
        filter(lambda x: x.status in [TStatusEnum.pending, TStatusEnum.running], tasks_store)
    )
    if pending_or_running_tasks:
        return pending_or_running_tasks[-1]
    task_id = len(tasks_store) + 1
    bg_task = push_task_by_id(task_id)
    background_tasks.add_task(sub_render_video, data, task_id)
    return {
        "task": serialize_task(bg_task),
    }


@bp.get("/api/tasks/status")
def render_status():
    if not tasks_store:
        return {
            "task": None,
            "progress": None,
        }
    bg_task = tasks_store[-1]
    return {
        "task": {
            "taskId": bg_task.task_id,
            "status": bg_task.status,
            "completed": bg_task.completed,
            "total": bg_task.total,
            "subtasks": bg_task.subtasks,
            "videoPath": bg_task.video_path,
        },
        "progress": {"main": pbar.status[0] if pbar.status else None, "tasks": pbar.status[1:]},
    }


@bp.get("/api/tasks/interrupt")
def render_interrupt():
    return {"message": "Hello World"}


@bp.get("/api/tasks/skip")
def presets__a():
    return {"message": "Hello World"}


@bp.get("/media")
async def image_proxy(path: str, request: Request):
    p = Path(path)
    if not p.exists():
        return Response(status_code=404)
    absolute_path = Path(path_mgr.repo) / path
    repo_dir = Path(path_mgr.repo)
    if str(repo_dir) not in str(absolute_path):
        return Response(status_code=404)
    suffix = str(absolute_path).split(".")[-1]
    if suffix not in ["png", "jpg", "jpeg", "mp4", "webp"]:
        return Response(status_code=404)

    if suffix == "mp4":
        file_size = os.path.getsize(absolute_path)
        range_header = request.headers.get('Range', None)
        if range_header:
            range_value = range_header.strip('Range: bytes=')
            byte1, byte2 = 0, None
            if '-' in range_value:
                byte1, byte2 = range_value.split('-')
                byte1 = int(byte1)
                byte2 = int(byte2) if byte2 else file_size - 1
            else:
                byte1 = int(range_value)
                byte2 = file_size - 1

            byte2 = min(byte2, file_size - 1)
            length = byte2 + 1 - byte1
            with open(absolute_path, 'rb') as f:
                f.seek(byte1)
                data = f.read(length)
            response = Response(content=data, media_type="video/mp4", status_code=206)
            response.headers['Content-Range'] = f'bytes {byte1}-{byte2}/{file_size}'
            response.headers['Accept-Ranges'] = 'bytes'
            return response
        else:
            return FileResponse(str(absolute_path), media_type="video/mp4")
    else:
        return FileResponse(str(absolute_path))
