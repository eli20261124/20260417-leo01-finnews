from __future__ import annotations

import json
import time
from typing import Any

from google import genai

from src.config import BATCH_SIZE, DEFAULT_SUMMARIZER_PROVIDER, RATE_LIMIT_SLEEP


VALID_TAGS = {
    "Interest Rates",
    "Inflation",
    "AI Boom",
    "Economic Slowdown",
    "Geopolitics",
    "Energy Market",
    "Liquidity / Fed Policy",
}


def _truncate_text(text: str, limit: int = 1200) -> str:
    return (text or "")[:limit]


def _fallback_summary(article: dict[str, Any]) -> tuple[str, str]:
    text = _truncate_text(article.get("text", "") or article.get("title", ""), 220)
    en = f"{article.get('title', 'Untitled')}: {text}".strip()
    zh = f"重點摘要：{text}".strip()
    return en, zh


def build_batch_prompt(articles: list[dict[str, Any]]) -> str:
    payload = []
    for index, article in enumerate(articles, start=1):
        payload.append(
            {
                "index": index,
                "title": article.get("title", ""),
                "source": article.get("source_label", ""),
                "published": article.get("published", ""),
                "text": _truncate_text(article.get("text", "")),
            }
        )
    return (
        "You are a financial news editor. Summarize each article in 2-3 precise sentences in English and 2-3 precise sentences in Traditional Chinese (zh-TW). "
        "Return only valid JSON with this shape: "
        "[{\"index\": 1, \"summary_en\": \"...\", \"summary_zh\": \"...\"}]. "
        f"Articles: {json.dumps(payload, ensure_ascii=False)}"
    )


def _extract_json(text: str) -> Any:
    stripped = text.strip()
    if stripped.startswith("```"):
        parts = stripped.split("```")
        stripped = next((part for part in parts if "[" in part or "{" in part), stripped)
    start = stripped.find("[")
    end = stripped.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON array found")
    return json.loads(stripped[start : end + 1])


def _apply_fallback_summaries(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for article in articles:
        summary_en, summary_zh = _fallback_summary(article)
        article["summary_en"] = summary_en
        article["summary_zh"] = summary_zh
    return articles


def summarize_all(articles: list[dict[str, Any]], provider: str | None, api_key: str | None) -> list[dict[str, Any]]:
    normalized_provider = (provider or DEFAULT_SUMMARIZER_PROVIDER).strip().lower()
    if normalized_provider != "gemini":
        return _apply_fallback_summaries(articles)
    if not api_key:
        print("SUMMARIZER_PROVIDER=gemini but GEMINI_API_KEY is missing; falling back to non-AI summaries.")
        return _apply_fallback_summaries(articles)

    client = genai.Client(api_key=api_key)

    for start in range(0, len(articles), BATCH_SIZE):
        batch = articles[start : start + BATCH_SIZE]
        prompt = build_batch_prompt(batch)
        try:
            response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
            items = _extract_json(response.text)
            by_index = {item["index"]: item for item in items if "index" in item}
            for index, article in enumerate(batch, start=1):
                item = by_index.get(index, {})
                summary_en = item.get("summary_en")
                summary_zh = item.get("summary_zh")
                if not summary_en or not summary_zh:
                    summary_en, summary_zh = _fallback_summary(article)
                article["summary_en"] = summary_en
                article["summary_zh"] = summary_zh
        except Exception as exc:
            print(f"Gemini summary batch failed; using fallback summaries. Error: {exc}")
            for article in batch:
                summary_en, summary_zh = _fallback_summary(article)
                article["summary_en"] = summary_en
                article["summary_zh"] = summary_zh
        if start + BATCH_SIZE < len(articles):
            time.sleep(RATE_LIMIT_SLEEP)
    return articles


def build_narrative_prompt(articles: list[dict[str, Any]]) -> str:
    sample = [
        {
            "title": article.get("title", ""),
            "source": article.get("source_label", ""),
            "summary_en": article.get("summary_en", ""),
        }
        for article in articles[:40]
    ]
    return (
        "Based on ALL selected stories, identify the single dominant market narrative today. "
        "Write one sharp sentence, max 25 words, that captures what is happening, why it matters, and the market direction. "
        "Then provide a Narrative Tag chosen from exactly one of: Interest Rates, Inflation, AI Boom, Economic Slowdown, Geopolitics, Energy Market, Liquidity / Fed Policy. "
        "Rules: must be specific, not generic; avoid vague statements like 'markets are uncertain'; sound like a professional financial headline; NYT tone: calm, analytical, precise. "
        "Return only valid JSON like {\"sentence\": \"...\", \"tag\": \"...\"}. "
        f"Stories: {json.dumps(sample, ensure_ascii=False)}"
    )


def generate_market_narrative(articles: list[dict[str, Any]], provider: str | None, api_key: str | None) -> dict[str, str]:
    fallback = {
        "sentence": "Markets are being steered by a mixed macro and corporate-news flow, with investors focusing on policy signals and sector leadership.",
        "tag": "Liquidity / Fed Policy",
    }
    normalized_provider = (provider or DEFAULT_SUMMARIZER_PROVIDER).strip().lower()
    if normalized_provider != "gemini" or not api_key or not articles:
        return fallback

    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=build_narrative_prompt(articles))
        text = response.text.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            return fallback
        data = json.loads(text[start : end + 1])
        sentence = (data.get("sentence") or "").strip()
        tag = (data.get("tag") or "").strip()
        if not sentence or not tag:
            return fallback
        if tag not in VALID_TAGS:
            tag = fallback["tag"]
        words = sentence.split()
        if len(words) > 25:
            sentence = " ".join(words[:25])
        return {"sentence": sentence, "tag": tag}
    except Exception as exc:
        print(f"Gemini market narrative failed; using fallback narrative. Error: {exc}")
        return fallback
