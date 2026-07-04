#!/usr/bin/env python3
"""
HKEX/SFC Regulatory Watch Dashboard Generator

Usage:
    python main.py                    # Generate dashboard with sample data
    python main.py --live             # Use Claude API to fetch real data
    python main.py --open             # Generate and open in browser

Environment variables:
    ANTHROPIC_API_KEY    Required for --live mode (Claude API key)
"""

import argparse
import os
import sys
import webbrowser
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.output.models import RegulatoryItem
from src.output.html_generator import generate_html
from src.output.sample_data import SAMPLE_ITEMS, generate_trend_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate HKEX/SFC Regulatory Watch Dashboard"
    )
    parser.add_argument(
        "--live", action="store_true",
        help="Use Claude API web_search to fetch real regulatory data"
    )
    parser.add_argument(
        "--open", action="store_true",
        help="Open the generated dashboard in browser"
    )
    parser.add_argument(
        "--model", default="claude-sonnet-4-6",
        help="Claude model for live search (default: claude-sonnet-4-6)"
    )
    parser.add_argument(
        "--output", default="docs/index.html",
        help="Output HTML path (default: docs/index.html)"
    )
    parser.add_argument(
        "--lookback", type=int, default=7,
        help="Days to look back for regulatory items (default: 7)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  香港監管諮詢看板 — 生成工具")
    print("=" * 60)
    print()

    items: list[RegulatoryItem] = []

    # ---- Mode 1: Live Claude API collection ----
    if args.live:
        print("[1/2] Fetching regulatory data via Claude API...")
        print()

        from src.collectors.claude_search import collect_via_claude

        items = collect_via_claude(
            lookback_days=args.lookback,
            model=args.model,
        )

        if not items:
            print()
            print("[INFO] No items collected. This could mean:")
            print("   - ANTHROPIC_API_KEY is not set")
            print("   - Claude API search didn't find new items in the lookback period")
            print("   - The API call encountered an error")
            print()
            print("Falling back to sample data for demonstration...")
            items = SAMPLE_ITEMS
    else:
        # ---- Mode 2: Sample data (quick demo) ----
        print("[1/2] Using sample data for demonstration...")
        print("       (Run with --live to fetch real data via Claude API)")
        items = SAMPLE_ITEMS

    # ---- Generate HTML Dashboard ----
    print()
    print(f"[2/2] Generating dashboard from {len(items)} items...")

    output_path = PROJECT_ROOT / args.output
    trend = generate_trend_data()

    from datetime import datetime, timedelta
    period_start = datetime.now() - timedelta(days=30)

    generate_html(
        items=items,
        output_path=output_path,
        trend_data=trend,
        period_start=period_start,
        period_end=datetime.now(),
    )

    print()
    print("=" * 60)
    print(f"  看板已生成：{output_path}")
    print(f"  監管資訊：{len(items)} 項")
    print("=" * 60)

    # ---- Open in browser ----
    if args.open:
        url = output_path.resolve().as_uri()
        print(f"\n  Opening {url} ...")
        webbrowser.open(url)

    # ---- Next steps ----
    print()
    print("下一步：")
    print("  1. 查看 docs/index.html 生成的看板")
    print("  2. 設定 ANTHROPIC_API_KEY 後執行 python main.py --live --open 獲取真實數據")
    print("  3. 部署至 GitHub Pages 實現公開訪問")
    print("  4. 設定 GitHub Actions 實現每日自動更新")


if __name__ == "__main__":
    main()
