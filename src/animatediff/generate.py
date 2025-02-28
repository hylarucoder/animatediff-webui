import glob
import logging
import os
import re
from collections import defaultdict
from functools import partial
from itertools import chain
from os import PathLike
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np
import torch
from controlnet_aux import LineartAnimeDetector
from controlnet_aux.processor import (
    MODELS,
    Processor as ControlnetPreProcessor,
)
from controlnet_aux.util import (
    HWC3,
    ade_palette,
    resize_image as aux_resize_image,
)
from diffusers import (
    AutoencoderKL,
    ControlNetModel,
    DiffusionPipeline,
    StableDiffusionControlNetImg2ImgPipeline,
    StableDiffusionPipeline,
    StableDiffusionXLPipeline,
)
from PIL import Image
from torchvision.datasets.folder import IMG_EXTENSIONS
from tqdm.rich import tqdm
from transformers import (
    AutoImageProcessor,
    CLIPImageProcessor,
    CLIPTextModel,
    CLIPTextModelWithProjection,
    CLIPTokenizer,
    UperNetForSemanticSegmentation,
)

from animatediff import get_dir
from animatediff.adw.schema import TPerformance
from animatediff.consts import CACHE_DIR, MODELS_DIR, path_mgr
from animatediff.dwpose import DWposeDetector
from animatediff.globals import check_interrupted
from animatediff.models.clip import CLIPSkipTextModel
from animatediff.models.unet import UNet3DConditionModel
from animatediff.pipelines import AnimationPipeline, load_text_embeddings
from animatediff.pipelines.lora import load_lcm_lora, load_lora_map
from animatediff.pipelines.pipeline_controlnet_img2img_reference import (
    StableDiffusionControlNetImg2ImgReferencePipeline,
)
from animatediff.schedulers import DiffusionScheduler, get_scheduler
from animatediff.schema import (
    TAnyControlnet,
    TControlnetMap,
    TControlnetRef,
    TGradualLatentHiresFixMap,
    TImg2imgMap,
    TIPAdapterMap,
    TOutput,
    TPreprocessor,
    TProjectSetting,
    TUpscaleConfig,
)
from animatediff.settings import InferenceConfig
from animatediff.utils.convert_from_ckpt import convert_ldm_vae_checkpoint
from animatediff.utils.model import ensure_motion_modules, get_checkpoint_weights, get_checkpoint_weights_sdxl
from animatediff.utils.util import (
    get_resized_image,
    get_resized_image2,
    get_resized_images,
    get_tensor_interpolation_method,
    prepare_animatediff_controlnet,
    prepare_dwpose,
    prepare_ip_adapter,
    prepare_ip_adapter_sdxl,
    prepare_lcm_lora,
    prepare_motion_module,
    save_frames,
    save_imgs,
    save_video,
)

try:
    import onnxruntime

    onnxruntime_installed = True
except:
    onnxruntime_installed = False

logger = logging.getLogger(__name__)

default_base_path = path_mgr.huggingface_pipeline / "stable-diffusion-v1-5"

re_clean_prompt = re.compile(r"[^\w\-, ]")

controlnet_preprocessor = {}


def load_safetensors_lora2(text_encoder, unet, lora_path, alpha=0.75, is_animatediff=True):
    from safetensors.torch import load_file

    from animatediff.utils.lora_diffusers import LoRANetwork, create_network_from_weights

    sd = load_file(lora_path)

    logger.debug("create LoRA network")
    lora_network: LoRANetwork = create_network_from_weights(
        text_encoder, unet, sd, multiplier=alpha, is_animatediff=is_animatediff
    )
    logger.debug("load LoRA network weights")
    lora_network.load_state_dict(sd, False)
    lora_network.merge_to(alpha)


def load_tensors(path: Path, framework="pt", device="cpu"):
    tensors = {}
    if path.suffix == ".safetensors":
        from safetensors import safe_open

        with safe_open(path, framework=framework, device=device) as f:
            for k in f.keys():
                tensors[k] = f.get_tensor(k)  # loads the full tensor given a key
    else:
        from torch import load

        tensors = load(path, device)
        if "state_dict" in tensors:
            tensors = tensors["state_dict"]
    return tensors


def load_motion_lora(unet, lora_path: Path, alpha=1.0):
    state_dict = load_tensors(lora_path)

    # directly update weight in diffusers model
    for key in state_dict:
        # only process lora down key
        if "up." in key:
            continue

        up_key = key.replace(".down.", ".up.")
        model_key = key.replace("processor.", "").replace("_lora", "").replace("down.", "").replace("up.", "")
        model_key = model_key.replace("to_out.", "to_out.0.")
        layer_infos = model_key.split(".")[:-1]

        curr_layer = unet
        try:
            while len(layer_infos) > 0:
                temp_name = layer_infos.pop(0)
                curr_layer = curr_layer.__getattr__(temp_name)
        except:
            logger.info(f"{model_key} not found")
            continue

        weight_down = state_dict[key]
        weight_up = state_dict[up_key]
        curr_layer.weight.data += alpha * torch.mm(weight_up, weight_down).to(curr_layer.weight.data.device)


class SegPreProcessor:
    def __init__(self):
        self.image_processor = AutoImageProcessor.from_pretrained("openmmlab/upernet-convnext-small")
        self.processor = UperNetForSemanticSegmentation.from_pretrained("openmmlab/upernet-convnext-small")

    def __call__(self, input_image, detect_resolution=512, image_resolution=512, output_type="pil", **kwargs):
        input_array = np.array(input_image, dtype=np.uint8)
        input_array = HWC3(input_array)
        input_array = aux_resize_image(input_array, detect_resolution)

        pixel_values = self.image_processor(input_array, return_tensors="pt").pixel_values

        with torch.no_grad():
            outputs = self.processor(pixel_values.to(self.processor.device))

        outputs.loss = outputs.loss.to("cpu") if outputs.loss is not None else outputs.loss
        outputs.logits = outputs.logits.to("cpu") if outputs.logits is not None else outputs.logits
        outputs.hidden_states = (
            outputs.hidden_states.to("cpu") if outputs.hidden_states is not None else outputs.hidden_states
        )
        outputs.attentions = outputs.attentions.to("cpu") if outputs.attentions is not None else outputs.attentions

        seg = self.image_processor.post_process_semantic_segmentation(outputs, target_sizes=[input_image.size[::-1]])[0]
        color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8)  # height, width, 3

        for label, color in enumerate(ade_palette()):
            color_seg[seg == label, :] = color

        color_seg = color_seg.astype(np.uint8)
        color_seg = aux_resize_image(color_seg, image_resolution)
        color_seg = Image.fromarray(color_seg)

        return color_seg


class NullPreProcessor:
    def __call__(self, input_image, **kwargs):
        return input_image


class BlurPreProcessor:
    def __call__(self, input_image, sigma=5.0, **kwargs):
        import cv2

        input_array = np.array(input_image, dtype=np.uint8)
        input_array = HWC3(input_array)

        dst = cv2.GaussianBlur(input_array, (0, 0), sigma)

        return Image.fromarray(dst)


class TileResamplePreProcessor:
    def resize(self, input_image, resolution):
        import cv2

        H, W, C = input_image.shape
        H = float(H)
        W = float(W)
        k = float(resolution) / min(H, W)
        H *= k
        W *= k
        img = cv2.resize(input_image, (int(W), int(H)), interpolation=cv2.INTER_LANCZOS4 if k > 1 else cv2.INTER_AREA)
        return img

    def __call__(self, input_image, down_sampling_rate=1.0, **kwargs):
        input_array = np.array(input_image, dtype=np.uint8)
        input_array = HWC3(input_array)

        H, W, C = input_array.shape

        target_res = min(H, W) / down_sampling_rate

        dst = self.resize(input_array, target_res)

        return Image.fromarray(dst)


