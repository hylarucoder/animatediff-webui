import json
import os

import gradio as gr
import pydantic as pt

from animatediff.consts import (
    path_mgr,
)
from animatediff.settings import ModelConfig
from animatediff.utils.progressbar import pgr
from animatediff.utils.torch_compact import get_torch_device
from animatediff.utils.util import read_json


def group_by_n(l, n):
    for i in range(0, len(l), n):
        yield l[i: i + n]


BLANK_PLACEHOLDER = "---"


def get_models_endswith(d, endswith="safetensors"):
    return [f for f in os.listdir(d) if f.endswith(endswith)]


def get_projects():
    return [BLANK_PLACEHOLDER] + list(sorted([_.name for _ in path_mgr.projects.iterdir() if _.is_dir()]))


checkpoint_list = get_models_endswith(path_mgr.checkpoints)
if checkpoint_list:
    default_checkpoint = checkpoint_list[0]

lora_arr = [[BLANK_PLACEHOLDER, 0.7] for _ in range(5)]


class Preset(pt.BaseModel):
    name: str
    performance: str = "Speed"
    aspect_radio: str = "432x768 | 9:16"
    head_prompt: str = "masterpiece, best quality"
    tail_prompt: str = ""
    negative_prompt: str = "(worst quality, low quality:1.4),nudity,simple background,border,text, patreon,bed,bedroom,white background,((monochrome)),sketch,(pink body:1.4),7 arms,8 arms,4 arms"

    checkpoint: str = "majicmixRealistic_v7.safetensors"
    loras: list[list] = pt.Field(default_factory=lambda: lora_arr)
    motion: str = "mm_sd_v15_v2.ckpt"
    motion_lora: str | None = None

    fps: int = 8
    duration: int = 4
    seed: int = -1

    lcm: bool = False
    sampler: str = "k_dpmpp_sde"
    step: int = 20
    cfg: float = 7


preset_default = Preset(
    name="default",
)
preset_lcm = Preset(
    name="default - lcm",
    performance="Extreme Speed",
    aspect_radio="768x432 | 16:9",
)

preset_color = Preset(
    name="lcm + motion-lora + color fashion",
    performance="Extreme Speed",
    head_prompt="masterpiece,best quality, 1girl, walk,",
    tail_prompt="photorealistic,realistic,photography,ultra-detailed,1girl,full body,water,dress,looking at viewer,red dress,white hair,md colorful",
    lcm=True,
)
preset_color.loras[0] = ["釉彩·麻袋调色盘_v1.0.safetensors", 0.8]

presets = [
    preset_default,
    preset_lcm,
    preset_color,
]


def get_presets():
    return [preset.name for preset in presets]


controlnets = [
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
    "qr_code_monster_v1",
    "qr_code_monster_v2",
    "controlnet_mediapipe_face",
    # "controlnet_ref",
]


# open(project_setting.project_dir / "prompts.json", "wt").write(json.dumps(prompt_tmpl, indent=2))
# subprocess.Popen(f'start cmd /k call {project_dir}/gen_preview.bat', shell=True)


