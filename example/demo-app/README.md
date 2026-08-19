# demo-app

> 由 ai-collab 1.0.0 生成（2026-08-19）。这是一个 **AI 多角色协作项目**：沟通介质是文件，没有 IM、没有会议。

示例

## 快速开始（新会话接棒）

把 `SESSION_BOOT.md` 中的接棒提示词发给你的 AI（WorkBuddy / CodeBuddy / DeepSeek Harness / Claude 等均可），
AI 会按序读取约定文件完成上下文继承，然后即可派发任务。

## 约定文件（第一读者是 AI）

| 文件 | 作用 |
|---|---|
| `CONTEXT.md` | 项目速览（第一必读） |
| `ROLE_CARDS.md` | 角色卡（O + 专业角色） |
| `TASK_BOARD.md` | 任务看板（任务级状态） |
| `RELAY.md` | 阶段流水线 + 里程碑 + 待拍板项 |
| `COMMLOG.md` | 沟通交接记录（倒序） |
| `COLLABORATION.md` | 协作总规 |
| `NAVIGATION.md` | 文档导航与交叉引用索引 |

## 机制

- 机制原理：ai-collab 插件 `docs/MECHANISM.md`
- 定制指南：ai-collab 插件 `docs/CUSTOMIZATION.md`
