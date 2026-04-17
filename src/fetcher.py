from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Any
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

from src.config import ARTICLE_TEXT_LIMIT, GUARDIAN_SECTIONS, MAX_ARTICLES_PER_SOURCE, NEWSAPI_ALLOWED_DOMAINS, REQUEST_TIMEOUT, RSS_FEEDS, SCRAPE_RSS_ARTICLE_TEXT


USER_AGENT = "FinNewsBot/1.0 (+https://example.com)"


def _clean_text(value: str) -> str:
    text = BeautifulSoup(unescape(value or ""), "html.parser").get_text(" ", strip=True)
    return " ".join(text.split())


def _normalize_date(value: str) -> str:
    if not value:
        return ""
    try:
        return parsedate_to_datetime(value).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return value


def extract_article_text(url: str) -> str:
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
    except requests.RequestException:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    text = " ".join(part for part in paragraphs if part)
    text = " ".join(text.split())
    return text[:ARTICLE_TEXT_LIMIT]


def fetch_rss(feed_key: str, feed_cfg: dict[str, str]) -> list[dict[str, Any]]:
    parsed = feedparser.parse(feed_cfg["url"])
    articles: list[dict[str, Any]] = []
    for entry in parsed.entries[:MAX_ARTICLES_PER_SOURCE]:
        link = getattr(entry, "link", "")
        description = _clean_text(getattr(entry, "summary", "") or getattr(entry, "description", ""))
        full_text = extract_article_text(link) if SCRAPE_RSS_ARTICLE_TEXT and link else ""
        text = full_text or description or _clean_text(getattr(entry, "title", ""))
        articles.append(
            {
                "id": f"{feed_key}:{link or getattr(entry, 'title', '')}",
                "title": _clean_text(getattr(entry, "title", "Untitled")),
                "link": link,
                "published": _normalize_date(getattr(entry, "published", "") or getattr(entry, "updated", "")),
                "source_key": feed_key,
                "source_label": feed_cfg["label"],
                "source_url": feed_cfg["site_url"],
                "category": feed_cfg["category"],
                "text": text,
                "content_mode": "full" if full_text else "excerpt",
            }
        )
    return articles


def fetch_guardian(section: str, api_key: str) -> list[dict[str, Any]]:
    url = "https://content.guardianapis.com/search"
    params = {
        "api-key": api_key,
        "section": section,
        "page-size": MAX_ARTICLES_PER_SOURCE,
        "show-fields": "bodyText",
        "order-by": "newest",
    }
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    data = response.json()
    results = data.get("response", {}).get("results", [])
    source_key = f"guardian_{section}"
    category_map = {
        "business": "World Business",
        "money": "Global Finance & Markets",
        "technology": "Technology & Innovation",
        "world": "Policy & Institutions",
    }
    return [
        {
            "id": f"{source_key}:{item.get('webUrl', '')}",
            "title": item.get("webTitle", "Untitled"),
            "link": item.get("webUrl", ""),
            "published": item.get("webPublicationDate", "")[:16].replace("T", " "),
            "source_key": source_key,
            "source_label": "The Guardian",
            "source_url": "https://www.theguardian.com",
            "category": category_map.get(section, "World Business"),
            "text": _clean_text(item.get("fields", {}).get("bodyText", ""))[:ARTICLE_TEXT_LIMIT] or item.get("webTitle", ""),
            "content_mode": "full",
        }
        for item in results
    ]


def fetch_newsapi(api_key: str) -> list[dict[str, Any]]:
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": api_key,
        "category": "business",
        "language": "en",
        "pageSize": 100,
    }
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    data = response.json()
    articles = []
    for item in data.get("articles", [])[: MAX_ARTICLES_PER_SOURCE * 2]:
        link = item.get("url", "")
        source_name = (item.get("source") or {}).get("name") or "NewsAPI"
        parsed = urlparse(link)
        site_url = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else "https://newsapi.org"
        domain = (parsed.netloc or "").lower().removeprefix("www.")
        if domain not in NEWSAPI_ALLOWED_DOMAINS:
            continue
        text = _clean_text(item.get("description", "") or item.get("title", ""))
        articles.append(
            {
                "id": f"newsapi_business:{link or item.get('title', '')}",
                "title": item.get("title", "Untitled"),
                "link": link,
                "published": (item.get("publishedAt") or "")[:16].replace("T", " "),
                "source_key": "newsapi_business",
                "source_label": source_name,
                "source_url": site_url,
                "category": "Global Finance & Markets",
                "text": text,
                "content_mode": "excerpt",
            }
        )
    return articles


def fetch_all(guardian_api_key: str | None, newsapi_key: str | None) -> list[dict[str, Any]]:
    tasks = []
    articles: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for feed_key, feed_cfg in RSS_FEEDS.items():
            tasks.append(executor.submit(fetch_rss, feed_key, feed_cfg))
        if guardian_api_key:
            for section in GUARDIAN_SECTIONS:
                tasks.append(executor.submit(fetch_guardian, section, guardian_api_key))
        if newsapi_key:
            tasks.append(executor.submit(fetch_newsapi, newsapi_key))

        for future in as_completed(tasks):
            try:
                articles.extend(future.result())
            except Exception:
                continue

    deduped: dict[str, dict[str, Any]] = {}
    for article in articles:
        link = article.get("link") or article.get("title")
        deduped[link] = article
    return sorted(deduped.values(), key=lambda item: (item.get("published", ""), item.get("title", "")), reverse=True)
