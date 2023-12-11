import glob
import logging
import os
import shutil
from pathlib import Path

from PIL import Image

from animatediff.ama import ama_init, ama_mask
from animatediff.consts import CONST_PROJECT_FILE, path_mgr
from animatediff.settings import get_project_setting
from animatediff.utils.tagger import get_labels
from animatediff.utils.util import extract_frames

logging.basicConfig(
    level=logging.INFO,
)


def ama_info(project):
    project_dir = path_mgr.projects / project
    input_frames_dir = project_dir / CONST_PROJECT_FILE.input_frames
    img = Image.open(input_frames_dir.joinpath("00000000.png"))
    W, H = img.size

    if W < H:
        width = 512
        height = int(512 * H / W)
    else:
        width = int(512 * W / H)
        height = 512

    length = len(glob.glob(os.path.join(input_frames_dir, "[0-9]*.png"), recursive=False))
    return {
        "length": length,
        "width": width,
        "height": height,
    }


def main():
    project = "999-video"
    # step 01
    # ama_init(project, path_mgr.repo / "temp" / "input.mp4")
    # step 02
    info = ama_info(project)
    print(info)
    ama_mask(project)
    # ama_generate(project)


if __name__ == "__main__":
    main()
