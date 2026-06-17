#!/usr/bin/env python3
"""质量自检 — 跑在 fetch_today + LLM 填字段之后、generate_today 之前
- 检查每张卡的字数、概念数、对话数、章节数、marker 分布
- exit 0 = 通过; exit 1 = 有不达标字段
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CANDIDATES = DATA / "candidates_today.json"

# 阈值
MIN_READING = 1500        # 精读最少字数
MIN_INTRO = 150            # 导读最少字数
MIN_POSITIONING = 60       # 一句话定位最少
MIN_BIO = 30               # author.bio 最少
MIN_CONCEPTS = 3            # 核心概念数
MAX_CONCEPTS = 6
MIN_DIALOGUE = 1            # 对话段数
MIN_CHAPTERS = 4            # 章节数 (chapter_title)
MIN_KEY_MARKER = 2          # 关键段数
MIN_SKIP_MARKER = 1         # 可跳段数
MIN_SCORE_REASON = 50       # 评分理由最少
REQUIRED_FIELDS = [
    "title_zh", "title_zh_full", "positioning", "intro",
    "core_concepts", "reading_detail", "dialogue", "score",
    "score_breakdown", "score_reason", "author", "openalex_id",
]

def check_one(card, key):
    """返回 (passed: bool, issues: list[str])"""
    issues = []
    # 必填字段
    for f in REQUIRED_FIELDS:
        if not card.get(f):
            issues.append(f"  [{key}] 缺字段: {f}")

    # 字数
    intro = card.get("intro", "") or ""
    if len(intro) < MIN_INTRO:
        issues.append(f"  [{key}] intro 字数 {len(intro)} < {MIN_INTRO}")
    pos = card.get("positioning", "") or ""
    if len(pos) < MIN_POSITIONING:
        issues.append(f"  [{key}] positioning 字数 {len(pos)} < {MIN_POSITIONING}")

    # author.bio
    author = card.get("author", {})
    bio = author.get("bio", "") or ""
    if len(bio) < MIN_BIO:
        issues.append(f"  [{key}] author.bio 字数 {len(bio)} < {MIN_BIO}")

    # core_concepts
    concepts = card.get("core_concepts", [])
    n_concepts = len(concepts) if isinstance(concepts, list) else 0
    if n_concepts < MIN_CONCEPTS:
        issues.append(f"  [{key}] 核心概念数 {n_concepts} < {MIN_CONCEPTS}")
    if n_concepts > MAX_CONCEPTS:
        issues.append(f"  [{key}] 核心概念数 {n_concepts} > {MAX_CONCEPTS}")

    # 概念字段格式
    for i, c in enumerate(concepts if isinstance(concepts, list) else []):
        if not c.get("term_zh") or not c.get("definition"):
            issues.append(f"  [{key}] 概念 {i+1} 缺 term_zh 或 definition")

    # reading_detail 字数 + 章节
    rd = card.get("reading_detail", [])
    if not isinstance(rd, list):
        issues.append(f"  [{key}] reading_detail 不是列表")
        return False, issues
    rd_text_total = sum(len(p.get("text", "")) for p in rd if isinstance(p, dict))
    if rd_text_total < MIN_READING:
        issues.append(f"  [{key}] 精读总字数 {rd_text_total} < {MIN_READING}")
    chapter_count = sum(1 for p in rd if isinstance(p, dict) and p.get("type") == "chapter_title")
    if chapter_count < MIN_CHAPTERS:
        issues.append(f"  [{key}] 章节数 {chapter_count} < {MIN_CHAPTERS}")
    key_count = sum(1 for p in rd if isinstance(p, dict) and p.get("marker") == "关键")
    skip_count = sum(1 for p in rd if isinstance(p, dict) and p.get("marker") == "可跳")
    if key_count < MIN_KEY_MARKER:
        issues.append(f"  [{key}] 关键段 {key_count} < {MIN_KEY_MARKER}")
    if skip_count < MIN_SKIP_MARKER:
        issues.append(f"  [{key}] 可跳段 {skip_count} < {MIN_SKIP_MARKER}")

    # dialogue
    dialogue = card.get("dialogue", [])
    n_dial = len(dialogue) if isinstance(dialogue, list) else 0
    if n_dial < MIN_DIALOGUE:
        issues.append(f"  [{key}] 对话段数 {n_dial} < {MIN_DIALOGUE}")

    # score_reason
    reason = card.get("score_reason", "") or ""
    if len(reason) < MIN_SCORE_REASON:
        issues.append(f"  [{key}] score_reason 字数 {len(reason)} < {MIN_SCORE_REASON}")

    return len(issues) == 0, issues


def main():
    if not CANDIDATES.exists():
        print(f"❌ {CANDIDATES} 不存在")
        return 1

    d = json.load(open(CANDIDATES, encoding="utf-8"))
    total_issues = []
    summary = []

    for key, cards in d.items():
        for c in cards:
            passed, issues = check_one(c, key)
            rd = c.get("reading_detail", [])
            rd_text_total = sum(len(p.get("text", "")) for p in rd if isinstance(p, dict))
            chapter_count = sum(1 for p in rd if isinstance(p, dict) and p.get("type") == "chapter_title")
            key_count = sum(1 for p in rd if isinstance(p, dict) and p.get("marker") == "关键")
            skip_count = sum(1 for p in rd if isinstance(p, dict) and p.get("marker") == "可跳")
            status = "✅" if passed else "❌"
            summary.append(f"  {status} [{key}] 精读 {rd_text_total}字 / 章节 {chapter_count} / 关键 {key_count} / 可跳 {skip_count} / 概念 {len(c.get('core_concepts',[]))} / 对话 {len(c.get('dialogue',[]))}")
            if not passed:
                total_issues.extend(issues)

    print("\n".join(summary))
    print()
    if total_issues:
        print(f"❌ {len(total_issues)} 个不达标项:")
        for iss in total_issues:
            print(iss)
        return 1
    print("✅ 全部达标")
    return 0


if __name__ == "__main__":
    sys.exit(main())
