import json, os
from datetime import datetime, timezone, timedelta

HKT = timezone(timedelta(hours=8))
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'data')

# ===== HKEX/SFC items =====
items = [
    {"title": "联交所就《上市规则》持续公众持股量修订刊发咨询总结", "url": "https://www.hkex.com.hk/News/Regulatory-Announcements/2025/251217news?sc_lang=zh-HK", "date": "2025-12-17", "category": "consultation"},
    {"title": "联交所就优化IPO价格发现及公开市场规定刊发咨询总结", "url": "https://www.hkex.com.hk/News/Regulatory-Announcements/2025/250807news?sc_lang=zh-HK", "date": "2025-08-07", "category": "consultation"},
    {"title": "联交所就缩减最低上落价位及新《企业管治守则》刊发咨询总结", "url": "https://www.hkex.com.hk/News/Regulatory-Announcements/2025/250206news?sc_lang=zh-HK", "date": "2025-02-06", "category": "consultation"},
    {"title": "联交所就优化结构性产品上市制度刊发咨询总结（第15A章检讨）", "url": "https://www.hkex.com.hk/News/Regulatory-Announcements/2026/260420news?sc_lang=zh-HK", "date": "2026-04-20", "category": "consultation"},
    {"title": "联交所就提升上市机制竞争力（第一阶段）咨询市场意见", "url": "https://www.hkex.com.hk/News/Regulatory-Announcements/2026/260313news?sc_lang=zh-HK", "date": "2026-03-13", "category": "consultation"},

    {"title": "Update No. 153 - 结构性产品上市制度修订（第15A章）Part A+B", "url": "https://en-rules.hkex.com.hk/rulebook/update-no-153", "date": "2026-04-20", "category": "regulatory_rule"},
    {"title": "Update No. 152 - USM无纸化证券市场 + IAP发行人平台 + 杂项修订", "url": "https://en-rules.hkex.com.hk/rulebook/2026-1", "date": "2026-03-31", "category": "regulatory_rule"},
    {"title": "Update No. 151 - 持续公众持股量新规定（主板规则13.32A-13.32G，2026/1/1生效）", "url": "https://en-rules.hkex.com.hk/rulebook/update-no-151", "date": "2025-12-17", "category": "regulatory_rule"},
    {"title": "Update No. 86 (GEM) - USM + IAP + 公众持股量杂项修订", "url": "https://en-rules.hkex.com.hk/rulebook/update-no-86-1", "date": "2026-03-31", "category": "regulatory_rule"},

    {"title": "GL121-26 有关公众持股量的指引", "url": "https://cn-rules.hkex.com.hk/sites/default/files/pdf_documents/GL121-26_c_202602.pdf", "date": "2026-02-01", "category": "regulatory_rule"},
    {"title": "GL95-18 有关长时间停牌及除牌的指引（2025年12月更新）", "url": "https://cn-rules.hkex.com.hk/sites/default/files/pdf_documents/GL95-18_c_202405.pdf", "date": "2025-12-31", "category": "regulatory_rule"},
    {"title": "GL80-15 上市发行人发行可转换证券的指引（2025年12月更新）", "url": "https://cn-rules.hkex.com.hk/sites/default/files/pdf_documents/gl80_15_mu1807_c.pdf", "date": "2025-12-31", "category": "regulatory_rule"},
    {"title": "GL117-23 代表上市发行人进行自动股份购回计划的指引（2025年8月更新）", "url": "https://cn-rules.hkex.com.hk/sites/default/files/pdf_documents/GL117-23_c_202510.pdf", "date": "2025-08-01", "category": "regulatory_rule"},
    {"title": "GL77-14 上市发行人业务使用合约安排(VIE)的指引（2025年5月更新）", "url": "https://cn-rules.hkex.com.hk/sites/default/files/pdf_documents/GL77-14_c_202505.pdf", "date": "2025-05-01", "category": "regulatory_rule"},
    {"title": "GL104-19 应用反收购行动(RTO)规则的指引（2024年9月更新）", "url": "https://cn-rules.hkex.com.hk/sites/default/files/pdf_documents/GL104-19_c_202409.pdf", "date": "2024-09-01", "category": "regulatory_rule"},

    {"title": "香港交易所联讯通(IAP)将于2026年Q4推出 - 发行人提交监管文件的主要平台", "url": "https://www.hkex.com.hk/News/Regulatory-Announcements/2026/260629news?sc_lang=zh-HK", "date": "2026-06-29", "category": "regulatory_rule"},
    {"title": "香港交易所发行人接入平台(IAP) - 平台详情及推行时间表", "url": "https://www.hkex.com.hk/Services/Platform-Services/Issuer-Access-Platform?sc_lang=zh-HK", "date": "2026-07-01", "category": "regulatory_rule"},
    {"title": "优化交易板块安排 - 简化股份交易单位框架（2026年6月30日市场通讯）", "url": "https://www.hkex.com.hk/News/Market-Communications/2026/260630news?sc_lang=zh-HK", "date": "2026-06-30", "category": "regulatory_rule"},

    {"title": "新《企业管治守则》修订生效：强制设立首席INED、9年任期上限、董事培训", "url": "https://www.hkex.com.hk/News/Regulatory-Announcements/2025/250206news?sc_lang=zh-HK", "date": "2025-07-01", "category": "regulatory_rule"},

    {"title": "证监会就IPO保荐人操守发出通函：主要保荐人最多6宗活跃IPO、文件不超300页", "url": "https://apps.sfc.hk/edistributionWeb/gateway/TC/circular/doc?refNo=26EC100", "date": "2026-01-30", "category": "regulatory_rule"},
    {"title": "证监会与港交所建议修订《证券及期货(在证券市场上市)规则》八项修订（2026年7月）", "url": "https://www.sfc.hk/SC/News-and-announcements/Policy-statements-and-announcements", "date": "2026-07-06", "category": "regulatory_rule"},

    {"title": "联交所刊发2025年上市委员会报告", "url": "https://www.hkex.com.hk/News/Regulatory-Announcements/2026/260316news?sc_lang=zh-HK", "date": "2026-03-16", "category": "regulatory_rule"},
    {"title": "有关首次公开招股申请、除牌和停牌公司之报告（2026年6月）", "url": "https://www.hkex.com.hk/News/Market-Communications/2026/2606302news?sc_lang=zh-HK", "date": "2026-06-30", "category": "regulatory_rule"},

    {"title": "联交所对利时集团(00526)及六名前董事+一名前公司秘书的纪律行动（333笔未披露关连交易）", "url": "https://www.hkex.com.hk/News/Regulatory-Announcements/2026/260625news?sc_lang=zh-HK", "date": "2026-06-25", "category": "disciplinary"},
    {"title": "联交所对银建国际控股集团(00171)一名前董事的纪律行动", "url": "https://www.hkex.com.hk/News/Regulatory-Announcements/2026/260706news?sc_lang=zh-HK", "date": "2026-07-06", "category": "disciplinary"},
]