controlnet_address_table = {
    "controlnet_tile": ["lllyasviel/control_v11f1e_sd15_tile"],
    "controlnet_lineart_anime": ["lllyasviel/control_v11p_sd15s2_lineart_anime"],
    "controlnet_ip2p": ["lllyasviel/control_v11e_sd15_ip2p"],
    "controlnet_openpose": ["lllyasviel/control_v11p_sd15_openpose"],
    "controlnet_softedge": ["lllyasviel/control_v11p_sd15_softedge"],
    "controlnet_shuffle": ["lllyasviel/control_v11e_sd15_shuffle"],
    "controlnet_depth": ["lllyasviel/control_v11f1p_sd15_depth"],
    "controlnet_canny": ["lllyasviel/control_v11p_sd15_canny"],
    "controlnet_inpaint": ["lllyasviel/control_v11p_sd15_inpaint"],
    "controlnet_lineart": ["lllyasviel/control_v11p_sd15_lineart"],
    "controlnet_mlsd": ["lllyasviel/control_v11p_sd15_mlsd"],
    "controlnet_normalbae": ["lllyasviel/control_v11p_sd15_normalbae"],
    "controlnet_scribble": ["lllyasviel/control_v11p_sd15_scribble"],
    "controlnet_seg": ["lllyasviel/control_v11p_sd15_seg"],
    "qr_code_monster_v1": ["monster-labs/control_v1p_sd15_qrcode_monster"],
    "qr_code_monster_v2": ["monster-labs/control_v1p_sd15_qrcode_monster", "v2"],
    "controlnet_mediapipe_face": ["CrucibleAI/ControlNetMediaPipeFace", "diffusion_sd15"],
    "animatediff_controlnet": ["crishhh/animatediff_controlnet", "controlnet_checkpoint.ckpt"],
}

controlnet_address_table_sdxl = {
    "controlnet_openpose": ["thibaud/controlnet-openpose-sdxl-1.0"],
    "controlnet_softedge": ["SargeZT/controlnet-sd-xl-1.0-softedge-dexined"],
    "controlnet_depth": ["diffusers/controlnet-depth-sdxl-1.0-small"],
    "controlnet_canny": ["diffusers/controlnet-canny-sdxl-1.0-small"],
    "controlnet_seg": ["SargeZT/sdxl-controlnet-seg"],
    "qr_code_monster_v1": ["monster-labs/control_v1p_sdxl_qrcode_monster"],
}


def is_valid_controlnet_type(type_str: str, is_sdxl: bool):
    if not is_sdxl:
        return type_str in controlnet_address_table
    else:
        return type_str in controlnet_address_table_sdxl


def load_animatediff_controlnet(addr, torch_dtype=torch.float16):
    prepare_animatediff_controlnet()
    controlnet_state_dict = torch.load(
        path_mgr.controlnet / "animatediff_controlnet" / addr, map_location="cuda", weights_only=True
    )
    model = ControlNetModel(cross_attention_dim=768)
    missing, _ = model.load_state_dict(controlnet_state_dict["state_dict"], strict=False)
    if len(missing) > 0:
        logger.info(f"ControlNetModel has missing keys: {missing}")
    return model.to(dtype=torch_dtype)


def create_controlnet_model(type_str, is_sdxl):
    if not is_sdxl:
        # TODO: better code
        if type_str in controlnet_address_table:
            addr = controlnet_address_table[type_str]
            if type_str == "animatediff_controlnet":
                return load_animatediff_controlnet(addr[1])
            if len(addr) == 1:
                return ControlNetModel.from_pretrained(addr[0], torch_dtype=torch.float16)
            else:
                return ControlNetModel.from_pretrained(addr[0], subfolder=addr[1], torch_dtype=torch.float16)
        else:
            raise ValueError(f"unknown controlnet type {type_str}")
    else:
        if type_str in controlnet_address_table_sdxl:
            addr = controlnet_address_table_sdxl[type_str]
            if len(addr) == 1:
                return ControlNetModel.from_pretrained(addr[0], torch_dtype=torch.float16)
            else:
                return ControlNetModel.from_pretrained(addr[0], subfolder=addr[1], torch_dtype=torch.float16)
        else:
            raise ValueError(f"unknown controlnet type {type_str}")


default_preprocessor_table = {
    "controlnet_lineart_anime": "lineart_anime",
    "controlnet_openpose": "openpose_full" if not onnxruntime_installed else "dwpose",
    "controlnet_softedge": "softedge_hedsafe",
    "controlnet_shuffle": "shuffle",
    "controlnet_depth": "depth_midas",
    "controlnet_canny": "canny",
    "controlnet_lineart": "lineart_realistic",
    "controlnet_mlsd": "mlsd",
    "controlnet_normalbae": "normal_bae",
    "controlnet_scribble": "scribble_pidsafe",
    "controlnet_seg": "upernet_seg",
    "controlnet_mediapipe_face": "mediapipe_face",
    "qr_code_monster_v1": "depth_midas",
    "qr_code_monster_v2": "depth_midas",
}


def create_preprocessor_from_name(pre_type):
    if pre_type == "dwpose":
        prepare_dwpose()
        return DWposeDetector()
    elif pre_type == "upernet_seg":
        return SegPreProcessor()
    elif pre_type == "blur":
        return BlurPreProcessor()
    elif pre_type == "tile_resample":
        return TileResamplePreProcessor()
    elif pre_type == "none":
        return NullPreProcessor()
    elif pre_type in MODELS:
        return ControlnetPreProcessor(pre_type)
    else:
        raise ValueError(f"unknown controlnet preprocessor type {pre_type}")


def create_default_preprocessor(type_str):
    if type_str in default_preprocessor_table:
        pre_type = default_preprocessor_table[type_str]
    else:
        pre_type = "none"

    return create_preprocessor_from_name(pre_type)


def get_preprocessor(controlnet_type, preprocessor_map: TPreprocessor, device_str="cpu"):
    """TODO: memory usage profiling."""
    if preprocessor_map and preprocessor_map.type:
        controlnet_preprocessor[controlnet_type] = create_preprocessor_from_name(preprocessor_map.type)

    if controlnet_type in controlnet_preprocessor:
        return controlnet_preprocessor[controlnet_type]

    if controlnet_type not in controlnet_preprocessor:
        controlnet_preprocessor[controlnet_type] = create_default_preprocessor(controlnet_type)

    cn_preprocessor = controlnet_preprocessor[controlnet_type]
    if hasattr(cn_preprocessor, "processor"):
        if hasattr(cn_preprocessor, "to"):
            cn_preprocessor.processor.to(device_str)

    if hasattr(cn_preprocessor, "to"):
        cn_preprocessor.to(device_str)

    return cn_preprocessor


def clear_controlnet_preprocessor(type_str=None):
    global controlnet_preprocessor
    if type_str is None:
        for t in controlnet_preprocessor:
            controlnet_preprocessor[t] = None
        controlnet_preprocessor = {}
        torch.cuda.empty_cache()
    else:
        controlnet_preprocessor[type_str] = None
        torch.cuda.empty_cache()


