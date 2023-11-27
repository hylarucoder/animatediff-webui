import os

import torch


def is_macos():
    return os.name == "posix" and os.uname().sysname == "Darwin"


def get_torch_device():
    if is_macos():
        # TODO fix bf16 "mps"
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
