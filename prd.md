# videoclaw 演进 PRD（草案）

## 背景

`videoclaw` 主要开发于 2026 年 2 月，当时的设计目标是面向 Claude Code 的 AI 视频创作 CLI，通过项目目录管理一次视频创作流程。到 2026 年 5 月，对比后续开发的 `plotloom`，`videoclaw` 在生产模型、工作流抽象和宿主适配方式上已经显得偏早期。

当前需要基于 `plotloom` 的经验，对 `videoclaw` 做一轮产品和架构升级梳理，明确下一阶段的演进方向。

---

## 目标

把 `videoclaw` 从“单视频项目制的 Claude Code 专用工具”升级为：

1. 面向共享资产和多视频产出的工作空间系统；
2. 支持更现代的图片生成与视频生成能力；
3. 兼容多种 agent/runtime 宿主，而不是只围绕 Claude Code 安装与使用；
4. 尽量通过插件式安装接入，而不是把宿主绑定在某一个代码助手上。

---

## 当前识别出的核心问题

### 1. 单个视频对应一个 project，工作流过重

#### 现状

当前 `videoclaw` 的项目模型更接近“一次视频任务 = 一个 project”。初始化后会创建独立项目目录，包含配置、素材、storyboard、video、audio 等内容。

#### 问题

这种模型适合单次快速生成，但不适合持续创作。

对于真实创作场景，一个 project 往往应该承载：

- 一组共享角色资产；
- 一组共享场景资产；
- 一套长期复用的风格、设定和模板；
- 基于这些共享资产持续产出多个视频。

当前模型会导致：

- project 创建频率太高；
- 资产复用成本高；
- 跨视频保持角色/场景一致性困难；
- 管理多个视频时目录组织不自然。

#### 本轮结论

这一问题已经完成第一轮收敛，结论如下：

- 顶层对象继续叫 **project**，不改名为 workspace 或 repo；
- 一个 `project` 不再对应单条视频，而是对应一个**共享资产空间**；
- 单条产出统一放在 `videos/<slug>/` 下；
- `videos/<id>/` 使用 **slug 名**，而不是自动编号；
- 保留轻量入口，但命令模型改为显式的 `videoclaw video <subcommand>`。

也就是说，`videoclaw` 的核心抽象从：

- 旧模型：一个 `project` = 一个视频任务

升级为：

- 新模型：一个 `project` = 一个可持续产出多个视频的共享空间
- 一个 `project` 下包含多个 `videos/<slug>/`
- 每个 `video` 是独立产出单元

这不是单纯增强，而是在纠正原本“project 粒度过细”的抽象问题。

#### 目录结构（方案 A）

本轮采用轻量的 **方案 A**，优先修正 project / video 抽象，不立即引入 `plotloom` 式的重型 artifact 模型。

推荐目录如下：

```text
my-project/
├── .videoclaw/
│   ├── config.yaml
│   ├── index.json
│   └── logs/
├── assets/
│   ├── characters/
│   ├── scenes/
│   ├── props/
│   └── covers/
├── videos/
│   ├── summer-launch/
│   │   ├── meta.json
│   │   ├── brief.md
│   │   ├── storyboard/
│   │   ├── images/
│   │   ├── clips/
│   │   ├── audio/
│   │   └── final.mp4
│   └── brand-story/
└── exports/
```

#### 各目录职责

- `.videoclaw/`
  - 放项目级系统信息，不放业务素材；
  - `config.yaml` 保存项目配置；
  - `index.json` 作为轻量索引，方便 `video list` / `video status`；
  - `logs/` 保存项目级日志。

- `assets/`
  - 放跨视频复用的长期资产；
  - 第一阶段只保留最简单的 `characters/`、`scenes/`、`props/`、`covers/` 四类；
  - 暂不引入复杂 manifest 或引用图谱。

- `videos/`
  - 每个子目录是一条视频；
  - 每条视频拥有自己的 brief、storyboard、images、clips、audio 和 final 产物；
  - 单视频目录是主要生产单元。

