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


def test_atlas_image_backend_requires_a_key():
    import pytest

    with pytest.raises(ValueError, match="Atlas Cloud API Key is required"):
        get_image_backend("atlas", "bytedance/seedream-v4", {})


def test_atlas_image_backend_is_registered():
    backend = get_image_backend("atlas", "bytedance/seedream-v4", {"atlas": {"api_key": "test-key"}})
    assert backend.backend_name == "atlas"
    assert backend.model == "bytedance/seedream-v4"


def test_atlas_size_payload_differs_per_model_family():
    seedream = get_image_backend("atlas", "bytedance/seedream-v4", {"atlas": {"api_key": "k"}})
    # seedream 精确遵守 size，1024x1024 兼容写法转成 Atlas 的 宽*高
    assert seedream._size_payload({"size": "1024x1024"}) == {"size": "1024*1024"}

    banana = get_image_backend(
        "atlas", "google/nano-banana-pro/text-to-image", {"atlas": {"api_key": "k"}}
    )
    # nano-banana 系列实测忽略 size，只认 aspect_ratio
    assert banana._size_payload({"size": "1024x1024"}) == {"aspect_ratio": "1:1"}
    assert banana._size_payload({"aspect_ratio": "16:9"}) == {"aspect_ratio": "16:9"}
