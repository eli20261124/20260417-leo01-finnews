from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATE_DIR = BASE_DIR / "templates"
MAX_ARTICLES_PER_SOURCE = 10
SECTION_ARTICLE_LIMIT = 3
BATCH_SIZE = 5
RATE_LIMIT_SLEEP = 4
REQUEST_TIMEOUT = 20
ARTICLE_TEXT_LIMIT = 3000
SCRAPE_RSS_ARTICLE_TEXT = False
DEFAULT_SUMMARIZER_PROVIDER = "none"
DEFAULT_SHOW_RANK_DEBUG = True

SECTION_PRIORITY = {
    "Technology & Innovation": 6,
    "Asia & Greater China": 5,
    "Global Finance & Markets": 4,
    "Policy & Institutions": 3,
    "World Business": 2,
    "General / Media": 1,
}

SOURCE_PRIORITY = {
    "guardian_money": 4,
    "guardian_business": 4,
    "guardian_world": 3,
    "guardian_technology": 3,
    "reuters_business": 5,
    "ap_business": 4,
    "imf": 5,
    "cnbc": 3,
    "bbc_business": 3,
    "newsapi_business": 2,
    "deutsche_welle_business": 2,
    "npr_business": 2,
    "techcrunch": 3,
    "the_verge": 2,
    "scmp": 2,
    "cna": 2,
    "al_jazeera": 2,
}

IMPACT_KEYWORDS = {
    "fed": 5,
    "federal reserve": 5,
    "central bank": 5,
    "interest rate": 5,
    "rates": 4,
    "inflation": 5,
    "tariff": 4,
    "trade": 3,
    "oil": 4,
    "energy": 4,
    "war": 4,
    "ceasefire": 3,
    "sanctions": 4,
    "earnings": 3,
    "profit": 3,
    "recession": 5,
    "growth": 3,
    "gdp": 4,
    "employment": 4,
    "jobs": 3,
    "bank": 3,
    "banks": 3,
    "bond": 3,
    "stocks": 3,
    "market": 2,
    "ai": 3,
    "semiconductor": 3,
    "chip": 3,
}

CATEGORY_KEYWORDS = {
    "Technology & Innovation": {
        "ai": 5,
        "semiconductor": 6,
        "chip": 5,
        "chips": 5,
        "tsmc": 8,
        "nvidia": 6,
        "ai server": 6,
        "advanced packaging": 7,
        "cowos": 8,
        "hbm": 7,
        "wafer": 5,
        "chipmaking": 6,
        "fab": 5,
        "fabless": 5,
        "asic": 5,
        "electronics": 4,
        "server": 4,
        "datacenter": 4,
        "data center": 4,
        "cloud": 3,
        "foundry": 5,
        "smartphone": 3,
        "iphone": 3,
        "export controls": 5,
    },
    "Asia & Greater China": {
        "taiwan": 8,
        "taiex": 8,
        "tpex": 6,
        "tsmc": 9,
        "foxconn": 6,
        "mediatek": 6,
        "quanta": 6,
        "pegatron": 5,
        "wistron": 5,
        "inventec": 5,
        "advanced packaging": 7,
        "cowos": 8,
        "hbm": 7,
        "ai server": 7,
        "semiconductor": 6,
        "chip": 5,
        "electronics": 4,
        "china": 5,
        "beijing": 4,
        "yuan": 4,
        "renminbi": 4,
        "hong kong": 4,
        "cross-strait": 7,
        "strait": 4,
        "export": 4,
        "supply chain": 5,
    },
    "Global Finance & Markets": {
        "fed": 6,
        "federal reserve": 6,
        "treasury": 5,
        "yields": 5,
        "dollar": 5,
        "usd": 5,
        "oil": 5,
        "energy": 4,
        "freight": 4,
        "shipping": 4,
        "tariff": 5,
        "export": 3,
    },
    "Policy & Institutions": {
        "tariff": 6,
        "sanctions": 5,
        "export controls": 6,
        "central bank": 5,
        "regulator": 4,
        "government": 3,
        "ministry": 3,
        "policy": 4,
        "ceasefire": 4,
        "war": 4,
    },
    "World Business": {
        "earnings": 4,
        "guidance": 4,
        "demand": 4,
        "consumer": 3,
        "retail": 3,
        "manufacturing": 4,
        "factory": 4,
        "supply chain": 4,
    },
    "General / Media": {
        "market": 2,
        "economy": 2,
        "business": 2,
    },
}