- `exports/`
  - 放最终面向外部交付的产物，如压缩版、带字幕版、发布封面、发布包等；
  - 与 `videos/<slug>/final.mp4` 区分开，前者偏交付，后者偏生产结果。

#### `meta.json` 与 `index.json`

推荐保留两个轻量元数据文件：

1. `videos/<slug>/meta.json`
   - 作为单视频的元信息文件；
   - 建议至少包含：`id`、`title`、`status`、`created_at`、`updated_at`；
   - 可后续扩展 tags、source assets 等字段。

2. `.videoclaw/index.json`
   - 作为项目级索引/缓存；
   - 用于快速列出 videos、记录创建时间、支持未来 `video list --json`；
   - 不是唯一真相，真实状态仍以 `videos/<slug>/meta.json` 和文件系统为准。

#### 资产与视频的关系

第一阶段采用**弱关联**：

- 允许 `video` 直接引用 `assets/` 下的文件路径；
- 可在 `brief.md` 或 `meta.json` 中记录用到了哪些共享资产；
- 暂不强制引入 `reference-map` 一类更重的引用模型。

原因是当前阶段的目标是先修正抽象，不把 `videoclaw` 立即推向 `plotloom` 那样的重工作流。

#### CLI 方向

本轮不采用“给旧命令补 `--video` 参数”的兼容路线，而是直接引入新的 `video` 命令组。

第一阶段推荐命令面：

```bash
videoclaw init my-project
videoclaw status
videoclaw config

videoclaw video create summer-launch
videoclaw video list
videoclaw video status summer-launch
videoclaw video delete summer-launch
```

后续现有能力逐步收敛到 `video` 子命令组下，例如：

```bash
videoclaw video t2i summer-launch ...
videoclaw video i2i summer-launch ...
videoclaw video i2v summer-launch ...
videoclaw video audio summer-launch ...
videoclaw video merge summer-launch ...
```

这样可以从交互层明确表达：`video` 是 `project` 下的一级对象，而不是隐含在目录结构中的概念。

#### `video create` 默认生成内容

推荐 `videoclaw video create <slug>` 默认创建：

```text
videos/<slug>/
├── meta.json
├── brief.md
├── storyboard/
├── images/
├── clips/
└── audio/
```

其中：

- `meta.json` 用于记录视频元信息和状态；
- `brief.md` 生成一个最小模板，作为进入创作的起点；
- 其余目录作为图片、分镜、视频片段、音频的天然落点。

#### 兼容迁移策略

旧项目可视为一个只包含默认视频的新项目：

- 老项目自动映射为 `videos/default/`；
- 原 `storyboard/` → `videos/default/storyboard/`；
- 原顶层 `videos/`（旧片段）→ `videos/default/clips/`；
- 原顶层 `audio/` → `videos/default/audio/`。

这样可以兼容既有目录，避免历史项目失效。

#### 本阶段明确不解决的内容

方案 A 当前**不解决**以下问题：

- candidate / selected / review 闭环；
- receipt / task artifact；
- prompt 编译与审计；
- 复杂 continuity 管理；
- `plotloom` 式的重型视频生产闭环。

这些内容属于后续“视频模型像 `plotloom` 一样真正调通并产品化”的下一阶段议题。

---

### 2. 图片模型需要支持 OpenAI 图片生成，并尽量复用用户已有 Codex 订阅

#### 现状

当前 `videoclaw` 的图片模型主要围绕 Gemini、DashScope、VolcEngine 等 provider 设计。对于 OpenAI 图片能力，现阶段既没有正式的独立 provider，也没有像 `plotloom` 那样的 Codex 宿主适配路径。

#### 问题

当前图片能力与 2026 年的新使用习惯不完全匹配。用户希望：

- 支持更现代的 OpenAI 图片生成能力；
- 最好用户已有 Codex / ChatGPT 登录环境时，就能低门槛直接在这套系统里使用图片生成；
- 避免要求用户单独配置新的平台和复杂计费链路；
- 同时不要把 `videoclaw` 的架构绑死在单一宿主上。

