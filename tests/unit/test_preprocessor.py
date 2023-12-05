import pytest

from animatediff.generate import get_preprocessor
from animatediff.schema import TPreprocessor
from tests.utils.path import open_test_image


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "dwpose",
        "openpose_full",
        "openpose_face",
    ],
)
def test_openpose(preprocessor_str):
    processor = get_preprocessor("controlnet_openpose", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "canny",
        # ("tile", "tile_resample"),
    ],
)
def test_canny(preprocessor_str):
    processor = get_preprocessor("controlnet_canny", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "depth_midas",
        # ("tile", "tile_resample"),
    ],
)
def test_depth(preprocessor_str):
    processor = get_preprocessor("controlnet_depth", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "lineart_realistic",
    ],
)
def test_lineart(preprocessor_str):
    processor = get_preprocessor("controlnet_lineart", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "lineart_anime",
    ],
)
def test_lineart_anime(preprocessor_str):
    processor = get_preprocessor("controlnet_lineart_anime", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "softedge_hedsafe",
    ],
)
def test_lineart_anime(preprocessor_str):
    processor = get_preprocessor("controlnet_softedge", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "softedge_hedsafe",
    ],
)
def test_shuffle(preprocessor_str):
    processor = get_preprocessor("controlnet_shuffle", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "mlsd",
    ],
)
def test_mlsd(preprocessor_str):
    processor = get_preprocessor("controlnet_mlsd", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "normal_bae",
    ],
)
def test_normalbae(preprocessor_str):
    processor = get_preprocessor("controlnet_normalbae", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "scribble_pidsafe",
    ],
)
def test_scribble(preprocessor_str):
    processor = get_preprocessor("controlnet_scribble", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "upernet_seg",
    ],
)
def test_seg(preprocessor_str):
    processor = get_preprocessor("controlnet_seg", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "mediapipe_face",
    ],
)
def test_mediapipe_face(preprocessor_str):
    processor = get_preprocessor("controlnet_mediapipe_face", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "qr_code_monster_v1",
    ],
)
def test_qr_code_monster_v1(preprocessor_str):
    processor = get_preprocessor("qr_code_monster_v1", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))


@pytest.mark.parametrize(
    "preprocessor_str",
    [
        None,
        "qr_code_monster_v2",
    ],
)
def test_qr_code_monster_v2(preprocessor_str):
    processor = get_preprocessor("qr_code_monster_v2", TPreprocessor(type=preprocessor_str))
    i = processor(open_test_image("animate_portrait.jpeg"))
