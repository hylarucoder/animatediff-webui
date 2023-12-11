import os

import torch


def is_macos():
    return os.name == "posix" and os.uname().sysname == "Darwin"


def auto_scale_float32(h):
    if not is_macos():
        return h
    return h.to(torch.float32)


def auto_half(h):
    if not is_macos():
        return h
    return h.half()


def get_execution_providers():
    device = get_torch_device()
    if is_macos:
        return ["CoreMLExecutionProvider", "CPUExecutionProvider"]
    if device == "cuda":
        return ["CUDAExecutionProvider", "CPUExecutionProvider"]
    return ["CPUExecutionProvider"]


def get_torch_device():
    if is_macos() and torch.backends.mps.is_available() and torch.backends.mps.is_built():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
