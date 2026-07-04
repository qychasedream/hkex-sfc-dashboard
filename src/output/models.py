"""Unified data models for regulatory items."""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ItemCategory(Enum):
    DISCIPLINARY_ACTION = "disciplinary_action"
    CONSULTATION_CONCLUSION = "consultation_conclusion"
    REGULATORY_RULE = "regulatory_rule"
    ENFORCEMENT_NEWS = "enforcement_news"
    OTHER = "other"

    @property
    def label_en(self) -> str:
        labels = {
            "disciplinary_action": "Disciplinary Action",
            "consultation_conclusion": "Consultation Conclusion",
            "regulatory_rule": "Regulatory Rule",
            "enforcement_news": "Enforcement News",
            "other": "Other",
        }
        return labels.get(self.value, self.value)

    @property
    def label_zh(self) -> str:
        labels = {
            "disciplinary_action": "紀律處分",
            "consultation_conclusion": "諮詢總結",
            "regulatory_rule": "監管規則",
            "enforcement_news": "執法新聞",
            "other": "其他",
        }
        return labels.get(self.value, self.value)

    @property
    def color(self) -> str:
        colors = {
            "disciplinary_action": "#e74c3c",
            "consultation_conclusion": "#3498db",
            "regulatory_rule": "#2ecc71",
            "enforcement_news": "#e67e22",
            "other": "#95a5a6",
        }
        return colors.get(self.value, "#95a5a6")


class ItemSource(Enum):
    SFC = "SFC"
    HKEX = "HKEX"

    @property
    def label(self) -> str:
        return self.value

    @property
    def color(self) -> str:
        return "#1a5276" if self.value == "SFC" else "#b7950b"


@dataclass
class RegulatoryItem:
    """A single regulatory announcement/action."""
    title_en: str
    url: str
    published_date: str  # ISO 8601 date string
    source: ItemSource
    category: ItemCategory
    summary_en: str = ""
    summary_zh: str = ""
    title_zh: str = ""
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())
    collection_method: str = "unknown"  # "rss", "scraper", "claude_api", "manual"

    @property
    def id(self) -> str:
        """Deterministic ID based on URL."""
        return hashlib.sha256(self.url.encode()).hexdigest()[:12]

    @property
    def date_display(self) -> str:
        """Human-readable date."""
        try:
            dt = datetime.fromisoformat(self.published_date.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            return self.published_date

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title_en": self.title_en,
            "title_zh": self.title_zh,
            "url": self.url,
            "date": self.date_display,
            "source": self.source.value,
            "source_label": self.source.label,
            "category": self.category.value,
            "category_label_en": self.category.label_en,
            "category_label_zh": self.category.label_zh,
            "category_color": self.category.color,
            "source_color": self.source.color,
            "summary_en": self.summary_en,
            "summary_zh": self.summary_zh,
            "fetched_at": self.fetched_at,
            "collection_method": self.collection_method,
        }
