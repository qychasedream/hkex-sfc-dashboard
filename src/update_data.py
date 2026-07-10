#!/usr/bin/env python3
"""
SFC / HKEX 数据自动更新脚本
- 从 SFC API 抓取最新新闻稿和通函
- 从 HKEX 规则手册抓取指引文件更新
- 生成 JSON 数据供看板使用
- 由 GitHub Actions 每日自动执行
"""

import urllib.request
import urllib.error
import json
import re
import os
import sys
import io
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# === 配置 ===
HKT = timezone(timedelta(hours=8))
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; HKRegulatoryDashboard/1.0)',
    'Content-Type': 'application/json'
}


def fetch_sfc_news():
    """从 SFC e-Distribution API 获取最新新闻稿"""
    print("[SFC] 获取新闻稿...")
    url = 'https://apps.sfc.hk/edistributionWeb/api/news/search'

    all_items = []
    for page in range(3):  # 获取最近3页 (约30条)
        body = json.dumps({
            "pageNo": page,
            "pageSize": 30,
            "lang": "TC",
            "searchMode": "by-year",
            "year": str(datetime.now(HKT).year)
        }).encode('utf-8')

        try:
            req = urllib.request.Request(url, data=body, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))

            if 'items' in result and result['items']:
                for item in result['items']:
                    ref_no = item.get('newsRefNo', '') or item.get('refNo', '')
                    all_items.append({
                        'refNo': ref_no,
                        'title': item.get('title', ''),
                        'type': 'enforcement' if item.get('newsType') == 'EF' else 'general',
                        'date': (item.get('issueDate', '') or '')[:10],
                        'url': f"https://apps.sfc.hk/edistributionWeb/gateway/TC/news-and-announcements/news/doc?refNo={ref_no}"
                    })
        except Exception as e:
            print(f"  [WARN] 第{page}页获取失败: {e}")

    print(f"  ✓ 共获取 {len(all_items)} 条新闻")
    return all_items


def fetch_sfc_circulars():
    """从 SFC API 获取最新通函"""
    print("[SFC] 获取通函...")
    url = 'https://apps.sfc.hk/edistributionWeb/api/circular/search'

    all_items = []
    body = json.dumps({
        "pageNo": 0,
        "pageSize": 20,
        "lang": "TC"
    }).encode('utf-8')

    try:
        req = urllib.request.Request(url, data=body, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))

        if 'items' in result and result['items']:
            for item in result['items']:
                ref_no = item.get('circularRefNo', '') or item.get('refNo', '')
                all_items.append({
                    'refNo': ref_no,
                    'title': item.get('title', ''),
                    'date': (item.get('issueDate', '') or '')[:10],
                    'url': f"https://apps.sfc.hk/edistributionWeb/gateway/TC/circular/doc?refNo={ref_no}"
                })
    except Exception as e:
        print(f"  [WARN] 通函获取失败: {e}")

    print(f"  ✓ 共获取 {len(all_items)} 条通函")
    return all_items