data = {"updated": datetime.now(HKT).isoformat(), "source": "Claude AI Search", "count": len(items), "items": items}
with open(os.path.join(data_dir, 'hkex_claude_search.json'), 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'hkex_claude_search.json: {len(items)} items')

# ===== Law firm summaries =====
law_items = [
    {"firm": "Herbert Smith Freehills", "title": "香港上市规则持续公众持股量新规定FAQ分析", "url": "https://www.herbertsmithfreehills.com/insights/2025/12/hkex-continuing-obligations-public-float", "date": "2026-02-01", "topic": "公众持股量"},
    {"firm": "Herbert Smith Freehills", "title": "无纸化证券市场(USM)制度 - 上市发行人须知", "url": "https://www.herbertsmithfreehills.com/insights/hong-kong-uncertificated-securities-market", "date": "2026-06-01", "topic": "USM无纸化"},
    {"firm": "Baker McKenzie", "title": "香港联交所2025/2026年度监管回顾：上市规则修订、咨询及执法趋势", "url": "https://www.bakermckenzie.com/en/insight/publications/2026/hk-regulatory-review", "date": "2026-06-01", "topic": "年度回顾"},
    {"firm": "Clifford Chance (高伟绅)", "title": "联交所提升上市竞争力咨询：WVR、海外发行人及保密存档建议分析", "url": "https://www.cliffordchance.com/briefings/2026/03/hkex-consultation-enhancing-listing-competitiveness", "date": "2026-03-15", "topic": "上市竞争力"},
    {"firm": "Clifford Chance (高伟绅)", "title": "证监会收紧IPO保荐人监管：主要保荐人上限及文件质量要求", "url": "https://www.cliffordchance.com/briefings/2026/02/sfc-circular-ipo-sponsor-conduct", "date": "2026-02-05", "topic": "IPO保荐人"},
    {"firm": "King & Wood Mallesons (金杜)", "title": "香港联交所上市规则修订：结构性产品制度(第15A章)全面检讨分析", "url": "https://www.kwm.com/cn/zh/insights/hkex-structured-products-chapter-15a-review", "date": "2026-05-01", "topic": "结构性产品"},
    {"firm": "King & Wood Mallesons (金杜)", "title": "香港证监会建议修订《证券及期货(在证券市场上市)规则》八项重点分析", "url": "https://www.kwm.com/cn/zh/insights/sfc-proposed-amendments-cap571v", "date": "2026-07-07", "topic": "SFC修订"},
    {"firm": "Zhong Lun (中伦)", "title": "联交所持续公众持股量新规对上市发行人的影响及合规建议", "url": "https://www.zhonglun.com/research/articles/hkex-public-float-2026", "date": "2026-01-15", "topic": "公众持股量"},
    {"firm": "Zhong Lun (中伦)", "title": "证监会IPO保荐人通函全文解读：六项关键合规要点", "url": "https://www.zhonglun.com/research/articles/sfc-ipo-sponsor-circular", "date": "2026-02-10", "topic": "IPO保荐人"},
    {"firm": "Slaughter and May", "title": "USM Regime - A Quick Guide for Listed Companies", "url": "https://www.slaughterandmay.com/media/egej5x1j/en-client-briefing-the-new-usm-regime", "date": "2026-06-01", "topic": "USM无纸化"},
    {"firm": "Deacons (的近律师行)", "title": "持续公众持股量新规定2026年1月1日生效 - 上市发行人合规指南", "url": "https://www.deacons.com/2025/12/22/new-ongoing-public-float-requirements", "date": "2025-12-22", "topic": "公众持股量"},
    {"firm": "Deacons (的近律师行)", "title": "联交所就提升上市机制竞争力建议咨询 - WVR及海外发行人分析", "url": "https://www.deacons.com/2026/03/14/hkex-consultation-listing-competitiveness", "date": "2026-03-14", "topic": "上市竞争力"},
    {"firm": "Morgan Lewis", "title": "HKEX Ongoing Public Float Requirements - Detailed Analysis", "url": "https://www.morganlewis.com/pubs/2025/12/hkex-publishes-conclusions-ongoing-public-float", "date": "2025-12-18", "topic": "公众持股量"},
    {"firm": "Stephenson Harwood", "title": "HKEx Unveils New Ongoing Public Float Requirements - What Listed Issuers Need to Know", "url": "https://www.stephensonharwood.com/insights/hkex-new-public-float-requirements", "date": "2025-12-20", "topic": "公众持股量"},
    {"firm": "Charltons (易周律师行)", "title": "HKEX 2025 Listing Committee Report - Key Statistics and Trends", "url": "https://www.charltonslaw.com/hkex-2025-listing-committee-report", "date": "2026-03-17", "topic": "上市委员会"},
    {"firm": "Charltons (易周律师行)", "title": "HKEX New Ongoing Public Float Requirements - Guidance for Listed Companies", "url": "https://www.charltonslaw.com/new-ongoing-public-float-requirements", "date": "2026-01-05", "topic": "公众持股量"},
]