def create_pipeline_sdxl(
        base_model: Union[str, PathLike],
        model_config: TProjectSetting,
        infer_config: InferenceConfig,
        video_length: int = 16,
        motion_module_path=...,
) -> AnimationPipeline:
    # TODO: cast bug, remove this when fixed
    from animatediff.pipelines.sdxl_animation import AnimationPipeline
    from animatediff.sdxl_models.unet import UNet3DConditionModel

    logger.info("Loading tokenizer...")
    tokenizer: CLIPTokenizer = CLIPTokenizer.from_pretrained(base_model, subfolder="tokenizer")
    logger.info("Loading text encoder...")
    text_encoder: CLIPTextModel = CLIPTextModel.from_pretrained(
        base_model, subfolder="text_encoder", torch_dtype=torch.float16
    )
    logger.info("Loading VAE...")
    vae: AutoencoderKL = AutoencoderKL.from_pretrained(base_model, subfolder="vae")
    logger.info("Loading tokenizer two...")
    tokenizer_two = CLIPTokenizer.from_pretrained(base_model, subfolder="tokenizer_2")
    logger.info("Loading text encoder two...")
    text_encoder_two = CLIPTextModelWithProjection.from_pretrained(
        base_model, subfolder="text_encoder_2", torch_dtype=torch.float16
    )

    logger.info("Loading UNet...")
    unet: UNet3DConditionModel = UNet3DConditionModel.from_pretrained_2d(
        pretrained_model_path=base_model,
        motion_module_path=motion_module_path,
        subfolder="unet",
        unet_additional_kwargs=infer_config.unet_additional_kwargs,
    )

    # set up scheduler
    sched_kwargs = infer_config.noise_scheduler_kwargs
    scheduler = get_scheduler(model_config.scheduler, sched_kwargs)
    logger.info(f'Using scheduler "{model_config.scheduler}" ({scheduler.__class__.__name__})')

    # Load the checkpoint weights into the pipeline
    if model_config.checkpoint is not None:
        model_path = path_mgr.checkpoints / model_config.checkpoint
        logger.info(f"Loading weights from {model_path}")
        if model_path.is_file():
            logger.debug("Loading from single checkpoint file")
            unet_state_dict, tenc_state_dict, tenc2_state_dict, vae_state_dict = get_checkpoint_weights_sdxl(model_path)
        elif model_path.is_dir():
            logger.debug("Loading from Diffusers model directory")
            temp_pipeline = StableDiffusionXLPipeline.from_pretrained(model_path)
            unet_state_dict, tenc_state_dict, tenc2_state_dict, vae_state_dict = (
                temp_pipeline.unet.state_dict(),
                temp_pipeline.text_encoder.state_dict(),
                temp_pipeline.text_encoder_2.state_dict(),
                temp_pipeline.vae.state_dict(),
            )
            del temp_pipeline
        else:
            raise FileNotFoundError(f"model_path {model_path} is not a file or directory")

        # Load into the unet, TE, and VAE
        logger.info("Merging weights into UNet...")
        _, unet_unex = unet.load_state_dict(unet_state_dict, strict=False)
        if len(unet_unex) > 0:
            raise ValueError(f"UNet has unexpected keys: {unet_unex}")
        tenc_missing, _ = text_encoder.load_state_dict(tenc_state_dict, strict=False)
        if len(tenc_missing) > 0:
            raise ValueError(f"TextEncoder has missing keys: {tenc_missing}")
        tenc2_missing, _ = text_encoder_two.load_state_dict(tenc2_state_dict, strict=False)
        if len(tenc2_missing) > 0:
            raise ValueError(f"TextEncoder2 has missing keys: {tenc2_missing}")
        vae_missing, _ = vae.load_state_dict(vae_state_dict, strict=False)
        if len(vae_missing) > 0:
            raise ValueError(f"VAE has missing keys: {vae_missing}")
    else:
        logger.info("Using base model weights (no checkpoint/LoRA)")

    if model_config.vae:
        vae_path = path_mgr.vaes / model_config.vae
        logger.info(f"Loading vae from {vae_path}")

        if vae_path.is_dir():
            vae = AutoencoderKL.from_pretrained(vae_path)
        else:
            tensors = load_tensors(vae_path)
            tensors = convert_ldm_vae_checkpoint(tensors, vae.config)
            vae.load_state_dict(tensors)

    unet.to(torch.float16)
    text_encoder.to(torch.float16)
    text_encoder_two.to(torch.float16)

    del unet_state_dict
    del tenc_state_dict
    del tenc2_state_dict
    del vae_state_dict

    # motion lora
    for l in model_config.motion_lora_map:
        lora_path = path_mgr.motion_loras / l
        logger.info(f"loading motion lora {lora_path=}")
        if lora_path.is_file():
            logger.info(f"Loading motion lora {lora_path}")
            logger.info(f"alpha = {model_config.motion_lora_map[l]}")
            load_motion_lora(unet, lora_path, alpha=model_config.motion_lora_map[l])
        else:
            raise ValueError(f"{lora_path=} not found")

    logger.info("Creating AnimationPipeline...")
    pipeline = AnimationPipeline(
        vae=vae,
        text_encoder=text_encoder,
        text_encoder_2=text_encoder_two,
        tokenizer=tokenizer,
        tokenizer_2=tokenizer_two,
        unet=unet,
        scheduler=scheduler,
        controlnet_map=None,
    )

    del vae
    del text_encoder
    del text_encoder_two
    del tokenizer
    del tokenizer_two
    del unet

    torch.cuda.empty_cache()

    if model_config.apply_lcm_lora:
        prepare_lcm_lora()
        load_lcm_lora(pipeline, model_config.lcm_lora_scale, is_sdxl=True)

    load_lora_map(pipeline, model_config.lora_map, video_length, is_sdxl=True)

    # Load TI embeddings
    load_text_embeddings(pipeline, is_sdxl=True)

    return pipeline


