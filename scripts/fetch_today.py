#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方案 A 全自动: 拉取 4 领域近 2 周新作, 生成 candidates.json
每日 7:50 由沙箱 cron 调用。
"""
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CANDIDATES_FILE = DATA / "candidates_today.json"
CANDIDATES_FILE_FIRST = DATA / "candidates.json"  # 首期锁定用, 不被 fetch_today 覆盖

# 每个领域 1 个最权威期刊 (简化：避免 retry 错误)
JOURNALS = {
    "sociology": ("American Sociological Review", "S157620343"),
    "anthropology": ("Cultural Anthropology", "S22506700"),
    "history": ("Late Imperial China", "S144953016"),
    "political_science": ("American Political Science Review", "S176007004"),
}

# 兜底期刊 (当主期刊 0 命中时用)
FALLBACK = {
    "sociology": ("American Journal of Sociology", "S122471516"),
    "anthropology": ("American Ethnologist", "S114801684"),
    "history": ("Journal of Modern History", "S125270255"),
    "political_science": ("Comparative Political Studies", "S105556297"),
}

# 人类学额外备选 (CA 是季刊, AE 双月刊, 都少)
ANTHRO_EXTRA = [
    ("Journal of the Royal Anthropological Institute", "S65256140"),
    ("American Anthropologist", "S102499938"),
    ("Ethnography", "S158932249"),
]

# 默认封面 (4 张主题图, 轮换)
DEFAULT_COVERS = [
    "/assets/images/sociology_cover.jpg",
    "/assets/images/anthropology_cover.jpg",
    "/assets/images/history_cover.jpg",
    "/assets/images/polsci_cover.jpg",
]


def fetch_papers(source_id, win_start, win_end, per_page=4):
    """拉某期刊近 2 周论文"""
    url = (
        f"https://api.openalex.org/works"
        f"?filter=primary_location.source.id:{source_id},"
        f"from_publication_date:{win_start},to_publication_date:{win_end}"
        f"&sort=publication_date:desc&per-page={per_page}"
    )
    req = urllib.request.Request(url, headers={
        "User-Agent": "ScholarDaily/1.0 (mailto:dailybook@example.com)"
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        return data.get("results", [])
    except Exception as e:
        print(f"    ERR fetching {source_id}: {e}")
        return []


def paper_to_card(p, discipline, disc_idx):
    """OpenAlex paper → 候选卡 (LLM 后续会填充精读等)"""
    if not p:
        return None
    # 过滤掉没有标题的 (罕见, 但 4 周兜底可能拿到)
    title = p.get("title") or ""
    if not title.strip():
        return None

    # authors
    auths = []
    affs = []
    import re as _re
    for a in p.get("authorships", [])[:3]:
        # display_name 可能含元数据噪音 (如 "James; id_orcid 0000-0002-...")
        # 用正则清洗: 截断到第一个 ";" 或 "(id" 等元数据 marker
        raw_name = a.get("author", {}).get("display_name", "?") or "?"
        name = _re.split(r';\s*(id_orcid|orcid|id\s*=|/orcid)', raw_name, maxsplit=1)[0].strip()
        if not name or name == "?":
            name = "Anonymous"
        auths.append(name)
        for inst in a.get("institutions", [])[:1]:
            inst_name = (inst.get("display_name", "") or "").strip()
            if inst_name:
                affs.append(inst_name)

    # abstract (rebuild from inverted index)
    abs_ii = p.get("abstract_inverted_index")
    abstract = ""
    if abs_ii:
        words = {}
        for word, positions in abs_ii.items():
            for pos in positions:
                words[pos] = word
        abstract = " ".join(words[k] for k in sorted(words.keys()))

    # volume/issue
    biblio = p.get("biblio", {}) or {}
    vol = biblio.get("volume") or ""
    iss = biblio.get("issue") or ""
    vol_iss = (f"Vol. {vol}, No. {iss}" if vol and iss else
               f"Vol. {vol}" if vol else
               f"No. {iss}" if iss else "")

    journal = p.get("primary_location", {}).get("source", {}).get("display_name", "?")
    date = p.get("publication_date", "")

    doi = p.get("doi") or ""
    doi_url = f"https://doi.org/{doi.replace('https://doi.org/', '')}" if doi else ""

    return {
        "title_en": title,
        "title_zh": title[:80],
        "title_zh_full": title[:80],
        "cover_url": DEFAULT_COVERS[disc_idx],
        "illustrations": [],
        "core_concepts": [],
        "author": {
            "name": auths[0] if auths else "?",
            "affiliation": affs[0] if affs else "未知",
            "bio": "",
            "more": ""
        },
        "co_authors": [
            {"name": a, "affiliation": "", "bio": "", "more": ""}
            for a in auths[1:]
        ] if len(auths) > 1 else [],
        "meta": {
            "作者": ", ".join(auths) or "?",
            "期刊": journal,
            "卷期": vol_iss,
            "出版日期": date,
            "DOI": doi,
            "URL": doi_url,
            "类型": "原创研究论文" if p.get("type") == "article" else (p.get("type") or "")
        },
        "intro": (abstract[:1500] if abstract else "（无摘要）"),
        "positioning": f"{date} 发表于 {journal} 的新作",
        "reading_detail": [
            {"marker": "摘要", "text": (abstract[:2000] if abstract else "（无摘要）")}
        ],
        "dialogue": [],
        "reviews": [],
        "score": 0,
        "score_breakdown": {},
        "score_reason": "（待 LLM 评分）",
        "has_fulltext": False,
        "openalex_id": (p.get("id", "") or "").split("/")[-1],
        "_raw_abstract": abstract,
        "_needs_llm_enhance": True
    }


def load_seen_ids() -> set:
    """从 history.jsonl 读所有已发表的 OpenAlex ID"""
    hist_file = DATA / "history.jsonl"
    seen = set()
    if hist_file.exists():
        for line in hist_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                # 新格式: openalex_ids 列表
                for oid in obj.get("openalex_ids", []):
                    if oid:
                        seen.add(oid)
                # 旧格式: 单 openalex_id
                oid = obj.get("openalex_id")
                if oid:
                    seen.add(oid)
            except Exception:
                continue
    return seen


def save_seen_ids(seen: set) -> None:
    """追加本次选的 ID 到 history.jsonl (同日期覆盖, 不是真正存"所有 seen", 而是 daily record)"""
    # 这次不存 seen, 直接由 caller 写 history
    pass


def main():
    end = datetime.now()
    start = end - timedelta(days=14)
    win_start = start.strftime("%Y-%m-%d")
    win_end = end.strftime("%Y-%m-%d")
    print(f"Window: {win_start} ~ {win_end}")

    seen = load_seen_ids()
    print(f"已发表过 {len(seen)} 篇, 将跳过")

    data = {}
    disciplines = list(JOURNALS.keys())

    for i, disc in enumerate(disciplines):
        jname, sid = JOURNALS[disc]
        print(f"\n=== {disc} ({jname}) ===")
        papers = fetch_papers(sid, win_start, win_end)
        papers = [p for p in papers if (p.get("id", "") or "").split("/")[-1] not in seen]
        print(f"  过滤后剩余 {len(papers)} 篇")

        # 人类学额外尝试其他期刊
        if disc == "anthropology" and not papers:
            print(f"  人类学额外备选期刊...")
            for exname, exid in ANTHRO_EXTRA:
                extra = fetch_papers(exid, win_start, win_end)
                extra = [p for p in extra if (p.get("id", "") or "").split("/")[-1] not in seen]
                if extra:
                    print(f"    {exname}: 命中 {len(extra)} 篇")
                    papers = extra
                    break

        if not papers:
            # 兜底
            fbname, fbsid = FALLBACK[disc]
            print(f"  过滤后 0, 兜底: {fbname}")
            papers = fetch_papers(fbsid, win_start, win_end)
            papers = [p for p in papers if (p.get("id", "") or "").split("/")[-1] not in seen]
            if not papers:
                # 二次兜底: 扩窗口到 4 周
                win_start_4w = (end - timedelta(days=28)).strftime("%Y-%m-%d")
                print(f"  兜底过滤后 0, 二次兜底: 4 周窗口")
                papers = fetch_papers(sid, win_start_4w, win_end)
                papers = [p for p in papers if (p.get("id", "") or "").split("/")[-1] not in seen]
                if not papers:
                    papers = fetch_papers(FALLBACK[disc][1], win_start_4w, win_end)
                    papers = [p for p in papers if (p.get("id", "") or "").split("/")[-1] not in seen]
                # 人类学再尝试
                if disc == "anthropology" and not papers:
                    for exname, exid in ANTHRO_EXTRA:
                        papers = fetch_papers(exid, win_start_4w, win_end)
                        papers = [p for p in papers if (p.get("id", "") or "").split("/")[-1] not in seen]
                        if papers:
                            print(f"    4 周窗口 {exname}: 命中")
                            break

        if papers:
            card = paper_to_card(papers[0], disc, i)
            if card:
                card["fallback"] = "4 周窗口" in str(papers) or False
                # 检查是否真走了兜底
                # 简化: 不在这里打标, 留给 main 外部判断
                data[disc] = [card]
                print(f"  → picked: {card['title_en'][:60]}")
        else:
            data[disc] = []
            print(f"  → no candidate")

    # 写
    CANDIDATES_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    total = sum(len(v) for v in data.values())
    print(f"\n✓ {CANDIDATES_FILE} written, {total} cards")
    return total


if __name__ == "__main__":
    sys.exit(0 if main() > 0 else 1)
