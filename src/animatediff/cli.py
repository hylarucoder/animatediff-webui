"""cli.py
"""
import glob
import logging
import os.path
from datetime import datetime
from importlib.metadata import version as meta_version
from pathlib import Path
from typing import Annotated, Optional

import torch
import typer
from diffusers import DiffusionPipeline
from diffusers.utils.logging import set_verbosity_error as set_diffusers_verbosity_error
from packaging import version
from rich.logging import RichHandler
from rich.progress import Progress

from animatediff import __version__, console, get_dir
from animatediff.consts import path_mgr
from animatediff.generate import (
    controlnet_preprocess,
    create_pipeline,
    create_us_pipeline,
    img2img_preprocess,
    load_controlnet_models,
    region_preprocess,
    run_inference,
    run_upscale,
    save_output,
    unload_controlnet_models,
    wild_card_conversion,
)
from animatediff.pipelines import load_text_embeddings
from animatediff.settings import CKPT_EXTENSIONS, InferenceConfig, get_infer_config, get_project_setting
from animatediff.utils.civitai2config import generate_config_from_civitai_info
from animatediff.utils.model import checkpoint_to_pipeline, fix_checkpoint_if_needed, get_base_model
from animatediff.utils.pipeline import get_context_params, send_to_device
from animatediff.utils.progressbar import pbar
from animatediff.utils.util import (
    is_sdxl_checkpoint,
    is_v2_motion_module,
    path_from_cwd,
    save_video,
    set_tensor_interpolation_method,
)

cli: typer.Typer = typer.Typer(
    context_settings=dict(help_option_names=["-h", "--help"]),
    rich_markup_mode="rich",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)
data_dir = get_dir("data")
pipeline_dir = path_mgr.huggingface_pipeline

try:
    import google.colab

    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:
    import sys

    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True),
        ],
        datefmt="%H:%M:%S",
        force=True,
    )

logger = logging.getLogger(__name__)

diffuser_ver = meta_version("diffusers")

logger.info(f"{diffuser_ver=}")

if version.parse(diffuser_ver) < version.parse("0.23.0"):
    logger.error("The version of diffusers is out of date")
    logger.error("python -m pip install diffusers==0.23.0")
    raise ImportError("Please update diffusers to 0.23.0")

try:
    from animatediff.rife import app as rife_app

    cli.add_typer(rife_app, name="rife")
except ImportError:
    logger.debug("RIFE not available, skipping...", exc_info=True)
    rife_app = None

from animatediff.stylize import stylize

cli.add_typer(stylize, name="stylize")

# mildly cursed globals to allow for reuse of the pipeline if we're being called as a module
g_pipeline: Optional[DiffusionPipeline] = None
last_model_path: Optional[Path] = None


def version_callback(value: bool):
    if value:
        console.print(f"AnimateDiff v{__version__}")
        raise typer.Exit()


def get_random():
    import sys

    import numpy as np

    return int(np.random.randint(sys.maxsize, dtype=np.int64))


