#!/usr/bin/env python3
"""Fetch Andy Holst's GitHub activity and format a daily 'pulse' post."""

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict

GITHUB_USER = "andyholst"
API_BASE = f"https://api.github.com/users/{GITHUB_USER}"

# Emoji map for event types / keywords
EMOJI = {
    "PushEvent": "📦",
    "PullRequestEvent": "🔀",
    "PullRequestReviewEvent": "👀",
    "CreateEvent": "🌱",
    "ForkEvent": "🍴",
    "WatchEvent": "⭐",
    "IssueCommentEvent": "💬",
    "IssuesEvent": "🐛",
    "ReleaseEvent": "🚀",
    "DeleteEvent": "🗑️",
    "default": "✨",
}

# Keyword-based emojis for commit messages
KEYWORD_EMOJI = {
    "fix": "🐛",
    "feat": "✨",
    "docs": "📝",
    "style": "💄",
    "refactor": "♻️",
    "test": "🧪",
    "chore": "🔧",
    "ci": "⚙️",
    "perf": "⚡",
    "security": "🔒",
    "merge": "🔀",
}


def gh_api(path: str) -> list | dict:
    """Call GitHub API and return JSON."""
    url = f"{API_BASE}/{path}" if not path.startswith("http") else path
    result = subprocess.run(
        ["curl", "-s", "-H", "Accept: application/vnd.github+json", url],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"  ⚠️  API call failed: {result.stderr[:200]}", file=sys.stderr)
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"  ⚠️  Bad JSON from {url}", file=sys.stderr)
        return []


def get_events() -> list:
    """Fetch recent public events."""
    return gh_api("events/public?per_page=100")


def get_repo_commits(owner_repo: str, since: str) -> list:
    """Fetch commits for a repo since a date."""
    return gh_api(f"repos/{owner_repo}/commits?since={since}&per_page=20")


def classify_commit(msg: str) -> str:
    """Pick an emoji for a commit message."""
    lower = msg.lower()
    for kw, emoji in KEYWORD_EMOJI.items():
        if kw in lower:
            return emoji
    return "📝"


def filter_today(events: list) -> tuple:
    """Filter events to the last 24h and yesterday for a clean daily window."""
    now = datetime.now(timezone.utc)
    # Use a window: from yesterday same time to now
    cutoff = now - timedelta(hours=24)

    today_events = []
    for e in events:
        created = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
        if created >= cutoff:
            today_events.append(e)

    return today_events, cutoff


def format_post(events: list, since: datetime) -> str:
    """Format events into a fancy social media post."""
    if not events:
        return None

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%b %d, %Y")

    # Group by repo
    repo_events = defaultdict(list)
    for e in events:
        repo = e["repo"].get("name", "unknown")
        repo_events[repo].append(e)

    lines = []
    lines.append(f"🔥 {GITHUB_USER}'s GitHub Pulse — {date_str}")
    lines.append("")

    # Counters
    commits_count = 0
    prs_opened = 0
    prs_merged = 0
    prs_reviewed = 0
    repos_active = set()

    for repo, evts in repo_events.items():
        repos_active.add(repo)
        # Clean repo name (drop username prefix for display)
        display_repo = repo.split("/")[-1] if "/" in repo else repo

        lines.append(f"📦 {display_repo}")

        for e in evts:
            etype = e["type"]
            dt = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
            time_str = dt.strftime("%H:%M")

            if etype == "PushEvent":
                commits = e["payload"].get("commits", [])
                commits_count += len(commits)
                for c in commits[:5]:  # max 5 commits per push
                    msg = c["message"].split("\n")[0][:70]
                    emoji = classify_commit(msg)
                    lines.append(f"  {emoji} {msg}")
                if len(commits) > 5:
                    lines.append(f"  ... +{len(commits)-5} more commits")

            elif etype == "PullRequestEvent":
                pr = e["payload"].get("pull_request", {})
                title = pr.get("title", "?")[:70]
                action = e["payload"].get("action", "?")
                merged = pr.get("merged", False)
                if action == "opened":
                    prs_opened += 1
                    lines.append(f"  🔀 Opened PR: {title}")
                elif action == "closed" and merged:
                    prs_merged += 1
                    lines.append(f"  ✅ Merged PR: {title}")
                elif action == "closed":
                    lines.append(f"  ❌ Closed PR: {title}")
                else:
                    lines.append(f"  🔀 PR [{action}]: {title}")

            elif etype == "PullRequestReviewEvent":
                prs_reviewed += 1
                rev = e["payload"].get("review", {})
                state = rev.get("state", "?")
                lines.append(f"  👀 Reviewed PR ({state})")

            elif etype == "CreateEvent":
                ref = e["payload"].get("ref", "?")
                rtype = e["payload"].get("ref_type", "?")
                lines.append(f"  🌱 Created {rtype}: {ref}")

            elif etype == "ForkEvent":
                lines.append(f"  🍴 Forked repo")

            elif etype == "WatchEvent":
                lines.append(f"  ⭐ Starred repo")

            elif etype == "IssueCommentEvent":
                lines.append(f"  💬 Commented on issue")

            elif etype == "ReleaseEvent":
                lines.append(f"  🚀 Released")

            else:
                emoji = EMOJI.get(etype, EMOJI["default"])
                lines.append(f"  {emoji} {etype}")

        lines.append("")

    # Stats line
    stats = []
    if commits_count:
        stats.append(f"{commits_count} commit{'s' if commits_count != 1 else ''}")
    if prs_opened:
        stats.append(f"{prs_opened} PR{'s' if prs_opened != 1 else ''} opened")
    if prs_merged:
        stats.append(f"{prs_merged} PR{'s' if prs_merged != 1 else ''} merged")
    if prs_reviewed:
        stats.append(f"{prs_reviewed} PR{'s' if prs_reviewed != 1 else ''} reviewed")

    if stats:
        lines.append(f"📊 Today: {', '.join(stats)} across {len(repos_active)} repo{'s' if len(repos_active) != 1 else ''}")
        lines.append("")

    lines.append("#OpenSource #DevSecOps #GitHub #BuildInPublic")

    return "\n".join(lines)


def main():
    print("🔍 Fetching Andy Holst's GitHub activity...", file=sys.stderr)

    events = get_events()
    if not events:
        print("❌ No events fetched", file=sys.stderr)
        sys.exit(1)

    today_events, since = filter_today(events)
    print(f"  Found {len(today_events)} events in last 24h", file=sys.stderr)

    post = format_post(today_events, since)
    if post:
        print(post)
    else:
        print(f"😴 No public GitHub activity from {GITHUB_USER} in the last 24h.")
        print(f"#OpenSource #GitHub")


if __name__ == "__main__":
    main()
