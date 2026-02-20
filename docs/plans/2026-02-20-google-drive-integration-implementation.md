# Google Drive 集成实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现视频生成过程中自动上传到 Google Drive，用户可通过链接在手机端查看

**Architecture:** 基于现有 StorageBackend 抽象层，添加 GoogleDriveStorage 实现，使用 OAuth 2.0 认证

**Tech Stack:** Google Drive API, google-api-python-client, OAuth 2.0

---

## Task 1: 更新 StorageResult 数据类

**Files:**
- Modify: `videoclaw/storage/base.py`

**Step 1: 更新 StorageResult**

```python
@dataclass
class StorageResult:
    local_path: Path
    cloud_url: Optional[str] = None  # Google Drive webViewLink
    file_id: Optional[str] = None   # Google Drive file_id
```

**Step 2: Commit**

```bash
git add videoclaw/storage/base.py
git commit -m "feat: add file_id to StorageResult for cloud storage"
```

---

## Task 2: 创建 storage/factory.py 工厂函数

**Files:**
- Create: `videoclaw/storage/factory.py`

**Step 1: 读取现有模块结构**

```bash
head -20 videoclaw/storage/local.py
```

**Step 2: 创建 factory.py**

```python
"""存储后端工厂函数"""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any

from videoclaw.storage.base import StorageBackend
from videoclaw.storage.local import LocalStorage


def get_storage_backend(
    provider: str = "local",
    config: Optional[Dict[str, Any]] = None,
    base_dir: Optional[Path] = None
) -> StorageBackend:
    """获取存储后端实例

    Args:
        provider: 存储提供商 (local, google_drive, dropbox)
        config: 配置字典
        base_dir: 本地存储基础目录

    Returns:
        StorageBackend 实例
    """
    config = config or {}

    if provider == "local":
        base_dir = base_dir or Path.home() / "videoclaw-projects"
        return LocalStorage(base_dir)
    elif provider == "google_drive":
        from videoclaw.storage.google_drive import GoogleDriveStorage
        credentials_path = config.get("credentials_path")
        return GoogleDriveStorage(credentials_path=credentials_path)
    elif provider == "dropbox":
        # TODO: 未来实现
        raise NotImplementedError("Dropbox storage not yet implemented")
    else:
        raise ValueError(f"Unknown storage provider: {provider}")
```

**Step 3: Commit**

```bash
git add videoclaw/storage/factory.py
git commit -m "feat: add storage backend factory function"
```

---

## Task 3: 创建 GoogleDriveStorage 类

**Files:**
- Create: `videoclaw/storage/google_drive.py`

**Step 1: 安装依赖测试**

```bash
pip install google-api-python-client google-auth-oauthlib
```

**Step 2: 创建 GoogleDriveStorage**

```python
"""Google Drive 存储后端"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Dict, Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from videoclaw.storage.base import StorageBackend, StorageResult


SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveStorage(StorageBackend):
    """Google Drive 存储后端"""

    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or os.path.expanduser(
            "~/.config/videoclaw/credentials.json"
        )
        self.token_path = os.path.expanduser("~/.config/videoclaw/token.json")
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """OAuth 2.0 认证"""
        creds = None

        # 加载已有 token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_info(
                self._load_json(self.token_path), SCOPES
            )

        # 如果没有有效 credentials，需要授权
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(self._get_token_request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # 保存 token
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)

    def _load_json(self, path: str) -> Dict[str, Any]:
        """加载 JSON 文件"""
        import json
        with open(path, 'r') as f:
            return json.load(f)

    def _get_token_request(self):
        """获取 token 请求（用于刷新）"""
        from google.oauth2.credentials import Credentials
        return None  # 使用现有 refresh_token

    def _get_or_create_folder(self, name: str, parent_id: Optional[str] = None) -> str:
        """获取或创建文件夹"""
        # 先查询
        query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()

        if results.get('files'):
            return results['files'][0]['id']

        # 创建文件夹
        folder_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]

        folder = self.service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        return folder['id']

    def save(self, data: bytes, path: str) -> StorageResult:
        """保存数据到本地（可选上传 GD）"""
        from videoclaw.storage.local import LocalStorage
        local = LocalStorage()
        result = local.save(data, path)
        return result

    def upload(self, local_path: Path, remote_path: str) -> StorageResult:
        """上传文件到 Google Drive

        Args:
            local_path: 本地文件路径
            remote_path: 远程路径，如 "videoclaw/project/assets/image.png"

        Returns:
            StorageResult 包含 cloud_url 和 file_id
        """
        # 解析远程路径
        parts = remote_path.strip('/').split('/')
        if len(parts) < 2:
            raise ValueError("remote_path must be like 'folder1/folder2/file.png'")

        # 创建文件夹结构
        parent_id = None
        for i, part in enumerate(parts[:-1]):
            parent_id = self._get_or_create_folder(part, parent_id)

        # 上传文件
        file_metadata = {
            'name': parts[-1],
            'parents': [parent_id]
        }

        media = MediaFileUpload(str(local_path))
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, name'
        ).execute()

        return StorageResult(
            local_path=local_path,
            cloud_url=file.get('webViewLink'),
            file_id=file.get('id')
        )

    def load(self, path: str) -> bytes:
        """加载数据（暂不支持 GD 下载）"""
        raise NotImplementedError("Loading from Google Drive not supported")

    def delete(self, path: str) -> None:
        """删除数据"""
        # TODO: 实现删除
        pass

    def get_url(self, path: str) -> Optional[str]:
        """获取访问链接"""
        # 需要通过 file_id 查询
        return None
```

**Step 3: 测试导入**

```python
from videoclaw.storage.google_drive import GoogleDriveStorage
print("Import OK")
```

**Step 4: Commit**