def create_pipeline(
        base_model: Union[str, PathLike],
        project_setting: TProjectSetting,
        infer_config: InferenceConfig,
        video_length: int = 16,
        is_sdxl: bool = False,
) -> AnimationPipeline:
    """Create an AnimationPipeline from a pretrained model.
    Uses the base_model argument to load or download the pretrained reference pipeline model.
    """
    # make sure motion_module is a Path and exists
    logger.info("Checking motion module...")
    motion_module = path_mgr.motions / project_setting.motion
    if not (motion_module.exists() and motion_module.is_file()):
        prepare_motion_module()
        if not (motion_module.exists() and motion_module.is_file()):
            # check for safetensors version
            motion_module = motion_module.with_suffix(".safetensors")
            if not (motion_module.exists() and motion_module.is_file()):
                # download from HuggingFace Hub if not found
                ensure_motion_modules()
            if not (motion_module.exists() and motion_module.is_file()):
                # this should never happen, but just in case...
                raise FileNotFoundError(f"Motion module {motion_module} does not exist or is not a file!")

    if is_sdxl:
        return create_pipeline_sdxl(
            base_model=base_model,
            model_config=project_setting,
            infer_config=infer_config,
            video_length=video_length,
            motion_module_path=motion_module,
        )

    logger.info("Loading tokenizer...text encoder...VAE...UNet...")
    tokenizer: CLIPTokenizer = CLIPTokenizer.from_pretrained(base_model, subfolder="tokenizer")
    text_encoder: CLIPSkipTextModel = CLIPSkipTextModel.from_pretrained(base_model, subfolder="text_encoder")
    vae: AutoencoderKL = AutoencoderKL.from_pretrained(base_model, subfolder="vae")
    unet: UNet3DConditionModel = UNet3DConditionModel.from_pretrained_2d(
        pretrained_model_path=base_model,
        motion_module_path=motion_module,
        subfolder="unet",
        unet_additional_kwargs=infer_config.unet_additional_kwargs,
    )
    feature_extractor = CLIPImageProcessor.from_pretrained(base_model, subfolder="feature_extractor")

    # set up scheduler
    if project_setting.gradual_latent_hires_fix_map.enable:
        project_setting.scheduler = DiffusionScheduler.euler_a
        logger.warning("gradual_latent_hires_fix enable -> Change scheduler to euler_a")

    sched_kwargs = infer_config.noise_scheduler_kwargs
    scheduler = get_scheduler(project_setting.scheduler, sched_kwargs)
    logger.info(f'Using scheduler "{project_setting.scheduler}" ({scheduler.__class__.__name__})')

    # Load the checkpoint weights into the pipeline
    model_path = path_mgr.checkpoints / project_setting.checkpoint
    logger.info(f"Loading weights from {model_path}")
    if model_path.is_file():
        logger.debug("Loading from single checkpoint file")
        unet_state_dict, tenc_state_dict, vae_state_dict = get_checkpoint_weights(model_path)
    elif model_path.is_dir():
        logger.debug("Loading from Diffusers model directory")
        temp_pipeline = StableDiffusionPipeline.from_pretrained(model_path)
        unet_state_dict, tenc_state_dict, vae_state_dict = (
            temp_pipeline.unet.state_dict(),
            temp_pipeline.text_encoder.state_dict(),
            temp_pipeline.vae.state_dict(),
        )
        del temp_pipeline
    else:
        raise FileNotFoundError(f"model_path {model_path} is not a file or directory")

    # Load into the unet, TE, and VAE
    logger.info("Merging weights into UNet...")
    _, unet_unex = unet.load_state_dict(unet_state_dict, strict=False)
    if len(unet_unex) > 0:
        raise ValueError(f"UNet has unexpected keys: {unet_unex}")
    tenc_missing, _ = text_encoder.load_state_dict(tenc_state_dict, strict=False)
    if len(tenc_missing) > 0:
        raise ValueError(f"TextEncoder has missing keys: {tenc_missing}")
    vae_missing, _ = vae.load_state_dict(vae_state_dict, strict=False)
    if len(vae_missing) > 0:
        raise ValueError(f"VAE has missing keys: {vae_missing}")

    if project_setting.vae:
        vae_path = path_mgr.vaes / project_setting.vae
        logger.info(f"Loading vae from {vae_path}")

        if vae_path.is_dir():
            vae = AutoencoderKL.from_pretrained(vae_path)
        else:
            tensors = load_tensors(vae_path)
            tensors = convert_ldm_vae_checkpoint(tensors, vae.config)
            vae.load_state_dict(tensors)

    # motion lora
    for l in project_setting.motion_lora_map:
        lora_path = path_mgr.motion_loras / l
        logger.info(f"loading motion lora {lora_path=}")
        if lora_path.is_file():
            logger.info(f"Loading motion lora {lora_path}")
            logger.info(f"alpha = {project_setting.motion_lora_map[l]}")
            load_motion_lora(unet, lora_path, alpha=project_setting.motion_lora_map[l])
        else:
            raise ValueError(f"{lora_path=} not found")

    pipeline = AnimationPipeline(
        vae=vae,
        text_encoder=text_encoder,
        tokenizer=tokenizer,
        unet=unet,
        scheduler=scheduler,
        feature_extractor=feature_extractor,
        controlnet_map=None,
    )
    # project_setting.

    if project_setting.performance == TPerformance.QUALITY:
        pipeline.enable_freeu(0.9, 0.2, 1.5, 1.6)

    if project_setting.apply_lcm_lora:
        prepare_lcm_lora()
        load_lcm_lora(pipeline, project_setting.lcm_lora_scale, is_sdxl=False)

    load_lora_map(pipeline, project_setting.lora_map, video_length)

    # Load TI embeddings
    load_text_embeddings(pipeline)

    return pipeline


def load_controlnet_models(
        project_dir: Path, pipe: AnimationPipeline, project_setting: TProjectSetting, is_sdxl: bool = False
):
    controlnet_map = {}
    c_image_dir = project_dir / project_setting.controlnet_map.input_image_dir
    for c, cn in project_setting.controlnet_map.controlnets:
        if not cn.enable:
            continue
        if not is_valid_controlnet_type(c, is_sdxl):
            continue
        img_dir = c_image_dir / c
        cond_imgs = sorted(glob.glob(os.path.join(img_dir, "[0-9]*.png"), recursive=False))
        if not cond_imgs:
            continue
        logger.info(f"loading {c=} model")
        controlnet_map[c] = create_controlnet_model(c, is_sdxl)

    if not controlnet_map:
        controlnet_map = None

    pipe.controlnet_map = controlnet_map


def unload_controlnet_models(pipe: AnimationPipeline):
    # show_gpu("before uload controlnet")
    pipe.controlnet_map = None
    torch.cuda.empty_cache()
    # show_gpu("after unload controlnet")


def create_us_pipeline(
        model_config: TProjectSetting,
        infer_config: InferenceConfig,
        use_controlnet_ref: bool = False,
        use_controlnet_tile: bool = False,
        use_controlnet_line_anime: bool = False,
        use_controlnet_ip2p: bool = False,
) -> DiffusionPipeline:
    # set up scheduler
    sched_kwargs = infer_config.noise_scheduler_kwargs
    scheduler = get_scheduler(model_config.scheduler, sched_kwargs)
    logger.info(f'Using scheduler "{model_config.scheduler}" ({scheduler.__class__.__name__})')

    controlnet = []
    if use_controlnet_tile:
        controlnet.append(ControlNetModel.from_pretrained("lllyasviel/control_v11f1e_sd15_tile"))
    if use_controlnet_line_anime:
        controlnet.append(ControlNetModel.from_pretrained("lllyasviel/control_v11p_sd15s2_lineart_anime"))
    if use_controlnet_ip2p:
        controlnet.append(ControlNetModel.from_pretrained("lllyasviel/control_v11e_sd15_ip2p"))

    if len(controlnet) == 1:
        controlnet = controlnet[0]
    elif len(controlnet) == 0:
        controlnet = None

    # Load the checkpoint weights into the pipeline
    pipeline: DiffusionPipeline

    if model_config.checkpoint is not None:
        model_path = path_mgr.checkpoints / model_config.checkpoint
        logger.info(f"Loading weights from {model_path}")
        if model_path.is_file():

            def is_empty_dir(path):
                import os

                return len(os.listdir(path)) == 0

            save_path = CACHE_DIR.joinpath("huggingface/" + model_path.stem + "_" + str(model_path.stat().st_size))
            save_path.mkdir(exist_ok=True)
            if save_path.is_dir() and is_empty_dir(save_path):
                # StableDiffusionControlNetImg2ImgPipeline.from_single_file does not exist in version 18.2
                logger.debug("Loading from single checkpoint file")
                tmp_pipeline = StableDiffusionPipeline.from_single_file(
                    pretrained_model_link_or_path=str(model_path.absolute())
                )
                tmp_pipeline.save_pretrained(save_path, safe_serialization=True)
                del tmp_pipeline

            if use_controlnet_ref:
                pipeline = StableDiffusionControlNetImg2ImgReferencePipeline.from_pretrained(
                    save_path,
                    controlnet=controlnet,
                    local_files_only=False,
                    load_safety_checker=False,
                    safety_checker=None,
                )
            else:
                pipeline = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
                    save_path,
                    controlnet=controlnet,
                    local_files_only=False,
                    load_safety_checker=False,
                    safety_checker=None,
                )

        elif model_path.is_dir():
            logger.debug("Loading from Diffusers model directory")
            if use_controlnet_ref:
                pipeline = StableDiffusionControlNetImg2ImgReferencePipeline.from_pretrained(
                    model_path,
                    controlnet=controlnet,
                    local_files_only=True,
                    load_safety_checker=False,
                    safety_checker=None,
                )
            else:
                pipeline = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
                    model_path,
                    controlnet=controlnet,
                    local_files_only=True,
                    load_safety_checker=False,
                    safety_checker=None,
                )
        else:
            raise FileNotFoundError(f"model_path {model_path} is not a file or directory")
    else:
        raise ValueError("model_config.path is invalid")

    pipeline.scheduler = scheduler

    # lora
    for l in model_config.lora_map:
        lora_path = path_mgr.loras / l
        if lora_path.is_file():
            alpha = model_config.lora_map[l]
            if isinstance(alpha, dict):
                alpha = 0.75

            logger.info(f"Loading lora {lora_path}")
            logger.info(f"alpha = {alpha}")
            load_safetensors_lora2(pipeline.text_encoder, pipeline.unet, lora_path, alpha=alpha, is_animatediff=False)

    # Load TI embeddings
    load_text_embeddings(pipeline)

    return pipeline


