#!/usr/bin/env python3
"""Generate daily pulse and post to X/LinkedIn."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pulse import format_daily_post, get_events, get_repos, get_user
from x_poster import XPoster
from linkedin_poster import LinkedInPoster


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and post daily GitHub pulse")
    parser.add_argument("--dry-run", action="store_true", help="Generate post without sending")
    parser.add_argument("--platform", choices=["x", "linkedin", "both"], default="both")
    parser.add_argument("--output", type=Path, help="Save post to file")
    args = parser.parse_args()

    print("🔍 Fetching GitHub activity...")
    user = get_user()
    events = get_events()
    repos = get_repos()

    if not events:
        print("😴 No public GitHub activity in the last 24h.")
        return

    post = format_daily_post(events, user, repos)

    if args.dry_run:
        print("\n--- DRY RUN ---\n")
        print(post)
        print("\n--- END DRY RUN ---\n")
        return

    if args.output:
        args.output.write_text(post)
        print(f"✅ Post saved to {args.output}")

    if args.platform in ("x", "both"):
        poster = XPoster()
        if poster.is_configured:
            try:
                result = poster.post(post)
                print(f"✅ Posted to X: {result.get('data', {}).get('id', '?')}")
            except RuntimeError as e:
                print(f"❌ X posting failed: {e}")
        else:
            print("⚠️ X API not configured — skipping")

    if args.platform in ("linkedin", "both"):
        poster = LinkedInPoster()
        if poster.is_configured:
            try:
                result = poster.post(post)
                print(f"✅ Posted to LinkedIn: {result.get('id', '?')}")
            except RuntimeError as e:
                print(f"❌ LinkedIn posting failed: {e}")
        else:
            print("⚠️ LinkedIn API not configured — skipping")


if __name__ == "__main__":
    main()
