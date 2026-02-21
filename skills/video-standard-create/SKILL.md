---
name: video-standard-create
description: Use when user wants to create a complete video from a description in one step
---

# video-standard-create - 创建视频

## 概述
一句话创建完整视频，自动执行所有步骤。交互确认在 skill 层通过 AskUserQuestion 实现。

## 使用方式

用户只需要描述想要创建的视频：
> "帮我做一个关于宇航员在火星上发现外星遗迹的短视频"

## 执行流程

1. 调用 `videoclaw init <project-name>` 初始化项目
2. **交互式分析**：
   - 用户输入视频想法
   - 使用 AskUserQuestion 追问关键问题，一次只问一个
   - 追问示例：
     - "这个视频想表达什么氛围？"（紧张/有趣/史诗感）
     - "大概多长时间？"（15秒/30秒/1分钟）
     - "需要几个主要角色？"
   - 追问完后确认："我理解你要做一个30秒、有史诗感的视频..."
   - 用户确认后，生成 JSON 并写入 state
3. **资产生成 + 交互确认**：
   - 调用 `videoclaw assets --project <project-name>` 生成资产
   - 读取生成的图片路径，用 AskUserQuestion 询问用户：
     - "已生成角色图片，请确认是否满意？或者需要调整哪里？"
   - 如果用户不满意：
     - 询问具体调整方向："需要调整提示词还是重新生成？"
     - 根据用户反馈更新提示词
     - 重新调用 assets 命令（可删除旧图片后重试）
   - 确认满意后进入下一步
4. **故事板生成 + 交互确认**：
   - 调用 `videoclaw storyboard --project <project-name>` 生成故事板
   - 读取生成的图片路径，用 AskUserQuestion 询问用户
   - 如果不满意，重复上述调整流程
5. 调用 `videoclaw i2v --project <project-name>` 图生视频
6. 调用 `videoclaw audio --project <project-name>` 生成音频
7. 调用 `videoclaw merge --project <project-name>` 合并视频

## 交互确认模式

### 资产生成确认流程
```
1. 调用 CLI 生成图片
2. 读取生成的图片路径
3. 用 AskUserQuestion 询问:
   - "已生成 {角色/场景} 图片，路径: {path}"
   - "这帧可以吗？还是需要调整提示词？"
   - 选项: "满意" / "调整提示词" / "重新生成"
4. 根据用户选择:
   - 满意: 继续下一个
   - 调整提示词: 询问具体调整方向，重新生成
   - 重新生成: 不改提示词直接重试
```

### 故事板确认流程
同上，针对每一帧进行确认。

## 本地图片支持

如需使用本地图片（不使用 T2I）：
```bash
# 将图片放入 assets 目录
# 角色: assets/character_{name}.png
# 场景: assets/scene_{name}.png

# 调用时使用 --use-local
videoclaw assets --project <name> --use-local
```

## 生成规则

### 图像生成 (assets / storyboard)

**重要**: 每个 asset/storyboard 会生成多张候选（默认 4 张），让用户选择最喜欢的一张。

```bash
# 生成的候选文件
assets/character_astronaut_1.png
assets/character_astronaut_2.png
assets/character_astronaut_3.png
assets/character_astronaut_4.png
```

**选择流程**:
1. 展示所有候选图片
2. 让用户选择最喜欢的一张
3. 将选择结果记录到 state.json

**调整生成数量**:
```bash
# 默认生成 4 张
videoclaw assets --project mars-video

# 只需要 1 张
videoclaw assets --project mars-video --num-variants 1

# 生成更多
videoclaw assets --project mars-video --num-variants 6
```

### 视频生成 (i2v)

**重要**: 视频生成不生成多张候选，每次只生成 1 个（因为费用较高）。

### 独立命令

如需单独调用 T2I/I2I，可以使用独立命令:

```bash
# 文生图
videoclaw t2i --prompt "宇航员在火星上" --output astronaut.png

# 图生图
videoclaw i2i --input astronaut.png --prompt "穿红色制服" --output astronaut_red.png
```

## 状态检查

每步完成后检查 `videoclaw status --project <project-name>` 确认状态。

## 错误处理

如果某一步失败：
1. 查看日志了解错误原因
2. 尝试重新执行该步骤
3. 如需跳过，可以手动调用后续步骤
4. 失败超过 2 次后，将问题报告给用户

## 示例

```
用户: 做一个宇航员在火星的视频

Claude Code:
1. videoclaw init mars-video
2. 交互式分析:
   - AskUserQuestion: "这个视频想表达什么氛围？A 紧张 B 有趣 C 史诗感"
   - 用户选择: C 史诗感
   - AskUserQuestion: "大概多长时间？A 15秒 B 30秒 C 1分钟"
   - 用户选择: B 30秒
   - AskUserQuestion: "需要几个主要角色？"
   - 用户回答: 2个，宇航员和外星人
   - 确认理解，生成 JSON 保存
3. videoclaw assets --project mars-video
4. 读取生成的图片，用 AskUserQuestion 确认:
   - "已生成角色图片，要查看一下吗？这帧可以吗？"
   - 用户: 角色表情有点问题
   - AskUserQuestion: "需要调整哪里？A 表情 B 服装 C 动作"
   - 用户选择: A 表情
   - 更新提示词，重新生成
5. 确认满意后，videoclaw storyboard --project mars-video
6. 故事板交互确认（同上）
7. videoclaw i2v --project mars-video
8. videoclaw audio --project mars-video
9. videoclaw merge --project mars-video
```

## 配置

如需配置模型提供商：

```bash
videoclaw config --project mars-video --set models.image.provider=dashscope
videoclaw config --project mars-video --set models.video.provider=volcengine
```

### Google Gemini

如需使用 Google Gemini 图像生成:

```bash
videoclaw config --project mars-video --set models.image.provider=gemini
videoclaw config --project mars-video --set models.image.model=gemini-2.0-flash-exp-image-generation
```

需要设置环境变量:
```bash
export GOOGLE_API_KEY="your-api-key"
```

## 云盘配置

如需将生成的视频/图片上传到 Google Drive：

```bash
# 配置全局存储
videoclaw config --set storage.provider=google_drive
videoclaw config --set storage.upload_on_generate=true
```

首次使用需要 OAuth 授权，程序会提示你在浏览器中授权。

上传后，云盘链接会在每个步骤后显示，方便你在手机端查看。

如需关闭上传功能：

```bash
videoclaw config --set storage.provider=local
```

## 分析结果格式

```json
{
  "script": "原始脚本描述",
  "characters": [
    {"name": "角色名", "description": "角色描述", "appearance": "外观描述"}
  ],
  "scenes": [
    {"name": "场景名", "description": "场景描述", "time": "时间"}
  ],
  "frames": [
    {
      "id": 1,
      "scene": "场景名",
      "description": "画面描述",
      "duration": 5
    }
  ]
}
```
