---
name: ydn-voice-memo
description: Processes voice memos that are not call summaries. Transcribes, understands intent, takes appropriate action or asks clarifying questions.
version: 1.0.0
author: ydn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ydn, voice, tasks, ideas, logging, lattanye]
    category: ydn
---

# ydn-voice-memo

Handles voice memos that are not call summaries. Transcribes the audio, understands what Tatenda is communicating, and takes the right action. Could be anything: task, idea, decision, concern, reflection, question, or thinking out loud. Bot figures out what it is and responds accordingly.

## When to invoke

Invoke when Tatenda sends a voice note that does not match call summary pattern. If voice note starts with just got off a call or I spoke with [name], route to ydn-call-ingest instead. All other voice notes: invoke this skill.

## Step 1: Transcribe

Use Hermes audio transcription. Preserve full transcript including hesitations - they sometimes carry meaning.

## Step 2: Understand intent

Classify what Tatenda is communicating. A memo can contain multiple intents. Identify all of them:

Task: something that needs to be done, by Tatenda or someone else, with or without a deadline.
Decision: something Tatenda has decided or is deciding.
Idea: new concept or feature not yet actionable but worth capturing.
Priority shift: Tatenda is changing what matters most right now.
Concern or blocker: something worrying him or blocking progress.
Reflection: thinking out loud with no clear action.
Question: something he wants looked up or reasoned through.

## Step 3: Take action based on intent

Task: extract task, owner, deadline. If Tatenda owns it and Lattanye-related, ask if it should go into next block focus. If someone else owns it, ask if Tatenda wants a message drafted. Log with kind = task_extracted.

Decision: capture and implications. If it affects lattanye_ledger, flag it for Sunday review. Log with kind = decision_logged.

Idea: capture it. Ask which domain (Lattanye vertical, Payer, Modus, personal). Store it. Surface in next relevant block. Log with kind = idea_captured.

Priority shift: offer to replan. If yes, invoke ydn-replan.

Concern or blocker: acknowledge. If team blocker ask if Tatenda wants a message drafted. If pipeline concern flag for Sunday review. Log with kind = concern_logged.

Reflection: capture in learnings table, domain = personal, confidence = low. Do not over-interpret.

Question: answer directly using Supabase context and libraries. Web search if needed.

## Step 4: Respond to Tatenda

Heard: [one line summary]
[For each action taken or question asked, one line each]

Tight response. If 3+ actions use a short list.

## Step 5: Clarifying questions

Ask only when genuinely ambiguous. One question at a time. Max 2 questions. Do not ask what can be inferred from context.

## Logging

Every voice memo: kind = voice_memo, payload: transcript, intents_identified, actions_taken, time_logged. Then log each extracted item separately per schemas above.

## Failure modes

Transcription fails: ask Tatenda to type key points. Too short to classify: ask what it was about. Multiple conflicting priorities: surface them, ask Tatenda to rank. Voice note in Shona or another language: transcribe and respond in same language.

## What NOT to do

Never ignore a voice memo. Never take irreversible actions without confirming first. Never over-interpret reflections as decisions. Never ask more than 2 questions at once. Never respond with a wall of text.
