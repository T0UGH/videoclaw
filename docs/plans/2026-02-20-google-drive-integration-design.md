# Google Drive 云盘集成设计

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现视频生成过程中自动上传到 Google Drive，用户可通过链接在手机端查看

**Architecture:** 基于现有 StorageBackend 抽象层，添加 GoogleDriveStorage 实现，使用 OAuth 2.0 认证

**Tech Stack:** Google Drive API, google-api-python-client, OAuth 2.0

---

## 1. 配置设计

### 1.1 配置文件

```yaml
# ~/.videoclaw/config.yaml 或项目配置
storage:
  provider: google_drive  # local | google_drive | dropbox (未来)
  upload_on_generate: true  # 是否在生成每个文件时自动上传
  credentials_path: ~/.config/videoclaw/credentials.json  # OAuth credentials 文件路径
```

### 1.2 配置优先级

1. 项目配置 `project/.videoclaw/config.yaml`
2. 全局配置 `~/.videoclaw/config.yaml`

---

## 2. 存储后端架构

### 2.1 现有结构

```
videoclaw/storage/
├── __init__.py
├── base.py          # StorageBackend 抽象类
├── local.py         # LocalStorage 实现
└── factory.py       # 工厂函数 (新建)
```

### 2.2 新增结构

```
videoclaw/storage/
├── __init__.py
├── base.py
├── local.py
├── factory.py       # get_storage_backend()
└── google_drive.py # GoogleDriveStorage 实现
```

### 2.3 StorageResult 更新

```python
@dataclass
class StorageResult:
    local_path: Path
    cloud_url: Optional[str] = None  # Google Drive webViewLink
    file_id: Optional[str] = None   # Google Drive file_id
```

---

## 3. Google Drive Storage 实现

### 3.1 核心功能

| 方法 | 职责 |
|------|------|
| `save()` | 保存到本地 + 可选上传 GD |
| `upload()` | 上传文件到 GD，返回 webViewLink |
| `get_or_create_folder()` | 创建/获取项目文件夹 |
| `get_url()` | 获取 webViewLink |

### 3.2 OAuth 2.0 认证流程

```
首次使用:
1. 检查 credentials.json 是否存在
2. 不存在 → 提示用户在浏览器授权
3. 授权后保存 token.json
4. 后续自动使用 token.json
```

### 3.3 文件上传结构

```
Google Drive 根目录/
└── videoclaw/
    └── {project-name}/
        ├── assets/
        │   ├── character_astronaut.png
        │   └── scene_mars.png
        ├── storyboard/
        │   ├── frame_001.png
        │   └── frame_002.png
        ├── videos/
        │   └── clip_001.mp4
        └── audio/
            └── background.mp3
```

---

## 4. 工作流程集成

### 4.1 生成流程

```
每个命令执行后:
1. 保存文件到本地
2. 检查配置: storage.provider == "google_drive" && storage.upload_on_generate == true
3. 如果是，上传到 Google Drive
4. 返回 StorageResult 包含 cloud_url
```

### 4.2 命令修改

所有生成命令需要修改:
- `assets.py` - 生成角色/场景图片后
- `storyboard.py` - 生成故事板帧后
- `i2v.py` - 生成视频片段后
- `audio.py` - 生成音频后
- `merge.py` - 合并最终视频后

### 4.3 Skill 集成

video-create skill 在每步生成后:
1. 获取返回的 cloud_url
2. 用 AskUserQuestion 告知用户: "已生成 XXX，云盘链接: https://drive.google.com/..."

---

## 5. 错误处理

| 场景 | 处理 |
|------|------|
| 未授权 | 提示用户执行 OAuth 授权 |
| token 过期 | 自动刷新 |
| 上传失败 | 记录日志，继续本地流程 |
| 网络错误 | 重试 3 次，失败则跳过 |

---

## 6. 未来扩展

### 6.1 Dropbox 支持

```python
# 只需新增 DropboxStorage 实现相同的接口
elif provider == "dropbox":
    return DropboxStorage(...)
```

### 6.2 模式说明

| provider | upload_on_generate | 行为 |
|----------|-------------------|------|
| local | 任意 | 只存本地，不上传 |
| google_drive | true | 每次生成都上传 |
| google_drive | false | merge 后手动上传 |
| dropbox | true/false | 同上 |

---

## 7. 依赖

```toml
google-api-python-client>=2.100.0
google-auth-oauthlib>=1.0.0
```

---

## 8. 实施步骤

1. 添加 GoogleDriveStorage 类
2. 添加 factory.py 工厂函数
3. 修改各命令集成上传逻辑
4. 添加配置加载支持
5. 更新 video-create skill
