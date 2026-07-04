"""专业级静态 HTML 看板生成器 — 简体中文界面。"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .models import RegulatoryItem, ItemCategory

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #f4f2ef;
  --surface: #ffffff;
  --surface-alt: #f7f5f1;
  --primary: #1B365D;
  --primary-light: #2C4F7A;
  --accent: #B8860B;
  --accent-light: #f5f0e0;
  --text: #2C2C2C;
  --text-secondary: #5A5A5A;
  --text-muted: #8C8C8C;
  --border: #e0dcd5;
  --danger: #B85450;
  --danger-bg: #faf4f3;
  --info: #2E6B8F;
  --info-bg: #f2f6f9;
  --success: #4A8C6F;
  --success-bg: #f2f7f4;
  --warning: #C8963E;
  --warning-bg: #faf7f2;
  --shadow-sm: 0 1px 2px rgba(0,0,0,.04);
  --shadow-md: 0 4px 12px rgba(0,0,0,.05);
  --shadow-lg: 0 8px 24px rgba(0,0,0,.07);
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
}}

* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: 'Noto Sans SC', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}}

/* Navigation */
.nav {{
  background: var(--primary);
  color: #fff;
  padding: 0 32px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 8px rgba(0,0,0,.15);
}}
.nav-brand {{
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 1.05em;
  letter-spacing: .01em;
}}
.nav-brand .icon {{ font-size: 1.4em; }}
.nav-right {{ font-size: .85em; opacity: .75; }}

.container {{ max-width: 1160px; margin: 0 auto; padding: 32px 24px 48px; }}

/* Page Header */
.page-header {{ margin-bottom: 32px; }}
.page-header .period-badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--accent-light);
  color: #8b6914;
  font-size: .82em;
  font-weight: 600;
  padding: 6px 14px;
  border-radius: 20px;
  margin-bottom: 12px;
}}
.page-header h1 {{
  font-size: 1.9em;
  font-weight: 700;
  color: var(--primary);
  letter-spacing: .02em;
  margin-bottom: 6px;
}}
.page-header .subtitle {{
  font-size: .95em;
  color: var(--text-secondary);
}}

/* Stats Row */
.stats-row {{
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
  margin-bottom: 32px;
}}
@media (max-width: 900px) {{ .stats-row {{ grid-template-columns: repeat(3, 1fr); }} }}
@media (max-width: 600px) {{ .stats-row {{ grid-template-columns: repeat(2, 1fr); }} }}

.stat-card {{
  background: var(--surface);
  border-radius: var(--radius-md);
  padding: 22px 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  transition: box-shadow .2s, transform .2s;
  cursor: default;
}}
.stat-card:hover {{ box-shadow: var(--shadow-md); transform: translateY(-2px); }}
.stat-card .stat-icon {{
  width: 40px; height: 40px;
  border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2em;
  margin-bottom: 12px;
}}
.stat-card .stat-count {{ font-size: 2.2em; font-weight: 700; line-height: 1; margin-bottom: 4px; }}
.stat-card .stat-label {{ font-size: .85em; color: var(--text-secondary); }}
.stat-card.total {{
  background: var(--primary); color: #fff; border-color: var(--primary);
}}
.stat-card.total .stat-label {{ color: rgba(255,255,255,.7); }}

/* Section */
.section {{ margin-bottom: 40px; }}
.section-header {{
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 18px; padding-bottom: 14px;
  border-bottom: 2px solid var(--border);
}}
.section-header .dot {{
  width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0;
}}
.section-header h2 {{ font-size: 1.25em; font-weight: 700; color: var(--primary); flex: 1; }}
.section-header .count-tag {{
  font-size: .82em; background: var(--surface-alt);
  color: var(--text-secondary); padding: 4px 10px;
  border-radius: 12px; font-weight: 500;
}}

/* Item Card */
.item-card {{
  background: var(--surface); border-radius: var(--radius-md);
  margin-bottom: 12px; box-shadow: var(--shadow-sm);
  border: 1px solid var(--border); overflow: hidden;
  transition: box-shadow .2s;
}}
.item-card:hover {{ box-shadow: var(--shadow-md); }}
.item-card-inner {{ display: flex; gap: 0; }}
.item-accent {{ width: 5px; flex-shrink: 0; }}
.item-body {{ flex: 1; padding: 18px 22px; min-width: 0; }}
.item-top {{
  display: flex; justify-content: space-between;
  align-items: flex-start; gap: 14px; flex-wrap: wrap;
}}
.item-title-group {{ flex: 1; min-width: 260px; }}
.item-title {{
  font-size: 1.05em; font-weight: 700; color: var(--text);
  line-height: 1.5; margin-bottom: 6px;
}}
.item-title a {{ color: inherit; text-decoration: none; transition: color .15s; }}
.item-title a:hover {{ color: var(--primary-light); }}
.item-meta {{
  display: flex; gap: 8px; align-items: center;
  flex-wrap: wrap; flex-shrink: 0;
}}
.tag {{
  display: inline-flex; align-items: center; gap: 4px;
  padding: 4px 10px; border-radius: 6px;
  font-size: .76em; font-weight: 600;
  white-space: nowrap; letter-spacing: .01em;
}}
.tag-source {{ border: 1px solid; background: #fff; }}
.tag-category {{ color: #fff; }}
.tag-date {{
  background: var(--surface-alt); color: var(--text-secondary);
  border: 1px solid var(--border);
}}
.item-summary {{
  margin-top: 12px; font-size: .92em;
  color: var(--text-secondary); line-height: 1.75;
}}
.item-bottom {{
  margin-top: 14px; display: flex; justify-content: space-between;
  align-items: center; flex-wrap: wrap; gap: 10px;
  padding-top: 12px; border-top: 1px solid var(--border);
}}
.item-method {{
  font-size: .75em; color: var(--text-muted);
  display: flex; align-items: center; gap: 5px;
}}
.source-btn {{
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 16px; background: var(--primary); color: #fff;
  text-decoration: none; border-radius: 6px;
  font-size: .82em; font-weight: 600;
  transition: background .15s, transform .15s;
}}
.source-btn:hover {{ background: var(--primary-light); transform: translateY(-1px); }}
.source-btn .arr {{ font-size: 1.1em; }}

/* Chart */
.chart-section {{
  background: var(--surface); border-radius: var(--radius-lg);
  padding: 28px; margin-top: 40px;
  box-shadow: var(--shadow-sm); border: 1px solid var(--border);
}}
.chart-section h2 {{
  font-size: 1.2em; font-weight: 700; color: var(--primary);
  margin-bottom: 20px; display: flex; align-items: center; gap: 8px;
}}

/* Footer */
.footer {{
  margin-top: 56px; padding: 32px 0 24px;
  border-top: 1px solid var(--border); text-align: center;
}}
.footer .links {{
  display: flex; justify-content: center; gap: 24px;
  flex-wrap: wrap; margin-bottom: 16px;
}}
.footer .links a {{
  color: var(--primary-light); text-decoration: none;
  font-size: .88em; font-weight: 500;
  display: flex; align-items: center; gap: 5px;
}}
.footer .links a:hover {{ text-decoration: underline; }}
.footer .disclaimer {{
  font-size: .8em; color: var(--text-muted); line-height: 1.8;
}}

/* Empty State */
.empty-state {{
  text-align: center; padding: 56px 24px; color: var(--text-muted);
}}
.empty-state .empty-icon {{ font-size: 3em; margin-bottom: 12px; }}
.empty-state p {{ font-size: .95em; }}

/* Quick Link Bar */
.quick-bar {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 32px; }}
.quick-btn {{
  display: inline-flex; align-items: center; gap: 6px;
  padding: 10px 18px; background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  color: var(--primary); text-decoration: none;
  font-size: .85em; font-weight: 600;
  transition: all .15s; box-shadow: var(--shadow-sm);
}}
.quick-btn:hover {{
  border-color: var(--accent); background: var(--accent-light);
  box-shadow: var(--shadow-md);
}}
.quick-btn .qb-icon {{ font-size: 1.1em; }}

/* Filter Tags */
.filter-bar {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 24px; }}
.filter-tag {{
  padding: 7px 16px; border-radius: 20px;
  border: 1.5px solid var(--border); background: var(--surface);
  font-size: .84em; font-weight: 600; cursor: pointer;
  transition: all .15s; color: var(--text-secondary);
  user-select: none;
}}
.filter-tag:hover {{ border-color: var(--primary-light); color: var(--primary); }}
.filter-tag.active {{ background: var(--primary); color: #fff; border-color: var(--primary); }}
</style>
</head>
<body>

<!-- Navigation -->
<nav class="nav">
  <div class="nav-brand">
    <span class="icon">🏛️</span>
    <span>香港监管咨询看板</span>
  </div>
  <div class="nav-right">SFC · HKEX 监管动态追踪</div>
</nav>

<div class="container">

  <!-- Page Header -->
  <div class="page-header">
    <div class="period-badge">
      📅 {period_label}
    </div>
    <h1>{period_title}</h1>
    <div class="subtitle">覆盖香港证监会（SFC）及香港联交所（HKEX）官方监管公告、纪律处分、咨询总结及规则更新</div>
  </div>

  <!-- Quick Links -->
  <div class="quick-bar">
    <a href="https://apps.sfc.hk/edistributionWeb/gateway/SC/news-and-announcements/news/" target="_blank" class="quick-btn">
      <span class="qb-icon">📋</span> SFC 监管新闻
    </a>
    <a href="https://apps.sfc.hk/edistributionWeb/gateway/SC/circular/" target="_blank" class="quick-btn">
      <span class="qb-icon">📄</span> SFC 通函
    </a>
    <a href="https://www.hkex.com.hk/News/Regulatory-Announcements?sc_lang=zh-CN" target="_blank" class="quick-btn">
      <span class="qb-icon">🏢</span> HKEX 监管公告
    </a>
    <a href="https://www.hkex.com.hk/Listing/Rules-and-Guidance/Listing-Rules?sc_lang=zh-CN" target="_blank" class="quick-btn">
      <span class="qb-icon">📖</span> HKEX 上市规则
    </a>
    <a href="https://apps.sfc.hk/edistributionWeb/gateway/SC/consultation/" target="_blank" class="quick-btn">
      <span class="qb-icon">💬</span> SFC 咨询文件
    </a>
  </div>

  <!-- Stats Row -->
  <div class="stats-row">
    {stats_cards}
    <div class="stat-card total">
      <div class="stat-count">{total_count}</div>
      <div class="stat-label">公告总数</div>
    </div>
  </div>

  <!-- Filter Bar -->
  <div class="filter-bar">
    <span class="filter-tag active" data-filter="all">全部类别</span>
    {filter_tags}
  </div>

  <!-- Items by Category -->
  {sections}

  <!-- Chart -->
  <div class="chart-section">
    <h2>📊 近30天监管动态趋势</h2>
    <canvas id="trendChart" height="80"></canvas>
  </div>

  <!-- Footer -->
  <div class="footer">
    <div class="links">
      <a href="https://www.sfc.hk/SC/" target="_blank">🔗 SFC 证监会官网</a>
      <a href="https://www.hkex.com.hk/?sc_lang=zh-CN" target="_blank">🔗 HKEX 联交所官网</a>
    </div>
    <div class="disclaimer">
      <p>本看板仅供参考，不构成法律或投资建议。所有内容以监管机构官方发布为准。</p>
      <p>数据来源：香港证监会（SFC）及香港交易及结算所有限公司（HKEX）官方网站</p>
      <p>更新时间：{generated_at}</p>
    </div>
  </div>
</div>

<script>
// Filter functionality
(function() {{
  document.querySelectorAll('.filter-tag').forEach(function(tag) {{
    tag.addEventListener('click', function() {{
      document.querySelectorAll('.filter-tag').forEach(function(t) {{ t.classList.remove('active'); }});
      this.classList.add('active');
      var filter = this.dataset.filter;
      document.querySelectorAll('.section-group').forEach(function(section) {{
        section.style.display = (filter === 'all' || section.dataset.category === filter) ? 'block' : 'none';
      }});
    }});
  }});

  // Chart
  var ctx = document.getElementById('trendChart');
  if (!ctx || !REGULATORY_DATA || !REGULATORY_DATA.trend) return;
  var trend = REGULATORY_DATA.trend;
  var cats = [];
  var seen = {{}};
  trend.forEach(function(d) {{ if (!seen[d.category]) {{ cats.push(d.category); seen[d.category] = true; }} }});
  var catColors = {{ {cat_colors} }};
  var days = [];
  var seenDays = {{}};
  trend.forEach(function(d) {{ if (!seenDays[d.day]) {{ days.push(d.day); seenDays[d.day] = true; }} }});
  days.sort();

  new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels: days,
      datasets: cats.map(function(cat) {{
        var counts = days.map(function(day) {{
          var found = trend.find(function(d) {{ return d.day === day && d.category === cat; }});
          return found ? found.count : 0;
        }});
        return {{
          label: cat,
          data: counts,
          backgroundColor: catColors[cat] || '#94a3b8',
          borderColor: catColors[cat] || '#94a3b8',
          borderWidth: 0,
          barPercentage: 0.9,
          categoryPercentage: 0.95,
        }};
      }}),
    }},
    options: {{
      responsive: true,
      interaction: {{ intersect: false, mode: 'index' }},
      plugins: {{
        legend: {{
          position: 'bottom',
          labels: {{
            usePointStyle: true, pointStyleWidth: 10, padding: 24,
            font: {{ size: 13, family: "'Noto Sans SC', 'Inter', sans-serif" }},
          }},
        }},
        tooltip: {{ mode: 'index', intersect: false }},
      }},
      scales: {{
        x: {{
          stacked: true,
          grid: {{ display: false }},
          ticks: {{ font: {{ size: 10 }}, maxRotation: 45, autoSkip: true, autoSkipPadding: 4 }},
        }},
        y: {{
          stacked: true,
          beginAtZero: true,
          ticks: {{ stepSize: 1, font: {{ size: 12 }} }},
          grid: {{ color: '#f1f5f9' }},
          title: {{ display: true, text: '公告数量', font: {{ size: 12 }} }},
        }},
      }},
    }},
  }});
}})();
</script>

</body>
</html>"""


