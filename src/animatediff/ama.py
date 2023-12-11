import glob
import json
import logging
import os.path
import shutil
from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import torch
import typer
from PIL import Image

from animatediff import get_dir
from animatediff.consts import CONST_CONTROLNET, CONST_PROJECT_FILE, ensure_project_dirs, path_mgr
from animatediff.schema import TIPAdapterMap, TProjectSetting
from animatediff.settings import get_project_setting
from animatediff.utils.tagger import get_labels
from animatediff.utils.torch_compact import get_torch_device
from animatediff.utils.util import (
    extract_frames,
    prepare_anime_seg,
    prepare_groundingDINO,
    prepare_propainter,
    prepare_sam_hq,
    read_json,
)

logger = logging.getLogger(__name__)

ama: typer.Typer = typer.Typer(
    name="ama",
    context_settings=dict(help_option_names=["-h", "--help"]),
    rich_markup_mode="rich",
    pretty_exceptions_show_locals=False,
    help="animate anyone",
)

data_dir = get_dir("data")


@ama.command(no_args_is_help=True)
def ama_init(
    project,
    input_video: Path,
    aspect_ratio=-1,
    size_of_short_edge=512,
    predicte_interval: int = 1,
    general_threshold=0.35,
    character_threshold=0.85,
    is_img2img=False,
):
    # 1. 抽帧, 并且裁剪到 512x768 这种
    # 1.2 适当大点呢? + hires 呢?
    # 2. 生成 mask
    # 3. 生成 bg
    # 4. 生成 prompt.json
    # 5. 生成 draft + compose 版本
    """Create a config file for video stylization."""
    logger.info(f"{aspect_ratio=} {size_of_short_edge=} {predicte_interval=}")
    logger.info(f"{general_threshold=} {character_threshold=}")
    project_dir = path_mgr.projects / project
    ensure_project_dirs(project_dir)
    input_video_path = project_dir / CONST_PROJECT_FILE.input_video
    shutil.copy(input_video, input_video_path)
    input_frames_dir = project_dir / CONST_PROJECT_FILE.input_frames
    controlnet_dir = project_dir / CONST_PROJECT_FILE.controlnet
    ip_adapter_dir = project_dir / CONST_PROJECT_FILE.ip_adapter

    project_setting = TProjectSetting(**read_json(path_mgr.demo_prompt_json))

    fps = 16
    extract_frames(input_video_path, fps, input_frames_dir, aspect_ratio, -1, 0, size_of_short_edge, False)
    for p in [
        controlnet_dir / CONST_CONTROLNET.controlnet_tile,
        controlnet_dir / CONST_CONTROLNET.controlnet_ip2p,
    ]:
        shutil.copytree(input_frames_dir, p, dirs_exist_ok=True)

    black_list = []

    project_setting.prompt_map = get_labels(
        frame_dir=input_frames_dir,
        interval=predicte_interval,
        general_threshold=general_threshold,
        character_threshold=character_threshold,
        ignore_tokens=black_list,
        with_confidence=False,
        is_danbooru_format=False,
        is_cpu=False,
    )

    project_setting.head_prompt = ""
    project_setting.tail_prompt = ""
    project_setting.controlnet_map.input_image_dir = CONST_PROJECT_FILE.controlnet
    project_setting.controlnet_map.is_loop = False

    project_setting.lora_map = {}
    project_setting.motion_lora_map = {}

    project_setting.controlnet_map.max_samples_on_vram = 0
    project_setting.controlnet_map.max_models_on_vram = 0

    if not is_img2img:
        project_setting.controlnet_map.controlnet_tile.control_scale_list = []
    else:
        project_setting.controlnet_map.controlnet_openpose.control_scale_list = []
    project_setting.controlnet_map.controlnet_ip2p.controlnet_conditioning_scale = 0.5
    project_setting.controlnet_map.controlnet_ip2p.control_scale_list = []

    for cn_type, cn in project_setting.controlnet_map.controlnets:
        if cn_type == "controlnet_ref":
            continue
        cn.control_scale_list = []

    project_setting.ip_adapter_map = TIPAdapterMap(
        **{
            "enable": True,
            "input_image_dir": CONST_PROJECT_FILE.ip_adapter,
            "prompt_fixed_ratio": 0.5,
            "save_input_image": True,
            "resized_to_square": False,
            "scale": 0.5,
            "is_full_face": False,
            "is_plus_face": True,
            "is_plus": True,
            "is_light": False,
        }
    )

    project_setting.img2img_map = {
        "enable": is_img2img,
        "init_img_dir": CONST_PROJECT_FILE.input_frames,
        "save_init_image": True,
        "denoising_strength": 0.7,
    }

    project_setting.region_map = {}

    project_setting.output = {"format": "mp4", "fps": fps, "encode_param": {"crf": 10}}

    config_org = project_dir / "prompts.json"
    open(config_org, "wt", encoding="utf-8").write(
        project_setting.model_dump_json(
            indent=2,
        )
    )


