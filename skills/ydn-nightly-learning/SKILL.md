---
name: ydn-nightly-learning
description: Nightly automated review of the day logs. Extracts patterns and insights, writes to learnings table, posts summary to Tatenda.
version: 1.0.0
author: ydn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ydn, learning, supabase, cron, observability]
    category: ydn
---

# ydn-nightly-learning

Runs at 22:30 every night. Reviews the day logs across all domains, extracts patterns and insights, writes to the learnings table, and posts a brief summary to Tatenda as part of the wind-down.

## When to invoke

Invoke automatically at 22:30 via cron. Also invoke if Tatenda says what did I learn today, daily review, or what did today look like. Do NOT invoke mid-day or repeatedly. Once per day at night.

## What to review

Query all of today logs: SELECT created_at, kind, payload FROM logs WHERE created_at >= CURRENT_DATE ORDER BY created_at;

Review across five domains: (1) Body: did workout happen, how did nutrition track vs target, did last night sleep affect today. (2) Lattanye: how many hours of deep work actually happened vs template, what got done, what got skipped. (3) Calls: any calls logged today, were commitments made, are any deadlines within 48 hrs. (4) Sleep: what time is it now vs 22:00 target, is wind-down on track. (5) August 15 gating: any movement today on gating conditions.

## What to extract

For each insight write a learning row with fields: domain (body/lattanye/sleep/calls/system), observation (what actually happened in plain language), pattern (one-off or recurring, check last 7 days), confidence (high/medium/low), actionable (bool), action_suggested (if actionable, what specifically should change), superseded_by (null by default).

## Learning schema

INSERT INTO learnings (domain, observation, pattern, confidence, actionable, action_suggested) VALUES with the extracted fields. Use the above field definitions.

## Pattern detection

Before writing a learning, check if the same pattern appeared in the last 7 days. If the same pattern appears 3 or more times in 7 days, upgrade it from observation to pattern and set actionable = true with a protocol-change suggestion.

## Telegram summary

After writing learnings, post brief summary. Format:

Day review, [day date]:
Body: [one line]
Lattanye: [one line]
Calls: [one line]
Sleep: [one line]
[0-2 flagged patterns if any]
Tomorrow: [one line, what first Lattanye focus should be]

Keep under 10 lines total. This is a wind-down message not a report.

## Failure modes

No logs today: post no logs recorded today. Learnings INSERT fails: GRANT INSERT ON learnings TO service_role. Cron fires during restart: log missed, Sunday review will catch the gap.

## What NOT to do

Do not write more than 5 learnings per night. Do not repeat learnings already written in last 3 days for same pattern. Do not post a long report. Do not wake Tatenda up if past 22:30, keep message short and end with Sleep.