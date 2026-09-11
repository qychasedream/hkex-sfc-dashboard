#!/usr/bin/env python3
"""
律所监管通讯自动扫描器
- Charltons RSS 订阅源
- Bird & Bird / Davis Polk / JSM / Latham & Watkins sitemap
- 按关键词筛选 HKEX/SFC 香港上市监管相关文章
- 验证链接可打开 (HTTP 200) 后合并进 law_firm_summaries.json
- 已有人工精选条目（含中文摘要）保留不动
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
LAW_JSON = os.path.join(DATA_DIR, 'law_firm_summaries.json')

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

# 只保留最近 N 天发布的文章
MAX_AGE_DAYS = 120
# 每次运行最多新增条目数
MAX_NEW = 10

# URL 关键词（任一命中即候选）
URL_KEYWORDS = [
    'hkex', 'hong-kong-stock-exchange', 'hong-kong-listing', 'listing-rule',
    'sfc', 'public-float', 'sponsor', 'wvr', 'weighted-voting',
    'digital-asset', 'virtual-asset', 'stablecoin', 'ipo',
]

# 主题自动分类（按 URL/标题关键词）
TOPIC_MAP = [
    (r'digital.?asset|virtual.?asset|stablecoin|token', '数字资产'),
    (r'public.?float', '公众持股量'),
    (r'sponsor|ipo', 'IPO保荐人'),
    (r'competitiveness|wvr|weighted.?voting|secondary.?listing|listing.?framework|listing.?regime', '上市竞争力'),
    (r'structured.?product|chapter.?15a', '结构性产品'),
    (r'enforcement|disciplinary|fine|sanction', '监管执法'),
    (r'esg|sustainab', 'ESG'),
    (r'disciplinary|delisting|suspension', '纪律处分'),
]

SOURCES = [
    {'firm': 'Charltons (易周律师行)', 'type': 'rss', 'url': 'https://www.charltonslaw.com/feed/'},
    {'firm': 'Bird & Bird (鸿鹄)', 'type': 'sitemap', 'url': 'https://www.twobirds.com/sitemap.xml',
     'path_filter': r'/en/insights/'},
    {'firm': 'Davis Polk', 'type': 'sitemap', 'url': 'https://www.davispolk.com/sitemap.xml',
     'path_filter': r'/insights/'},
    {'firm': 'JSM (孖士打)', 'type': 'sitemap', 'url': 'https://www.jsm.com/sitemap.xml',
     'path_filter': r'/publications/'},
    {'firm': 'Latham & Watkins (瑞生)', 'type': 'sitemap', 'url': 'https://www.lw.com/sitemap.xml',
     'path_filter': r'/insights/'},
]


def http_get(url, timeout=40):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def normalize_url(url):
    """URL 归一化：去掉语言前缀（/zh/ /en/ 等），同一篇文章的中英文页视为同一条"""
    u = (url or '').strip().lower().rstrip('/')
    u = re.sub(r'^(https?://[^/]+)/(?:zh|en|tc|sc|zh-hk|zh-cn|zh-hant|zh-hans)/', r'\1/', u)
    return u


def parse_date(s):
    """尽力解析日期为 YYYY-MM-DD"""
    if not s:
        return ''
    s = s.strip()
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        return m.group(0)
    # RFC 822 (RSS pubDate): Mon, 28 Jul 2026 09:00:00 +0000
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


def get_sitemap_urls(url, path_filter, depth=0):
    """解析 sitemap（支持 sitemap index 递归一层），返回 [(loc, lastmod), ...]"""
    out = []
    try:
        raw = http_get(url, timeout=60)
        if not raw.lstrip().startswith(b'<?xml'):
            print(f'  [跳过] {url} 非 XML')
            return out
        root = ET.fromstring(raw)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        # sitemap index → 递归抓子 sitemap（仅限可能含文章路径的）
        for sm in root.findall('sm:sitemap', ns):
            loc = sm.find('sm:loc', ns)
            if loc is not None and loc.text and depth == 0:
                if re.search(r'post|publication|insight|article|news|pub', loc.text, re.I):
                    out.extend(get_sitemap_urls(loc.text.strip(), path_filter, depth + 1))
        for u in root.findall('sm:url', ns):
            loc = u.find('sm:loc', ns)
            lastmod = u.find('sm:lastmod', ns)
            if loc is None or not loc.text:
                continue
            loc_t = loc.text.strip()
            if path_filter and not re.search(path_filter, loc_t):
                continue
            out.append((loc_t, lastmod.text.strip() if lastmod is not None and lastmod.text else ''))
    except Exception as e:
        print(f'  [WARN] sitemap 获取失败 {url}: {e}')
    return out


def get_rss_items(url):
    """解析 RSS，返回 [(title, link, date), ...]"""
    out = []
    try:
        root = ET.fromstring(http_get(url))
        for item in root.iter('item'):
            title = item.findtext('title') or ''
            link = item.findtext('link') or ''
            pub = item.findtext('pubDate') or ''
            out.append((title.strip(), link.strip(), parse_date(pub)))
    except Exception as e:
        print(f'  [WARN] RSS 获取失败 {url}: {e}')
    return out


def fetch_title_and_date(url):
    """验证链接可打开并提取页面标题与发布日期；
    返回 (title, date)；打不开返回 (None, '')，标题无效返回 ('', '')"""
    try:
        raw = http_get(url, timeout=30).decode('utf-8', errors='ignore')
        m = re.search(r'<title[^>]*>(.*?)</title>', raw, re.S | re.I)
        title = ''
        if m:
            import html as html_mod
            t = html_mod.unescape(re.sub(r'\s+', ' ', m.group(1))).strip()
            # 去掉站点名后缀（中英文）
            t = re.split(r'\s*[|｜–—-]\s*(?:Charltons|Bird|Davis|Latham|Morgan|Norton|JSM|Mayer|孖士打|汉坤|漢坤|何韋|易周).*$', t)[0].strip()
            # 拒绝通用标题（如纯所名 "Bird & Bird"）
            if len(t) >= 15 and not re.fullmatch(r'[A-Za-z &]+', t):
                title = t
        # 提取真实发布日期（优先页面 meta，而非 sitemap 的 lastmod）
        date = ''
        for pat in (r'article:published_time"[^>]*content="([^"]+)"',
                    r'"datePublished"\s*:\s*"([^"]+)"',
                    r'<time[^>]*datetime="([^"]+)"'):
            dm = re.search(pat, raw)
            if dm:
                date = parse_date(dm.group(1))
                if date:
                    break
        return title, date
    except Exception:
        return None, ''  # 打不开


def main():
    print(f"=== 律所通讯扫描 {datetime.now(HKT).strftime('%Y-%m-%d %H:%M HKT')} ===")

    # 读取现有条目
    if os.path.exists(LAW_JSON):
        with open(LAW_JSON, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {'items': []}
    items = data.get('items', [])
    existing_urls = {normalize_url(i.get('url', '')) for i in items}
    print(f"现有条目: {len(items)}")

    cutoff = (datetime.now(HKT) - timedelta(days=MAX_AGE_DAYS)).strftime('%Y-%m-%d')
    candidates = []

    for src in SOURCES:
        firm = src['firm']
        if src['type'] == 'rss':
            entries = get_rss_items(src['url'])
            print(f"[{firm}] RSS 获取 {len(entries)} 条")
            for title, link, date in entries:
                text = f'{title} {link}'
                if not any(k in text.lower() for k in URL_KEYWORDS):
                    continue
                if normalize_url(link) in existing_urls:
                    continue
                if date and date < cutoff:
                    continue
                candidates.append({'firm': firm, 'title': title, 'url': link, 'date': date})
        else:
            urls = get_sitemap_urls(src['url'], src.get('path_filter'))
            print(f"[{firm}] sitemap 解析 {len(urls)} 个 URL")
            for loc, lastmod in urls:
                if not any(k in loc.lower() for k in URL_KEYWORDS):
                    continue
                if normalize_url(loc) in existing_urls:
                    continue
                date = parse_date(lastmod)
                if date and date < cutoff:
                    continue
                candidates.append({'firm': firm, 'title': '', 'url': loc, 'date': date})

    # 同一文章的中英文页面（/zh/ 与英文路径）合并为一条，优先中文版
    grouped = {}
    for c in candidates:
        key = normalize_url(c['url'])
        if key not in grouped or '/zh/' in c['url'].lower():
            grouped[key] = c
    candidates = list(grouped.values())

    print(f"\n候选新文章: {len(candidates)} 篇，开始验证链接...", flush=True)

    added = 0
    for idx, c in enumerate(candidates, 1):
        if added >= MAX_NEW:
            break
        print(f"  验证中 ({idx}/{len(candidates)})...", flush=True)
        title, page_date = fetch_title_and_date(c['url'])
        if title is None:
            print(f"  ✗ 打不开: {c['url'][:80]}")
            continue
        if not c['title']:
            c['title'] = title
        # 标题无效（通用名/太短）则跳过
        if not c['title'] or len(c['title']) < 15:
            continue
        # 优先使用页面上的真实发布日期（sitemap 的 lastmod 可能只是页面被编辑的时间）
        if page_date:
            c['date'] = page_date
        if c.get('date') and c['date'] < cutoff:
            continue
        # 用标题再校验一次相关性（避免 sitemap URL 误匹配）
        if not any(k in (c['title'] + ' ' + c['url']).lower() for k in URL_KEYWORDS):
            continue
        c['topic'] = guess_topic(c['url'] + ' ' + c['title'])
        c['summary'] = ''  # 自动收录条目暂无中文摘要，卡片显示原标题
        items.append(c)
        added += 1
        print(f"  ✓ [{c['firm'][:20]}] {c['title'][:60]}")

    # 按日期倒序
    items.sort(key=lambda i: i.get('date', ''), reverse=True)
    data['items'] = items
    data['count'] = len(items)
    data['updated'] = datetime.now(HKT).isoformat()
    data['source'] = 'Verified Law Firm Publications (curated + auto-scan)'

    with open(LAW_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n=== 完成：新增 {added} 篇，共 {len(items)} 篇 ===")
    return 0


if __name__ == '__main__':
    sys.exit(main())
