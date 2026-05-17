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
  ...
```

## Adapter notes

- The CLI remains the only execution core.
- Skill content should come from the repo `skills/` directory.
- Hermes-specific wrappers should not duplicate prompts or workflow definitions.