CAT_META = {
    ItemCategory.DISCIPLINARY_ACTION: {
        "label": "纪律处分",
        "color": "#B85450", "bg": "#faf4f3", "icon": "⚖️", "sort": 0,
    },
    ItemCategory.CONSULTATION_CONCLUSION: {
        "label": "咨询总结",
        "color": "#2E6B8F", "bg": "#f2f6f9", "icon": "📝", "sort": 1,
    },
    ItemCategory.REGULATORY_RULE: {
        "label": "监管规则",
        "color": "#4A8C6F", "bg": "#f2f7f4", "icon": "📜", "sort": 2,
    },
    ItemCategory.ENFORCEMENT_NEWS: {
        "label": "执法新闻",
        "color": "#C8963E", "bg": "#faf7f2", "icon": "🔍", "sort": 3,
    },
    ItemCategory.OTHER: {
        "label": "其他",
        "color": "#7B8D8E", "bg": "#f5f6f6", "icon": "📌", "sort": 4,
    },
}


def _build_stat_card(label: str, count: int, color: str, bg: str, icon: str) -> str:
    return f"""
    <div class="stat-card">
      <div class="stat-icon" style="background:{bg};color:{color};">{icon}</div>
      <div class="stat-count" style="color:{color};">{count}</div>
      <div class="stat-label">{label}</div>
    </div>"""