#### 调研结论

本轮调研后，有几个判断已经可以明确：

1. **`plotloom` 的图片链路是可复用的技术样本，但不是最终架构答案**
   - `plotloom` 当前图片生成本质上是复用本机 Codex host capability，再把结果归档到 repo；
   - 它证明了“Codex 宿主能力接入可行”；
   - 但它更像宿主适配器，不是成熟的宿主无关图片 provider。

2. **本地 CLI + ChatGPT / Codex 登录是成立的产品路径**
   - Codex 支持本地 CLI 使用和 ChatGPT 登录；
   - 因此“本机 Codex 登录后复用图片能力”在产品方向上是可行的。

3. **但不能承诺“有 Codex 订阅就一定等于本地图片生成完全可用且无额外限制”**
   - 现有线索表明，Codex 与 image generation 存在独立 usage limits；
   - 因此不能把 Codex 登录和图片生成额度直接视为完全同池；
   - 更不能承诺“零额外限制”“天然免费”或“完全等价于 API 路线”。

4. **Codex 宿主路径适合作为低门槛接入通道，但不适合作为唯一正式后端**
   - 原因包括登录态稳定性、平台差异、`app-server` / `exec` 行为不一致，以及 API key 覆盖登录后导致意外计费的风险；
   - 因此它适合作为 host adapter，而不是唯一 backend。

5. **OpenAI 官方 API 路线仍是长期正式方案**
   - 官方图片生成 API / tool surface 是稳定、宿主无关的能力边界；
   - 这条路线更符合 `videoclaw` 后续要适配 Hermes / OpenClaw / Codex 的长期目标。

#### 本轮结论

图片能力采用**双轨架构**，主次明确：

1. **正式 provider：`openai-image`**
   - 定位：标准图片 backend；
   - 职责：通过 OpenAI 官方 API 提供宿主无关的图片生成能力；
   - 目标：成为 `videoclaw` 长期稳定的正式图片 provider。

2. **宿主适配器：`codex-host-image`**
   - 定位：host capability adapter；
   - 职责：复用本机 Codex 的图片生成能力；
   - 目标：先做到“像 `plotloom` 一样能跑通”，为已有 Codex / ChatGPT 用户提供低门槛路径。

也就是说：

- **短期**：复用 Codex host capability 跑通体验；
- **长期**：用 OpenAI 官方 API 建立正式 provider；
- **架构上**：两者并存，但角色不同，不能混为一个概念。

#### 能力分层

推荐显式分成两层：

1. **图片 provider 层**
   - 面向模型厂商的正式后端抽象；
   - 现有候选包括：`gemini`、`dashscope`、`volcengine`、`openai-image`；
   - 其中 `openai-image` 是新增的正式 OpenAI 图片 provider。

2. **宿主能力适配层**
   - 面向宿主运行时的能力复用通道；
   - 当前候选包括：`codex-host-image`；
   - 后续理论上可扩展到 `hermes-host-image`、`openclaw-host-image` 等。

两层的角色必须清晰区分：

- `openai-image` 是 **provider**；
- `codex-host-image` 是 **host adapter**；
- 前者强调宿主无关与正式能力边界；
- 后者强调低门槛与宿主集成便利性。

#### auth / execution / billing 模型

系统必须显式区分以下三个维度：

1. **auth source**（认证来源）
   - `api_key`
   - `chatgpt_login`

2. **execution surface**（执行面）
   - `openai_api`
   - `codex_host`

3. **billing expectation**（计费预期）
   - `api_billed`
   - `subscription_limited`
   - `unknown`

对应关系建议如下：

- `openai-image`
  - auth source: `api_key`
  - execution surface: `openai_api`
  - billing expectation: `api_billed`

- `codex-host-image`
  - auth source: `chatgpt_login`（或本机 Codex 登录态）
  - execution surface: `codex_host`
  - billing expectation: `subscription_limited` 或 `unknown`

注意：不应使用 `subscription_free` 这类暗示“天然免费/无限”的表述。

#### 命名结论

