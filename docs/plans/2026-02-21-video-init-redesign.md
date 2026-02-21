# video-init 交互重构设计方案

## 背景

问题描述：videoclaw init 默认是交互式的，但 CLI 工具不应该有交互（交互应该在 skill 层用 AskUserQuestion 实现）。

当前问题：
1. CLI init 默认 `--interactive` 为 True
2. CLI 使用 click.prompt 进行交互
3. 目录存在时直接 return，跳过了配置文件创建
4. 配置加载逻辑有问题：环境变量没有统一纳入，项目配置用 update 会整体覆盖

## 设计方案

### 1. CLI init 命令改动

- 默认改为 `--no-interactive`
- 移除所有 click.prompt 交互逻辑
- 修复 bug：目录存在时检查配置文件是否存在，不存在则创建

### 2. video-init Skill 改动

使用 AskUserQuestion 实现交互确认：
1. 询问图像生成提供商（volcengine/dashscope/gemini/mock）
2. 询问视频生成提供商（volcengine/dashscope/mock）
3. 询问存储方式（local/google_drive）

### 3. 配置加载逻辑优化

**优先级**：环境变量 > 项目配置 > 全局配置

实现：
- 加载顺序：先全局，再项目，最后环境变量覆盖
- 使用深度合并（deep merge）而非整体覆盖
- 项目配置简化：只存 project_name 和 version，其他继承全局

### 4. 全局配置管理

- 用户手动用 `videoclaw config --set` 设置全局配置
- 项目配置只记录项目特定信息

## 文件改动

| 文件 | 改动 |
|------|------|
| `videoclaw/cli/main.py` | init 命令改为 --no-interactive 默认，移除交互逻辑，修复目录存在时的 bug |
| `videoclaw/config/loader.py` | 优化配置加载逻辑，实现深度合并 |
| `skills/video-init/SKILL.md` | 添加 AskUserQuestion 交互流程 |