def seed_everything(seed):
    import random

    import numpy as np

    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed % (2 ** 32))
    random.seed(seed)


@check_interrupted
def controlnet_preprocess(
        project_dir: Path,
        out_dir: Path,
        controlnet_map: TControlnetMap,
        width: int = 512,
        height: int = 512,
        duration: int = 16,
        device_str: Optional[str] = None,
        is_sdxl: bool = False,
):
    controlnet_image_map = defaultdict(dict)

    controlnet_type_map = {}

    c_image_dir = project_dir / controlnet_map.input_image_dir
    save_detectmap = controlnet_map.save_detectmap

    cache_dir = path_mgr.projects / project_dir / "cache"
    cache_dir.mkdir(exist_ok=True)

    @check_interrupted
    def processing_controlnet_images(cn_name, cn: TAnyControlnet):
        processed = False
        if isinstance(cn, TControlnetRef):
            return
        if not cn.enable:
            return
        if not is_valid_controlnet_type(cn_name, is_sdxl):
            return
        img_dir = c_image_dir / controlnet_name
        images_to_be_processing = sorted(glob.glob(os.path.join(img_dir, "[0-9]*.png"), recursive=False))
        if not images_to_be_processing:
            return
        preprocessor_config = controlnet.preprocessor

        for img_path in images_to_be_processing:
            frame_no = int(Path(img_path).stem)
            cache_image_path = os.path.join(cache_dir, f"{frame_no:08d}_{cn_name}.png")

            def has_cache():
                if not os.path.exists(cache_image_path):
                    return False
                original_img_mtime = os.path.getmtime(img_path)
                preprocessed_img_mtime = os.path.getmtime(cache_image_path)
                if original_img_mtime > preprocessed_img_mtime:
                    # If the original image isn't newer than the preprocessed one, use the preprocessed image
                    return False
                return True

            if frame_no > duration:
                continue
            if not cn.use_preprocessor:
                # TODO: fix
                # read cache if cache exists, use cache
                # if not, create cache
                if not has_cache():
                    controlnet_image_map[frame_no][cn_name] = get_resized_image2(img_path, 512)
                else:
                    controlnet_image_map[frame_no][cn_name] = Image.open(cache_image_path)

                controlnet_image_map[frame_no][cn_name].save(cache_image_path)
                continue

            # 检查缓存文件是否存在
            if has_cache():
                controlnet_image_map[frame_no][cn_name] = Image.open(cache_image_path)
                continue
            img = get_resized_image2(img_path, 512)
            preprocessed_img = get_preprocessor(cn_name, preprocessor_config)(img, **preprocessor_config.param)
            controlnet_image_map[frame_no][cn_name] = preprocessed_img
            preprocessed_img.save(cache_image_path)

        controlnet_type_map[cn_name] = {
            "controlnet_conditioning_scale": cn.controlnet_conditioning_scale,
            "control_guidance_start": cn.control_guidance_start,
            "control_guidance_end": cn.control_guidance_end,
            "control_scale_list": cn.control_scale_list,
            "guess_mode": cn.guess_mode,
        }

        if save_detectmap and processed:
            det_dir = out_dir.joinpath(f"{0:02d}_detectmap/{cn_name}")
            det_dir.mkdir(parents=True, exist_ok=True)

            for frame_no in controlnet_image_map:
                save_path = det_dir.joinpath(f"{frame_no:08d}.png")
                if cn_name in controlnet_image_map[frame_no]:
                    controlnet_image_map[frame_no][cn_name].save(save_path)

        clear_controlnet_preprocessor(cn_name)

    for controlnet_name, controlnet in controlnet_map.controlnets:
        processing_controlnet_images(controlnet_name, controlnet)

    clear_controlnet_preprocessor()

    controlnet_ref_map = None

    r = controlnet_map.controlnet_ref
    if r.enable:
        org_name = project_dir.joinpath(r.ref_image).stem
        ref_image = get_resized_image2(str(project_dir.joinpath(r.ref_image)), 512)

        if ref_image is not None:
            controlnet_ref_map = {
                "ref_image": ref_image,
                "style_fidelity": r["style_fidelity"],
                "attention_auto_machine_weight": r["attention_auto_machine_weight"],
                "gn_auto_machine_weight": r["gn_auto_machine_weight"],
                "reference_attn": r["reference_attn"],
                "reference_adain": r["reference_adain"],
                "scale_pattern": r["scale_pattern"],
            }

            if save_detectmap:
                det_dir = out_dir.joinpath(f"{0:02d}_detectmap/controlnet_ref")
                det_dir.mkdir(parents=True, exist_ok=True)
                save_path = det_dir.joinpath(f"{org_name}.png")
                ref_image.save(save_path)

    return controlnet_image_map, controlnet_type_map, controlnet_ref_map


def ip_adapter_preprocess(
        project_dir: Path,
        out_dir: Path,
        ip_adapter_config_map: TIPAdapterMap,
        width: int = 512,
        height: int = 512,
        duration: int = 16,
        is_sdxl: bool = False,
):
    ip_adapter_map = {}
    if not ip_adapter_config_map.enable:
        return ip_adapter_map

    processed = False

    resized_to_square = ip_adapter_config_map.resized_to_square
    image_dir = project_dir.joinpath(ip_adapter_config_map.input_image_dir)
    imgs = sorted(chain.from_iterable([glob.glob(os.path.join(image_dir, f"[0-9]*{ext}")) for ext in IMG_EXTENSIONS]))
    if len(imgs) > 0:
        prepare_ip_adapter_sdxl() if is_sdxl else prepare_ip_adapter()
        ip_adapter_map["images"] = {}
        for img_path in tqdm(imgs, desc="Preprocessing images (ip_adapter)"):
            frame_no = int(Path(img_path).stem)
            if frame_no < duration:
                if resized_to_square:
                    ip_adapter_map["images"][frame_no] = get_resized_image(img_path, 256, 256)
                else:
                    ip_adapter_map["images"][frame_no] = get_resized_image2(img_path, 256)
                processed = True

    if processed:
        ip_adapter_config_map.prompt_fixed_ratio = max(min(1.0, ip_adapter_config_map.prompt_fixed_ratio), 0)

        prompt_fixed_ratio = ip_adapter_config_map.prompt_fixed_ratio
        prompt_map = ip_adapter_map["images"]
        prompt_map = dict(sorted(prompt_map.items()))
        key_list = list(prompt_map.keys())
        for k0, k1 in zip(key_list, key_list[1:] + [duration]):
            k05 = k0 + round((k1 - k0) * prompt_fixed_ratio)
            if k05 == k1:
                k05 -= 1
            if k05 != k0:
                prompt_map[k05] = prompt_map[k0]
        ip_adapter_map["images"] = prompt_map

    if ip_adapter_config_map.save_input_image and processed:
        det_dir = out_dir.joinpath(f"{0:02d}_ip_adapter/")
        det_dir.mkdir(parents=True, exist_ok=True)
        for frame_no in tqdm(ip_adapter_map["images"], desc="Saving Preprocessed images (ip_adapter)"):
            save_path = det_dir.joinpath(f"{frame_no:08d}.png")
            ip_adapter_map["images"][frame_no].save(save_path)

    return ip_adapter_map if processed else None


