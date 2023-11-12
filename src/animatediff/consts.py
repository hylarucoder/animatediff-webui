from pathlib import Path

REPO_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = REPO_DIR / "models"
CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"
LORAS_DIR = MODELS_DIR / "loras"
MOTIONS_DIR = MODELS_DIR / "motions"
MOTION_LORAS_DIR = MODELS_DIR / "motion-loras"
VAES_DIR = MODELS_DIR / "vaes"
CACHE_DIR = REPO_DIR / ".cache"


class PathMgr:
    ip_adapter = MODELS_DIR / "ip_adapter"
    wd14_tagger = MODELS_DIR / "wd14_tagger"
    dwpose = MODELS_DIR / "dwpose"
    softsplat = MODELS_DIR / "softsplat"
    sam = MODELS_DIR / "sam"
    grounding_dino = MODELS_DIR / "grounding_dino"
    anime_seg = MODELS_DIR / "anime_seg"
    motions = MODELS_DIR / "motions"
    huggingface_pipeline = MODELS_DIR / "huggingface"
    loras = MODELS_DIR / "loras"


path_mgr = PathMgr()
# 读取项目配置文件
PROJECTS_DIR = REPO_DIR / "projects"
TEMPLATES_DIR = REPO_DIR / "templates"