def fetch_hkex_guidance():
    """从 HKEX 规则手册抓取指引文件更新"""
    print("[HKEX] 检查指引文件...")

    topics = [
        (1, 12800, "董事及高級管理人員"),
        (2, 12801, "合規顧問和其他專業顧問"),
        (3, 12802, "會計及審計事宜"),
        (4, 12803, "短暫停牌、停牌、除牌及撤回上市"),
        (5, 12805, "繼續上市準則"),
        (6, 12807, "發行證券或再出售庫存股份及相關事宜"),
        (7, 12806, "公眾持股量"),
        (8, 13507, "由GEM轉往主板上市"),
        (9, 12808, "股份購回及庫存股份"),
        (10, 12804, "持續責任"),
        (11, 12809, "須予公布的交易"),
        (12, 12810, "關連交易"),
        (13, 13505, "股份計劃"),
        (14, 12812, "特別上市制度或其他上市架構"),
        (15, 12811, "分拆上市"),
        (16, 13508, "核心的股東保障水平"),
        (17, 13509, "企業管治 / 環境、社會及管治 / 董事進行證券交易"),
        (18, 12813, "其他主題"),
    ]

    this_year = str(datetime.now(HKT).year)
    last_year = str(datetime.now(HKT).year - 1)
    recent_updates = []

    for num, nid, name in topics:
        try:
            url = f'https://cn-rules.hkex.com.hk/node/{nid}'
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                html = resp.read().decode('utf-8')

            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
            for row in rows:
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                if len(cells) >= 4:
                    detail_html = cells[0]
                    ref = re.sub(r'<[^>]+>', '', cells[2]).strip()
                    date_str = re.sub(r'<[^>]+>', '', cells[3]).strip()

                    # 跳过表头行（有背景色或空引用）
                    if 'background-color' in detail_html or not ref:
                        continue
                    # 跳过列标题行（参考编号为纯HTML空格的占位行）
                    if ref in ('&nbsp;', '參考編號', '出版日期', 'Reference', 'Publication Date'):
                        continue
                    # 跳过 section 标题行（ref 以纯数字+点开头如 "1.1 "，"2.1 "）
                    if re.match(r'^\d+\.\d+', ref):
                        continue

                    # 判断是否为指引信 (GL-xxx 格式)
                    is_guidance_letter = bool(re.match(r'^GL\d+', ref))

                    # 日期匹配：当年更新 或 上年更新 或 指引信始终收录
                    date_ok = this_year in date_str or last_year in date_str
                    if not date_ok and not is_guidance_letter:
                        continue

                    detail = re.sub(r'<[^>]+>', '', detail_html).strip()
                    link_match = re.search(r'href="([^"]+)"', detail_html)
                    doc_url = ''
                    if link_match:
                        doc_url = link_match.group(1)
                        if doc_url.startswith('/'):
                            doc_url = 'https://cn-rules.hkex.com.hk' + doc_url

                    # 确定文档类型
                    doc_type = 'guidance_letter' if is_guidance_letter else 'faq'

                    recent_updates.append({
                        'topic': name,
                        'ref': ref,
                        'detail': detail,
                        'date': date_str.replace('\n', ' ').strip(),
                        'url': doc_url,
                        'topicUrl': f'https://cn-rules.hkex.com.hk/node/{nid}',
                        'docType': doc_type
                    })
        except Exception as e:
            print(f"  [WARN] 主题{num}获取失败: {e}")

    print(f"  ✓ {this_year}/{last_year}年更新: {len(recent_updates)} 项")
    return recent_updates


def fetch_hkex_regulatory_announcements():
    """从 HKEX RSS Feed 获取监管通讯 (Regulatory Announcements)"""
    print("[HKEX] 获取监管通讯 (RSS)...")
    url = 'https://www.hkex.com.hk/Services/RSS-Feeds/regulatory-announcements?sc_lang=zh-HK'

    items = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            rss_xml = resp.read().decode('utf-8')

        root = ET.fromstring(rss_xml)
        channel = root.find('channel')
        if channel is None:
            print("  [WARN] RSS 中没有 channel 元素")
            return items

        for item in channel.findall('item'):
            title_el = item.find('title')
            link_el = item.find('link')
            pubdate_el = item.find('pubDate')
            desc_el = item.find('description')
            guid_el = item.find('guid')

            title = title_el.text.strip() if title_el is not None and title_el.text else ''
            link = link_el.text.strip() if link_el is not None and link_el.text else ''
            pubdate = pubdate_el.text.strip() if pubdate_el is not None and pubdate_el.text else ''
            description = desc_el.text.strip() if desc_el is not None and desc_el.text else ''

            # 跳过占位条目（如年度归档链接 "2026", "2025" 等纯数字标题）
            if re.match(r'^\d{4}\s*$', title):
                continue
            if not link or not title:
                continue

            # 自动分类
            category = 'other'
            if '紀律行動' in title:
                category = 'disciplinary'
            elif re.search(r'諮詢總結|諮詢文件|諮詢市場意見', title):
                category = 'consultation'
            elif re.search(r'取消上市|除牌', title):
                category = 'enforcement_news'
            elif re.search(r'刊發.*報告|刊發.*指引|修訂|規則|上市委員會|上市提名|結構性產品|上市機制', title):
                category = 'regulatory_rule'

            # 解析日期
            date_str = ''
            if pubdate:
                try:
                    dt = datetime.strptime(pubdate, '%a, %d %b %Y %H:%M:%S %z')
                    date_str = dt.strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        dt = datetime.strptime(pubdate, '%a, %d %b %Y %H:%M:%S %Z')
                        date_str = dt.strftime('%Y-%m-%d')
                    except ValueError:
                        date_str = pubdate[:16] if len(pubdate) >= 16 else pubdate

            items.append({
                'title': title,
                'url': link,
                'date': date_str,
                'description': description,
                'category': category
            })

    except Exception as e:
        print(f"  [WARN] 监管通讯 RSS 获取失败: {e}")

    print(f"  ✓ 共获取 {len(items)} 条监管通讯")
    return items