def prompt_preprocess(
        prompt_config_map: Dict[str, Any],
        head_prompt: str,
        tail_prompt: str,
        prompt_fixed_ratio: float,
        video_length: int,
):
    prompt_map = {}
    for k in prompt_config_map.keys():
        if int(k) < video_length:
            pr = prompt_config_map[k]
            if head_prompt:
                pr = head_prompt + "," + pr
            if tail_prompt:
                pr = pr + "," + tail_prompt

            prompt_map[int(k)] = pr

    prompt_map = dict(sorted(prompt_map.items()))
    key_list = list(prompt_map.keys())
    for k0, k1 in zip(key_list, key_list[1:] + [video_length]):
        k05 = k0 + round((k1 - k0) * prompt_fixed_ratio)
        if k05 == k1:
            k05 -= 1
        if k05 != k0:
            prompt_map[k05] = prompt_map[k0]

    return prompt_map


def region_preprocess(
        project_dir: Path,
        out_dir: Path,
        project_setting: TProjectSetting,
        width: int = 512,
        height: int = 512,
        duration: int = 16,
        is_init_img_exist: bool = False,
        is_sdxl: bool = False,
):
    is_bg_init_img = False
    if is_init_img_exist:
        if project_setting.region_map:
            if "background" in project_setting.region_map:
                is_bg_init_img = project_setting.region_map["background"]["is_init_img"]

    region_condi_list = []

    condi_index = 0

    prev_ip_map = None

    if not is_bg_init_img:
        ip_map = ip_adapter_preprocess(
            project_dir, out_dir, project_setting.ip_adapter_map, width, height, duration, is_sdxl
        )

        if ip_map:
            prev_ip_map = ip_map

        condition_map = {
            "prompt_map": prompt_preprocess(
                project_setting.prompt_map,
                project_setting.head_prompt,
                project_setting.tail_prompt,
                project_setting.prompt_fixed_ratio,
                duration,
            ),
            "ip_adapter_map": ip_map,
        }

        region_condi_list.append(condition_map)

        bg_src = condi_index
        condi_index += 1
    else:
        bg_src = -1

    region_list = [{"mask_images": None, "src": bg_src, "crop_generation_rate": 0}]

    if project_setting.region_map:
        for r in project_setting.region_map:
            if r == "background":
                continue
            if project_setting.region_map[r]["enable"] is not True:
                continue
            region_dir = out_dir.joinpath(f"region_{int(r):05d}/")
            region_dir.mkdir(parents=True, exist_ok=True)

            mask_map = mask_preprocess(project_dir, project_setting.region_map[r], width, height, duration, region_dir)

            if not mask_map:
                continue

            if project_setting.region_map[r]["is_init_img"] is False:
                ip_map = ip_adapter_preprocess(
                    project_dir,
                    region_dir,
                    project_setting.region_map[r]["condition"]["ip_adapter_map"],
                    width,
                    height,
                    duration,
                    is_sdxl,
                )

                if ip_map:
                    prev_ip_map = ip_map

                condition_map = {
                    "prompt_map": prompt_preprocess(
                        project_setting.region_map[r]["condition"]["prompt_map"],
                        project_setting.region_map[r]["condition"]["head_prompt"],
                        project_setting.region_map[r]["condition"]["tail_prompt"],
                        project_setting.region_map[r]["condition"]["prompt_fixed_ratio"],
                        duration,
                    ),
                    "ip_adapter_map": ip_map,
                }

                region_condi_list.append(condition_map)

                src = condi_index
                condi_index += 1
            else:
                if is_init_img_exist is False:
                    logger.warning("'is_init_img' : true / BUT init_img is not exist -> ignore region")
                    continue
                src = -1

            region_list.append(
                {
                    "mask_images": mask_map,
                    "src": src,
                    "crop_generation_rate": project_setting.region_map[r]["crop_generation_rate"]
                    if "crop_generation_rate" in project_setting.region_map[r]
                    else 0,
                }
            )

    ip_adapter_config_map = None

    if prev_ip_map is not None:
        ip_adapter_config_map = {
            "scale": project_setting.ip_adapter_map.scale,
            "is_plus": project_setting.ip_adapter_map.is_plus,
            "is_plus_face": project_setting.ip_adapter_map.is_plus_face,
            "is_light": project_setting.ip_adapter_map.is_light,
            "is_full_face": project_setting.ip_adapter_map.is_full_face,
        }
        for c in region_condi_list:
            if c["ip_adapter_map"] is None:
                logger.info("fill map")
                c["ip_adapter_map"] = prev_ip_map

    # for c in region_condi_list:
    #    logger.info(f"{c['prompt_map']=}")

    if not region_condi_list:
        raise ValueError("erro! There is not a single valid region")

    return region_condi_list, region_list, ip_adapter_config_map


def img2img_preprocess(
        project_dir: Path,
        out_dir: Path,
        img2img_config_map: TImg2imgMap,
        width: int = 512,
        height: int = 512,
        duration: int = 16,
):
    img2img_map = {}

    processed = False

    if not img2img_config_map:
        return None
    if img2img_config_map.enable:
        image_dir = project_dir / img2img_config_map.init_img_dir
        imgs = sorted(glob.glob(os.path.join(image_dir, "[0-9]*.png"), recursive=False))
        if not imgs:
            return None
        img2img_map["images"] = {}
        img2img_map["denoising_strength"] = img2img_config_map["denoising_strength"]
        for img_path in tqdm(imgs, desc="Preprocessing images (img2img)"):
            frame_no = int(Path(img_path).stem)
            if frame_no < duration:
                img2img_map["images"][frame_no] = get_resized_image(img_path, width, height)
                processed = True

        if (img2img_config_map["save_init_image"] is True) and processed:
            det_dir = out_dir.joinpath(f"{0:02d}_img2img_init_img/")
            det_dir.mkdir(parents=True, exist_ok=True)
            for frame_no in tqdm(img2img_map["images"], desc="Saving Preprocessed images (img2img)"):
                save_path = det_dir.joinpath(f"{frame_no:08d}.png")
                img2img_map["images"][frame_no].save(save_path)

    return img2img_map if processed else None


def mask_preprocess(
        project_dir: Path,
        region_config_map: Optional[Dict[str, Any]] = None,
        width: int = 512,
        height: int = 512,
        duration: int = 16,
        out_dir: PathLike = ...,
):
    mask_map = {}

    processed = False
    size = None
    mode = None

    if region_config_map:
        image_dir = project_dir.joinpath(region_config_map["mask_dir"])
        imgs = sorted(glob.glob(os.path.join(image_dir, "[0-9]*.png"), recursive=False))
        if len(imgs) > 0:
            for img_path in tqdm(imgs, desc="Preprocessing images (mask)"):
                frame_no = int(Path(img_path).stem)
                if frame_no < duration:
                    mask_map[frame_no] = get_resized_image(img_path, width, height)
                    if size is None:
                        size = mask_map[frame_no].size
                        mode = mask_map[frame_no].mode

                    processed = True

        if processed:
            if 0 in mask_map:
                prev_img = mask_map[0]
            else:
                prev_img = Image.new(mode, size, color=0)

            for i in range(duration):
                if i in mask_map:
                    prev_img = mask_map[i]
                else:
                    mask_map[i] = prev_img

        if (region_config_map["save_mask"] is True) and processed:
            det_dir = out_dir.joinpath("mask/")
            det_dir.mkdir(parents=True, exist_ok=True)
            for frame_no in tqdm(mask_map, desc="Saving Preprocessed images (mask)"):
                save_path = det_dir.joinpath(f"{frame_no:08d}.png")
                mask_map[frame_no].save(save_path)

    return mask_map if processed else None


