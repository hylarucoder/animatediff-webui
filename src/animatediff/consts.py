from pathlib import Path

REPO_DIR = Path(__file__).parent.parent.parent
MODELS_DIR = REPO_DIR / "models"
CHECKPOINTS_DIR = MODELS_DIR / "checkpoints"
MOTIONS_DIR = MODELS_DIR / "motions"
CACHE_DIR = REPO_DIR / ".cache"


class PathMgr:
    checkpoints = MODELS_DIR / "checkpoints"
    vaes = MODELS_DIR / "vaes"
    ip_adapter = MODELS_DIR / "ip_adapter"
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


path_mgr = PathMgr()
# 读取项目配置文件
PROJECTS_DIR = REPO_DIR / "projects"
TEMPLATES_DIR = REPO_DIR / "templates"
