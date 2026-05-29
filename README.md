# ydn

ydn is the system I built to run my life. It watches every domain at once, holds the full context in one place, and acts without being asked. Everything below is live right now.

---

## Body

- Tells me exactly what to make for each meal based on what's in my kitchen, sized to hit a dynamically recalibrated calorie and protein target
- Logs every meal I eat, estimates macros, tracks running daily totals, adjusts every remaining meal slot if I over or under-ate
- Tells me when I'm behind on protein and forces a shake
- Knows my full lifting program and body targets
- Knows my soda cap, fast-food rule, no-weekday-eat-out rule and will flag violations
- Nudges me toward bed at 21:30, 22:00, 22:30, 23:00
- Logs my bedtime and wake time, tracks sleep quality
- Reduces tomorrow's lift volume if I slept under 6 hours

## Planning

- Generates a structured daily plan on demand or when reality breaks the template
- Knows today's lift type, meal slots, working hours, scheduled events
- Reflows the rest of the day in real time when a call runs long or a block gets eaten
- Surfaces the top 3 actionable next items at any moment
- Delivers tomorrow's plan at 21:40 every night as part of wind-down

## Calls

- Ingests call summaries via text or voice
- Extracts who, duration, decisions made, my commitments, their commitments, next action and owner
- Asks 1-2 clarifying questions if something is ambiguous
- Flags when a commitment I made has a deadline within 48 hours
- Auto-triggers a replan if a call consumed more than 2 hours of a deep work block

## Work

- Knows every stakeholder, their status, last touch, next action
- Tracks every stakeholder touch end-to-end — stage, last contact, open commitments, next action; auto-drafts follow-up emails after calls and flags conversations that have gone cold
- 30 minutes before any meeting, sends a full brief — who I'm meeting, their background, last conversation summary, open commitments on both sides, and what I need to get out of the room
- When I forward a bookmark from X, does a deep dive on the full content, sends a summary of what it's about and exactly how it's relevant to what I'm building, then tags it by domain and stores it — surfacing it again proactively when it matters
- Has coding agents that ship code autonomously. I can prompt them via voice or text, but they also trigger themselves: a call summary mentions a new feature, an investor email implies a product gap, a meeting brief surfaces something unbuilt. The agents write the code, open a pull request, and tag the right person to review
- Flags stale investor conversations (>14 days no contact)
- Flags stale blocked items (>7 days no movement)
- Flags stale decisions (>21 days no decision)

## Intelligence

- Every morning at 06:15, scans the web across 8 domains for developments that could affect the startup — market signals, competitor activity, regulatory shifts, partner mentions, funding announcements
- Filters everything through a relevance test — no noise, only actionable signals
- Delivers a structured intel brief to Telegram before the morning work block starts
- Logs every scan; weekly review surfaces the week's top signals and flags domains going quiet

## Inbox and calendar

- Watches my Gmail every 15 minutes
- Classifies every email into Tier 1 (investor, partner — immediate alert), Tier 2 (team — silent log), Tier 3 (everything else — ignored)
- Pings me the moment an investor or partner emails me
- Syncs my Google Calendar every 30 minutes
- Ingests new events and checks for conflicts with template blocks

## Learning and observability

- At 22:30 every night, reviews the full day's logs across every domain, extracts patterns, writes insights to a learnings table, posts a day summary
- Every Sunday at 19:00, runs a full weekly review: body trajectory, nutrition adherence, lift count, sleep averages, work hours, fundraising touches, target status
- Detects when any activities are fragmenting deep work blocks and flags it
- Surfaces a gentle flag if I haven't had a non-work call scheduled for 21 days
- Pushes back when I override the template instead of complying
- Logs every override so Sunday review can surface the pattern

---

## Stack

- **Hermes** — agentic framework, runs on DigitalOcean
- **Supabase** — all state, logs, learnings, ledger
- **Google OAuth** — Calendar + Gmail
- **Telegram** — mobile interface
- **GitHub** — code agent PR workflow

## Skills

| Skill | What it does |
|---|---|
| `ydn-log` | Logs every observable event to Supabase |
| `ydn-replan` | Structured daily plan generation and reflow |
| `ydn-call-ingest` | Call extraction, ledger updates, reflow trigger |
| `ydn-nightly-learning` | 22:30 daily review, writes to learnings table |
| `ydn-observability` | Weekly review and fragmentation tracking |
| `ydn-bookmark` | X bookmark deep dive via screenshot or pasted text |
| `ydn-code-agent` | Autonomous PR shipping with approval flow |
| `ydn-email-draft` | Follow-up email drafting after calls |
| `ydn-voice-memo` | Voice memo transcription and intent classification |

---

*Libraries (workout, nutrition, sleep, work ledger) are personal and kept in a private repo.*

---

## What's not here

The `libraries/` folder contains sanitized example files showing structure and schema. Real libraries with personal targets, schedules, and operational data are kept in a private repo. Libraries are structured markdown documents that Hermes reasons over — they contain personal targets, schedules, and operational data (body metrics, calorie targets, fundraising pipeline, stakeholder details). The structure is visible in `scripts/load_libraries.py`. If you're building something similar, you'd replace these with your own.

| `ydn-intel-scan` | Morning web scan across 8 domains — surfaces actionable signals relevant to the startup via Telegram at 06:15 daily |
