import enum

import pydantic as pt

from animatediff.adw.contrib import PtBaseModel


class TStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class TSubtask(PtBaseModel):
    description: str = ""
    completed: int = 0
    total: int = 100
    status: TStatusEnum = TStatusEnum.PENDING


class TTask(PtBaseModel):
    task_id: int
    status: TStatusEnum = TStatusEnum.PENDING
    completed: int = 0
    total: int = 100
    subtasks: list[TSubtask] = pt.Field(default_factory=list)
    video_path: str = ""


def lora_arr():
    return [[None, 0.7] for _ in range(5)]


class TPerformance(str, enum.Enum):
    SPEED = "SPEED"
    QUALITY = "QUALITY"
    EXTREME_SPEED = "EXTREME_SPEED"


class TAspectRatio(str, enum.Enum):
    AR_16_9 = "16:9"
    AR_4_3 = "4:3"
    AR_1_1 = "1:1"
    AR_3_4 = "3:4"
    AR_9_16 = "9:16"


class TPromptBlock(PtBaseModel):
    # ms
    start: int = 0
    prompt: str = ""


def default_prompt_points():
    return [
        TPromptBlock(start=0, duration=125, prompt="walk"),
        TPromptBlock(start=1000, duration=125, prompt="run"),
        TPromptBlock(start=2000, duration=125, prompt="sit"),
        TPromptBlock(start=3000, duration=125, prompt="sunny"),
        TPromptBlock(start=4000, duration=125, prompt="sit"),
    ]


class TCameraControl(PtBaseModel):
    pan_left: float = 0
    pan_right: float = 0
    rolling_anticlockwise: float = 0
    rolling_clockwise: float = 0
    tile_down: float = 0
    tile_up: float = 0
    zoom_in: float = 0
    zoom_out: float = 0


class TPreset(PtBaseModel):
    name: str
    performance: TPerformance = TPerformance.SPEED
    aspect_ratio: TAspectRatio = TAspectRatio.AR_9_16
    high_res: bool = False
    head_prompt: str = "masterpiece, best quality"
    prompt: str = "1girl"
    negative_prompt: str = "(worst quality, low quality:1.4),nudity,simple background,border,text, patreon,bed,bedroom,white background,((monochrome)),sketch,(pink body:1.4),7 arms,8 arms,4 arms"
    prompt_blocks: list[TPromptBlock] = pt.Field(default_factory=default_prompt_points)

    checkpoint: str = r"dynamicwang\AWPainting_v1.2.safetensors"
    loras: list[list] = pt.Field(default_factory=lora_arr)
    camera_control: TCameraControl = pt.Field(default_factory=lambda: TCameraControl())

    fps: int = 8
    duration: int = 2
    seed: int = -1

    lcm: bool = False
    sampler: str = "k_dpmpp_sde"
    step: int = 20
    cfg: float = 7
