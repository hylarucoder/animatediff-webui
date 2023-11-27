import json
import logging
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from pydantic import BaseConfig, Field
from pydantic.v1.env_settings import SettingsSourceCallable
from pydantic_settings import BaseSettings, EnvSettingsSource, InitSettingsSource, SecretsSettingsSource

from animatediff import get_dir
from animatediff.schedulers import DiffusionScheduler
from animatediff.schema import TProjectSetting
from animatediff.utils.util import read_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CKPT_EXTENSIONS = [".pt", ".ckpt", ".pth", ".safetensors"]


class InferenceConfig(BaseSettings):
    unet_additional_kwargs: dict[str, Any]
    noise_scheduler_kwargs: dict[str, Any]


def get_infer_config(
    is_v2: bool,
    is_sdxl: bool,
) -> InferenceConfig:
    config_path: Path = get_dir("config").joinpath(
        "inference/default.json" if not is_v2 else "inference/motion_v2.json"
    )

    if is_sdxl:
        config_path = get_dir("config").joinpath("inference/motion_sdxl.json")

    settings = InferenceConfig(**read_json(config_path))
    return settings


class ModelConfig(BaseSettings):
    name: str
    checkpoint: Path
    apply_lcm_lora: bool = Field(False)
    lcm_lora_scale: float = Field(1.0)
    vae: str = ""  # Path to the model
    motion: Path = Field(...)  # Path to the motion module
    compile: bool = Field(False)  # whether to compile the model with TorchDynamo
    tensor_interpolation_slerp: bool = Field(False)
    seed: list[int] = Field([])  # Seed(s) for the random number generators
    scheduler: DiffusionScheduler = Field(DiffusionScheduler.k_dpmpp_2m)  # Scheduler to use
    steps: int = 25  # Number of inference steps to run
    guidance_scale: float = 7.5  # CFG scale to use
    unet_batch_size: int = 1
    clip_skip: int = 1  # skip the last N-1 layers of the CLIP text encoder
    prompt_fixed_ratio: float = 0.5
    head_prompt: str = ""
    prompt_map: dict[str, str] = Field({})
    tail_prompt: str = ""
    n_prompt: list[str] = Field([])  # Anti-prompt(s) to use
    is_single_prompt_mode: bool = Field(False)
    lora_map: dict[str, Any] = Field({})
    motion_lora_map: dict[str, float] = Field({})
    ip_adapter_map: dict[str, Any] = Field({})
    img2img_map: dict[str, Any] = Field({})
    region_map: dict[str, Any] = Field({})
    controlnet_map: dict[str, Any] = Field({})
    upscale_config: dict[str, Any] = Field({})
    stylize_config: dict[str, Any] = Field({})
    output: dict[str, Any] = Field({})
    result: dict[str, Any] = Field({})

    @property
    def save_name(self):
        return f"{self.name.lower()}-{self.checkpoint.stem.lower()}"


def get_model_config_old(config_path: Path) -> ModelConfig:
    d = read_json(config_path)
    settings = ModelConfig(**d)
    return settings


def get_project_setting(config_path: Path) -> TProjectSetting:
    d = read_json(config_path)
    settings = TProjectSetting(**d)
    return settings
