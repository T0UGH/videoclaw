# Videoclaw 设计方案 - Skill 驱动架构

## 背景

初始计划是将脚本分析作为 CLI 命令实现，但经过头脑风暴，发现有更好的方案。

## 核心设计决策

### 不使用 CLI 进行脚本分析

**原方案**：创建 `videoclaw analyze` 命令，调用外部 LLM 或简单解析

**新方案**：直接在 Skill 中利用 Claude 本身的能力进行分析

**理由**：
1. 利用 Claude 本身强大的理解和推理能力
2. 不需要额外 API Key（零成本）
3. 更灵活，可以生成更丰富、创造性的描述
4. 用户体验更自然（直接对话，不需要记命令）

## 新流程设计

```
用户: "帮我做一个宇航员在火星发现变形金刚的视频"

    ↓

Claude 加载 video-create skill

    ↓
    ├─→ 分析脚本（直接用 Claude 能力）
    │   - 生成角色列表
    │   - 生成场景列表
    │   - 生成分镜脚本（frames）
    │
    ├─→ 调用 videoclaw assets 生成角色/场景图片
    │
    ├─→ 调用 videoclaw storyboard 生成故事板
    │
    ├─→ 调用 videoclaw i2v 生成视频片段
    │
    ├─→ 调用 videoclaw audio 生成语音
    │
    └─→ 调用 videoclaw merge 合并视频
```

## 架构变化

| 组件 | 变化 |
|------|------|
| analyze CLI 命令 | 移除或降级为辅助工具 |
| video-create skill | 加入脚本分析指导 |
| video-assets skill | 加入资产生成指导 |
| 其他 skills | 保持不变 |

## 问题二：分析结果保存格式

**决定**：使用现有格式 - JSON 保存在 `<project>/.videoclaw/state.json` 的 `steps.analyze.output` 字段

```json
{
  "script": "宇航员在火星发现变形金刚",
  "characters": [...],
  "scenes": [...],
  "frames": [...]
}
```

**理由**：
- 与现有 state.json 机制一致
- 便于后续 CLI 命令读取
- 后续可以扩展保存为独立的 script.json 文件（如果需要）

## 问题三：如何保存分析结果到 state.json

**决定**：直接用 Write 工具写 JSON + CLI 格式验证

**理由**：
1. 更直接，不需要绕一圈调用 CLI
2. 利用 Claude 本身的能力生成 JSON
3. 提供格式检查命令，防止 JSON 格式错误

**实现方式**：
1. Skill 指导 Claude 直接写 JSON 到 `<project>/.videoclaw/state.json`
2. 提供 `videoclaw validate` 命令检查 JSON 格式
3. 如果格式错误，提示 Claude 修正

## 问题四：模型调用方式

**决定**：保持现有设计 - 通过 CLI 调用专业模型后端

**理由**：
- assets (T2I)、i2v (图生视频)、audio (TTS) 需要专业模型
- 使用 dashscope/volcengine 等专业服务
- 与现有 models/factory.py 架构一致
- CLI 默认使用 volcengine（当 ARK_API_KEY 配置后自动生效）

## 待讨论

- [ ] 各 CLI 命令的具体实现细节

---

*创建时间：2026-02-20*
*更新时间：2026-02-20*

---

*创建时间：2026-02-20*
*更新时间：2026-02-20*
