# video:init - 初始化项目

## 概述
初始化新的视频项目，创建目录结构。

## 使用方式

```bash
videoclaw init my-project
```

## 创建的目录

- `.videoclaw/` - 配置和状态文件
- `assets/` - 角色和场景图片
- `storyboard/` - 故事板帧图片
- `videos/` - 生成的视频片段
- `audio/` - 音频文件

## 参数

- `project_name`: 项目名称（必填）
- `--dir`: 项目目录路径（可选，默认 ~/videoclaw-projects）

## 示例

```
用户: 创建一个新项目

Claude Code: videoclaw init my-video-project
```
