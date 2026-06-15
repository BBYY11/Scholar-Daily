#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日一书 · 今日精读生成器

输入：data/candidates.json（每个领域 2 周窗口内的候选书目/论文）
输出：
  - index.html（首页 4 张卡）
  - archive/YYYY-MM-DD.html（每日归档）
  - archive/index.json（归档索引）
  - downloads/YYYY-MM-DD.zip（打包下载）
  - data/history.jsonl（追加历史）

每日 8:30 由 cron 触发。
"""
from __future__ import annotations
import json
import os
import re
import shutil
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
ARCHIVE = ROOT / "archive"
DOWNLOADS = ROOT / "downloads"
CANDIDATES_FILE = DATA / "candidates.json"
HISTORY_FILE = DATA / "history.jsonl"

DISCIPLINES = [
    ("sociology", "社会学", "Sociology"),
    ("anthropology", "人类学", "Anthropology"),
    ("history", "历史学", "History"),
    ("political_science", "政治学", "Political Science"),
]


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def window_str() -> tuple[str, str]:
    """回看 14 天（2 周）窗口"""
    end = datetime.now() - timedelta(days=1)  # 含昨日
    start = end - timedelta(days=13)  # 14 天总跨度
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def load_candidates() -> dict[str, list[dict[str, Any]]]:
    if not CANDIDATES_FILE.exists():
        return {k: [] for k, _, _ in DISCIPLINES}
    with CANDIDATES_FILE.open(encoding="utf-8") as f:
        data = json.load(f)
    return data


def pick_one(cands: list[dict[str, Any]], discipline: str) -> dict[str, Any] | None:
    """简单策略：取评分最高的一项。若空，返回 None。"""
    if not cands:
        return None
    return sorted(cands, key=lambda x: x.get("score", 0), reverse=True)[0]


def render_card(card: dict[str, Any], disc_en: str, disc_zh: str) -> str:
    """渲染单张精读卡的 HTML"""
    cover = card.get("cover_url")
    cover_html = (
        f'<img src="{cover}" alt="cover" />' if cover
        else '<div class="cover-placeholder">封面占位<br/>（未搜到原书封面）</div>'
    )

    score = card.get("score", 0)
    score_breakdown = card.get("score_breakdown", {})
    sb_html = "".join(
        f'<div><b>{k}</b>：{v}</div>' for k, v in score_breakdown.items()
    )

    illustrations = card.get("illustrations", [])
    illus_html = ""
    if illustrations:
        items = "".join(
            f'''<figure class="illu-item">
              <img src="{illu.get("url", "")}" alt="{illu.get("alt", "")}" />
              <figcaption>{illu.get("caption", "")}</figcaption>
            </figure>'''
            for illu in illustrations
        )
        illus_html = f'<div class="illustrations">{items}</div>'

    # 核心概念释义
    concepts = card.get("core_concepts", [])
    concepts_html = ""
    if concepts:
        items = "".join(
            f'''<div class="concept-item">
              <div class="concept-term">
                {c.get("term_zh", "")}
                <span class="concept-page">第 {c.get("page", "")} 页</span>
                <span class="concept-term-en">{c.get("term_en", "")}</span>
              </div>
              <div class="concept-def">{c.get("definition", "")}</div>
            </div>'''
            for c in concepts
        )
        concepts_html = f'<div class="concepts-list">{items}</div>'
    else:
        concepts_html = '<p style="color:var(--ink-mute);font-size:14px;font-style:italic;">本书无生概念，沿用常识术语即可。</p>'

    # 精读分章节 — 支持 chapter_title / marker / blockquote
    detail_html = ""
    for chunk in card.get("reading_detail", []):
        kind = chunk.get("type", "para")
        if kind == "chapter_title":
            detail_html += f'<p class="chapter-title no-indent">{chunk.get("text", "")}</p>'
        elif kind == "blockquote":
            detail_html += f'<blockquote>{chunk.get("text", "")}</blockquote>'
        else:
            marker = chunk.get("marker", "")
            cls = "skip" if marker == "可跳" else ("note" if marker == "关键脚注" else "")
            marker_html = f'<span class="marker {cls}">{marker}</span>' if marker else ""
            detail_html += f'<p class="no-indent">{marker_html}{chunk.get("text", "")}</p>'

    reviews_html = ""

    dialogue_html = "".join(
        f'<li><b>{d.get("work", "")}</b>（{d.get("year", "")}）'
        f'<span class="dialogue-relation">{d.get("relation", "")}</span>'
        f'：{d.get("note", "")}</li>'
        for d in card.get("dialogue", [])
    )

    meta = card.get("meta", {})
    meta_html = "".join(
        f'<div><span>{k}</span><span>{v}</span></div>' for k, v in meta.items()
    )

    # 作者信息
    author = card.get("author", {})
    author_avatar = author.get("avatar_url", "")
    author_name = author.get("name", card.get("meta", {}).get("作者", "佚名"))
    author_aff = author.get("affiliation", "")
    author_bio_html = ""
    if author_avatar:
        author_avatar_html = f'<img class="author-avatar" src="{author_avatar}" alt="{author_name}" />'
    else:
        initials = "".join([c for c in author_name if '\u4e00' <= c <= '\u9fff'])[:1] or author_name[:1]
        author_avatar_html = f'<div class="author-avatar placeholder">{initials}</div>'
    author_bio_html = f'''
      <div class="author-card">
        <div class="author-head">
          {author_avatar_html}
          <div class="author-info">
            <div class="author-name">{author_name}</div>
            {f'<div class="author-aff">{author_aff}</div>' if author_aff else ''}
          </div>
        </div>
        <div class="author-bio">{author.get("bio", "")}</div>
        {f'<div class="author-meta">{author.get("more", "")}</div>' if author.get("more") else ''}
      </div>
    '''

    # 合著者
    co_authors = card.get("co_authors", [])
    co_authors_html = ""
    if co_authors:
        items = "".join(
            f'''<div class="author-card co-author">
              <div class="author-head">
                <div class="author-avatar placeholder">{ca.get("name", "?")[0]}</div>
                <div class="author-info">
                  <div class="author-name">{ca.get("name", "")}</div>
                  {f'<div class="author-aff">{ca.get("affiliation", "")}</div>' if ca.get("affiliation") else ''}
                </div>
              </div>
              <div class="author-bio">{ca.get("bio", "")}</div>
              {f'<div class="author-meta">{ca.get("more", "")}</div>' if ca.get("more") else ''}
            </div>'''
            for ca in co_authors
        )
        co_authors_html = items

    fallback_badge = (
        '<div class="discipline-tag" style="background:#888;">⚠ 已回退至 4 周窗口</div>'
        if card.get("fallback") else ''
    )

    # 内容深度提示：精读字数 + 是否基于全文
    reading_chars = sum(len(c.get("text", "")) for c in card.get("reading_detail", []))
    has_fulltext = card.get("has_fulltext", False)
    if has_fulltext:
        depth_badge = f'<div class="depth-badge fulltext">✓ 精读基于全文 · {reading_chars} 字</div>'
    else:
        depth_badge = f'<div class="depth-badge abridged">⚡ 精读基于公开摘要（未读全文） · {reading_chars} 字 · 完整 2000 字版待全文获取</div>'

    return f'''<article class="card">
      <div class="card-header">
        <div class="card-cover">{cover_html}</div>
        <div>
          {fallback_badge}
          {depth_badge}
          <div class="discipline-tag">{disc_en.upper()} · {disc_zh}</div>
          <h2>{card.get("title_zh", "")}</h2>
          <p class="card-title-en">{card.get("title_en", "")}</p>
          <p class="card-title-zh">中译：{card.get("title_zh_full", "")}</p>
          <div class="meta">{meta_html}</div>
        </div>
      </div>

      <div class="positioning">📍 {card.get("positioning", "")}</div>

      {author_bio_html}
      {co_authors_html}

      <section class="card-section">
        <h3>导 读</h3>
        <p class="lead">{card.get("intro", "")}</p>
      </section>

      <section class="card-section">
        <h3>核心概念释义</h3>
        {concepts_html}
      </section>

      {f'<section class="card-section"><h3>重要插图 / 图表</h3>{illus_html}</section>' if illus_html else ''}

      <section class="card-section reading-detail">
        <h3>精 读（Seminar）</h3>
        {detail_html}
      </section>

      <section class="card-section">
        <h3>学术对话</h3>
        <ul class="dialogue-list">{dialogue_html}</ul>
      </section>

      <section class="card-section">
        <h3>推荐指数</h3>
        <div class="score-box">
          <div class="score-headline">
            <div class="score-number">{score}</div>
            <div class="score-max">/ 100</div>
          </div>
          <p class="score-reason">{card.get("score_reason", "")}</p>
          <div class="score-breakdown">{sb_html}</div>
        </div>
      </section>

      <p style="margin-top:24px;font-size:12px;color:var(--ink-mute);">
        图表版权归原出版方，本文用于学术评介。原文页码/DOI 见上方元信息。
      </p>
    </article>'''


def render_index(cards_html: list[str], date: str, win_start: str, win_end: str, is_first: bool = False) -> str:
    """重写首页内容区 — 模板内嵌，不读文件，避免自覆盖。"""
    cards_block = "\n".join(cards_html)
    first_badge = '<span class="first-issue-badge">起点 · 首期</span>' if is_first else ''
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>每日一书 · 学术精读</title>
  <link rel="stylesheet" href="assets/style.css" />
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="index.html" class="logo">每日一书 · 学术精读</a>
      <nav>
        <a href="index.html">今日</a>
        <a href="archive.html">归档</a>
        <a href="about.html">关于</a>
      </nav>
    </div>
  </header>

  <main>
    <section class="hero">
      <p class="hero-date" id="today-date">{date}</p>
      {first_badge}
      <h1>今日四份精读</h1>
      <p class="hero-sub">社会学 · 人类学 · 历史学 · 政治学 · 研究生 Seminar 标准</p>
      <p class="hero-window" id="window-info">时间窗口：{win_start} ~ {win_end}</p>
    </section>

    <section class="cards" id="today-cards">
      {cards_block}
    </section>

    <section class="download-bar">
      <p>下载今日全部内容（Markdown + 图片）</p>
      <a class="btn-download" id="download-link" href="downloads/{date}.zip" download>⬇ 下载 ZIP 包</a>
    </section>
  </main>

  <footer>
    <p>每日 8:30 自动更新 · 内容由"每日一书"生成 · 图表版权归原出版方</p>
  </footer>

  <script src="assets/script.js"></script>
</body>
</html>'''


def render_archive_day(cards_html: list[str], date: str, win_start: str, win_end: str) -> str:
    """生成单日归档页（与首页同结构）"""
    body = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{date} 归档 · 每日一书</title>
  <link rel="stylesheet" href="../assets/style.css" />
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a href="../index.html" class="logo">每日一书 · 学术精读</a>
      <nav>
        <a href="../index.html">今日</a>
        <a href="../archive.html">归档</a>
        <a href="../about.html">关于</a>
      </nav>
    </div>
  </header>

  <main>
    <section class="hero">
      <p class="hero-date">{date}</p>
      <h1>{date} · 4 份精读</h1>
      <p class="hero-sub">社会学 · 人类学 · 历史学 · 政治学</p>
      <p class="hero-window">时间窗口：{win_start} ~ {win_end}</p>
    </section>

    <section class="cards">
      {''.join(cards_html)}
    </section>

    <section class="download-bar">
      <p>下载当日全部内容（Markdown + 图片）</p>
      <a class="btn-download" href="../downloads/{date}.zip" download>⬇ 下载 ZIP 包</a>
    </section>
  </main>

  <footer>
    <p>每日 8:30 自动更新 · 内容由"每日一书"生成 · 图表版权归原出版方</p>
  </footer>
</body>
</html>'''
    return body


def update_archive_index(history: list[dict[str, Any]]) -> None:
    """按月份分块，方便前端渲染。"""
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    idx_path = ARCHIVE / "index.json"
    months: dict[str, list[dict[str, Any]]] = {}
    for h in history:
        ym = h["date"][:7]  # YYYY-MM
        months.setdefault(ym, []).append({"date": h["date"], "tags": h.get("tags", [])})
    ordered = sorted(months.items(), key=lambda x: x[0], reverse=True)
    idx_path.write_text(
        json.dumps([{"month": m, "items": items} for m, items in ordered], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_history() -> list[dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    return [json.loads(line) for line in HISTORY_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]


def save_history(history: list[dict[str, Any]]) -> None:
    HISTORY_FILE.write_text(
        "\n".join(json.dumps(h, ensure_ascii=False) for h in history) + "\n",
        encoding="utf-8",
    )


def make_markdown(card: dict[str, Any], disc_zh: str) -> str:
    """把单张卡导出为 Markdown，便于下载阅读"""
    lines = [
        f"# {card.get('title_zh', '')}",
        f"**{disc_zh}** · {card.get('title_en', '')}",
        "",
        f"> 中译：{card.get('title_zh_full', '')}",
        "",
        "## 作者简介",
    ]
    a = card.get("author", {})
    if a:
        lines.append(f"\n**{a.get('name', '')}** · {a.get('affiliation', '')}\n")
        lines.append(a.get("bio", ""))
        if a.get("more"):
            lines.append(f"\n> {a.get('more', '')}")
    lines += ["", "## 元信息"]
    for k, v in card.get("meta", {}).items():
        lines.append(f"- **{k}**：{v}")
    lines += [
        "",
        f"## 一句话定位\n{card.get('positioning', '')}",
        "",
        f"## 导读\n{card.get('intro', '')}",
        "",
        "## 核心概念释义",
    ]
    for c in card.get("core_concepts", []):
        lines.append(
            f"\n**{c.get('term_zh', '')}**（{c.get('term_en', '')}） · 第 {c.get('page', '')} 页\n\n"
            f"{c.get('definition', '')}"
        )
    lines += ["", "## 精读"]
    for chunk in card.get("reading_detail", []):
        marker = f"[{chunk.get('marker', '')}] " if chunk.get("marker") else ""
        lines.append(f"\n{marker}{chunk.get('text', '')}")
    lines += [
        "",
        "## 学术对话",
    ]
    for d in card.get("dialogue", []):
        lines.append(f"- **{d.get('work', '')}**（{d.get('year', '')}）— {d.get('relation', '')}：{d.get('note', '')}")
    lines += ["", "## 优秀评论"]
    for r in card.get("reviews", []):
        lines.append(f"- **{r.get('title', '')}** — {r.get('author', '')} · {r.get('venue', '')}")
        lines.append(f"  {r.get('summary', '')}")
        if r.get("url"):
            lines.append(f"  链接：{r['url']}")
    lines += [
        "",
        f"## 推荐指数：{card.get('score', 0)}/100",
        card.get("score_reason", ""),
    ]
    return "\n".join(lines)


def build_zip(date: str, cards: list[dict[str, Any]], disciplines_zh: list[str]) -> Path:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    zip_path = DOWNLOADS / f"{date}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for card, dzh in zip(cards, disciplines_zh):
            md = make_markdown(card, dzh)
            slug = re.sub(r"[^\w\-]+", "_", card.get("title_en", card.get("title_zh", "card")))[:60]
            zf.writestr(f"{slug}.md", md)
    return zip_path


def main() -> int:
    date = today_str()
    win_start, win_end = window_str()
    candidates = load_candidates()

    cards_html: list[str] = []
    cards_data: list[dict[str, Any]] = []
    disciplines_zh_used: list[str] = []
    tags: list[str] = []

    for key, dzh, den in DISCIPLINES:
        cands = candidates.get(key, [])
        chosen = pick_one(cands, key)
        if not chosen:
            cards_html.append(
                f'<article class="card loading"><p class="loading-text">【{dzh}】今天暂无合格新作（窗口 {win_start} ~ {win_end}）</p></article>'
            )
            tags.append(f"{dzh}（无）")
            continue
        cards_html.append(render_card(chosen, den, dzh))
        cards_data.append(chosen)
        disciplines_zh_used.append(dzh)
        tags.append(dzh)

    # 写首页
    is_first = len(load_history()) == 0  # 历史为空 → 起点
    index_html = render_index(cards_html, date, win_start, win_end, is_first=is_first)
    (ROOT / "index.html").write_text(index_html, encoding="utf-8")

    # 写每日归档页
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    day_html = render_archive_day(cards_html, date, win_start, win_end)
    (ARCHIVE / f"{date}.html").write_text(day_html, encoding="utf-8")

    # 打包下载
    if cards_data:
        build_zip(date, cards_data, disciplines_zh_used)

    # 追加历史
    history = load_history()
    history.insert(0, {"date": date, "tags": tags})
    save_history(history[:365 * 5])  # 保留 5 年
    update_archive_index(history[:365 * 5])

    print(f"[ok] {date} generated. {len(cards_data)} cards. window {win_start} ~ {win_end}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
