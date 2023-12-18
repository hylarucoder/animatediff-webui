import dataclasses
from contextvars import ContextVar

import tqdm
from werkzeug.local import Local, LocalProxy

from animatediff.adw.schema import TPipeline, TStatusEnum


class ProgressBar:
    """two level depth."""

    def __init__(self):
        self.pbar = tqdm.tqdm(desc="Video Rendering...", total=100)
        self.pbar_config = tqdm.tqdm(desc="Step 01/08: Checking Configuration", total=100)
        self.pbar_preprocess_image = tqdm.tqdm(
            desc="Step 02/08: Preprocessing Images Controlnet & IPAdapter", total=100
        )
        self.pbar_image_2_image = tqdm.tqdm(desc="Step 03/08: Preprocessing Img 2 Img", total=100)
        self.pbar_load_model = tqdm.tqdm(
            desc="Step 04/08: Load Models: Ckpt, tokenizer, text encoder, vae, unet, Controlnet", total=100
        )
        self.pbar_animate = tqdm.tqdm(desc="Step 05/08: Animating ...", total=100)
        self.pbar_unload_models = tqdm.tqdm(desc="Step 06/08: Unload Controlnet Models", total=100)
        self.pbar_make_video = tqdm.tqdm(desc="Step 07/08: Make Video ...", total=100)

    def update(self, n):
        self.pbar.update(n)
        if self.bg_task:
            self.bg_task.completed = n

    def init_pbar(self, task_id):
        self.bg_task = get_pipeline_by_id(task_id)

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


@dataclasses.dataclass
class GPipeline:
    pid: int
    pipeline: TPipeline
    progress_bar: ProgressBar | None


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
