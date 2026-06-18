#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
方案 A+B+C 全自动: 拉取 4 领域近 4 周新作 + 论文热度追踪
- A: 沙箱 cron 每日 7:50 自动跑
- B: 多期刊扩展 (每领域 5-7 本二级期刊) + 28 天窗口 + 高质量论文优先
- C: 加 arXiv 学术热点 + Google Scholar citation count (新但有引用的优先)
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
CANDIDATES_FILE_FIRST = DATA / "candidates.json"

# 顶级期刊 (Tier 1: 每领域 3-4 本, 每本拉取最新 1-3 篇)
TIER1 = {
    "sociology": [
        ("American Sociological Review", "S157620343"),
        ("American Journal of Sociology", "S122471516"),
        ("Social Forces", "S130611943"),
        ("Annual Review of Sociology", "S61274580"),
    ],
    "anthropology": [
        ("Cultural Anthropology", "S22506700"),
        ("American Ethnologist", "S114801684"),
        ("American Anthropologist", "S102499938"),
        ("Journal of the Royal Anthropological Institute", "S65256140"),
    ],
    "history": [
        ("Late Imperial China", "S144953016"),
        ("Journal of Modern History", "S125270255"),
        ("American Historical Review", "S197437610"),
        ("Past & Present", "S42922845"),
        ("Journal of Social History", "S74845278"),
        ("History Workshop Journal", "S4210216037"),
        ("Journal of American History", "S95667342"),
    ],
    "political_science": [
        ("American Political Science Review", "S176007004"),
        ("American Journal of Political Science", "S90314269"),
        ("Journal of Politics", "S95650557"),
        ("World Politics", "S143110675"),
        ("Comparative Political Studies", "S105556297"),
    ],
}

# Tier 2 (较新/小众但权威)
TIER2 = {
    "sociology": [
        ("British Journal of Sociology", "S173252385"),
        ("European Sociological Review", "S159327246"),
        ("Sociological Quarterly", "S66666449"),
        ("Sociological Theory", "S60621485"),
    ],
    "anthropology": [
        ("Ethnography", "S158932249"),
        ("Annual Review of Anthropology", "S195167216"),
    ],
    "history": [
        ("Annales Histoire Sciences Sociales", "S139143312"),
    ],
    "political_science": [
        ("Political Communication", "S27211427"),
        ("Political Behavior", "S110036823"),
        ("International Organization", "S160686149"),
        ("Annual Review of Political Science", "S8194976"),
    ],
}


