"""
load_libraries.py

Mirror markdown library files from ~/ydn/libraries/ into the Supabase `libraries` table.

Each library is versioned. Running this script after edits will:
- Read every .md file in ~/ydn/libraries/
- Check the current latest version in the `libraries` table for each library name
- If the file's content differs from the latest stored version (or no version exists), insert a new row with version = previous + 1
- If the file content is identical to the latest stored version, skip (no change)

Usage:
    cd ~/ydn
    python scripts/load_libraries.py

Environment:
    Reads SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from ~/ydn/.env.local

The `libraries` table schema (from the YDN Supabase schema):
    id              uuid PK
    name            text
    version         int (default 1)
    content         text
    parsed          jsonb (nullable)
    created_at      timestamptz
    unique (name, version)
"""

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    from supabase import create_client
except ImportError:
    print("Missing dependencies. Run: pip install python-dotenv supabase")
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent.parent
LIBRARY_DIR = REPO_ROOT / "libraries"
ENV_FILE = REPO_ROOT / ".env.local"

# Expected library names. Files not in this list are ignored.
EXPECTED_LIBRARIES = [
    "workout",
    "nutrition_targets",
    "sleep",
    "lattanye_ledger",
    "study_tactics",
]


def load_env():
    """Load .env.local from the repo root."""
    if not ENV_FILE.exists():
        print(f"ERROR: {ENV_FILE} not found.")
        sys.exit(1)
    load_dotenv(ENV_FILE)


def get_client():
    """Create the Supabase client using the service role key."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("ERROR: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing from .env.local")
        sys.exit(1)
    return create_client(url, key)


def get_latest_version(client, name):
    """Return (version_int, content_str) for the latest version of `name`, or (0, None) if no rows."""
    result = (
        client.table("libraries")
        .select("version, content")
        .eq("name", name)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )
    if result.data:
        row = result.data[0]
        return row["version"], row["content"]
    return 0, None


def insert_library(client, name, version, content):
    """Insert a new library row."""
    client.table("libraries").insert(
        {
            "name": name,
            "version": version,
            "content": content,
        }
    ).execute()


def main():
    load_env()
    client = get_client()

    if not LIBRARY_DIR.exists():
        print(f"ERROR: {LIBRARY_DIR} not found.")
        sys.exit(1)

    print(f"Loading libraries from {LIBRARY_DIR}")
    print(f"Targeting Supabase: {os.environ['SUPABASE_URL']}")
    print()

    inserted = 0
    skipped = 0
    missing = 0

    for name in EXPECTED_LIBRARIES:
        path = LIBRARY_DIR / f"{name}.md"
        if not path.exists():
            print(f"  [MISSING] {name}.md — file not found, skipping")
            missing += 1
            continue

        content = path.read_text(encoding="utf-8")
        prev_version, prev_content = get_latest_version(client, name)

        if prev_content == content:
            print(f"  [SKIP]    {name} — content unchanged (v{prev_version})")
            skipped += 1
            continue

        new_version = prev_version + 1
        insert_library(client, name, new_version, content)
        action = "INSERT" if prev_version == 0 else "UPDATE"
        print(f"  [{action}]  {name} v{new_version} ({len(content)} chars)")
        inserted += 1

    print()
    print(f"Done. Inserted: {inserted}, Skipped (unchanged): {skipped}, Missing: {missing}")


if __name__ == "__main__":
    main()
