from pathlib import Path

from click.testing import CliRunner

from videoclaw.cli.main import main


def test_video_clip_workflow_smoke(tmp_path):
    runner = CliRunner()
    project_root = tmp_path / "projects"

    init_result = runner.invoke(main, ["init", "demo", "--dir", str(project_root)])
    assert init_result.exit_code == 0

    project_path = project_root / "demo"

    create_video = runner.invoke(main, ["video", "create", str(project_path), "sample-video"])
    assert create_video.exit_code == 0

    create_clip = runner.invoke(main, ["video", "clip", "create", str(project_path), "sample-video", "clip-01"])
    assert create_clip.exit_code == 0

    generate_clip = runner.invoke(
        main,
        ["video", "clip", "generate", str(project_path), "sample-video", "clip-01", "--prompt", "turn head", "--provider", "mock"],
    )
    assert generate_clip.exit_code == 0

    select_clip = runner.invoke(main, ["video", "clip", "select", str(project_path), "sample-video", "clip-01", "v001.mp4"])
    assert select_clip.exit_code == 0

    selected = project_path / "videos" / "sample-video" / "clips" / "clip-01" / "selected.mp4"
    assert selected.exists()

    merge_result = runner.invoke(main, ["merge", "--project", str(project_path), "--output", "final-test.mp4"])
    assert merge_result.exit_code == 0

    merged = project_path / "exports" / "final-test.mp4"
    assert merged.exists()