def fetch_hkex_news_releases():
    """从 HKEX RSS Feed 获取新闻稿，过滤监管相关内容"""
    print("[HKEX] 获取新闻稿 (RSS, 过滤监管相关)...")
    url = 'https://www.hkex.com.hk/Services/RSS-Feeds/News-Releases?sc_lang=zh-HK'

    # 监管相关关键词（繁体中文）
    regulatory_keywords = [
        '上市', '監管', '紀律', '合規', '指數', '期貨', '期權',
        '交易', '結算', '風險管理', '董事', '治理', 'ESG',
        '披露', '市場', '規則', '諮詢', '指引', '結構性',
        'Listing', 'ETF', 'IPO', 'MOU', 'Stock Connect',
        'Futures', 'Options', 'Clearing', 'Risk',
    ]

    items = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            rss_xml = resp.read().decode('utf-8')

        root = ET.fromstring(rss_xml)
        channel = root.find('channel')
        if channel is None:
            print("  [WARN] RSS 中没有 channel 元素")
            return items

        for item in channel.findall('item'):
            title_el = item.find('title')
            link_el = item.find('link')
            pubdate_el = item.find('pubDate')
            desc_el = item.find('description')

            title = title_el.text.strip() if title_el is not None and title_el.text else ''
            link = link_el.text.strip() if link_el is not None and link_el.text else ''
            pubdate = pubdate_el.text.strip() if pubdate_el is not None and pubdate_el.text else ''
            description = desc_el.text.strip() if desc_el is not None and desc_el.text else ''

            # 跳过占位条目
            if re.match(r'^\d{4}\s*$', title):
                continue
            if not link or not title:
                continue

            # 法规监管相关性过滤
            is_regulatory = any(kw.lower() in title.lower() for kw in regulatory_keywords)
            if not is_regulatory:
                continue

            # 分类
            category = 'general'
            if re.search(r'紀律|合規|監管|風險管理', title):
                category = 'regulatory_rule'
            elif re.search(r'指數|期貨|期權|ETF', title):
                category = 'general'

            # 解析日期
            date_str = ''
            if pubdate:
                try:
                    dt = datetime.strptime(pubdate, '%a, %d %b %Y %H:%M:%S %z')
                    date_str = dt.strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        dt = datetime.strptime(pubdate, '%a, %d %b %Y %H:%M:%S %Z')
                        date_str = dt.strftime('%Y-%m-%d')
                    except ValueError:
                        date_str = pubdate[:16] if len(pubdate) >= 16 else pubdate

            items.append({
                'title': title,
                'url': link,
                'date': date_str,
                'description': description,
                'category': category
            })

    except Exception as e:
        print(f"  [WARN] 新闻稿 RSS 获取失败: {e}")

    print(f"  ✓ 共获取 {len(items)} 条监管相关新闻稿")
    return items


