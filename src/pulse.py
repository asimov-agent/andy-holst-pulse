"""GitHub API core + formatting for Andy Holst Pulse."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from typing import Any

GITHUB_USER = "andyholst"
API_BASE = f"https://api.github.com/users/{GITHUB_USER}"


def gh_api(path: str) -> Any:
    """Call GitHub API and return JSON."""
    url = f"{API_BASE}/{path}"
    result = subprocess.run(
        ["curl", "-s", "-H", "Accept: application/vnd.github+json", url],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def get_user() -> Any:
    return gh_api("")


def get_events(per_page: int = 100) -> Any:
    return gh_api(f"events/public?per_page={per_page}")


def get_repos(per_page: int = 100) -> Any:
    return gh_api(f"repos?per_page={per_page}&sort=updated")


def get_repo_issues(owner: str, repo: str, state: str = "all", per_page: int = 30) -> Any:
    return gh_api(f"repos/{owner}/{repo}/issues?state={state}&per_page={per_page}")


def get_pull_request(owner: str, repo: str, pr_number: int) -> Any:
    return gh_api(f"repos/{owner}/{repo}/pulls/{pr_number}")


def time_ago(dt_str: str) -> str:
    """Convert ISO datetime to human-readable relative time."""
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    diff = (datetime.now(timezone.utc) - dt).total_seconds()
    if diff < 60:
        return f"{int(diff)}s ago"
    if diff < 3600:
        return f"{int(diff / 60)}m ago"
    if diff < 86400:
        return f"{int(diff / 3600)}h ago"
    return f"{int(diff / 86400)}d ago"


def event_icon(event_type: str) -> str:
    icons = {
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
        "CommitCommentEvent": "💬",
        "GollumEvent": "📖",
    }
    return icons.get(event_type, "✨")


def event_url(event: dict) -> str:
    """Get the URL for a specific event."""
    repo = event.get("repo", {}).get("name", "")
    payload = event.get("payload", {})

    if event["type"] == "PushEvent":
        # Link to the comparison or repo
        before = payload.get("before", "")
        head = payload.get("head", "")
        if before and head:
            return f"https://github.com/{repo}/compare/{before}...{head}"
        return f"https://github.com/{repo}"

    if event["type"] == "PullRequestEvent":
        pr = payload.get("pull_request", {})
        return pr.get("html_url", f"https://github.com/{repo}")

    if event["type"] == "PullRequestReviewEvent":
        review = payload.get("review", {})
        return review.get("html_url", f"https://github.com/{repo}")

    if event["type"] == "IssuesEvent":
        issue = payload.get("issue", {})
        return issue.get("html_url", f"https://github.com/{repo}/issues")

    if event["type"] == "IssueCommentEvent":
        comment = payload.get("comment", {})
        return comment.get("html_url", f"https://github.com/{repo}/issues")

    if event["type"] == "CreateEvent":
        ref = payload.get("ref", "")
        ref_type = payload.get("ref_type", "")
        if ref and ref_type == "branch":
            return f"https://github.com/{repo}/tree/{ref}"
        if ref and ref_type == "tag":
            return f"https://github.com/{repo}/releases/tag/{ref}"
        return f"https://github.com/{repo}"

    if event["type"] == "ForkEvent":
        forkee = payload.get("forkee", {})
        return forkee.get("html_url", f"https://github.com/{repo}")

    if event["type"] == "WatchEvent":
        return f"https://github.com/{repo}"

    if event["type"] == "ReleaseEvent":
        release = payload.get("release", {})
        return release.get("html_url", f"https://github.com/{repo}/releases")

    if event["type"] == "DeleteEvent":
        return f"https://github.com/{repo}"

    return f"https://github.com/{repo}"


def event_summary(event: dict) -> str:
    """Get a detailed summary of an event."""
    repo = (event.get("repo", {}).get("name") or "").split("/")[-1]
    payload = event.get("payload", {})

    if event["type"] == "PushEvent":
        commits = payload.get("commits", [])
        if not commits:
            return f"Pushed to <b>{repo}</b>"
        parts = []
        for c in commits[:5]:
            msg = c.get("message", "").split("\n")[0][:80]
            sha = c.get("id", "")[:7]
            parts.append(f"<code>{sha}</code> {msg}")
        summary = "<br>".join(parts)
        if len(commits) > 5:
            summary += f"<br>... and {len(commits) - 5} more commits"
        return f"Pushed to <b>{repo}</b>:<br>{summary}"

    if event["type"] == "PullRequestEvent":
        pr = payload.get("pull_request", {})
        title = pr.get("title", "?")
        action = payload.get("action", "?")
        merged = pr.get("merged", False)
        body = (pr.get("body") or "")[:200]
        num = pr.get("number", "?")
        if action == "opened":
            return f"Opened <b>#{num}</b> on <b>{repo}</b>:<br><i>{title}</i><br><small>{body}</small>"
        if action == "closed" and merged:
            return f"✅ Merged <b>#{num}</b> on <b>{repo}</b>:<br><i>{title}</i>"
        if action == "closed":
            return f"❌ Closed <b>#{num}</b> on <b>{repo}</b>:<br><i>{title}</i>"
        if action == "merged":
            return f"✅ Merged <b>#{num}</b> on <b>{repo}</b>:<br><i>{title}</i>"
        return f"PR <b>#{num}</b> [{action}] on <b>{repo}</b>:<br><i>{title}</i>"

    if event["type"] == "PullRequestReviewEvent":
        review = payload.get("review", {})
        state = review.get("state", "?")
        body = (review.get("body") or "")[:200]
        pr_url = review.get("pull_request_url", "")
        # Extract PR number from URL
        pr_num = pr_url.split("/")[-1] if pr_url else "?"
        states = {
            "approved": "✅ approved",
            "changes_requested": "🔴 requested changes on",
            "commented": "💬 commented on",
        }
        state_text = states.get(state, state)
        return f"{state_text} PR <b>#{pr_num}</b> on <b>{repo}</b><br><small>{body}</small>"

    if event["type"] == "IssuesEvent":
        issue = payload.get("issue", {})
        title = issue.get("title", "?")
        action = payload.get("action", "?")
        num = issue.get("number", "?")
        body = (issue.get("body") or "")[:200]
        return f"{action.capitalize()} issue <b>#{num}</b> on <b>{repo}</b>:<br><i>{title}</i><br><small>{body}</small>"

    if event["type"] == "IssueCommentEvent":
        comment = payload.get("comment", {})
        body = (comment.get("body") or "")[:200]
        issue = payload.get("issue", {})
        num = issue.get("number", "?")
        title = issue.get("title", "")
        return f"💬 Commented on issue <b>#{num}</b> on <b>{repo}</b>:<br><i>{title}</i><br><small>{body}</small>"

    if event["type"] == "CreateEvent":
        ref = payload.get("ref", "?")
        ref_type = payload.get("ref_type", "?")
        return f"🌱 Created {ref_type} <b>{ref}</b> in <b>{repo}</b>"

    if event["type"] == "ForkEvent":
        forkee = payload.get("forkee", {})
        fname = forkee.get("full_name", "?")
        return f"🍴 Forked <b>{repo}</b> to <b>{fname}</b>"

    if event["type"] == "WatchEvent":
        return f"⭐ Starred <b>{repo}</b>"

    if event["type"] == "ReleaseEvent":
        release = payload.get("release", {})
        tag = release.get("tag_name", "?")
        name = release.get("name", "")
        return f"🚀 Released <b>{tag}</b> ({name}) on <b>{repo}</b>"

    if event["type"] == "CommitCommentEvent":
        comment = payload.get("comment", {})
        body = (comment.get("body") or "")[:200]
        return f"💬 Commented on commit in <b>{repo}</b><br><small>{body}</small>"

    return f"{event_icon(event['type'])} {event['type']} on <b>{repo}</b>"


def filter_events(events: list, event_type: str | None = None) -> list:
    """Filter events by type. Returns all if event_type is None."""
    if event_type is None:
        return events

    type_map = {
        "all": None,
        "pr": ["PullRequestEvent"],
        "issue": ["IssuesEvent", "IssueCommentEvent"],
        "commit": ["PushEvent"],
        "review": ["PullRequestReviewEvent", "CommitCommentEvent"],
        "fork": ["ForkEvent"],
        "star": ["WatchEvent"],
        "release": ["ReleaseEvent"],
    }

    allowed = type_map.get(event_type.lower())
    if allowed is None:
        return events
    return [e for e in events if e.get("type") in allowed]


def summarize_events(events: list) -> dict:
    """Produce summary statistics from a list of events."""
    return {
        "total": len(events),
        "commits": sum(len(e.get("payload", {}).get("commits", [])) for e in events if e["type"] == "PushEvent"),
        "prs_opened": sum(1 for e in events if e["type"] == "PullRequestEvent" and e.get("payload", {}).get("action") == "opened"),
        "prs_merged": sum(1 for e in events if e["type"] == "PullRequestEvent" and e.get("payload", {}).get("pull_request", {}).get("merged")),
        "prs_closed": sum(1 for e in events if e["type"] == "PullRequestEvent" and e.get("payload", {}).get("action") == "closed" and not e.get("payload", {}).get("pull_request", {}).get("merged")),
        "reviews": sum(1 for e in events if e["type"] == "PullRequestReviewEvent"),
        "issues_opened": sum(1 for e in events if e["type"] == "IssuesEvent" and e.get("payload", {}).get("action") == "opened"),
        "issues_closed": sum(1 for e in events if e["type"] == "IssuesEvent" and e.get("payload", {}).get("action") == "closed"),
        "forks": sum(1 for e in events if e["type"] == "ForkEvent"),
        "stars": sum(1 for e in events if e["type"] == "WatchEvent"),
        "active_repos": len({e.get("repo", {}).get("name", "") for e in events}),
    }


def format_daily_post(events: list, user: dict, repos: list) -> str:
    """Format a daily post for X/LinkedIn."""
    if not events:
        return f"😴 No public GitHub activity from @{GITHUB_USER} today.\n\n#OpenSource #GitHub"

    stats = summarize_events(events)
    date_str = datetime.now(timezone.utc).strftime("%b %d, %Y")

    lines = [f"🔥 @{GITHUB_USER}'s GitHub Pulse — {date_str}", ""]

    # Top repos by activity
    repo_counts: dict[str, int] = {}
    for e in events:
        name = (e.get("repo", {}).get("name") or "").split("/")[-1]
        repo_counts[name] = repo_counts.get(name, 0) + 1

    for repo, count in sorted(repo_counts.items(), key=lambda x: -x[1])[:5]:
        lines.append(f"📦 {repo} ({count} events)")

    lines.append("")

    # Recent highlights
    for e in events[:8]:
        lines.append(f"{event_icon(e['type'])} {event_summary(e).split('<br>')[0]}")

    lines.append("")
    lines.append(f"📊 {stats['commits']} commits · {stats['prs_opened']} PRs opened · {stats['prs_merged']} merged · {stats['reviews']} reviews")
    lines.append("")
    lines.append("#OpenSource #DevSecOps #GitHub #BuildInPublic")

    return "\n".join(lines)
