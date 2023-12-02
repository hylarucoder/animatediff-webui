import pydantic as pt
from rich.progress import Progress

from animatediff.adw.schema import TStatusEnum, TTask
from animatediff.consts import path_mgr
from animatediff.settings import ModelConfig
from animatediff.utils.progressbar import pgr
from animatediff.utils.util import read_json

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
        yield l[i: i + n]


def lora_arr():
    return [
        [
            None, 0.7
        ] for _ in range(5)
    ]


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


def do_render_video(data: TParams, task_id):
    with Progress() as progress:
        pgr.set_pgr(progress, task_id)
        bg_task = get_task_by_id(task_id)
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

        # TODO: use gpt2 optimizing?
        global_config.head_prompt = "masterpiece, best quality"
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
            bg_task.video_path = save_dir / "video.mp4"
            bg_task.status = TStatusEnum.success
        except Exception as e:
            print(e)
