import glob
import os

from animatediff.consts import path_mgr
from animatediff.utils.mask import create_bg, create_fg
from animatediff.utils.util import extract_frames

basedir = path_mgr.motions / "./../../resources/R01_jinitaimei"
frame_dir = basedir / "00_frames"
input_dir = basedir / "input.mp4"

fg_dir = basedir / "00_fg"
fg_mask_dir = basedir / "00_mask" / "fg"

bg_dir = basedir / "00_bg"
bg_mask_dir = basedir / "00_bg_mask"

bg_inpaint_dir = basedir / "00_bg"
bg_inpaint_mask_dir = basedir / "00_mask" / "bg"


def extract_():
    extract_frames(
        input_dir,
        fps=8,
        out_dir=frame_dir,
        aspect_ratio=-1,
        duration=20,
        offset=0,
    )


def create_fg_():
    ...


def create_bg_():
    ...


if __name__ == "__main__":
    # extract_frames(
    #     input_dir,
    #     fps=8,
    #     out_dir=frame_dir,
    #     aspect_ratio=-1,
    #     duration=23,
    #     offset=0,
    # )
    stylize_frame = sorted(glob.glob(os.path.join(frame_dir, "[0-9]*.png"), recursive=False))
    print(stylize_frame, frame_dir)
    frame_len = len(stylize_frame)
    masked_area = [None for f in range(frame_len)]
    masked_area = create_fg(
        mask_token="person and basketball",
        frame_dir=frame_dir,
        output_dir=fg_dir,
        output_mask_dir=fg_mask_dir,
        masked_area_list=masked_area,
        box_threshold=0.3,
        text_threshold=0.25,
        mask_padding=100,
        sam_checkpoint=path_mgr.sam / "sam_hq_vit_h.pth",
        bg_color=(0, 255, 0),
        device="cuda",
    )
    low_vram = True
    create_bg(
        frame_dir,
        bg_inpaint_dir,
        masked_area,
        use_half=True,
        raft_iter=20,
        subvideo_length=80 if not low_vram else 50,
        neighbor_length=10 if not low_vram else 8,
        ref_stride=10 if not low_vram else 8,
        low_vram=low_vram,
    )

    # import os
    # from PIL import Image
    # import numpy as np
    #
    # # 输入和输出目录
    #
    # # 遍历输入目录中的每一个文件
    # for filename in os.listdir(fg_mask_dir):
    #     if filename.endswith(".png"):
    #         input_path = os.path.join(fg_mask_dir, filename)
    #         output_path = os.path.join(bg_mask_dir, filename)
    #
    #         img = Image.open(input_path).convert("L")
    #         img = Image.fromarray(255 - np.array(img))
    #         img.save(output_path)
