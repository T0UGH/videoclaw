from pathlib import Path

from videoclaw.config.loader import Config
from videoclaw.models.factory import normalize_image_backend, get_image_backend


def test_image_backend_config_prefers_backend_key(tmp_path):
    project = tmp_path / "proj"
    config_dir = project / ".videoclaw"
    config_dir.mkdir(parents=True)
    (config_dir / "config.yaml").write_text(
        """
models:
  image:
    backend: codex-host-image
    provider: gemini
    auth: chatgpt_login
    codex_mode: exec
""",
        encoding="utf-8",
    )

    cfg = Config(project)
    image_cfg = cfg.get_image_backend_config()

    assert image_cfg["backend"] == "codex-host-image"
    assert image_cfg["auth"] == "chatgpt_login"
    assert image_cfg["codex_mode"] == "exec"


def test_normalize_image_backend_aliases():
    assert normalize_image_backend("openai-image") == "gemini"
    assert normalize_image_backend("codex-host-image") == "codex-host-image"


def test_mock_backend_smoke_path(tmp_path):
    backend = get_image_backend("mock", "smoke", {})
    result = backend.text_to_image("smoke")
    assert Path(result.local_path).exists()
    assert result.local_path.suffix == ".png"
