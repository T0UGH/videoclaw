"""Atlas Cloud 后端的离线测试（不打真实网络）"""
from pathlib import Path

import pytest

from videoclaw.models.atlas.client import AtlasClient, _fix_extension
from videoclaw.models.factory import get_image_backend, get_video_backend

JPEG_MAGIC = b"\xff\xd8\xff\xe0" + b"\x00" * 8
PNG_MAGIC = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8


def test_fix_extension_renames_jpeg_written_as_png(tmp_path):
    target = _fix_extension(tmp_path / "a.png", JPEG_MAGIC)
    assert target.name == "a.jpg"


def test_fix_extension_keeps_matching_suffix(tmp_path):
    target = _fix_extension(tmp_path / "a.png", PNG_MAGIC)
    assert target.name == "a.png"


def test_video_backend_requires_a_key():
    with pytest.raises(ValueError, match="Atlas Cloud API Key is required"):
        get_video_backend("atlas", "bytedance/seedance-2.0/image-to-video", {})


def test_video_backend_rejects_refs_it_cannot_express():
    backend = get_video_backend(
        "atlas", "bytedance/seedance-2.0/image-to-video", {"atlas": {"api_key": "k"}}
    )
    with pytest.raises(ValueError, match="video references"):
        backend.image_to_video(b"", "prompt", video_refs=["clip.mp4"])
    with pytest.raises(ValueError, match="audio references"):
        backend.image_to_video(b"", "prompt", audio_refs=["voice.mp3"])


def test_video_payload_defaults_are_explicit(monkeypatch, tmp_path):
    backend = get_video_backend(
        "atlas", "bytedance/seedance-2.0/image-to-video", {"atlas": {"api_key": "k"}}
    )
    captured = {}

    def fake_run(self, endpoint, payload, local_path):
        captured["endpoint"] = endpoint
        captured["payload"] = payload
        target = tmp_path / "out.mp4"
        target.write_bytes(b"\x00")
        return target

    monkeypatch.setattr(AtlasClient, "run", fake_run)
    result = backend.image_to_video(b"frame-bytes", "camera holds", size="1280x720", duration=5)

    assert captured["endpoint"] == "generateVideo"
    payload = captured["payload"]
    # 空 shot_type 会被接口拒掉，所以必须显式给值
    assert payload["shot_type"] == "single"
    # Seedance 2.0 默认出音频，配乐撞版权校验会让整条任务 failed，所以默认关掉
    assert payload["generate_audio"] is False
    assert payload["size"] == "1280*720"
    assert payload["duration"] == 5
    assert payload["images"].startswith("data:image/png;base64,")
    assert Path(result.local_path).exists()


def test_image_to_image_switches_to_the_edit_task(monkeypatch, tmp_path):
    backend = get_image_backend(
        "atlas", "bytedance/seedream-v4/text-to-image", {"atlas": {"api_key": "k"}}
    )
    captured = {}

    def fake_run(self, endpoint, payload, local_path):
        captured["payload"] = payload
        target = tmp_path / "out.png"
        target.write_bytes(PNG_MAGIC)
        return target

    monkeypatch.setattr(AtlasClient, "run", fake_run)
    backend.image_to_image(b"src-bytes", "make it dusk")

    assert captured["payload"]["model"] == "bytedance/seedream-v4/edit"
    assert captured["payload"]["images"].startswith("data:image/png;base64,")
