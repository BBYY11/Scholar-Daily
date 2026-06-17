# 每日一书 Cron Prompt 详细说明

## 流程

```
1. cd /workspace/daily-book
2. python3 scripts/fetch_today.py   # 拉 OpenAlex 4 领域近 2 周新作
   (已带质量门: type:article|review + referenced_works_count:30-9999)
3. 读 data/candidates_today.json — 看 4 张是什么论文
```

## 字段要求

| 字段 | 要求 | 字符数下限 |
|---|---|---|
| `title_zh` | 中文译名 | 10 |
| `title_zh_full` | 《中文译名》 | 15 |
| `positioning` | 一句话定位（中文） | 100 |
| `intro` | 200-300 字导读（用 abstract 作底，**用中文**） | 200 |
| `core_concepts` | 3-5 个学术概念（含中英对照 + 学术释义 80 字以上/个） | 3 |
| `reading_detail` | **1500-2000 字**精读（中文，Seminar 讨论稿级别） | **1500** |
| `dialogue` | 1 段学术对话（提问-回答形式，中文） | 1 |
| `score` | 0-100 整数 | — |
| `score_breakdown` | 论据/新颖/可读/学术影响 四维评分 | 4 |
| `score_reason` | 评分理由（中文 100 字+） | 100 |
| `author.bio` | 作者简介 50 字+ | 50 |

## 字段格式示例

```python
# core_concepts 字段名 (注意!)
{
    "term_zh": "碎片化工作场所",
    "term_en": "Fissured Workplace",
    "page": "",
    "definition": "Weil (2014) 提出的概念框架，指品牌方通过层层外包把雇佣责任转嫁给下游网络的法律安排。本文证明这一安排不仅影响工资水平，更系统性地降低了雇佣稳定性。"
}

# reading_detail 必须分章节 (章节化)
[
    {"type": "chapter_title", "text": "范式重置：从工人侧转向组织侧"},
    {"type": "para", "marker": "关键", "text": "Aeppli 这篇论文最值得讨论的不是..."},
    {"type": "chapter_title", "text": "数据基础：DADS 受限访问 + 处理强度指标"},
    {"type": "para", "marker": "关键", "text": "这一转向的实证基础非常扎实..."},
    {"type": "chapter_title", "text": "研究局限：性别与移民视角缺位"},
    {"type": "para", "marker": "可跳", "text": "论文的一个小遗憾是没有深入讨论..."},
    # ... 至少 5 个 chapter_title + 至少 3 段标"关键"+ 至少 1 段标"可跳"
]

# dialogue 提问-回答形式
[
    {"speaker": "提问", "text": "你的发现是不是说..."},
    {"speaker": "回答", "text": "不是偏好问题，是结构问题..."}
]
```

## 自检 (跑 quality_check.py)

```bash
python3 scripts/quality_check.py
```

如果 exit 1 — 看具体哪个字段不达标 — 修 — 重跑 — 一直到 exit 0。

## 推送

```bash
python3 scripts/generate_today.py
git add -A
if git diff --cached --quiet; then
    echo "无变更"
else
    git commit -m "chore: daily auto-generate $(date +%Y-%m-%d)"
    git push origin main --force-with-lease
fi
echo $(git rev-parse HEAD) > data/last_push.json
```

## 验证 Pages

```bash
sleep 30
for i in 1 2 3 4 5; do
    curl -sL --max-time 30 https://bbyy11.github.io/Scholar-Daily/ -o /tmp/check.html
    if [ -f /tmp/check.html ] && [ $(wc -c < /tmp/check.html) -gt 30000 ]; then
        echo "✅ Pages 重建成功: $(wc -c < /tmp/check.html) bytes"
        break
    fi
    sleep 10
done
```

## 通知

```bash
bash scripts/notify.sh "✅ 每日一书 $(date +%Y-%m-%d) 推送成功\n\n4 张精读卡已上线\ncommit: $(cat data/last_push.json)\n链接: https://bbyy11.github.io/Scholar-Daily/"
```

失败通知:
```bash
bash scripts/notify.sh "❌ 每日一书 $(date +%Y-%m-%d) 失败\n\n错误: <error details>"
```

## 重要约束

- **6.16 是当前首期** — candidates.json 锁定的 4 张真品精读不要动
- **6.17+** — fetch_today 拉新数据后由你写
- **找不到全文** — 标 `abridged`，但精读不能短于 1500 字（用 abstract + 论文背景扩写）
- **author.bio** — OpenAlex 拿不到就标 "（基于 affiliation 推测）"，**但 50 字+**
- **不偷懒** — 你（LLM）写不到位 = 任务失败 = 浪费时间。明小楼明早会检查。

## 响应

推送成功后简短回复（< 200 字）：
```
✅ YYYY-MM-DD 推送成功
4 张精读卡已上线
GitHub: https://bbyy11.github.io/Scholar-Daily/
RSS: https://bbyy11.github.io/Scholar-Daily/feed.xml
commit: <SHA>
```
