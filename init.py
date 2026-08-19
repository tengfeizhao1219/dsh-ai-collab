#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai-collab init —— 从模板生成 AI 协作项目的约定文件五件套。

用法:
    python3 ai-collab/init.py <项目名> [选项]

选项:
    --desc "一句话描述"         项目定位（写入 CONTEXT）
    --dir <路径>                生成目录（默认: ./<项目名>）
    --tech "技术栈"             技术栈（默认: 待定）
    --repo "https://..."       仓库地址（默认: 待定）
    --constraint "文本"         硬前提，可多次指定（默认: 待 owner 拍板）
    --mech-version 1.0.0        机制版本（默认读 plugin.json）
    -y                          跳过交互确认

示例:
    python3 ai-collab/init.py my-app --desc "团队任务管理小程序" \\
        --tech "微信小程序 + 云开发" --constraint "UI 复用现有设计令牌" -y

生成物（写入 <dir>）:
    CONTEXT.md / ROLE_CARDS.md / TASK_BOARD.md / RELAY.md / COMMLOG.md
    COLLABORATION.md / NAVIGATION.md / SESSION_BOOT.md
    docs/01-需求规划 … docs/06-上线复盘（.gitkeep）
    README.md（项目入口 + 接棒提示词指引）
"""

import argparse
import datetime
import json
import os
import shutil
import sys

MECH_VERSION = "1.0.0"

TEMPLATE_VARS = [
    "PROJECT_NAME", "PROJECT_DESC", "START_DATE", "MECH_VERSION",
    "TECH_STACK", "REPO_URL", "HARD_CONSTRAINT_1", "HARD_CONSTRAINT_2",
    "HARD_CONSTRAINT_3", "ARCH_SKETCH", "OWNER_DECISIONS",
    "EXTRA_OWNER_DECISIONS", "GLOSSARY_ROWS",
]

DOC_DIRS = [
    "01-需求规划", "02-产品设计", "03-技术方案",
    "04-开发实现", "05-测试验收", "06-上线复盘",
]

TPL_FILES = [
    "CONTEXT.md.tpl", "ROLE_CARDS.md.tpl", "TASK_BOARD.md.tpl",
    "RELAY.md.tpl", "COMMLOG.md.tpl", "COLLABORATION.md.tpl",
    "NAVIGATION.md.tpl", "SESSION_BOOT.md.tpl",
    "LEARNINGS.md.tpl", "ADR.md.tpl",
]

TPL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")


def load_plugin_meta():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugin.json")
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def substitute(template: str, ctx: dict) -> str:
    out = template
    for k in TEMPLATE_VARS:
        out = out.replace("{{" + k + "}}", str(ctx.get(k, "")))
    return out


def sanitize_name(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "-" for c in name)


def main():
    ap = argparse.ArgumentParser(description="ai-collab 项目初始化脚手架")
    ap.add_argument("name", help="项目名")
    ap.add_argument("--desc", default="", help="一句话项目定位")
    ap.add_argument("--dir", default=None, help="生成目录（默认 ./<项目名>）")
    ap.add_argument("--tech", default="待定", help="技术栈")
    ap.add_argument("--repo", default="待定", help="仓库地址")
    ap.add_argument("--constraint", action="append", default=[], help="硬前提（可多次）")
    ap.add_argument("--mech-version", default=MECH_VERSION, help="机制版本")
    ap.add_argument("-y", action="store_true", help="跳过确认")
    args = ap.parse_args()

    meta = load_plugin_meta()
    mech = args.mech_version or meta.get("version", MECH_VERSION)
    name = args.name.strip()
    if not name:
        print("错误：请提供项目名"); sys.exit(1)

    out_dir = args.dir or os.path.join(os.getcwd(), sanitize_name(name))
    out_dir = os.path.abspath(out_dir)

    if os.path.exists(out_dir) and os.listdir(out_dir):
        print(f"错误：目标目录非空或已存在：{out_dir}")
        sys.exit(1)

    constraints = args.constraint or [
        "待 owner 拍板（项目启动时确认，写入本文件后生效）",
        "所有产物以「AI 实现/输出」为前提生产，且必须是 AI 可直接消费的形态",
        "增量改动必须显式标记且可整体摘除（如需在既有代码库上叠加）",
    ]
    while len(constraints) < 3:
        constraints.append("—")

    ctx = {
        "PROJECT_NAME": name,
        "PROJECT_DESC": args.desc or "（待 owner 补充一句话定位）",
        "START_DATE": datetime.date.today().strftime("%Y-%m-%d"),
        "MECH_VERSION": mech,
        "TECH_STACK": args.tech,
        "REPO_URL": args.repo,
        "HARD_CONSTRAINT_1": constraints[0],
        "HARD_CONSTRAINT_2": constraints[1],
        "HARD_CONSTRAINT_3": constraints[2],
        "ARCH_SKETCH": "（待 Phase 0 技术栈确认后补充架构草图）",
        "OWNER_DECISIONS": "技术栈 / 凭证与外部资源（见 RELAY 待拍板项）",
        "EXTRA_OWNER_DECISIONS": "（随项目推进补充）",
        "GLOSSARY_ROWS": "（随文档产出补充）",
    }

    print(f"\nai-collab {mech} · 初始化项目「{name}」")
    print(f"  生成目录: {out_dir}")
    if not args.y:
        ans = input("  确认继续? [Y/n] ").strip().lower()
        if ans not in ("", "y", "yes"):
            print("已取消"); sys.exit(0)

    os.makedirs(out_dir, exist_ok=True)

    # 1. 模板五件套 + 导航 + 会话接棒
    for tpl in TPL_FILES:
        src = os.path.join(TPL_DIR, tpl)
        with open(src, encoding="utf-8") as f:
            content = substitute(f.read(), ctx)
        dst_name = tpl[:-4]  # 去掉 .tpl
        with open(os.path.join(out_dir, dst_name), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ {dst_name}")

    # 2. docs/ 目录骨架
    for d in DOC_DIRS:
        os.makedirs(os.path.join(out_dir, "docs", d), exist_ok=True)
        open(os.path.join(out_dir, "docs", d, ".gitkeep"), "w").close()
    print("  ✓ docs/01-需求规划 … 06-上线复盘 目录骨架")

    # 3. 项目 README 入口
    readme = f"""# {name}

> 由 ai-collab {mech} 生成（{ctx['START_DATE']}）。这是一个 **AI 多角色协作项目**：沟通介质是文件，没有 IM、没有会议。

{ctx['PROJECT_DESC']}

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
"""
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)
    print("  ✓ README.md")

    print(f"\n✅ 初始化完成：{out_dir}")
    print("下一步：")
    print("  1. 编辑 CONTEXT.md 补充定位/硬前提（或直接让 O 主控按模板推进）")
    print("  2. 新会话粘贴 SESSION_BOOT.md 接棒提示词，开始派发任务")
    print("  3. 跑 scripts/check.py 验证机制文件一致性；可选：git init + scripts/git_sync.sh 启动同步守护")


if __name__ == "__main__":
    main()
