---
name: ydn-replan
description: "Generate or regenerate Tatenda's daily plan, structured but flexible, written to the plans table."
version: 1.0.0
author: ydn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ydn, planning, supabase, telegram, reflow]
    category: ydn
---

# ydn-replan

The planning primitive for YDN. Composes a structured-but-flexible plan for the day (or remaining day), writes it to the plans table, and surfaces it to Tatenda. Used for the 21:40 wind-down daily plan delivery and for mid-day reflow when reality breaks the template.

## When to invoke

Invoke ydn-replan in three situations:

1. **Explicit user request**: Tatenda sends "/replan", "replan my day", "rebuild the plan", "what should I do now", or any variant asking for the day's plan.
2. **Wind-down delivery (21:40)**: triggered by cron or scheduled prompt. Composes tomorrow's plan.
3. **Reality breaks the template** — automatically when one of these is detected:
   - A call has been logged that consumed 2+ hours of a deep block
   - A workout has been logged as skipped
   - Bedtime slipped >30 min past 22:00 (affects tomorrow's lift load)
   - A calendar event was ingested that conflicts with a template block

Do NOT regenerate the plan on every meal log, every minor event, or on a fixed schedule like every hour. The template is the default. The plan only regenerates when there's a real reason.

## Plan format: structured but flexible

The plan has three components, in order:

### Component 1: Fixed blocks (anchored, non-negotiable)
Listed with time-of-day. These come from the template directly and only move under exceptional circumstances:
- Sleep (22:00-05:00)
- Faith (05:15-05:45 + 21:50-22:00)
- Mind reading (05:45-06:30)
- P&T job (08:00-13:00 Mon-Thu)
- Lift (17:00-18:30 Mon-Sat) + post-lift bath
- Saturday church (05:00-06:00)
- Wind-down protocol (21:30-22:00)
- Meals: breakfast 05:30, snack 09:30, lunch 13:00, pre-lift 16:30, dinner 18:30, pre-bed 21:00

### Component 2: Lattanye blocks (flexible within the day)
Lattanye gets 44.5 hrs/week. On weekdays this lands in three blocks:
- Block A: 06:30-07:30 (1h, pre-P&T)
- Block B: 13:30-16:30 (3h, post-P&T)
- Block C: 19:30-21:30 (2h, evening comms/async/planning)

These are listed by their target time slot, but with a specific focus task pulled from lattanye_ledger.md based on what's most important for August 15 gating conditions.

### Component 3: What's next (the actionable view)
At the bottom of the plan, list the next 1-3 actionable items in chronological order. This is what Tatenda actually reads first and acts on.

## Plan composition logic

When called, do the following:

1. Read the current time to know where we are in the day.
2. Read the relevant libraries for context (cheap, do this every time):
   SELECT name, content FROM libraries WHERE name IN ('workout', 'nutrition_targets', 'sleep', 'lattanye_ledger') ORDER BY name;
3. Read today's logs to see what's already happened:
   SELECT created_at, kind, payload FROM logs WHERE created_at >= CURRENT_DATE ORDER BY created_at;
4. Check today's calendar events (once ydn-calendar-sync exists):
   SELECT id, title, starts_at, ends_at, category FROM events WHERE starts_at::date = CURRENT_DATE ORDER BY starts_at;
5. Determine day-of-week to pick the right daily shape from sleep.md / workout.md / nutrition_targets.md.
6. Compose the plan:
   - Fixed blocks come from the template, adjusted for day-of-week
   - Lattanye block focus tasks come from lattanye_ledger.md "August 15 gating conditions" + "blocked/waiting on" + "decision queue"
   - Workout type (Push/Pull/Leg) comes from workout.md split + day-of-week
   - Meal slots come from nutrition_targets.md schedule
7. Write the plan to plans table with horizon='day', body as jsonb, reasoning as a one-paragraph narrative, generated_by='sonnet'.
8. Reply to Tatenda with the rendered plan.

## Output format (what to send to Tatenda)

The Telegram reply should be readable, not raw JSON. Render the plan as a structured message:

Plan for Wed May 27 (Phase 1)

Fixed:
- 05:00 wake
- 05:15-05:45 faith
- 05:30 breakfast (logged, 920 kcal)
- 05:45-06:30 mind
- 08:00-13:00 P&T
- 17:00-18:30 lift (Leg day)
- 21:30-22:00 wind-down
- 22:00 lights off

Lattanye:
- Block A 06:30-07:30: Draft 3 cold investor emails
- Block B 13:30-16:30: SovOS SDK v0 spec draft (Aug 15 gating)
- Block C 19:30-21:30: Comms with Chidubem + Yusta, plan tomorrow

Meals remaining: Snack 1, Lunch, Pre-lift, Dinner, Pre-bed

Next:
- 09:30 Snack 1
- 13:00 Lunch
- 13:30 Lattanye block B

Keep it tight. No prose padding. No "Here is your plan!" preamble. Just the plan.

If the trigger was a reflow (call happened, workout skipped, etc.), prepend one line explaining what changed.

## Reflow logic specifically

When the bot detects a real disruption, the reflow is targeted:

- Call consumed deep block time: shrink the affected block's focus task scope. Don't push it elsewhere unless the call eliminated >50% of the slot.
- Workout skipped: if illness/injury, no reflow needed beyond a note. If skipped for time, propose the restructure per workout.md skip protocol.
- Calendar event added: insert into events list, check for conflict. Propose moving the event or compressing the block.
- Bedtime missed: affect tomorrow's plan, not today's. Reduce tomorrow's lift volume per workout.md hard rule.

## Composing the focus tasks

Lattanye block focus tasks come from lattanye_ledger.md. Priority order:

1. Unticked gating conditions for August 15 (Part 1 of lattanye_ledger)
2. Stale blocked/waiting on items (>7 days no movement)
3. Stale decision queue items (>21 days no decision)
4. Stale pipeline entries (>14 days no contact)
5. Modus directive: build and grow MVP - at least one Modus task per week

Generic "do Lattanye work" is not a focus task. Each block should have a specific output it's pointed at.

## Storing the plan

Always INSERT a new row into plans, don't UPDATE existing rows. Latest row is the active plan. Old plans stay for audit.

## Failure modes

1. No libraries loaded -> tell Tatenda to run scripts/load_libraries.py
2. Logs query empty -> day just started, compose from template
3. Calendar empty -> ydn-calendar-sync hasn't run, compose without events, note the gap
4. Insert fails on plans -> permission, run GRANT INSERT ON plans TO service_role
5. Past 22:00 -> day is over, offer tomorrow's plan instead

## What NOT to do

- Don't compose ignoring the libraries
- Don't list every meal/block in next_actions, top 3 only
- Don't write prose explanations of why each block exists
- Don't propose plans that violate hard rules in workout/nutrition/sleep
- Don't fight the template without naming why
- Don't regenerate more than once per hour unless explicitly asked or a real disruption

## Tone

Match SOUL.md. Direct, short sentences, no em dashes, no servile filler. State the plan.