正式采用以下命名：

- `openai-image`
- `codex-host-image`

不建议把 `imagegen2` 作为正式后端名称。`imagegen2` 可以继续作为内部讨论代称，但不应成为 PRD 的正式术语。

#### 配置方向

推荐通过统一的 `models.image.backend` 指定当前图片后端，例如：

```yaml
models:
  image:
    backend: openai-image
```

或：

```yaml
models:
  image:
    backend: codex-host-image
```

并按 backend 分别配置参数，例如：

```yaml
models:
  image:
    backend: openai-image
    model: gpt-image-1
    auth: api_key
```

```yaml
models:
  image:
    backend: codex-host-image
    auth: chatgpt_login
    codex_mode: exec
```

不建议使用“provider 是 OpenAI，但实际走 Codex host”这种混合表述方式，以免混淆厂商后端和宿主执行面。

#### CLI 方向

第一阶段图片能力不追求复杂命令树，而是优先支持：

- 选择 backend；
- 执行 doctor；
- 执行 smoke；
- 正常生成与归档。

推荐命令面：

```bash
videoclaw config --get models.image.backend
videoclaw config --set models.image.backend=codex-host-image
videoclaw config --set models.image.backend=openai-image

videoclaw doctor --backend codex-host-image
videoclaw doctor --backend openai-image

videoclaw image smoke --backend codex-host-image
videoclaw image smoke --backend openai-image
```

其中：

- `codex-host-image` 的 doctor 应重点检查：
  - 是否安装 `codex`；
  - 是否已登录；
  - 是否可用 `image_generation`；
  - 是否存在 API key 覆盖登录态、导致意外计费的风险；
  - 当前平台是否存在已知问题。

- `openai-image` 的 doctor 应重点检查：
  - 是否存在 `OPENAI_API_KEY`；
  - API key 是否可用；
  - 模型名是否有效；
  - 当前网络与返回格式是否正常。

#### 对 repo 结构的影响

无论图片能力来自 `openai-image` 还是 `codex-host-image`，都不应由 backend 决定最终目录结构。

推荐归档规则：

- 共享资产图：落到 `assets/characters/`、`assets/scenes/`、`assets/props/`、`assets/covers/`
- 某条视频的工作图：落到 `videos/<slug>/images/`

也就是说：

- backend 只负责出图；
- `videoclaw` 负责归档；
- 能力来源可以变，但 repo 落点必须稳定。

#### 与 `plotloom` 的关系

本轮不采用“直接照搬 `plotloom` 图片方案”的表述，而采用：

- 复用 `plotloom` 已验证的 Codex host capability 路线；
- 但在 `videoclaw` 中明确拆分为“正式 provider”与“宿主适配器”两层。

这样既承认 `plotloom` 已经验证了可行路径，也避免把 `videoclaw` 绑死到 `plotloom` 当前实现上。

#### 本阶段明确不承诺的内容

当前阶段不应承诺：

- 只要有 Codex / ChatGPT 订阅，就一定无需额外限制地使用图片生成；
- `codex-host-image` 在所有平台、所有宿主、所有运行模式下行为一致；
- `codex-host-image` 可以替代正式的 OpenAI 图片 provider；
- `imagegen2` 会作为最终对外产品命名。

---

### 3. 视频模型能力需要像 plotloom 一样真正调通并产品化

#### 现状

`videoclaw` 当前虽然有视频 provider 抽象，也接入了 VolcEngine / DashScope 等方向，但成熟度、可审计性和生产流程治理上仍弱于 `plotloom`。

#### 问题

相比 `plotloom`，`videoclaw` 当前视频链路在以下方面偏弱：

- reference intent 不够显式；
- prompt 落盘、追踪和复盘能力不足；
- task / receipt / 状态记录不够完善；
- candidate 管理与 selected 固化能力不足；
- provider smoke / doctor / deep check 能力不足；
- 对真实视频 provider 的“可持续调通”程度不够。

#### 调整原则

