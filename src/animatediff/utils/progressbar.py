import gradio as gr
from tqdm.rich import tqdm


class ProgressBar:

    """two level depth"""

    main_pgr: gr.Progress | None = None

    # 当前步骤

    def __init__(self):
        ...

    def set_pgr(self, _pgr: gr.Progress):
        self.main_pgr = _pgr

    def tqdm(self, *args, **kwargs):
        if self.main_pgr is None:
            return tqdm(*args, **kwargs)
        return self.main_pgr.tqdm(*args, **kwargs)

    def update_phrase(self, value, desc=None):
        if self.main_pgr is None:
            return
        self.main_pgr(value / 100, desc=desc)

    def __call__(self, value, desc=None):
        if self.main_pgr is None:
            return
        self.main_pgr(value, desc)


pgr = ProgressBar()
