---
name: video-publish-douyin
description: Publish videos to Douyin (抖音). Use when user wants to upload and publish videos to Douyin platform.
---

# video-publish-douyin

> **注意**：如果是首次使用，确保已安装 videoclaw：`uvx videoclaw --help`

Publish videos to Douyin platform.

## Usage

```bash
videoclaw publish upload douyin -v <video_path> -t "<title>" --tags "<tag1,tag2>"
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `-v, --video` | Video file path (required) |
| `-t, --title` | Video title (required) |
| `--tags` | Comma-separated tags (optional) |
| `-c, --cover` | Cover image path (optional) |
| `-a, --account` | Account name, default: default (optional) |

## Examples

```bash
# Basic
videoclaw publish upload douyin -v /path/to/video.mp4 -t "精彩视频"

# With tags
videoclaw publish upload douyin -v /path/to/video.mp4 -t "精彩视频" --tags "搞笑,日常"

# With cover
videoclaw publish upload douyin -v /path/to/video.mp4 -t "精彩视频" -c /path/to/cover.jpg
```

## Prerequisites

Login to Douyin account first:
```bash
videoclaw publish login douyin
```
