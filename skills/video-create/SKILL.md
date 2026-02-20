---
name: video-create
description: Use when user wants to create a complete video from a description in one step
---

# video-create - 创建视频

## 概述
一句话创建完整视频，自动执行所有步骤。

## 使用方式

用户只需要描述想要创建的视频：
> "帮我做一个关于宇航员在火星上发现外星遗迹的短视频"

## 执行流程

1. 调用 `videoclaw init <project-name>` 初始化项目
2. **交互式分析**（替代直接生成）：
   - 用户输入视频想法（如 "帮我做个宇航员在火星发现变形金刚的视频"）
   - 使用 AskUserQuestion 追问关键问题，一次只问一个
   - 追问示例：
     - "这个视频想表达什么氛围？"（紧张/有趣/史诗感）
     - "大概多长时间？"（15秒/30秒/1分钟）
     - "需要几个主要角色？"
   - 追问完后确认："我理解你要做一个30秒、有史诗感的视频，有宇航员和变形金刚两个角色。我这样理解对吗？"
   - 用户确认后，生成 JSON 并写入 `<project>/.videoclaw/state.json` 的 `steps.analyze.output` 字段
3. 调用 `videoclaw assets --project <project-name>` 生成资产
4. 调用 `videoclaw storyboard --project <project-name>` 生成故事板
5. 调用 `videoclaw i2v --project <project-name>` 图生视频
6. 调用 `videoclaw audio --project <project-name>` 生成音频
7. 调用 `videoclaw merge --project <project-name>` 合并视频

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
2. 交互式分析：
   - "这个视频想表达什么氛围？A 紧张 B 有趣 C 史诗感"
   - 用户选择: C 史诗感
   - "大概多长时间？A 15秒 B 30秒 C 1分钟"
   - 用户选择: B 30秒
   - "需要几个主要角色？"
   - 用户回答: 2个，宇航员和外星人
   - "我理解你要做一个30秒、有史诗感的视频，有宇航员和外星人两个角色。我这样理解对吗？"
   - 用户确认: 对
   - 生成 JSON 并保存
3. videoclaw assets --project mars-video
4. videoclaw storyboard --project mars-video
5. videoclaw i2v --project mars-video
6. videoclaw audio --project mars-video
7. videoclaw merge --project mars-video
```

## 配置

如需配置模型提供商，可以在项目配置中设置：

```bash
videoclaw config --project mars-video --set models.image.provider=dashscope
videoclaw config --project mars-video --set models.video.provider=volcengine
```

## 分析结果格式

分析结果直接写入 `<project>/.videoclaw/state.json` 的 `steps.analyze.output` 字段：

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

