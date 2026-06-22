## 2026-06-18 09:59:37 UTC

✅ 6.18 章节顺序修复

修 bug:
- 3 张卡章节末尾堆叠 (社会学 9 个 + 人类学 8 个 + 政治学 7 个)
- 现在章节按 md 源实际段位置插入
- 用户看到的不再是空标题堆

验证:
- sociology: 9 章节嵌入 5 段
- anthropology: 8 章节嵌入 4 段
- history: 6.16 真品 (未改)
- political_science: 7 章节嵌入 5 段

commit: dd7ffe8b9f7aa1985ee6c11046fb8e36382c059f

---

## 2026-06-18 06:38:06 UTC

✅ 6.18 内容修复完成

修 bug:
- dialogue {q,a} → {speaker,text} 格式 — 现在每卡 4 条 (提问-回答×2)
- details/summary 现在正确显示 5-6 个 / 卡
- 推荐指数 88/85/94/90

完整 4 张:
- 社会学 (BJS 6.15): 精读 2207字, 5 概念, 4 对话
- 人类学 (Ethnography 6.08): 精读 2390字, 5 概念, 4 对话
- 历史学 (LIC 6.16 复用): 精读 2517字, 6 概念, 4 对话
- 政治学 (CPS 6.15): 精读 2348字, 5 概念, 4 对话

commit: 319b07c561ea402d7d77b40af6f648af2761c771

---

## 2026-06-18 03:05:52 UTC

✅ 6.18 推送成功

4 张新论文 (B+C 增强):
- 社会学: Education/Skills (BJS 6.15) 1553字
- 人类学: Emotion-as-method (Ethnography 6.08) 1643字  
- 历史学: Concealing/Revealing (LIC 6.16 复用) 2324字
- 政治学: State Power/Civil Servant (CPS 6.15) 1524字

B: 多期刊扩展 (每领域 5-7 本) + 28天窗口 + 论文热度评分
C: 论文 heat score 计算 (时效+引用+深度+合作)
fetch_today 历史学 fallback: OpenAlex 顶刊半年没新文, 自动回读 6.16 真品精读

commit: 9aa0328
Pages: https://bbyy11.github.io/Scholar-Daily/

---

## 2026-06-17 02:57:49 UTC

✅ 每日一书 2026-06-17 推送成功

commit: 06bbd12848b9336d94ad2c7a135ff2848f6232b1
链接: https://bbyy11.github.io/Scholar-Daily/
RSS: https://bbyy11.github.io/Scholar-Daily/feed.xml

---

## 2026-06-17 02:55:03 UTC

测试通知 — 每日一书 cron 通知脚本

---

