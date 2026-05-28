#!/usr/bin/env python3
"""
gmail_watch.py

Checks Gmail for new messages from priority contacts and writes them
to the Supabase logs table. Runs as a cron job every 15 minutes.

Priority tiers (from lattanye_ledger.md):
- Tier 1 (interrupt): investors, government partners, Prof Rosman, Prof Marivate
- Tier 2 (digest): team (Yusta, Chidubem, Tafadzwa), advisors
- Tier 3 (silent log): newsletters, notifications, other

Tier 1 emails also trigger a Telegram notification.
"""

import json
import os
import sys
import base64
from datetime import datetime, timezone, timedelta

TOKEN_FILE = '/root/google_token.json'
ENV_FILE = '/root/ydn_db.env'
STATE_FILE = '/root/gmail_state.json'

TIER_1_KEYWORDS = [
    'a16z', 'andreessen', 'afore', 'speedrun', 'investor', 'term sheet',
    'rosman', 'marivate', 'ocpo', 'dcdt', 'treasury', 'cape town',
    'ministry', 'government', 'vc', 'fund', 'pre-seed', 'seed round'
]

TIER_2_NAMES = ['yusta', 'chidubem', 'tafadzwa']

def load_env():
    env = {}
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {'last_history_id': None, 'processed_ids': []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_gmail_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    with open(TOKEN_FILE) as f:
        td = json.load(f)

    creds = Credentials(
        token=td.get('token'),
        refresh_token=td.get('refresh_token'),
        token_uri=td.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=td.get('client_id'),
        client_secret=td.get('client_secret'),
        scopes=td.get('scopes')
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        td['token'] = creds.token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(td, f, indent=2)

    return build('gmail', 'v1', credentials=creds)

def classify_email(sender, subject):
    text = (sender + ' ' + subject).lower()
    if any(kw in text for kw in TIER_1_KEYWORDS):
        return 'tier1'
    if any(name in text for name in TIER_2_NAMES):
        return 'tier2'
    return 'tier3'

def fetch_new_emails(service, state):
    query = 'is:unread newer_than:1d'
    result = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=20
    ).execute()

    messages = result.get('messages', [])
    new_messages = []

    processed_ids = set(state.get('processed_ids', []))

    for msg in messages:
        if msg['id'] in processed_ids:
            continue

        full = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='metadata',
            metadataHeaders=['From', 'Subject', 'Date']
        ).execute()

        headers = {h['name']: h['value'] for h in full.get('payload', {}).get('headers', [])}
        sender = headers.get('From', '')
        subject = headers.get('Subject', '')
        date = headers.get('Date', '')
        snippet = full.get('snippet', '')
        thread_id = full.get('threadId', '')

        tier = classify_email(sender, subject)
        new_messages.append({
            'id': msg['id'],
            'thread_id': thread_id,
            'sender': sender,
            'subject': subject,
            'date': date,
            'snippet': snippet,
            'tier': tier
        })

    return new_messages

def log_to_supabase(emails, db_uri):
    import psycopg2
    conn = psycopg2.connect(db_uri)
    cur = conn.cursor()

    logged = 0
    for email in emails:
        if email['tier'] == 'tier3':
            continue

        cur.execute("""
            INSERT INTO logs (kind, payload) VALUES ('gmail', %s::jsonb)
        """, (json.dumps({
            'gmail_id': email['id'],
            'thread_id': email['thread_id'],
            'sender': email['sender'],
            'subject': email['subject'],
            'date': email['date'],
            'snippet': email['snippet'],
            'tier': email['tier'],
            'time_logged': datetime.now(timezone.utc).isoformat(),
            'actioned': False
        }),))
        logged += 1

    conn.commit()
    cur.close()
    conn.close()
    return logged

def send_telegram_alert(email, bot_token, chat_id):
    import urllib.request
    tier = email['tier']
    if tier != 'tier1':
        return

    text = (
        f"Email from {email['sender']}\n"
        f"Subject: {email['subject']}\n"
        f"Preview: {email['snippet'][:200]}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps({'chat_id': chat_id, 'text': text}).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

def get_telegram_creds():
    with open('/root/.hermes/.env') as f:
        env = {}
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env.get('TELEGRAM_BOT_TOKEN'), env.get('TELEGRAM_ALLOWED_USERS', '').split(',')[0]

def main():
    env = load_env()
    db_uri = env.get('DATABASE_URI')
    if not db_uri:
        print("ERROR: DATABASE_URI not found")
        sys.exit(1)

    state = load_state()
    service = get_gmail_service()
    emails = fetch_new_emails(service, state)

    if not emails:
        print("No new emails.")
        return

    print(f"Found {len(emails)} new emails")
    t1 = [e for e in emails if e['tier'] == 'tier1']
    t2 = [e for e in emails if e['tier'] == 'tier2']
    t3 = [e for e in emails if e['tier'] == 'tier3']
    print(f"  Tier 1 (interrupt): {len(t1)}")
    print(f"  Tier 2 (digest): {len(t2)}")
    print(f"  Tier 3 (silent): {len(t3)}")

    logged = log_to_supabase(emails, db_uri)
    print(f"Logged {logged} emails to Supabase")

    if t1:
        try:
            bot_token, chat_id = get_telegram_creds()
            for email in t1:
                send_telegram_alert(email, bot_token, chat_id)
            print(f"Sent {len(t1)} Telegram alerts for Tier 1 emails")
        except Exception as e:
            print(f"Telegram alert failed: {e}")

    processed_ids = set(state.get('processed_ids', []))
    for email in emails:
        processed_ids.add(email['id'])
    state['processed_ids'] = list(processed_ids)[-500:]
    save_state(state)

main()
