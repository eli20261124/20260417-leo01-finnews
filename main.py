from __future__ import annotations

import os
from datetime import datetime

from dotenv import load_dotenv

from src.config import DEFAULT_SHOW_RANK_DEBUG, DEFAULT_SUMMARIZER_PROVIDER
from src.fetcher import fetch_all
from src.mailer import EmailSettings, send_report_email
from src.renderer import publish_latest_html, render_html, save_html
from src.summarizer import generate_market_narrative, summarize_all


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

    generated_at = datetime.now()
    articles = fetch_all(guardian_api_key=guardian_api_key, newsapi_key=newsapi_key)
    if not articles:
        print("No articles fetched. Check API keys or network connectivity.")
        return 1

    summarized_articles = summarize_all(articles, provider=summarizer_provider, api_key=gemini_api_key)
    narrative = generate_market_narrative(summarized_articles, provider=summarizer_provider, api_key=gemini_api_key)
    html = render_html(summarized_articles, narrative, generated_at, show_rank_debug=show_rank_debug)
    output_path = save_html(html, generated_at)
    published_path = publish_latest_html(html)

    try:
        if send_report_email(email_settings, html, output_path, generated_at):
            print(f"Email sent to {email_settings.recipient}")
    except Exception as exc:
        print(f"Email delivery failed: {exc}")

    print(f"Generated {output_path}")
    print(f"Published {published_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())