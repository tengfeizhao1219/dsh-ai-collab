#!/bin/bash
# git_sync.sh —— AI 协作项目 Git 同步守护（通用版）
# 每 60s 自动 commit + push，保证「文件即通信」实时落档。
#
# 用法:
#   ./git_sync.sh [仓库目录] [间隔秒]
#   默认: 当前目录, 60s
#
# 建议在项目根目录后台运行:
#   nohup bash scripts/git_sync.sh . 60 >/dev/null 2>&1 &

set -u
REPO_DIR="${1:-$(pwd)}"
INTERVAL="${2:-60}"
COMMIT_MSG="chore(ai-collab): auto sync $(date '+%Y-%m-%d %H:%M:%S')"
LOG_FILE="$REPO_DIR/.git_sync.log"

cd "$REPO_DIR" || { echo "目录不存在: $REPO_DIR"; exit 1; }

# 安全检查：必须是 git 仓库
if [ ! -d .git ]; then
  echo "错误：$REPO_DIR 不是 git 仓库（先执行 git init）"; exit 1
fi

# 安全检查：不提交敏感文件
if [ -f .gitignore ]; then
  grep -q "^\.secrets\.env$" .gitignore || echo ".secrets.env" >> .gitignore
  grep -q "^secrets/" .gitignore || echo "secrets/" >> .gitignore
  grep -q "^\*\.key$" .gitignore || echo "*.key" >> .gitignore
fi

echo "[git_sync] 守护启动: $REPO_DIR 每 ${INTERVAL}s 同步一次 (日志: $LOG_FILE)"
while true; do
  # 拉取（rebase 防分叉）
  git pull --rebase --quiet 2>>"$LOG_FILE" || true

  # 有改动才提交
  if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "$COMMIT_MSG" >>"$LOG_FILE" 2>&1
    git push --quiet 2>>"$LOG_FILE" || echo "[$(date '+%H:%M:%S')] push 失败（网络/凭证），下次重试" >>"$LOG_FILE"
    echo "[$(date '+%H:%M:%S')] 已同步 $(git log -1 --format='%h')" >>"$LOG_FILE"
  fi
  sleep "$INTERVAL"
done
