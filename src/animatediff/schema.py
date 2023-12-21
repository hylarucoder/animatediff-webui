from __future__ import annotations

from typing import Any, Union

import pydantic as pt
from pydantic import BaseModel, Field

from animatediff.adw.schema import TPerformance


def normal_scale_list():
    return [0.5, 0.4, 0.3, 0.2, 0.1]


class TIPAdapterMap(BaseModel):
    enable: bool = True
    # TODO: input image dir
    input_image_dir: str = "./00_ip_adapter"
    prompt_fixed_ratio: float = 0.5
    save_input_image: bool = False
    resized_to_square: bool = True
    scale: float = 1.0
    is_plus_face: bool = False
    is_full_face: bool = False
    is_plus: bool = True
    is_light: bool = False


class TPreprocessor(BaseModel):
    type: str | None = None
    param: dict[str, Any] = Field({})


class TControlnetTile(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=list)


class TControlnetIp2p(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=list)


class TControlnetLineartAnime(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TControlnetOpenpose(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor(type="dwpose", param={"size": 512})
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=list)


class TControlnetSoftedge(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TControlnetShuffle(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TControlnetDepth(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TControlnetCanny(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TControlnetInpaint(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)  # TODO: wierd


class TControlnetLineart(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TControlnetMlsd(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TControlnetNormalbae(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TControlnetScribble(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TControlnetSeg(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TAnimatediffControlnet(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TQrCodeMonsterV1(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TQrCodeMonsterV2(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TControlnetMediapipeFace(BaseModel):
    enable: bool = True
    use_preprocessor: bool = True
    preprocessor: TPreprocessor = TPreprocessor()
    guess_mode: bool = False
    controlnet_conditioning_scale: float = 1.0
    control_guidance_start: float = 0.0
    control_guidance_end: float = 1.0
    control_scale_list: list[float] = pt.Field(default_factory=normal_scale_list)


class TControlnetRef(BaseModel):
    enable: bool = False
    ref_image: str = ""
    attention_auto_machine_weight: float = 0.3
    gn_auto_machine_weight: float = 0.3
    style_fidelity: float = 0.5
    reference_attn: bool = True
    reference_adain: bool = False
    scale_pattern: list[float] = pt.Field(default_factory=lambda: [1.0])


class TControlnetMap(BaseModel):
    input_image_dir: str = "./00_controlnet"
    max_samples_on_vram: int = 200
    max_models_on_vram: int = 3
    save_detectmap: bool = True
    preprocess_on_gpu: bool = True
    is_loop: bool = True
    controlnet_tile: TControlnetTile = pt.Field(default_factory=lambda: TControlnetTile())
    controlnet_ip2p: TControlnetIp2p = pt.Field(default_factory=lambda: TControlnetIp2p())
    controlnet_lineart_anime: TControlnetLineartAnime = pt.Field(default_factory=lambda: TControlnetLineartAnime())
    controlnet_openpose: TControlnetOpenpose = pt.Field(default_factory=lambda: TControlnetOpenpose())
    controlnet_softedge: TControlnetSoftedge = pt.Field(default_factory=lambda: TControlnetSoftedge())
    controlnet_shuffle: TControlnetShuffle = pt.Field(default_factory=lambda: TControlnetShuffle())
    controlnet_depth: TControlnetDepth = pt.Field(default_factory=lambda: TControlnetDepth())
    controlnet_canny: TControlnetCanny = pt.Field(default_factory=lambda: TControlnetCanny())
    controlnet_inpaint: TControlnetInpaint = pt.Field(default_factory=lambda: TControlnetInpaint())
    controlnet_lineart: TControlnetLineart = pt.Field(default_factory=lambda: TControlnetLineart())
    controlnet_mlsd: TControlnetMlsd = pt.Field(default_factory=lambda: TControlnetMlsd())
    controlnet_normalbae: TControlnetNormalbae = pt.Field(default_factory=lambda: TControlnetNormalbae())
    controlnet_scribble: TControlnetScribble = pt.Field(default_factory=lambda: TControlnetScribble())
    controlnet_seg: TControlnetSeg = pt.Field(default_factory=lambda: TControlnetSeg())
    qr_code_monster_v1: TQrCodeMonsterV1 = pt.Field(default_factory=lambda: TQrCodeMonsterV1())
    qr_code_monster_v2: TQrCodeMonsterV2 = pt.Field(default_factory=lambda: TQrCodeMonsterV2())
    controlnet_mediapipe_face: TControlnetMediapipeFace = pt.Field(default_factory=lambda: TControlnetMediapipeFace())
    animatediff_controlnet: TAnimatediffControlnet = pt.Field(default_factory=lambda: TAnimatediffControlnet())
    controlnet_ref: TControlnetRef = pt.Field(default_factory=lambda: TControlnetRef())

    @property
    def controlnets(self) -> list[tuple[str, TAnyControlnet]]:
        controlnet_items = []
        for k, v in self.model_dump().items():
            if k.startswith("controlnet_") or k in [
                "qr_code_monster_v1",
                "qr_code_monster_v2",
                "animatediff_controlnet",
            ]:
                controlnet_items.append((k, getattr(self, k)))
        return controlnet_items


TAnyControlnet = Union[
    TControlnetTile,
    TControlnetIp2p,
    TControlnetLineartAnime,
    TControlnetOpenpose,
    TControlnetSoftedge,
    TControlnetShuffle,
    TControlnetDepth,
    TControlnetCanny,
    TControlnetInpaint,
    TControlnetLineart,
    TControlnetMlsd,
    TControlnetNormalbae,
    TControlnetScribble,
    TControlnetSeg,
    TQrCodeMonsterV1,
    TQrCodeMonsterV2,
    TControlnetMediapipeFace,
    TControlnetRef,
]


class TUpscaleControlnetRef(BaseModel):
    enable: bool = False
    use_frame_as_ref_image: bool = False
    use_1st_frame_as_ref_image: bool = False
    ref_image: str = ""
    attention_auto_machine_weight: float = 1.0
    gn_auto_machine_weight: float = 1.0
    style_fidelity: float = 0.25
    reference_attn: bool = True
    reference_adain: bool = True


class TUpscaleConfig(BaseModel):
    scheduler: str = "k_dpmpp_sde"
    steps: int = 20
    strength: float = 0.5
    guidance_scale: int = 10
    controlnet_tile: TControlnetTile = pt.Field(default_factory=lambda: TControlnetTile())
    controlnet_line_anime: TControlnetLineartAnime = pt.Field(default_factory=lambda: TControlnetLineartAnime())
    controlnet_ip2p: TControlnetIp2p = pt.Field(default_factory=lambda: TControlnetIp2p())
    controlnet_ref: TUpscaleControlnetRef = pt.Field(default_factory=lambda: TUpscaleControlnetRef())


class TEncodeParam(BaseModel):
    crf: int = 10


class TOutput(BaseModel):
    preview_steps: list[int] = pt.Field(default_factory=lambda: [10])
    format: str = "mp4"
    fps: int = 8
    encode_param: TEncodeParam = pt.Field(default_factory=lambda: TEncodeParam())


class TImg2imgMap(BaseModel):
    enable: bool = False
    init_img_dir: str = "./00_img2img"
    save_init_image: bool = False
    denoising_strength: float = 0.7


class TGradualLatentHiresFixMap(BaseModel):
    enable: bool = (True,)
    scale: dict[str, float] = Field({"0": 0.5, "0.7": 1.0})
    reverse_steps: int = 5
    noise_add_count: int = 3


class TProjectSetting(BaseModel):
    performance: TPerformance = TPerformance.SPEED
    apply_lcm_lora: bool = False
    lcm_lora_scale: float = 1.0
    region_map: dict[str, float] = Field(default_factory=dict)
    is_single_prompt_mode: bool = False
    name: str = "100-demo"
    vae: str = ""
    checkpoint: str = "majicmixRealistic_v7.safetensors"
    motion: str = "mm_sd_v15_v2.ckpt"
    compile: bool = False
    gradual_latent_hires_fix_map: TGradualLatentHiresFixMap = pt.Field(
        default_factory=lambda: TGradualLatentHiresFixMap()
    )
    tensor_interpolation_slerp: bool = Field(False)
    seed: list[int] = pt.Field(default_factory=lambda: [-1])
    scheduler: str = "k_dpmpp_sde"
    steps: int = 20
    guidance_scale: float = 7.5
    unet_batch_size: int = 1
    clip_skip: int = 2
    prompt_fixed_ratio: float = 0.5
    head_prompt: str = "masterpiece"
    prompt_map: dict[str, str] = Field({})
    tail_prompt: str = ""
    n_prompt: list[str] = pt.Field(default_factory=lambda: [])
    lora_map: dict[str, float] = Field(default_factory=dict)
    motion_lora_map: dict[str, float] = Field(default_factory=dict)
    ip_adapter_map: TIPAdapterMap = pt.Field(default_factory=lambda: TIPAdapterMap())
    controlnet_map: TControlnetMap = pt.Field(default_factory=lambda: TControlnetMap())
    upscale_config: TUpscaleConfig = pt.Field(default_factory=lambda: TUpscaleConfig())
    output: TOutput = pt.Field(default_factory=lambda: TOutput())
    img2img_map: TImg2imgMap = Field(default_factory=lambda: TImg2imgMap())


if __name__ == "__main__":
    t = TProjectSetting()
    print(t.model_dump())
