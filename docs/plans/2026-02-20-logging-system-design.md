# Videoclaw 日志系统设计方案

## 背景

当前项目没有日志系统，调试困难。需要在每个项目中添加可配置的日志功能。

## 需求

1. **用途**：调试问题 + 记录执行过程
2. **内容**：CLI 命令执行、模型调用、项目级追踪
3. **位置**：`<project>/.videoclaw/logs/`
4. **级别**：ERROR, WARNING, INFO, DEBUG
5. **默认**：INFO 及以上写入日志文件，支持配置

## 架构

### 目录结构

```
<project>/.videoclaw/logs/
├── 2026-02-20.log    # 按日期归档
├── 2026-02-21.log
└── ...
```

### 组件

1. **Logger 工具类** - `videoclaw/utils/logging.py`
   - 封装 Python logging
   - 双输出：控制台 + 文件
   - 可配置日志级别

2. **配置项**
   - `logging.level`: 控制台日志级别（默认 INFO）
   - `logging.file_level`: 文件日志级别（默认 INFO）

## 日志格式

```
2026-02-20 11:30:45 [INFO] videoclaw.assets: 开始生成资产，角色: ['宇航员', '变形金刚']
2026-02-20 11:30:46 [DEBUG] volcengine.seedream: API 请求: model=seedream-3, prompt=...
2026-02-20 11:30:48 [ERROR] volcengine.seedream: API 错误: 401 Unauthorized
```

## 实现计划

1. 创建 `videoclaw/utils/logging.py`
2. 修改各 CLI 命令添加日志
3. 修改模型后端添加日志
4. 支持通过 `videoclaw config` 配置日志级别

---

*创建时间：2026-02-20*