def do_render(config_org):
    from animatediff.cli import generate

    output_0_dir = generate(
        config_path=config_org,
        width=width,
        height=height,
        length=16,
        context=16,
        out_dir=project_dir / CONST_PROJECT_FILE.draft,
    )

    torch.cuda.empty_cache()

    logger.info(f"Stylized results are output to {output_0_dir}")


@ama.command(no_args_is_help=True)
def ama_mask(
    project,
    box_threshold: Annotated[
        float,
        typer.Option(
            "--box_threshold",
            "-b",
            min=0.0,
            max=1.0,
            help="box_threshold",
            rich_help_panel="create mask",
        ),
    ] = 0.3,
    text_threshold: Annotated[
        float,
        typer.Option(
            "--text_threshold",
            "-t",
            min=0.0,
            max=1.0,
            help="text_threshold",
            rich_help_panel="create mask",
        ),
    ] = 0.25,
    mask_padding: Annotated[
        int,
        typer.Option(
            "--mask_padding",
            "-mp",
            min=-100,
            max=100,
            help="padding pixel value",
            rich_help_panel="create mask",
        ),
    ] = 0,
    no_gb: Annotated[
        bool,
        typer.Option(
            "--no_gb",
            "-ng",
            is_flag=True,
            help="no green back",
            rich_help_panel="create mask",
        ),
    ] = False,
    no_crop: Annotated[
        bool,
        typer.Option(
            "--no_crop",
            "-nc",
            is_flag=True,
            help="no crop",
            rich_help_panel="create mask",
        ),
    ] = False,
    use_rembg: Annotated[
        bool,
        typer.Option(
            "--use_rembg",
            "-rem",
            is_flag=True,
            help="use [rembg] instead of [Sam+GroundingDINO]",
            rich_help_panel="create mask",
        ),
    ] = False,
    use_animeseg: Annotated[
        bool,
        typer.Option(
            "--use_animeseg",
            "-anim",
            is_flag=True,
            help="use [anime-segmentation] instead of [Sam+GroundingDINO]",
            rich_help_panel="create mask",
        ),
    ] = False,
    low_vram: Annotated[
        bool,
        typer.Option(
            "--low_vram",
            "-lo",
            is_flag=True,
            help="low vram mode",
            rich_help_panel="create mask/tag",
        ),
    ] = False,
    ignore_list: Annotated[
        Path,
        typer.Option(
            "--ignore-list",
            "-g",
            path_type=Path,
            dir_okay=False,
            exists=True,
            help="path to ignore token list file",
            rich_help_panel="create tag",
        ),
    ] = Path("config/prompts/ignore_tokens.txt"),
    predicte_interval: Annotated[
        int,
        typer.Option(
            "--predicte-interval",
            "-p",
            min=1,
            max=120,
            help="Interval of frames to be predicted",
            rich_help_panel="create tag",
        ),
    ] = 1,
    general_threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            "-th",
            min=0.0,
            max=1.0,
            help="threshold for general token confidence",
            rich_help_panel="create tag",
        ),
    ] = 0.35,
    character_threshold: Annotated[
        float,
        typer.Option(
            "--threshold2",
            "-th2",
            min=0.0,
            max=1.0,
            help="threshold for character token confidence",
            rich_help_panel="create tag",
        ),
    ] = 0.85,
    is_no_danbooru_format: Annotated[
        bool,
        typer.Option(
            "--no-danbooru-format",
            "-ndf",
            is_flag=True,
            help="danbooru token format or not. ex. 'bandaid_on_leg, short_hair' -> 'bandaid on leg, short hair'",
            rich_help_panel="create tag",
        ),
    ] = False,
):
    """Create mask from prompt."""
    from animatediff.utils.mask import create_bg, create_fg, crop_frames, crop_mask_list, save_crop_info

    is_danbooru_format = not is_no_danbooru_format

    if use_animeseg and use_rembg:
        raise ValueError("use_animeseg and use_rembg cannot be enabled at the same time")

    prepare_sam_hq(low_vram)
    prepare_groundingDINO()
    prepare_propainter()

    if use_animeseg:
        prepare_anime_seg()

    project_dir = path_mgr.projects / project

    config_org = project_dir / CONST_PROJECT_FILE.config

    project_setting = get_project_setting(config_org)

    frame_dir = project_dir / CONST_PROJECT_FILE.input_frames

    if not frame_dir.is_dir():
        raise ValueError(f"{frame_dir=} does not exist.")

    is_img2img = project_setting.img2img_map.enable

    # create_mask_list = []
    # if "create_mask" in project_setting.stylize_config:
    #     create_mask_list = project_setting.stylize_config["create_mask"]
    # else:
    #     raise ValueError('model_config.stylize_config["create_mask"] not found')

    output_list = []

    stylize_frame = sorted(glob.glob(os.path.join(frame_dir, "[0-9]*.png"), recursive=False))
    frame_len = len(stylize_frame)

    W, H = Image.open(stylize_frame[0]).size
    org_frame_size = (H, W)

    masked_area = [None for f in range(frame_len)]

    def create_controlnet_dir(controlnet_root):
        for c in [
            "controlnet_canny",
            "controlnet_depth",
            "controlnet_inpaint",
            "controlnet_ip2p",
            "controlnet_lineart",
            "controlnet_lineart_anime",
            "controlnet_mlsd",
            "controlnet_normalbae",
            "controlnet_openpose",
            "controlnet_scribble",
            "controlnet_seg",
            "controlnet_shuffle",
            "controlnet_softedge",
            "controlnet_tile",
        ]:
            c_dir = controlnet_root.joinpath(c)
            c_dir.mkdir(parents=True, exist_ok=True)

    if use_rembg:
        create_mask_list = ["rembg"]
    elif use_animeseg:
        create_mask_list = ["anime-segmentation"]

    create_mask_list = ["person"]
    for i, mask_token in enumerate(create_mask_list):
        fg_dir = project_dir / "fg"
        fg_dir.mkdir(parents=True, exist_ok=True)

        create_controlnet_dir(fg_dir / "00_controlnet_image")

        fg_masked_dir = fg_dir / "00_img2img"
        fg_masked_dir.mkdir(parents=True, exist_ok=True)

        fg_mask_dir = fg_dir / "00_mask"
        fg_mask_dir.mkdir(parents=True, exist_ok=True)

        if use_animeseg:
            from animatediff.utils.mask_animseg import animseg_create_fg

            masked_area = animseg_create_fg(
                frame_dir=frame_dir,
                output_dir=fg_masked_dir,
                output_mask_dir=fg_mask_dir,
                masked_area_list=masked_area,
                mask_padding=mask_padding,
                bg_color=None if no_gb else (0, 255, 0),
            )
        elif use_rembg:
            from animatediff.utils.mask_rembg import rembg_create_fg

            masked_area = rembg_create_fg(
                frame_dir=frame_dir,
                output_dir=fg_masked_dir,
                output_mask_dir=fg_mask_dir,
                masked_area_list=masked_area,
                mask_padding=mask_padding,
                bg_color=None if no_gb else (0, 255, 0),
            )
        else:
            masked_area = create_fg(
                mask_token=mask_token,
                frame_dir=frame_dir,
                output_dir=fg_masked_dir,
                output_mask_dir=fg_mask_dir,
                masked_area_list=masked_area,
                box_threshold=box_threshold,
                text_threshold=text_threshold,
                mask_padding=mask_padding,
                sam_checkpoint=path_mgr.sam / "sam_hq_vit_h.pth" if not low_vram else path_mgr.sam / "sam_hq_vit_b.pth",
                bg_color=None if no_gb else (0, 255, 0),
                device=get_torch_device(),
            )

        if not no_crop:
            frame_size_hw = (masked_area[0].shape[1], masked_area[0].shape[2])
            cropped_mask_list, mask_pos_list, crop_size_hw = crop_mask_list(masked_area)

            logger.info("crop fg_masked_dir")
            crop_frames(mask_pos_list, crop_size_hw, fg_masked_dir)
            logger.info("crop fg_mask_dir")
            crop_frames(mask_pos_list, crop_size_hw, fg_mask_dir)
            save_crop_info(mask_pos_list, crop_size_hw, frame_size_hw, fg_dir / "crop_info.json")
        else:
            crop_size_hw = None

        logger.info(f"mask from [{mask_token}] are output to {fg_dir}")

        if not is_img2img:
            shutil.copytree(fg_masked_dir, fg_dir / "00_controlnet_image/controlnet_tile", dirs_exist_ok=True)
        else:
            shutil.copytree(fg_masked_dir, fg_dir / "00_controlnet_image/controlnet_openpose", dirs_exist_ok=True)

        shutil.copytree(fg_masked_dir, fg_dir / "00_controlnet_image/controlnet_ip2p", dirs_exist_ok=True)

        if crop_size_hw:
            if crop_size_hw[0] == 0 or crop_size_hw[1] == 0:
                crop_size_hw = None

        output_list.append((fg_dir, crop_size_hw))

    torch.cuda.empty_cache()

    bg_dir = project_dir / "bg"
    bg_dir.mkdir(parents=True, exist_ok=True)
    create_controlnet_dir(bg_dir / "00_controlnet_image")
    bg_inpaint_dir = bg_dir / "00_img2img"
    bg_inpaint_dir.mkdir(parents=True, exist_ok=True)

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

    logger.info(f"background are output to {bg_dir}")

    if not is_img2img:
        shutil.copytree(bg_inpaint_dir, bg_dir / "00_controlnet_image/controlnet_tile", dirs_exist_ok=True)
    else:
        shutil.copytree(bg_inpaint_dir, bg_dir / "00_controlnet_image/controlnet_openpose", dirs_exist_ok=True)

    shutil.copytree(bg_inpaint_dir, bg_dir / "00_controlnet_image/controlnet_ip2p", dirs_exist_ok=True)

    output_list.append((bg_dir, None))

    torch.cuda.empty_cache()

    black_list = []
    if ignore_list.is_file():
        with open(ignore_list) as f:
            black_list = [s.strip() for s in f.readlines()]

    for output, size in output_list:
        project_setting.prompt_map = get_labels(
            frame_dir=output / "00_img2img",
            interval=predicte_interval,
            general_threshold=general_threshold,
            character_threshold=character_threshold,
            ignore_tokens=black_list,
            with_confidence=False,
            is_danbooru_format=is_danbooru_format,
            is_cpu=False,
        )

        project_setting.controlnet_map["input_image_dir"] = os.path.relpath(
            (output / "00_controlnet_image").absolute(), data_dir
        )
        project_setting.img2img_map["init_img_dir"] = os.path.relpath((output / "00_img2img").absolute(), data_dir)

        if size is not None:
            h, w = size
            height = 1024 * (h / (h + w))
            width = 1024 * (w / (h + w))
            height = int(height // 8 * 8)
            width = int(width // 8 * 8)

            project_setting.stylize_config["0"]["width"] = width
            project_setting.stylize_config["0"]["height"] = height
            if "1" in project_setting.stylize_config:
                project_setting.stylize_config["1"]["width"] = int(width * 1.25 // 8 * 8)
                project_setting.stylize_config["1"]["height"] = int(height * 1.25 // 8 * 8)
        else:
            height, width = org_frame_size
            project_setting.stylize_config["0"]["width"] = width
            project_setting.stylize_config["0"]["height"] = height
            if "1" in project_setting.stylize_config:
                project_setting.stylize_config["1"]["width"] = int(width * 1.25 // 8 * 8)
                project_setting.stylize_config["1"]["height"] = int(height * 1.25 // 8 * 8)

        save_config_path = output.joinpath("prompt.json")
        save_config_path.write_text(project_setting.model_dump_json(indent=4), encoding="utf-8")


@ama.command(no_args_is_help=True)
def composite(
    stylize_dir: Annotated[
        Path,
        typer.Argument(path_type=Path, file_okay=False, dir_okay=True, exists=True, help="Path to stylize dir"),
    ] = ...,
    box_threshold: Annotated[
        float,
        typer.Option(
            "--box_threshold",
            "-b",
            min=0.0,
            max=1.0,
            help="box_threshold",
            rich_help_panel="create mask",
        ),
    ] = 0.3,
    text_threshold: Annotated[
        float,
        typer.Option(
            "--text_threshold",
            "-t",
            min=0.0,
            max=1.0,
            help="text_threshold",
            rich_help_panel="create mask",
        ),
    ] = 0.25,
    mask_padding: Annotated[
        int,
        typer.Option(
            "--mask_padding",
            "-mp",
            min=-100,
            max=100,
            help="padding pixel value",
            rich_help_panel="create mask",
        ),
    ] = 0,
    use_rembg: Annotated[
        bool,
        typer.Option(
            "--use_rembg",
            "-rem",
            is_flag=True,
            help=r"use \[rembg] instead of \[Sam+GroundingDINO]",
            rich_help_panel="create mask",
        ),
    ] = False,
    use_animeseg: Annotated[
        bool,
        typer.Option(
            "--use_animeseg",
            "-anim",
            is_flag=True,
            help=r"use \[anime-segmentation] instead of \[Sam+GroundingDINO]",
            rich_help_panel="create mask",
        ),
    ] = False,
    low_vram: Annotated[
        bool,
        typer.Option(
            "--low_vram",
            "-lo",
            is_flag=True,
            help="low vram mode",
            rich_help_panel="create mask/tag",
        ),
    ] = False,
    is_simple_composite: Annotated[
        bool,
        typer.Option(
            "--simple_composite",
            "-si",
            is_flag=True,
            help="simple composite",
            rich_help_panel="composite",
        ),
    ] = False,
):
    """Composite FG and BG."""
    from animatediff.utils.composite import composite, simple_composite
    from animatediff.utils.mask import create_fg, load_frame_list, load_mask_list, restore_position
    from animatediff.utils.mask_animseg import animseg_create_fg
    from animatediff.utils.mask_rembg import rembg_create_fg

    if use_animeseg and use_rembg:
        raise ValueError("use_animeseg and use_rembg cannot be enabled at the same time")

    prepare_sam_hq(low_vram)
    if use_animeseg:
        prepare_anime_seg()

    time_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    config_org = stylize_dir.joinpath("prompt.json")

    model_config = get_project_setting(config_org)

    composite_config = {}
    if "composite" in model_config.stylize_config:
        composite_config = model_config.stylize_config["composite"]
    else:
        raise ValueError('model_config.stylize_config["composite"] not found')

    save_dir = stylize_dir.joinpath(f"cp_{time_str}")
    save_dir.mkdir(parents=True, exist_ok=True)

    save_config_path = save_dir.joinpath("prompt.json")
    save_config_path.write_text(model_config.model_dump_json(indent=4), encoding="utf-8")

    bg_dir = composite_config["bg_frame_dir"]
    bg_dir = Path(bg_dir)
    if not bg_dir.is_dir():
        raise ValueError('model_config.stylize_config["composite"]["bg_frame_dir"] not valid')

    frame_len = len(sorted(glob.glob(os.path.join(bg_dir, "[0-9]*.png"), recursive=False)))

    fg_list = composite_config["fg_list"]

    for i, fg_param in enumerate(fg_list):
        mask_token = fg_param["mask_prompt"]
        frame_dir = Path(fg_param["path"])
        if not frame_dir.is_dir():
            logger.warning(f"{frame_dir=} not valid -> skip")
            continue

        mask_dir = Path(fg_param["mask_path"])
        if not mask_dir.is_dir():
            logger.info(f"{mask_dir=} not valid -> create mask")

            fg_tmp_dir = save_dir.joinpath(f"fg_{i:02d}_{time_str}")
            fg_tmp_dir.mkdir(parents=True, exist_ok=True)

            masked_area_list = [None for f in range(frame_len)]

            if use_animeseg:
                mask_list = animseg_create_fg(
                    frame_dir=frame_dir,
                    output_dir=fg_tmp_dir,
                    output_mask_dir=None,
                    masked_area_list=masked_area_list,
                    mask_padding=mask_padding,
                )
            elif use_rembg:
                mask_list = rembg_create_fg(
                    frame_dir=frame_dir,
                    output_dir=fg_tmp_dir,
                    output_mask_dir=None,
                    masked_area_list=masked_area_list,
                    mask_padding=mask_padding,
                )
            else:
                mask_list = create_fg(
                    mask_token=mask_token,
                    frame_dir=frame_dir,
                    output_dir=fg_tmp_dir,
                    output_mask_dir=None,
                    masked_area_list=masked_area_list,
                    box_threshold=box_threshold,
                    text_threshold=text_threshold,
                    mask_padding=mask_padding,
                    sam_checkpoint="models/sam/sam_hq_vit_h.pth" if not low_vram else "models/sam/sam_hq_vit_b.pth",
                )

        else:
            logger.info(f"use {mask_dir=} as mask")

            masked_area_list = [None for f in range(frame_len)]

            mask_list = load_mask_list(mask_dir, masked_area_list, mask_padding)

        mask_list = [m.transpose([1, 2, 0]) if m is not None else m for m in mask_list]

        crop_info_path = frame_dir.parent.parent / "crop_info.json"
        crop_info = {}
        if crop_info_path.is_file():
            with open(crop_info_path, mode="rt", encoding="utf-8") as f:
                crop_info = json.load(f)
            mask_list = restore_position(mask_list, crop_info)

        fg_list = [None for f in range(frame_len)]
        fg_list = load_frame_list(frame_dir, fg_list, crop_info)

        output_dir = save_dir.joinpath(f"bg_{i:02d}_{time_str}")
        output_dir.mkdir(parents=True, exist_ok=True)

        if is_simple_composite:
            simple_composite(bg_dir, fg_list, output_dir, mask_list)
        else:
            composite(bg_dir, fg_list, output_dir, mask_list)

        bg_dir = output_dir

    from animatediff.generate import save_output

    frames = sorted(glob.glob(os.path.join(bg_dir, "[0-9]*.png"), recursive=False))
    out_images = []
    for f in frames:
        out_images.append(Image.open(f))

    out_file = save_dir.joinpath("composite")
    save_output(out_images, bg_dir, out_file, model_config.output, True, save_frames=None, save_video=None)

    logger.info(f"output to {out_file}")


@ama.command(no_args_is_help=True)
def create_region(
    stylize_dir: Annotated[
        Path,
        typer.Argument(path_type=Path, file_okay=False, dir_okay=True, exists=True, help="Path to stylize dir"),
    ] = ...,
    frame_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--frame_dir",
            "-f",
            path_type=Path,
            file_okay=False,
            help="Path to source frames directory. default is 'STYLIZE_DIR/00_img2img'",
        ),
    ] = None,
    box_threshold: Annotated[
        float,
        typer.Option(
            "--box_threshold",
            "-b",
            min=0.0,
            max=1.0,
            help="box_threshold",
            rich_help_panel="create mask",
        ),
    ] = 0.3,
    text_threshold: Annotated[
        float,
        typer.Option(
            "--text_threshold",
            "-t",
            min=0.0,
            max=1.0,
            help="text_threshold",
            rich_help_panel="create mask",
        ),
    ] = 0.25,
    mask_padding: Annotated[
        int,
        typer.Option(
            "--mask_padding",
            "-mp",
            min=-100,
            max=100,
            help="padding pixel value",
            rich_help_panel="create mask",
        ),
    ] = 0,
    use_rembg: Annotated[
        bool,
        typer.Option(
            "--use_rembg",
            "-rem",
            is_flag=True,
            help="use [rembg] instead of [Sam+GroundingDINO]",
            rich_help_panel="create mask",
        ),
    ] = False,
    use_animeseg: Annotated[
        bool,
        typer.Option(
            "--use_animeseg",
            "-anim",
            is_flag=True,
            help="use [anime-segmentation] instead of [Sam+GroundingDINO]",
            rich_help_panel="create mask",
        ),
    ] = False,
    low_vram: Annotated[
        bool,
        typer.Option(
            "--low_vram",
            "-lo",
            is_flag=True,
            help="low vram mode",
            rich_help_panel="create mask/tag",
        ),
    ] = False,
    ignore_list: Annotated[
        Path,
        typer.Option(
            "--ignore-list",
            "-g",
            path_type=Path,
            dir_okay=False,
            exists=True,
            help="path to ignore token list file",
            rich_help_panel="create tag",
        ),
    ] = Path("config/prompts/ignore_tokens.txt"),
    predicte_interval: Annotated[
        int,
        typer.Option(
            "--predicte-interval",
            "-p",
            min=1,
            max=120,
            help="Interval of frames to be predicted",
            rich_help_panel="create tag",
        ),
    ] = 1,
    general_threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            "-th",
            min=0.0,
            max=1.0,
            help="threshold for general token confidence",
            rich_help_panel="create tag",
        ),
    ] = 0.35,
    character_threshold: Annotated[
        float,
        typer.Option(
            "--threshold2",
            "-th2",
            min=0.0,
            max=1.0,
            help="threshold for character token confidence",
            rich_help_panel="create tag",
        ),
    ] = 0.85,
    without_confidence: Annotated[
        bool,
        typer.Option(
            "--no-confidence-format",
            "-ncf",
            is_flag=True,
            help="confidence token format or not. ex. '(close-up:0.57), (monochrome:1.1)' -> 'close-up, monochrome'",
            rich_help_panel="create tag",
        ),
    ] = False,
    is_no_danbooru_format: Annotated[
        bool,
        typer.Option(
            "--no-danbooru-format",
            "-ndf",
            is_flag=True,
            help="danbooru token format or not. ex. 'bandaid_on_leg, short_hair' -> 'bandaid on leg, short hair'",
            rich_help_panel="create tag",
        ),
    ] = False,
):
    """Create region from prompt."""
    from animatediff.utils.mask import create_bg, create_fg
    from animatediff.utils.mask_animseg import animseg_create_fg
    from animatediff.utils.mask_rembg import rembg_create_fg

    is_danbooru_format = not is_no_danbooru_format
    with_confidence = not without_confidence

    if use_animeseg and use_rembg:
        raise ValueError("use_animeseg and use_rembg cannot be enabled at the same time")

    prepare_sam_hq(low_vram)
    prepare_groundingDINO()
    prepare_propainter()

    if use_animeseg:
        prepare_anime_seg()

    time_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    config_org = stylize_dir.joinpath("prompt.json")

    model_config = get_project_setting(config_org)

    if frame_dir is None:
        frame_dir = stylize_dir / "00_img2img"

    if not frame_dir.is_dir():
        raise ValueError(f"{frame_dir=} does not exist.")

    create_mask_list = []
    if "create_mask" in model_config.stylize_config:
        create_mask_list = model_config.stylize_config["create_mask"]
    else:
        raise ValueError('model_config.stylize_config["create_mask"] not found')

    output_list = []

    stylize_frame = sorted(glob.glob(os.path.join(frame_dir, "[0-9]*.png"), recursive=False))
    frame_len = len(stylize_frame)

    masked_area = [None for f in range(frame_len)]

    if use_rembg:
        create_mask_list = ["rembg"]
    elif use_animeseg:
        create_mask_list = ["anime-segmentation"]

    for i, mask_token in enumerate(create_mask_list):
        fg_dir = stylize_dir.joinpath(f"r_fg_{i:02d}_{time_str}")
        fg_dir.mkdir(parents=True, exist_ok=True)

        fg_masked_dir = fg_dir / "00_tmp_masked"
        fg_masked_dir.mkdir(parents=True, exist_ok=True)

        fg_mask_dir = fg_dir / "00_mask"
        fg_mask_dir.mkdir(parents=True, exist_ok=True)

        if use_animeseg:
            masked_area = animseg_create_fg(
                frame_dir=frame_dir,
                output_dir=fg_masked_dir,
                output_mask_dir=fg_mask_dir,
                masked_area_list=masked_area,
                mask_padding=mask_padding,
                bg_color=(0, 255, 0),
            )
        elif use_rembg:
            masked_area = rembg_create_fg(
                frame_dir=frame_dir,
                output_dir=fg_masked_dir,
                output_mask_dir=fg_mask_dir,
                masked_area_list=masked_area,
                mask_padding=mask_padding,
                bg_color=(0, 255, 0),
            )
        else:
            masked_area = create_fg(
                mask_token=mask_token,
                frame_dir=frame_dir,
                output_dir=fg_masked_dir,
                output_mask_dir=fg_mask_dir,
                masked_area_list=masked_area,
                box_threshold=box_threshold,
                text_threshold=text_threshold,
                mask_padding=mask_padding,
                sam_checkpoint="models/sam/sam_hq_vit_h.pth" if not low_vram else "models/sam/sam_hq_vit_b.pth",
                bg_color=(0, 255, 0),
            )

        logger.info(f"mask from [{mask_token}] are output to {fg_dir}")

        output_list.append((fg_dir, fg_masked_dir, fg_mask_dir))

    torch.cuda.empty_cache()

    bg_dir = stylize_dir.joinpath(f"r_bg_{time_str}")
    bg_dir.mkdir(parents=True, exist_ok=True)

    bg_inpaint_dir = bg_dir / "00_tmp_inpainted"
    bg_inpaint_dir.mkdir(parents=True, exist_ok=True)

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

    logger.info(f"background are output to {bg_dir}")

    output_list.append((bg_dir, bg_inpaint_dir, None))

    torch.cuda.empty_cache()

    black_list = []
    if ignore_list.is_file():
        with open(ignore_list) as f:
            black_list = [s.strip() for s in f.readlines()]

    black_list.append("simple_background")
    black_list.append("green_background")

    region_map = {}

    for i, (output_root, masked_dir, mask_dir) in enumerate(output_list):
        prompt_map = get_labels(
            frame_dir=masked_dir,
            interval=predicte_interval,
            general_threshold=general_threshold,
            character_threshold=character_threshold,
            ignore_tokens=black_list,
            with_confidence=with_confidence,
            is_danbooru_format=is_danbooru_format,
            is_cpu=False,
        )

        if mask_dir:
            ipadapter_dir = output_root / "00_ipadapter"
            ipadapter_dir.mkdir(parents=True, exist_ok=True)

            region_map[str(i)] = {
                "enable": True,
                "crop_generation_rate": 0.0,
                "mask_dir": os.path.relpath(mask_dir.absolute(), data_dir),
                "save_mask": True,
                "is_init_img": False,
                "condition": {
                    "prompt_fixed_ratio": 0.5,
                    "head_prompt": "",
                    "prompt_map": prompt_map,
                    "tail_prompt": "",
                    "ip_adapter_map": {
                        "enable": True,
                        "input_image_dir": os.path.relpath(ipadapter_dir.absolute(), data_dir),
                        "prompt_fixed_ratio": 0.5,
                        "save_input_image": True,
                        "resized_to_square": False,
                    },
                },
            }
        else:
            region_map["background"] = {
                "is_init_img": False,
                "hint": "background's condition refers to the one in root",
            }

            model_config.prompt_map = prompt_map

        model_config.region_map = region_map

        config_org.write_text(model_config.model_dump_json(indent=4), encoding="utf-8")
