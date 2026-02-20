"""Google Drive 存储后端"""
from __future__ import annotations

import os
import json
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

    def _load_json(self, path: str) -> Dict[str, Any]:
        """加载 JSON 文件"""
        with open(path, 'r') as f:
            return json.load(f)

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
                creds.refresh(None)
            else:
                # 检查 credentials 文件是否存在
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Google Drive credentials file not found: {self.credentials_path}\n"
                        "Please download OAuth credentials from Google Cloud Console:\n"
                        "1. Go to https://console.cloud.google.com/\n"
                        "2. Create a project and enable Google Drive API\n"
                        "3. Create OAuth credentials (Desktop app)\n"
                        "4. Download and save as ~/.config/videoclaw/credentials.json"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # 保存 token
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)

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
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        # 解析远程路径
        parts = remote_path.strip('/').split('/')
        if len(parts) < 2:
            raise ValueError("remote_path must be like 'folder1/folder2/file.png'")

        # 创建文件夹结构
        parent_id = None
        for part in parts[:-1]:
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
