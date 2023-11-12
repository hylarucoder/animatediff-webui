import json
import os
import shutil
from pathlib import Path

import gradio as gr
from pydantic import BaseModel

from animatediff.consts import (
    REPO_DIR,
    CHECKPOINTS_DIR,
    LORAS_DIR,
    MOTIONS_DIR,
    MOTION_LORAS_DIR,
    PROJECTS_DIR,
    TEMPLATES_DIR,
)


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

project_state = WorkflowState(
    interval=16,
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
    "ip_adapter",
]


def group_by_n(l, n):
    for i in range(0, len(l), n):
        yield l[i : i + n]


class TInput(BaseModel):
    project_name: str
    checkpoint: str
    motion_module: str
    motion_loras: str
    loras: list[str]
    head_prompt: str
    tail_prompt: str
    negative_prompt: str
    image_prompts: list


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
    project_dir = PROJECTS_DIR / project_name
    project_setting.project_dir = project_dir
    os.makedirs(PROJECTS_DIR / project_name, exist_ok=True)
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
    for i, (img, prompt) in enumerate(group_by_n(image_prompts, 2)):
        frame = i * project_state.interval
        if img:
            img.save(project_setting.project_dir / "00_ip_adapter" / f"{str(frame).zfill(4)}.png")
            img.save(
                project_setting.project_dir / "00_controlnet_image/controlnet_softedge" / f"{str(frame).zfill(8)}.png"
            )
        if prompt:
            prompt_tmpl["prompt_map"][f"{frame}"] = prompt

    open(project_setting.project_dir / "prompts.json", "wt").write(json.dumps(prompt_tmpl, indent=2))
    # subprocess.Popen(f'start cmd /k call {project_dir}/gen_preview.bat', shell=True)


def get_models_endswith(d, endswith="safetensors"):
    return [f for f in os.listdir(d) if f.endswith(endswith)]


def build_setup():
    with gr.Blocks(
        theme=gr.themes.Default(
            spacing_size="sm",
            text_size="sm",
        ),
    ) as demo:
        with gr.Row():
            input_project = gr.Textbox("demo_001", label="Project Name")
            input_load = gr.Button("Load")
            input_interval = gr.Number(label="Interval", value=15, maximum=64)
            input_refresh = gr.Button("Refresh")  # TODO: 刷心
        gr.Markdown("## CheckPoints && LoRA")
        with gr.Row():
            with gr.Column():
                input_checkpoint = gr.Dropdown(
                    value="mistoonAnime_v20.safetensors",
                    label="CheckPoints",
                    choices=get_models_endswith(
                        CHECKPOINTS_DIR,
                    ),
                )
                input_lora = gr.Dropdown(
                    label="LoRA",
                    choices=get_models_endswith(
                        LORAS_DIR,
                    ),
                    multiselect=True,
                )
            with gr.Column():
                input_motion = gr.Dropdown(label="Motion", choices=get_models_endswith(MOTIONS_DIR, endswith="ckpt"))
                input_motion_lora = gr.Dropdown(
                    multiselect=True,
                    label="Motion LoRA",
                    choices=get_models_endswith(MOTION_LORAS_DIR, endswith="ckpt"),
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
        with gr.Row():
            for i in range(project_state.max_frames // project_state.interval):
                with gr.Column(min_width=200):
                    i_01 = gr.Image(label=f"Frame {str(16 * i).zfill(4)}", type="pil")
                    p_01 = gr.Textbox(label=f"Prompt {str(16 * i).zfill(4)}")
                    image_prompts.append(i_01)
                    image_prompts.append(p_01)

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


demo = build_setup()
with gr.Blocks() as demo2:
    gr.Markdown("# AnimateDiff Cli Traveler GUI")
    with gr.Row():
        image_input = gr.Image()
        image_output = gr.Image()
    image_button = gr.Button("Generate")

with gr.Blocks() as demo3:
    gr.Markdown("# AnimateDiff Cli Traveler GUI")
    with gr.Row():
        image_input = gr.Image()
        image_output = gr.Image()
    image_button = gr.Button("Generate")

t2v_app = gr.TabbedInterface(
    [demo, demo2, demo3], tab_names=["I. Setup Basic Image And Prompts", "2. Generate Basic Videos", "3. Refine Videos"]
)
