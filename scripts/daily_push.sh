#!/bin/bash
# 方案 A 全自动: 拉取今日 4 论文 + 渲染 + 推送
# 每日 7:50 由沙箱 cron 调用
set -e

WORKSPACE="/workspace/daily-book"
cd "$WORKSPACE" || exit 1

echo "=== [$(date '+%H:%M:%S')] 开始今日推送 ==="

# 1) 拉 OpenAlex 数据
python3 scripts/fetch_today.py

# 2) 渲染 (candidate 还是 LLM 没加工的 abridged 摘要版, 但每天都跑)
python3 scripts/generate_today.py

# 3) 提交 + 推送 (用环境变量里的 token)
git config user.name "daily-book-bot" 2>/dev/null
git config user.email "bot@daily-book.local" 2>/dev/null
git add -A
if git diff --cached --quiet; then
    echo "无变更 (生成器幂等)"
else
    git commit -m "chore: daily auto-generate $(date -u +%Y-%m-%d)"
    # 强制推送 (因为 Actions 也会 push, 会有 race condition)
    git push origin main --force-with-lease 2>&1 | tail -3 || echo "push 失败, 稍后重试"
fi

echo "=== [$(date '+%H:%M:%S')] 推送完成 ==="
