---
name: video-publish-kuaishou
description: Publish videos to Kuaishou (快手). Use when user wants to upload and publish videos to Kuaishou platform.
---

# video-publish-kuaishou

Publish videos to Kuaishou platform.

## Usage

```bash
videoclaw publish kuaishou -v <video_path> -t "<title>" --tags "<tag1,tag2>"
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
videoclaw publish kuaishou -v /path/to/video.mp4 -t "精彩视频"

# With tags
videoclaw publish kuaishou -v /path/to/video.mp4 -t "精彩视频" --tags "搞笑,日常"

# With cover
videoclaw publish kuaishou -v /path/to/video.mp4 -t "精彩视频" -c /path/to/cover.jpg
```

## Prerequisites

Login to Kuaishou account first:
```bash
videoclaw publish login kuaishou
```