本轮目标不是把 `videoclaw` 直接做成第二个 `plotloom`，而是让它从“能调 provider 出文件”升级成“可生产、可调试、可复跑的视频工具”，同时保持比 `plotloom` 更轻的心智和结构。

因此：

- 不直接引入 `plotloom` 那套完整的重型 review / continuity / compare 体系；
- 优先补齐最小生产闭环；
- 先覆盖单段 video，再向多段 video 扩展。

#### 本轮结论

视频能力应升级为：

- **`video` 是最小必选治理单位**；
- **`clip` 是可选扩展单位，不是强制前提**；
- 系统先在 `video` 级补齐最小生产闭环；
- 只有在确实需要多段生成时，才引入 `clips/` 细分结构。

这意味着：

- 单段视频不应被强制拆成 clip；
- 多段视频可以按 clip 管理；
- `clip` 不是默认前提，而是按需扩展。

#### 目标方向

把视频生成从“能调用 provider”升级为“可调试、可追踪、可复跑的轻量生产链路”。

第一阶段应至少补齐以下 **6 个最小闭环能力**：

1. reference planning
2. compiled prompt 落盘
3. task / receipt 记录
4. candidate 管理
5. selected 固化
6. doctor / smoke

这些能力先在 `video` 级成立，必要时再下沉到 `clip` 级。

#### 目录结构方向

##### 单段 video（默认）

对于不需要拆段的单条视频，推荐结构：

```text
videos/<slug>/
├── meta.json
├── brief.md
├── storyboard/
├── images/
├── render/
│   ├── input/
│   │   ├── reference.json
│   │   └── prompt.md
│   ├── candidates/
│   ├── selected.mp4
│   └── task.json
├── audio/
└── final.mp4
```

说明：

- `render/` 是单段视频的默认生成工作目录；
- 不需要先引入 `clip` 概念；
- 一条视频可以直接在 `render/` 下完成输入、候选、选择和状态记录。

##### 多段 video（按需扩展）

如果某条视频需要拆成多个镜头/段落，则再扩展为：

```text
videos/<slug>/
├── meta.json
├── brief.md
├── storyboard/
├── images/
├── clips/
│   ├── clip-01/
│   │   ├── input/
│   │   │   ├── reference.json
│   │   │   └── prompt.md
│   │   ├── candidates/
│   │   ├── selected.mp4
│   │   └── task.json
│   └── clip-02/
├── audio/
└── final.mp4
```

说明：

- 多段视频才引入 `clips/`；
- 每个 clip 自己维护输入、候选、selected 和 task 记录；
- merge 时使用各 clip 的 `selected.mp4`。

#### 6 个最小闭环能力如何落盘

##### 1. reference planning

先做轻量化落盘，不强制上复杂 schema。

- 单段 video：`render/input/reference.json`
- 多段 video：`clips/<clip-id>/input/reference.json`

建议至少记录：

- first frame / source image
- 使用到的共享资产路径
- 其他参考图或补充素材路径

##### 2. compiled prompt 落盘

无论最终 prompt 是用户直写还是系统拼装，都应把“最终送给 provider 的文本”落盘。

- 单段 video：`render/input/prompt.md`
- 多段 video：`clips/<clip-id>/input/prompt.md`

##### 3. task / receipt 记录

建议：

- 单段 video：`render/task.json`
- 多段 video：`clips/<clip-id>/task.json`

第一阶段至少记录：

- task id
- provider
- model
- mode
- status
- created_at / updated_at
- 输入引用
- prompt 文件路径
- candidates 列表
- selected 指向
- 错误信息（如失败）

##### 4. candidate 管理

生成结果不应散落或覆盖，应统一归档：

- 单段 video：`render/candidates/`
- 多段 video：`clips/<clip-id>/candidates/`

这一步是从“调用式工具”升级到“生产型工具”的关键步骤。

##### 5. selected 固化

必须有显式“选择最终版本”的动作与落点：

- 单段 video：`render/selected.mp4`
- 多段 video：`clips/<clip-id>/selected.mp4`

后续 merge 或发布默认只消费 selected 结果，而不是直接消费全部候选。