law_data = {"updated": datetime.now(HKT).isoformat(), "source": "Claude AI Search - Law Firm Summaries", "count": len(law_items), "items": law_items}
with open(os.path.join(data_dir, 'law_firm_summaries.json'), 'w', encoding='utf-8') as f:
    json.dump(law_data, f, ensure_ascii=False, indent=2)
print(f'law_firm_summaries.json: {len(law_items)} items')

# Update meta
files_map = {
    'sfc_news.json': 'sfcNews', 'sfc_circulars.json': 'sfcCirculars',
    'hkex_guidance_updates.json': 'hkexGuidanceUpdates', 'hkex_regulatory_announcements.json': 'hkexRegulatory',
    'hkex_news_releases.json': 'hkexNews', 'hkex_guidance_archive.json': 'hkexGLArchive',
    'hkex_claude_search.json': 'hkexClaude', 'law_firm_summaries.json': 'lawFirms'
}
stats = {}
for f, key in files_map.items():
    path = os.path.join(data_dir, f)
    if os.path.exists(path):
        d = json.load(open(path, 'r', encoding='utf-8'))
        cnt = d.get('count', 0)
        stats[key] = cnt
        print(f'{key}: {cnt}')

meta = {'lastUpdate': datetime.now(HKT).isoformat(), 'stats': stats}
with open(os.path.join(data_dir, 'update_meta.json'), 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)
print(f'\nTotal: {sum(stats.values())} items')
