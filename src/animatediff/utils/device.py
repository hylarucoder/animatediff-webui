import logging
from functools import lru_cache
from math import ceil
from typing import Union

import torch

from animatediff.utils.torch_compact import auto_scale_float32, is_macos

logger = logging.getLogger(__name__)


def device_info_str(device: torch.device) -> str:
    device_info = torch.cuda.get_device_properties(device)
    return (
        f"{device_info.name} {ceil(device_info.total_memory / 1024 ** 3)}GB, "
        + f"CC {device_info.major}.{device_info.minor}, {device_info.multi_processor_count} SM(s)"
    )


@lru_cache(maxsize=4)
def supports_bfloat16(device: Union[str, torch.device]) -> bool:
    """A non-exhaustive check for bfloat16 support on a given device.
    Weird that torch doesn't have a global function for this. If your device
    does support bfloat16 and it's not listed here, go ahead and add it.
    """
    device = torch.device(device)  # make sure device is a torch.device
    match device.type:
        case "cpu":
            ret = False
        case "cuda":
            with device:
                ret = torch.cuda.is_bf16_supported()
        case "xla":
            ret = True
        case "mps":
            # ret = True
            # TODO: Does MPS support bfloat16?
            ret = False
        case _:
            ret = False
    return ret


@lru_cache(maxsize=4)
def maybe_bfloat16(
    device: Union[str, torch.device],
    fallback: torch.dtype = torch.float32,
) -> torch.dtype:
    """Returns torch.bfloat16 if available, otherwise the fallback dtype (default float32)."""
    device = torch.device(device)  # make sure device is a torch.device
    return torch.bfloat16 if supports_bfloat16(device) else fallback


def dtype_for_model(model: str, device: torch.device) -> torch.dtype:
    match model:
        case "unet":
            return torch.float32 if device.type == "cpu" else torch.float16
        case "tenc":
            return torch.float32 if device.type == "cpu" else torch.float16
        case "vae":
            return maybe_bfloat16(device, fallback=torch.float32)

        case unknown:
            raise ValueError(f"Invalid model {unknown}")


def get_model_dtypes(
    device: Union[str, torch.device],
) -> tuple[torch.dtype, torch.dtype, torch.dtype]:
    device = torch.device(device)  # make sure device is a torch.device
    unet_dtype = dtype_for_model("unet", device)
    tenc_dtype = dtype_for_model("tenc", device)
    vae_dtype = dtype_for_model("vae", device)

    if device.type == "cpu":
        logger.warning("Device explicitly set to CPU, will run everything in fp32")
        logger.warning("This is likely to be *incredibly* slow, but I don't tell you how to live.")

    logger.info(f"Selected data types: {unet_dtype=}, {tenc_dtype=}, {vae_dtype=}")
    return unet_dtype, tenc_dtype, vae_dtype


def get_memory_format(device: Union[str, torch.device]) -> torch.memory_format:
    device = torch.device(device)  # make sure device is a torch.device
    # if we have a cuda device
    if device.type == "cuda":
        device_info = torch.cuda.get_device_properties(device)
        # Volta and newer seem to like channels_last. This will probably bite me on TU11x cards.
        if device_info.major >= 7:
            ret = torch.channels_last
        else:
            ret = torch.contiguous_format
    elif device.type == "xpu":
        # Intel ARC GPUs/XPUs like channels_last
        ret = torch.channels_last
    else:
        # TODO: Does MPS like channels_last? do other devices?
        ret = torch.contiguous_format
    if ret == torch.channels_last:
        logger.info("Using channels_last memory format for UNet and VAE")
    return ret
