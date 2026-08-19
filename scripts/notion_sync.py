#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notion_sync.py —— AI 协作项目文档 → Notion 同步（通用版，幂等）

把本地约定文件与 docs/ 下的 .md 文件同步到 Notion 数据库：
  - 每个本地 .md 对应数据库中的一条 page（按「名称」属性匹配）
  - 内容变更才更新（用「内容哈希」属性记录，未变更跳过）
  - 本地删除的文件，可选清理对应 Notion page

配置（环境变量或 ~/.ai-collab/secrets.env）:
  NOTION_TOKEN            Notion Integration token（必填）
  NOTION_DATABASE_ID      Notion 数据库 id（必填，32 位 hex）
  SYNC_DIR                 要同步的本地目录（默认: 当前目录）
  SYNC_PATTERN             文件名匹配（默认: *.md，逗号分隔可多个）
  NOTION_CLEANUP           是否删除本地已不存在的 page（默认 false）

用法:
  python3 scripts/notion_sync.py [--dir .] [--pattern "*.md"] [--cleanup] [--once]

需要 pip 包: requests
  pip3 install requests
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time

try:
    import requests
except ImportError:
    print("缺少 requests 库，请先: pip3 install requests")
    sys.exit(1)

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"

NAME_PROP = "名称"
HASH_PROP = "内容哈希"
TYPE_PROP = "类型"


def load_secrets():
    """从环境变量或 secrets 文件读取凭证。"""
    secrets = {}
    for p in (os.path.expanduser("~/.ai-collab/secrets.env"),
              os.path.join(os.getcwd(), ".secrets.env")):
        if os.path.exists(p):
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    secrets[k.strip()] = v.strip()
    return secrets


def headers(token):
    return {"Authorization": f"Bearer {token}", "Notion-Version": VERSION,
            "Content-Type": "application/json"}


def api(method, path, token, body=None):
    url = API + path
    r = requests.request(method, url, headers=headers(token), json=body, timeout=30)
    if r.status_code >= 400:
        print(f"  !! API {method} {path} -> {r.status_code}: {r.text[:200]}")
        return None
    return r.json()


def md_to_blocks(text):
    """把 markdown 文本转成 Notion blocks（支持标题/列表/表格/代码/引用/段落）。"""
    blocks = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i]); i += 1
            i += 1
            blocks.append({"object": "block", "type": "code", "code": {
                "rich_text": [{"type": "text", "text": {"content": "\n".join(code_lines)[:1900]}}],
                "language": "plain text"}})
            continue
        if stripped.startswith("#"):
            m = re.match(r"^(#{1,3})\s+(.*)$", stripped)
            if m:
                lvl = min(len(m.group(1)), 3)
                blocks.append({"object": "block", "type": f"heading_{lvl}", f"heading_{lvl}": {
                    "rich_text": [{"type": "text", "text": {"content": m.group(2)[:1900]}}]}})
                i += 1
                continue
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i]); i += 1
            rows = []
            for tl in table_lines:
                cells = [c.strip() for c in tl.strip().strip("|").split("|")]
                if all(set(c) <= set("-: ") for c in cells):  # 分隔行
                    continue
                rows.append([{"type": "text", "text": {"content": c[:1900]}} for c in cells])
            if rows:
                ncols = max(len(r) for r in rows)
                blocks.append({"object": "block", "type": "table", "table": {
                    "table_width": ncols, "has_column_header": True, "has_row_header": False,
                    "children": [{"object": "block", "type": "table_row",
                                  "table_row": {"cells": r + [{"type": "text", "text": {"content": ""}}] * (ncols - len(r))}}
                                 for r in rows]}})
            continue
        if stripped.startswith("- "):
            blocks.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": stripped[2:][:1900]}}]}})
            i += 1
            continue
        if stripped.startswith("> "):
            blocks.append({"object": "block", "type": "quote", "quote": {
                "rich_text": [{"type": "text", "text": {"content": stripped[2:][:1900]}}]}})
            i += 1
            continue
        blocks.append({"object": "block", "type": "paragraph", "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": stripped[:1900]}}]}})
        i += 1
    return blocks[:100]  # Notion 单次创建上限


def content_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def find_pages(token, db_id, limit=100):
    pages = []
    cursor = None
    while True:
        body = {"page_size": limit}
        if cursor:
            body["start_cursor"] = cursor
        r = api("POST", f"/databases/{db_id}/query", token, body)
        if not r:
            break
        pages += r.get("results", [])
        if not r.get("has_more"):
            break
        cursor = r.get("next_cursor")
    return pages


