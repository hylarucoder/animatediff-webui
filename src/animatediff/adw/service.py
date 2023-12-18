import logging

import pydantic as pt

from animatediff.adw.contrib import PtBaseModel
from animatediff.adw.schema import TCameraControl, TPerformance, TPromptBlock, TStatusEnum, default_prompt_points
from animatediff.consts import path_mgr
from animatediff.schema import TProjectSetting
from animatediff.globals import g, get_pipeline_by_id, ProgressBar
from animatediff.utils.torch_compact import get_torch_device
from animatediff.utils.util import read_json

logger = logging.getLogger(__name__)


def get_projects():
    return list(sorted([_.name for _ in path_mgr.projects.iterdir() if _.is_dir()]))


def group_by_n(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def lora_arr():
    return [TLoraInput(name=None, weight=0.7) for _ in range(5)]


class TLoraInput(PtBaseModel):
    name: str | None = ""
    weight: float = 0.7


class TParamsRenderVideo(PtBaseModel):
    project: str
    performance: TPerformance = TPerformance.SPEED
    aspect_ratio: str = "9:16"
    prompt: str = "masterpiece, best quality"
    prompt_blocks: list[TPromptBlock] = pt.Field(default_factory=default_prompt_points)
    negative_prompt: str = "(worst quality, low quality:1.4),nudity,simple background,border,text, patreon,bed,bedroom,white background,((monochrome)),sketch,(pink body:1.4),7 arms,8 arms,4 arms"
    high_res: bool = False
    fps: int = 8
    duration: int = 4
    camera_control: TCameraControl = pt.Field(default_factory=lambda: TCameraControl())
    seed: int = -1
    checkpoint: str = "majicmix/majicmixRealistic_v7.safetensors"
    loras: list[TLoraInput] = pt.Field(default_factory=lora_arr)


def get_width_height(aspect_ratio: str):
    a = {
        "16:9": "768x432",
        "4:3": "768x576",
        "1:1": "600x600",
        "3:4": "576x768",
        "9:16": "432x768",
    }[aspect_ratio]

    w, h = a.split("x")
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


def sub_render_video(data, task_id):
    pipeline = get_pipeline_by_id(task_id)
    g.pipeline = pipeline
    pbar = ProgressBar()
    pipeline.progress_bar = pbar

    def on_config_start():
        pbar.init_pbar(task_id)
        pipeline.pipeline.status = TStatusEnum.RUNNING
        ...

    def on_config_end():
        pbar.pbar_config.update(100)

    def on_render_start():
        pbar.update(10)
        ...

    def on_render_success(path):
        pipeline.pipeline.video_path = path
        pipeline.pipeline.status = TStatusEnum.SUCCESS
        ...

    def on_render_failed():
        pipeline.pipeline.status = TStatusEnum.ERROR

    def on_render_end():
        ...

    do_render_video(
        data=data,
        on_config_start=on_config_start,
        on_config_end=on_config_end,
        on_render_start=on_render_start,
        on_render_success=on_render_success,
        on_render_failed=on_render_failed,
        on_render_end=on_render_end,
    )


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
    width, height = get_width_height(data.aspect_ratio)
    logger.info(f"{width=} {height=} {data.aspect_ratio}")
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
    elif performance == TPerformance.EXTREME_SPEED:
        project_setting.lcm_lora_scale = 1
        project_setting.apply_lcm_lora = True
        project_setting.steps = 8
        project_setting.guidance_scale = 1.8

    if data.high_res:
        project_setting.gradual_latent_hires_fix_map.enable = True
        width, height = resize_to_768(width, height)

    # TODO: use gpt2 optimizing?
    project_setting.head_prompt = "masterpiece, best quality"
    project_setting.tail_prompt = data.prompt
    project_setting.n_prompt = [data.negative_prompt]

    project_setting.lora_map = {lora.name: lora.weight for lora in data.loras if lora.name}
    project_setting.seed = [data.seed]
    project_setting.checkpoint = data.checkpoint
    project_setting.motion = "mm_sd_v15_v2.ckpt"
    camera_control = data.camera_control

    def filter_zero_dict(d):
        return {k: v for k, v in d.items() if round(v, 1)}

    project_setting.motion_lora_map = filter_zero_dict(
        {
            "v2_lora_PanLeft.ckpt": camera_control.pan_left,
            "v2_lora_PanRight.ckpt": camera_control.pan_right,
            "v2_lora_RollingAnticlockwise.ckpt": camera_control.rolling_anticlockwise,
            "v2_lora_RollingClockwise.ckpt": camera_control.rolling_clockwise,
            "v2_lora_TiltDown.ckpt": camera_control.tile_down,
            "v2_lora_TiltUp.ckpt": camera_control.tile_up,
            "v2_lora_ZoomIn.ckpt": camera_control.zoom_in,
            "v2_lora_ZoomOut.ckpt": camera_control.zoom_out,
        }
    )

    project_setting.prompt_map = {p.start: p.prompt for p in data.prompt_blocks}
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
    # context = 8 if video_len > 8 else 8
    if on_render_start:
        on_render_start()
    try:
        save_dir = generate(
            config_path=project_dir / "prompts.json",
            width=width,
            height=height,
            length=data.fps * data.duration,
            context=context,
            repeats=1,
            device=get_torch_device(),
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