NEGATIVE_KEYWORDS = {
    "opinion": 5,
    "editorial": 5,
    "review": 4,
    "celebrity": 4,
    "lifestyle": 4,
    "fashion": 3,
    "sports": 5,
    "weather": 5,
    "rainstorm": 5,
    "theatre": 4,
    "movie": 3,
    "music": 3,
    "festival": 3,
    "live blog": 2,
    "briefing": 2,
}

GUARDIAN_SECTIONS = [
    "business",
    "money",
    "technology",
    "world",
]

RSS_FEEDS = {
    "reuters_business": {
        "url": "https://feeds.reuters.com/reuters/businessNews",
        "label": "Reuters Business",
        "site_url": "https://www.reuters.com",
        "category": "Global Finance & Markets",
    },
    "bbc_business": {
        "url": "http://feeds.bbci.co.uk/news/business/rss.xml",
        "label": "BBC Business",
        "site_url": "https://www.bbc.com/news/business",
        "category": "General / Media",
    },
    "ap_business": {
        "url": "https://rss.ap.org/apf-business",
        "label": "AP Business",
        "site_url": "https://apnews.com/hub/business",
        "category": "World Business",
    },
    "cnbc": {
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "label": "CNBC",
        "site_url": "https://www.cnbc.com",
        "category": "Global Finance & Markets",
    },
    "techcrunch": {
        "url": "https://techcrunch.com/feed/",
        "label": "TechCrunch",
        "site_url": "https://techcrunch.com",
        "category": "Technology & Innovation",
    },
    "the_verge": {
        "url": "https://www.theverge.com/rss/index.xml",
        "label": "The Verge",
        "site_url": "https://www.theverge.com",
        "category": "Technology & Innovation",
    },
    "imf": {
        "url": "https://www.imf.org/en/News/RSS",
        "label": "IMF News",
        "site_url": "https://www.imf.org/en/News",
        "category": "Policy & Institutions",
    },
    "al_jazeera": {
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "label": "Al Jazeera",
        "site_url": "https://www.aljazeera.com/economy/",
        "category": "Asia & Greater China",
    },
    "deutsche_welle_business": {
        "url": "https://rss.dw.com/xml/rss-en-bus",
        "label": "Deutsche Welle Business",
        "site_url": "https://www.dw.com/en/business/s-1431",
        "category": "Policy & Institutions",
    },
    "npr_business": {
        "url": "https://feeds.npr.org/1006/rss.xml",
        "label": "NPR Business",
        "site_url": "https://www.npr.org/sections/business/",
        "category": "Policy & Institutions",
    },
    "scmp": {
        "url": "https://www.scmp.com/rss/91/feed",
        "label": "South China Morning Post",
        "site_url": "https://www.scmp.com/business",
        "category": "Asia & Greater China",
    },
    "cna": {
        "url": "https://www.cna.com.tw/rss/aopl.aspx",
        "label": "CNA",
        "site_url": "https://www.cna.com.tw",
        "category": "Asia & Greater China",
    },
}

FEED_CATEGORIES = {
    "Global Finance & Markets": [
        "guardian_money",
        "newsapi_business",
        "reuters_business",
        "cnbc",
    ],
    "World Business": [
        "guardian_business",
        "ap_business",
    ],
    "Policy & Institutions": [
        "guardian_world",
        "imf",
        "deutsche_welle_business",
        "npr_business",
    ],
    "Technology & Innovation": [
        "guardian_technology",
        "techcrunch",
        "the_verge",
    ],
    "Asia & Greater China": [
        "scmp",
        "cna",
        "al_jazeera",
    ],
    "General / Media": [
        "bbc_business",
    ],
}

TAG_COLORS = {
    "Interest Rates": "#b45309",
    "Inflation": "#be123c",
    "AI Boom": "#1d4ed8",
    "Economic Slowdown": "#475569",
    "Geopolitics": "#c2410c",
    "Energy Market": "#0f766e",
    "Liquidity / Fed Policy": "#7c3aed",
}

NEWSAPI_ALLOWED_DOMAINS = {
    "abcnews.go.com",
    "apnews.com",
    "axios.com",
    "bbc.com",
    "bbc.co.uk",
    "cbsnews.com",
    "cnn.com",
    "npr.org",
    "reuters.com",
    "time.com",
    "usatoday.com",
}
