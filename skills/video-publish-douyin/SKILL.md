---
description: 发布视频到抖音平台
---

# video-publish-douyin

发布视频到抖音平台。

## 使用方法

```
videoclaw publish douyin -v <video_path> -t "<title>" --tags "<tag1,tag2>"
```

## 参数

- `video_path`: 视频文件路径
- `title`: 视频标题
- `tags`: 话题标签，逗号分隔（可选）
- `cover`: 封面图片路径（可选）
- `account`: 账号名称，默认 default（可选）

## 示例

发布视频:
```
videoclaw publish douyin -v /path/to/video.mp4 -t "精彩视频"
```

带话题:
```
videoclaw publish douyin -v /path/to/video.mp4 -t "精彩视频" --tags "搞笑,日常"
```

## 前提条件

需要先登录抖音账号:
```
videoclaw publish login douyin
```
