# 设计方案：全面拥抱 Seedance 2.0，清理标准流程

## 背景

项目当前存在两套视频创建流程：
1. **标准流程** (`video-standard-create`)：init → assets → storyboard → i2v → audio → merge，使用状态管理 (state.json)
2. **快速流程** (`video-quick-create`)：故事大纲 → 素材准备 → 文本分镜 → i2v，不使用状态管理

为了全面拥抱 Seedance 2.0，需要清理标准流程相关代码。

## 目标

1. 删除标准流程相关的 skills
2. 删除标准流程相关的 CLI 命令代码
3. 修改 merge 命令，移除状态管理依赖
4. 保留快速流程和原子操作

## 详细设计

### 1. Skills 清理

| 操作 | Skill | 说明 |
|------|-------|------|
| 删除 | `video-standard-create` | 与 quick-create 重复 |
| 删除 | `video-assets` | 依赖 state.json，quick-create 内部已整合 |
| 删除 | `video-storyboard` | 依赖 state.json，quick-create 使用文本分镜 |
| 删除 | `video-status` | quick-create 不使用状态管理 |
| 保留 | `video-quick-create` | 主流程 |
| 保留 | `video-t2i` | 文生图，原子操作 |
| 保留 | `video-i2i` | 图生图，原子操作 |
| 保留 | `video-i2v` | 图生视频，原子操作 |
| 保留 | `video-audio` | 音频生成 |
| 保留 | `video-merge` | 视频合并，需修改 |
| 保留 | `video-text-storyboard` | 文本分镜 |
| 保留 | `video-init` | 项目初始化 |
| 保留 | `video-config` | 配置管理 |
| 保留 | `video-upload` | 云盘上传 |
| 保留 | `video-preview` | 预览 |
| 保留 | `video-publish-*` | 发布到社交平台 |

### 2. CLI 命令清理

| 操作 | 命令 | 文件 |
|------|------|------|
| 删除 | `videoclaw assets` | `cli/commands/assets.py` |
| 删除 | `videoclaw storyboard` | `cli/commands/storyboard.py` |
| 删除 | `videoclaw status` | `cli/commands/status.py` |
| 修改 | `videoclaw merge` | `cli/commands/merge.py` |

### 3. merge.py 改造

移除 StateManager 依赖，改为：

```python
# 改造后的 merge 命令
@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--videos", "-v", multiple=True, required=True, help="视频文件路径")
@click.option("--audio", "-a", help="背景音乐文件")
@click.option("--output", "-o", default="final.mp4", help="输出文件名")
def merge(project: str, videos: tuple, audio: str, output: str):
    """合并视频片段"""
    # 直接接收视频和音频文件路径，不再从 state.json 读取
    video_files = list(videos)
    # 使用 FFmpeg 合并
    ...
```

### 4. 主入口清理

`cli/main.py` 中移除以下命令的注册：
- assets
- storyboard
- status

### 5. 状态管理模块

`StateManager` 类保留（可能用于其他用途），但上述命令不再依赖它。

## 风险与注意事项

1. **向后兼容性**：如果用户有旧项目，可能无法通过新 CLI 管理
2. **测试覆盖**：需要确保保留的命令正常工作
3. **文档更新**：skills 文档已清理

## 验收标准

1. `videoclaw --help` 不再显示 assets/storyboard/status 命令
2. `videoclaw merge` 可以独立运行，不依赖 state.json
3. `video-quick-create` skill 正常工作
4. 保留的原子操作 skill 正常工作
