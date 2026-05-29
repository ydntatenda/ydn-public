#!/usr/bin/env python3
"""
ydn-intel-scan: Morning intelligence scan
Runs at 06:15 daily via cron
Scans 8 domains relevant to the operator's startup and surfaces actionable signals via Telegram.
"""

import os
import json
import requests
from datetime import datetime, timezone
import psycopg2
from dotenv import load_dotenv

load_dotenv('/root/.hermes/.env')
load_dotenv('/root/ydn_db.env')

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
DATABASE_URI = os.getenv('DATABASE_URI')

# Search terms by domain — replace with your own domains and queries
SEARCH_TERMS = {
    'domain_1': [
        '[your domain 1 query 1]',
        '[your domain 1 query 2]',
        '[your domain 1 query 3]',
    ],
    'domain_2': [
        '[your domain 2 query 1]',
        '[your domain 2 query 2]',
        '[your domain 2 query 3]',
    ],
    'domain_3': [
        '[your domain 3 query 1]',
        '[your domain 3 query 2]',
        '[your domain 3 query 3]',
    ],
    'domain_4': [
        '[your domain 4 query 1]',
        '[your domain 4 query 2]',
        '[your domain 4 query 3]',
    ],
    'domain_5': [
        '[your domain 5 query 1]',
        '[your domain 5 query 2]',
        '[your domain 5 query 3]',
    ],
    'competitors': [
        '[competitor 1 name]',
        '[competitor 2 name]',
        '[competitor 3 name]',
    ],
    'partners': [
        '[key partner or stakeholder name]',
        '[key partner or stakeholder name]',
        '[key partner or stakeholder name]',
    ],
    'fundraising': [
        '[relevant VC or accelerator name]',
        '[startup funding query for your sector]',
        '[investor signal query]',
    ],
}

PRODUCT_MAP = {
    'domain_1': 'DOMAIN 1',
    'domain_2': 'DOMAIN 2',
    'domain_3': 'DOMAIN 3',
    'domain_4': 'DOMAIN 4',
    'domain_5': 'DOMAIN 5',
    'competitors': 'COMPETITIVE',
    'partners': 'PIPELINE',
    'fundraising': 'FUNDRAISING',
}

# Adjust to your target markets or geographies
TARGET_KEYWORDS = ['[your market keyword 1]', '[your market keyword 2]']

EXCLUDE_KEYWORDS = ['opinion', 'editorial', 'letter to the editor']


def tavily_search(query):
    try:
        response = requests.post(
            'https://api.tavily.com/search',
            json={
                'api_key': TAVILY_API_KEY,
                'query': query,
                'search_depth': 'basic',
                'max_results': 5,
                'include_answer': True,
            },
            timeout=15
        )
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Tavily error: {e}")
        return None


def is_relevant(result):
    title = (result.get('title') or '').lower()
    content = (result.get('content') or '').lower()
    text = title + ' ' + content
    if not any(kw in text for kw in TARGET_KEYWORDS):
        return False
    if any(kw in title for kw in EXCLUDE_KEYWORDS):
        return False
    return True


def format_signal(result, product):
    title = result.get('title', 'No title')
    content = result.get('content', '')
    snippet = content[:180].strip() + '...' if len(content) > 180 else content
    return {
        'headline': title,
        'snippet': snippet,
        'product': product,
        'url': result.get('url', ''),
    }


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False,
        }, timeout=10)
        if not r.ok:
            import time
            time.sleep(30)
            requests.post(url, json={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
            }, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")


def log_to_supabase(items, searches_run, filtered_out):
    try:
        conn = psycopg2.connect(DATABASE_URI)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO logs (kind, payload, created_at) VALUES (%s, %s, %s)",
            (
                'intel_scan',
                json.dumps({
                    'date': datetime.now(timezone.utc).date().isoformat(),
                    'items_surfaced': items,
                    'searches_run': searches_run,
                    'items_filtered_out': filtered_out,
                    'sent_at': datetime.now(timezone.utc).isoformat(),
                }),
                datetime.now(timezone.utc),
            )
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Supabase log error: {e}")


def main():
    date_str = datetime.now().strftime('%a %d %b %Y')

    signals = []
    searches_run = []
    filtered_out = 0
    seen_urls = set()

    for domain, terms in SEARCH_TERMS.items():
        domain_signal = None
        for query in terms:
            searches_run.append(query)
            results = tavily_search(query)
            if not results:
                continue
            for result in results.get('results', []):
                url = result.get('url', '')
                if url in seen_urls:
                    continue
                if is_relevant(result):
                    domain_signal = format_signal(result, PRODUCT_MAP[domain])
                    seen_urls.add(url)
                    break
                else:
                    filtered_out += 1
            if domain_signal:
                break
        if domain_signal:
            signals.append(domain_signal)
        if len(signals) >= 5:
            break

    if not signals:
        message = f"<b>Intel — {date_str}</b>\n\nNo actionable signals today."
    else:
        lines = [f"<b>Intel — {date_str}</b>\n"]
        for i, s in enumerate(signals[:5], 1):
            lines.append(f"{i}. <b>[{s['product']}]</b> <a href=\"{s['url']}\">{s['headline']}</a>")
            lines.append(f"   {s['snippet']}\n")
        message = '\n'.join(lines)

    send_telegram(message)
    log_to_supabase(
        [s['headline'] for s in signals],
        searches_run,
        filtered_out
    )
    print(f"Intel scan complete. {len(signals)} signals surfaced.")


if __name__ == '__main__':
    main()
