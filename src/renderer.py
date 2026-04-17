from __future__ import annotations

import os
import re
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


def _configure_macos_pdf_libraries() -> None:
    if sys.platform != "darwin":
        return
    library_paths = ["/opt/homebrew/lib", "/opt/homebrew/opt/libffi/lib"]
    existing_paths = [path for path in (os.getenv("DYLD_FALLBACK_LIBRARY_PATH") or "").split(":") if path]
    merged_paths = []
    for path in library_paths + existing_paths:
        if path and path not in merged_paths:
            merged_paths.append(path)
    if merged_paths:
        os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = ":".join(merged_paths)


_configure_macos_pdf_libraries()

from weasyprint import HTML

from src.config import CATEGORY_KEYWORDS, DOCS_DIR, FEED_CATEGORIES, IMPACT_KEYWORDS, NEGATIVE_KEYWORDS, OUTPUT_DIR, SECTION_ARTICLE_LIMIT, SECTION_PRIORITY, SOURCE_PRIORITY, TAG_COLORS, TEMPLATE_DIR


def _published_sort_key(value: str) -> datetime:
    try:
        return datetime.strptime(value or "", "%Y-%m-%d %H:%M")
    except ValueError:
        return datetime.min


def _keyword_present(text: str, keyword: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(keyword.lower()) + r"(?!\w)"
    return re.search(pattern, text) is not None


def _importance_score(article: dict[str, Any]) -> tuple[int, list[str]]:
    category = article.get("category") or "General / Media"
    score = SOURCE_PRIORITY.get(article.get("source_key", ""), 1)
    reasons = [f"source {article.get('source_key', 'unknown')} +{SOURCE_PRIORITY.get(article.get('source_key', ''), 1)}"]
    score += SECTION_PRIORITY.get(category, 0)
    reasons.append(f"section {category} +{SECTION_PRIORITY.get(category, 0)}")
    text = f"{article.get('title', '')} {article.get('text', '')}".lower()
    for keyword, weight in IMPACT_KEYWORDS.items():
        if _keyword_present(text, keyword):
            score += weight
            reasons.append(f"impact {keyword} +{weight}")
    for keyword, weight in CATEGORY_KEYWORDS.get(category, {}).items():
        if _keyword_present(text, keyword):
            score += weight
            reasons.append(f"category {keyword} +{weight}")
    for keyword, weight in NEGATIVE_KEYWORDS.items():
        if _keyword_present(text, keyword):
            score -= weight
            reasons.append(f"negative {keyword} -{weight}")
    if article.get("content_mode") == "full":
        score += 1
        reasons.append("full text +1")
    return score, reasons


def group_articles(articles: list[dict[str, Any]], limit: int = SECTION_ARTICLE_LIMIT) -> OrderedDict[str, list[dict[str, Any]]]:
    grouped: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    ordered_categories = sorted(
        FEED_CATEGORIES,
        key=lambda category: (SECTION_PRIORITY.get(category, 0), category),
        reverse=True,
    )
    for category in ordered_categories:
        grouped[category] = []
    for article in articles:
        category = article.get("category") or "General / Media"
        grouped.setdefault(category, []).append(article)
    ranked: OrderedDict[str, list[dict[str, Any]]] = OrderedDict()
    for key, value in grouped.items():
        if not value:
            continue
        scored_articles = []
        for article in value:
            score, reasons = _importance_score(article)
            enriched = dict(article)
            enriched["importance_score"] = score
            enriched["importance_reasons"] = reasons[:8]
            scored_articles.append(enriched)
        ranked[key] = sorted(
            scored_articles,
            key=lambda article: (
                article.get("importance_score", 0),
                _published_sort_key(article.get("published", "")),
                article.get("title", ""),
            ),
            reverse=True,
        )[:limit]
    return ranked


def render_html(articles: list[dict[str, Any]], narrative: dict[str, str], generated_at: datetime, show_rank_debug: bool = False) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("report.html")
    grouped = group_articles(articles)
    return template.render(
        generated_at=generated_at.strftime("%Y-%m-%d %H:%M"),
        narrative=narrative,
        show_rank_debug=show_rank_debug,
        tag_color=TAG_COLORS.get(narrative.get("tag", ""), "#334155"),
        grouped_articles=grouped,
        total_articles=sum(len(items) for items in grouped.values()),
    )


def save_html(html: str, generated_at: datetime) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"news_{generated_at.strftime('%Y%m%d')}.html"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def save_pdf(html: str, generated_at: datetime) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"news_{generated_at.strftime('%Y%m%d')}.pdf"
    HTML(string=html, base_url=str(TEMPLATE_DIR.parent)).write_pdf(output_path)
    return output_path


def publish_latest_html(html: str) -> Path:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    published_path = DOCS_DIR / "index.html"
    published_path.write_text(html, encoding="utf-8")
    return published_path
