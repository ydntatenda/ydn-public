---
name: ydn-call-ingest
description: "Ingest a call summary, extract structured data, update ledger state, reflow day if needed."
version: 1.0.0
author: ydn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ydn, calls, logging, supabase, lattanye, reflow]
    category: ydn
---

# ydn-call-ingest

Handles call logging for YDN. When Tatenda reports a call via text or voice, the bot extracts structured data, writes to logs, updates lattanye_ledger state if relevant, asks 1-2 clarifying questions if ambiguous, and reflows the day if the call consumed significant block time.

## When to invoke

Invoke when Tatenda says he just got off a call, sends a voice note summarizing a call, says log a call or call with X or just spoke with X, or mentions a meeting that just ended. Do NOT invoke for scheduled calls not yet happened or for async messages and emails.

## Input modes

Accept text and voice both. Voice: transcribe first, then process same as text.

## Extraction logic

Extract these fields from raw input:
1. Who: name plus relationship category. Categories: investor, gov_partner, team, advisor, other.
2. Duration in minutes. If not stated, ask.
3. Key decisions made. Concrete decisions only, not discussion topics.
4. Tatenda commitments: things Tatenda said he would do, with deadline if stated.
5. Their commitments: things the other party said they would do.
6. Next action: single most important next step and who owns it.
7. Lattanye ledger impact: does this call update any open ledger item?
8. Day impact: did this call consume time from a scheduled block?

## Ambiguity protocol

After extracting, ask 1-2 clarifying questions only if genuinely ambiguous. Ask only when duration was not stated, a commitment deadline is unclear and matters, relationship category is unclear, or a decision vs discussion is unclear. Ask at most 2 questions. Wait for answer before writing the log. If nothing is ambiguous, write the log immediately.

## Log schema

Write to logs table with kind = call_log. Payload fields: contact_name, contact_relationship, duration_minutes, time_logged (ISO with Atlanta TZ), input_mode, raw_input, key_decisions (array), tatenda_commitments (array of action/deadline/deadline_stated), their_commitments (array), next_action, next_action_owner, lattanye_ledger_impact (bool), ledger_update_description, day_impact_minutes, reflow_triggered (bool), notes.

## Lattanye ledger update

After writing call log, if lattanye_ledger_impact is true, surface suggested update: "This call updates [contact] in the ledger. Suggested: [what changed]. Want me to note anything else?" Do NOT rewrite lattanye_ledger.md automatically. Exception: if a gating condition is touched, flag it explicitly.

## Confirmation message format

Call logged: [contact], [duration] min.
Extracted:
- Decision: [key decision]
- Your commitment: [action] by [deadline]
- Their commitment: [action]
- Next action: [action] ([owner], by [date])
Ledger: [what changed or no ledger impact].
[Block impact or no block impact].

## Reflow trigger

If day_impact_minutes over 120 AND call happened during Block A 06:30-07:30, Block B 13:30-16:30, or Block C 19:30-21:30: auto-invoke ydn-replan. If day_impact_minutes 60-120: ask if replan is wanted. If under 60: no reflow, no flag.

## Commitment tracking

Tatenda commitments from calls surface in next morning plan if deadline within 48 hrs, in Sunday review if not actioned, and as mid-week flag if deadline passes. Bot does not auto-complete commitments.

## Contact priority tiers

Investor and gov_partner: always surface ledger impact, check gating conditions, extract deadlines explicitly. Team: extract blockers resolved and SovOS progress. Advisor and other: extract decisions and commitments, no automatic ledger prompt unless relevant.

## Failure modes

Voice fails: ask for text. Contact unknown: log as other, ask. Duration missing: ask before logging. INSERT fails: run GRANT INSERT ON logs TO service_role. Replan fails: log call first, surface failure separately.

## What NOT to do

Do not log calls not yet happened. Do not rewrite lattanye_ledger.md automatically. Do not ask more than 2 clarifying questions. Do not auto-complete commitments. Do not trigger replan for calls under 60 min.
