#!/usr/bin/env python3
"""检查 candidates.json 并打印摘要 — 在 Actions workflow 里被调用"""
import json, sys
from pathlib import Path

cand = Path("data/candidates.json")
if not cand.exists():
    print("::warning::data/candidates.json 不存在")
    sys.exit(0)

with cand.open(encoding="utf-8") as f:
    d = json.load(f)
print(f"Fields: {list(d.keys())}")
print(f"Counts: {[(k, len(v)) for k, v in d.items()]}")
