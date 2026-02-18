# video:config - 配置管理

## 概述
管理项目配置和全局配置。

## 使用方式

```bash
# 列出配置
videoclaw config --list

# 获取配置值
videoclaw config --get key

# 设置配置值
videoclaw config --set key=value

# 项目配置
videoclaw config --project my-project --list
videoclaw config --project my-project --get key
videoclaw config --project my-project --set key=value
```

## 参数

- `--project, -p`: 项目名称（可选，不指定则为全局配置）
- `--list`: 列出所有配置
- `--get`: 获取配置值
- `--set`: 设置配置值 (key=value)

## 示例

```
# 查看全局配置
Claude Code: videoclaw config --list

# 设置项目使用的模型
Claude Code: videoclaw config --project mars-video --set models.image.provider=dashscope
Claude Code: videoclaw config --project mars-video --set models.video.provider=volcengine

# 查看配置
Claude Code: videoclaw config --project mars-video --get models.image.provider
```
