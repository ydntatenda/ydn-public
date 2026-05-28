---
name: ydn-email-draft
description: After a call is logged, drafts a follow-up email, sends to Tatenda for approval, sends via Gmail API on approval.
version: 1.0.0
author: ydn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ydn, email, gmail, follow-up, calls]
    category: ydn
---

# ydn-email-draft

Drafts follow-up emails after calls. Sends draft to Tatenda on Telegram for approval or revision. Sends via Gmail API only after Tatenda approves. Never auto-sends.

## When to invoke

Invoke automatically after ydn-call-ingest logs a call with contact_relationship of investor, gov_partner, advisor, or team. Not for personal or other calls unless Tatenda asks.

## Step 1: Read the call log

Extract from the call_log: contact_name, contact_relationship, key_decisions, tatenda_commitments, their_commitments, next_action. Find contact email from previous gmail logs: SELECT payload->>sender FROM logs WHERE kind = gmail AND LOWER(payload->>sender) LIKE contact_name_keyword ORDER BY created_at DESC LIMIT 1. If no email found, ask Tatenda.

## Step 2: Draft the email

Write in Tatenda voice. Direct, confident, no filler, no excessive pleasantries, short. Every sentence earns its place. Structure: one-line opener specific to what was discussed (not it was great to speak), 2-4 lines on decisions and next steps, one clear close with what happens next. Investor: slightly formal, reference vision, end with clear next step. Gov partner: professional, reference specific initiative, concrete timeline. Team: casual, direct, bullet points fine. Advisor: warm but direct. No em dashes. No AI-slop openers.

## Step 3: Send draft to Tatenda

Format:
Draft follow-up for [contact name]:
To: [email]
Subject: [subject]
[email body]
---
Reply send to send, or give feedback to revise.

Wait for response. Do not send until approved.

## Step 4: On approval

Send via Gmail API POST https://gmail.googleapis.com/gmail/v1/users/me/messages/send. Message must be RFC 2822 formatted and base64url encoded. Use google_token.json for auth, refresh if expired. After sending: log with kind = email_sent, payload including contact_name, contact_email, subject, body, call_log_id, sent_at.

## Step 5: On feedback

Revise based on feedback. Resend revised draft. Ask for approval again. If Tatenda says skip: log as email_skipped, move on.

## Failure modes

No email found and Tatenda does not provide: log as email_skipped, reason no_address. Gmail 401: refresh token and retry once. Other error: tell Tatenda, ask to retry or copy manually. Draft ignored 24+ hrs: one reminder, then log as email_pending.

## What NOT to do

Never send without approval. Never use generic openers. Never write more than 8 lines. Never guess email addresses.