@cli.command()
def generate(
        config_path: Annotated[
            Path,
            typer.Option(
                "--config-path",
                "-c",
                path_type=Path,
                exists=True,
                readable=True,
                dir_okay=False,
                help="Path to a prompt configuration JSON file",
            ),
        ] = Path("config/prompts/01-ToonYou.json"),
        width: Annotated[
            int,
            typer.Option(
                "--width",
                "-W",
                min=64,
                max=3840,
                help="Width of generated frames",
                rich_help_panel="Generation",
            ),
        ] = 512,
        height: Annotated[
            int,
            typer.Option(
                "--height",
                "-H",
                min=64,
                max=2160,
                help="Height of generated frames",
                rich_help_panel="Generation",
            ),
        ] = 512,
        length: Annotated[
            int,
            typer.Option(
                "--length",
                "-L",
                min=1,
                max=9999,
                help="Number of frames to generate",
                rich_help_panel="Generation",
            ),
        ] = 16,
        context: Annotated[
            int,
            typer.Option(
                "--context",
                "-C",
                min=1,
                max=32,
                help="Number of frames to condition on (default: max of <length> or 32). max for motion module v1 is 24",
                show_default=False,
                rich_help_panel="Generation",
            ),
        ] = 16,
        overlap: Annotated[
            int,
            typer.Option(
                "--overlap",
                "-O",
                min=0,
                max=12,
                help="Number of frames to overlap in context (default: context//4)",
                show_default=False,
                rich_help_panel="Generation",
            ),
        ] = 4,
        stride: Annotated[
            int,
            typer.Option(
                "--stride",
                "-S",
                min=0,
                max=8,
                help="Max motion stride as a power of 2 (default: 0)",
                show_default=False,
                rich_help_panel="Generation",
            ),
        ] = 0,
        repeats: Annotated[
            int,
            typer.Option(
                "--repeats",
                "-r",
                min=1,
                max=99,
                help="Number of times to repeat the prompt (default: 1)",
                show_default=False,
                rich_help_panel="Generation",
            ),
        ] = 1,
        device: Annotated[
            str,
            typer.Option("--device", "-d", help="Device to run on (cpu, cuda, cuda:id)", rich_help_panel="Advanced"),
        ] = "cuda",
        use_xformers: Annotated[
            bool,
            typer.Option(
                "--xformers",
                "-x",
                is_flag=True,
                help="Use XFormers instead of SDP Attention",
                rich_help_panel="Advanced",
            ),
        ] = False,
        force_half_vae: Annotated[
            bool,
            typer.Option(
                "--half-vae",
                is_flag=True,
                help="Force VAE to use fp16 (not recommended)",
                rich_help_panel="Advanced",
            ),
        ] = False,
        out_dir: Annotated[
            Path,
            typer.Option(
                "--out-dir",
                "-o",
                path_type=Path,
                file_okay=False,
                help="Directory for output folders (frames, gifs, etc)",
                rich_help_panel="Output",
            ),
        ] = Path("output/"),
        no_frames: Annotated[
            bool,
            typer.Option(
                "--no-frames",
                "-N",
                is_flag=True,
                help="Don't save frames, only the animation",
                rich_help_panel="Output",
            ),
        ] = False,
        save_merged: Annotated[
            bool,
            typer.Option(
                "--save-merged",
                "-m",
                is_flag=True,
                help="Save a merged animation of all prompts",
                rich_help_panel="Output",
            ),
        ] = False,
        version: Annotated[
            Optional[bool],
            typer.Option(
                "--version",
                "-v",
                callback=version_callback,
                is_eager=True,
                is_flag=True,
                help="Show version",
            ),
        ] = None,
        progress: Progress = ...
):
    """Do the thing. Make the animation happen. Waow."""
    # be quiet, diffusers. we care not for your safety checker
    set_diffusers_verbosity_error()

    # torch.set_flush_denormal(True)

    config_path = config_path.absolute()
    project_dir = config_path.parent
    logger.info(f"Using generation config: {path_from_cwd(config_path)}")
    project_setting = get_project_setting(config_path)
    is_sdxl = is_sdxl_checkpoint(path_mgr.checkpoints / project_setting.checkpoint)

    if is_sdxl:
        is_v2 = False
    else:
        is_v2 = is_v2_motion_module(path_mgr.motions / project_setting.motion)

    infer_config: InferenceConfig = get_infer_config(is_v2, is_sdxl)

    set_tensor_interpolation_method(project_setting.tensor_interpolation_slerp)

    # set sane defaults for context, overlap, and stride if not supplied
    context, overlap, stride = get_context_params(length, context, overlap, stride)

    if (not is_v2) and (not is_sdxl) and (context > 24):
        logger.warning("For motion module v1, the maximum value of context is 24. Set to 24")
        context = 24

    # turn the device string into a torch.device
    torch_device: torch.device = torch.device(device)

    model_name_or_path = (
        Path("runwayml/stable-diffusion-v1-5") if not is_sdxl else Path("stabilityai/stable-diffusion-xl-base-1.0")
    )

    # Get the base model if we don't have it already
    logger.info(f"Using base model: {model_name_or_path}")
    base_model_path: Path = get_base_model(model_name_or_path, local_dir=path_mgr.huggingface_pipeline, is_sdxl=is_sdxl)

    # get a timestamp for the output directory
    time_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    # make the output directory
    save_dir = out_dir.joinpath(f"{time_str}")
    save_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Will save outputs to ./{path_from_cwd(save_dir)}")

    pbar.pbar_preprocess_image.update(10)
    pbar.pbar.update(10)

    controlnet_image_map, controlnet_type_map, controlnet_ref_map = controlnet_preprocess(
        project_dir,
        save_dir,
        project_setting.controlnet_map,
        width,
        height,
        length,
        torch_device,
        is_sdxl,
    )
    pbar.pbar_preprocess_image.update(100)
    pbar.pbar_image_2_image.update(10)
    img2img_map = img2img_preprocess(
        project_dir,
        save_dir,
        project_setting.img2img_map,
        width,
        height,
        length,
    )
    pbar.pbar_image_2_image.update(100)

    # beware the pipeline
    global g_pipeline
    global last_model_path
    pbar.pbar_load_model.update(10)
    if g_pipeline is None or last_model_path != path_mgr.checkpoints / project_setting.checkpoint:
        g_pipeline = create_pipeline(
            base_model=base_model_path,
            project_setting=project_setting,
            infer_config=infer_config,
            use_xformers=use_xformers,
            video_length=length,
            is_sdxl=is_sdxl,
        )
        last_model_path = path_mgr.checkpoints / project_setting.checkpoint
    else:
        logger.info("Pipeline already loaded, skipping initialization")
        # reload TIs; create_pipeline does this for us, but they may have changed
        # since load time if we're being called from another package
        load_text_embeddings(g_pipeline, is_sdxl=is_sdxl)

    pbar.pbar_load_model.update(80)
    load_controlnet_models(project_dir, pipe=g_pipeline, project_setting=project_setting, is_sdxl=is_sdxl)
    pbar.pbar_load_model.update(100)
    pbar.pbar.update(10)

    if g_pipeline.device == torch_device:
        logger.info("Pipeline already on the correct device, skipping device transfer")
    else:
        g_pipeline = send_to_device(
            g_pipeline,
            torch_device,
            freeze=True,
            force_half=force_half_vae,
            compile=project_setting.compile,
            is_sdxl=is_sdxl,
        )

        torch.cuda.empty_cache()

    # save raw config to output directory
    save_config_path = save_dir.joinpath("raw_prompt.json")
    save_config_path.write_text(project_setting.model_dump_json(indent=4), encoding="utf-8")

    # fix seed
    for i, s in enumerate(project_setting.seed):
        if s == -1:
            project_setting.seed[i] = get_random()

    # wildcard conversion
    wild_card_conversion(project_setting)

    is_init_img_exist = img2img_map is not None
    region_condi_list, region_list, ip_adapter_config_map = region_preprocess(
        project_dir, save_dir, project_setting, width, height, length, is_init_img_exist, is_sdxl
    )

    # save config to output directory
    logger.info("Saving prompt config to output directory")
    save_config_path = save_dir.joinpath("prompt.json")
    save_config_path.write_text(project_setting.model_dump_json(indent=4), encoding="utf-8")

    num_negatives = len(project_setting.n_prompt)
    num_seeds = len(project_setting.seed)
    gen_total = repeats  # total number of generations

    logger.info("Initialization complete!")
    logger.info(f"Generating {gen_total} animations")
    outputs = []

    gen_num = 0  # global generation index

    pbar.pbar.update(20)
    pbar.pbar_animate.update(0)
    # repeat the prompts if we're doing multiple runs
    for _ in range(repeats):
        if project_setting.prompt_map:
            # get the index of the prompt, negative, and seed
            idx = gen_num
            logger.info(f"Running generation {gen_num + 1} of {gen_total}")

            # allow for reusing the same negative prompt(s) and seed(s) for multiple prompts
            n_prompt = project_setting.n_prompt[idx % num_negatives]
            seed = project_setting.seed[idx % num_seeds]

            logger.info(f"Generation seed: {seed}")

            # pgr.update_phrase(1, "Step 05/08: Run Interference...")
            output = run_inference(
                pipeline=g_pipeline,
                n_prompt=n_prompt,
                seed=seed,
                steps=project_setting.steps,
                guidance_scale=project_setting.guidance_scale,
                unet_batch_size=project_setting.unet_batch_size,
                width=width,
                height=height,
                duration=length,
                idx=gen_num,
                out_dir=save_dir,
                context_frames=context,
                context_overlap=overlap,
                context_stride=stride,
                clip_skip=project_setting.clip_skip,
                controlnet_map=project_setting.controlnet_map,
                controlnet_image_map=controlnet_image_map,
                controlnet_type_map=controlnet_type_map,
                controlnet_ref_map=controlnet_ref_map,
                no_frames=no_frames,
                img2img_map=img2img_map,
                ip_adapter_config_map=ip_adapter_config_map,
                region_list=region_list,
                region_condi_list=region_condi_list,
                output_map=project_setting.output,
                is_single_prompt_mode=project_setting.is_single_prompt_mode,
                is_sdxl=is_sdxl,
                apply_lcm_lora=project_setting.apply_lcm_lora,
                gradual_latent_map=project_setting.gradual_latent_hires_fix_map
            )
            outputs.append(output)
            torch.cuda.empty_cache()

            # increment the generation number
            gen_num += 1

    pbar.pbar_animate.update(100)
    pbar.pbar_unload_models.update(50)
    unload_controlnet_models(pipe=g_pipeline)
    pbar.pbar_unload_models.update(100)

    logger.info("Generation complete!")
    pbar.pbar_make_video.update(50)
    if save_merged:
        logger.info("Output merged output video...")
        merged_output = torch.concat(outputs, dim=0)
        save_video(merged_output, save_dir.joinpath("final.gif"))
    pbar.pbar_make_video.update(100)
    pbar.pbar.update(100)

    logger.info("Done, exiting...")
    return save_dir


