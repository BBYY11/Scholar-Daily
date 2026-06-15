#!/usr/bin/env python3
"""生成预览版 candidates.json（示意数据，仅用于看版式）"""
import json
from pathlib import Path

data = {
    "_note": "占位示意数据，不是真实检索结果。",
    "sociology": [{
        "title_zh": "平台悖论",
        "title_zh_full": "《平台悖论：数字劳动的隐形政治学》",
        "title_en": "The Platform Paradox: The Invisible Politics of Digital Labour",
        "cover_url": "",
        "positioning": "在数字劳动研究领域，把“平台=解放者”的乐观叙事做了一次系统性拆解，定位于劳工政治经济学的当代前沿。",
        "meta": {
            "作者": "Lina M. Howell",
            "出版社": "Stanford University Press",
            "出版日期": "2026-06-03",
            "ISBN": "978-1-5036-XXXX-X",
            "页数": "288 页",
            "URL": "https://www.sup.org/books/the-platform-paradox"
        },
        "intro": "Howell 借用骑手、零工、家政工三类田野，论证平台经济越成熟，劳动者的议价能力反而越脆弱。她提出“算法管理”概念，把过去隐形的劳动控制机制可视化，并比较中印两国的差异——这一跨国比较框架是本书最锋利之处。",
        "illustrations": [
            {"url": "", "caption": "示意：上海陆家嘴骑手在雨天接单（原书第 47 页配图说明）"},
            {"url": "", "caption": "示意：算法评分卡对接到骑手收入的因果图（原书图 3.2）"}
        ],
        "core_concepts": [
            {
                "term_zh": "算法管理",
                "term_en": "algorithmic management",
                "page": 41,
                "definition": "平台用算法评分、派单、定价等系统替代传统管理者的现场监督。区别于“算法歧视”——后者关注偏见的伦理后果，前者关注劳动控制的技术重构。Howell 在此把 Barocas & Selbst（2016）的算法公平研究与 Lepper & Nambisan（2021）的算法工作设计研究接了起来。"
            },
            {
                "term_zh": "劳动定价的转嫁",
                "term_en": "pricing-as-discipline",
                "page": 56,
                "definition": "平台不是用罚款来“管理”劳动者，而是用动态定价的随机性来制造焦虑。与泰勒制“科学管理”不同，这是一种“概率管理”——劳动者的任何微小偏差都可能被折算成下一单的损失。"
            },
            {
                "term_zh": "国家·平台共谋",
                "term_en": "state-platform co-construction",
                "page": 132,
                "definition": "Howell 反对“国家压制平台”的简化叙事，提出国家与平台不是对立面，而是在不同环节互相为对方供能——平台负责把劳动过程商品化，国家负责把不平等合法化。"
            }
        ],
        "reading_detail": [
            {"type": "chapter_title", "text": "第三章 · 算法作为管理者"},
            {"marker": "必读", "text": "Howell 跟踪北京和班加罗尔两支研究团队，记录平台如何用评分系统替代传统雇佣监督。她给出一组关键数据：评分每下降 0.1，骑手单均收入下降 8.3%。这个数字看起来技术性极强，但实际指向的是平台对劳动过程的彻底改造——过去骑手可以跟站长讨价还价，今天只能跟算法谈。"},
            {"type": "blockquote", "text": "“评分不是激励，是规训。它把不确定性从平台一侧转嫁到了劳动者一侧。”（原书第 51 页）"},
            {"marker": "必读", "text": "在这一节中，Howell 还揭示了一个被忽视的机制：算法评分对不同年龄段的骑手影响差异极大。她发现 40 岁以上骑手的评分下降速度是 25 岁以下骑手的 2.1 倍。这意味着平台的“中立”技术表面下，隐藏着一条不声不响的年龄淘汰线。这一观察对她后续的政体分析极为关键。"},
            {"type": "chapter_title", "text": "第五章 · 国家与平台的非对称关系"},
            {"marker": "必读", "text": "本章是全书亮点。Howell 对比中印两国监管路径：中国选择“算法协商”（出台算法透明性指引），印度选择“集体诉讼”（IT 工人工会主导的零工权益诉讼）。她用这个对比反驳了“国家压制平台”的简化叙事——国家其实在跟平台共谋，差别只在共谋的形态。这一节对理解当下中国互联网治理有直接借鉴意义。"},
            {"marker": "可跳", "text": "第二章 · 文献综述。相对标准，对熟悉劳动经济学的读者可以略读。"},
            {"marker": "关键脚注", "text": "第 47 页注 12 引用了 2024 年中国社科院的一份内部报告，Howell 通过私人渠道获得——这个数据源本身值得在方法论上讨论。"}
        ],
        "dialogue": [
            {"work": "Ghost Work", "year": 2019, "relation": "补充", "note": "Gray & Suri 关注点击工，本书关注平台工；前者是隐形劳动，后者是可见但被算法重塑的劳动。"},
            {"work": "《平台劳动：新业态下的劳动关系研究》", "year": 2023, "relation": "修正", "note": "国内既有研究偏重法权分析，Howell 则把政治经济学拉回中心，回应了国内研究“只见制度不见资本”的批评。"}
        ],
        "reviews": [{
            "title": "Book review: The Platform Paradox",
            "author": "Trevor M. Allen",
            "venue": "Contemporary Sociology",
            "date": "2026-06-10",
            "summary": "Allen 高度评价 Howell 的跨国比较，但批评她把 SaaS 工具型平台和零工平台混为一谈，削弱了结论的锋利度。",
            "url": "https://doi.org/10.1177/example"
        }],
        "score": 82,
        "score_breakdown": {
            "论据扎实度(40)": 32,
            "议题新颖度(30)": 26,
            "可读性(15)": 12,
            "学术影响(15)": 12
        },
        "score_reason": "田野扎实，跨国比较框架有创意；扣分点：平台定义偏窄，对“算法管理”概念的理论化还可以再推一步。"
    }],
    "anthropology": [{
        "title_zh": "照护作为通货",
        "title_zh_full": "《照护作为通货：东京老龄化社区的情感劳动》",
        "title_en": "Care as Currency: Affective Labour in Tokyo's Aging Neighbourhoods",
        "cover_url": "",
        "positioning": "在情感人类学与经济人类学交叉处，把照护重新理论化为可交换的社会通货，定位于当代日本研究新锐。",
        "meta": {
            "作者": "Yuki Tanabe",
            "期刊": "Cultural Anthropology",
            "出版日期": "2026-06-08",
            "DOI": "10.14506/caXX.XX.X",
            "URL": "https://journal.culanth.org/article/care-as-currency"
        },
        "intro": "Tanabe 在东京练马区一个老人照护互助小组里做了一年半田野。核心论点是：照护本身正在变成一种可被量化、可被交换的社会通货。这一判断挑战了传统人类学把照护视为“非生产性劳动”的预设。",
        "illustrations": [
            {"url": "", "caption": "示意：练马区某社区照护互助小组的“照护账本”内页（作者田野照片）"},
            {"url": "", "caption": "示意：练马区夕阳下的商店街（与正文描述的“老龄化社区”场景对应）"}
        ],
        "core_concepts": [
            {
                "term_zh": "照护账本",
                "term_en": "care ledger",
                "page": 14,
                "definition": "Tanabe 从田野中挖出的本土概念，指邻里间非货币化的互惠关系被逐笔登记下来的现象。它在功能上类似区块链的分布式账本，差别在信任机制——区块链靠技术，照护账本靠长期的面对面人际积累。"
            },
            {
                "term_zh": "照护作为通货",
                "term_en": "care as currency",
                "page": 3,
                "definition": "Tanabe 的核心概念。挑战传统人类学把照护视为“非生产性劳动”的预设。前提是：照护一旦可计量、可流通、可结转，它就具备了通货的所有特征，与货币的差别仅在形式。"
            },
            {
                "term_zh": "低龄退休社区",
                "term_en": "early-retirement enclaves",
                "page": 27,
                "definition": "指意大利、巴西等地出现的、由 50—65 岁健康退休人员自发组织起来的照护互助网络。Tanabe 把它与日本练马区对照，证明照护通货化不是东亚特殊现象。"
            }
        ],
        "reading_detail": [
            {"type": "chapter_title", "text": "一、Care ledger：被遮蔽的市场"},
            {"marker": "必读", "text": "Tanabe 用这个本土概念追踪邻里间非货币化的互惠关系。账本上记录的“我帮你买菜 1 次 = 你将来帮我挂号 1 次”，看似琐碎，实则是田野里挖出来的“被遮蔽的市场”。她把这个账本叫通货，不是隐喻，是严格意义上的通货——可计量、可流通、可结转。"},
            {"type": "blockquote", "text": "“在练马区，照顾一位邻居并不是礼物。它是一种预支。”（原文第 14 页）"},
            {"marker": "必读", "text": "Tanabe 进一步把这个账本跟区块链做了类比。两者都是分布式账本，差别在信任机制：区块链靠技术，照护账本靠长期的、面对面的人际积累。这一类比看似俏皮，但理论意义不小——它把“通货”概念的物质基础从国家背书转移到了社群关系上。"},
            {"type": "chapter_title", "text": "二、回嵌全球老龄化议题"},
            {"marker": "必读", "text": "Tanabe 没有把日本经验孤立处理。她用最后一节把练马区的小账本跟意大利、巴西的低龄退休社区对照，提出一个大胆命题：照护通货化不是日本的“地方奇观”，而是全球老龄资本主义的统一趋势。这个回嵌动作给论文加了不少分。"},
            {"marker": "关键脚注", "text": "第 8 页注 3 详细交代了进入田野的伦理程序——这一脚注的方法论含金量比正文还高。"}
        ],
        "dialogue": [
            {"work": "For Love or Money", "year": 2022, "relation": "补充", "note": "England 在美国语境下量化了照护的机会成本，Tanabe 的差异在于把账本搬进了田野现场。"},
            {"work": "Global Aging and the Future of Care Work", "year": 2024, "relation": "对话", "note": "Estes 等偏宏观政策分析，本文的微观民族志恰好补足了“政策怎么落到人”这一环。"}
        ],
        "reviews": [{
            "title": "Tanabe's Care Ledger as Method",
            "author": "Priya Krishnan",
            "venue": "American Ethnologist",
            "date": "2026-06-09",
            "summary": "Krishnan 认为 Tanabe 真正的方法论贡献是发明了 ledger as method——把账本当作民族志工具。这一创新值得被更多人类学借用。",
            "url": "https://doi.org/10.1176/example"
        }],
        "score": 88,
        "score_breakdown": {
            "论据扎实度(40)": 34,
            "议题新颖度(30)": 27,
            "可读性(15)": 13,
            "学术影响(15)": 14
        },
        "score_reason": "田野厚度够，把照护从道德领域拽进经济人类学；扣分点：理论对话稍显单薄，对欧美照护研究的援引可再深。"
    }],
    "history": [{
        "title_zh": "小人物的帝国",
        "title_zh_full": "《小人物的帝国：清代基层档案中的微历史》",
        "title_en": "The Empire of the Small: Microhistory from Late-Qing Grassroots Archives",
        "cover_url": "",
        "positioning": "在中国近代史研究里，重新激活“自下而上”路径，借新开放的县级档案把晚清地方政治做了一次像素级复原。",
        "meta": {
            "作者": "Wang Ming-ke",
            "出版社": "Brill",
            "出版日期": "2026-06-05",
            "ISBN": "978-90-04-XXXXX-X",
            "页数": "412 页",
            "URL": "https://brill.com/display/serial/EMH"
        },
        "intro": "作者借助四川巴县、浙江鄞县、江西万载三地新开放的晚清县级档案，重建 1880—1910 年间 12 个普通县民的诉讼、迁徙、宗族纠纷个案。核心论点：晚清地方治理的实际运行，远比传统宏观叙事所描绘的“国家扩张”或“内卷化”更复杂——它在很多时候是模糊、随机、依赖个人运作的。",
        "illustrations": [
            {"url": "", "caption": "示意：巴县衙门旧址（今重庆渝中区）—— 田野调查地标（原书第 89 页配图）"},
            {"url": "", "caption": "示意：万载县某族谱内页（作者抄录的宗族纠纷调解记录）"}
        ],
        "core_concepts": [
            {
                "term_zh": "档案沉默",
                "term_en": "archival silence",
                "page": 215,
                "definition": "Ann Laura Stoler 2010 年提出的概念，指档案中刻意或偶然的缺失——被删改的口供、被略去的人名、被消失的物证。本书把它推到对晚清旗人档案的分析，揭示了“沉默”本身就是一种史料。"
            },
            {
                "term_zh": "讼师中心",
                "term_en": "litigation-broker centricity",
                "page": 132,
                "definition": "作者的核心概念。在县以下的实际秩序维护中，讼师（而非县官、族长）才是关键节点。这一概念直接挑战了费孝通“无讼”传统的经典叙事。"
            },
            {
                "term_zh": "县级实际治理",
                "term_en": "de facto county governance",
                "page": 87,
                "definition": "区别于“de jure”（法定治理）——县官在文件里做的事，跟县以下实际发生的事，常常是脱节的。本书用大量个案证明，脱节是常态而非例外。"
            }
        ],
        "reading_detail": [
            {"type": "chapter_title", "text": "个案 4 · 讼师赵有德的二十年"},
            {"marker": "必读", "text": "作者用 9 页篇幅把一个讼师 1882—1901 年间的 31 桩案件串联起来。通过这个人物，读者看到讼师不是简单的法律掮客，而是地方秩序的实际维护者——国家法律反而是缺失的。这一节对理解中国法律传统的非国家化特征极具说服力。"},
            {"type": "blockquote", "text": "“帝国对县以下的世界几乎一无所知，而赵有德们填补了这一空白。”（第 132 页）"},
            {"marker": "必读", "text": "这一节的史料功夫是惊人的。作者从三个不同类型的档案（县衙卷宗、宗族族谱、地方报刊）交叉还原一个人物的轨迹，每一步都标明了档案之间的张力。这种“档案互证法”值得中国法律史研究者直接借鉴。"},
            {"type": "chapter_title", "text": "第十章 · 论档案沉默"},
            {"marker": "必读", "text": "作者专辟一章讨论档案里没有的——失踪的妇女、被略去的少数民族口供、刻意删除的旗人纠纷。这种反向史料学是近年海外汉学的新趋势，本书把它推到极致，值得国内学界借鉴。"},
            {"marker": "可跳", "text": "方法论附录。对熟悉档案学的读者而言内容偏基础，可略读。"}
        ],
        "dialogue": [
            {"work": "Primitive Rebels", "year": 1959, "relation": "对话", "note": "Hobsbawm 的原始反叛者框架强调结构性不满，本书则更关注个体的策略性行动。"},
            {"work": "《被治理的帝国：清代的州县与地方行政》", "year": 2024, "relation": "修正", "note": "既有研究偏重国家能力分析，本书指出县级实际治理高度依赖个人——这是对国家中心论的有力修正。"}
        ],
        "reviews": [{
            "title": "Microhistory with Teeth",
            "author": "Liam Kelley",
            "venue": "Late Imperial China",
            "date": "2026-06-11",
            "summary": "Kelley 评价本书的微史不是温情小品，而是有理论锋芒的解构——作者把皇帝、士绅、讼师都拉平到同一个分析平面。",
            "url": "https://doi.org/10.1353/late.XXXX"
        }],
        "score": 90,
        "score_breakdown": {
            "论据扎实度(40)": 36,
            "议题新颖度(30)": 26,
            "可读性(15)": 13,
            "学术影响(15)": 15
        },
        "score_reason": "档案解读功力深厚，对档案沉默的方法论自觉是本书最大亮点；扣分点：跨国比较略显仓促，三个县之间衔接可再打磨。"
    }],
    "political_science": [{
        "title_zh": "威权韧性",
        "title_zh_full": "《威权韧性：数字监控时代的政权存续》",
        "title_en": "Authoritarian Resilience in the Age of Digital Surveillance",
        "cover_url": "",
        "positioning": "在比较政治学领域，对“威权衰退论”做了一次系统反驳，定位于数字威权研究的最新一波。",
        "meta": {
            "作者": "Karim Sadjapour",
            "出版社": "Cambridge University Press",
            "出版日期": "2026-06-02",
            "ISBN": "978-1-108-XXXXX-X",
            "页数": "356 页",
            "URL": "https://www.cambridge.org/XXXXX"
        },
        "intro": "Sadjapour 选取 8 个案例（伊朗、沙特、埃及、埃塞俄比亚、匈牙利、塞尔维亚、菲律宾、越南），论证数字监控技术不是威权的棺材钉，反而是它的延长命。他把 2020—2024 年的衰退论叙事系统地驳回去——这本书值得所有做政体转型的学者认真对待。",
        "illustrations": [
            {"url": "", "caption": "示意：布达佩斯国会大厦——匈牙利案例的标志性场景（原书第 124 页）"},
            {"url": "", "caption": "示意：8 国监控技术渗透率 × 抗议事件数量的散点图（原书图 4.1）"}
        ],
        "core_concepts": [
            {
                "term_zh": "三重锁定",
                "term_en": "triple lock-in",
                "page": 33,
                "definition": "Sadjapour 的核心框架：精英锁定（co-optation）、叙事锁定（discourse）、技术锁定（surveillance）三层互锁。与 Levitsky & Way 的“竞争性威权”不同，三重锁定不强调“可竞争性”，强调三种机制的耦合。"
            },
            {
                "term_zh": "可量化指标体系",
                "term_en": "operationalizable index",
                "page": 47,
                "definition": "作者把“三重锁定”做成了可量化的指标体系。这是过去十年威权研究文献里少见的尝试——他给每个维度配了 5–8 个可观察变量，读者可以直接拿来比较。"
            },
            {
                "term_zh": "威权衰退论",
                "term_en": "autocratic decline thesis",
                "page": 11,
                "definition": "指 2020 年以来由 Treisman、Loubère、Svolik 等推动的一组论断，认为技术变化与人口结构正在终结威权的存续能力。本书是对这组论断的系统反驳。"
            }
        ],
        "reading_detail": [
            {"type": "chapter_title", "text": "第二章 · 概念框架：三重锁定"},
            {"marker": "必读", "text": "Sadjapour 提出“三重锁定”概念：精英锁定（co-optation）、叙事锁定（discourse）、技术锁定（surveillance）。他用这个框架把过去散落的威权研究文献整合起来，比 Levitsky & Way 的竞争性威权框架更具操作化优势。"},
            {"type": "blockquote", "text": "“威权不是一块石头，是一组通过日常重复而自我加固的锁。”（第 47 页）"},
            {"marker": "必读", "text": "这一章的方法论意义超出了案例本身。作者把“三重锁定”做成了可量化的指标体系——这是过去十年威权研究文献里少见的尝试。对做定量比较政治学的读者尤其值得精读。"},
            {"type": "chapter_title", "text": "第六章 · 越南的反例价值"},
            {"marker": "必读", "text": "Sadjapour 没有回避反例。他专辟一章讨论越南——一个监控很重、但体制内有改革派的国家。这一章实际削弱了他的主论点，但他处理得诚实，值得称赞。"},
            {"marker": "可跳", "text": "第七章 · 匈牙利。虽是案例之一，但跟既有文献重合度较高，可重点读第 2、3 节。"}
        ],
        "dialogue": [
            {"work": "The Recurrent Crisis of Authoritarianism", "year": 2023, "relation": "颠覆", "note": "Pepinsky 在该书中说威权正在衰退，Sadjapour 直接对话这一论断。"},
            {"work": "Digital Authoritarianism", "year": 2024, "relation": "补充", "note": "Feldstein 关注监控技术的供给端（厂商），本书关注需求端（政权的策略使用）。"}
        ],
        "reviews": [{
            "title": "Why Authoritarianism Persists",
            "author": "Steven Levitsky",
            "venue": "Journal of Democracy",
            "date": "2026-06-09",
            "summary": "Levitsky 高度评价该书是近五年最值得读的威权研究，但提醒读者注意：作者对反例（越南）的处理虽诚实，但理论上的吸纳仍显不够。",
            "url": "https://www.journalofdemocracy.org/articles/XXXX"
        }],
        "score": 85,
        "score_breakdown": {
            "论据扎实度(40)": 34,
            "议题新颖度(30)": 27,
            "可读性(15)": 12,
            "学术影响(15)": 12
        },
        "score_reason": "案例选择有策略，概念框架有锋芒；扣分点：对反例的理论吸纳不够，结论略偏决定论。"
    }]
}

Path("data/candidates.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("✓ candidates.json (preview) written")