def _build_item_html(item: RegulatoryItem) -> str:
    meta = CAT_META.get(item.category, CAT_META[ItemCategory.OTHER])
    source_color = "#1a5276" if item.source.value == "SFC" else "#b7950b"
    source_label = item.source.label
    title = item.title_zh or item.title_en
    summary = item.summary_zh or item.summary_en

    return f"""
    <div class="item-card" data-category="{item.category.value}">
      <div class="item-card-inner">
        <div class="item-accent" style="background:{meta['color']};"></div>
        <div class="item-body">
          <div class="item-top">
            <div class="item-title-group">
              <div class="item-title">
                <a href="{item.url}" target="_blank" rel="noopener">{title}</a>
              </div>
            </div>
            <div class="item-meta">
              <span class="tag tag-source" style="color:{source_color};border-color:{source_color};">{source_label}</span>
              <span class="tag tag-category" style="background:{meta['color']};">{meta['label']}</span>
              <span class="tag tag-date">{item.date_display}</span>
            </div>
          </div>
          {f'<div class="item-summary">{summary}</div>' if summary else ''}
          <div class="item-bottom">
            <span class="item-method">📡 来源：{item.collection_method}</span>
            <a href="{item.url}" target="_blank" rel="noopener" class="source-btn">
              查看原文 <span class="arr">↗</span>
            </a>
          </div>
        </div>
      </div>
    </div>"""


