import os
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import FileResponse, Response

from animatediff.adw.contrib import PtBaseModel
from animatediff.adw.exceptions import raise_unless
from animatediff.adw.schema import TPerformance, TPipeline, TPreset, TStatusEnum
from animatediff.adw.service import (
    TParamsRenderVideo,
    get_projects,
    sub_render_video,
)
from animatediff.adw.utils import get_models_endswith
from animatediff.consts import path_mgr
from animatediff.globals import GPipeline, g, get_pipeline_by_id, pipeline_queue, set_global_pipeline

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
        aspect_ratio="16:9",
    )
    preset_color = TPreset(
        name="lcm + motion-lora + color fashion",
        performance=TPerformance.EXTREME_SPEED,
        head_prompt="masterpiece,best quality, 1girl, walk,",
        prompt="photorealistic,realistic,photography,ultra-detailed,1girl,full body,water,dress,looking at viewer,red dress,white hair,md colorful",
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


def serialize_pipeline(p: GPipeline):
    return {
        "pid": p.pid,
        "status": p.pipeline.status,
        "completed": p.pipeline.completed,
        "total": p.pipeline.total,
        "subtasks": p.pipeline.subtasks,
        "videoPath": p.pipeline.video_path,
    }


@bp.post("/api/pipeline/submit")
def render_submit(
        data: TParamsRenderVideo,
        background_tasks: BackgroundTasks,
):
    validate_data(data)
    pending_or_running_pipelines = list(
        filter(lambda x: x.pipeline.status in [TStatusEnum.PENDING, TStatusEnum.RUNNING], pipeline_queue)
    )
    if pending_or_running_pipelines:
        return pending_or_running_pipelines[-1]
    pid = len(pipeline_queue) + 1
    pipeline = set_global_pipeline(pid)
    background_tasks.add_task(sub_render_video, data, pid)
    return {
        "pipeline": serialize_pipeline(pipeline),
    }


class TTasksStatusData(PtBaseModel):
    pid: int


@bp.post("/api/pipeline/status")
async def render_status(data: TTasksStatusData) -> TPipeline | dict:
    pipeline = get_pipeline_by_id(data.pid)
    if not pipeline:
        return {}
    pbar = pipeline.progress_bar
    return TPipeline(
        pid=pipeline.pid,
        status=pipeline.pipeline.status,
        video_path=str(pipeline.pipeline.video_path),
        completed=pipeline.pipeline.completed,
        total=pipeline.pipeline.total,
        interrupt_processing=pipeline.interrupt_processing,
        processing_interrupted=pipeline.processing_interrupted(),
        subtasks=[
            {
                "description": p.desc,
                "total": p.total,
                "completed": p.n,
            }
            for p in [
                pbar.pbar_config,
                pbar.pbar_preprocess_image,
                pbar.pbar_image_2_image,
                pbar.pbar_load_model,
                pbar.pbar_animate,
                pbar.pbar_unload_models,
                pbar.pbar_make_video,
            ]
        ],
    )


class TTasksStatusData(PtBaseModel):
    pid: int


@bp.post("/api/pipeline/interrupt")
def render_interrupt(data: TTasksStatusData):
    pipeline = get_pipeline_by_id(data.pid)
    pipeline.interrupt_current_processing()
    return {}


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
        range_header = request.headers.get("Range", None)
        if range_header:
            range_value = range_header.strip("Range: bytes=")
            if "-" in range_value:
                byte1, byte2 = range_value.split("-")
                byte1 = int(byte1)
                byte2 = int(byte2) if byte2 else file_size - 1
            else:
                byte1 = int(range_value)
                byte2 = file_size - 1

            byte2 = min(byte2, file_size - 1)
            length = byte2 + 1 - byte1
            with open(absolute_path, "rb") as f:
                f.seek(byte1)
                data = f.read(length)
            response = Response(content=data, media_type="video/mp4", status_code=206)
            response.headers["Content-Range"] = f"bytes {byte1}-{byte2}/{file_size}"
            response.headers["Accept-Ranges"] = "bytes"
            return response
        else:
            return FileResponse(str(absolute_path), media_type="video/mp4")
    else:
        return FileResponse(str(absolute_path))
