import dataclasses
import functools
import threading
from typing import Any, Callable

import tqdm
from werkzeug.local import Local

from animatediff.adw.schema import TPipeline, TStatusEnum


class ProgressBar:

    """two level depth."""

    def __init__(self):
        self.pbar = tqdm.tqdm(desc="Video Rendering...", total=100)
        self.pbar_config = tqdm.tqdm(desc="S01: Checking Configuration", total=100)
        self.pbar_preprocess_image = tqdm.tqdm(
            desc="S02: Preprocessing Images Controlnet & IPAdapter", total=100
        )
        self.pbar_image_2_image = tqdm.tqdm(desc="S03: Preprocessing Img 2 Img", total=100)
        self.pbar_load_model = tqdm.tqdm(
            desc="S04: Load Models: Ckpt, tokenizer, text encoder, vae, unet, Controlnet", total=100
        )
        self.pbar_animate = tqdm.tqdm(desc="S05: Animating ...", total=100)
        self.pbar_unload_models = tqdm.tqdm(desc="S06: Unload Controlnet Models", total=100)
        self.pbar_make_video = tqdm.tqdm(desc="S07: Make Video ...", total=100)

    def update(self, n):
        self.pbar.update(n)

    @property
    def status(self):
        return [
            {
                "description": t.description,
                "completed": t.completed,
                "total": t.total,
            }
            for t in [
                self.pbar_config,
                self.pbar_preprocess_image,
                self.pbar_image_2_image,
                self.pbar_load_model,
                self.pbar_animate,
                self.pbar_unload_models,
                self.pbar_make_video,
            ]
        ]


class InterruptProcessingException(Exception):
    pass


@dataclasses.dataclass
class GPipeline:
    pid: int
    pipeline: TPipeline
    progress_bar: ProgressBar | None
    interrupt_processing = False
    interrupt_processing_mutex = threading.RLock()

    def interrupt_current_processing(self, value=True):
        with self.interrupt_processing_mutex:
            self.interrupt_processing = value

    def processing_interrupted(self):
        with self.interrupt_processing_mutex:
            return self.interrupt_processing

    def throw_exception_if_processing_interrupted(self):
        with self.interrupt_processing_mutex:
            if self.interrupt_processing:
                self.interrupt_processing = False
                raise InterruptProcessingException()


def check_interrupted(func: Callable) -> Callable:
    """装饰器，用于检查处理是否被中断，并在中断时抛出异常。
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        g.pipeline.throw_exception_if_processing_interrupted()
        return func(self, *args, **kwargs)

    return wrapper


g = Local()

pipeline_queue: list[GPipeline] = []


def set_global_pipeline(pid: int) -> GPipeline:
    pipeline = GPipeline(
        pid,
        TPipeline(
            pid=pid,
            status=TStatusEnum.PENDING,
        ),
        None,
    )
    pipeline_queue.append(pipeline)

    g.pipeline = pipeline
    return pipeline


def get_global_pipeline() -> GPipeline:
    return g.pipeline


def get_pipeline_by_id(pid: int):
    for task in pipeline_queue:
        if task.pid == pid:
            return task
    return None
