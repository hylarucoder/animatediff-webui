import os

from animatediff.adw.schema import TStatusEnum
from animatediff.adw.service import TParamsRenderVideo, do_render_video
from animatediff.consts import path_mgr
from animatediff.globals import get_global_pipeline, set_global_pipeline, get_pipeline_by_id, ProgressBar, g

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
        aspect_ratio="9:16",
        prompt="masterpiece, best quality, 1girl, walk,",
    )
    task_id = 1
    set_global_pipeline(task_id)
    g_pipeline = get_pipeline_by_id(task_id)
    g.pipeline = g_pipeline
    pbar = ProgressBar()
    g.pipeline.progress_bar = pbar
    clean_draft_cache(project)

    def on_config_start():
        ...

    def on_config_end():
        g_pipeline.progress_bar.pbar_config.update(100)

    def on_render_start():
        g_pipeline.progress_bar.update(10)
        ...

    def on_render_success(path):
        g_pipeline.video_path = path
        g_pipeline.status = TStatusEnum.SUCCESS
        ...

    def on_render_failed():
        g_pipeline.status = TStatusEnum.ERROR

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

    assert g_pipeline.status == TStatusEnum.SUCCESS
    print(g_pipeline.video_path)


def test_video_test_cn_ipadapter():
    project = "999-test-cn-ipadapter"
    params = TParamsRenderVideo(
        project=project,
        duration=1,
        aspect_ratio="9:16",
        prompt="masterpiece, best quality, 1girl, walk,",
    )
    task_id = 1
    set_global_pipeline(task_id)
    g_pipeline = get_pipeline_by_id(task_id)
    g.pipeline = g_pipeline
    pbar = ProgressBar()
    g.pipeline.progress_bar = pbar

    clean_draft_cache(project)

    def on_config_start():
        ...

    def on_config_end():
        g_pipeline.progress_bar.pbar_config.update(100)

    def on_render_start():
        g_pipeline.progress_bar.update(10)
        ...

    def on_render_success(path):
        g_pipeline.video_path = path
        g_pipeline.status = TStatusEnum.SUCCESS
        ...

    def on_render_failed():
        g_pipeline.status = TStatusEnum.ERROR

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

    assert g_pipeline.status == TStatusEnum.SUCCESS
    print(g_pipeline.video_path)
