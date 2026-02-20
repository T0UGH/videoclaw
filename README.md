# Videoclaw

AI 视频创作 CLI 工具，给 Claude Code 用。

## 安装

```bash
pip install -e .
```

## 快速开始

```bash
# 1. 初始化项目
videoclaw init my-video

# 2. 分析脚本（由 video-create skill 自动完成）
# Claude 会直接分析并保存到 state.json

# 3. 生成资产
videoclaw assets --project my-video

# 4. 生成故事板
videoclaw storyboard --project my-video

# 5. 图生视频
videoclaw i2v --project my-video

# 6. 合并视频
videoclaw merge --project my-video
```

## 配置

配置优先级（高到低）：
1. 环境变量：`ARK_API_KEY`, `DASHSCOPE_API_KEY`
2. 全局配置：`~/.videoclaw/config.yaml`
3. 项目配置：`<project>/.videoclaw/config.yaml`

推荐使用全局配置，一次设置，所有项目共用：

```bash
# 全局配置（推荐）
videoclaw config --global --set models.image.provider=volcengine
videoclaw config --global --set models.video.provider=volcengine

# 或使用环境变量
export ARK_API_KEY=your-api-key
```

## 日志

日志保存在项目目录：`<project>/.videoclaw/logs/`

可以通过配置调整日志级别：
```bash
videoclaw config --project my-video --set logging.level=DEBUG
```

## 使用

```bash
videoclaw --help
```