def render_ui():
    # main render
    with gr.Row():
        with gr.Column(scale=3):
            with gr.Row():
                with gr.Column():
                    ip_preset = gr.Dropdown(
                        label="Preset",
                        choices=get_presets(),
                        value=preset_default.name,
                        interactive=True,
                    )
                with gr.Column():
                    ip_project = gr.Textbox(
                        label="Project",
                        value="001-demo",
                        interactive=True,
                    )

        with gr.Column(scale=1):
            btn_new_project = gr.Button("New", variant="secondary")
            btn_refresh_project = gr.Button("Refresh", variant="secondary")

            @btn_refresh_project.click(
                inputs=[
                    ip_preset,
                    ip_project,
                ],
                outputs=[ip_preset, ip_project],
            )
            def refresh_preset_projects(project_name):
                return gr.update(choices=get_presets()), gr.update(value=project_name)

    with gr.Row():
        with gr.Column(scale=3):
            with gr.Tab(label="Preview"):
                preview_video = gr.Video(height=504, show_label=False, label="Preview", interactive=False)
            with gr.Tab(label="Image Prompt"):
                with gr.Row():
                    gr.Gallery()
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.Checkbox(value=True, label="Preprocess Image")
                        gr.Checkbox(value=True, label="Rename Images")
                        gr.Number(value=16, precision=0, label="Rename Interval")
                    with gr.Column(scale=1):
                        gr.Files(container=False)
            with gr.Tab(label="Controlnet"):
                with gr.Row():
                    gr.Gallery()
                    gr.Gallery()
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Dropdown(
                            choices=[BLANK_PLACEHOLDER] + controlnets,
                            label="Controlnets",
                            multiselect=True,
                        )
                        gr.Checkbox(value=True, label="Preprocess")
                    with gr.Column(scale=4):
                        gr.Files(container=False)
            with gr.Tab(label="File Explorer"):
                # gr.FileExplorer("projects/**/*.*")
                ...

            with gr.Row():
                with gr.Column(scale=1):
                    ...

            with gr.Tab(label="Draft"):
                with gr.Row():
                    with gr.Column(scale=3):
                        ...
                    with gr.Column(scale=1):
                        generate_button = gr.Button(value="Generate", visible=True)
                        stop_button = gr.Button(
                            "Stop",
                            interactive=False,
                        )
            with gr.Tab(label="Upscale"):
                with gr.Row():
                    with gr.Column(scale=3):
                        ip_upscale = gr.Dropdown(
                            label="draft", choices=[BLANK_PLACEHOLDER], value=BLANK_PLACEHOLDER, interactive=True
                        )
                    with gr.Column(scale=1):
                        btn_refresh = gr.Button("🔁")
                        btn_upscale = gr.Button("Upscale")

                @btn_refresh.click(inputs=ip_project, outputs=ip_upscale)
                def fn_refresh_project_draft(project_name):
                    frames_dirs = list(
                        sorted([_.name for _ in (path_mgr.projects / project_name / "draft").iterdir() if _.is_dir()])
                    )
                    return gr.update(
                        choices=[BLANK_PLACEHOLDER] + frames_dirs,
                        value=frames_dirs[-1] if frames_dirs else BLANK_PLACEHOLDER,
                        interactive=True,
                    )

                @btn_upscale.click(
                    inputs=[
                        ip_project,
                        ip_upscale,
                    ],
                    outputs=ip_upscale,
                )
                def fn_upscale(project, upscale_dir):
                    from animatediff.cli import tile_upscale

                    tile_upscale(
                        frames_dir=path_mgr.projects / project / "draft" / upscale_dir / "00-frames",
                        config_path=path_mgr.projects / project / "prompts.json",
                        width=1024,
                        height=-1,
                        device="cuda",
                        use_xformers=False,
                        force_half_vae=False,
                        out_dir=path_mgr.projects / project / "upscaled",
                        no_frames=False,
                    )

                # state.frames_dirs = frames_dirs = list(
                #     sorted([_.name for _ in (path_mgr.projects / project_name / "draft").iterdir() if _.is_dir()])
                # )
            with gr.Tab(label="Refine"):
                gr.Dropdown("settings")
            gr.Button("🔁")

        with gr.Column(scale=1):
            with gr.Tab(label="Setting"):
                with gr.Row():
                    ip_performance = gr.Radio(
                        [
                            "Speed",
                            "Quality",
                            "Extreme Speed",
                        ],
                        label="Performance",
                        value=preset_default.performance,
                        interactive=True,
                    )

                with gr.Row():
                    ip_aspect_radio = gr.Radio(
                        [
                            "768x432 | 16:9",
                            "768x576 | 4:3",
                            "600x600 | 1:1",
                            "432x768 | 9:16",
                            "576x768 | 3:4",
                        ],
                        label="Aspect Ratios",
                        value=preset_default.aspect_radio,
                        interactive=True,
                    )
                with gr.Row():
                    ip_head_prompt = gr.Textbox(
                        label="Head Prompt",
                        placeholder="Type prompt here. 1: 1girl; 2:2girl",
                        autofocus=True,
                        lines=3,
                    )
                    ip_tail_prompt = gr.Textbox(
                        label="Tail Prompt",
                        placeholder="Type prompt here.",
                        autofocus=True,
                        lines=3,
                    )
                with gr.Row():
                    ip_negative_prompt = gr.Textbox(
                        label="Negative Prompt", lines=2, value=preset_default.negative_prompt, interactive=True
                    )
                with gr.Row():
                    ip_fps = gr.Number(
                        label="FPS",
                        value=preset_default.fps,
                        precision=0,
                        minimum=8,
                        maximum=24,
                    )
                    ip_duration = gr.Number(
                        label="Duration(s)",
                        value=preset_default.duration,
                        minimum=1,
                        maximum=300,
                        precision=0,
                    )

                with gr.Row():
                    with gr.Group():
                        cb_random_seed = gr.Checkbox(label="random", interactive=True, value=True)
                        ip_seed = gr.Number(label="Seed", value=preset_default.seed, precision=0)

            with gr.Tab(label="Model"):
                with gr.Row():
                    ip_checkpoint = gr.Dropdown(
                        value=preset_default.checkpoint,
                        label="CheckPoint",
                        choices=checkpoint_list,
                        interactive=True,
                    )

                with gr.Row():
                    ip_motion = gr.Dropdown(
                        label="Motion",
                        choices=get_models_endswith(
                            path_mgr.motions,
                            endswith="ckpt",
                        ),
                        value="mm_sd_v15_v2.ckpt",
                        interactive=True,
                    )

                    ip_motion_loras = gr.Dropdown(
                        multiselect=True,
                        label="Motion LoRA",
                        choices=get_models_endswith(path_mgr.motion_loras, endswith="ckpt"),
                        value=[BLANK_PLACEHOLDER],
                        interactive=True,
                    )
                with gr.Row():
                    with gr.Group():
                        ip_lora_items = []
                        # TODO: refresh state
                        for i in range(5):
                            with gr.Row():
                                lora_model = gr.Dropdown(
                                    label=f"LoRA {i + 1}",
                                    choices=get_models_endswith(
                                        path_mgr.loras,
                                    ),
                                    value=BLANK_PLACEHOLDER,
                                    interactive=True,
                                )
                                lora_weight = gr.Slider(
                                    label="Weight",
                                    minimum=-2,
                                    maximum=2,
                                    step=0.1,
                                    value=0.7,
                                )

                                ip_lora_items += [lora_model, lora_weight]

            with gr.Tab(label="Setting"):
                gr.Slider(minimum=1, maximum=100, value=50, label="CFG")

    def fn_generate(
            project,
            performance,
            aspect_radio,
            head_prompt,
            tail_prompt,
            negative_prompt,
            fps,
            duration,
            seed,
            checkpoint,
            motion,
            motion_loras,
            *lora_items,
            data=None,
            progress=gr.Progress(
                track_tqdm=True,
            ),
    ):
        project_dir = path_mgr.projects / project
        global_config = ModelConfig(**read_json(path_mgr.demo_prompt_json))
        project_dir.mkdir(exist_ok=True)
        pgr.set_pgr(progress)
        pgr(1, desc="Step 01/08: Apply Configuration...")
        if performance == "Speed":
            # 感觉要重写
            global_config.lcm_lora_scale = 1
            global_config.apply_lcm_lora = False
            global_config.steps = 20
            global_config.guidance_scale = 8
        elif performance == "Quality":
            global_config.lcm_lora_scale = 1
            global_config.apply_lcm_lora = False
            global_config.steps = 40
            global_config.guidance_scale = 8
        elif performance == "Extreme Speed":
            global_config.lcm_lora_scale = 1
            global_config.apply_lcm_lora = True
            global_config.steps = 8
            global_config.guidance_scale = 1.8

        global_config.head_prompt = head_prompt
        global_config.tail_prompt = tail_prompt
        global_config.n_prompt = [negative_prompt]

        global_config.lora_map = {
            lora[0]: lora[1] for lora in group_by_n(lora_items, 2) if lora[0] != BLANK_PLACEHOLDER
        }

        global_config.seed = [seed]
        global_config.checkpoint = checkpoint
        global_config.motion = motion
        global_config.motion_lora_map = {}
        global_config.prompt_map = {
            "0": global_config.head_prompt,
        }
        global_config.output = {
            "format": "mp4",
            "fps": 8,
            "encode_param": {
                "crf": 10
            }
        }
        open(project_dir / "prompts.json", "wt", encoding="utf-8").write(
            global_config.model_dump_json(
                indent=2,
            )
        )

        from animatediff.cli import generate

        save_dir = generate(
            config_path=project_dir / "prompts.json",
            width=432,
            height=768,
            length=fps * duration,
            # TODO: check something
            context=16,
            overlap=16 // 4,
            stride=0,
            repeats=1,
            device=get_torch_device(),
            use_xformers=False,
            force_half_vae=False,
            out_dir=project_dir / "draft",
            no_frames=False,
            save_merged=False,
        )
        return save_dir / "video.mp4"

    generate_button.click(
        lambda: (gr.update(visible=True, interactive=True), gr.update(visible=False)),
        inputs=[],
        outputs=[
            stop_button,
            generate_button,
        ],
    ).then(
        fn_generate,
        inputs=[
            ip_project,
            ip_performance,
            ip_aspect_radio,
            ip_head_prompt,
            ip_tail_prompt,
            ip_negative_prompt,
            ip_fps,
            ip_duration,
            ip_seed,
            ip_checkpoint,
            ip_motion,
            ip_motion_loras,
            *ip_lora_items,
        ],
        outputs=[preview_video],
    ).then(
        lambda: (gr.update(visible=False, interactive=False), gr.update(visible=True)),
        inputs=[],
        outputs=[
            stop_button,
            generate_button,
        ],
    )

    def apply_preset(
            preset_name,
    ):
        preset = next((_ for _ in presets if _.name == preset_name), None)
        loras_gr = []
        for lora in preset.loras:
            loras_gr.append(gr.update(value=lora[0]))
            loras_gr.append(gr.update(value=lora[1]))
        return (
            gr.update(
                value=preset.performance,
            ),
            gr.update(
                value=preset.aspect_radio,
            ),
            gr.update(
                value=preset.head_prompt,
            ),
            gr.update(
                value=preset.tail_prompt,
            ),
            gr.update(
                value=preset.negative_prompt,
            ),
            gr.update(
                value=preset.fps,
            ),
            gr.update(
                value=preset.duration,
            ),
            gr.update(
                value=preset.seed,
            ),
            gr.update(
                value=preset.checkpoint,
            ),
            gr.update(
                value=preset.motion,
            ),
            gr.update(
                value=preset.motion_lora,
            ),
            *loras_gr,
        )

    ip_preset.change(
        apply_preset,
        inputs=[
            ip_preset,
        ],
        outputs=[
            ip_performance,
            ip_aspect_radio,
            ip_head_prompt,
            ip_tail_prompt,
            ip_negative_prompt,
            ip_fps,
            ip_duration,
            ip_seed,
            ip_checkpoint,
            ip_motion,
            ip_motion_loras,
            *ip_lora_items,
        ],
    )


with gr.Blocks(
        title="Animatediff WebUI",
        css="""
        video {
            height: 504px !important;
        }
        """,
        theme=gr.themes.Default(
            spacing_size="sm",
            text_size="sm",
        ),
) as demo:
    render_ui()

demo.launch(server_name="0.0.0.0")