@cli.command()
def tile_upscale(
        frames_dir: Annotated[
            Path,
            typer.Argument(path_type=Path, file_okay=False, exists=True, help="Path to source frames directory"),
        ],
        config_path: Annotated[
            Optional[Path],
            typer.Option(
                "--config-path",
                "-c",
                path_type=Path,
                exists=True,
                readable=True,
                dir_okay=False,
                help="Path to a prompt configuration JSON file. default is frames_dir/../prompt.json",
            ),
        ] = None,
        width: Annotated[
            int,
            typer.Option(
                "--width",
                "-W",
                min=-1,
                max=3840,
                help="Width of generated frames",
                rich_help_panel="Generation",
            ),
        ] = -1,
        height: Annotated[
            int,
            typer.Option(
                "--height",
                "-H",
                min=-1,
                max=2160,
                help="Height of generated frames",
                rich_help_panel="Generation",
            ),
        ] = -1,
        device: Annotated[
            str,
            typer.Option("--device", "-d", help="Device to run on (cpu, cuda, cuda:id)", rich_help_panel="Advanced"),
        ] = "cuda",
        use_xformers: Annotated[
            bool,
            typer.Option(
                "--xformers",
                "-x",
                is_flag=True,
                help="Use XFormers instead of SDP Attention",
                rich_help_panel="Advanced",
            ),
        ] = False,
        force_half_vae: Annotated[
            bool,
            typer.Option(
                "--half-vae",
                is_flag=True,
                help="Force VAE to use fp16 (not recommended)",
                rich_help_panel="Advanced",
            ),
        ] = False,
        out_dir: Annotated[
            Path,
            typer.Option(
                "--out-dir",
                "-o",
                path_type=Path,
                file_okay=False,
                help="Directory for output folders (frames, gifs, etc)",
                rich_help_panel="Output",
            ),
        ] = Path("upscaled/"),
        no_frames: Annotated[
            bool,
            typer.Option(
                "--no-frames",
                "-N",
                is_flag=True,
                help="Don't save frames, only the animation",
                rich_help_panel="Output",
            ),
        ] = False,
):
    """Upscale frames using controlnet tile"""
    # be quiet, diffusers. we care not for your safety checker
    set_diffusers_verbosity_error()

    if width < 0 and height < 0:
        raise ValueError(f"invalid width,height: {width},{height} \n At least one of them must be specified.")

    if not config_path:
        tmp = frames_dir.parent.joinpath("prompt.json")
        if tmp.is_file():
            config_path = tmp

    project_dir = frames_dir.parent
    assert config_path
    config_path = config_path.absolute()
    logger.info(f"Using generation config: {path_from_cwd(config_path)}")
    project_setting = get_project_setting(config_path)
    is_sdxl = is_sdxl_checkpoint(path_mgr.checkpoints / project_setting.checkpoint)
    if is_sdxl:
        raise ValueError("Currently SDXL model is not available for this command.")

    infer_config: InferenceConfig = get_infer_config(
        is_v2_motion_module(path_mgr.motions.joinpath(project_setting.motion)), is_sdxl
    )
    frames_dir = frames_dir.absolute()

    set_tensor_interpolation_method(project_setting.tensor_interpolation_slerp)

    # turn the device string into a torch.device
    torch_device: torch.device = torch.device(device)

    # get a timestamp for the output directory
    time_str = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    # make the output directory
    save_dir = out_dir.joinpath(f"{time_str}")
    save_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Will save outputs to ./{path_from_cwd(save_dir)}")

    if "controlnet_tile" not in project_setting.upscale_config:
        project_setting.upscale_config["controlnet_tile"] = {
            "enable": True,
            "controlnet_conditioning_scale": 1.0,
            "guess_mode": False,
            "control_guidance_start": 0.0,
            "control_guidance_end": 1.0,
        }

    use_controlnet_ref = False
    use_controlnet_tile = False
    use_controlnet_line_anime = False
    use_controlnet_ip2p = False

    if project_setting.upscale_config:
        use_controlnet_ref = (
            project_setting.upscale_config["controlnet_ref"]["enable"]
            if "controlnet_ref" in project_setting.upscale_config
            else False
        )
        use_controlnet_tile = (
            project_setting.upscale_config["controlnet_tile"]["enable"]
            if "controlnet_tile" in project_setting.upscale_config
            else False
        )
        use_controlnet_line_anime = (
            project_setting.upscale_config["controlnet_line_anime"]["enable"]
            if "controlnet_line_anime" in project_setting.upscale_config
            else False
        )
        use_controlnet_ip2p = (
            project_setting.upscale_config["controlnet_ip2p"]["enable"]
            if "controlnet_ip2p" in project_setting.upscale_config
            else False
        )

    if not use_controlnet_tile:
        if not use_controlnet_line_anime:
            if not use_controlnet_ip2p:
                raise ValueError(
                    f"At least one of them should be enabled. {use_controlnet_tile=}, {use_controlnet_line_anime=}, {use_controlnet_ip2p=}"
                )

    # beware the pipeline
    us_pipeline = create_us_pipeline(
        model_config=project_setting,
        infer_config=infer_config,
        use_xformers=use_xformers,
        use_controlnet_ref=use_controlnet_ref,
        use_controlnet_tile=use_controlnet_tile,
        use_controlnet_line_anime=use_controlnet_line_anime,
        use_controlnet_ip2p=use_controlnet_ip2p,
    )

    if us_pipeline.device == torch_device:
        logger.info("Pipeline already on the correct device, skipping device transfer")
    else:
        us_pipeline = send_to_device(
            us_pipeline, torch_device, freeze=True, force_half=force_half_vae, compile=project_setting.compile
        )

    project_setting.result = {"original_frames": str(frames_dir)}

    # save config to output directory
    logger.info("Saving prompt config to output directory")
    save_config_path = save_dir.joinpath("prompt.json")
    save_config_path.write_text(project_setting.model_dump_json(indent=4), encoding="utf-8")

    num_prompts = 1
    num_negatives = len(project_setting.n_prompt)
    num_seeds = len(project_setting.seed)

    logger.info("Initialization complete!")

    gen_num = 0  # global generation index

    org_images = sorted(glob.glob(os.path.join(frames_dir, "[0-9]*.png"), recursive=False))
    length = len(org_images)

    if project_setting.prompt_map:
        # get the index of the prompt, negative, and seed
        idx = gen_num % num_prompts
        logger.info(f"Running generation {gen_num + 1} of {1} (prompt {idx + 1})")

        # allow for reusing the same negative prompt(s) and seed(s) for multiple prompts
        n_prompt = project_setting.n_prompt[idx % num_negatives]
        seed = seed = project_setting.seed[idx % num_seeds]

        if seed == -1:
            seed = get_random()
        logger.info(f"Generation seed: {seed}")

        prompt_map = {}
        for k in project_setting.prompt_map.keys():
            if int(k) < length:
                pr = project_setting.prompt_map[k]
                if project_setting.head_prompt:
                    pr = project_setting.head_prompt + "," + pr
                if project_setting.tail_prompt:
                    pr = pr + "," + project_setting.tail_prompt

                prompt_map[int(k)] = pr

        if project_setting.upscale_config:
            upscaled_output = run_upscale(
                project_dir,
                project_setting,
                org_imgs=org_images,
                pipeline=us_pipeline,
                prompt_map=prompt_map,
                n_prompt=n_prompt,
                seed=seed,
                steps=project_setting.steps,
                guidance_scale=project_setting.guidance_scale,
                clip_skip=project_setting.clip_skip,
                us_width=width,
                us_height=height,
                idx=gen_num,
                out_dir=save_dir,
                use_controlnet_ref=use_controlnet_ref,
                use_controlnet_tile=use_controlnet_tile,
                use_controlnet_line_anime=use_controlnet_line_anime,
                use_controlnet_ip2p=use_controlnet_ip2p,
                no_frames=no_frames,
            )
            torch.cuda.empty_cache()

        # increment the generation number
        gen_num += 1

    logger.info("Generation complete!")

    logger.info("Done, exiting...")
    cli.info

    return save_dir


