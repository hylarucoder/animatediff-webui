from rich.progress import Progress


class ProgressBar:
    """two level depth"""

    _pgr: Progress | None = None

    # 当前步骤

    def __init__(self):
        ...

    def set_pgr(self, _pgr: Progress):
        self._pgr = _pgr
        self.task_id_main = _pgr.add_task("Video Rendering...", total=100)
        self.task_id_config = _pgr.add_task("Step 01/08: Checking Configuration", total=100)
        self.task_id_preprocessing_image = _pgr.add_task("Step 02/08: Preprocessing Images Controlnet & IPAdapter",
                                                         total=100)
        self.task_id_image_2_image = _pgr.add_task("Step 03/08: Preprocessing Img 2 Img", total=100)
        self.task_id_load_model = _pgr.add_task(
            "Step 04/08: Load Models: Ckpt, tokenizer, text encoder, vae, unet, Controlnet", total=100)
        self.task_id_animate = _pgr.add_task("Step 05/08: Animating ...", total=100)
        self.task_id_unload_models = _pgr.add_task("Step 06/08: Unload Controlnet Models", total=100)
        self.task_id_make_video = _pgr.add_task("Step 07/08: Make Video ...", total=100)

    def update(self, task_id, advance=1):
        if self._pgr is None:
            return
        self._pgr.update(task_id, advance=advance)

    @property
    def status(self):
        return [
            {
                "description": t.description,
                "completed": t.completed,
                "total": t.total,
            } for t in self._pgr.tasks
        ] if self._pgr else []


pgr = ProgressBar()
