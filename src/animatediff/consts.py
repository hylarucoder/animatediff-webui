import enum
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = REPO_DIR / "models"
CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"
MOTIONS_DIR = MODELS_DIR / "motions"
CACHE_DIR = REPO_DIR / ".cache"


class PathMgr:
    config = REPO_DIR / "config"
    checkpoints = MODELS_DIR / "checkpoints"
    lcm_loras = MODELS_DIR / "lcm_loras"
    vaes = MODELS_DIR / "vaes"
    ip_adapter = MODELS_DIR / "ip_adapter"
    ip_adapter_sdxl = MODELS_DIR / "ip_adapter_sdxl"
    wd14_tagger = MODELS_DIR / "wd14_tagger"
    dwpose = MODELS_DIR / "dwpose"
    softsplat = MODELS_DIR / "softsplat"
    sam = MODELS_DIR / "sam"
    grounding_dino = MODELS_DIR / "grounding_dino"
    anime_seg = MODELS_DIR / "anime_seg"
    huggingface_pipeline = MODELS_DIR / "huggingface"
    loras = MODELS_DIR / "loras"
    motions = MODELS_DIR / "motions"
    motion_loras = MODELS_DIR / "motion_loras"
    controlnet = MODELS_DIR / "controlnet"
    projects = REPO_DIR / "projects"
    pro_painter = MODELS_DIR / "pro_painter"
    demo_prompt_json = REPO_DIR / "config/prompts/prompt_travel.json"
    repo = REPO_DIR
    rvm = MODELS_DIR / "rvm"


path_mgr = PathMgr()
# 读取项目配置文件
PROJECTS_DIR = REPO_DIR / "projects"
TEMPLATES_DIR = REPO_DIR / "templates"


class CONST_CONTROLNET:
    controlnet_tile = "controlnet_tile"
    controlnet_lineart_anime = "controlnet_lineart_anime"
    controlnet_ip2p = "controlnet_ip2p"
    controlnet_openpose = "controlnet_openpose"
    controlnet_softedge = "controlnet_softedge"
    controlnet_shuffle = "controlnet_shuffle"
    controlnet_depth = "controlnet_depth"
    controlnet_canny = "controlnet_canny"
    controlnet_inpaint = "controlnet_inpaint"
    controlnet_lineart = "controlnet_lineart"
    controlnet_mlsd = "controlnet_mlsd"
    controlnet_normalbae = "controlnet_normalbae"
    controlnet_scribble = "controlnet_scribble"
    controlnet_seg = "controlnet_seg"
    qr_code_monster_v1 = "qr_code_monster_v1"
    qr_code_monster_v2 = "qr_code_monster_v2"
    controlnet_mediapipe_face = "controlnet_mediapipe_face"
    animatediff_controlnet = "animatediff_controlnet"


class CONST_PROJECT_FILE:
    input_video = "input.mp4"
    input_frames = "input_frames"
    controlnet = "00_controlnet"
    ip_adapter = "00_ip_adapter"
    config = "prompts.json"
    draft = "prompts.json"


def ensure_project_dirs(project_dir: Path):
    for p in [
        project_dir / CONST_PROJECT_FILE.input_frames,
        project_dir / CONST_PROJECT_FILE.controlnet,
        project_dir / CONST_PROJECT_FILE.ip_adapter,
    ]:
        p.mkdir(parents=True, exist_ok=True)

    cn_dir = project_dir / CONST_PROJECT_FILE.controlnet
    for p in [
        cn_dir / CONST_CONTROLNET.controlnet_tile,
        cn_dir / CONST_CONTROLNET.controlnet_lineart_anime,
        cn_dir / CONST_CONTROLNET.controlnet_ip2p,
        cn_dir / CONST_CONTROLNET.controlnet_openpose,
        cn_dir / CONST_CONTROLNET.controlnet_softedge,
        cn_dir / CONST_CONTROLNET.controlnet_shuffle,
        cn_dir / CONST_CONTROLNET.controlnet_depth,
        cn_dir / CONST_CONTROLNET.controlnet_canny,
        cn_dir / CONST_CONTROLNET.controlnet_inpaint,
        cn_dir / CONST_CONTROLNET.controlnet_lineart,
        cn_dir / CONST_CONTROLNET.controlnet_mlsd,
        cn_dir / CONST_CONTROLNET.controlnet_normalbae,
        cn_dir / CONST_CONTROLNET.controlnet_scribble,
        cn_dir / CONST_CONTROLNET.controlnet_seg,
        cn_dir / CONST_CONTROLNET.qr_code_monster_v1,
        cn_dir / CONST_CONTROLNET.qr_code_monster_v2,
        cn_dir / CONST_CONTROLNET.controlnet_mediapipe_face,
        cn_dir / CONST_CONTROLNET.animatediff_controlnet,
    ]:
        p.mkdir(parents=True, exist_ok=True)
