"""Codex OAuth-native image backend."""
from __future__ import annotations

import base64
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from videoclaw.models.base import GenerationResult, ImageBackend

_CODEX_BASE_URL = "https://chatgpt.com/backend-api/codex"
_CODEX_CHAT_MODEL = "gpt-5.4"
_CODEX_INSTRUCTIONS = (
    "You are an assistant that must fulfill image generation requests by using the image_generation tool when provided."
)

_MODELS: Dict[str, Dict[str, Any]] = {
    "gpt-image-2-low": {
        "display": "GPT Image 2 (Low)",
        "speed": "~15s",
        "strengths": "Fast iteration, lowest cost",
        "quality": "low",
    },
    "gpt-image-2-medium": {
        "display": "GPT Image 2 (Medium)",
        "speed": "~40s",
        "strengths": "Balanced — default",
        "quality": "medium",
    },
    "gpt-image-2-high": {
        "display": "GPT Image 2 (High)",
        "speed": "~2min",
        "strengths": "Highest fidelity, strongest prompt adherence",
        "quality": "high",
    },
}

DEFAULT_MODEL = "gpt-image-2-medium"
_SIZES = {
    "landscape": "1536x1024",
    "square": "1024x1024",
    "portrait": "1024x1536",
}


class CodexHostImageBackend(ImageBackend):
    """通过 Codex / ChatGPT OAuth 直接调用 backend-api/codex 的图片后端。"""

    backend_name = "codex-host-image"
    auth_source = "chatgpt_login"
    execution_surface = "codex_oauth"
    billing_expectation = "subscription_limited"

    def __init__(self, model: str, config: Dict[str, Any]):
        self.config = config
        self.model = self._resolve_model(model, config)

    @staticmethod
    def available_models() -> List[str]:
        return list(_MODELS.keys())

    def text_to_image(self, prompt: str, **kwargs) -> GenerationResult:
        return self._generate(prompt=prompt, aspect_ratio=kwargs.get("aspect_ratio", "landscape"))

    def image_to_image(self, image: bytes, prompt: str, **kwargs) -> GenerationResult:
        # 先对齐 Hermes 的 text-only provider 行为，后续再扩展输入图片拼接
        return self._generate(prompt=prompt, aspect_ratio=kwargs.get("aspect_ratio", "landscape"))

    def _generate(self, *, prompt: str, aspect_ratio: str) -> GenerationResult:
        token = self._read_codex_access_token()
        if not token:
            raise RuntimeError("No Codex/ChatGPT OAuth credentials available")

        try:
            import openai
        except ImportError as exc:
            raise RuntimeError("openai Python package not installed") from exc

        client = openai.OpenAI(
            api_key=token,
            base_url=_CODEX_BASE_URL,
            default_headers=self._codex_cloudflare_headers(token),
        )

        meta = _MODELS[self.model]
        size = _SIZES.get(aspect_ratio, _SIZES["landscape"])
        image_b64 = self._collect_image_b64(client, prompt=prompt, size=size, quality=meta["quality"])
        if not image_b64:
            raise RuntimeError("Codex response contained no image_generation result")

        output_path = self._save_b64_image(image_b64, prefix=f"codex_{self.model}")
        return GenerationResult(
            local_path=output_path,
            cloud_url=output_path.resolve().as_uri(),
            metadata={
                "backend": self.backend_name,
                "auth": self.auth_source,
                "transport": self.execution_surface,
                "model": self.model,
                "size": size,
                "quality": meta["quality"],
            },
        )

    def _resolve_model(self, requested: str, config: Dict[str, Any]) -> str:
        candidate = requested or config.get("model") or DEFAULT_MODEL
        if candidate in _MODELS:
            return candidate
        return DEFAULT_MODEL

    def _read_codex_access_token(self) -> Optional[str]:
        auth_path = Path.home() / ".hermes" / "auth.json"
        if not auth_path.exists():
            return None
        try:
            data = json.loads(auth_path.read_text(encoding="utf-8"))
            provider = data.get("providers", {}).get("openai-codex", {})
            tokens = provider.get("tokens", {})
            access_token = tokens.get("access_token")
            if not isinstance(access_token, str) or not access_token.strip():
                return None
            try:
                payload = access_token.split(".")[1]
                payload += "=" * (-len(payload) % 4)
                claims = json.loads(base64.urlsafe_b64decode(payload))
                exp = claims.get("exp", 0)
                if exp and time.time() > exp:
                    return None
            except Exception:
                pass
            return access_token.strip()
        except Exception:
            return None

    def _codex_cloudflare_headers(self, access_token: str) -> Dict[str, str]:
        headers = {
            "User-Agent": "codex_cli_rs/0.0.0 (videoclaw)",
            "originator": "codex_cli_rs",
        }
        try:
            payload = access_token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            claims = json.loads(base64.urlsafe_b64decode(payload))
            acct_id = claims.get("https://api.openai.com/auth", {}).get("chatgpt_account_id")
            if isinstance(acct_id, str) and acct_id:
                headers["ChatGPT-Account-ID"] = acct_id
        except Exception:
            pass
        return headers

    def _collect_image_b64(self, client: Any, *, prompt: str, size: str, quality: str) -> Optional[str]:
        image_b64: Optional[str] = None
        with client.responses.stream(
            model=_CODEX_CHAT_MODEL,
            store=False,
            instructions=_CODEX_INSTRUCTIONS,
            input=[{
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            }],
            tools=[{
                "type": "image_generation",
                "model": "gpt-image-2",
                "size": size,
                "quality": quality,
                "output_format": "png",
                "background": "opaque",
                "partial_images": 1,
            }],
            tool_choice={
                "type": "allowed_tools",
                "mode": "required",
                "tools": [{"type": "image_generation"}],
            },
        ) as stream:
            for event in stream:
                event_type = getattr(event, "type", "")
                if event_type == "response.output_item.done":
                    item = getattr(event, "item", None)
                    if getattr(item, "type", None) == "image_generation_call":
                        result = getattr(item, "result", None)
                        if isinstance(result, str) and result:
                            image_b64 = result
                elif event_type == "response.image_generation_call.partial_image":
                    partial = getattr(event, "partial_image_b64", None)
                    if isinstance(partial, str) and partial:
                        image_b64 = partial
            final = stream.get_final_response()

        for item in getattr(final, "output", None) or []:
            if getattr(item, "type", None) == "image_generation_call":
                result = getattr(item, "result", None)
                if isinstance(result, str) and result:
                    image_b64 = result
        return image_b64

    def _save_b64_image(self, b64_data: str, *, prefix: str) -> Path:
        raw = base64.b64decode(b64_data)
        ts = time.strftime("%Y%m%d_%H%M%S")
        short = uuid.uuid4().hex[:8]
        path = Path.home() / "videoclaw-projects" / "temp" / f"{prefix}_{ts}_{short}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path
