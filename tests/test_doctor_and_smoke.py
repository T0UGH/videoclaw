from click.testing import CliRunner

from videoclaw.cli.main import main


def test_video_smoke_command_mock_backend():
    runner = CliRunner()
    result = runner.invoke(main, ["video-smoke", "--backend", "mock"])
    assert result.exit_code == 0
    assert "OK video smoke generated:" in result.output


def test_doctor_command_mock_video_backend():
    runner = CliRunner()
    result = runner.invoke(main, ["doctor", "--backend", "mock-video"])
    assert result.exit_code == 0
    assert "OK mock video backend available" in result.output


def test_doctor_command_codex_host_backend():
    runner = CliRunner()
    result = runner.invoke(main, ["doctor", "--backend", "codex-host-image"])
    assert result.exit_code == 0
    assert "backend: codex-host-image" in result.output
    assert "transport: codex_oauth" in result.output
