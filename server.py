import json
from pathlib import Path
import fastapi
import pydantic as pt
from fastapi import BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rich.progress import Progress
from starlette.responses import Response, FileResponse

from animatediff.consts import path_mgr
from animatediff.settings import ModelConfig
from animatediff.utils.progressbar import pgr
from animatediff.utils.util import read_json

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ApiException(HTTPException):
    def __init__(self, message: str, code=400):
        self.status_code = code
        self.detail = message


app.add_exception_handler(ApiException, lambda req, e: Response(status_code=e.status_code, content=json.dumps({
    "message": e.detail
})))


def get_models_endswith_v2(d: Path, endswith="safetensors"):
    all_files = list(d.glob("**/*.*"))
    # 创建一个映射，将每个图片文件的基本名称映射到其相对路径
    image_map = {
        f.stem: str(f) for f in all_files
        if f.is_file() and f.suffix.lstrip('.').lower() in {"png", "webp", "jpg", "jpeg"}
    }

    # 对于每个模型，获取其名字（不包括扩展名），然后在映射中查找对应的图片
    models = [
        {
            "name": str(f.relative_to(d)),
            "thumbnail": image_map.get(f.stem)  # 如果没有找到对应的图片，这将返回 None
        }
        for f in all_files
        if f.is_file() and f.name.endswith(endswith)
    ]
    models.sort(key=lambda x: x["name"])
    return models


def lora_arr():
    return [
        [
            None, 0.7
        ] for _ in range(5)
    ]


class TPreset(pt.BaseModel):
    name: str
    performance: str = "Speed"
    aspect_ratio: str = "432x768 | 9:16"
    head_prompt: str = "masterpiece, best quality"
    tail_prompt: str = ""
    negative_prompt: str = "(worst quality, low quality:1.4),nudity,simple background,border,text, patreon,bed,bedroom,white background,((monochrome)),sketch,(pink body:1.4),7 arms,8 arms,4 arms"

    checkpoint: str = "majicmixRealistic_v7.safetensors"
    loras: list[list] = pt.Field(default_factory=lora_arr)
    motion: str = "mm_sd_v15_v2.ckpt"
    motion_lora: str | None = None

    fps: int = 8
    duration: int = 4
    seed: int = -1

    lcm: bool = False
    sampler: str = "k_dpmpp_sde"
    step: int = 20
    cfg: float = 7


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


def get_projects():
    return list(sorted([_.name for _ in path_mgr.projects.iterdir() if _.is_dir()]))


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


class TParams(pt.BaseModel):
    project: str
    performance: str = "Speed"
    aspect_radio: str = "432x768 | 9:16"
    prompt: str = "masterpiece, best quality"
    negative_prompt: str = "(worst quality, low quality:1.4),nudity,simple background,border,text, patreon,bed,bedroom,white background,((monochrome)),sketch,(pink body:1.4),7 arms,8 arms,4 arms"
    fps: int = 8
    duration: int = 4
    seed: int = -1
    checkpoint: str = "majicmixRealistic_v7.safetensors"
    motion: str = "mm_sd_v15_v2.ckpt"
    motion_loras: str | None = None
    lora_items: list[list] = pt.Field(default_factory=lora_arr)


def group_by_n(l, n):
    for i in range(0, len(l), n):
        yield l[i: i + n]


def render_bg(data: TParams):
    with Progress() as progress:
        pgr.set_pgr(progress)

        project_dir = path_mgr.projects / data.project
        global_config = ModelConfig(**read_json(path_mgr.demo_prompt_json))
        project_dir.mkdir(exist_ok=True)
        performance = data.performance
        if performance == "Speed":
            # 感觉要重写
            global_config.lcm_lora_scale = 1
            global_config.apply_lcm_lora = False
            global_config.steps = 20
            global_config.guidance_scale = 8
        elif performance == "Quality":
            global_config.lcm_lora_scale = 1
            global_config.apply_lcm_lora = False
            global_config.steps = 40
            global_config.guidance_scale = 8
        elif performance == "Extreme Speed":
            global_config.lcm_lora_scale = 1
            global_config.apply_lcm_lora = True
            global_config.steps = 8
            global_config.guidance_scale = 1.8

        global_config.head_prompt = "masterpiece, best quality"
        # TODO: use gpt2 optimizing?
        global_config.tail_prompt = data.prompt
        global_config.n_prompt = [data.negative_prompt]

        global_config.lora_map = {
            lora[0]: lora[1] for lora in data.lora_items if lora[0]
        }
        global_config.seed = [data.seed]
        global_config.checkpoint = data.checkpoint
        global_config.motion = data.motion
        global_config.motion_lora_map = {}
        global_config.prompt_map = {
            "0": global_config.tail_prompt,
        }
        global_config.output = {"format": "mp4", "fps": 8, "encode_param": {"crf": 10}}
        open(project_dir / "prompts.json", "wt", encoding="utf-8").write(
            global_config.model_dump_json(
                indent=2,
            )
        )

        pgr.update(pgr.task_id_config, advance=100)
        pgr.update(pgr.task_id_main, advance=10)
        global bg_task
        global bg_task_video
        from animatediff.cli import generate
        try:
            save_dir = generate(
                config_path=project_dir / "prompts.json",
                width=432,
                height=768,
                length=data.fps * data.duration,
                # TODO: check something
                context=16,
                overlap=16 // 4,
                stride=0,
                repeats=1,
                device="cuda",
                use_xformers=False,
                force_half_vae=False,
                out_dir=project_dir / "draft",
                no_frames=False,
                save_merged=False,
            )
            bg_task_video = save_dir / "video.mp4"
        except Exception as e:
            print(e)
        finally:
            bg_task = False


bg_task = False
bg_task_video = None


def raise_if(
        condition: bool,
        message: str,
):
    if condition:
        raise ApiException(message)


def raise_unless(
        condition: bool,
        message: str,
):
    if not condition:
        raise ApiException(message)


def validate_data(data: TParams):
    raise_unless((path_mgr.checkpoints / data.checkpoint).exists(), "Checkpoint not Exist!")
    # loras
    raise_unless((path_mgr.motions / data.motion).exists(), "Motion not Exist!")
    # motion
    # motion loras


@app.post("/api/tasks/submit")
def render_submit(
        data: TParams,
        background_tasks: BackgroundTasks,
):
    validate_data(data)
    global bg_task_video
    global bg_task
    if bg_task:
        return {"message": "rendering"}
    bg_task_video = None
    bg_task = True
    background_tasks.add_task(render_bg, data)
    return {"message": "Hello World"}


@app.get("/api/tasks/status")
def render_status():
    global bg_task_video
    global task_progress
    return {
        "video_path": bg_task_video,
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