def fetch_hkex_guidance_archive():
    """从 HKEX 指引信档案页抓取所有指引信（含结构性产品、债务证券等）"""
    print("[HKEX] 获取指引信档案 (hkex.com.hk)...")
    url = 'https://www.hkex.com.hk/Listing/Rules-and-Resources/Archive/Guidance-Letters?sc_lang=zh-HK'

    items = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8')

        # Parse table rows with role="row"
        rows = re.findall(r'<tr[^>]*role=\"row\"[^>]*>(.*?)</tr>', html, re.DOTALL)
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) >= 4:
                # Column 0: dates
                date_html = cells[0]
                # Prepend '>' to capture text before first <br /> tag
                date_html = '>' + date_html
                dates = re.findall(r'>([^<]+)<', date_html)
                # dates format: ['05/2015', '(31/12/2025)'] or ['(01/01/2024)'] or ['25/05/2018', '(31/12/2025)']
                first_date = ''
                update_date_raw = ''
                for d in dates:
                    d = d.strip()
                    if not d:
                        continue
                    if d.startswith('(') and d.endswith(')'):
                        update_date_raw = d.strip('()（） ')
                    elif re.match(r'\d', d):
                        if not first_date:
                            first_date = d
                        elif not update_date_raw:
                            update_date_raw = d.strip('()（） ')
                # If only one date and it's in parens-like format
                if not update_date_raw:
                    update_date_raw = first_date.strip('()（） ') if first_date.startswith('(') else ''
                    if update_date_raw:
                        first_date = ''

                # Column 1: title + PDF link
                title_html = cells[1]
                link_match = re.search(r'href=\"([^\"]+)\"', title_html)
                pdf_url = ''
                if link_match:
                    pdf_url = link_match.group(1)
                    if pdf_url.startswith('/'):
                        pdf_url = 'https://www.hkex.com.hk' + pdf_url

                # Extract title text and GL number
                title_text = re.sub(r'<[^>]+>', ' ', title_html).strip()
                title_text = re.sub(r'\s+', ' ', title_text)
                gl_match = re.search(r'GL\d+[-–—]\d+', title_text)
                gl_ref = gl_match.group(0) if gl_match else ''

                # Column 2: document type
                doc_type_text = re.sub(r'<[^>]+>', '', cells[2]).strip()

                # Column 3: category
                category_text = re.sub(r'<[^>]+>', '', cells[3]).strip()

                if not title_text or not gl_ref:
                    continue

                # Use update_date_raw (could be empty)
                update_date = update_date_raw

                # Parse update date into YYYY-MM-DD format
                date_str = ''
                if update_date:
                    # Try DD/MM/YYYY format first, then MM/YYYY
                    date_match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', update_date)
                    if date_match:
                        date_str = f'{date_match.group(3)}-{date_match.group(2).zfill(2)}-01'
                    else:
                        date_match = re.match(r'(\d{1,2})/(\d{4})', update_date)
                        if date_match:
                            date_str = f'{date_match.group(2)}-{date_match.group(1).zfill(2)}-01'

                items.append({
                    'gl_ref': gl_ref,
                    'title': title_text,
                    'url': pdf_url,
                    'first_date': first_date,
                    'update_date': update_date,
                    'date': date_str,
                    'doc_type': doc_type_text,
                    'category': category_text
                })

    except Exception as e:
        print(f"  [WARN] 指引信档案获取失败: {e}")

    print(f"  ✓ 共获取 {len(items)} 条指引信")
    return items