##### 6. doctor / smoke

视频 provider 需要正式具备可检查、可 smoke 的能力，而不是只看“能不能请求成功”。

第一阶段建议支持：

```bash
videoclaw doctor --backend volcengine-video
videoclaw doctor --backend dashscope-video
videoclaw video smoke --backend volcengine-video
videoclaw video smoke --backend dashscope-video
```

#### CLI 方向

既然系统已经采用 `videoclaw video <subcommand>` 的命令心智，视频侧建议分两层：

##### video 级（默认）

适合单段视频：

```bash
videoclaw video create summer-launch
videoclaw video list
videoclaw video status summer-launch
videoclaw video generate summer-launch
videoclaw video select summer-launch v002
videoclaw video merge summer-launch
```

##### clip 级（按需）

适合多段视频：

```bash
videoclaw video clip create summer-launch clip-01
videoclaw video clip list summer-launch
videoclaw video clip generate summer-launch clip-01
videoclaw video clip select summer-launch clip-01 v002
```

这样可以保证：

- 单段视频不需要先引入 `clip`；
- 多段视频又有清晰的扩展路径；
- 命令结构保持一致。

#### 与 `plotloom` 的关系

本轮不追求把 `plotloom` 的视频生产模型整体搬进 `videoclaw`，而是借它已经验证过的“生产闭环”思想，提炼出更轻的最小集合。

可以概括为：

- 借 `plotloom` 的方法论；
- 不直接照搬 `plotloom` 的重工作流；
- 优先补齐最小 artifact 和最小命令闭环。

#### 本阶段明确不引入的能力

当前阶段先不引入以下较重能力：

- 重型 review artifact
- continuity 分析
- compare 报告
- 多层 prompt lint
- 强约束 reference schema
- 完整的 `plotloom` 式 compare / review / selection 套件

这些能力有价值，但更适合作为下一阶段扩展，而不是当前版本的必做项。

#### PRD 级结论

`videoclaw` 的视频能力应升级为以 `video` 为最小必选生产单元、以 `clip` 为可选扩展单元的轻量生产链路；系统至少补齐 reference planning、compiled prompt 落盘、task/receipt 记录、candidate 管理、selected 固化、doctor/smoke 六项能力，使单段视频和多段视频都能实现可调试、可追踪、可复跑的生成流程。

---

### 4. 需要适配 Hermes / OpenClaw / Codex 等宿主，并通过插件方式安装

#### 现状

当前 `videoclaw` 的推荐使用方式和技能安装方式，明显以 Claude Code 为中心。CLI 本身已经是标准 Python 包，但宿主接入方式仍然主要围绕 `.claude-plugin` 和 Claude Code 插件市场展开。

#### 问题

这会带来几个限制：

- 宿主耦合过强；
- 用户迁移到其他 agent/runtime 时复用困难；
- 安装方式不统一；
- skill / prompt / workflow 容易在不同宿主里重复维护；
- 难以形成“同一工作流，多宿主可接入”的生态。

#### 调研结论

本轮调研后，可以明确几点：

1. **Plotloom 的关键经验不是某个单独宿主，而是“CLI 与 skill 分发分离”**
   - CLI 走标准 Python 包分发；
   - `skills/` 目录本身作为主要分发单元；
   - 各宿主只做薄安装适配。

2. **videoclaw 当前的主要短板不是 CLI，而是 skill 分发过度依赖 Claude Code 专用壳**
   - 这会导致宿主切换成本高；
   - 也会让未来 Hermes / OpenClaw / Codex 适配变成复制业务逻辑，而不是复用统一 skill 包。

3. **不同宿主其实不是同一种类型**
   - 有些宿主更像 skills-style host，适合直接消费 skill 目录；
   - 有些宿主更像 plugin-style host，适合正式 manifest；
   - Codex 更像 runtime / host capability，不应简单按“技能市场宿主”处理。

#### 本轮结论

宿主适配采用 **`canonical skill pack + host adapters`** 架构：

