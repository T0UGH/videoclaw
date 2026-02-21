# 问题列表

---

## ✅ 已处理

### 1. 生成asset和storyboard时多选一
- **状态**: 已处理
- **说明**: 已在 video-standard-create 和 video-quick-create skill 中实现多张候选让用户选择
- **相关文件**:
  - skills/video-standard-create/SKILL.md (行 80-93)
  - skills/video-quick-create/SKILL.md

### 2. 后面流程使用CLI工具
- **状态**: 已处理
- **说明**: 所有流程已改用 CLI 命令 (videoclaw i2v, videoclaw audio, videoclaw merge)
- **相关文件**:
  - skills/video-i2v/SKILL.md
  - skills/video-audio/SKILL.md
  - skills/video-merge/SKILL.md
  - skills/video-standard-create/SKILL.md

### 3. CLI工具提供i2i和t2i命令
- **状态**: 已处理
- **说明**: 已实现 t2i.py 和 i2i.py 命令
- **相关文件**:
  - videoclaw/cli/commands/t2i.py
  - videoclaw/cli/commands/i2i.py

### 10 提供了t2i和i2i的命令但是没有提供对应的skill
- **状态**: 已处理
- **说明**: 已创建 video-t2i 和 video-i2i skill
- **相关文件**:
  - skills/video-t2i/SKILL.md
  - skills/video-i2i/SKILL.md

### 11 i2v只支持standard模式，不支持quick模式
- **状态**: 已处理
- **说明**: i2v 命令已重构为通用模式，支持传入图片和 prompt，quick-create 可直接使用
- **相关文件**:
  - videoclaw/cli/commands/i2v.py
  - skills/video-i2v/SKILL.md

### 9. 待测试Google Drive
- **状态**: 已处理
- **说明**: 已测试上传功能，OAuth 认证后成功上传到 Google Drive
- **相关文件**:
  - videoclaw/storage/google_drive.py

### 5. 上传包到PyPI
- **状态**: 已处理
- **说明**: 已发布到 PyPI，可以使用 `uvx videoclaw` 运行

### 4. 测试方法应该先安装这个marketplace
- **状态**: 未处理
- **说明**: 需要在测试文档中说明如何先安装 marketplace 再测试

## 未处理  

### videoclaw init 默认应该是非交互式的, 交互应该放在video-init这个skills中

Usage: videoclaw init [OPTIONS] PROJECT_NAME

  初始化新的视频项目

Options:
  --dir TEXT                      项目目录路径
  --interactive / --no-interactive
                                  交互式配置
  --help                          Show this message and exit.


total 0
drwxr-xr-x@ 7 wangguiping  staff  224 Feb 21 22:17 .
drwxr-xr-x@ 5 wangguiping  staff  160 Feb 21 22:17 ..
drwxr-xr-x@ 2 wangguiping  staff   64 Feb 21 22:17 .videoclaw
drwxr-xr-x@ 2 wangguiping  staff   64 Feb 21 22:17 assets
drwxr-xr-x@ 2 wangguiping  staff   64 Feb 21 22:17 audio
drwxr-xr-x@ 2 wangguiping  staff   64 Feb 21 22:17 storyboard
drwxr-xr-x@ 2 wangguiping  staff   64 Feb 21 22:17 videos


最开始初始化的项目中没有配置文件, 主要是因为skill写的不好导致的没有配置文件,以及需要一个全局的配置文件, 没有找到在哪

找到原因了。看 main.py:57-59：


if project_path.exists():
    click.echo(f"错误: 项目 {project_name} 已存在", err=True)
    return
问题在于：当项目目录已存在时，代码直接 return，跳过了后面创建配置文件的逻辑（第 120-124 行）。

具体情况：

第一次运行 uvx videoclaw init lulu-test（无 --no-interactive）进入了交互模式
交互式选择时可能部分创建了目录结构（或者之前某次运行已创建）
第二次运行 uvx videoclaw init lulu-test --no-interactive 时检测到目录已存在
立即返回，没有创建 config.yaml
这是一个 bug：当使用 --no-interactive 时，即使项目目录已存在，也应该尝试创建配置文件，或者至少应该给出更明确的提示。


## 暂不处理

### 6. 给用户选用asset/frame作为参考的机会
- **状态**: 部分处理
- **说明**: video-quick-create 已支持 I2I 模式（人物参考图），但 storyboard 阶段选择参考帧的功能需要进一步确认

### 8. 火山音频模型接入
- **状态**: 未处理
- **说明**: VolcEngineTTS 类已创建，但实际调用的是 mock 数据（第35-36行 TODO），需要接入真实的火山引擎 TTS API
- **相关文件**:
  - videoclaw/models/volcengine/tts.py (行 35-36)


