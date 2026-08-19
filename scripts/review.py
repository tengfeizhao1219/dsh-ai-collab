#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
review.py —— ai-collab 复盘输入分析器（复盘的"数据采集器"）

用法:
    python3 scripts/review.py [项目目录]        # 输出复盘输入报告（stdout）
    python3 scripts/review.py [项目目录] --write  # 把统计写入 REVIEW.md 末尾

从 TASK_BOARD / COMMLOG / LEARNINGS / REVIEW 提取复盘素材：
  [1] 任务状态分布（📋/🔄/✅/🚫/🔁/⛔）
  [2] 阻塞项清单（🚫）与重试项（🔁）
  [3] 最近交接（COMMLOG 最新 5 条日期）
  [4] 教训统计（LEARNINGS 条目数 + 最近 3 条标题）
  [5] 未完成优化行动（REVIEW 中未打勾的 [ ]）
  [6] 模式检测：返工关键词频率 / 同一阶段多次阻塞 / 长期进行中
"""

import json
import os
import re
import sys
from collections import Counter

STATUS_RE = re.compile(r"\|\s*(T\d+\.\d+)\s*\|.*?\|\s*(📋|🔄|✅|🚫|🔁|⛔)\s*\|")
LESSON_RE = re.compile(r"^###\s+\[([^\]]+)\]\s+(.*)$", re.M)
ADDR_RE = re.compile(r"^###\s+(ADR-\d+)\s*·\s*(.*)$", re.M)
TODO_RE = re.compile(r"^\s*-\s*\[\s\]\s+(.*)$", re.M)
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
REDO_WORDS = ["修复", "返工", "重试", "再次", "又", "回退", "重复"]
GATE_RE = re.compile(r"Phase\s*\d+\s*→\s*Phase\s*\d+")

SUPPORTED_STATUSES = {"📋", "🔄", "✅", "🚫", "🔁", "⛔"}


def load_config(root):
    for base in (os.getcwd(), root):
        fp = os.path.join(base, ".ai-collab.json")
        if os.path.exists(fp):
            try:
                return json.load(open(fp, encoding="utf-8"))
            except Exception:
                return {}
    return {}


def resolve(name, aliases):
    return aliases.get(name, name)


def read_file(root, name, aliases):
    fp = os.path.join(root, resolve(name, aliases))
    if not os.path.exists(fp):
        return ""
    return open(fp, encoding="utf-8").read()


def main(root):
    cfg = load_config(root)
    aliases = cfg.get("required_files", {}) or {}
    tb = read_file(root, "TASK_BOARD.md", aliases)
    comm = read_file(root, "COMMLOG.md", aliases)
    learn = read_file(root, "LEARNINGS.md", aliases)
    review = read_file(root, "REVIEW.md", aliases)

    lines = []
    a = lines.append
    a(f"# 复盘输入报告 · {os.path.abspath(root)}")
    a("")
    a(f"> 生成时间：{__import__('datetime').date.today()} | 由 review.py 自动生成，供 O 主控复盘参考")

    # [1] 任务状态分布
    a("\n## 1. 任务状态分布")
    statuses = Counter()
    for m in STATUS_RE.finditer(tb):
        statuses[m.group(2)] += 1
    if statuses:
        for s in ["📋", "🔄", "✅", "🚫", "🔁", "⛔"]:
            a(f"- {s} {statuses.get(s, 0)}")
        total = sum(statuses.values())
        done = statuses.get("✅", 0)
        a(f"- 合计 {total} 项，完成率 {done}/{total}（{done*100//max(total,1)}%）")
    else:
        a("- （未解析到任务条目）")

    # [2] 阻塞与重试
    a("\n## 2. 阻塞 / 重试清单")
    blocked = [m.group(1) for m in STATUS_RE.finditer(tb) if m.group(2) == "🚫"]
    retry = [m.group(1) for m in STATUS_RE.finditer(tb) if m.group(2) == "🔁"]
    a(f"- 阻塞（🚫）: {blocked if blocked else '无'}")
    a(f"- 重试（🔁）: {retry if retry else '无'}")

    # [3] 最近交接
    a("\n## 3. 最近交接（COMMLOG 最新 5 条）")
    dates = DATE_RE.findall(comm)
    a(f"- COMMLOG 共 {len(dates)} 条日期条目，最新 {sorted(set(dates))[-5:] if dates else '无'}")

    # [4] 教训统计
    a("\n## 4. 教训统计（LEARNINGS）")
    lessons = LESSON_RE.findall(learn)
    if lessons:
        a(f"- 共 {len(lessons)} 条，最近：")
        for d, t in lessons[-3:]:
            a(f"  - [{d}] {t[:50]}")
    else:
        a("- 暂无教训条目（修复后请按规则记录）")

    # [5] 未完成优化行动
    a("\n## 5. 复盘优化行动（未完成）")
    todos = TODO_RE.findall(review)
    a(f"- REVIEW 中未打勾行动 {len(todos)} 条：")
    for t in todos[-8:]:
        a(f"  - [ ] {t[:70]}")

    # [6] 模式检测
    a("\n## 6. 模式检测")
    redo_hits = Counter()
    for line in comm.splitlines():
        for w in REDO_WORDS:
            if w in line:
                redo_hits[w] += 1
    if redo_hits:
        a("- 交接记录中返工类关键词：" + ", ".join(f"{w}×{n}" for w, n in redo_hits.most_common(4)))
        if sum(redo_hits.values()) >= 4:
            a("- ⚠ 返工信号较多，建议本次复盘专项审视（触发：模式）")
    phase_blocks = Counter()
    for m in STATUS_RE.finditer(tb):
        # 找任务所在 Phase 段落
        seg = tb[: m.start()]
        pm = list(re.finditer(r"##\s+(Phase\s*\d+)", seg))
        if pm and m.group(2) == "🚫":
            phase_blocks[pm[-1].group(1)] += 1
    if phase_blocks:
        a(f"- 各阶段阻塞分布：{dict(phase_blocks)}")
    gates = GATE_RE.findall(tb)
    a(f"- 关口记录 {len(gates)} 处" + ("（含未完成关口，建议过关口前先复盘）" if gates else ""))

    # 输出
    report = "\n".join(lines) + "\n"
    print(report)

    if "--write" in sys.argv and os.path.exists(os.path.join(root, resolve("REVIEW.md", aliases))):
        with open(os.path.join(root, resolve("REVIEW.md", aliases)), "a", encoding="utf-8") as f:
            f.write(f"\n---\n\n<details><summary>复盘输入快照（{__import__('datetime').date.today()}）</summary>\n\n```\n{report}\n```\n\n</details>\n")
        print(f"[review] 统计已追加到 REVIEW.md")
    return 0


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.getcwd()
    sys.exit(main(root))
