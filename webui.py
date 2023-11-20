import json
import os
import shutil
import time
from pathlib import Path

import gradio as gr
import tqdm
from pydantic import BaseModel

from animatediff.consts import (
    REPO_DIR,
    TEMPLATES_DIR,
    path_mgr,
)
from animatediff.settings import ModelConfig
from animatediff.utils.util import read_json

BLANK_PLACEHOLDER = "---"


class WorkflowState(BaseModel):
    interval: int = 16
    max_frames: int = 160


class GeneralSetting(BaseModel):
    frames: int = 8


class ProjectSetting(BaseModel):
    project_name: str
    project_dir: Path
    template_dir: Path
    template_prompts_dir: Path


project_setting = ProjectSetting(
    project_dir=REPO_DIR,  # placeholder
    project_name="demo_001",
    template_dir=TEMPLATES_DIR / "001_t2v",
    template_prompts_dir=TEMPLATES_DIR / "proj_000_template_t2v/prompts.json",
)

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


def group_by_n(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


def p(
    project_name,
    checkpoint,
    loras,
    motion_loras,
    motion_module,
    head_prompt,
    tail_prompt,
    negative_prompt,
    *image_prompts,
):
    project_dir = path_mgr.projects / project_name
    project_setting.project_dir = project_dir
    os.makedirs(project_dir, exist_ok=True)
    shutil.copytree(project_setting.template_dir, project_setting.project_dir, dirs_exist_ok=True)

    prompt_tmpl = json.loads(open(project_setting.template_prompts_dir).read())
    prompt_tmpl["ip_adapter_map"]["input_image_dir"] = str(project_setting.project_dir / "00_ip_adapter")
    prompt_tmpl["controlnet_map"]["input_image_dir"] = str(project_setting.project_dir / "00_controlnet_image")
    prompt_tmpl["checkpoint"] = checkpoint
    prompt_tmpl["motion"] = motion_module
    prompt_tmpl["head_prompt"] = head_prompt
    prompt_tmpl["tail_prompt"] = tail_prompt
    prompt_tmpl["n_prompt"] = [negative_prompt]
    prompt_tmpl["lora_map"] = {f"{lora}": 0.7 for lora in loras}
    prompt_tmpl["motion_lora_map"] = {f"{lora}": 0.7 for lora in motion_loras}
    open(project_setting.project_dir / "prompts.json", "wt").write(json.dumps(prompt_tmpl, indent=2))
    # subprocess.Popen(f'start cmd /k call {project_dir}/gen_preview.bat', shell=True)


def get_models_endswith(d, endswith="safetensors"):
    return [BLANK_PLACEHOLDER] + [f for f in os.listdir(d) if f.endswith(endswith)]


def build_setup():
    with gr.Blocks() as demo:
        with gr.Row():
            input_project = gr.Textbox("demo_001", label="Project Name")
            input_load = gr.Button("Load")
            input_interval = gr.Number(
                label="Interval",
                value=15,
                maximum=64,
            )
            input_refresh = gr.Button("Refresh")  # TODO: 刷心
        gr.Markdown("## CheckPoints && LoRA")
        with gr.Row():
            with gr.Column():
                input_checkpoint = gr.Dropdown(
                    value=BLANK_PLACEHOLDER,
                    label="CheckPoints",
                    choices=get_models_endswith(
                        path_mgr.checkpoints,
                    ),
                )
                input_lora = gr.Dropdown(
                    label="LoRA",
                    choices=get_models_endswith(
                        path_mgr.loras,
                    ),
                    multiselect=True,
                )
            with gr.Column():
                input_motion = gr.Dropdown(
                    label="Motion", choices=get_models_endswith(path_mgr.motions, endswith="ckpt")
                )
                input_motion_lora = gr.Dropdown(
                    multiselect=True,
                    label="Motion LoRA",
                    choices=get_models_endswith(path_mgr.motion_loras, endswith="ckpt"),
                )

        gr.Markdown("## Controlnet && IP Adapter")
        with gr.Row():
            (
                gr.CheckboxGroup(
                    controlnets,
                    label="Controlnet",
                    info="Controlnet && IP Adapter",
                    value=[
                        "controlnet_softedge",
                    ],
                ),
            )
        gr.Markdown("## Prompt Images")
        with gr.Row():
            input_head_prompt = gr.Textbox(label="Prompt Head", value="(masterpiece, best quality), ")
            input_tail_prompt = gr.Textbox(
                label="Prompt Tail",
            )
        with gr.Row():
            input_negative_prompt = gr.Textbox(
                label="Prompt Negative",
                value="nude, nsfw, (worst quality:2), (bad quality:2), (normal quality:2), lowers, bad anatomy, bad hands, (multiple views), ng_deepnegative_v1_75t, (badhandv4:1.2), (worst quality:2), (low quality:2), lowres, bad anatomy, bad hands, ",
            )
        image_prompts = []

        (
            gr.Dataframe(
                headers=["frame", "age", "gender"],
                datatype=["str", "number", "str"],
                row_count=5,
                col_count=(3, "fixed"),
            ),
        )

        with gr.Row():
            with gr.Column():
                txt_3 = gr.Textbox(label="Result")
            with gr.Column():
                btn_submit = gr.Button(value="Submit && Preview")
                btn_submit.click(
                    p,
                    inputs=[
                        input_project,
                        input_checkpoint,
                        input_lora,
                        input_motion_lora,
                        input_motion,
                        input_head_prompt,
                        input_tail_prompt,
                        input_negative_prompt,
                        *image_prompts,
                    ],
                    outputs=[txt_3],
                )
        # with gr.Row():
        #     output_video = gr.Video(label="Preview")
        #     btn_preview = gr.Button(value="Preview")
        #     btn_preview.click(
        #         p,
        #         outputs=[output_video]
        #     )
    return demo


tab_02 = build_setup()
with gr.Blocks() as tab_03:
    gr.Markdown("# Extract Frames")
    with gr.Row():
        input_video = gr.Textbox()
        output_frame = gr.Image()

    def _extract_frames(
        movie_file_path,
        # fps, out_dir, aspect_ratio, duration, offset, size_of_short_edge=-1, low_vram_mode=False
    ):
        ...
        # extract_frames(
        #     movie_file_path, fps, out_dir, aspect_ratio, duration, offset, size_of_short_edge=-1, low_vram_mode=False
        # )

    image_button = gr.Button(
        "Generate",
    )
    image_button.click(
        _extract_frames,
        inputs=[
            input_video,
        ],
        outputs=[
            output_frame,
        ],
    )


def fn_generate_1(project, frames):
    from animatediff.cli import generate

    generate(
        config_path=path_mgr.projects / project / "prompts.json",
        # width=896,
        # height=504,
        width=504,
        height=896,
        length=frames,
        context=8,
        overlap=8 // 4,
        stride=0,
        repeats=1,
        device="cuda",
        use_xformers=False,
        force_half_vae=False,
        out_dir=path_mgr.projects / project / "draft",
        no_frames=False,
        save_merged=False,
    )


def get_projects():
    return [BLANK_PLACEHOLDER] + list(sorted([_.name for _ in path_mgr.projects.iterdir() if _.is_dir()]))


class TState(BaseModel):
    project: str = BLANK_PLACEHOLDER
    project_choices: list[str] = [BLANK_PLACEHOLDER]
    frames_dirs: list[str] = [BLANK_PLACEHOLDER]


default_sampler = "k_dpmpp_sde"
default_seed = "666"
default_step = 20
default_cfg = 7
default_head_prompt = "masterpiece, best quality"
default_n_prompt = "(worst quality, low quality:1.4),nudity,simple background,border,text, patreon,bed,bedroom,white background,((monochrome)),sketch,(pink body:1.4),7 arms,8 arms,4 arms"
default_checkpoint = BLANK_PLACEHOLDER
checkpoint_list = get_models_endswith(path_mgr.checkpoints)
if checkpoint_list:
    default_checkpoint = checkpoint_list[0]

default_motion = BLANK_PLACEHOLDER
motion_list = get_models_endswith(path_mgr.motions)
if motion_list:
    default_motion = motion_list[0]

global_config = ModelConfig(**read_json(path_mgr.demo_prompt_json))

lora_arr = [[BLANK_PLACEHOLDER, 0.7] for _ in range(5)]

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

    def render_container():
        ...

    # main render
    with gr.Row():
        with gr.Column(scale=3):
            dp_project = gr.Dropdown(
                label="Project",
                choices=get_projects(),
                value=BLANK_PLACEHOLDER,
                interactive=True,
            )

            @dp_project.change(inputs=dp_project)
            def on_change(name):
                global_config.name = name

        with gr.Column(scale=1):
            btn_new_project = gr.Button("New", variant="secondary")
            btn_refresh_project = gr.Button("Refresh", variant="secondary")

            @btn_refresh_project.click(inputs=[dp_project], outputs=[dp_project])
            def refresh_projects(project_name):
                choices = get_projects()
                gr.update(choices=choices)
                return project_name

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
                gr.FileExplorer("projects/**/*.*")
            with gr.Group():
                tb_prompt = gr.Textbox(
                    show_label=False,
                    placeholder="Type prompt here. 1: 1girl; 2:2girl",
                    autofocus=True,
                    elem_classes="type_row",
                    lines=3,
                )

                @tb_prompt.change(inputs=tb_prompt)
                def change(value):
                    global_config.tail_prompt = value

                negative_prompt = gr.Textbox(label="Negative Prompt", lines=2, value=default_n_prompt, interactive=True)

                @negative_prompt.change(inputs=negative_prompt)
                def change(value):
                    global_config.n_prompt = [value]

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
                        dp_upscale = gr.Dropdown(
                            label="draft", choices=[BLANK_PLACEHOLDER], value=BLANK_PLACEHOLDER, interactive=True
                        )
                    with gr.Column(scale=1):
                        btn_refresh = gr.Button("🔁")
                        btn_upscale = gr.Button("Upscale")

                @btn_refresh.click(inputs=dp_project, outputs=dp_upscale)
                def fn_refresh_project_draft(project_name):
                    state.frames_dirs = frames_dirs = list(
                        sorted([_.name for _ in (path_mgr.projects / project_name / "draft").iterdir() if _.is_dir()])
                    )
                    return gr.update(
                        choices=[BLANK_PLACEHOLDER] + frames_dirs,
                        value=frames_dirs[-1] if frames_dirs else BLANK_PLACEHOLDER,
                        interactive=True,
                    )

                @btn_upscale.click(
                    inputs=[
                        dp_project,
                        dp_upscale,
                    ],
                    outputs=dp_upscale,
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
                    cbg_performance = gr.Radio(
                        [
                            "Speed",
                            "Quality",
                            "Extreme Speed",
                        ],
                        label="Performance",
                        value="Speed",
                        interactive=True,
                    )

                    @cbg_performance.change(inputs=cbg_performance)
                    def change(value):
                        if value == "Extreme Speed":
                            global_config.lcm_lora_scale = 1
                            global_config.apply_lcm_lora = True
                        else:
                            global_config.lcm_lora_scale = 1
                            global_config.apply_lcm_lora = False

                with gr.Row():
                    cbg_ar = (
                        gr.Radio(
                            [
                                "768x432 | 16:9",
                                "768x576 | 4:3",
                                "600x600 | 1:1",
                                "432x768 | 9:16",
                                "576x768 | 3:4",
                            ],
                            label="Aspect Ratios",
                            value="768x432 | 16:9",
                            interactive=True,
                        ),
                    )
                with gr.Row():
                    with gr.Group():
                        cb_random_seed = gr.Checkbox(label="random", interactive=True, value=True)
                        num_seed = gr.Number(label="Seed", value=-1, precision=0)

                        @num_seed.change(inputs=num_seed)
                        def change(value):
                            global_config.seed = [value]

            with gr.Tab(label="Model"):
                with gr.Row():
                    dp_checkpoint = gr.Dropdown(
                        value=default_checkpoint,
                        label="CheckPoint",
                        choices=checkpoint_list,
                        interactive=True,
                    )

                    @dp_checkpoint.change(inputs=dp_checkpoint)
                    def change(value):
                        global_config.checkpoint = value

                with gr.Row():
                    dp_motion = gr.Dropdown(
                        label="Motion",
                        choices=get_models_endswith(
                            path_mgr.motions,
                            endswith="ckpt",
                        ),
                        value="mm_sd_v15_v2.ckpt",
                        interactive=True,
                    )

                    @dp_motion.change(inputs=dp_motion)
                    def change(value):
                        global_config.motion = value

                    input_motion_lora = gr.Dropdown(
                        multiselect=True,
                        label="Motion LoRA",
                        choices=get_models_endswith(path_mgr.motion_loras, endswith="ckpt"),
                        value=[BLANK_PLACEHOLDER],
                        interactive=True,
                    )
                with gr.Row():
                    with gr.Group():
                        lora_ctrls = []
                        # TODO: refresh state
                        for i in range(5):
                            with gr.Row():
                                lora_model = gr.Dropdown(
                                    label=f"LoRA {i + 1}",
                                    choices=get_models_endswith(
                                        path_mgr.loras,
                                    ),
                                    value=BLANK_PLACEHOLDER,
                                )
                                lora_weight = gr.Slider(
                                    label="Weight",
                                    minimum=-2,
                                    maximum=2,
                                    step=0.01,
                                    value=0.7,
                                )

                                @lora_model.change(inputs=[lora_model])
                                def change(v, idx=i):
                                    global_config.lora_map = {
                                        lora[0]: lora[1] for lora in lora_arr if lora[0] != BLANK_PLACEHOLDER
                                    }

                                lora_ctrls += [lora_model, lora_weight]

                with gr.Row():
                    model_refresh = gr.Button(
                        value="\U0001f504 Refresh All Files",
                        variant="secondary",
                    )

            with gr.Tab(label="Setting"):
                gr.Slider(minimum=1, maximum=100, value=50, label="CFG")

    def track_tqdm(project, data, progress=gr.Progress(track_tqdm=True)):
        for i in tqdm.tqdm(range(2), desc="outer"):
            for j in tqdm.tqdm(range(2), desc="inner"):
                time.sleep(1)

        from animatediff.cli import generate

        save_dir = generate(
            config_path=path_mgr.projects / project / "prompts.json",
            width=432,
            height=768,
            # height=504,
            # width=896,
            # length=frames,
            length=64,
            context=16,
            overlap=16 // 4,
            stride=0,
            repeats=1,
            device="cuda",
            use_xformers=False,
            force_half_vae=False,
            out_dir=path_mgr.projects / project / "draft",
            no_frames=False,
            save_merged=False,
        )
        # TODO: 缩减 name
        # TODO: 如果搞定,则选中 video 最新的 video

        return save_dir / "video.mp4"

    generate_button.click(
        lambda: (gr.update(visible=True, interactive=True), gr.update(visible=False)),
        inputs=[],
        outputs=[
            stop_button,
            generate_button,
        ],
    ).then(
        track_tqdm,
        inputs=[
            dp_project,
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

demo.launch(server_name="0.0.0.0")