def wild_card_conversion(
        model_config: TProjectSetting,
):
    from animatediff.utils.wild_card import replace_wild_card

    wild_card_dir = get_dir("wildcards")
    for k in model_config.prompt_map.keys():
        model_config.prompt_map[k] = replace_wild_card(model_config.prompt_map[k], wild_card_dir)

    if model_config.head_prompt:
        model_config.head_prompt = replace_wild_card(model_config.head_prompt, wild_card_dir)
    if model_config.tail_prompt:
        model_config.tail_prompt = replace_wild_card(model_config.tail_prompt, wild_card_dir)

    model_config.prompt_fixed_ratio = max(min(1.0, model_config.prompt_fixed_ratio), 0)

    if model_config.region_map:
        for r in model_config.region_map:
            if r == "background":
                continue

            if "condition" in model_config.region_map[r]:
                c = model_config.region_map[r]["condition"]
                for k in c["prompt_map"].keys():
                    c["prompt_map"][k] = replace_wild_card(c["prompt_map"][k], wild_card_dir)

                if "head_prompt" in c:
                    c["head_prompt"] = replace_wild_card(c["head_prompt"], wild_card_dir)
                if "tail_prompt" in c:
                    c["tail_prompt"] = replace_wild_card(c["tail_prompt"], wild_card_dir)
                if "prompt_fixed_ratio" in c:
                    c["prompt_fixed_ratio"] = max(min(1.0, c["prompt_fixed_ratio"]), 0)


def save_output(
        pipeline_output,
        frame_dir: Path,
        out_file: Path,
        output_map: TOutput,
        no_frames: bool = False,
        save_frames=save_frames,
        save_video=None,
):
    output_format = "h264" if output_map.format == "mp4" else "h2654"
    output_fps = output_map.fps
    if save_frames:
        save_frames(pipeline_output, frame_dir)

    from animatediff.rife.ffmpeg import FfmpegEncoder, codec_extn

    out_file = out_file.with_suffix(f".{codec_extn(output_format)}")

    logger.info("Creating ffmpeg encoder...")
    encoder = FfmpegEncoder(
        frames_dir=frame_dir,
        out_file=out_file,
        codec=output_format,
        in_fps=output_fps,
        out_fps=output_fps,
        lossless=False,
        param=output_map.encode_param.model_dump(),
    )
    logger.info("Encoding interpolated frames with ffmpeg...")
    result = encoder.encode()
    logger.debug(f"ffmpeg result: {result}")


def run_inference(
        pipeline: AnimationPipeline,
        n_prompt: str = ...,
        seed: int = -1,
        steps: int = 25,
        guidance_scale: float = 7.5,
        unet_batch_size: int = 1,
        width: int = 512,
        height: int = 512,
        duration: int = 16,
        idx: int = 0,
        out_dir: PathLike = ...,
        context_frames: int = -1,
        context_stride: int = 3,
        context_overlap: int = 4,
        context_schedule: str = "uniform",
        clip_skip: int = 1,
        controlnet_map: TControlnetMap = None,
        controlnet_image_map: Optional[Dict[str, Any]] = None,
        controlnet_type_map: Optional[Dict[str, Any]] = None,
        controlnet_ref_map: Optional[Dict[str, Any]] = None,
        no_frames: bool = False,
        img2img_map: Optional[Dict[str, Any]] = None,
        ip_adapter_config_map: Optional[Dict[str, Any]] = None,
        region_list: Optional[List[Any]] = None,
        region_condi_list: Optional[List[Any]] = None,
        output_map: TOutput = None,
        is_single_prompt_mode: bool = False,
        is_sdxl: bool = False,
        apply_lcm_lora: bool = False,
        gradual_latent_map: TGradualLatentHiresFixMap = None,
):
    out_dir = Path(out_dir)  # ensure out_dir is a Path

    # Trim and clean up the prompt for filename use
    prompt_map = region_condi_list[0]["prompt_map"]
    prompt_tags = [
        re_clean_prompt.sub("", tag).strip().replace(" ", "-")
        for tag in prompt_map[list(prompt_map.keys())[0]].split(",")
    ]
    frame_dir = out_dir.joinpath(f"{idx:02d}-frames")
    out_file = out_dir.joinpath("video")

    def preview_callback(i: int, video: torch.Tensor, save_fn: Callable[[torch.Tensor], None], out_file: str) -> None:
        save_fn(video, out_file=Path(f"{out_file}_preview@{i}"))

    save_fn = partial(
        save_output,
        frame_dir=frame_dir,
        output_map=output_map,
        no_frames=no_frames,
        save_frames=partial(save_frames, show_progress=False),
        save_video=save_video,
    )
    callback = partial(preview_callback, save_fn=save_fn, out_file=out_file)

    seed_everything(seed)

    logger.info(f"{len( region_condi_list )=}")
    logger.info(f"{len( region_list )=}")

    pipeline_output = pipeline(
        negative_prompt=n_prompt,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        unet_batch_size=unet_batch_size,
        width=width,
        height=height,
        video_length=duration,
        return_dict=False,
        context_frames=context_frames,
        context_stride=context_stride + 1,
        context_overlap=context_overlap,
        context_schedule=context_schedule,
        clip_skip=clip_skip,
        controlnet_type_map=controlnet_type_map,
        controlnet_image_map=controlnet_image_map,
        controlnet_ref_map=controlnet_ref_map,
        controlnet_max_samples_on_vram=controlnet_map.max_samples_on_vram,
        controlnet_max_models_on_vram=controlnet_map.max_models_on_vram,
        controlnet_is_loop=controlnet_map.is_loop,
        img2img_map=img2img_map,
        ip_adapter_config_map=ip_adapter_config_map,
        region_list=region_list,
        region_condi_list=region_condi_list,
        interpolation_factor=1,
        is_single_prompt_mode=is_single_prompt_mode,
        apply_lcm_lora=apply_lcm_lora,
        gradual_latent_map=gradual_latent_map,
        callback=callback,
        callback_steps=output_map.preview_steps,
    )
    logger.info("Generation complete, saving...")

    save_fn(pipeline_output, out_file=out_file)

    logger.info(f"Saved sample to {out_file}")
    return pipeline_output