1. **`videoclaw` CLI 是唯一执行核心**
   - 负责确定性执行、配置读取、backend 调用、产物归档；
   - 永远宿主无关。

2. **仓库内 `skills/` 是唯一工作流定义源**
   - 负责承载 skill 的文案、交互、模板、上下文和工作流定义；
   - 不再以 `.claude-plugin` 作为主分发中心。

3. **各宿主只做最薄的 adapter**
   - 负责安装路径映射、manifest / metadata、权限声明、tool 能力映射和宿主特有说明；
   - 不复制核心 skill 内容。

#### 目标架构

推荐采用三层结构：

##### 层 1：Core CLI

`videoclaw` Python 包，职责包括：

- 配置读取
- backend 调用
- 文件处理
- 产物归档
- 结构化结果返回

这一层始终保持宿主无关。

##### 层 2：Canonical skill pack

仓库里的 `skills/` 目录升级为规范技能包。每个 skill 目录应是完整工作流单元，例如：

```text
skills/
  video-quick-create/
    SKILL.md
    templates/
    references/
  video-i2v/
    SKILL.md
    templates/
    references/
```

这一层是：

- 工作流定义源
- 文案与交互定义源
- 模板与上下文定义源
- 各宿主共享的唯一 skill 内容源

##### 层 3：Host adapters

不同宿主只负责最薄的适配层，例如：

- `.claude-plugin/` → Claude Code adapter
- `openclaw.plugin.json` 或 OpenClaw plugin 目录 → OpenClaw adapter
- Hermes profile 安装说明 / wrapper → Hermes adapter
- Codex runtime wrapper / host integration docs → Codex adapter

关键约束：

- adapter 不复制核心 skill 内容；
- adapter 只引用 canonical skill pack；
- 业务逻辑、模板和 prompts 不在不同宿主里各维护一套。

#### 宿主分类与适配策略

##### A 类：directory / skills-style hosts

特点：

- 能直接消费 skill 目录；
- 有固定的 skills 路径；
- 更像“加载 skill pack”。

当前候选：

- Claude Code
- Hermes
- OpenCode
- 某些 OpenClaw 形态

适配策略：

- 尽量复用同一 skill 目录结构；
- 安装器只负责复制 / 软链 / 注册；
- 不修改核心业务逻辑。

##### B 类：manifest / plugin-style hosts

特点：

- 有正式 plugin manifest；
- 有安装 / 启用 / 权限模型；
- 更像“插件系统”。

当前候选：

- OpenClaw

适配策略：

- 基于 canonical skill pack 生成 manifest；
- 插件元数据单独维护；
- skill 内容仍不复制。

##### C 类：runtime / execution-style hosts

特点：

- 更像执行环境；
- 不一定天然有技能市场；
- 更像 host capability / app server / runtime bridge。

当前候选：

- Codex

适配策略：

- 不把 Codex 当普通技能市场宿主；
- 而把它视为 runtime / host capability 适配对象；
- 更关注如何在 Codex 环境中调用 `videoclaw` 与复用宿主能力，而不是如何按 marketplace 方式安装 skill。

#### 宿主优先级

推荐优先级如下：

1. **Priority 1：把 `skills/` 变成真正主分发单元**
   - 这是第四题的根本；
   - 以后主叙事应从“安装 Claude 插件”改为“安装 videoclaw skill pack”。

2. **Priority 2：保留并重定义 Claude Code adapter**
   - `.claude-plugin` 继续保留；
   - 但定位降级为 Claude Code 专用 adapter；
   - 不再充当主分发中心。

3. **Priority 3：优先做 OpenClaw adapter**
   - OpenClaw 最适合作为正式 plugin 宿主试验场；
   - 可验证宿主中立插件化是否真的成立。

4. **Priority 4：Hermes 先走轻适配**
   - 先提供 skills 目录式接入与安装说明；
   - 暂不强求正式 manifest 机制。

5. **Priority 5：Codex 单独处理**
   - Codex 不是第四题里的“插件市场重点”；
   - 更像 runtime / host capability 层面的适配对象；
   - 与第二题里的 `codex-host-image` 能力路线保持一致。

