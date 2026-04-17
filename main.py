from __future__ import annotations

import os
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv

from src.config import DEFAULT_SHOW_RANK_DEBUG, DEFAULT_SUMMARIZER_PROVIDER
from src.fetcher import fetch_all
from src.mailer import EmailSettings, send_report_email
from src.renderer import publish_latest_html, render_html, save_html
from src.summarizer import generate_market_narrative, summarize_all


def _get_generated_at() -> datetime:
    timezone_name = (os.getenv("REPORT_TIMEZONE") or "").strip()
    if not timezone_name:
        return datetime.now()
    try:
        return datetime.now(ZoneInfo(timezone_name))
    except ZoneInfoNotFoundError:
        print(f"Unknown REPORT_TIMEZONE '{timezone_name}', falling back to system local time.")
        return datetime.now()


def main() -> int:
    load_dotenv()
    summarizer_provider = (os.getenv("SUMMARIZER_PROVIDER") or DEFAULT_SUMMARIZER_PROVIDER).strip().lower()
    show_rank_debug = (os.getenv("SHOW_RANK_DEBUG", str(DEFAULT_SHOW_RANK_DEBUG)).strip().lower() in {"1", "true", "yes", "on"})
    email_enabled = os.getenv("EMAIL_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
    gemini_api_key = os.getenv("GEMINI_API_KEY") or None
    guardian_api_key = os.getenv("GUARDIAN_API_KEY") or None
    newsapi_key = os.getenv("NEWSAPI_KEY") or None
    email_settings = EmailSettings(
        enabled=email_enabled,
        recipient=os.getenv("EMAIL_TO") or None,
        sender=os.getenv("EMAIL_FROM") or None,
        app_password=os.getenv("EMAIL_APP_PASSWORD") or None,
    )

    generated_at = _get_generated_at()
    articles = fetch_all(guardian_api_key=guardian_api_key, newsapi_key=newsapi_key)
    if not articles:
        print("No articles fetched. Check API keys or network connectivity.")
        return 1

    summarized_articles = summarize_all(articles, provider=summarizer_provider, api_key=gemini_api_key)
    narrative = generate_market_narrative(summarized_articles, provider=summarizer_provider, api_key=gemini_api_key)
    html = render_html(summarized_articles, narrative, generated_at, show_rank_debug=show_rank_debug)
    output_path = save_html(html, generated_at)
    published_path = publish_latest_html(html)

    email_sent = False
    try:
        email_sent = send_report_email(email_settings, html, output_path, generated_at)
        if email_sent:
            print(f"Email sent to {email_settings.recipient}")
    except Exception as exc:
        print(f"Email delivery failed: {exc}")
        if email_enabled:
            return 1

    if email_enabled and not email_sent:
        print("Email was enabled but no report was sent.")
        return 1

    print(f"Generated {output_path}")
    print(f"Published {published_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())