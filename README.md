# ai-collab · AI 协作开发框架插件

> 把「**文件即通信**」的多角色 AI 协作机制做成通用插件：任何软件项目，通过本插件一键初始化约定文件，任何 AI 客户端都能驱动 AI 多角色协作（O 主控 + 专业角色）完成项目。

- **机制来源**：真实项目实践「AI 情报官」多角色协作机制 v1.0（源自 One News 多会话协作框架），已验证可支撑一个完整项目的 AI 协作开发。
- **核心洞察**：AI 会失忆、会并行互相覆盖、会自作主张、会编造——文件机制解决这一切。AI 的"云端记忆"只带你是谁，**文件机制才带项目进行到哪**。
- **不绑定任何 AI 客户端**：载体是文件，WorkBuddy / CodeBuddy / DeepSeek Harness / Claude 桌面端等均适用。

---

## 快速开始（3 步）

```bash
# 1. 初始化一个新项目（生成约定文件五件套 + docs 骨架）
python3 ai-collab/init.py my-app --desc "团队任务管理小程序" \
    --tech "微信小程序 + 云开发" --constraint "UI 复用现有设计令牌" -y

# 2. （可选）git 初始化 + 同步守护
cd my-app && git init
nohup bash ../ai-collab/scripts/git_sync.sh . 60 >/dev/null 2>&1 &

# 3. 打开任意 AI 客户端，粘贴 SESSION_BOOT.md 的接棒提示词 → AI 完成上下文继承 → 开始派发任务
```

> 已有项目想切换协作模式：在项目根目录跑 `init.py` 生成约定文件（目录非空时先 `--dir` 指定子目录或手动放置模板），
> 或直接把 `templates/` 下的模板复制进项目根目录并替换 `{{变量}}`。

---

## 包结构

```
ai-collab/
├── README.md                  ← 本文件
├── plugin.json                ← 插件元数据
├── SKILL.md                   ← 技能形态入口（支持自定义技能的工具可引用）
├── init.py                    ← 一键初始化脚手架
├── docs/
│   ├── MECHANISM.md           ← 机制原理（为什么有效）
│   └── CUSTOMIZATION.md       ← 定制指南（角色/阶段/验收/同步）
├── templates/                 ← 通用模板（{{变量}} 占位）
│   ├── CONTEXT.md.tpl         ← 项目速览（第一必读）
│   ├── ROLE_CARDS.md.tpl      ← 角色卡（O + 6 专业角色）
│   ├── TASK_BOARD.md.tpl      ← 任务看板（📋→🔄→✅/🚫 + 关口检查）
│   ├── RELAY.md.tpl           ← 阶段流水线 + 里程碑 + 待拍板项
│   ├── COMMLOG.md.tpl         ← 沟通交接记录（倒序）
│   ├── COLLABORATION.md.tpl   ← 协作总规
│   ├── NAVIGATION.md.tpl      ← 文档导航与交叉引用索引
│   └── SESSION_BOOT.md.tpl    ← 新会话接棒提示词（复制即用）
└── scripts/
    ├── git_sync.sh            ← Git 守护（60s 自动 commit+push）
    └── notion_sync.py         ← Notion 文档同步（可选，幂等）
```

---

## 机制速览（详见 docs/MECHANISM.md）

| 要素 | 要点 |
|---|---|
| 文件即通信 | 约定文件是唯一事实来源；新会话读文件 100% 继承 |
| 角色体系 | O 主控持有全局，子 Agent 临时扮演 I/A/P/D/Q/K，身份由角色卡权威定义 |
| 约定文件 | CONTEXT / ROLE_CARDS / TASK_BOARD / RELAY / COMMLOG / COLLABORATION / NAVIGATION |
| Git 纪律 | 改前 pull --rebase，改后立即 commit，小步快推 |
| 任务流转 | 📋 待认领 → 🔄 进行中 → ✅ 完成 / 🚫 阻塞；交付交接包；3 分支意图识别 |
| 关口检查 | 阶段级全 ✅ 由 O 检查，通过才放行下一阶段 |
| owner 参与 | 只拍板 + 给凭证；AI 显式请求资源，绝不编造 |
| 会话继承 | 新会话按序读五件套 → 汇报继承摘要 → 等待派发 |
| 同步 | Git 60s 守护 + Notion 60s 幂等同步（可选） |

---

## 常见问题

**Q: 我的 AI 客户端不支持自定义技能，能用吗？**
能。核心用法就是把 `SESSION_BOOT.md` 的接棒提示词粘贴进新会话——任何能读文件、能 git 的 AI 都能按机制运行。

**Q: 云端会话和本地会话能并行吗？**
能。两边都遵守 Git 纪律（改前拉、改后推、认领前看状态），各自改不同文件时无冲突。

**Q: 子 Agent 怎么派？**
O 用 `SESSION_BOOT.md` 中的「子 Agent 身份注入」模板开头，子 Agent 启动读角色卡获得身份，交付写回约定文件。

**Q: 需要一直开着同步守护吗？**
不必。守护只是让多端实时一致；单人单机时手动 commit+push 即可（机制不依赖守护）。

---

## 许可

MIT。机制与模板欢迎自由复用与改进；改进建议可回写本包（docs/CUSTOMIZATION.md §6）。

---

## 作为 DSH 插件安装 / 发布

本包已按官方规范打包为 **DSH 插件（cordis bundle 形态）**：`package.json` 声明 `dsh.bundle` + `cordis.patch.yml`，并注册 `ai_collab_init` 工具（AI 可直接调用它初始化协作项目）。

### 本地安装（有 dsh CLI 时）

```bash
dsh plugin --profile web add ./ai-collab            # 本地目录
dsh plugin --profile web add dsh-ai-collab          # npm 发布后
dsh plugin --profile web add github:you/dsh-ai-collab  # GitHub 直装（需授权 prepare 脚本）
```

无 dsh CLI 的桌面版：把本仓库克隆到 `~/.dsh/profiles/web/node_modules/dsh-ai-collab`，并在 `~/.dsh/profiles/web/cordis.patch.yml` 注册：

```yaml
- insert:
    - id: ai-collab
      name: dsh-ai-collab
```

重启 DSH 生效。

### 发布到市场（让其他人可用）

1. **npm 发布**（供 `dsh plugin add dsh-ai-collab`）：`pnpm publish`（本包为纯 JS，无构建步骤）。
2. **GitHub 仓库 + 打 `dsh-plugin` topic** → [DSH 插件市场](https://github.com/bradeGithub/DSH-Plugins-Marketplace) 每 2 小时自动收录，用户可在 Web GUI 设置页一键安装；`SKILL.md` 会被识别为 skill 形态安装到 `~/.dsh/skills/`。
3. 参考：官方发布文档 [docs/user/develop/basic/publish.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/main/docs/user/develop/basic/publish.zh.md)。