#### 安装叙事调整

未来文档建议改成两步：

##### 1. 先安装 CLI

```bash
uvx videoclaw --help
# 或
pip install videoclaw
```

##### 2. 再安装 skill pack / host adapter

根据宿主选择接入方式，例如：

- Claude Code adapter
- OpenClaw adapter
- Hermes adapter
- 未来其他 adapter

这样可以把“CLI 分发”和“工作流分发”明确拆开，而不再把 Claude Code marketplace 当作主入口。

#### 分发模型

建议明确区分两条分发线：

##### A. CLI distribution

标准 Python 包分发：

- PyPI
- `uvx`
- `pip`

##### B. Skill-pack distribution

标准 skill 包分发：

- GitHub 仓库直接安装
- `skills add`
- 本地路径安装
- 宿主 adapter 生成器 / wrapper

这样可以让执行层和工作流层各自独立演进。

#### 与 `.claude-plugin` 的关系

`.claude-plugin` 不再作为宿主中立分发中心，而是明确降级为：

- Claude Code 专用 adapter；
- 某一条安装通道；
- 不是唯一事实源；
- 不是其他宿主适配的模板来源。

#### 本阶段明确的决策

本轮正式定下以下决策：

- `videoclaw` CLI 是唯一执行核心；
- `skills/` 是唯一工作流定义源；
- 宿主适配采用薄 adapter，不复制业务逻辑；
- `.claude-plugin` 不再做主分发中心；
- OpenClaw 优先做正式 plugin adapter；
- Hermes 先走目录式 skills 适配；
- Codex 作为 runtime / host capability 适配对象单独处理。

#### PRD 级结论

`videoclaw` 的宿主适配采用 “canonical skill pack + host adapters” 架构：`videoclaw` CLI 作为唯一执行核心，仓库内 `skills/` 作为唯一工作流定义源，各宿主仅负责最薄的安装、manifest、权限和能力映射适配；`.claude-plugin` 由主分发中心降级为 Claude Code 专用 adapter，OpenClaw 优先作为正式插件宿主适配目标，Hermes 先采用 skills 目录式接入，Codex 则作为 runtime / host capability 适配对象单独处理。

---

## 设计原则（草案）

1. **Workspace-first，而不是 single-video-first**
   - 核心抽象应支持共享资产和多个视频持续产出。

2. **Repo-first / Artifact-first**
   - 关键中间产物应落盘并可审查，而不是只存在运行时状态中。

3. **Host-neutral**
   - CLI 与生产模型不绑定单一宿主；宿主只负责交互和工具调度。

4. **Provider-pluggable**
   - 图片、视频、音频、发布能力都应可插拔。

5. **Fast path + Production path 并存**
   - 既保留轻量快速生成入口，也支持更完整的生产工作流。

---

## 本轮 brainstorm 需要优先讨论的问题

1. `videoclaw` 的核心单位是否要从 project 改成 workspace / repo？
2. 多视频产物与共享资产的目录结构应该怎么设计？
3. 是否应该直接吸收 `plotloom` 的 artifact 模型？
4. OpenAI 图片生成要优先走 API，还是优先复用 Codex 宿主能力？
5. 视频链路是迁移 `plotloom` 成熟实现，还是在 `videoclaw` 内重建？
6. 多宿主插件分发机制应如何设计？

---

## 非目标（当前阶段）

以下内容暂不在本轮 PRD 的首要范围内：

- 立即重写全部 provider；
- 立即统一 `videoclaw` 与 `plotloom` 为单一仓库；
- 立即定义最终 UI 产品形态；
- 立即承诺任何特定宿主的一键安装细节已经落地。

---

## 备注

这个文档当前是问题定义和方向梳理稿，不是最终方案。后续应通过 brainstorm 把：

- 核心抽象；
- 目录结构；
- provider 适配策略；
- 多宿主插件分发模型；
- 与 `plotloom` 的关系

逐步收敛为正式设计。
