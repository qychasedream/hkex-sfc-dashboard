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

                    if 'background-color' in detail_html or not ref:
                        continue
                    if re.match(r'^\d+\.\d+\s', ref):
                        continue

                    if this_year in date_str:
                        detail = re.sub(r'<[^>]+>', '', detail_html).strip()
                        link_match = re.search(r'href="([^"]+)"', detail_html)
                        doc_url = ''
                        if link_match:
                            doc_url = link_match.group(1)
                            if doc_url.startswith('/'):
                                doc_url = 'https://cn-rules.hkex.com.hk' + doc_url

                        recent_updates.append({
                            'topic': name,
                            'ref': ref,
                            'detail': detail,
                            'date': date_str.replace('\n', ' ').strip(),
                            'url': doc_url,
                            'topicUrl': f'https://cn-rules.hkex.com.hk/node/{nid}'
                        })
        except Exception as e:
            print(f"  [WARN] 主题{num}获取失败: {e}")

    print(f"  ✓ {this_year}年更新: {len(recent_updates)} 项")
    return recent_updates


def save_json(data, filename):
    """保存 JSON 文件"""
    filepath = os.path.join(DATA_DIR, filename)
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

    # 3. HKEX 指引文件
    hkex_updates = fetch_hkex_guidance()
    save_json({
        'updated': datetime.now(HKT).isoformat(),
        'source': 'HKEX 规则手册',
        'count': len(hkex_updates),
        'items': hkex_updates
    }, 'hkex_guidance_updates.json')

    # 4. 元数据 (记录本次更新)
    save_json({
        'lastUpdate': datetime.now(HKT).isoformat(),
        'stats': {
            'sfcNews': len(sfc_news),
            'sfcCirculars': len(sfc_circulars),
            'hkexGuidanceUpdates': len(hkex_updates)
        }
    }, 'update_meta.json')

    print(f"\n=== 更新完成 ===")
    return 0


if __name__ == '__main__':
    sys.exit(main())
