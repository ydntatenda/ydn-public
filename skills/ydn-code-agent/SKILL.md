---
name: ydn-code-agent
description: Autonomous coding agent. Writes code and opens draft PRs for Lattanye, YDN, or Modus. Waits for Tatenda approval before tagging reviewer.
version: 1.0.0
author: ydn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ydn, github, coding, agents, pr, lattanye, modus]
    category: ydn
---

# ydn-code-agent

Autonomous coding agent for YDN. Triggered by explicit prompts, call summaries, or inferred signals from emails. Reads the target repo to understand the stack, writes the code, opens a draft PR, and sends Tatenda a link for approval. Does not tag a reviewer until Tatenda approves.

## When to invoke

Invoke when: (1) Tatenda says build this, write this, add this feature, fix this bug, or ship this alongside a description. (2) A call log contains a concrete feature decision for Lattanye, YDN, or Modus. (3) A Tier 1 email implies an unambiguous product gap. When in doubt on signals 2 or 3, ask Tatenda to confirm before writing code.

Do NOT invoke for vague ideas without a clear spec, personal tasks, or anything Tatenda has not sanctioned.

## Step 1: Identify the target repo

Lattanye: Owo, Oltapho, Salama, Leema, Khanya, Lattanye Data, SovOS SDK, government OS, agentic infrastructure for African governments. YDN: personal agent, skills, libraries, cron scripts, the bot. Modus: campus operations, GT Parking and Transportation, Aanya, the Modus MVP. If ambiguous, ask Tatenda. Repo owner is ydntatenda for all three. Confirm exact repo names with Tatenda - do not guess.

## Step 2: Read the repo structure

GET https://api.github.com/repos/ydntatenda/REPO_NAME/git/trees/HEAD?recursive=1 with Authorization: Bearer GITHUB_TOKEN. Read package.json, requirements.txt, pyproject.toml, or tsconfig.json to identify the stack. Read 2-3 existing source files to understand coding patterns and style. Do not write code until you have read at least the file tree and one representative source file.

## Step 3: Write and confirm the spec

Write a 3-5 line spec covering: what it does, where it lives in the repo, what it depends on, what existing files change. Send to Tatenda: Spec for [feature]: [spec]. Reply yes to proceed or give feedback. Wait for confirmation before writing code.

## Step 4: Write the code

Write complete working code in the correct language. Follow observed style and patterns. Include proper imports, type annotations if the repo uses them, comments matching repo convention, and error handling matching repo pattern. Do not write placeholder code or TODOs.

## Step 5: Create branch and open draft PR

1. Get default branch SHA: GET https://api.github.com/repos/ydntatenda/REPO_NAME/git/refs/heads/main
2. Create branch: POST https://api.github.com/repos/ydntatenda/REPO_NAME/git/refs with ref=refs/heads/ydn/FEATURE_NAME and sha from step 1
3. Create file: PUT https://api.github.com/repos/ydntatenda/REPO_NAME/contents/FILE_PATH with message, content (base64 encoded), and branch
4. Open draft PR: POST https://api.github.com/repos/ydntatenda/REPO_NAME/pulls with title, body, head=ydn/FEATURE_NAME, base=main, draft=true

PR body must include: what this does, why it was triggered, what the reviewer should check.

## Step 6: Send approval request to Tatenda

Draft PR ready: [title]. Repo: [repo]. Branch: ydn/[feature]. Link: [PR URL]. What it does: [one line]. Files changed: [list]. Reply approve to send to [reviewer] for review, or give feedback to revise. Wait for Tatenda response. Do not convert draft to ready-for-review until he approves.

## Step 7: On approval

1. Convert draft to ready: PATCH https://api.github.com/repos/ydntatenda/REPO_NAME/pulls/PR_NUMBER with draft=false
2. Request review: POST https://api.github.com/repos/ydntatenda/REPO_NAME/pulls/PR_NUMBER/requested_reviewers with reviewers list
3. Reviewer mapping: Lattanye = chidubem primary, YDN = ydntatenda, Modus = chidubem primary
4. Confirm to Tatenda: PR sent to [reviewer]. Link: [PR URL]

## Step 8: On feedback

Revise code based on feedback. Push updated file to same branch using file SHA from previous PUT. Tell Tatenda what changed and ask for approval again.

## GitHub API authentication

All calls use: Authorization: Bearer GITHUB_TOKEN, Accept: application/vnd.github+json, X-GitHub-Api-Version: 2022-11-28. Read GITHUB_TOKEN from environment at /root/.hermes/.env.

## Logging

After opening a PR write to logs table with kind = code_ship. Payload: repo, branch, pr_url, pr_number, feature_name, trigger_source (explicit/call/email), files_changed, reviewer, approved_by_tatenda (bool).

## Failure modes

Repo not found: ask Tatenda for correct name. Branch exists: append timestamp and retry. File conflict: read current file first, merge changes, retry PUT with correct SHA. PR creation fails: log error, tell Tatenda. Reviewer not found: ask Tatenda for their GitHub username.

## What NOT to do

Never push to main directly. Never open a non-draft PR without approval. Never tag a reviewer without approval. Never write placeholder code. Never infer a code ship from a vague conversation. Never write code in the wrong language.
