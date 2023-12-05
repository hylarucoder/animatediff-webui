from PIL import Image

from animatediff.consts import path_mgr


def open_test_image(path: str):
    return Image.open(path_mgr.repo / "tests/assets" / path)
