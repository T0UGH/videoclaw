# i2v 命令重构设计

## 背景

当前 `videoclaw i2v` 命令只支持 standard 模式（从 storyboard 读取帧图片），不支持 quick 模式（直接传入 asset 图片 + 文本分镜）。需要重构为两个独立命令。

## 设计

### 命令 1: `videoclaw i2v`（通用模式）

接收图片和文本作为参数，纯粹的图生视频工具。

```bash
videoclaw i2v -p project \
  -i assets/image1.png -t "镜头1描述" \
  -i assets/image2.png -t "镜头2描述"
```

**参数：**

| 参数 | 简写 | 必填 | 说明 |
|------|------|------|------|
| `--project` | `-p` | 是 | 项目名称 |
| `--image` | `-i` | 是 | 图片路径，可多次指定 |
| `--prompt` | `-t` | 是 | 传给视频模型的 prompt（可以是镜头描述、动作指令等） |
| `--provider` | - | 否 | 模型提供商 |
| `--resolution` | `-r` | 否 | 分辨率 |

### 命令 2: `videoclaw i2v-from-storyboard`（从 storyboard 读取）

保持原有逻辑，从 storyboard 步骤读取帧图片。

```bash
videoclaw i2v-from-storyboard -p project
```

**参数：**

| 参数 | 简写 | 必填 | 说明 |
|------|------|------|------|
| `--project` | `-p` | 是 | 项目名称 |
| `--provider` | - | 否 | 模型提供商 |
| `--resolution` | `-r` | 否 | 分辨率 |

## 实现任务

1. 重命名现有 `i2v.py` 为 `i2v_from_storyboard.py`
2. 创建新的 `i2v.py`，支持 `-i` 和 `-t` 参数
3. 在 `main.py` 中注册两个命令
4. 更新相关 skill 文档