@cli.command()
def civitai2config(
        lora_dir: Annotated[
            Path,
            typer.Argument(path_type=Path, file_okay=False, exists=True, help="Path to loras directory"),
        ],
        config_org: Annotated[
            Path,
            typer.Option(
                "--config-org",
                "-c",
                path_type=Path,
                dir_okay=False,
                exists=True,
                help="Path to original config file",
            ),
        ] = Path("config/prompts/prompt_travel.json"),
        out_dir: Annotated[
            Path,
            typer.Option(
                "--out-dir",
                "-o",
                path_type=Path,
                file_okay=False,
                help="Target directory for generated configs",
            ),
        ] = Path("config/prompts/converted/"),
        lora_weight: Annotated[
            float,
            typer.Option(
                "--lora_weight",
                "-l",
                min=0.0,
                max=3.0,
                help="Lora weight",
            ),
        ] = 0.75,
):
    """Generate config file from *.civitai.info"""
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Generate config files from: {lora_dir}")
    generate_config_from_civitai_info(lora_dir, config_org, out_dir, lora_weight)
    logger.info(f"saved at: {out_dir.absolute()}")


@cli.command()
def convert(
        checkpoint: Annotated[
            Path,
            typer.Option(
                "--checkpoint",
                "-i",
                path_type=Path,
                dir_okay=False,
                exists=True,
                help="Path to a model checkpoint file",
            ),
        ],
        out_dir: Annotated[
            Optional[Path],
            typer.Option(
                "--out-dir",
                "-o",
                path_type=Path,
                file_okay=False,
                help="Target directory for converted model",
            ),
        ],
):
    """Convert a StableDiffusion checkpoint into a Diffusers pipeline"""
    logger.info(f"Converting checkpoint: {checkpoint}")
    _, pipeline_dir = checkpoint_to_pipeline(checkpoint, target_dir=out_dir)
    logger.info(f"Converted to HuggingFace pipeline at {pipeline_dir}")


