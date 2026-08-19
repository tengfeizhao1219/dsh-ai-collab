#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check.py —— ai-collab 约定文件一致性审计（机制的"体检仪"）

用法:
    python3 scripts/check.py [项目目录]     # 默认当前目录

检查项:
  [1] 约定文件完整性：五件套 + LEARNINGS + ADR + NAVIGATION + SESSION_BOOT 是否存在
  [2] 占位符残留：{{...}} 是否还有未替换的模板变量
  [3] TASK_BOARD 状态机合法性：任务状态是否只在允许集合内
  [4] RELAY 与 TASK_BOARD 阶段一致性：看板阶段是否都在流水线中出现
  [5] COMMLOG 格式：是否含日期、条目是否大致倒序（警告级）
  [6] docs/ 目录骨架：01-需求规划 … 06-上线复盘
  [7] 关口记录：TASK_BOARD 中 ⏳ 关口是否对应阶段全 ✅（警告级）

退出码: 0 = 通过（可进关口检查）；1 = 有问题（先修复再过关口）。
"""

import os
import re
import sys

REQUIRED_FILES = [
    "CONTEXT.md", "ROLE_CARDS.md", "TASK_BOARD.md", "RELAY.md",
    "COMMLOG.md", "COLLABORATION.md", "NAVIGATION.md",
    "SESSION_BOOT.md", "LEARNINGS.md", "ADR.md", "REVIEW.md",
]
DOC_DIRS = ["01-需求规划", "02-产品设计", "03-技术方案",
            "04-开发实现", "05-测试验收", "06-上线复盘"]
# 可选配置（项目根或目标目录的 .ai-collab.json）：
#   {"required_files": {"COLLABORATION.md": "AI情报官_协作机制.md", ...},  # 标准名 → 项目实际文件名
#    "docs_dirs": ["intel-docs"]}                                           # 自定义 docs 目录（替代标准六目录检查）
def load_config(target):
    for base in (os.getcwd(), target):
        fp = os.path.join(base, ".ai-collab.json")
        if os.path.exists(fp):
            try:
                import json
                return json.load(open(fp, encoding="utf-8"))
            except Exception:
                return {}
    return {}
ALLOWED_STATUSES = {"📋", "🔄", "✅", "🚫", "🔁", "⛔", "⏳"}
PHASE_RE = re.compile(r"Phase\s*(\d+)")
TASK_STATUS_RE = re.compile(r"\|\s*(T\d+\.\d+)\s*\|.*?\|\s*(📋|🔄|✅|🚫|🔁|⛔)\s*\|")
GATE_RE = re.compile(r"\|?\s*(Phase\s*\d+\s*→\s*Phase\s*\d+)\s*\|?\s*(\|?\s*)(✅|🚫|⏳|🔄)")

problems = []   # 阻断项（exit 1）
warnings = []   # 警告（不影响 exit）


def p(path):
    return os.path.join(root, path)


def read(name):
    fp = p(name)
    if not os.path.exists(fp):
        problems.append(f"[1] 缺少约定文件: {name}")
        return ""
    return open(fp, encoding="utf-8").read()


def main(root):
    print(f"== ai-collab check: {os.path.abspath(root)}\n")
    cfg = load_config(root)
    aliases = cfg.get("required_files", {}) or {}
    docs_dirs = cfg.get("docs_dirs") or []

    def resolve(name):
        return aliases.get(name, name)

    # [1] 文件完整性
    present = []
    for name in REQUIRED_FILES:
        if os.path.exists(p(resolve(name))):
            present.append(name)
    if len(present) < len(REQUIRED_FILES):
        print(f"[1] 缺失 {len(REQUIRED_FILES) - len(present)} 个约定文件: "
              f"{set(REQUIRED_FILES) - set(present)}")

    # [2] 占位符残留
    for name in REQUIRED_FILES + ["README.md"]:
        fp = p(resolve(name))
        if not os.path.exists(fp):
            continue
        text = open(fp, encoding="utf-8").read()
        for m in re.finditer(r"\{\{[A-Z_]+\}\}", text):
            problems.append(f"[2] {name}: 未替换占位符 {m.group(0)} (行 {text[:m.start()].count(chr(10))+1})")

    # [3] TASK_BOARD 状态机
    tb = read("TASK_BOARD.md")
    for m in TASK_STATUS_RE.finditer(tb):
        tid, st = m.group(1), m.group(2)
        if st not in ALLOWED_STATUSES:
            problems.append(f"[3] 非法任务状态: {tid} = {st}")

    # [4] RELAY 阶段 vs TASK_BOARD 阶段
    relay = read("RELAY.md")
    relay_phases = set(PHASE_RE.findall(relay))
    tb_phases = set(PHASE_RE.findall(tb))
    if not tb_phases:
        warnings.append("[4] TASK_BOARD.md 未找到 Phase 阶段标记")
    if tb_phases - relay_phases:
        warnings.append(f"[4] TASK_BOARD 有流水线未收录的阶段: {sorted(tb_phases - relay_phases)}")
    if not relay_phases:
        warnings.append("[4] RELAY.md 未找到 Phase 阶段标记")

    # [5] COMMLOG 格式与倒序
    comm = read("COMMLOG.md")
    dates = re.findall(r"\b(20\d{2}-\d{2}-\d{2})\b", comm)
    if not dates:
        warnings.append("[5] COMMLOG 未找到日期条目（应含 YYYY-MM-DD）")
    elif dates != sorted(dates, reverse=True):
        warnings.append("[5] COMMLOG 条目疑似未保持倒序（最新在上）")

    # [5.5] COMMLOG 膨胀预警（归档策略）
    comm_count = len(dates)
    if comm_count > 30:
        warnings.append(f"[5] COMMLOG 已有 {comm_count} 条日期条目，建议归档（>30 条按 COLLABORATION §十二 归档到 docs/06-上线复盘/）")

    # [6] docs 目录骨架（支持自定义 docs_dirs 配置）
    check_dirs = docs_dirs or [os.path.join("docs", d) for d in DOC_DIRS]
    missing_docs = [d for d in check_dirs if not os.path.isdir(p(d))]
    if missing_docs:
        problems.append(f"[6] 缺少文档目录: {missing_docs}")

    # [7.5] 复盘优化行动追踪（REVIEW 中未打勾的行动）
    review = read("REVIEW.md")
    open_actions = re.findall(r"^\s*-\s*\[ \]\s+(.*)$", review, re.M)
    if len(open_actions) >= 5:
        warnings.append(f"[7] REVIEW 未完成优化行动已达 {len(open_actions)} 条，建议尽快复盘消化（复盘不落地 = 没复盘）")

    # [7] 关口检查记录
    if "关口检查记录" in tb:
        gates = [m for m in GATE_RE.finditer(tb)]
        pending = [m.group(1) for m in gates if m.group(3) in ("⏳", "🔄")]
        if pending:
            warnings.append(f"[7] 尚有未完成关口: {pending}（通过关口前须先过 check）")
    else:
        warnings.append("[7] TASK_BOARD 未找到「关口检查记录」表")

    print(f"-- 阻断项: {len(problems)} / 警告: {len(warnings)}")
    for w in warnings:
        print(f"   ⚠ {w}")
    for pr in problems:
        print(f"   ❌ {pr}")

    if problems:
        print("\n结论: ❌ 未通过——先修复阻断项，再进入关口检查/会话交接。")
        return 1
    if warnings:
        print("\n结论: ⚠️ 通过（有警告，建议处理）——可进入关口检查/会话交接。")
        return 0
    print("\n结论: ✅ 全部通过——机制文件一致，可进入关口检查/会话交接。")
    return 0


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    sys.exit(main(root))
