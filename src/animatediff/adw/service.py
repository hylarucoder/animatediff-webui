import enum
import logging

import pydantic as pt
from rich.progress import Progress

from animatediff.adw.contrib import PtBaseModel
from animatediff.adw.schema import TPerformance, TStatusEnum, TTask
from animatediff.consts import path_mgr
from animatediff.schema import TProjectSetting
from animatediff.utils.progressbar import pbar
from animatediff.utils.torch_compact import get_torch_device
from animatediff.utils.util import read_json

logger = logging.getLogger(__name__)

tasks_store: list[TTask] = []


def get_task_by_id(task_id: int):
    for task in tasks_store:
        if task.task_id == task_id:
            return task
    return None


def push_task_by_id(task_id: int):
    task = TTask(
        task_id=task_id,
        status=TStatusEnum.pending,
    )
    tasks_store.append(task)
    return task


def get_projects():
    return list(sorted([_.name for _ in path_mgr.projects.iterdir() if _.is_dir()]))


def group_by_n(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def lora_arr():
    return [[None, 0.7] for _ in range(5)]


class TParamsRenderVideo(PtBaseModel):
    project: str
    performance: TPerformance = TPerformance.SPEED
    aspect_radio: str = "432x768 | 9:16"
    prompt: str = "masterpiece, best quality"
    negative_prompt: str = "(worst quality, low quality:1.4),nudity,simple background,border,text, patreon,bed,bedroom,white background,((monochrome)),sketch,(pink body:1.4),7 arms,8 arms,4 arms"
    fps: int = 8
    duration: int = 4
    seed: int = -1
    checkpoint: str = "majicmix/majicmixRealistic_v7.safetensors"
    motion: str = "mm_sd_v15_v2.ckpt"
    motion_loras: str | None = None
    lora_items: list[list] = pt.Field(default_factory=lora_arr)


def get_width_height(aspect_radio: str):
    w, h = aspect_radio.split("|")[0].strip().split("x")
    return int(w), int(h)


def resize_to_768(width, height):
    max_dim = 768

    # calculate the aspect ratio
    aspect_ratio = width / height

    if width < height:
        width = max_dim
        # new height is derived from the aspect ratio
        height = int(width / aspect_ratio)
    else:
        height = max_dim
        # new width is derived from the aspect ratio
        width = int(height * aspect_ratio)

    return width // 8 * 8, height // 8 * 8


def do_render_video(
    data: TParamsRenderVideo,
    on_config_start=lambda: None,
    on_config_end=lambda: None,
    on_render_start=lambda: None,
    on_render_success=lambda: None,
    on_render_failed=lambda: None,
    on_render_end=lambda: None,
):
    if on_config_start:
        on_config_start()
    project_dir = path_mgr.projects / data.project
    project_setting = TProjectSetting(**read_json(path_mgr.demo_prompt_json))
    project_dir.mkdir(exist_ok=True)
    performance = data.performance
    width, height = get_width_height(data.aspect_radio)
    if performance == TPerformance.SPEED:
        # TODO: use lcm map
        project_setting.lcm_lora_scale = 1
        project_setting.apply_lcm_lora = False
        project_setting.steps = 20
        project_setting.guidance_scale = 8
    elif performance == TPerformance.QUALITY:
        project_setting.lcm_lora_scale = 1
        project_setting.apply_lcm_lora = False
        project_setting.steps = 20
        project_setting.guidance_scale = 10
    elif performance == TPerformance.SPEED_HI_RES:
        project_setting.lcm_lora_scale = 1
        project_setting.apply_lcm_lora = False
        project_setting.steps = 20
        project_setting.guidance_scale = 10
        project_setting.gradual_latent_hires_fix_map.enable = True
        width, height = resize_to_768(width, height)
    elif performance == TPerformance.EXTREME_SPEED_HI_RES:
        project_setting.lcm_lora_scale = 1
        project_setting.apply_lcm_lora = True
        project_setting.steps = 8
        project_setting.guidance_scale = 1.8
        project_setting.gradual_latent_hires_fix_map.enable = True
        width, height = resize_to_768(width, height)

    # TODO: use gpt2 optimizing?
    project_setting.head_prompt = "masterpiece, best quality"
    project_setting.tail_prompt = data.prompt
    project_setting.n_prompt = [data.negative_prompt]

    project_setting.lora_map = {lora[0]: lora[1] for lora in data.lora_items if lora[0]}
    project_setting.seed = [data.seed]
    project_setting.checkpoint = data.checkpoint
    project_setting.motion = data.motion
    project_setting.motion_lora_map = {}
    project_setting.prompt_map = {
        "0": project_setting.tail_prompt,
    }
    project_setting.output = {"format": "mp4", "fps": 8, "encode_param": {"crf": 10}}
    open(project_dir / "prompts.json", "wt", encoding="utf-8").write(
        project_setting.model_dump_json(
            indent=2,
        )
    )

    if on_config_end:
        on_config_end()

    from animatediff.cli import generate

    video_len = data.fps * data.duration
    context = 16 if video_len > 16 else 8
    overlap = context // 4
    if on_render_start:
        on_render_start()
    try:
        save_dir = generate(
            config_path=project_dir / "prompts.json",
            width=width,
            height=height,
            length=data.fps * data.duration,
            context=context,
            overlap=overlap,
            stride=0,
            repeats=1,
            device=get_torch_device(),
            force_half_vae=False,
            out_dir=project_dir / "draft",
            no_frames=False,
            save_merged=False,
        )
        if on_render_success:
            # TODO typehint
            on_render_success(save_dir / "video.mp4")
    except Exception as e:
        import traceback

        print(traceback.format_exc())
        if on_render_failed:
            on_render_failed()
    finally:
        if on_render_end:
            on_render_end()
