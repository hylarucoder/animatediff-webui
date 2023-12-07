import logging
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings

from animatediff import get_dir
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


def get_project_setting(config_path: Path) -> TProjectSetting:
    d = read_json(config_path)
    settings = TProjectSetting(**d)
    return settings
