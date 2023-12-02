import pydantic as pt
import enum


class TStatusEnum(str, enum.Enum):
    pending = "pending"
    running = "running"
    error = "error"
    success = "success"


class TSubtask(pt.BaseModel):
    description: str = ""
    completed: int = 0
    total: int = 100
    status: TStatusEnum = TStatusEnum.pending


class TTask(pt.BaseModel):
    task_id: int
    status: TStatusEnum = TStatusEnum.pending
    completed: int = 0
    total: int = 100
    subtasks: list[TSubtask] = pt.Field(default_factory=list)
    video_path: str = ""


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
    prompt: str = ""
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
