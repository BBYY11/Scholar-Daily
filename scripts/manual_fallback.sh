#!/bin/bash
# 手动 fallback 脚本 — 如果 7:50 cron 失败, 8:30 用户跑这个
# 用法: bash scripts/manual_fallback.sh
# 这个脚本不调 LLM — 只确保数据 + HTML + push 一致
# 真正的 LLM 翻译精读需要用户在当前会话手动跑

set -e

WORKSPACE="/workspace/daily-book"
cd "$WORKSPACE" || exit 1

echo "=== [$(date '+%H:%M:%S')] 开始 fallback ==="

# 1. 检查 7:50 是否成功
if [ -f data/last_push.json ]; then
    last_push_date=$(python3 -c "
import json
d = json.load(open('data/last_push.json', encoding='utf-8'))
print(d.get('timestamp', '')[:10])
")
    today=$(date +%Y-%m-%d)
    if [ "$last_push_date" = "$today" ]; then
        echo "✅ 7:50 cron 已成功推送今天 ($today)"
        bash scripts/notify.sh "✅ 7:50 cron 已成功, fallback 无需执行"
        exit 0
    fi
fi

# 2. 7:50 失败 — 跑 fetch + generate (无 LLM)
echo "⚠️ 7:50 cron 未成功, 跑 fallback"

# fetch
python3 scripts/fetch_today.py || true

# 通知 fallback 模式
bash scripts/notify.sh "⚠️ Fallback 模式: 跑 fetch_today + generate_today + push — **精读内容可能不达标,需要用户手动补 LLM 翻译**"

# generate (无 LLM 翻译)
python3 scripts/generate_today.py || true

# 推送
git add -A
if git diff --cached --quiet; then
    echo "无变更"
else
    git commit -m "chore: daily auto-generate $(date +%Y-%m-%d) [fallback]"
    git push origin main --force-with-lease 2>&1 | tail -3 || echo "push 失败, 稍后重试"
fi

echo "=== [$(date '+%H:%M:%S')] fallback 完成 ==="
bash scripts/notify.sh "✅ Fallback 推送完成 (无 LLM 精读), commit: $(git rev-parse HEAD 2>/dev/null || echo 'no commit')"