def run_upscale(
        project_dir: Path,
        project_setting: TProjectSetting,
        org_imgs: List[str],
        pipeline: AnimationPipeline,
        prompt_map: Optional[Dict[int, str]] = None,
        n_prompt: str = ...,
        seed: int = -1,
        steps: int = 25,
        strength: float = 0.5,
        guidance_scale: float = 7.5,
        clip_skip: int = 1,
        us_width: int = 512,
        us_height: int = 512,
        idx: int = 0,
        out_dir: Path = ...,
        use_controlnet_ref: bool = False,
        use_controlnet_tile: bool = False,
        use_controlnet_line_anime: bool = False,
        use_controlnet_ip2p: bool = False,
        no_frames: bool = False,
):
    upscale_config: TUpscaleConfig = project_setting.upscale_config
    output_map = project_setting.output
    from animatediff.utils.lpw_stable_diffusion import lpw_encode_prompt

    pipeline.set_progress_bar_config(disable=True)

    images = get_resized_images(org_imgs, us_width, us_height)

    steps = upscale_config.steps
    scheduler = upscale_config.scheduler
    guidance_scale = upscale_config.guidance_scale
    clip_skip = upscale_config.clip_skip
    strength = upscale_config.strength

    controlnet_conditioning_scale = []
    guess_mode = []
    control_guidance_start = []
    control_guidance_end = []

    # for controlnet tile
    if use_controlnet_tile:
        controlnet_conditioning_scale.append(upscale_config.controlnet_tile.controlnet_conditioning_scale)
        guess_mode.append(upscale_config.controlnet_tile.guess_mode)
        control_guidance_start.append(upscale_config.controlnet_tile.control_guidance_start)
        control_guidance_end.append(upscale_config.controlnet_tile.control_guidance_end)

    # for controlnet line_anime
    if use_controlnet_line_anime:
        controlnet_conditioning_scale.append(upscale_config.controlnet_line_anime.controlnet_conditioning_scale)
        guess_mode.append(upscale_config.controlnet_line_anime.guess_mode)
        control_guidance_start.append(upscale_config.controlnet_line_anime.control_guidance_start)
        control_guidance_end.append(upscale_config.controlnet_line_anime.control_guidance_end)

    # for controlnet ip2p
    if use_controlnet_ip2p:
        controlnet_conditioning_scale.append(upscale_config.controlnet_ip2p.controlnet_conditioning_scale)
        guess_mode.append(upscale_config.controlnet_ip2p.guess_mode)
        control_guidance_start.append(upscale_config.controlnet_ip2p.control_guidance_start)
        control_guidance_end.append(upscale_config.controlnet_ip2p.control_guidance_end)

    # for controlnet ref
    ref_image = None
    if use_controlnet_ref:
        if (
                not upscale_config.controlnet_ref.use_frame_as_ref_image
                and not upscale_config.controlnet_ref.use_1st_frame_as_ref_image
        ):
            ref_image = get_resized_images(
                [project_dir / upscale_config.controlnet_ref.ref_image], us_width, us_height
            )[0]

    generator = torch.manual_seed(seed)

    seed_everything(seed)

    prompt_embeds_map = {}
    prompt_map = dict(sorted(prompt_map.items()))

    do_classifier_free_guidance = guidance_scale > 1.0

    prompt_list = [prompt_map[key_frame] for key_frame in prompt_map.keys()]

    prompt_embeds, neg_embeds = lpw_encode_prompt(
        pipe=pipeline,
        prompt=prompt_list,
        do_classifier_free_guidance=do_classifier_free_guidance,
        negative_prompt=n_prompt,
    )

    if do_classifier_free_guidance:
        negative = neg_embeds.chunk(neg_embeds.shape[0], 0)
        positive = prompt_embeds.chunk(prompt_embeds.shape[0], 0)
    else:
        negative = [None]
        positive = prompt_embeds.chunk(prompt_embeds.shape[0], 0)

    for i, key_frame in enumerate(prompt_map):
        prompt_embeds_map[key_frame] = positive[i]

    key_first = list(prompt_map.keys())[0]
    key_last = list(prompt_map.keys())[-1]

    def get_current_prompt_embeds(center_frame: int = 0, video_length: int = 0):
        key_prev = key_last
        key_next = key_first

        for p in prompt_map.keys():
            if p > center_frame:
                key_next = p
                break
            key_prev = p

        dist_prev = center_frame - key_prev
        if dist_prev < 0:
            dist_prev += video_length
        dist_next = key_next - center_frame
        if dist_next < 0:
            dist_next += video_length

        if key_prev == key_next or dist_prev + dist_next == 0:
            return prompt_embeds_map[key_prev]

        rate = dist_prev / (dist_prev + dist_next)

        return get_tensor_interpolation_method()(prompt_embeds_map[key_prev], prompt_embeds_map[key_next], rate)

    line_anime_processor = LineartAnimeDetector.from_pretrained("lllyasviel/Annotators")

    out_images = []

    logger.info(f"{use_controlnet_tile=}")
    logger.info(f"{use_controlnet_line_anime=}")
    logger.info(f"{use_controlnet_ip2p=}")

    logger.info(f"{controlnet_conditioning_scale=}")
    logger.info(f"{guess_mode=}")
    logger.info(f"{control_guidance_start=}")
    logger.info(f"{control_guidance_end=}")

    for i, org_image in enumerate(tqdm(images, desc="Upscaling...")):
        cur_positive = get_current_prompt_embeds(i, len(images))

        #        logger.info(f"w {condition_image.size[0]}")
        #        logger.info(f"h {condition_image.size[1]}")
        condition_image = []

        if use_controlnet_tile:
            condition_image.append(org_image)
        if use_controlnet_line_anime:
            condition_image.append(line_anime_processor(org_image))
        if use_controlnet_ip2p:
            condition_image.append(org_image)

        if not use_controlnet_ref:
            out_image = pipeline(
                prompt_embeds=cur_positive,
                negative_prompt_embeds=negative[0],
                image=org_image,
                control_image=condition_image,
                width=org_image.size[0],
                height=org_image.size[1],
                strength=strength,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                generator=generator,
                controlnet_conditioning_scale=controlnet_conditioning_scale
                if len(controlnet_conditioning_scale) > 1
                else controlnet_conditioning_scale[0],
                guess_mode=guess_mode[0],
                control_guidance_start=control_guidance_start
                if len(control_guidance_start) > 1
                else control_guidance_start[0],
                control_guidance_end=control_guidance_end if len(control_guidance_end) > 1 else control_guidance_end[0],
            ).images[0]
        else:
            if upscale_config["controlnet_ref"]["use_1st_frame_as_ref_image"]:
                if i == 0:
                    ref_image = org_image
            elif upscale_config["controlnet_ref"]["use_frame_as_ref_image"]:
                ref_image = org_image

            out_image = pipeline(
                prompt_embeds=cur_positive,
                negative_prompt_embeds=negative[0],
                image=org_image,
                control_image=condition_image,
                width=org_image.size[0],
                height=org_image.size[1],
                strength=strength,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                generator=generator,
                controlnet_conditioning_scale=controlnet_conditioning_scale
                if len(controlnet_conditioning_scale) > 1
                else controlnet_conditioning_scale[0],
                guess_mode=guess_mode[0],
                # control_guidance_start= control_guidance_start,
                # control_guidance_end= control_guidance_end,
                ### for controlnet ref
                ref_image=ref_image,
                attention_auto_machine_weight=upscale_config["controlnet_ref"]["attention_auto_machine_weight"],
                gn_auto_machine_weight=upscale_config["controlnet_ref"]["gn_auto_machine_weight"],
                style_fidelity=upscale_config["controlnet_ref"]["style_fidelity"],
                reference_attn=upscale_config["controlnet_ref"]["reference_attn"],
                reference_adain=upscale_config["controlnet_ref"]["reference_adain"],
            ).images[0]

        out_images.append(out_image)

    # Trim and clean up the prompt for filename use
    prompt_tags = [
        re_clean_prompt.sub("", tag).strip().replace(" ", "-")
        for tag in prompt_map[list(prompt_map.keys())[0]].split(",")
    ]

    # generate the output filename and save the video
    out_file = out_dir.joinpath("video")

    frame_dir = out_dir.joinpath(f"{idx:02d}-frames-upscaled")

    save_output(out_images, frame_dir, out_file, output_map, no_frames, save_imgs, None)

    logger.info(f"Saved sample to {out_file}")

    return out_images
