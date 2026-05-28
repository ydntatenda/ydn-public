#!/usr/bin/env python3
"""
calendar_sync.py

Pulls events from Google Calendar for the next 7 days and writes them
to the Supabase `events` table. Runs as a cron job every 30 minutes.

Usage:
    python3 /root/calendar_sync.py

Environment:
    Reads DATABASE_URI from /root/ydn_db.env
    Uses /root/google_token.json for Google OAuth credentials
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

TOKEN_FILE = '/root/google_token.json'
ENV_FILE = '/root/ydn_db.env'
DAYS_AHEAD = 7

def load_env():
    if not os.path.exists(ENV_FILE):
        print(f"ERROR: {ENV_FILE} not found")
        sys.exit(1)
    env = {}
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def get_calendar_service():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    with open(TOKEN_FILE) as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes', ['https://www.googleapis.com/auth/calendar.readonly'])
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_data['token'] = creds.token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_data, f, indent=2)

    return build('calendar', 'v3', credentials=creds)

def fetch_events(service):
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=DAYS_AHEAD)
    result = service.events().list(
        calendarId='primary',
        timeMin=now.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy='startTime',
        maxResults=50
    ).execute()
    return result.get('items', [])

def upsert_events(events, db_uri):
    import psycopg2
    conn = psycopg2.connect(db_uri)
    cur = conn.cursor()

    inserted = 0
    skipped = 0

    for event in events:
        gcal_id = event.get('id')
        title = event.get('summary', 'Untitled')
        description = event.get('description', '')
        location = event.get('location', '')

        start = event.get('start', {})
        end = event.get('end', {})
        starts_at = start.get('dateTime') or start.get('date')
        ends_at = end.get('dateTime') or end.get('date')

        if not starts_at:
            continue

        category = categorize(title)

        cur.execute("""
            SELECT id FROM events WHERE gcal_id = %s
        """, (gcal_id,))
        existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE events SET title=%s, starts_at=%s, ends_at=%s,
                category=%s, description=%s, location=%s, updated_at=NOW()
                WHERE gcal_id=%s
            """, (title, starts_at, ends_at, category, description, location, gcal_id))
            skipped += 1
        else:
            cur.execute("""
                INSERT INTO events (title, starts_at, ends_at, category, description, location, gcal_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (title, starts_at, ends_at, category, description, location, gcal_id))
            inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    return inserted, skipped

def categorize(title):
    title_lower = title.lower()
    if any(w in title_lower for w in ['investor', 'vc', 'pitch', 'funding', 'demo day']):
        return 'investor'
    if any(w in title_lower for w in ['ministry', 'government', 'ocpo', 'dcdt', 'cape town', 'rosman', 'marivate']):
        return 'gov_partner'
    if any(w in title_lower for w in ['chidubem', 'tafadzwa', 'yusta', 'team', 'lattanye sync']):
        return 'team'
    if any(w in title_lower for w in ['p&t', 'parking', 'transportation', 'work']):
        return 'work_external'
    if any(w in title_lower for w in ['church', 'bible', 'prayer', 'faith']):
        return 'faith'
    if any(w in title_lower for w in ['gym', 'lift', 'workout', 'leg', 'push', 'pull']):
        return 'body'
    return 'other'

def main():
    env = load_env()
    db_uri = env.get('DATABASE_URI')
    if not db_uri:
        print("ERROR: DATABASE_URI not in .env")
        sys.exit(1)

    try:
        service = get_calendar_service()
    except Exception as e:
        print(f"ERROR: Google auth failed: {e}")
        sys.exit(1)

    events = fetch_events(service)
    print(f"Fetched {len(events)} events from Google Calendar")

    if not events:
        print("No upcoming events.")
        return

    try:
        inserted, skipped = upsert_events(events, db_uri)
        print(f"Done. Inserted: {inserted}, Updated: {skipped}")
    except Exception as e:
        print(f"ERROR: DB upsert failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
