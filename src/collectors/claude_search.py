"""
Collect regulatory announcements via Claude API web_search + web_fetch.

This module uses the Anthropic native API (NOT the DeepSeek proxy) because
web_search and web_fetch are Anthropic server-side tools unavailable elsewhere.

Requires ANTHROPIC_API_KEY environment variable pointing to api.anthropic.com.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional

from ..output.models import RegulatoryItem, ItemCategory, ItemSource

SEARCH_PROMPT = """You are a Hong Kong financial regulatory monitoring assistant.
Search for the latest regulatory announcements published in the last {lookback_days} days
(since {date_since}) from:

1. **Hong Kong Securities and Futures Commission (SFC / 證監會)**:
   - Disciplinary actions and enforcement news (fines, bans, sanctions)
   - Regulatory policy announcements and consultation conclusions
   - New rules, codes, and guidelines
   - Primary site: sfc.hk

2. **Hong Kong Exchanges and Clearing (HKEX / 港交所)**:
   - Regulatory announcements and disciplinary actions against listed companies
   - Listing rule amendments and consultation conclusions
   - Listing Committee decisions and guidance letters
   - Primary site: hkex.com.hk

For each item found, you MUST:
1. Use web_search to locate recent regulatory announcements
2. For promising results, use web_fetch to extract full details
3. Record the exact publication date, title, and source URL
4. Write a concise 2-3 sentence summary in English
5. Write a concise 2-3 sentence summary in Traditional Chinese (zh-HK)
6. Classify into one category: disciplinary_action, consultation_conclusion,
   regulatory_rule, enforcement_news, or other
7. Assign a relevance_score (1-10): 10 = directly about HK financial regulation,
   1 = tangentially related

CRITICAL RULES:
- ALWAYS include the exact original source URL for every item
- Only include items from OFFICIAL SFC or HKEX sources
- Do not fabricate or guess any information
- If a date cannot be determined, use "Unknown"
- Focus on items relevant to Hong Kong financial market regulation

Return results strictly in the requested JSON format."""


def build_search_messages(lookback_days: int = 7) -> list[dict]:
    """Build the messages array for Claude API search."""
    date_since = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    prompt = SEARCH_PROMPT.format(lookback_days=lookback_days, date_since=date_since)
    return [{"role": "user", "content": prompt}]


def build_tools(max_search: int = 8, max_fetch: int = 6) -> list[dict]:
    """Build the tools array with web_search and web_fetch."""
    return [
        {
            "type": "web_search_20260209",
            "name": "web_search",
            "max_uses": max_search,
        },
        {
            "type": "web_fetch_20260209",
            "name": "web_fetch",
            "max_uses": max_fetch,
        },
    ]


def parse_claude_response(response) -> list[RegulatoryItem]:
    """
    Parse Claude's structured JSON response into RegulatoryItem objects.

    Handles both output_config.format (parsed JSON) and manual text extraction.
    """
    items = []

    # Try structured output first
    if hasattr(response, 'content'):
        for block in response.content:
            if hasattr(block, 'type') and block.type == "text":
                try:
                    data = json.loads(block.text)
                    raw_items = data.get("items", []) if isinstance(data, dict) else data
                except json.JSONDecodeError:
                    continue

                for raw in raw_items:
                    if not isinstance(raw, dict):
                        continue
                    try:
                        item = RegulatoryItem(
                            title_en=raw.get("title", "Untitled"),
                            title_zh=raw.get("title_zh", ""),
                            url=raw.get("url", ""),
                            published_date=raw.get("date", "Unknown"),
                            source=ItemSource(raw.get("source", "SFC")),
                            category=ItemCategory(raw.get("category", "other")),
                            summary_en=raw.get("summary_en", ""),
                            summary_zh=raw.get("summary_zh", ""),
                            collection_method="claude_api",
                        )
                        # Filter by relevance
                        score = raw.get("relevance_score", 5)
                        if score >= 6 and item.url:
                            items.append(item)
                    except (ValueError, KeyError) as e:
                        print(f"  [WARN] Skipping invalid item: {e}")
                        continue

    return items


def collect_via_claude(
    api_key: Optional[str] = None,
    lookback_days: int = 7,
    model: str = "claude-sonnet-4-6",
    max_search: int = 8,
    max_fetch: int = 6,
    effort: str = "high",
) -> list[RegulatoryItem]:
    """
    Collect regulatory items using Claude API web_search + web_fetch.

    Args:
        api_key: Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
        lookback_days: How many days back to search.
        model: Claude model to use.
        max_search: Max web_search calls per run.
        max_fetch: Max web_fetch calls per run.
        effort: Thinking effort level (low/medium/high/xhigh/max).

    Returns:
        List of RegulatoryItem objects.
    """
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[WARN] No ANTHROPIC_API_KEY set — skipping Claude API collection.")
        print("       Set this env var to enable AI-powered regulatory search.")
        return []

    try:
        import anthropic
    except ImportError:
        print("[WARN] anthropic SDK not installed. Run: pip install anthropic")
        return []

    client = anthropic.Anthropic(api_key=api_key)

    print(f"  Model: {model} | effort: {effort} | "
          f"searches: {max_search} | fetches: {max_fetch}")
    print(f"  Lookback: {lookback_days} days")

    messages = build_search_messages(lookback_days)
    tools = build_tools(max_search, max_fetch)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            thinking={"type": "adaptive"},
            output_config={
                "effort": effort,
                "format": {
                    "type": "json_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "title_zh": {"type": "string"},
                                        "url": {"type": "string"},
                                        "date": {"type": "string"},
                                        "source": {"type": "string", "enum": ["SFC", "HKEX"]},
                                        "category": {
                                            "type": "string",
                                            "enum": [
                                                "disciplinary_action",
                                                "consultation_conclusion",
                                                "regulatory_rule",
                                                "enforcement_news",
                                                "other",
                                            ],
                                        },
                                        "summary_en": {"type": "string"},
                                        "summary_zh": {"type": "string"},
                                        "relevance_score": {"type": "integer", "minimum": 1, "maximum": 10},
                                    },
                                    "required": ["title", "url", "date", "source", "category", "summary_en", "relevance_score"],
                                },
                            }
                        },
                        "required": ["items"],
                    },
                },
            },
            tools=tools,
            messages=messages,
        )

        items = parse_claude_response(response)
        print(f"  Collected {len(items)} items via Claude API")
        return items

    except Exception as e:
        print(f"  [ERROR] Claude API call failed: {e}")
        return []
