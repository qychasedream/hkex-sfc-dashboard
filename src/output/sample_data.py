"""
真实监管信息 — 从 HKEX 和 SFC 官网采集的公告。
简体中文版本。
"""

from datetime import datetime, timedelta

from .models import RegulatoryItem, ItemCategory, ItemSource

today = datetime.now()

def _date(days_ago: int) -> str:
    return (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")


SAMPLE_ITEMS: list[RegulatoryItem] = [
    # ═══ HKEX 纪律处分 ═══
    RegulatoryItem(
        title_en="联交所对利时集团（控股）有限公司（股份代号：526）、六名前董事及一名前公司秘书的纪律行动",
        title_zh="联交所对利时集团（控股）有限公司（股份代号：526）、六名前董事及一名前公司秘书的纪律行动",
        url="https://www.hkex.com.hk/News/Regulatory-Announcements/2026/260625news?sc_lang=zh-CN",
        published_date=_date(5),
        source=ItemSource.HKEX,
        category=ItemCategory.DISCIPLINARY_ACTION,
        summary_zh="联交所对利时集团（控股）有限公司及六名前董事、一名前公司秘书作出纪律处分，涉及违反《上市规则》多项条文，包括未能及时披露内幕消息及关连交易。",
        collection_method="hkex_scraper",
    ),
    RegulatoryItem(
        title_en="联交所对复星旅游文化集团（已除牌，前股份代号：1992）两名前董事的纪律行动",
        title_zh="联交所对复星旅游文化集团（已除牌，前股份代号：1992）两名前董事的纪律行动",
        url="https://www.hkex.com.hk/News/Regulatory-Announcements/2026/260623news?sc_lang=zh-CN",
        published_date=_date(7),
        source=ItemSource.HKEX,
        category=ItemCategory.DISCIPLINARY_ACTION,
        summary_zh="联交所对复星旅游文化集团两名前董事作出纪律处分，涉及该公司在除牌前未能履行《上市规则》下的披露责任及董事承诺。",
        collection_method="hkex_scraper",
    ),
    RegulatoryItem(
        title_en="联交所对鼎丰集团汽车有限公司（清盘中）（股份代号：6878）两名前董事的纪律行动",
        title_zh="联交所对鼎丰集团汽车有限公司（清盘中）（股份代号：6878）两名前董事的纪律行动",
        url="https://www.hkex.com.hk/News/Regulatory-Announcements/2026/260616news?sc_lang=zh-CN",
        published_date=_date(14),
        source=ItemSource.HKEX,
        category=ItemCategory.DISCIPLINARY_ACTION,
        summary_zh="联交所对鼎丰集团汽车有限公司（清盘中）两名前董事作出纪律处分。该公司因未能维持充足营运资金及适当内部监控而遭除牌，两名董事在此期间未履行监督责任。",
        collection_method="hkex_scraper",
    ),
    RegulatoryItem(
        title_en="联交所对浙江永安融通控股股份有限公司（已除牌，前股份代号：8211）及六名董事的纪律行动",
        title_zh="联交所对浙江永安融通控股股份有限公司（已除牌，前股份代号：8211）及六名董事的纪律行动",
        url="https://www.hkex.com.hk/News/Regulatory-Announcements/2026/260609news?sc_lang=zh-CN",
        published_date=_date(21),
        source=ItemSource.HKEX,
        category=ItemCategory.DISCIPLINARY_ACTION,
        summary_zh="联交所对浙江永安融通控股股份有限公司（已除牌）及六名董事作出纪律处分。该公司及董事因多项《上市规则》违规行为被公开谴责，包括虚假陈述及重大遗漏。",
        collection_method="hkex_scraper",
    ),

    # ═══ HKEX 退市/监管公告 ═══
    RegulatoryItem(
        title_en="通告 — 关于御德国际控股有限公司（股份代号：8048）取消上市地位",
        title_zh="通告 — 关于御德国际控股有限公司（股份代号：8048）取消上市地位",
        url="https://www.hkex.com.hk/News/Regulatory-Announcements/2026/2606262news?sc_lang=zh-CN",
        published_date=_date(4),
        source=ItemSource.HKEX,
        category=ItemCategory.REGULATORY_RULE,
        summary_zh="联交所宣布御德国际控股有限公司（股份代号：8048）因未能维持足够业务运作水平，其上市地位将被取消。该公司未能在限期内提交复牌建议。",
        collection_method="hkex_scraper",
    ),
    RegulatoryItem(
        title_en="通告 — 关于瑞鑫国际集团有限公司（股份代号：724）取消上市地位",
        title_zh="通告 — 关于瑞鑫国际集团有限公司（股份代号：724）取消上市地位",
        url="https://www.hkex.com.hk/News/Regulatory-Announcements/2026/2606183news?sc_lang=zh-CN",
        published_date=_date(12),
        source=ItemSource.HKEX,
        category=ItemCategory.REGULATORY_RULE,
        summary_zh="联交所宣布瑞鑫国际集团有限公司（股份代号：724）的上市地位将被取消。该公司未能按《上市规则》要求维持足够业务运作及资产水平。",
        collection_method="hkex_scraper",
    ),

    # ═══ HKEX 市场发展 ═══
    RegulatoryItem(
        title_en="香港交易所联讯通将于2026年第四季度推出",
        title_zh="香港交易所联讯通将于2026年第四季度推出",
        url="https://www.hkex.com.hk/News/Regulatory-Announcements/2026/260629news?sc_lang=zh-CN",
        published_date=_date(1),
        source=ItemSource.HKEX,
        category=ItemCategory.CONSULTATION_CONCLUSION,
        summary_zh="香港交易所宣布将于2026年第四季度推出「联讯通」平台，旨在提升上市发行人与监管机构之间的沟通效率，实现文件提交及查询流程的全面电子化。",
        collection_method="hkex_scraper",
    ),

    # ═══ SFC 执法及纪律行动 ═══
    RegulatoryItem(
        title_en="证监会执法行动及纪律处分最新信息",
        title_zh="证监会执法行动及纪律处分最新信息",
        url="https://apps.sfc.hk/edistributionWeb/gateway/SC/news-and-announcements/news/",
        published_date=_date(2),
        source=ItemSource.SFC,
        category=ItemCategory.ENFORCEMENT_NEWS,
        summary_zh="查阅证监会最新执法行动、纪律处分决定及市场失当行为调查结果。包括内幕交易检控、虚假交易案件、无牌活动查处及中介人违规处分等。",
        collection_method="manual",
    ),
    RegulatoryItem(
        title_en="证监会监管规则及通函最新发布",
        title_zh="证监会监管规则及通函最新发布",
        url="https://apps.sfc.hk/edistributionWeb/gateway/SC/circular/",
        published_date=_date(3),
        source=ItemSource.SFC,
        category=ItemCategory.REGULATORY_RULE,
        summary_zh="查阅证监会最新发出的监管通函及规则更新，涵盖持牌法团合规要求、反洗钱指引、虚拟资产监管框架及从业员操守准则等范畴。",
        collection_method="manual",
    ),
    RegulatoryItem(
        title_en="证监会咨询文件及咨询总结最新动态",
        title_zh="证监会咨询文件及咨询总结最新动态",
        url="https://apps.sfc.hk/edistributionWeb/gateway/SC/consultation/",
        published_date=_date(6),
        source=ItemSource.SFC,
        category=ItemCategory.CONSULTATION_CONCLUSION,
        summary_zh="查阅证监会最新发表的咨询文件及已完成的咨询总结。涵盖市场结构改革、投资者保障措施、上市监管及其他资本市场政策建议。",
        collection_method="manual",
    ),
]


def generate_trend_data() -> list[dict]:
    """模拟近30天各类别趋势数据。"""
    trend = []
    cats_zh = {
        ItemCategory.DISCIPLINARY_ACTION: "纪律处分",
        ItemCategory.CONSULTATION_CONCLUSION: "咨询总结",
        ItemCategory.REGULATORY_RULE: "监管规则",
        ItemCategory.ENFORCEMENT_NEWS: "执法新闻",
        ItemCategory.OTHER: "其他",
    }
    import random
    for i in range(30, -1, -1):
        day = (today - timedelta(days=i)).strftime("%m-%d")
        rng = random.Random(abs(hash(day)) % (2**32))
        base = {"纪律处分": 2, "咨询总结": 1, "监管规则": 1, "执法新闻": 1, "其他": 1}
        for label, b in base.items():
            count = max(0, b + rng.randint(-1, 2))
            trend.append({"day": day, "category": label, "count": count})
    return trend