def fetch_hkex_via_claude():
    """使用 Claude API web_search 抓取 HKEX 最新消息页面（JS渲染页面）"""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("[HKEX] Claude API: 未设置 ANTHROPIC_API_KEY，跳过")
        return []

    try:
        import anthropic
    except ImportError:
        print("[HKEX] Claude API: anthropic SDK 未安装，跳过")
        return []

    print("[HKEX] Claude API: 搜索 HKEX 最新消息...")
    client = anthropic.Anthropic(api_key=api_key)

    prompt = """Search the HKEX "What's New" listing page at:
https://www.hkex.com.hk/Listing/News-and-Publications/Whats-New?sc_lang=zh-HK

Also search for recent listing-related announcements from HKEX in the past 7 days.

Find ALL new/updated items including:
- Listing Rule amendments
- Guidance Letters (GL-xxx)
- FAQs / Frequently Asked Questions
- Consultation Papers and Conclusions
- Listing Committee decisions and reports
- Disciplinary actions
- Any other listing-related publications

For each item extract:
- title (in Chinese)
- url (the official HKEX link)
- date (in YYYY-MM-DD format)
- category: one of [disciplinary, consultation, regulatory_rule, enforcement_news]

Return as JSON: {"items": [{"title": "...", "url": "...", "date": "...", "category": "...", "relevance_score": 8}, ...]}
Only include items from OFFICIAL HKEX sources (hkex.com.hk)."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=[
                {"type": "web_search_20260209", "name": "web_search", "max_uses": 10},
                {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": 8},
            ],
            messages=[{"role": "user", "content": prompt}],
        )

        items = []
        for block in response.content:
            if hasattr(block, 'type') and block.type == "text":
                try:
                    data = json.loads(block.text)
                    raw_items = data.get("items", []) if isinstance(data, dict) else data
                    for raw in raw_items:
                        if raw.get("relevance_score", 0) >= 6 and raw.get("url"):
                            items.append({
                                "title": raw.get("title", ""),
                                "url": raw.get("url", ""),
                                "date": raw.get("date", ""),
                                "category": raw.get("category", "other"),
                            })
                except json.JSONDecodeError:
                    continue

        print(f"  ✓ Claude API: 获取 {len(items)} 条")
        return items
    except Exception as e:
        print(f"  [WARN] Claude API 失败: {e}")
        return []


def save_json(data, filename, skip_empty=True):
    """保存 JSON 文件（skip_empty: 无数据时不覆盖已有文件）"""
    filepath = os.path.join(DATA_DIR, filename)
    count = data.get('count', 0)
    if skip_empty and count == 0:
        print(f"  → 跳过: {filename} (无数据，保留已有文件)")
        return
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  → 已保存: {filename}")


def main():
    print(f"=== 监管数据更新 {datetime.now(HKT).strftime('%Y-%m-%d %H:%M HKT')} ===\n")

    # 1. SFC 新闻稿
    sfc_news = fetch_sfc_news()
    save_json({
        'updated': datetime.now(HKT).isoformat(),
        'source': 'SFC e-Distribution API',
        'count': len(sfc_news),
        'items': sfc_news
    }, 'sfc_news.json')

    # 2. SFC 通函
    sfc_circulars = fetch_sfc_circulars()
    save_json({
        'updated': datetime.now(HKT).isoformat(),
        'source': 'SFC e-Distribution API',
        'count': len(sfc_circulars),
        'items': sfc_circulars
    }, 'sfc_circulars.json')

    # 3. HKEX 指引文件 (FAQ + Guidance Letters)
    hkex_updates = fetch_hkex_guidance()
    save_json({
        'updated': datetime.now(HKT).isoformat(),
        'source': 'HKEX 规则手册',
        'count': len(hkex_updates),
        'items': hkex_updates
    }, 'hkex_guidance_updates.json')

    # 4. HKEX 监管通讯 (RSS)
    hkex_reg = fetch_hkex_regulatory_announcements()
    save_json({
        'updated': datetime.now(HKT).isoformat(),
        'source': 'HKEX Regulatory Announcements RSS',
        'count': len(hkex_reg),
        'items': hkex_reg
    }, 'hkex_regulatory_announcements.json')

    # 5. HKEX 新闻稿 (RSS, 过滤监管相关)
    hkex_news = fetch_hkex_news_releases()
    save_json({
        'updated': datetime.now(HKT).isoformat(),
        'source': 'HKEX News Releases RSS (filtered)',
        'count': len(hkex_news),
        'items': hkex_news
    }, 'hkex_news_releases.json')

    # 6. HKEX 指引信档案 (全面抓取，含结构性产品)
    hkex_gl_archive = fetch_hkex_guidance_archive()
    save_json({
        'updated': datetime.now(HKT).isoformat(),
        'source': 'HKEX 指引信档案',
        'count': len(hkex_gl_archive),
        'items': hkex_gl_archive
    }, 'hkex_guidance_archive.json')

    # 7. HKEX 最新消息 (Claude API web_search, 可选)
    hkex_claude = fetch_hkex_via_claude()
    save_json({
        'updated': datetime.now(HKT).isoformat(),
        'source': 'HKEX Claude API Search',
        'count': len(hkex_claude),
        'items': hkex_claude
    }, 'hkex_claude_search.json')

    # 8. 元数据 (记录本次更新)
    save_json({
        'lastUpdate': datetime.now(HKT).isoformat(),
        'stats': {
            'sfcNews': len(sfc_news),
            'sfcCirculars': len(sfc_circulars),
            'hkexGuidanceUpdates': len(hkex_updates),
            'hkexRegulatory': len(hkex_reg),
            'hkexNews': len(hkex_news),
            'hkexGLArchive': len(hkex_gl_archive),
            'hkexClaude': len(hkex_claude)
        }
    }, 'update_meta.json', skip_empty=False)

    print(f"\n=== 更新完成 ===")
    return 0


if __name__ == '__main__':
    sys.exit(main())