def generate_html(
    items: list[RegulatoryItem],
    output_path: Path,
    title: str = "香港监管咨询看板",
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    trend_data: Optional[list[dict]] = None,
) -> Path:
    """生成专业静态 HTML 看板。"""

    items_sorted = sorted(
        items,
        key=lambda x: x.published_date if x.published_date != "Unknown" else "0000-00-00",
        reverse=True,
    )

    categories_ordered = sorted(CAT_META.keys(), key=lambda c: CAT_META[c]["sort"])
    grouped = {cat: [i for i in items_sorted if i.category == cat] for cat in categories_ordered}

    # Period header
    if period_start and period_end:
        period_label = f"{period_start.strftime('%Y年%m月%d日')} — {period_end.strftime('%Y年%m月%d日')}"
        period_title = f"{period_start.strftime('%Y年%m月')}至今监管咨询概览"
    else:
        dates = [i.published_date for i in items_sorted if i.published_date != "Unknown"]
        if dates:
            earliest = min(dates)
            try:
                month = datetime.strptime(earliest, "%Y-%m-%d").strftime("%Y年%m月")
            except ValueError:
                month = earliest
            period_label = f"{earliest} — {max(dates)}"
            period_title = f"{month}至今监管咨询概览"
        else:
            period_label = "最近更新"
            period_title = "监管咨询概览"

    # Stats cards
    stats_cards = ""
    for cat in categories_ordered:
        if cat == ItemCategory.OTHER:
            continue
        meta = CAT_META[cat]
        stats_cards += _build_stat_card(meta["label"], len(grouped[cat]), meta["color"], meta["bg"], meta["icon"])

    # Filter tags
    filter_tags = ""
    for cat in categories_ordered:
        if cat == ItemCategory.OTHER:
            continue
        meta = CAT_META[cat]
        filter_tags += f'<span class="filter-tag" data-filter="{cat.value}">{meta["icon"]} {meta["label"]} ({len(grouped[cat])})</span>\n'

    # Content sections
    sections = ""
    for cat in categories_ordered:
        cat_items = grouped[cat]
        if not cat_items:
            continue
        meta = CAT_META[cat]
        sections += f"""
  <div class="section section-group" data-category="{cat.value}">
    <div class="section-header">
      <span class="dot" style="background:{meta['color']};"></span>
      <h2>{meta['icon']} {meta['label']}</h2>
      <span class="count-tag">{len(cat_items)} 项</span>
    </div>"""
        for item in cat_items:
            sections += _build_item_html(item)
        sections += "\n  </div>\n"

    # Trend data + data JSON
    if trend_data is None:
        trend_data = []
    data_json = json.dumps(
        {"items": [i.to_dict() for i in items_sorted], "trend": trend_data},
        ensure_ascii=False,
    )

    # Chart.js colors
    cat_colors = ", ".join(f'"{v["label"]}": "{v["color"]}"' for v in CAT_META.values())

    now = datetime.now().strftime("%Y-%m-%d %H:%M 北京时间")

    # Render HTML
    html = HTML_TEMPLATE.format(
        title=title,
        period_label=period_label,
        period_title=period_title,
        stats_cards=stats_cards,
        total_count=len(items_sorted),
        filter_tags=filter_tags,
        sections=sections or '<div class="empty-state"><div class="empty-icon">📭</div><p>暂无监管信息</p><p style="font-size:.82em;">请稍后回来查看，或调整搜索条件</p></div>',
        cat_colors=cat_colors,
        generated_at=now,
    )

    # Inject data BEFORE chart script — critical fix:
    # The chart code references REGULATORY_DATA, so data must be loaded first.
    data_script = f"<script>const REGULATORY_DATA = {data_json};</script>"
    html = html.replace("<div class=\"container\">", f"<div class=\"container\">\n{data_script}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"  [OK] HTML 看板已生成：{output_path}")

    return output_path
