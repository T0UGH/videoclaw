# video:create - 创建视频

## 概述
一句话创建完整视频，自动执行所有步骤。

## 使用方式

用户只需要描述想要创建的视频：
> "帮我做一个关于宇航员在火星上发现外星遗迹的短视频"

## 执行流程

1. 调用 `videoclaw init <project-name>` 初始化项目
2. 调用 `videoclaw analyze --script "<用户描述>" --project <project-name>` 分析脚本
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
2. videoclaw analyze --script "宇航员在火星上发现外星遗迹" --project mars-video
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
