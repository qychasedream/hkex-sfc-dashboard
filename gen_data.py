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

# ===== Law firm summaries (links verified via HTTP 200 + title match) =====
# 注：金杜(KWM)、O'Melveny 链接因 Cloudflare 反爬无法验证，不收录 —— 只保留可验证打开的真实链接
law_items = [
    # === 2026年7-8月：上市竞争力咨询总结 + GL122-26 数字资产指引（2026-08-28 验证） ===
    {"firm": "Morgan Lewis", "title": "HKEX Adopts Proposed Amendments to Listing Framework Following Competitiveness Review", "url": "https://www.morganlewis.com/pubs/2026/08/hkex-adopts-proposed-amendments-to-listing-framework-following-competitiveness-review", "date": "2026-08-10", "topic": "上市竞争力", "summary": "联交所采纳上市框架竞争力改革建议：WVR门槛下调、第二上市放宽，第二阶段咨询即将展开。"},
    {"firm": "Davis Polk", "title": "HKEX clarifies listing expectations for digital asset activities", "url": "https://www.davispolk.com/insights/client-update/hkex-clarifies-listing-expectations-digital-asset-activities", "date": "2026-08-21", "topic": "数字资产", "summary": "解读GL122-26：联交所厘清数字资产业务的上市期望，披露要求与内部监控架构全解析。"},
    {"firm": "Han Kun (汉坤)", "title": "香港联交所数字资产指引正式落地：港股发行人数字资产业务合规全景图", "url": "https://www.hankunlaw.com/portal/article/index/cid/8/id/17007.html", "date": "2026-07-30", "topic": "数字资产", "summary": "中文深度解读GL122-26：数字资产投资、稳定币、RWA代币化的上市资格、持续合规与披露要求。"},
    {"firm": "Charltons (易周律师行)", "title": "Revised HKEX Listing Rules Take Effect on 24 July 2026", "url": "https://www.charltonslaw.com/revised-hkex-listing-rules-take-effect-on-24-july-2026/", "date": "2026-07-29", "topic": "上市竞争力", "summary": "经修订的《上市规则》于2026年7月24日生效：WVR、第二上市、生物科技及特专科技公司改革要点。"},
    {"firm": "Howse Williams (何韦律师行)", "title": "上市框架競爭力檢討的諮詢總結", "url": "https://howsewilliams.com/tc/consultation-conclusions-on-competitiveness-review-of-listing-framework/", "date": "2026-07-29", "topic": "上市竞争力", "summary": "中文解读咨询总结：WVR财务资格门槛减半、第二上市门槛降低等改革逐条分析。"},
    {"firm": "Latham & Watkins (瑞生)", "title": "Hong Kong Stock Exchange Publishes Consultation Conclusions on Proposals to Enhance Listing Competitiveness", "url": "https://www.lw.com/en/insights/hong-kong-stock-exchange-publishes-consultation-conclusions-on-proposals-to-enhance-listing", "date": "2026-07-28", "topic": "上市竞争力", "summary": "联交所发布提升上市竞争力咨询总结：生物科技/特专科技公司外部验证要求及WVR资格门槛分析。"},
    {"firm": "Norton Rose Fulbright", "title": "HKEx Competitiveness Review: Key reforms to the listing framework", "url": "https://www.nortonrosefulbright.com/en/knowledge/publications/4bee16b7/hkex-competitiveness-review-key-reforms-to-the-listing-framework", "date": "2026-07-24", "topic": "上市竞争力", "summary": "竞争力检讨三大改革：优化WVR制度、便利海外发行人上市、简化首次上市要求。"},
    # === 2026年上半年（早前已验证） ===
    {"firm": "Charltons (易周律师行)", "title": "HKEX Launches Major Consultation on Listing Framework Reform", "url": "https://www.charltonslaw.com/hkex-launches-major-consultation-on-listing-framework-reform/", "date": "2026-03-17", "topic": "上市竞争力", "summary": "联交所就上市框架改革推出重大市场咨询，全面检讨上市机制竞争力。"},
    {"firm": "Bird & Bird (鸿鹄)", "title": "HKEX revises ongoing public float requirements: what listed issuers need to know", "url": "https://www.twobirds.com/en/insights/2026/china/hkex-revises-ongoing-public-float-requirements-what-listed-issuers-need-to-know", "date": "2026-01-15", "topic": "公众持股量", "summary": "解读联交所持续公众持股量要求修订要点，以及上市发行人需要了解的合规事项。"},
    {"firm": "JSM (孖士打)", "title": "Hong Kong Stock Exchange Announces More Flexible Public Float Requirements for 2026", "url": "https://www.jsm.com/publications/2025/hong-kong-stock-exchange-announces-more-flexible-public-float-requirements-for-2026/", "date": "2025-12-18", "topic": "公众持股量", "summary": "联交所宣布自2026年起实施更灵活的公众持股量要求及其对上市公司的影响。"},
    {"firm": "Charltons (易周律师行)", "title": "New Ongoing Public Float Requirements for HKEX Listed Companies from 1 January 2026", "url": "https://www.charltonslaw.com/new-ongoing-public-float-requirements-for-hkex-listed-companies-from-1-january-2026/", "date": "2025-12-17", "topic": "公众持股量", "summary": "联交所上市公司自2026年1月1日起适用新的持续公众持股量要求，逐条解读新规。"},
    {"firm": "Norton Rose Fulbright", "title": "SFC tightens sponsor compliance framework – new reporting, review and inspection requirements", "url": "https://www.nortonrosefulbright.com/en-cn/knowledge/publications/5937882d/sfc-tightens-sponsor-compliance-framework-new-reporting-review-and-inspection-requirements", "date": "2026-02-05", "topic": "IPO保荐人", "summary": "证监会收紧保荐人合规框架：新增申报、检讨及视察要求。"},
    {"firm": "Davis Polk", "title": "SFC identifies regulatory concerns on sponsor work amid surge in Hong Kong IPO activity", "url": "https://www.davispolk.com/insights/client-update/sfc-identifies-regulatory-concerns-sponsor-work-amid-surge-hong-kong-ipo", "date": "2026-02-04", "topic": "IPO保荐人", "summary": "香港IPO活动激增之际，证监会识别出保荐人工作的监管关注点。"},
    {"firm": "Bird & Bird (鸿鹄)", "title": "SFC issues stern warning to IPO sponsors amid surge in listing applications", "url": "https://www.twobirds.com/en/insights/2026/sfc-issues-stern-warning-to-ipo-sponsors-amid-surge-in-listing-applications", "date": "2026-02-03", "topic": "IPO保荐人", "summary": "上市申请激增，证监会向IPO保荐人发出严厉警告，强调尽职审查标准。"},
    {"firm": "Charltons (易周律师行)", "title": "Appendix to the SFC Sponsor Circular: Substandard Conduct of Sponsors – Case Examples and Regulatory Expectations", "url": "https://www.charltonslaw.com/appendix-to-the-sfc-sponsor-circular-substandard-conduct-of-sponsors-case-examples-and-regulatory-expectations/", "date": "2026-02-02", "topic": "IPO保荐人", "summary": "证监会保荐人通函附录：剖析保荐人不当行为案例及监管期望。"},
]

# 合并而非覆盖：保留扫描器 (src/collectors/law_firm_scan.py) 自动收录的条目
law_json_path = os.path.join(data_dir, 'law_firm_summaries.json')
curated_urls = {i['url'].rstrip('/') for i in law_items}
if os.path.exists(law_json_path):
    try:
        existing = json.load(open(law_json_path, 'r', encoding='utf-8')).get('items', [])
        for i in existing:
            if i.get('url', '').rstrip('/') not in curated_urls:
                law_items.append(i)  # 保留自动收录条目
    except Exception:
        pass
law_items.sort(key=lambda i: i.get('date', ''), reverse=True)

law_data = {"updated": datetime.now(HKT).isoformat(), "source": "Verified Law Firm Publications (curated + auto-scan)", "count": len(law_items), "items": law_items}
with open(law_json_path, 'w', encoding='utf-8') as f:
    json.dump(law_data, f, ensure_ascii=False, indent=2)
print(f'law_firm_summaries.json: {len(law_items)} items (verified links)')

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
