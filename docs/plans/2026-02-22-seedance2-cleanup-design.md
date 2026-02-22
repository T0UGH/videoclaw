# 设计方案：全面拥抱 Seedance 2.0，清理标准流程

## 背景

项目当前存在两套视频创建流程：
1. **标准流程** (`video-standard-create`)：init → assets → storyboard → i2v → audio → merge，使用状态管理 (state.json)
2. **快速流程** (`video-quick-create`)：故事大纲 → 素材准备 → 文本分镜 → i2v，不使用状态管理

为了全面拥抱 Seedance 2.0，需要清理标准流程相关代码。

## 目标

1. 删除标准流程相关的 skills
2. 删除标准流程相关的 CLI 命令代码
3. 删除状态管理模块
4. 修改 audio/merge 命令，移除状态管理依赖
5. 保留快速流程和原子操作

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

| 操作 | 命令 | 文件 | 说明 |
|------|------|------|------|
| 删除 | `videoclaw assets` | `cli/commands/assets.py` | 依赖 StateManager |
| 删除 | `videoclaw storyboard` | `cli/commands/storyboard.py` | 依赖 StateManager |
| 删除 | `videoclaw i2v-from-storyboard` | `cli/commands/i2v_from_storyboard.py` | 依赖 storyboard |
| 修改 | `videoclaw audio` | `cli/commands/audio.py` | 移除 StateManager 依赖 |
| 修改 | `videoclaw merge` | `cli/commands/merge.py` | 移除 StateManager 依赖 |
| 保留 | `videoclaw i2v` | `cli/commands/i2v.py` | 独立命令，不依赖 state |
| 保留 | `videoclaw t2i` | `cli/commands/t2i.py` | 独立命令 |
| 保留 | `videoclaw i2i` | `cli/commands/i2i.py` | 独立命令 |
| 保留 | `videoclaw config` | `cli/commands/config.py` | 配置管理 |
| 保留 | `videoclaw preview` | `cli/commands/preview.py` | 预览 |
| 保留 | `videoclaw upload` | `cli/commands/upload.py` | 上传 |
| 保留 | `videoclaw publish` | `cli/commands/publish.py` | 发布 |
| 保留 | `videoclaw validate` | `cli/commands/validate.py` | 验证 |

### 3. 状态管理模块删除

| 操作 | 文件 | 说明 |
|------|------|------|
| 删除 | `videoclaw/state/manager.py` | StateManager 类 |
| 删除 | `videoclaw/state/__init__.py` | 模块导出 |
| 删除 | `videoclaw/pipeline/orchestrator.py` | 工作流编排，使用 StateManager |

### 4. audio.py 改造

移除 StateManager 依赖，改为直接接收参数：

```python
# 改造后的 audio 命令
@click.command()
@click.option("--project", "-p", required=True, help="项目名称")
@click.option("--provider", default="volcengine", help="模型提供商")
@click.option("--text", "-t", help="TTS 文本内容")
@click.option("--duration", default=30, help="背景音乐时长")
def audio(project: str, provider: str, text: str, duration: int):
    """生成音频（TTS、音效、背景音乐）"""
    # 不再从 state.json 读取数据
    # 直接使用命令行参数
    ...
```

### 5. merge.py 改造

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
    ...
```

### 6. 主入口清理

`cli/main.py` 中：
1. 移除导入：`assets`, `storyboard`, `i2v_from_storyboard`
2. 移除命令注册：`.add_command(assets)`, `.add_command(storyboard)`, `.add_command(i2v_from_storyboard)`

### 7. 测试文件清理

删除相关测试文件：
- `tests/test_state.py`
- `tests/test_state_selections.py`
- `tests/test_storyboard_num_variants.py`
- `tests/test_assets_num_variants.py`
- `tests/test_pipeline.py`

## 风险与注意事项

1. **向后兼容性**：如果用户有旧项目，可能无法通过新 CLI 管理
2. **测试覆盖**：需要确保保留的命令正常工作
3. **audio/merge 参数变化**：命令行参数接口变化，需更新调用方

## 验收标准

1. `videoclaw --help` 不再显示 assets/storyboard/i2v-from-storyboard 命令
2. `videoclaw audio` 可以独立运行，不依赖 state.json
3. `videoclaw merge` 可以独立运行，不依赖 state.json
4. `videoclaw/state/` 目录已删除
5. `videoclaw/pipeline/orchestrator.py` 已删除
6. `video-quick-create` skill 正常工作
7. 保留的原子操作 skill 正常工作
