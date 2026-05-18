# Hermes Adapter

videoclaw treats `skills/` as the canonical skill pack and uses Hermes as a thin host adapter.

## Install CLI

```bash
uvx videoclaw --help
# or
pip install videoclaw
```

## Install skills into Hermes

Copy or symlink the repo `skills/` entries into your Hermes profile skills directory.

Example target layout:

```text
~/.hermes/profiles/<profile>/skills/
  video-quick-create/
  video-text-storyboard/
  video-t2i/
  video-i2i/
  video-i2v/
  ...
```

## Recommended image path

If the machine already has Codex / ChatGPT OAuth available, videoclaw now recommends:

```yaml
models:
  image:
    backend: codex-host-image
    model: gpt-image-2-medium
    auth: chatgpt_login
    transport: codex_oauth
```

This path is Hermes-style in the sense that it reads a local Codex / ChatGPT OAuth token and calls the Codex backend directly, instead of requiring `OPENAI_API_KEY`.

## Adapter notes

- The CLI remains the only execution core.
- Skill content should come from the repo `skills/` directory.
- Hermes-specific wrappers should not duplicate prompts or workflow definitions.
- The Codex-native image path and the VolcEngine Ark video path can coexist under the same project config.
