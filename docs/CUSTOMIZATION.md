# 定制指南（CUSTOMIZATION）

> 如何把 ai-collab 从"默认模板"定制成"你的项目专属机制"。原则：**先按默认跑起来，再按需裁剪**。

---

## 1. 角色裁剪与新增

默认 7 角色（O/I/A/P/D/Q/K）覆盖大多数软件项目。按项目实际裁剪：

| 场景 | 建议 |
|---|---|
| 无外部系统/数据源接入 | 去掉 A（适配/接入），或改为「数据工程师」 |
| 纯前端项目 | I 与 D 合并为「全栈」；P 去掉或改「状态管理」 |
| 算法/数据密集项目 | 把 P 细分为「算法」+「数据」两个角色 |
| 有运维/发布要求 | 新增「R 发布/运维」角色（CI/CD、监控、灰度） |

**角色卡格式**（新增角色照抄）：

```markdown
## ⑧ 角色名（英文代号）

- **身份**：一句话定位
- **可以**：职权清单（列到动作级）
- **不可以**：越权红线（至少 2 条）
- **产出目录**：`docs/xx-xx/`
- **参与阶段**：Phase x
- **上级**：O
```

> 规则：角色只减不增太快。一个角色能独立交付一个"可验收的产出物"才保留。

---

## 2. 阶段流水线定制

默认流水线：Phase 0 环境就绪 → Phase 1 需求设计 → Phase 2 开发实现 → Phase 3 测试验收 → Phase 4 交付复盘。

定制原则：
- **阶段边界 = 可关口检查的边界**。每个阶段结束必须有可验证的产出（文档/代码/验收报告），否则合并到相邻阶段。
- 大项目可拆细：如 Phase 2 开发实现 → Phase 2a 核心逻辑 / Phase 2b 前端 / Phase 2c 联调。
- 每阶段在 RELAY.md 中登记：目标 / 入口文档 / 状态 / 出口（下一棒输入）。

---

## 3. 验收闭环定制（替换"UI/UX 验收"示例）

机制 §七 的验收闭环以 UI/UX 为例。任何专业领域都可套用同一模式：

| 领域 | 设计权威角色 | 交付物标准 | 不可自行推断项 |
|---|---|---|---|
| UI/UX | D | 1:1 原型 + 规格 + 图标规范 | 色值/间距/圆角/字重/图标/状态覆盖 |
| 数据/算法 | P | 指标定义 + 口径文档 + 样例数据 | 口径/阈值/特征/样本 |
| 后端 API | I | 接口契约（OpenAPI）+ 示例请求/响应 | 字段名/状态码/错误语义 |
| 安全 | Q 扩展 | 威胁模型 + 红线清单 | 加密算法/密钥管理/合规项 |

---

## 4. 硬前提的写法（CONTEXT.md）

硬前提 = owner 拍板的不可违背约束，Q 角色红线审计依据。好的硬前提：

- ❌ 抽象：「保证质量」
- ✅ 可审计：「UI 复用既有设计令牌，禁止新增 hex 色值」「增量改动必须带 `BRIDGE` 标记且可整体摘除」「所有产出物必须是 AI 可直接消费的结构化文档」

---

## 5. 同步通道配置

### Git 同步（推荐必开）

```bash
git init
nohup bash scripts/git_sync.sh . 60 >/dev/null 2>&1 &
```

### Notion 同步（可选）

```bash
# 1. 建 Notion 数据库，属性：名称(title) / 内容哈希(rich_text) / 类型(select)
# 2. 配置凭证
mkdir -p ~/.ai-collab && chmod 700 ~/.ai-collab
cat > ~/.ai-collab/secrets.env <<'EOF'
NOTION_TOKEN=ntn_xxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EOF
chmod 600 ~/.ai-collab/secrets.env
# 3. 启动守护
nohup python3 scripts/notion_sync.py --dir . --once 2>/dev/null; \
nohup python3 scripts/notion_sync.py --dir . >/dev/null 2>&1 &
```

> 注意：Notion 数据库的「名称」属性用于匹配本地文件名，首次同步前请确认数据库属性名一致。

---

## 6. 机制自身的迭代（吃自己的狗粮）

项目复盘（Phase 4.3）时，把「这套机制哪里卡住了」回写：
- 卡在角色权限不清 → 回改 ROLE_CARDS
- 卡在文档不同步 → 回改同步脚本/NAVIGATION
- 卡在并行冲突 → 回改 Git 纪律/认领规则

改进积累后，回更本插件模板与 MECHANISM.md，形成机制版本迭代（plugin.json version）。
