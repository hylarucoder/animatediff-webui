import os

from animatediff.adw.schema import TStatusEnum
from animatediff.adw.service import TParamsRenderVideo, do_render_video
from animatediff.consts import path_mgr
from animatediff.globals import pbar, set_global_pipeline, get_pipeline_by_id

os.chdir(path_mgr.repo)


def clean_draft_cache(project):
    p = path_mgr.projects / project / "draft"
    import shutil

    shutil.rmtree(p, ignore_errors=True)
    p.mkdir(exist_ok=True, parents=True)


def test_video_prompt():
    project = "999-test-prompt"
    params = TParamsRenderVideo(
        project=project,
        duration=1,
        aspect_radio="9:16",
        prompt="masterpiece, best quality, 1girl, walk,",
    )
    task_id = 1
    set_global_pipeline(task_id)
    bg_task = get_pipeline_by_id(task_id)
    clean_draft_cache(project)

    def on_config_start():
        ...

    def on_config_end():
        pbar.pbar_config.update(100)

    def on_render_start():
        pbar.update(10)
        ...

    def on_render_success(path):
        bg_task.video_path = path
        bg_task.status = TStatusEnum.SUCCESS
        ...

    def on_render_failed():
        bg_task.status = TStatusEnum.ERROR

    def on_render_end():
        ...

    do_render_video(
        data=params,
        on_config_start=on_config_start,
        on_config_end=on_config_end,
        on_render_start=on_render_start,
        on_render_success=on_render_success,
        on_render_failed=on_render_failed,
        on_render_end=on_render_end(),
    )

    assert bg_task.status == TStatusEnum.SUCCESS
    print(bg_task.video_path)


def test_video_test_cn_ipadapter():
    project = "999-test-cn-ipadapter"
    params = TParamsRenderVideo(
        project=project,
        duration=1,
        aspect_radio="9:16",
        prompt="masterpiece, best quality, 1girl, walk,",
    )
    task_id = 1
    set_global_pipeline(task_id)
    bg_task = get_pipeline_by_id(task_id)

    clean_draft_cache(project)

    def on_config_start():
        ...

    def on_config_end():
        pbar.pbar_config.update(100)

    def on_render_start():
        pbar.pbar.update(10)
        ...

    def on_render_success(path):
        bg_task.video_path = path
        bg_task.status = TStatusEnum.SUCCESS
        ...

    def on_render_failed():
        bg_task.status = TStatusEnum.ERROR

    def on_render_end():
        ...

    do_render_video(
        data=params,
        on_config_start=on_config_start,
        on_config_end=on_config_end,
        on_render_start=on_render_start,
        on_render_success=on_render_success,
        on_render_failed=on_render_failed,
        on_render_end=on_render_end(),
    )

    assert bg_task.status == TStatusEnum.SUCCESS
    print(bg_task.video_path)
