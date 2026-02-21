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

### 7. video-init支持交互式配置
- **状态**: 已处理
- **说明**: init 命令已支持交互式选择图像提供商、视频提供商、存储方式
- **相关文件**:
  - videoclaw/cli/main.py (行 47-90)

---

## ⚠️ 未处理

### 10 提供了t2i和i2i的命令但是没有提供对应的skill

### 11 i2v只支持standard模式，不支持quick模式
- **状态**: 未处理
- **说明**: 当前 i2v 命令依赖 storyboard 步骤（图片故事板），quick-create 跳过图片故事板后无法使用。需要新增一个专门给 quick 模式用的 command
- **相关文件**:
  - videoclaw/cli/commands/i2v.py

### 4. 测试方法应该先安装这个marketplace
- **状态**: 未处理
- **说明**: 需要在测试文档中说明如何先安装 marketplace 再测试

### 5. 上传包到PyPI
- **状态**: 未处理
- **说明**: 需要将包上传到 PyPI 以支持 `uvx` 使用，并在 skill 和文档中说明下载方式

### 6. 给用户选用asset/frame作为参考的机会
- **状态**: 部分处理
- **说明**: video-quick-create 已支持 I2I 模式（人物参考图），但 storyboard 阶段选择参考帧的功能需要进一步确认

### 8. 火山音频模型接入
- **状态**: 未处理
- **说明**: VolcEngineTTS 类已创建，但实际调用的是 mock 数据（第35-36行 TODO），需要接入真实的火山引擎 TTS API
- **相关文件**:
  - videoclaw/models/volcengine/tts.py (行 35-36)

### 9. 待测试Google Drive
- **状态**: 未处理
- **说明**: google_drive.py 已实现，需要实际测试上传功能
- **相关文件**:
  - videoclaw/storage/google_drive.py
