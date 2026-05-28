---
name: ydn-bookmark
description: Deep dive on X bookmarks. Accepts URL plus pasted text, or a screenshot. Summarizes, tags by domain, stores in Supabase, surfaces proactively.
version: 1.0.0
author: ydn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ydn, bookmarks, x, twitter, research, supabase]
    category: ydn
---

# ydn-bookmark

Handles X/Twitter bookmarks from Tatenda. Accepts two input modes: (A) URL plus pasted text, or (C) a screenshot of the post. Does a deep dive, sends a summary to Tatenda, tags by domain, stores in Supabase, and surfaces proactively when relevant.

## When to invoke

Invoke when Tatenda sends any of these: a URL containing x.com or twitter.com alongside pasted text, a screenshot of an X post, or says bookmark this, save this, or forward this alongside either. Do NOT invoke for a bare URL with no text or image attached - instead tell Tatenda that X blocks direct fetch and ask him to paste the text or send a screenshot.

## Input mode detection

Mode A - URL plus text: Tatenda sends an x.com URL and also pastes the post text in the same message or immediately after. Use the pasted text as the content. Ignore the URL for fetching.

Mode C - Screenshot: Tatenda sends an image of an X post. Use vision to read the full text of the post including the author name, handle, and all text in the post. If it is a thread screenshot, read all visible text.

If Tatenda sends just a bare URL with no text or image: reply with one line - X blocks direct fetch. Paste the post text or send a screenshot and I will do the full deep dive.

## Deep dive (both modes)

After extracting the content, reason across four questions before composing the summary:

1. What is this actually about? Not just the surface topic but the underlying idea, argument, or insight. If it is a thread, what is the through-line?

2. Why did Tatenda bookmark this? What in this post likely caught his attention given what he is building - Lattanye (AI-native agentic OS for African governments), Payer (USD neobank for Zimbabwean diaspora), Modus (campus operations agents at GT)?

3. How is this relevant to his work? Be specific. If it maps to a specific Lattanye vertical (Owo, Oltapho, Salama, Leema, Khanya, Lattanye Data), a challenge (fundraising, government partnerships, technical architecture, African markets), or a personal priority (August 15 commitment, SovOS SDK), name it.

4. What should Tatenda do with this? Background reading, framework to apply, person to follow up with, competitive signal, tactical idea, share with Chidubem, or just context to hold?

## Summary format

Send to Tatenda via Telegram:

Bookmark saved: [author name, @handle]

What it is: [2-3 sentences on what the post is actually saying]

Why it matters for you: [2-3 sentences connecting specifically to Lattanye, Payer, Modus, or his August 15 commitment. Not generic - named and specific.]

What to do with it: [one line]

Domain: [fundraising, technical, african-markets, government, product, personal, competitive, or other]

Keep under 15 lines. No padding.

## Storage

Write to logs table with kind = bookmark. Payload: url (if provided), author_name, author_handle, content_summary, relevance_summary, action, domain, raw_content (full extracted text truncated to 2000 chars), input_mode (text or screenshot), time_logged (ISO Atlanta TZ), surfaced_count (0).

## Proactive surfacing

Before a Lattanye deep work block: if block focus is fundraising and there are unsurfaced fundraising bookmarks, surface the most relevant one. Max 1 per block.

During Sunday weekly review: surface top 2 most relevant bookmarks from the past week if more than 3 exist unsurfaced.

When Tatenda asks about bookmarks (what did I bookmark about X, find my bookmarks on Y): query logs for kind = bookmark and return top 3 most relevant sorted by created_at DESC.

## Failure modes

Bare URL with no content: ask for text or screenshot. Vision cannot read the screenshot clearly: ask Tatenda to paste the text. INSERT fails: GRANT INSERT ON logs TO service_role.

## What NOT to do

Do not attempt to fetch x.com or twitter.com URLs directly. Do not summarize without the relevance analysis. Do not store without sending the summary first. Do not surface more than 1 bookmark per deep work block. Do not ask Tatenda to explain why he bookmarked it - figure it out.