#!/bin/bash
# 任务已停止 — 自动 cron 触发后立即退出
# (用户 6.22 要求停止每日推送)
echo "[daily-book] $(date '+%Y-%m-%d %H:%M:%S') 自动推送已停止 (用户 6.22 取消)" >> /workspace/daily-book/data/last_notification.md
exit 0
