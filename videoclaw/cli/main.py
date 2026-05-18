"""CLI 主入口"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click
import yaml

from videoclaw.cli.commands.audio import audio
from videoclaw.cli.commands.config import config
from videoclaw.cli.commands.doctor import doctor
from videoclaw.cli.commands.i2i import i2i
from videoclaw.cli.commands.i2v import i2v
from videoclaw.cli.commands.image import image
from videoclaw.cli.commands.merge import merge
from videoclaw.cli.commands.preview import preview
from videoclaw.cli.commands.t2i import t2i
from videoclaw.cli.commands.upload import upload
from videoclaw.cli.commands.video_smoke import video_smoke
from videoclaw.config.loader import Config
from videoclaw.models.factory import get_video_backend

try:
    from videoclaw.cli.commands.publish import publish
except ModuleNotFoundError:
    publish = None

DEFAULT_PROJECTS_DIR = Path.home() / "videoclaw-projects"


def _resolve_project_path(project: str) -> Path:
    direct_path = Path(project).expanduser()
    if direct_path.exists():
        return direct_path
    return DEFAULT_PROJECTS_DIR / project


def _create_project_skeleton(project_path: Path) -> None:
    (project_path / ".videoclaw").mkdir(parents=True, exist_ok=True)
    (project_path / ".videoclaw" / "logs").mkdir(parents=True, exist_ok=True)
    (project_path / "assets" / "characters").mkdir(parents=True, exist_ok=True)
    (project_path / "assets" / "scenes").mkdir(parents=True, exist_ok=True)
    (project_path / "assets" / "props").mkdir(parents=True, exist_ok=True)
    (project_path / "assets" / "covers").mkdir(parents=True, exist_ok=True)
    (project_path / "videos").mkdir(parents=True, exist_ok=True)
    (project_path / "exports").mkdir(parents=True, exist_ok=True)


def _write_yaml(file_path: Path, data: dict) -> None:
    with open(file_path, "w") as f:
        yaml.dump(data, f, allow_unicode=True)


def _write_json(file_path: Path, data: dict) -> None:
    with open(file_path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_index(index_path: Path) -> dict:
    if index_path.exists():
        with open(index_path) as f:
            return json.load(f)
    return {"videos": []}


def _save_index(index_path: Path, data: dict) -> None:
    _write_json(index_path, data)


def _video_meta(slug: str) -> dict:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": slug,
        "title": slug,
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }


def _load_video_meta(meta_path: Path) -> dict:
    with open(meta_path) as f:
        return json.load(f)


def _save_video_meta(meta_path: Path, meta: dict) -> None:
    from datetime import datetime, timezone

    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    _write_json(meta_path, meta)


@click.group()
@click.version_option()
def main():
    """Videoclaw - AI 视频创作 CLI 工具"""
    pass


@click.group()
def video():
    """管理项目中的视频"""
    pass


@video.command("create")
@click.argument("project")
@click.argument("slug")
def video_create(project: str, slug: str):
    """在项目中创建一个视频单元"""
    project_path = _resolve_project_path(project)
    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    video_path = project_path / "videos" / slug
    if video_path.exists():
        click.echo(f"错误: 视频 {slug} 已存在", err=True)
        return

    (video_path / "storyboard").mkdir(parents=True)
    (video_path / "images").mkdir()
    (video_path / "clips").mkdir()
    (video_path / "audio").mkdir()

    _write_json(video_path / "meta.json", _video_meta(slug))
    (video_path / "brief.md").write_text(
        f"# {slug}\n\n## Idea\n\n## Style\n\n## Assets\n\n## Notes\n",
        encoding="utf-8",
    )

    index_path = project_path / ".videoclaw" / "index.json"
    index_data = _load_index(index_path)
    index_data.setdefault("videos", []).append(slug)
    index_data["videos"] = sorted(set(index_data["videos"]))
    _save_index(index_path, index_data)

    click.echo(f"视频 {slug} 已创建于 {video_path}")


@video.command("list")
@click.argument("project")
def video_list(project: str):
    """列出项目中的视频"""
    project_path = _resolve_project_path(project)
    if not project_path.exists():
        click.echo(f"错误: 项目 {project} 不存在", err=True)
        return

    index_path = project_path / ".videoclaw" / "index.json"
    index_data = _load_index(index_path)
    videos = index_data.get("videos", [])

    if not videos:
        click.echo("暂无视频")
        return

    for slug in videos:
        click.echo(slug)


@video.command("status")
@click.argument("project")
@click.argument("slug")
def video_status(project: str, slug: str):
    """查看视频状态"""
    project_path = _resolve_project_path(project)
    meta_path = project_path / "videos" / slug / "meta.json"

    if not meta_path.exists():
        click.echo(f"错误: 视频 {slug} 不存在", err=True)
        return

    meta = _load_video_meta(meta_path)
    click.echo(json.dumps(meta, ensure_ascii=False, indent=2))


@video.command("delete")
@click.argument("project")
@click.argument("slug")
def video_delete(project: str, slug: str):
    """删除项目中的视频"""
    import shutil

    project_path = _resolve_project_path(project)
    video_path = project_path / "videos" / slug
    if not video_path.exists():
        click.echo(f"错误: 视频 {slug} 不存在", err=True)
        return

    shutil.rmtree(video_path)

    index_path = project_path / ".videoclaw" / "index.json"
    index_data = _load_index(index_path)
    index_data["videos"] = [item for item in index_data.get("videos", []) if item != slug]
    _save_index(index_path, index_data)

    click.echo(f"视频 {slug} 已删除")


@video.command("generate")
@click.argument("project")
@click.argument("slug")
@click.option("--prompt", required=True, help="传给视频模型的 prompt")
@click.option("--image", "image_path", required=False, help="输入图片路径")
@click.option("--provider", default=None, help="视频提供商")
def video_generate(project: str, slug: str, prompt: str, image_path: str | None, provider: str | None):
    """为单段视频生成候选结果"""
    import shutil

    project_path = _resolve_project_path(project)
    video_path = project_path / "videos" / slug
    meta_path = video_path / "meta.json"
    if not meta_path.exists():
        click.echo(f"错误: 视频 {slug} 不存在", err=True)
        return

    render_input = video_path / "render" / "input"
    render_candidates = video_path / "render" / "candidates"
    render_input.mkdir(parents=True, exist_ok=True)
    render_candidates.mkdir(parents=True, exist_ok=True)

    reference_payload = {
        "first_frame": image_path,
        "references": [image_path] if image_path else [],
    }
    _write_json(render_input / "reference.json", reference_payload)
    (render_input / "prompt.md").write_text(prompt, encoding="utf-8")

    config = Config(project_path)
    backend_name = provider or config.get("models.video.provider", "mock")
    model = config.get("models.video.model", "")
    backend = get_video_backend(backend_name, model, config.get_all())

    image_bytes = Path(image_path).read_bytes() if image_path else b"placeholder-image"
    result = backend.image_to_video(image_bytes, prompt)

    existing = sorted(render_candidates.glob("v*.mp4"))
    candidate_name = f"v{len(existing) + 1:03d}.mp4"
    candidate_path = render_candidates / candidate_name
    shutil.copy(result.local_path, candidate_path)

    task_payload = {
        "provider": backend_name,
        "model": model,
        "mode": "image-to-video",
        "status": "completed",
        "prompt_file": str((render_input / "prompt.md").relative_to(video_path)),
        "references_file": str((render_input / "reference.json").relative_to(video_path)),
        "candidates": [p.name for p in sorted(render_candidates.glob("v*.mp4"))],
        "selected": None,
    }
    _write_json(video_path / "render" / "task.json", task_payload)

    meta = _load_video_meta(meta_path)
    meta["status"] = "generated"
    _save_video_meta(meta_path, meta)

    click.echo(f"已生成候选: {candidate_path}")


@video.command("select")
@click.argument("project")
@click.argument("slug")
@click.argument("candidate")
def video_select(project: str, slug: str, candidate: str):
    """为单段视频选择候选结果"""
    import shutil

    project_path = _resolve_project_path(project)
    video_path = project_path / "videos" / slug
    meta_path = video_path / "meta.json"
    candidate_path = video_path / "render" / "candidates" / candidate
    task_path = video_path / "render" / "task.json"

    if not meta_path.exists():
        click.echo(f"错误: 视频 {slug} 不存在", err=True)
        return
    if not candidate_path.exists():
        click.echo(f"错误: 候选 {candidate} 不存在", err=True)
        return

    selected_path = video_path / "render" / "selected.mp4"
    shutil.copy(candidate_path, selected_path)

    if task_path.exists():
        with open(task_path) as f:
            task = json.load(f)
        task["selected"] = "selected.mp4"
        _write_json(task_path, task)

    meta = _load_video_meta(meta_path)
    meta["status"] = "selected"
    _save_video_meta(meta_path, meta)

    click.echo(f"已选择候选: {candidate}")


@video.group("clip")
def video_clip():
    """管理多段视频 clip。"""
    pass


@video_clip.command("create")
@click.argument("project")
@click.argument("slug")
@click.argument("clip_id")
def video_clip_create(project: str, slug: str, clip_id: str):
    """为视频创建一个 clip。"""
    project_path = _resolve_project_path(project)
    video_path = project_path / "videos" / slug
    meta_path = video_path / "meta.json"
    if not meta_path.exists():
        click.echo(f"错误: 视频 {slug} 不存在", err=True)
        return

    clip_path = video_path / "clips" / clip_id
    if clip_path.exists():
        click.echo(f"错误: clip {clip_id} 已存在", err=True)
        return

    (clip_path / "input").mkdir(parents=True)
    (clip_path / "candidates").mkdir()
    click.echo(f"clip {clip_id} 已创建于 {clip_path}")


@video_clip.command("generate")
@click.argument("project")
@click.argument("slug")
@click.argument("clip_id")
@click.option("--prompt", required=True, help="传给视频模型的 prompt")
@click.option("--image", "image_path", required=False, help="输入图片路径")
@click.option("--provider", default=None, help="视频提供商")
def video_clip_generate(project: str, slug: str, clip_id: str, prompt: str, image_path: str | None, provider: str | None):
    """为 clip 生成候选结果。"""
    import shutil

    project_path = _resolve_project_path(project)
    clip_path = project_path / "videos" / slug / "clips" / clip_id
    if not clip_path.exists():
        click.echo(f"错误: clip {clip_id} 不存在", err=True)
        return

    input_dir = clip_path / "input"
    candidates_dir = clip_path / "candidates"
    input_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir.mkdir(parents=True, exist_ok=True)

    reference_payload = {
        "first_frame": image_path,
        "references": [image_path] if image_path else [],
    }
    _write_json(input_dir / "reference.json", reference_payload)
    (input_dir / "prompt.md").write_text(prompt, encoding="utf-8")

    config = Config(project_path)
    backend_name = provider or config.get("models.video.provider", "mock")
    model = config.get("models.video.model", "")
    backend = get_video_backend(backend_name, model, config.get_all())

    image_bytes = Path(image_path).read_bytes() if image_path else b"placeholder-image"
    result = backend.image_to_video(image_bytes, prompt)

    existing = sorted(candidates_dir.glob("v*.mp4"))
    candidate_name = f"v{len(existing) + 1:03d}.mp4"
    candidate_path = candidates_dir / candidate_name
    shutil.copy(result.local_path, candidate_path)

    task_payload = {
        "provider": backend_name,
        "model": model,
        "mode": "image-to-video",
        "status": "completed",
        "prompt_file": str((input_dir / "prompt.md").relative_to(clip_path)),
        "references_file": str((input_dir / "reference.json").relative_to(clip_path)),
        "candidates": [p.name for p in sorted(candidates_dir.glob("v*.mp4"))],
        "selected": None,
    }
    _write_json(clip_path / "task.json", task_payload)
    click.echo(f"已生成 clip 候选: {candidate_path}")


@video_clip.command("select")
@click.argument("project")
@click.argument("slug")
@click.argument("clip_id")
@click.argument("candidate")
def video_clip_select(project: str, slug: str, clip_id: str, candidate: str):
    """为 clip 选择候选结果。"""
    import shutil

    project_path = _resolve_project_path(project)
    clip_path = project_path / "videos" / slug / "clips" / clip_id
    candidate_path = clip_path / "candidates" / candidate
    task_path = clip_path / "task.json"

    if not clip_path.exists():
        click.echo(f"错误: clip {clip_id} 不存在", err=True)
        return
    if not candidate_path.exists():
        click.echo(f"错误: 候选 {candidate} 不存在", err=True)
        return

    selected_path = clip_path / "selected.mp4"
    shutil.copy(candidate_path, selected_path)

    if task_path.exists():
        with open(task_path) as f:
            task = json.load(f)
        task["selected"] = "selected.mp4"
        _write_json(task_path, task)

    click.echo(f"已选择 clip 候选: {candidate}")


# 注册子命令
main.add_command(i2v)
main.add_command(audio)
main.add_command(merge)
main.add_command(preview)
main.add_command(config)
main.add_command(t2i)
main.add_command(i2i)
main.add_command(image)
main.add_command(upload)
main.add_command(doctor)
main.add_command(video_smoke, name="video-smoke")
if publish is not None:
    main.add_command(publish)
main.add_command(video)


@main.command()
@click.argument("project_name")
@click.option("--dir", "project_dir", default=None, help="项目目录路径")
@click.option("--interactive/--no-interactive", default=False, help="交互式配置")
def init(project_name: str, project_dir: Optional[str], interactive: bool):
    """初始化新的视频项目"""
    projects_dir = Path(project_dir) if project_dir else DEFAULT_PROJECTS_DIR
    project_path = projects_dir / project_name

    if project_path.exists():
        config_file = project_path / ".videoclaw" / "config.yaml"
        if config_file.exists():
            click.echo(f"项目 {project_name} 已存在", err=True)
            return
    else:
        project_path.mkdir(parents=True)

    _create_project_skeleton(project_path)

    config_data = {
        "project_name": project_name,
        "version": "0.1.0",
        "models": {
            "image": {"backend": "codex-host-image", "auth": "chatgpt_login", "transport": "codex_oauth", "model": "gpt-image-2-medium"},
            "video": {"provider": "volcengine"},
        },
        "storage": {"provider": "local"},
    }
    _write_yaml(project_path / ".videoclaw" / "config.yaml", config_data)
    _write_json(project_path / ".videoclaw" / "index.json", {"videos": []})

    click.echo(f"项目 {project_name} 已创建于 {project_path}")


if __name__ == "__main__":
    main()
