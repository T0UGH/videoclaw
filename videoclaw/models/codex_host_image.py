"""Codex host image backend."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict

from videoclaw.models.base import GenerationResult, ImageBackend


class CodexHostImageBackend(ImageBackend):
    """通过本机 Codex host capability 生成图片。"""

    backend_name = "codex-host-image"
    auth_source = "chatgpt_login"
    execution_surface = "codex_host"
    billing_expectation = "subscription_limited"

    def __init__(self, model: str, config: Dict[str, Any]):
        self.model = model or "codex-host-image"
        self.config = config
        self.codex_binary = config.get("codex_binary", "codex")
        self.codex_mode = config.get("codex_mode", "exec")

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        return self._generate(prompt, [])

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        source_path = self._write_temp_image(image)
        try:
            return self._generate(prompt, [source_path])
        finally:
            source_path.unlink(missing_ok=True)

    def _generate(self, prompt: str, images: list[Path]) -> GenerationResult:
        codex_path = shutil.which(self.codex_binary)
        if not codex_path:
            raise RuntimeError(f"codex binary not found: {self.codex_binary}")

        output_dir = Path.home() / "videoclaw-projects" / "temp"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"codex_{abs(hash(prompt))}.png"

        schema = {
            "type": "object",
            "properties": {
                "image_path": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["image_path", "notes"],
            "additionalProperties": False,
        }

        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as result_file:
            result_path = Path(result_file.name)
        with tempfile.NamedTemporaryFile("w+", suffix=".schema.json", delete=False) as schema_file:
            schema_path = Path(schema_file.name)
            json.dump(schema, schema_file)
            schema_file.flush()

        try:
            args = [
                codex_path,
                "exec",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--enable",
                "image_generation",
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(result_path),
            ]
            for image in images:
                args.extend(["--image", str(image)])
            args.append("-")

            completed = subprocess.run(
                args,
                input=self._build_prompt(prompt, images),
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    "codex image generation failed "
                    f"with exit code {completed.returncode}: {completed.stderr.strip() or completed.stdout.strip()}"
                )

            payload = self._load_result(result_path, completed.stdout)
            source = self._source_image(payload) or self._newest_generated_image()
            if source is None:
                raise RuntimeError("codex image generation did not return an image path")
            shutil.copy2(source, output_path)

            return GenerationResult(
                local_path=output_path,
                cloud_url=output_path.resolve().as_uri(),
                metadata={
                    "backend": self.backend_name,
                    "notes": str(payload.get("notes", "")),
                    "source_image_path": str(source),
                    "codex_mode": self.codex_mode,
                },
            )
        finally:
            result_path.unlink(missing_ok=True)
            schema_path.unlink(missing_ok=True)

    def _write_temp_image(self, image: bytes) -> Path:
        path = Path(tempfile.mkstemp(suffix=".png")[1])
        path.write_bytes(image)
        return path

    def _build_prompt(self, prompt: str, images: list[Path]) -> str:
        if not images:
            return prompt
        image_lines = "\n".join(f"- {path}" for path in images)
        return f"{prompt}\n\nInput images:\n{image_lines}"

    def _load_result(self, path: Path, stdout: str) -> dict[str, Any]:
        text = path.read_text(encoding="utf-8").strip() if path.exists() else ""
        if not text and stdout.strip():
            text = stdout.strip()
        if not text:
            return {}
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            data = json.loads(text[start : end + 1]) if start >= 0 and end > start else {}
        return data if isinstance(data, dict) else {}

    def _source_image(self, payload: dict[str, Any]) -> Path | None:
        value = payload.get("image_path")
        if not value:
            return None
        path = Path(str(value).removeprefix("file://")).expanduser()
        return path if path.exists() else None

    def _newest_generated_image(self) -> Path | None:
        generated = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser() / "generated_images"
        if not generated.exists():
            return None
        image_exts = {".png", ".jpg", ".jpeg", ".webp"}
        candidates = [
            path
            for path in generated.rglob("*")
            if path.is_file() and path.suffix.lower() in image_exts and not path.name.startswith(".")
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda path: path.stat().st_mtime)
