import tqdm


class ProgressBar:

    """two level depth."""

    pbar: tqdm.tqdm | None = None

    # 当前步骤

    def __init__(self):
        self.bg_task = None
        self.pbar_make_video = None
        self.pbar_unload_models = None
        self.pbar_animate = None
        self.pbar_load_model = None
        self.pbar_image_2_image = None
        self.pbar_config = None
        self.pbar_preprocess_image = None

    def init_pbar(self, task_id):
        from animatediff.adw.service import get_task_by_id

        self.bg_task = get_task_by_id(task_id)
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

    @property
    def status(self):
        return []
        # return [
        #     {
        #         "description": t.description,
        #         "completed": t.completed,
        #         "total": t.total,
        #     } for t in self.pbar.total
        # ] if self.pbar else []


pbar = ProgressBar()
