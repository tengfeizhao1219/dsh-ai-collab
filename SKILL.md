---
name: ai-collab
description: AI 多角色协作开发框架。当用户要启动一个 AI 协作软件项目、把已有项目切换到「文件即通信」的多角色协作模式、或新会话需要接棒已有协作项目时使用。初始化项目五件套（CONTEXT/ROLE_CARDS/TASK_BOARD/RELAY/COMMLOG/COLLABORATION/NAVIGATION/SESSION_BOOT），并驱动 O 主控 + 专业角色的任务流转、关口检查与文档同步。
version: 1.0.0
---

# ai-collab 技能说明

本技能把「文件即通信」的多角色 AI 协作机制封装为可复用流程。适用于：任何软件项目的 AI 协作开发。

## 核心原则

1. **文件即通信**：所有角色通过 git 仓库中的约定文件交换信息，不靠会议、不靠 IM、不催进度。
2. **一个角色 = 一个固定身份**：身份由 ROLE_CARDS.md 权威定义，全程复用。
3. **先读后动**：新会话启动按序读约定文件（CONTEXT → ROLE_CARDS → TASK_BOARD → COMMLOG → RELAY → COLLABORATION → NAVIGATION），汇报继承摘要后再动手。
4. **owner 只拍板**：仅关键决策点决策、提供凭证；AI 显式请求资源，绝不编造。
5. **关口检查**：阶段级全 ✅ 才放行下一阶段。

## 启动流程

1. 运行 `python3 <插件路径>/init.py <项目名> --desc "..."` 生成约定文件（若项目已存在约定文件则跳过）。
2. 读取生成的 CONTEXT.md、RELAY.md、TASK_BOARD.md 了解项目状态。
3. 扮演 O 主控：拆解任务 → 派发子 Agent（角色按 ROLE_CARDS.md）→ 汇总交付 → 关口检查。
4. 每个交接点在 COMMLOG.md 留痕；改动后立即 git commit+push。

## 约定文件职责速查

| 文件 | 作用 | 维护者 |
|---|---|---|
| CONTEXT.md | 项目速览（第一必读） | 全员 |
| ROLE_CARDS.md | 角色卡 | O |
| TASK_BOARD.md | 任务看板（📋→🔄→✅/🚫） | 全员认领 |
| RELAY.md | 阶段流水线 + 里程碑 + 待拍板项 | O |
| COMMLOG.md | 沟通交接记录（倒序） | 全员 |
| COLLABORATION.md | 协作总规 | O |
| NAVIGATION.md | 文档导航索引 | K |

## 派发子 Agent 模板

```
你将在「<项目名>」中扮演【角色】。先读 ROLE_CARDS.md 对应角色卡确定身份，
读 CONTEXT.md 与 TASK_BOARD.md 了解上下文，认领任务后工作；
交付 = 更新 TASK_BOARD + COMMLOG 留痕 + 产出物写回约定目录；改前 pull --rebase，改后立即 commit+push。
```

## 可选同步

- `scripts/git_sync.sh`：每 60s 自动 commit+push。
- `scripts/notion_sync.py`：本地 .md → Notion 数据库幂等同步（需 NOTION_TOKEN + NOTION_DATABASE_ID）。