def page_name(page):
    props = page.get("properties", {})
    title = props.get(NAME_PROP, {}).get("title", [])
    return "".join(t.get("plain_text", "") for t in title) if title else ""


def page_hash(page):
    props = page.get("properties", {})
    rt = props.get(HASH_PROP, {}).get("rich_text", [])
    return rt[0].get("plain_text", "") if rt else ""


def upsert_page(token, db_id, name, text, type_label):
    pages = find_pages(token, db_id)
    existing = [p for p in pages if page_name(p) == name]
    h = content_hash(text)
    blocks = md_to_blocks(text)
    if not blocks:
        blocks = [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": []}}]
    if existing:
        page = existing[0]
        if page_hash(page) == h:
            return "skip"
        api("DELETE", f"/blocks/{page['id']}/children", token)  # 清空子块
        # 删除子块用批量删除接口
        api("PATCH", f"/blocks/{page['id']}", token, {"properties": {}})
        r = api("PATCH", f"/blocks/{page['id']}", token, {"children": blocks})
        if r:
            api("PATCH", f"/blocks/{page['id']}", token, {"properties": {
                HASH_PROP: {"rich_text": [{"type": "text", "text": {"content": h}}]},
                TYPE_PROP: {"select": {"name": type_label}}}})
        return "update"
    body = {
        "parent": {"database_id": db_id},
        "properties": {
            NAME_PROP: {"title": [{"type": "text", "text": {"content": name}}]},
            HASH_PROP: {"rich_text": [{"type": "text", "text": {"content": h}}]},
            TYPE_PROP: {"select": {"name": type_label}},
        },
        "children": blocks,
    }
    r = api("POST", "/pages", token, body)
    return "create" if r else "fail"


def main():
    ap = argparse.ArgumentParser(description="ai-collab Notion 文档同步")
    ap.add_argument("--dir", default=os.getcwd(), help="本地要同步的目录")
    ap.add_argument("--pattern", default="*.md", help="文件名匹配（逗号分隔）")
    ap.add_argument("--cleanup", action="store_true", help="删除本地已不存在的 page")
    ap.add_argument("--once", action="store_true", help="只跑一次（默认守护循环 60s）")
    ap.add_argument("--interval", type=int, default=60)
    args = ap.parse_args()

    secrets = load_secrets()
    token = os.environ.get("NOTION_TOKEN") or secrets.get("NOTION_TOKEN", "")
    db_id = os.environ.get("NOTION_DATABASE_ID") or secrets.get("NOTION_DATABASE_ID", "").strip().replace("-", "")
    if not token or not db_id:
        print("缺少 NOTION_TOKEN 或 NOTION_DATABASE_ID（环境变量或 ~/.ai-collab/secrets.env）")
        sys.exit(1)

    patterns = [p.strip() for p in args.pattern.split(",") if p.strip()]

    def sync_once():
        files = []
        for root, _, names in os.walk(args.dir):
            if ".git" in root or "node_modules" in root:
                continue
            for n in names:
                if any(__import__("fnmatch").fnmatch(n, p) for p in patterns):
                    files.append(os.path.join(root, n))
        files.sort()
        print(f"[notion_sync] {len(files)} 个文件待检查")
        created = updated = skipped = 0
        for fp in files:
            rel = os.path.relpath(fp, args.dir)
            with open(fp, encoding="utf-8") as f:
                text = f.read()
            res = upsert_page(token, db_id, rel, text, "md")
            if res == "create":
                created += 1; print(f"  + {rel}")
            elif res == "update":
                updated += 1; print(f"  ~ {rel}")
            else:
                skipped += 1
            time.sleep(0.3)
        if args.cleanup:
            local = {os.path.relpath(f, args.dir) for f in files}
            for p in find_pages(token, db_id):
                if page_name(p) not in local:
                    api("PATCH", f"/pages/{p['id']}", token, {"archived": True})
                    print(f"  - 归档 Notion page: {page_name(p)}")
        print(f"[notion_sync] 完成: 新建 {created} / 更新 {updated} / 跳过 {skipped}")

    sync_once()
    if not args.once:
        print(f"[notion_sync] 守护模式，每 {args.interval}s 轮询 (Ctrl+C 退出)")
        while True:
            time.sleep(args.interval)
            try:
                sync_once()
            except Exception as e:
                print(f"[notion_sync] 轮询异常: {e}")


if __name__ == "__main__":
    main()
