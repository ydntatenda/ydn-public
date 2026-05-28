---
name: ydn-log
description: "Write structured log entries to Tatenda's logs table for any observable event."
version: 1.0.0
author: ydn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ydn, logging, supabase, observability, telegram]
    category: ydn
---

# ydn-log

The logging primitive for YDN. Every observable event in Tatenda's life that the bot witnesses, ingests, or initiates gets a row in the logs table.

## When to use this skill

ALWAYS log when one of these happens:

- Tatenda taps an inline button on Telegram, kind = button
- Tatenda sends a voice note, kind = voice
- Tatenda sends freeform text reporting an event, kind = text
- Bot ingests a calendar event, kind = calendar
- Bot ingests a Gmail message from a priority contact, kind = gmail
- Health/wearable signal arrives, kind = health
- A cron job fires, kind = system
- Tatenda logs a meal, kind = meal_log
- A meal slot passes with no log, kind = meal_skip
- Tatenda logs a workout, kind = workout_log
- A workout is skipped, kind = workout_skip
- Tatenda logs bedtime/wake, kind = sleep_log
- Bedtime slips past 22:30, kind = sleep_skip
- Tatenda logs a call summary, kind = call_log
- Tatenda logs an investor touch, kind = fundraising_touch
- Tatenda logs a government partner touch, kind = gov_partner_touch
- Tatenda eats a cheat meal, kind = cheat_meal

Bot proposes a nudge -> write to interventions table, not logs.
Tatenda overrides a bot push -> write to pushback_log table, not logs.

If unsure which kind to use, default to text with a subtype field in the payload.

## Schema

logs table has: id (uuid pk), kind (text), payload (jsonb), event_id (uuid nullable), created_at (timestamptz default now()).

## How to write a log

Use mcp_supabase_execute_sql to INSERT. Example for a meal log:

INSERT INTO logs (kind, payload) VALUES ('meal_log', '{"meal_slot":"breakfast","time_logged":"2026-05-27T05:35:00-04:00","input_mode":"text","raw_input":"4 eggs, 80g oats with milk, banana, PB","total_kcal":930,"total_protein_g":47,"matches_planned":true,"planned_meal_label":"Breakfast A"}'::jsonb);

Payload schema varies by kind. Refer to the relevant library:
- meal_log, meal_skip, cheat_meal: nutrition_targets.md Part 4
- workout_log, workout_skip: workout.md Tracking section
- sleep_log, sleep_skip: sleep.md Tracking section
- fundraising_touch, gov_partner_touch, call_log: lattanye_ledger.md

To read a library before logging if uncertain:

SELECT content FROM libraries WHERE name = 'meal_log_kind_library' ORDER BY version DESC LIMIT 1;

## Payload conventions

- Always include time_logged as ISO timestamp with Atlanta TZ offset (-04:00 summer, -05:00 winter)
- Always include raw_input for user-triggered logs
- Set input_mode to one of: text, voice, picture, button, system
- Numeric measurements use numeric values not strings
- Free-text observations go in notes field
- Add confidence (high/medium/low) for estimates if relevant

## Confirmation behavior

After writing a log, briefly confirm to Tatenda. Summarize, don't echo. Examples:

"Logged breakfast: 930 kcal, 47g protein. On target. Next prompt at 09:30."

"Logged lunch at 600 kcal, 25g protein. 250 kcal and 15g under target. Pre-lift snack scales up to 500 kcal."

## Reading logs

Recent logs:
SELECT created_at, kind, payload FROM logs ORDER BY created_at DESC LIMIT 20;

Today's meals:
SELECT * FROM logs WHERE kind = 'meal_log' AND created_at >= CURRENT_DATE ORDER BY created_at;

Running daily totals:
SELECT SUM((payload->>'total_kcal')::int) AS kcal_so_far, SUM((payload->>'total_protein_g')::numeric) AS protein_so_far, COUNT(*) AS meals_logged FROM logs WHERE kind = 'meal_log' AND created_at >= CURRENT_DATE;

## Failure modes

1. Permission denied -> run GRANT INSERT ON logs TO service_role in Supabase SQL editor.
2. Malformed JSON -> use ::jsonb casting, ensure valid JSON.
3. Foreign key violation on event_id -> set null or create events row first.
4. Duplicate log within 60s same kind+payload -> likely double-tap, don't insert.

## What NOT to log

- Bot's internal reasoning
- Repeating confirmations
- Outbound nudges (use interventions table)
- Disagreements (use pushback_log table)

When in doubt: log it. Logs are cheap, missing data is expensive.
