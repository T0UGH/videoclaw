# 社交媒体发布功能设计

## 1. 背景

用户需要将生成的视频一键发布到抖音、快手等社交平台，省去手动复制粘贴的繁琐操作。

## 2. 目标

- 支持视频发布到抖音、快手两个平台
- 支持多账号（预留扩展，当前单账号）
- 支持标题、话题标签、封面图
- 提供 CLI 命令和 Skill 两种调用方式

## 3. 整体架构

```
┌─────────────────────────────────────────┐
│           Skills (Agent 调用)            │
│  video-publish-douyin / video-publish-kuaishou │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│           CLI 命令层                      │
│  videoclaw publish douyin/kuaishou      │
│  videoclaw publish login douyin/kuaishou│
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│          Publisher 模块                  │
│  publisher/base.py                      │
│  publisher/douyin.py                    │
│  publisher/kuaishou.py                  │
│  publisher/cookie_manager.py            │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│        Playwright 浏览器自动化            │
└─────────────────────────────────────────┘
```

## 4. 项目结构

```
videoclaw/publisher/
├── __init__.py
├── base.py                    # Publisher 基类
├── douyin.py                  # 抖音发布器
├── kuaishou.py                # 快手发布器
├── factory.py                 # get_publisher 工厂函数
└── cookie_manager.py          # Cookie 管理

videoclaw/cli/commands/
└── publish.py                 # publish 子命令

skills/
├── video-publish-douyin/
│   └── SKILL.md
└── video-publish-kuaishou/
    └── SKILL.md
```

## 5. CLI 用法

```bash
# 登录（打开浏览器扫码）
videoclaw publish login douyin
videoclaw publish login kuaishou

# 发布视频
videoclaw publish douyin -v video.mp4 -t "标题" --tags "tag1,tag2" --cover cover.jpg
videoclaw publish kuaishou -v video.mp4 -t "标题" --tags "tag1,tag2" --cover cover.jpg

# 查看已登录账号
videoclaw publish status
```

## 6. 配置

```yaml
# ~/.videoclaw/config.yaml
publisher:
  douyin:
    cookie_dir: ~/.videoclaw/cookies/douyin
  kuaishou:
    cookie_dir: ~/.videoclaw/cookies/kuaishou
```

## 7. 依赖

```toml
# pyproject.toml
playwright>=1.40.0
```

## 8. 实现要点

### 8.1 Cookie 管理

- 使用 Playwright 的 `storage_state` 保存登录状态
- Cookie 文件存储在 `~/.videoclaw/cookies/<platform>/<account>.json`
- 登录时使用 headless=False 让用户扫码
- 发布时使用 headless=True（可配置）

### 8.2 抖音发布器

- 访问抖音创作者中心：https://creator.douyin.com/
- 上传视频、填写标题、话题、封面
- 支持检测发布结果

### 8.3 快手发布器

- 访问快手创作者平台：https://cp.kuaishou.com/
- 流程类似抖音

### 8.4 多账号支持

- 设计时预留账号参数，当前默认使用 `default` 账号
- 后续可扩展为：`videoclaw publish douyin --account my_account ...`

## 9. 参考实现

- social-auto-upload 项目：https://github.com/.../social-auto-upload/
- 使用 Playwright 浏览器自动化
- 创作者中心网页版上传

## 10. 待办

- [ ] 实现 publisher 模块
- [ ] 实现 CLI publish 命令
- [ ] 添加 playwright 依赖
- [ ] 创建 video-publish-douyin Skill
- [ ] 创建 video-publish-kuaishou Skill
