---
name: ydn-observability
description: Weekly and monthly observability checks. Sunday relationship review, monthly Payer status, weekly call fragmentation tracking.
version: 1.0.0
author: ydn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ydn, observability, supabase, sunday-review, relationships]
    category: ydn
---

# ydn-observability

Runs three observability hooks on a schedule. Sunday weekly review, monthly Payer status check, and weekly call fragmentation tracking.

## Hook 1: Sunday weekly review (runs every Sunday at 19:00)

Invoke automatically every Sunday at 19:00. Also invoke if Tatenda says weekly review, Sunday review, or how was this week.

Compute: (1) Bodyweight trajectory: 7-day average vs prior 7-day average, target 0.5 kg/week gain. (2) Nutrition adherence: avg daily kcal vs 3500, avg protein vs 150g, meal skip rate. (3) Lift adherence: sessions this week vs target 6, flag if under 5. (4) Sleep adherence: avg bedtime vs 22:00, avg wake vs 05:00, avg hours. (5) Lattanye hours: estimated deep work hours vs 44.5 hr/week target, flag if under 35. (6) Fundraising pipeline: investor conversations this week, flag if zero. (7) August 15 gating conditions: which are unticked, weeks remaining. (8) Relationships check: if zero meaningful personal calls in 21 days, surface one gentle observation line only.

Sunday review Telegram format:
Weekly review, Sun [date]:
Body: [weight trend, lift count, nutrition avg]
Sleep: [avg bedtime, avg wake, avg hrs]
Lattanye: [estimated hrs, fundraising touches, gating conditions unticked]
Calls: [investor calls, gov partner calls, team syncs]
Flags: [0-3 specific flags, one line each]
This week priority: [single most important thing based on August 15 gating]
Under 15 lines total.

## Hook 2: Monthly Payer status check (runs first Sunday of each month)

Payer is paused for the summer by Tatenda explicit decision. Do not propose Payer work unless he raises it. On first Sunday of each month post one line only: Monthly Payer check: still paused per your decision. Any change? If not, nothing to do. If Tatenda says no change or ignores it: log as payer_status_check, status paused. If Tatenda raises Payer: engage fully, treat as active workstream.

## Hook 3: Weekly call fragmentation tracking (runs every Sunday as part of weekly review)

Check if calls are fragmenting deep work blocks. If more than 3 calls happened during Block B 13:30-16:30 this week: flag it. If total call time exceeded 5 hours this week: flag it. These are observations not directives.

## Failure modes

Logs empty for week: post no logs this week, restart logging tomorrow. Libraries not loaded: tell Tatenda to run load_libraries.py. learnings INSERT fails: GRANT INSERT ON learnings TO service_role. Hook 1 fires on wrong day: check day of week first, skip if not Sunday.

## What NOT to do

Do not run Hook 1 on weekdays. Do not surface Payer except first Sunday of month or if Tatenda raises it. Do not write more than 3 flags in Sunday review. Do not repeat flags from previous Sunday if nothing changed. Do not treat relationships check as a directive.