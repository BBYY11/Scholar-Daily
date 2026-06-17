#!/bin/bash
# 通知脚本 — 接收消息写到 data/last_notification.md + last_notification.json
# 未来可接入 server酱/Telegram/Email

WORKSPACE="/workspace/daily-book"
NOTIFY_DIR="$WORKSPACE/data"
LOG_FILE="$NOTIFY_DIR/last_notification.json"
MD_FILE="$NOTIFY_DIR/last_notification.md"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
MESSAGE="$1"

# 写 JSON
python3 -c "
import json, sys
from pathlib import Path
p = Path('$LOG_FILE')
data = {
    'timestamp': '$TIMESTAMP',
    'message': '''$MESSAGE'''
}
p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'✓ 写入 {p}')
"

# 写 Markdown (历史通知日志)
python3 -c "
import sys
from pathlib import Path
from datetime import datetime
p = Path('$MD_FILE')
ts = '$TIMESTAMP'
msg = '''$MESSAGE'''
# 如果文件存在, append; 否则创建
existing = p.read_text(encoding='utf-8') if p.exists() else ''
new_entry = f'## {ts}\n\n{msg}\n\n---\n\n'
p.write_text(new_entry + existing, encoding='utf-8')
print(f'✓ 追加 {p}')
"

# 也可以用 webhook — 当前用 print
echo ""
echo "=== 通知 ==="
echo "$MESSAGE"
echo "============="
