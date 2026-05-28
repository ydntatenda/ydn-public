#!/usr/bin/env python3
"""
meeting_prep.py

Runs every 5 minutes via cron. Checks for Tier 1 calendar events starting
in 25-35 minutes. If found and not yet briefed, composes a meeting prep
brief from contact history and sends it to Tatenda via Telegram.

Tier 1 events: investor, gov_partner (set by calendar_sync.py categorization)

Cron: */5 * * * * python3 /root/meeting_prep.py >> /root/ydn_cron.log 2>&1
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

ENV_FILE = '/root/ydn_db.env'
STATE_FILE = '/root/meeting_prep_state.json'
HERMES_ENV = '/root/.hermes/.env'
TIER1_CATEGORIES = ['investor', 'gov_partner']
WINDOW_MIN = 25
WINDOW_MAX = 35

def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {'briefed_event_ids': []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_upcoming_tier1_events(db_uri):
    import psycopg2
    conn = psycopg2.connect(db_uri)
    cur = conn.cursor()
    now = datetime.now(timezone.utc)
    window_start = now + timedelta(minutes=WINDOW_MIN)
    window_end = now + timedelta(minutes=WINDOW_MAX)
    cur.execute("""
        SELECT id, title, starts_at, ends_at, description, location, category
        FROM events
        WHERE category = ANY(%s)
        AND starts_at >= %s
        AND starts_at <= %s
        ORDER BY starts_at
    """, (TIER1_CATEGORIES, window_start, window_end))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    events = []
    for row in rows:
        events.append({
            'id': str(row[0]),
            'title': row[1],
            'starts_at': row[2],
            'ends_at': row[3],
            'description': row[4] or '',
            'location': row[5] or '',
            'category': row[6]
        })
    return events

def get_contact_history(db_uri, contact_name):
    import psycopg2
    conn = psycopg2.connect(db_uri)
    cur = conn.cursor()
    name_lower = contact_name.lower().split()[0]
    cur.execute("""
        SELECT kind, payload, created_at
        FROM logs
        WHERE (
            kind IN ('call_log', 'fundraising_touch', 'gov_partner_touch')
            AND LOWER(payload->>'contact_name') LIKE %s
        )
        OR (
            kind = 'gmail'
            AND (
                LOWER(payload->>'sender') LIKE %s
                OR LOWER(payload->>'subject') LIKE %s
            )
        )
        ORDER BY created_at DESC
        LIMIT 10
    """, (f'%{name_lower}%', f'%{name_lower}%', f'%{name_lower}%'))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    history = []
    for row in rows:
        history.append({
            'kind': row[0],
            'payload': row[1],
            'created_at': row[2]
        })
    return history

def get_open_commitments(db_uri, contact_name):
    import psycopg2
    conn = psycopg2.connect(db_uri)
    cur = conn.cursor()
    name_lower = contact_name.lower().split()[0]
    cur.execute("""
        SELECT payload, created_at
        FROM logs
        WHERE kind = 'call_log'
        AND LOWER(payload->>'contact_name') LIKE %s
        AND created_at >= NOW() - INTERVAL '30 days'
        ORDER BY created_at DESC
        LIMIT 5
    """, (f'%{name_lower}%',))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    commitments = {'tatenda': [], 'them': []}
    for row in rows:
        payload = row[0]
        if isinstance(payload, str):
            payload = json.loads(payload)
        for c in payload.get('tatenda_commitments', []):
            commitments['tatenda'].append(c)
        for c in payload.get('their_commitments', []):
            commitments['them'].append(c)
    return commitments

def compose_brief(event, history, commitments):
    title = event['title']
    starts_at = event['starts_at']
    if hasattr(starts_at, 'strftime'):
        time_str = starts_at.strftime('%H:%M')
    else:
        time_str = str(starts_at)[:16]

    lines = []
    lines.append(f"Meeting brief: {title}")
    lines.append(f"Starts at {time_str}. 30 minutes out.")
    lines.append("")

    if event['location']:
        lines.append(f"Location: {event['location']}")
        lines.append("")

    if history:
        lines.append("Last contact:")
        last = history[0]
        payload = last['payload']
        if isinstance(payload, str):
            payload = json.loads(payload)
        kind = last['kind']
        if kind == 'call_log':
            decisions = payload.get('key_decisions', [])
            if decisions:
                lines.append(f"- Call: {decisions[0]}")
            else:
                lines.append(f"- Call logged {str(last['created_at'])[:10]}")
        elif kind == 'gmail':
            lines.append(f"- Email: {payload.get('subject', 'no subject')} ({str(last['created_at'])[:10]})")
        elif kind in ('fundraising_touch', 'gov_partner_touch'):
            lines.append(f"- Touch logged {str(last['created_at'])[:10]}")
        lines.append("")

    if commitments['tatenda']:
        lines.append("Your open commitments:")
        for c in commitments['tatenda'][:3]:
            action = c.get('action', '') if isinstance(c, dict) else str(c)
            deadline = c.get('deadline', '') if isinstance(c, dict) else ''
            if deadline:
                lines.append(f"- {action} (by {deadline})")
            else:
                lines.append(f"- {action}")
        lines.append("")

    if commitments['them']:
        lines.append("Their open commitments:")
        for c in commitments['them'][:3]:
            action = c.get('action', '') if isinstance(c, dict) else str(c)
            lines.append(f"- {action}")
        lines.append("")

    lines.append("What do you need to get out of this meeting?")

    return "\n".join(lines)

def send_telegram(message, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps({'chat_id': chat_id, 'text': message}).encode()
    req = urllib.request.Request(
        url, data=data,
        headers={'Content-Type': 'application/json'}
    )
    urllib.request.urlopen(req, timeout=10)

def main():
    env = load_env(ENV_FILE)
    db_uri = env.get('DATABASE_URI')
    if not db_uri:
        print("ERROR: DATABASE_URI not found")
        sys.exit(1)

    hermes_env = load_env(HERMES_ENV)
    bot_token = hermes_env.get('TELEGRAM_BOT_TOKEN')
    chat_id = hermes_env.get('TELEGRAM_ALLOWED_USERS', '').split(',')[0].strip()

    if not bot_token or not chat_id:
        print("ERROR: Telegram credentials not found")
        sys.exit(1)

    state = load_state()
    briefed_ids = set(state.get('briefed_event_ids', []))

    events = get_upcoming_tier1_events(db_uri)

    if not events:
        return

    for event in events:
        if event['id'] in briefed_ids:
            continue

        title = event['title']
        print(f"Preparing brief for: {title}")

        history = get_contact_history(db_uri, title)
        commitments = get_open_commitments(db_uri, title)
        brief = compose_brief(event, history, commitments)

        send_telegram(brief, bot_token, chat_id)
        print(f"Brief sent for: {title}")

        briefed_ids.add(event['id'])

    state['briefed_event_ids'] = list(briefed_ids)[-200:]
    save_state(state)

main()
