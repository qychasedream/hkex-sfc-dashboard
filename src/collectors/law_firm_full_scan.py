#!/usr/bin/env python3
"""
律所监管解读·全量扫描器（个人版网站用）
- 基于 law_firm_summaries.json（现有 17 家，含默认隐藏的 4 家）为底
- 新增红圈所/港业务内资所列表页抓取：君合、方达、环球、中伦、天元
- 按香港资本市场关键词筛选，验证链接可打开后写入 law_firm_full.json
- 按 URL 去重，条目累积保留（最长 MAX_AGE_DAYS 天）
"""

import json
import os
import re
import sys
import io
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HKT = timezone(timedelta(hours=8))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PROJECT_ROOT, 'docs', 'data')
BASE_JSON = os.path.join(DATA_DIR, 'law_firm_summaries.json')   # 同事版（底）
FULL_JSON = os.path.join(DATA_DIR, 'law_firm_full.json')        # 个人版（全量）

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

MAX_AGE_DAYS = 365   # 个人版保留一年
MAX_NEW = 25         # 每次运行最多新增（验证链接耗时）

# 香港资本市场相关性关键词（中文所文章标题/摘要匹配用）
# 纯英文关键词走整词匹配，避免 'gem' 误中 'management' 这类词
HK_KEYWORDS_CN = [
    '香港', '港股', '联交所', '港交所', 'H股', '紅籌', '红筹', 'VIE',
    '18A', '18C', '境外上市', '海外上市', '赴港', 'SPAC', '上市规则', '上市規則',
    '香港证监', '香港證監', '主板上市', '中概股回',
]
HK_KEYWORDS_EN = [
    'hkex', 'hong kong', 'hong-kong', 'hongkong', 'listing rules', 'sfc',
    'connected transaction', 'public float', 'sponsor', 'wvr',
    'digital asset', 'virtual asset', 'stablecoin',
]

# 主题分类
TOPIC_MAP = [
    (r'digital.?asset|virtual.?asset|stablecoin|token|数字资产|虛擬資產|虚拟资产|稳定币|穩定幣', '数字资产'),
    (r'public.?float|公众持股|公眾持股', '公众持股量'),
    (r'sponsor|保荐|保薦', 'IPO保荐人'),
    (r'18A|18C|生物科技|特专科技|特專科技', '特专/生物科技'),
    (r'competitiveness|wvr|weighted.?voting|secondary.?listing|第二上市|同股不同权|上市制度|上市机制|上市框架', '上市制度'),
    (r'structured.?product|结构性产品|結構性產品', '结构性产品'),
    (r'enforcement|disciplinary|纪律|紀律|处罚|處罰|执法|執法|制裁', '监管执法'),
    (r'esg|sustainab|气候|氣候|可持续|可持續', 'ESG'),
    (r'关连交易|關連交易|connected.?transaction', '关连交易'),
    (r'备案|境外发行|境外上市', '境外上市备案'),
    (r'回购|回購|buyback', '股份回购'),
    (r'内幕|內幕|insider', '内幕消息'),
]

# === 新增律所列表页源 ===
# listpage: 列表页 HTML 解析；link_re 匹配文章链接；date_re 从 URL 提取日期（可选）
LIST_SOURCES = [
    {
        'firm': '君合 (Jun He)', 'type': 'listpage',
        'pages': ['https://www.junhe.com/legal-updates?page=%d' % n for n in range(1, 7)],
        'link_re': r'href="(/legal-updates/(\d+))"',
        'base': 'https://www.junhe.com',
    },
    {
        'firm': '环球 (Global Law Office)', 'type': 'listpage',
        'pages': ['https://www.glo.com.cn/insights/prespectives/'] +
                 ['https://www.glo.com.cn/insights/prespectives/Index_%d.html' % n for n in (2, 3, 4)],
        'link_re': r'href="(/Content/(\d{4})/(\d{2})-(\d{2})/\d+\.html)"',
        'base': 'https://www.glo.com.cn',
        # 日期在 URL 里：/Content/2026/09-03/xxx.html
        'date_from_url': lambda m: '%s-%s-%s' % (m.group(2), m.group(3), m.group(4)),
    },
    {
        'firm': '中伦 (Zhong Lun)', 'type': 'listpage',
        'pages': ['https://www.zhonglun.com/research/articles'],
        'link_re': r'href="(https://www\.zhonglun\.com)?(/research/articles/(\d+)\.html)"',
        'base': 'https://www.zhonglun.com',
    },
    {
        'firm': '天元 (Tian Yuan)', 'type': 'listpage',
        'pages': ['https://www.tylaw.com.cn/news/hydc/'],
        'link_re': r'href="(/Content/(\d{4})(\d{2})(\d{2})\d{10}\.html)"',
        'base': 'https://www.tylaw.com.cn',
        'date_from_url': lambda m: '%s-%s-%s' % (m.group(2), m.group(3), m.group(4)),
    },
]

