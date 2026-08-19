# 项目速览（CONTEXT）

> 任何 AI 角色的「记忆外挂」，**第一必读**。由全员在会话结束时更新，谁改谁负责。
> 本文件由 ai-collab 插件生成，机制版本：{{MECH_VERSION}}，初始化日期：{{START_DATE}}

## ⚠️ 这是一个 AI 协作项目

本项目由 AI 多角色协作完成（角色见 ROLE_CARDS.md），仅「用户（owner）」是真人。
沟通介质是文件（TASK_BOARD、COMMLOG、RELAY），**没有 IM、没有会议**。协作机制见 COLLABORATION.md。

## 基本信息

- **项目名**：{{PROJECT_NAME}}
- **定位**：{{PROJECT_DESC}}
- **技术栈**（待定/已定）：{{TECH_STACK}}
- **仓库**：{{REPO_URL}}
- **协作机制版本**：{{MECH_VERSION}}

## 硬前提（不可违背）

1. {{HARD_CONSTRAINT_1}}
2. {{HARD_CONSTRAINT_2}}
3. {{HARD_CONSTRAINT_3}}

> 硬前提由 owner 在项目启动时拍板，Q 角色负责红线审计。新增硬前提须经 owner 确认并写入本文件。

## 当前状态（{{START_DATE}}）

- ✅ 环境与资源就绪（Phase 0 完成项，参照 TASK_BOARD）
- 🔴 待定：{{OWNER_DECISIONS}}

## 技术架构速览

```plain text
{{ARCH_SKETCH}}
```

## 协作框架（必读文件）

本文件（CONTEXT.md）· ROLE_CARDS.md · TASK_BOARD.md · RELAY.md · COMMLOG.md · COLLABORATION.md · NAVIGATION.md

## 🔑 常用速查

- **Git 纪律**：改前 `git pull --rebase`，改后立即 commit+push，小步快推。
- **凭证**：存于 secrets 文件（权限 600，不入库），由 owner 提供。
- **同步守护**：`scripts/git_sync.sh`（GitHub）、`scripts/notion_sync.py`（Notion，可选）。
