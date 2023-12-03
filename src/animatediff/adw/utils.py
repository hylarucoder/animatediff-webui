from pathlib import Path


def get_models_endswith(d: Path, endswith="safetensors"):
    all_files = list(d.glob("**/*.*"))
    # 创建一个映射，将每个图片文件的基本名称映射到其相对路径
    image_map = {
        f.stem: str(f) for f in all_files
        if f.is_file() and f.suffix.lstrip('.').lower() in {"png", "webp", "jpg", "jpeg"}
    }

    # 对于每个模型，获取其名字（不包括扩展名），然后在映射中查找对应的图片
    models = [
        {
            "name": str(f.relative_to(d)),
            "thumbnail": image_map.get(f.stem)  # 如果没有找到对应的图片，这将返回 None
        }
        for f in all_files
        if f.is_file() and f.name.endswith(endswith)
    ]
    models.sort(key=lambda x: x["name"])
    return models