SITEMAP_SOURCES = [
    # 方达内容类型：details32=洞察文章、details31=洞察报告；details3=团队、details34=业绩新闻（不收）
    {'firm': '方达 (Fangda Partners)', 'type': 'sitemap',
     'url': 'https://www.fangdalaw.com/sitemap.xml', 'path_filter': r'/content/details(31|32)_\d+\.html'},
]


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    # 尽量正确解码
    for enc in ('utf-8', 'gb18030'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('utf-8', errors='ignore')


def normalize_url(url):
    u = (url or '').strip().lower().rstrip('/')
    u = re.sub(r'^(https?://[^/]+)/(?:zh|en|tc|sc|zh-hk|zh-cn|zh-hant|zh-hans)/', r'\1/', u)
    return u


def parse_date(s):
    if not s:
        return ''
    s = s.strip()
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        return m.group(0)
    m = re.match(r'(\d{4})[./年](\d{1,2})[./月](\d{1,2})', s)
    if m:
        return '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3)))
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(s).strftime('%Y-%m-%d')
    except Exception:
        return ''


def guess_topic(text):
    for pat, topic in TOPIC_MAP:
        if re.search(pat, text, re.I):
            return topic
    return '上市监管'


def hk_relevant(text):
    t = text.lower()
    if any(k in text for k in HK_KEYWORDS_CN):
        return True
    return any(re.search(r'\b' + re.escape(k) + r'\b', t) for k in HK_KEYWORDS_EN)


# 非专业解读的标题特征（业绩新闻/团队介绍/聘任由列表页剔除）
NOT_ANALYSIS = [
    '助力', '成功协助', '成功登陆', '完成上市', '重大新闻', '_团队', '加入', '荣列', '荣获', '排名',
]


def fetch_title_date_summary(url):
    """打开文章页：返回 (title, date, summary)；打不开返回 (None, '', '')"""
    try:
        raw = http_get(url)
        m = re.search(r'<title[^>]*>(.*?)</title>', raw, re.S | re.I)
        title = ''
        if m:
            import html as html_mod
            t = html_mod.unescape(re.sub(r'\s+', ' ', m.group(1))).strip()
            t = re.split(r'\s*[-_|｜–—]\s*(?:君合|环球|中伦|天元|方达|Jun\s*He|Global|Zhong\s*Lun|Tian\s*Yuan|Fangda).*$', t, flags=re.I)[0].strip()
            # 方达标题后缀形如：标题_文章_洞察_方达律师事务所
            t = re.sub(r'(_(?:文章|洞察|重大新闻|关于|团队))*_?(?:方达|君合|环球|中伦|天元)律师事务所$', '', t).strip()
            t = re.sub(r'[_\s]*(?:重大新闻|关于|团队|方达律师事务所|君合律师事务所|环球律师事务所|中伦律师事务所|天元律师事务所)[_\s]*$', '', t).strip()
            title = t
        date = ''
        for pat in (r'article:published_time"[^>]*content="([^"]+)"',
                    r'"datePublished"\s*:\s*"([^"]+)"',
                    r'<time[^>]*datetime="([^"]+)"',
                    r'(20\d{2}[-/年.]\d{1,2}[-/月.]\d{1,2})'):
            dm = re.search(pat, raw)
            if dm:
                date = parse_date(dm.group(1))
                if date:
                    break
        # 摘要：meta description
        summary = ''
        sm = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]+)"', raw, re.I)
        if sm:
            summary = re.sub(r'\s+', ' ', sm.group(1)).strip()[:150]
        return title, date, summary
    except Exception:
        return None, '', ''


def get_sitemap_urls(url, path_filter, depth=0):
    out = []
    try:
        raw = http_get(url, timeout=60)
        if not raw.lstrip().startswith('<?xml'):
            return out
        root = ET.fromstring(raw.encode('utf-8'))
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        for sm in root.findall('sm:sitemap', ns):
            loc = sm.find('sm:loc', ns)
            if loc is not None and loc.text and depth == 0:
                out.extend(get_sitemap_urls(loc.text.strip(), path_filter, depth + 1))
        for u in root.findall('sm:url', ns):
            loc = u.find('sm:loc', ns)
            lastmod = u.find('sm:lastmod', ns)
            if loc is None or not loc.text:
                continue
            loc_t = loc.text.strip().replace('//', '/').replace('https:/', 'https://')
            if path_filter and not re.search(path_filter, loc_t):
                continue
            out.append((loc_t, lastmod.text.strip() if lastmod is not None and lastmod.text else ''))
    except Exception as e:
        print(f'  [WARN] sitemap 获取失败 {url}: {e}')
    return out


