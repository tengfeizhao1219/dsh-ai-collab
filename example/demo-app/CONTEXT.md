# 项目速览（CONTEXT）

> 任何 AI 角色的「记忆外挂」，**第一必读**。由全员在会话结束时更新，谁改谁负责。
> 本文件由 ai-collab 插件生成，机制版本：1.0.0，初始化日期：2026-08-19

## ⚠️ 这是一个 AI 协作项目

本项目由 AI 多角色协作完成（角色见 ROLE_CARDS.md），仅「用户（owner）」是真人。
沟通介质是文件（TASK_BOARD、COMMLOG、RELAY），**没有 IM、没有会议**。协作机制见 COLLABORATION.md。

## 基本信息

- **项目名**：demo-app
- **定位**：示例项目
- **技术栈**（待定/已定）：微信小程序
- **仓库**：待定
- **协作机制版本**：1.0.0

## 硬前提（不可违背）

1. 待 owner 拍板（项目启动时确认，写入本文件后生效）
2. 所有产物以「AI 实现/输出」为前提生产，且必须是 AI 可直接消费的形态
3. 增量改动必须显式标记且可整体摘除（如需在既有代码库上叠加）

> 硬前提由 owner 在项目启动时拍板，Q 角色负责红线审计。新增硬前提须经 owner 确认并写入本文件。

## 当前状态（2026-08-19）

- ✅ 环境与资源就绪（Phase 0 完成项，参照 TASK_BOARD）
- 🔴 待定：技术栈 / 凭证与外部资源（见 RELAY 待拍板项）

## 技术架构速览

```plain text
（待 Phase 0 技术栈确认后补充架构草图）
```

## 协作框架（必读文件）

本文件（CONTEXT.md）· ROLE_CARDS.md · TASK_BOARD.md · RELAY.md · COMMLOG.md · COLLABORATION.md · NAVIGATION.md · LEARNINGS.md · ADR.md

## 🔑 常用速查

- **Git 纪律**：改前 `git pull --rebase`，改后立即 commit+push，小步快推。
- **凭证**：存于 secrets 文件（权限 600，不入库），由 owner 提供。
- **同步守护**：`scripts/git_sync.sh`（GitHub）、`scripts/notion_sync.py`（Notion，可选）。