```bash
git add videoclaw/storage/google_drive.py
git commit -m "feat: add Google Drive storage backend"
```

---

## Task 4: 更新 Config 支持 storage 配置

**Files:**
- Modify: `videoclaw/config/loader.py`

**Step 1: 添加 storage 相关配置读取**

在 Config 类中添加方法：

```python
def get_storage_config(self) -> Dict[str, Any]:
    """获取存储配置"""
    return {
        "provider": self.get("storage.provider", "local"),
        "upload_on_generate": self.get("storage.upload_on_generate", False),
        "credentials_path": self.get("storage.credentials_path"),
    }
```

**Step 2: Commit**

```bash
git add videoclaw/config/loader.py
git commit -m "feat: add storage config support"
```

---

## Task 5: 创建上传工具函数

**Files:**
- Create: `videoclaw/storage/uploader.py`

**Step 1: 创建上传工具**

```python
"""存储上传工具"""
from __future__ import annotations

from pathlib import Path
from typing import Optional
import shutil

from videoclaw.storage.factory import get_storage_backend
from videoclaw.config import Config


def upload_to_cloud(
    local_path: Path,
    remote_path: str,
    config: Config,
    project_name: str
) -> Optional[str]:
    """上传文件到云存储

    Args:
        local_path: 本地文件路径
        remote_path: 远程路径
        config: 配置对象
        project_name: 项目名称

    Returns:
        云盘链接，如果没有配置云存储则返回 None
    """
    storage_config = config.get_storage_config()
    provider = storage_config.get("provider", "local")

    # 如果是 local，不上传
    if provider == "local":
        return None

    # 如果不自动上传，也不上传
    if not storage_config.get("upload_on_generate", False):
        return None

    try:
        storage = get_storage_backend(provider, storage_config)

        # 上传文件
        result = storage.upload(local_path, remote_path)
        return result.cloud_url
    except Exception as e:
        # 上传失败不影响主流程
        import logging
        logging.warning(f"Upload to cloud failed: {e}")
        return None
```

**Step 2: Commit**

```bash
git add videoclaw/storage/uploader.py
git commit -m "feat: add upload utility function"
```

---

## Task 6: 修改 assets.py 集成上传

**Files:**
- Modify: `videoclaw/cli/commands/assets.py`

**Step 1: 添加上传调用**

在生成角色图片后添加：

```python
from videoclaw.storage.uploader import upload_to_cloud

# 生成角色图片后
if confirmed or not interactive:
    result["characters"][char_name] = str(dest_path)

    # 上传到云盘
    if config.get("storage.provider") != "local":
        cloud_url = upload_to_cloud(
            dest_path,
            f"videoclaw/{project}/assets/{dest_path.name}",
            config,
            project
        )
        if cloud_url:
            click.echo(f"  云盘链接: {cloud_url}")
```

**Step 2: Commit**

```bash
git add videoclaw/cli/commands/assets.py
git commit -m "feat: add cloud upload to assets command"
```

---

## Task 7: 修改 storyboard.py 集成上传

**Files:**
- Modify: `videoclaw/cli/commands/storyboard.py`

**Step 1: 类似 assets.py 添加上传逻辑**

**Step 2: Commit**

```bash
git add videoclaw/cli/commands/storyboard.py
git commit -m "feat: add cloud upload to storyboard command"
```

---

## Task 8: 修改 i2v.py 集成上传

**Files:**
- Modify: `videoclaw/cli/commands/i2v.py`

**Step 1: 添加上传调用**

**Step 2: Commit**

```bash
git add videoclaw/cli/commands/i2v.py
git commit -m "feat: add cloud upload to i2v command"
```

---

## Task 9: 修改 audio.py 集成上传

**Files:**
- Modify: `videoclaw/cli/commands/audio.py`

**Step 1: 添加上传调用**

**Step 2: Commit**

```bash
git add videoclaw/cli/commands/audio.py
git commit -m "feat: add cloud upload to audio command"
```

---

## Task 10: 修改 merge.py 集成上传

**Files:**
- Modify: `videoclaw/cli/commands/merge.py`

**Step 1: 添加上传调用**

**Step 2: Commit**

```bash
git add videoclaw/cli/commands/merge.py
git commit -m "feat: add cloud upload to merge command"
```

---

## Task 11: 更新 video-create skill 文档

**Files:**
- Modify: `skills/video-create/SKILL.md`

**Step 1: 添加云盘配置说明**

```markdown
## 云盘配置

如需将生成的视频/图片上传到 Google Drive：

```bash
# 配置全局存储
videoclaw config --set storage.provider=google_drive
videoclaw config --set storage.upload_on_generate=true
```

首次使用需要 OAuth 授权，程序会提示你在浏览器中授权。

上传后，云盘链接会在每个步骤后显示，方便你在手机端查看。
```

**Step 2: Commit**

```bash
git add skills/video-create/SKILL.md
git commit -m "docs: add cloud storage config to video-create skill"
```

---

## Task 12: 更新 CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: 添加存储配置说明**

在配置部分添加：

```markdown
### 云盘存储配置

```bash
# 配置 Google Drive 上传
videoclaw config --set storage.provider=google_drive
videoclaw config --set storage.upload_on_generate=true
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add cloud storage config to CLAUDE.md"
```

---

## 执行顺序

1. Task 1: 更新 StorageResult
2. Task 2: 创建 factory.py
3. Task 3: 创建 GoogleDriveStorage
4. Task 4: 更新 Config
5. Task 5: 创建上传工具
6. Task 6: 修改 assets.py
7. Task 7: 修改 storyboard.py
8. Task 8: 修改 i2v.py
9. Task 9: 修改 audio.py
10. Task 10: 修改 merge.py
11. Task 11: 更新 skill
12. Task 12: 更新 CLAUDE.md