@cli.command()
def fix_checkpoint(
        checkpoint: Annotated[
            Path,
            typer.Argument(path_type=Path, dir_okay=False, exists=True, help="Path to a model checkpoint file"),
        ],
        debug: Annotated[
            bool,
            typer.Option(
                "--debug",
                "-d",
                is_flag=True,
                rich_help_panel="Debug",
            ),
        ] = False,
):
    """Fix checkpoint with error "AttributeError: 'Attention' object has no attribute 'to_to_k'" on loading"""
    set_diffusers_verbosity_error()

    logger.info(f"Converting checkpoint: {checkpoint}")
    fix_checkpoint_if_needed(checkpoint, debug)


@cli.command()
def merge(
        checkpoint: Annotated[
            Path,
            typer.Option(
                "--checkpoint",
                "-i",
                path_type=Path,
                dir_okay=False,
                exists=True,
                help="Path to a model checkpoint file",
            ),
        ],
        out_dir: Annotated[
            Optional[Path],
            typer.Option(
                "--out-dir",
                "-o",
                path_type=Path,
                file_okay=False,
                help="Target directory for converted model",
            ),
        ],
):
    """Convert a StableDiffusion checkpoint into an AnimationPipeline"""
    raise NotImplementedError("Sorry, haven't implemented this yet!")

    # if we have a checkpoint, convert it to HF automagically
    if checkpoint.is_file() and checkpoint.suffix in CKPT_EXTENSIONS:
        logger.info(f"Loading model from checkpoint: {checkpoint}")
        # check if we've already converted this model
        model_dir = pipeline_dir.joinpath(checkpoint.stem)
        if model_dir.joinpath("model_index.json").exists():
            # we have, so just use that
            logger.info("Found converted model in {model_dir}, will not convert")
            logger.info("Delete the output directory to re-run conversion.")
        else:
            # we haven't, so convert it
            logger.info("Converting checkpoint to HuggingFace pipeline...")
            g_pipeline, model_dir = checkpoint_to_pipeline(checkpoint)
    logger.info("Done!")