def collect_listpage(src):
    """从列表页抓文章链接，返回 [{'url','date'}]"""
    found = {}
    for page in src['pages']:
        try:
            html = http_get(page)
        except Exception as e:
            print(f"  [WARN] 列表页获取失败 {page}: {e}")
            continue
        for m in re.finditer(src['link_re'], html):
            path = m.group(2) if m.group(2) and m.group(2).startswith('/') else m.group(1)
            if not path.startswith('http'):
                path = src['base'] + path
            date = src['date_from_url'](m) if src.get('date_from_url') else ''
            found[normalize_url(path)] = {'url': path, 'date': date}
    return list(found.values())


def main():
    print(f"=== 律所全量扫描 {datetime.now(HKT).strftime('%Y-%m-%d %H:%M HKT')} ===")

    # 1. 底：同事版全量（含隐藏的 4 家）
    base_items = []
    if os.path.exists(BASE_JSON):
        with open(BASE_JSON, encoding='utf-8') as f:
            base_items = json.load(f).get('items', [])
    print(f"同事版底数: {len(base_items)}")

    # 2. 读个人版现有条目
    if os.path.exists(FULL_JSON):
        with open(FULL_JSON, encoding='utf-8') as f:
            full = json.load(f)
    else:
        full = {'items': []}
    items = full.get('items', [])
    existing = {normalize_url(i.get('url', '')) for i in items}

    cutoff = (datetime.now(HKT) - timedelta(days=MAX_AGE_DAYS)).strftime('%Y-%m-%d')

    # 合并同事版（同事版里可能有新增；过期的跳过，避免反复并入又清理）
    merged_new = 0
    for i in base_items:
        if i.get('date') and i['date'] < cutoff:
            continue
        if normalize_url(i.get('url', '')) not in existing:
            items.append(i)
            existing.add(normalize_url(i.get('url', '')))
            merged_new += 1
    print(f"从同事版并入: {merged_new}")

    # 3. 新律所源抓取
    candidates = []
    for src in LIST_SOURCES:
        links = collect_listpage(src)
        print(f"[{src['firm']}] 列表页解析 {len(links)} 篇")
        for l in links:
            if normalize_url(l['url']) in existing:
                continue
            if l.get('date') and l['date'] < cutoff:
                continue
            candidates.append({'firm': src['firm'], 'url': l['url'], 'date': l.get('date', ''), 'title': ''})
    for src in SITEMAP_SOURCES:
        urls = get_sitemap_urls(src['url'], src.get('path_filter'))
        print(f"[{src['firm']}] sitemap 解析 {len(urls)} 篇")
        for loc, lastmod in urls:
            if normalize_url(loc) in existing:
                continue
            date = parse_date(lastmod)
            if date and date < cutoff:
                continue
            candidates.append({'firm': src['firm'], 'url': loc, 'date': date, 'title': ''})

    print(f"\n候选新文章: {len(candidates)} 篇，开始验证与筛选...", flush=True)

    added = 0
    for idx, c in enumerate(candidates, 1):
        if added >= MAX_NEW:
            break
        title, page_date, summary = fetch_title_date_summary(c['url'])
        if title is None:
            print(f"  ✗ 打不开: {c['url'][:80]}")
            continue
        c['title'] = title or c['title']
        if page_date:
            c['date'] = page_date
        if c.get('date') and c['date'] < cutoff:
            continue
        # 香港资本市场相关性筛选（标题+摘要），且剔除业绩新闻/团队介绍等非解读类
        probe = c['title'] + ' ' + summary
        if any(k in c['title'] for k in NOT_ANALYSIS):
            continue
        if not hk_relevant(probe):
            continue
        c['topic'] = guess_topic(probe)
        c['summary'] = summary
        items.append(c)
        existing.add(normalize_url(c['url']))
        added += 1
        print(f"  ✓ [{c['firm'][:16]}] {c['title'][:50]}")

    # 清理过期条目
    items = [i for i in items if not i.get('date') or i['date'] >= cutoff]

    items.sort(key=lambda i: i.get('date', ''), reverse=True)
    full['items'] = items
    full['count'] = len(items)
    full['updated'] = datetime.now(HKT).isoformat()
    full['source'] = 'Law Firm Publications (full edition: 17 existing + red-circle + HK-practice firms)'

    with open(FULL_JSON, 'w', encoding='utf-8') as f:
        json.dump(full, f, ensure_ascii=False, indent=2)
    print(f"\n=== 完成：新增 {added} 篇，共 {len(items)} 篇 ===")
    return 0


if __name__ == '__main__':
    sys.exit(main())