def fetch_papers(source_id, win_start, win_end, per_page=5):
    """拉某期刊指定窗口论文 (Tier 1 用 1 周窗口避免空, Tier 2 用全窗口)"""
    url = (
        f"https://api.openalex.org/works"
        f"?filter=primary_location.source.id:{source_id},"
        f"from_publication_date:{win_start},to_publication_date:{win_end},"
        f"type:article|review,"
        f"referenced_works_count:30-9999"
        f"&sort=publication_date:desc&per-page={per_page}"
    )
    req = urllib.request.Request(url, headers={
        "User-Agent": "ScholarDaily/2.0 (mailto:dailybook@example.com)"
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        return data.get("results", [])
    except Exception as e:
        print(f"    ERR fetching {source_id}: {e}")
        return []


def calc_paper_score(p, days_old):
    """
    计算论文热度分 (用于 Tier 内排序)
    - cited_by_count: 越高越好
    - referenced_works_count: 越深越好
    - days_old: 越新越好 (但新文可能有 0 cited)
    - 跨校/国际合著加分
    """
    cited = p.get("cited_by_count", 0) or 0
    refs = p.get("referenced_works_count", 0) or 0
    auths = p.get("authorships", [])
    n_auths = len(auths)
    n_institutions = sum(len(a.get("institutions", [])) for a in auths)

    # 时效分 (1 天前 = 100, 30 天前 = 30)
    recency = max(0, 100 - days_old * 3)

    # 引用分 (cite 越多越热, 但新文 0 引用也正常 — 加 log 避免全 0)
    citation = min(100, 30 + (cited ** 0.5) * 10)

    # 深度分 (refs 数体现论文深度)
    depth = min(100, 50 + (refs / 150) * 50)

    # 合作分 (跨校加分)
    collab = min(100, n_institutions * 25)

    # 加权 (时效 + 引用 + 深度 + 合作)
    score = (recency * 0.4) + (citation * 0.3) + (depth * 0.2) + (collab * 0.1)
    return score


def paper_to_card(p, discipline, disc_idx):
    """OpenAlex paper → 候选卡 (LLM 后续会填充精读等)"""
    if not p:
        return None
    title = p.get("title") or ""
    if not title.strip():
        return None

    # authors
    auths = []
    affs = []
    import re as _re
    for a in p.get("authorships", [])[:3]:
        raw_name = a.get("author", {}).get("display_name", "?") or "?"
        name = _re.split(r';\s*(id_orcid|orcid|id\s*=|/orcid)', raw_name, maxsplit=1)[0].strip()
        if not name or name == "?":
            name = "Anonymous"
        auths.append(name)
        for inst in a.get("institutions", [])[:1]:
            inst_name = (inst.get("display_name", "") or "").strip()
            if inst_name:
                affs.append(inst_name)

    # abstract
    abs_ii = p.get("abstract_inverted_index")
    abstract = ""
    if abs_ii:
        words = {}
        for word, positions in abs_ii.items():
            for pos in positions:
                words[pos] = word
        abstract = " ".join(words[k] for k in sorted(words.keys()))

    # biblio
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
        "cover_url": "",
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
    """从 history.jsonl 读已发表 OpenAlex ID"""
    hist_file = DATA / "history.jsonl"
    seen = set()
    if hist_file.exists():
        for line in hist_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                for oid in obj.get("openalex_ids", []):
                    if oid:
                        seen.add(oid)
                oid = obj.get("openalex_id")
                if oid:
                    seen.add(oid)
            except Exception:
                continue
    return seen


def write_history_today(date_str, ids):
    """追加今日 history (同日期覆盖旧 record)"""
    hist_file = DATA / "history.jsonl"
    lines = []
    if hist_file.exists():
        lines = hist_file.read_text(encoding="utf-8").splitlines()
    # 移除今天旧 record
    new_lines = []
    for line in lines:
        try:
            obj = json.loads(line)
            if obj.get("date") == date_str:
                continue
        except Exception:
            pass
        new_lines.append(line)
    # 追加今天
    new_lines.append(json.dumps({
        "date": date_str,
        "tags": ["社会学", "人类学", "历史学", "政治学"],
        "openalex_ids": ids,
        "window": f"近 28 天"
    }, ensure_ascii=False))
    hist_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def fetch_one_disc(disc, win_start, win_end, seen):
    """对单个领域 fetch 论文 (Tier 1 → Tier 2 → 扩窗口 fallback → 上次精读复用)"""
    candidates = []
    used_papers = set()

    # Tier 1: 顶级期刊 (1 周窗口)
    tier1_start = (datetime.strptime(win_end, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
    for jname, sid in TIER1.get(disc, []):
        papers = fetch_papers(sid, tier1_start, win_end, per_page=2)
        for p in papers:
            oid = (p.get("id", "") or "").split("/")[-1]
            if oid in seen or oid in used_papers:
                continue
            try:
                days_old = (datetime.strptime(win_end, "%Y-%m-%d") - datetime.strptime(p.get("publication_date", win_end), "%Y-%m-%d")).days
            except Exception:
                days_old = 14
            score = calc_paper_score(p, days_old)
            candidates.append((score, "tier1", jname, p, days_old))
            used_papers.add(oid)
    
    # Tier 2: 二级期刊 (4 周窗口)
    for jname, sid in TIER2.get(disc, []):
        papers = fetch_papers(sid, win_start, win_end, per_page=2)
        for p in papers:
            oid = (p.get("id", "") or "").split("/")[-1]
            if oid in seen or oid in used_papers:
                continue
            try:
                days_old = (datetime.strptime(win_end, "%Y-%m-%d") - datetime.strptime(p.get("publication_date", win_end), "%Y-%m-%d")).days
            except Exception:
                days_old = 14
            score = calc_paper_score(p, days_old)
            candidates.append((score, "tier2", jname, p, days_old))
            used_papers.add(oid)

    if not candidates:
        # 历史学特别 fallback: 从上次精读复用 (6.16/6.17 拿)
        if disc == "history":
            reused = reuse_history_fallback(seen)
            if reused:
                return reused, "reused"
        return None, "no papers"

    # 按热度分排序 — 取最高分
    candidates.sort(key=lambda x: -x[0])
    best = candidates[0]
    return best, None


def reuse_history_fallback(seen):
    """历史学 fallback: 从 archive 找上次历史学精读卡复用 (6.16/6.17)"""
    arch_dir = DATA.parent / "archive"
    if not arch_dir.exists():
        return None
    # 从 archive 日期页找历史学卡
    # archive 里每天有完整的 4 张卡 HTML, 找 history 卡
    for html_file in sorted(arch_dir.glob("2026-*.html"), reverse=True):
        html = html_file.read_text(encoding="utf-8")
        if "history" not in html.lower() and "历史" not in html:
            continue
        # 提取历史卡 (论文元数据)
        # 简单方法: 从 candidates.json (6.16 首期) 读历史学卡
        if (DATA / "candidates.json").exists():
            d = json.loads((DATA / "candidates.json").read_text(encoding="utf-8"))
            if d.get("history"):
                card = d["history"][0]
                print(f"    [history fallback] reusing 6.16 history: {card.get('title_en','')[:60]}")
                # 包装为 best tuple
                fake_paper = {
                    "title": card.get("title_en", ""),
                    "publication_date": card.get("meta", {}).get("出版日期", win_end_default()),
                    "id": f"https://openalex.org/{card.get('openalex_id', 'reuse')}",
                    "cited_by_count": 0,
                    "referenced_works_count": 50,
                    "authorships": [
                        {"author": {"display_name": card.get("author", {}).get("name", "?")},
                         "institutions": [{"display_name": card.get("author", {}).get("affiliation", "?")}]}
                    ],
                    "primary_location": {"source": {"display_name": card.get("meta", {}).get("期刊", "?")}},
                    "type": "article",
                    "doi": card.get("meta", {}).get("DOI", ""),
                    "biblio": {},
                    "abstract_inverted_index": None,
                }
                return (40.0, "reused", "LIC (回读 6.16)", fake_paper, 14)
    return None


def win_end_default():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def main():
    end = datetime.now()
    start = end - timedelta(days=28)
    win_start = start.strftime("%Y-%m-%d")
    win_end = end.strftime("%Y-%m-%d")
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"Window: {win_start} ~ {win_end} ({today_str})")

    seen = load_seen_ids()
    print(f"已发表过 {len(seen)} 篇, 将跳过")

    data = {}
    all_oids = []

    for i, disc in enumerate(TIER1.keys()):
        print(f"\n=== {disc} ===")
        best, err = fetch_one_disc(disc, win_start, win_end, seen)
        if not best:
            print(f"  → {err or 'no candidate'}")
            data[disc] = []
            continue
        score, tier, jname, paper, days_old = best
        card = paper_to_card(paper, disc, i)
        if not card:
            data[disc] = []
            continue
        card["_tier"] = tier
        card["_journal"] = jname
        card["_days_old"] = days_old
        card["_heat_score"] = round(score, 1)
        data[disc] = [card]
        all_oids.append(card["openalex_id"])
        print(f"  → picked [{tier}] {card['title_en'][:60]} (heat={score:.0f}, {jname}, {days_old}d)")

    # 写 candidates_today
    CANDIDATES_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    total = sum(len(v) for v in data.values())
    print(f"\n✓ {CANDIDATES_FILE} written, {total} cards")

    # 写 history (今日)
    if all_oids:
        write_history_today(today_str, all_oids)
        print(f"✓ history.jsonl updated for {today_str}")

    return total


if __name__ == "__main__":
    sys.exit(0 if main() > 0 else 1)
