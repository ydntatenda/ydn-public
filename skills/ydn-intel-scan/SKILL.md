# ydn-intel-scan

## What this skill does
Runs a structured web intelligence scan across 8 domains relevant to the operator's startup. Surfaces max 5 actionable signals via Telegram. Triggered at 06:15 daily.

## Trigger
- Cron: 06:15 daily
- Manual: "Run intel scan" or "What's happening with [startup] today?"

## Execution steps

1. Load TAVILY_API_KEY from environment.
2. Run searches across all 8 domains.
3. Score and filter results against relevance criteria.
4. Format top 5 signals into the output format.
5. Send via Telegram.
6. Log to Supabase.

## Search domains

8 domains, configured by the operator:
- Domain 1-5: core product or market verticals
- Competitors: named competitors in target markets
- Partners: key stakeholders and partners
- Fundraising: relevant investors, accelerators, sector funding signals

## Relevance filter

Include if any are true:
- New contract, tender, or RFP in a domain the startup covers
- New data point usable as a pitch stat or case study
- Competitor mentioned in a target market context
- New regulation affecting the startup's sector
- Named partner appears in news
- Funding announcement relevant to the startup's sector

Exclude:
- Generic news with no market angle
- Already logged in last 7 days
- Opinion pieces with no new facts
- Markets outside the operator's target geography

## Output format

Delivered via Telegram at 06:15:

Intel — [date]

1. [DOMAIN] [headline with link]
   [one-line signal and implication]

(max 5 items)

## Supabase logging

kind: intel_scan
payload: date, items_surfaced, searches_run, items_filtered_out, sent_at

## Error handling

- Tavily API error: log, skip domain, continue.
- Telegram failure: retry once after 30 seconds.
- Zero results: send no-signal message, log normally.