@cli.command(no_args_is_help=True)
def refine(
        frames_dir: Annotated[
            Path,
            typer.Argument(path_type=Path, file_okay=False, exists=True, help="Path to source frames directory"),
        ],
        config_path: Annotated[
            Optional[Path],
            typer.Option(
                "--config-path",
                "-c",
                path_type=Path,
                exists=True,
                readable=True,
                dir_okay=False,
                help="Path to a prompt configuration JSON file. default is frames_dir/../prompt.json",
            ),
        ] = None,
        interpolation_multiplier: Annotated[
            int,
            typer.Option(
                "--interpolation-multiplier",
                "-M",
                min=1,
                max=10,
                help="Interpolate with RIFE before generation. (I'll leave it as is, but I think interpolation after generation is sufficient).",
                rich_help_panel="Generation",
            ),
        ] = 1,
        tile_conditioning_scale: Annotated[
            float,
            typer.Option(
                "--tile",
                "-t",
                min=0,
                max=1.0,
                help="controlnet_tile conditioning scale",
                rich_help_panel="Generation",
            ),
        ] = 0.75,
        width: Annotated[
            int,
            typer.Option(
                "--width",
                "-W",
                min=-1,
                max=3840,
                help="Width of generated frames",
                rich_help_panel="Generation",
            ),
        ] = -1,
        height: Annotated[
            int,
            typer.Option(
                "--height",
                "-H",
                min=-1,
                max=2160,
                help="Height of generated frames",
                rich_help_panel="Generation",
            ),
        ] = -1,
        length: Annotated[
            int,
            typer.Option(
                "--length",
                "-L",
                min=-1,
                max=9999,
                help="Number of frames to generate. -1 means using all frames in frames_dir.",
                rich_help_panel="Generation",
            ),
        ] = -1,
        context: Annotated[
            Optional[int],
            typer.Option(
                "--context",
                "-C",
                min=1,
                max=32,
                help="Number of frames to condition on (default: max of <length> or 32). max for motion module v1 is 24",
                show_default=False,
                rich_help_panel="Generation",
            ),
        ] = None,
        overlap: Annotated[
            Optional[int],
            typer.Option(
                "--overlap",
                "-O",
                min=1,
                max=12,
                help="Number of frames to overlap in context (default: context//4)",
                show_default=False,
                rich_help_panel="Generation",
            ),
        ] = None,
        stride: Annotated[
            Optional[int],
            typer.Option(
                "--stride",
                "-S",
                min=0,
                max=8,
                help="Max motion stride as a power of 2 (default: 0)",
                show_default=False,
                rich_help_panel="Generation",
            ),
        ] = None,
        repeats: Annotated[
            int,
            typer.Option(
                "--repeats",
                "-r",
                min=1,
                max=99,
                help="Number of times to repeat the refine (default: 1)",
                show_default=False,
                rich_help_panel="Generation",
            ),
        ] = 1,
        device: Annotated[
            str,
            typer.Option("--device", "-d", help="Device to run on (cpu, cuda, cuda:id)", rich_help_panel="Advanced"),
        ] = "cuda",
        use_xformers: Annotated[
            bool,
            typer.Option(
                "--xformers",
                "-x",
                is_flag=True,
                help="Use XFormers instead of SDP Attention",
                rich_help_panel="Advanced",
            ),
        ] = False,
        force_half_vae: Annotated[
            bool,
            typer.Option(
                "--half-vae",
                is_flag=True,
                help="Force VAE to use fp16 (not recommended)",
                rich_help_panel="Advanced",
            ),
        ] = False,
        out_dir: Annotated[
            Path,
            typer.Option(
                "--out-dir",
                "-o",
                path_type=Path,
                file_okay=False,
                help="Directory for output folders (frames, gifs, etc)",
                rich_help_panel="Output",
            ),
        ] = Path("refine/"),
):
    """Create upscaled or improved video using pre-generated frames"""
    import shutil

    from PIL import Image

    from animatediff.rife.rife import rife_interpolate

    if not config_path:
        tmp = frames_dir.parent.joinpath("prompt.json")
        if tmp.is_file():
            config_path = tmp
        else:
            raise ValueError("config_path invalid.")

    org_frames = sorted(glob.glob(os.path.join(frames_dir, "[0-9]*.png"), recursive=False))
    W, H = Image.open(org_frames[0]).size

    if width == -1 and height == -1:
        width = W
        height = H
    elif width == -1:
        width = int(height * W / H) // 8 * 8
    elif height == -1:
        height = int(width * H / W) // 8 * 8
    else:
        pass

    if length == -1:
        length = len(org_frames)
    else:
        length = min(length, len(org_frames))

    config_path = config_path.absolute()
    logger.info(f"Using generation config: {path_from_cwd(config_path)}")
    project_setting = get_project_setting(config_path)

    save_dir = out_dir
    logger.info(f"Will save outputs to ./{path_from_cwd(save_dir)}")

    seeds = [get_random() for i in range(repeats)]

    rife_img_dir = None

    for repeat_count in range(repeats):
        if interpolation_multiplier > 1:
            rife_img_dir = save_dir.joinpath(f"{repeat_count:02d}_rife_frame")
            rife_img_dir.mkdir(parents=True, exist_ok=True)

            rife_interpolate(frames_dir, rife_img_dir, interpolation_multiplier)
            length *= interpolation_multiplier

            if project_setting.output:
                project_setting.output["fps"] *= interpolation_multiplier
            if project_setting.prompt_map:
                project_setting.prompt_map = {
                    str(int(i) * interpolation_multiplier): project_setting.prompt_map[i]
                    for i in project_setting.prompt_map
                }

            frames_dir = rife_img_dir

        controlnet_img_dir = save_dir.joinpath(f"{repeat_count:02d}_controlnet_image")

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
            c_dir = controlnet_img_dir.joinpath(c)
            c_dir.mkdir(parents=True, exist_ok=True)

        shutil.copytree(frames_dir, controlnet_img_dir.joinpath("controlnet_tile"), dirs_exist_ok=True)
        # TODO: fix
        shutil.copytree(frames_dir, controlnet_img_dir.joinpath("controlnet_openpose"), dirs_exist_ok=True)
        shutil.copytree(frames_dir, controlnet_img_dir.joinpath("controlnet_canny"), dirs_exist_ok=True)

        project_setting.controlnet_map["input_image_dir"] = os.path.relpath(controlnet_img_dir.absolute(), data_dir)
        project_setting.controlnet_map["is_loop"] = False

        if "controlnet_tile" in project_setting.controlnet_map:
            project_setting.controlnet_map["controlnet_tile"]["enable"] = True
            project_setting.controlnet_map["controlnet_tile"]["control_scale_list"] = []
            project_setting.controlnet_map["controlnet_tile"]["controlnet_conditioning_scale"] = tile_conditioning_scale

        if "controlnet_openpose" in project_setting.controlnet_map:
            project_setting.controlnet_map["controlnet_openpose"]["enable"] = True
            project_setting.controlnet_map["controlnet_openpose"]["control_scale_list"] = []
            project_setting.controlnet_map["controlnet_openpose"][
                "controlnet_conditioning_scale"
            ] = tile_conditioning_scale

        if "controlnet_canny" in project_setting.controlnet_map:
            project_setting.controlnet_map["controlnet_canny"]["enable"] = True
            project_setting.controlnet_map["controlnet_canny"]["control_scale_list"] = []
            project_setting.controlnet_map["controlnet_canny"][
                "controlnet_conditioning_scale"
            ] = tile_conditioning_scale

        else:
            project_setting.controlnet_map["controlnet_tile"] = {
                "enable": True,
                "use_preprocessor": True,
                "guess_mode": False,
                "controlnet_conditioning_scale": tile_conditioning_scale,
                "control_guidance_start": 0.0,
                "control_guidance_end": 1.0,
                "control_scale_list": [],
            }

        project_setting.seed = [seeds[repeat_count]]

        config_path = save_dir.joinpath(f"{repeat_count:02d}_prompt.json")
        config_path.write_text(project_setting.model_dump_json(indent=4), encoding="utf-8")

        generated_dir = generate(
            config_path=config_path,
            width=width,
            height=height,
            length=length,
            context=context,
            overlap=overlap,
            stride=stride,
            device=device,
            use_xformers=use_xformers,
            force_half_vae=force_half_vae,
            out_dir=save_dir,
        )

        interpolation_multiplier = 1

        torch.cuda.empty_cache()

        frames_dir = Path(glob.glob(os.path.join(generated_dir, "00-frames"), recursive=False)[0])

    if rife_img_dir:
        frames = sorted(glob.glob(os.path.join(rife_img_dir, "[0-9]*.png"), recursive=False))
        out_images = []
        for f in frames:
            out_images.append(Image.open(f))

        out_file = save_dir.joinpath("rife_only_for_comparison")
        save_output(out_images, rife_img_dir, out_file, project_setting.output, True, save_frames=None, save_video=None)

    logger.info(f"Refined results are output to {generated_dir}")
