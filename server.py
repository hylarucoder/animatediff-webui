import json
from pathlib import Path

import fastapi
import pydantic as pt
from fastapi import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response, FileResponse

from animatediff.adw.exceptions import ApiException, raise_unless
from animatediff.adw.schema import TTask, TPreset, TStatusEnum
from animatediff.adw.service import get_projects, TParams, tasks_store, push_task_by_id, do_render_video
from animatediff.adw.utils import get_models_endswith_v2
from animatediff.consts import path_mgr
from animatediff.utils.progressbar import pgr

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ApiException, lambda req, e: Response(status_code=e.status_code, content=json.dumps({
    "message": e.detail
})))


@app.get("/")
def index():
    return {"message": "Hello World"}


class TPresetItems(pt.BaseModel):
    presets: list[TPreset]


@app.get("/api/presets")
def get_presets() -> TPresetItems:
    presets = gen_presets()
    return TPresetItems(**{"presets": presets})


def gen_presets():
    preset_default = TPreset(
        name="default",
    )
    preset_lcm = TPreset(
        name="default - lcm",
        performance="Extreme Speed",
        aspect_radio="768x432 | 16:9",
    )
    preset_color = TPreset(
        name="lcm + motion-lora + color fashion",
        performance="Extreme Speed",
        head_prompt="masterpiece,best quality, 1girl, walk,",
        tail_prompt="photorealistic,realistic,photography,ultra-detailed,1girl,full body,water,dress,looking at viewer,red dress,white hair,md colorful",
        lcm=True,
        duration=2,
    )
    preset_color.loras[0] = ["釉彩·麻袋调色盘_v1.0.safetensors", 0.8]
    presets = [
        preset_default,
        preset_lcm,
        preset_color,
    ]
    return presets


@app.get("/api/options")
def get_checkpoints():
    checkpoints = get_models_endswith_v2(path_mgr.checkpoints)
    motion_loras = get_models_endswith_v2(path_mgr.motion_loras, endswith="ckpt")
    motions = get_models_endswith_v2(
        path_mgr.motions,
        endswith="ckpt",
    )
    loras = get_models_endswith_v2(
        path_mgr.loras,
    )
    presets = gen_presets()
    return {
        "projects": get_projects(),
        "checkpoints": checkpoints,
        "loras": loras,
        "motions": motions,
        "motion_loras": motion_loras,
        "presets": presets,
    }


def validate_data(data: TParams):
    raise_unless((path_mgr.checkpoints / data.checkpoint).exists(), "Checkpoint not Exist!")
    # loras
    raise_unless((path_mgr.motions / data.motion).exists(), "Motion not Exist!")
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


@app.post("/api/tasks/submit")
def render_submit(
        data: TParams,
        background_tasks: BackgroundTasks,
):
    validate_data(data)
    pending_or_running_tasks = list(
        filter(lambda x: x.status in [TStatusEnum.pending, TStatusEnum.running], tasks_store))
    if pending_or_running_tasks:
        return pending_or_running_tasks[-1]
    task_id = len(tasks_store) + 1
    bg_task = push_task_by_id(task_id)
    background_tasks.add_task(do_render_video, data, task_id)
    return {
        "task": serialize_task(bg_task),
    }


@app.get("/api/tasks/status")
def render_status():
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
        "progress": {
            "main": pgr.status[0] if pgr.status else None,
            "tasks": pgr.status[1:]
        }
    }


@app.get("/api/tasks/interrupt")
def render_interrupt():
    return {"message": "Hello World"}


@app.get("/api/tasks/skip")
def presets__a():
    return {"message": "Hello World"}


@app.get("/media")
def image_proxy(path: str):
    p = Path(path)
    if not p.exists():
        return Response(status_code=404)
    absolute_path = Path(path_mgr.repo) / path
    repo_dir = Path(path_mgr.repo)
    if str(repo_dir) not in str(absolute_path):
        return Response(status_code=404)
    if str(absolute_path).split(".")[-1] not in ["png", "jpg", "jpeg", "mp4", "webp"]:
        return Response(status_code=404)
    return FileResponse(str(absolute_path))


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, reload=True, host="0.0.0.0", port=7860)
