"""Tests for the pulse core logic."""

from datetime import datetime, timedelta, timezone

from src.pulse import (
    event_icon,
    event_summary,
    event_url,
    filter_events,
    format_daily_post,
    summarize_events,
    time_ago,
)


class TestTimeAgo:
    def test_seconds_ago(self):
        dt = (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat().replace("+00:00", "Z")
        result = time_ago(dt)
        assert "30s ago" in result

    def test_minutes_ago(self):
        dt = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
        result = time_ago(dt)
        assert "5m ago" in result

    def test_hours_ago(self):
        dt = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat().replace("+00:00", "Z")
        result = time_ago(dt)
        assert "3h ago" in result

    def test_days_ago(self):
        dt = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat().replace("+00:00", "Z")
        result = time_ago(dt)
        assert "2d ago" in result


class TestEventIcon:
    def test_push_event(self):
        assert event_icon("PushEvent") == "📦"

    def test_pr_event(self):
        assert event_icon("PullRequestEvent") == "🔀"

    def test_review_event(self):
        assert event_icon("PullRequestReviewEvent") == "👀"

    def test_unknown_event(self):
        assert event_icon("UnknownEvent") == "✨"


class TestEventUrl:
    def test_push_event_url(self):
        event = {
            "type": "PushEvent",
            "repo": {"name": "andyholst/llama-ai"},
            "payload": {"before": "abc123", "head": "def456"},
        }
        url = event_url(event)
        assert "compare/abc123...def456" in url

    def test_pr_event_url(self):
        event = {
            "type": "PullRequestEvent",
            "repo": {"name": "andyholst/llama-ai"},
            "payload": {"pull_request": {"html_url": "https://github.com/andyholst/llama-ai/pull/42"}},
        }
        url = event_url(event)
        assert url == "https://github.com/andyholst/llama-ai/pull/42"

    def test_issues_event_url(self):
        event = {
            "type": "IssuesEvent",
            "repo": {"name": "andyholst/llama-ai"},
            "payload": {"issue": {"html_url": "https://github.com/andyholst/llama-ai/issues/10"}},
        }
        url = event_url(event)
        assert url == "https://github.com/andyholst/llama-ai/issues/10"

    def test_create_branch_url(self):
        event = {
            "type": "CreateEvent",
            "repo": {"name": "andyholst/llama-ai"},
            "payload": {"ref": "feat/new-feature", "ref_type": "branch"},
        }
        url = event_url(event)
        assert "tree/feat/new-feature" in url

    def test_fork_event_url(self):
        event = {
            "type": "ForkEvent",
            "repo": {"name": "andyholst/llama-ai"},
            "payload": {"forkee": {"html_url": "https://github.com/forker/llama-ai"}},
        }
        url = event_url(event)
        assert url == "https://github.com/forker/llama-ai"


class TestEventSummary:
    def test_push_single_commit(self):
        event = {
            "type": "PushEvent",
            "repo": {"name": "andyholst/llama-ai"},
            "payload": {"commits": [{"message": "feat: add new feature", "id": "abc1234567890"}]},
        }
        summary = event_summary(event)
        assert "Pushed" in summary
        assert "llama-ai" in summary
        assert "feat: add new feature" in summary

    def test_push_multiple_commits(self):
        event = {
            "type": "PushEvent",
            "repo": {"name": "andyholst/llama-ai"},
            "payload": {
                "commits": [
                    {"message": "commit 1", "id": "aaa"},
                    {"message": "commit 2", "id": "bbb"},
                    {"message": "commit 3", "id": "ccc"},
                    {"message": "commit 4", "id": "ddd"},
                    {"message": "commit 5", "id": "eee"},
                    {"message": "commit 6", "id": "fff"},
                ]
            },
        }
        summary = event_summary(event)
        assert "1 more commit" in summary

    def test_pr_opened(self):
        event = {
            "type": "PullRequestEvent",
            "repo": {"name": "andyholst/llama-ai"},
            "payload": {
                "action": "opened",
                "pull_request": {"title": "Add new feature", "number": 42, "body": "Description here", "merged": False},
            },
        }
        summary = event_summary(event)
        assert "Opened" in summary
        assert "#42" in summary
        assert "Add new feature" in summary

    def test_pr_merged(self):
        event = {
            "type": "PullRequestEvent",
            "repo": {"name": "andyholst/llama-ai"},
            "payload": {
                "action": "closed",
                "pull_request": {"title": "Fix bug", "number": 99, "body": "", "merged": True},
            },
        }
        summary = event_summary(event)
        assert "Merged" in summary
        assert "✅" in summary

    def test_issue_opened(self):
        event = {
            "type": "IssuesEvent",
            "repo": {"name": "andyholst/llama-ai"},
            "payload": {
                "action": "opened",
                "issue": {"title": "Bug report", "number": 10, "body": "Something broke"},
            },
        }
        summary = event_summary(event)
        assert "Opened" in summary
        assert "#10" in summary
        assert "Bug report" in summary

    def test_review_approved(self):
        event = {
            "type": "PullRequestReviewEvent",
            "repo": {"name": "andyholst/llama-ai"},
            "payload": {
                "review": {
                    "state": "approved",
                    "body": "LGTM!",
                    "pull_request_url": "https://api.github.com/repos/andyholst/llama-ai/pulls/42",
                }
            },
        }
        summary = event_summary(event)
        assert "approved" in summary.lower() or "Approved" in summary
        assert "#42" in summary


class TestFilterEvents:
    def test_filter_all(self):
        events = [
            {"type": "PushEvent"},
            {"type": "PullRequestEvent"},
            {"type": "IssuesEvent"},
        ]
        result = filter_events(events, "all")
        assert len(result) == 3

    def test_filter_pr(self):
        events = [
            {"type": "PushEvent"},
            {"type": "PullRequestEvent"},
            {"type": "PullRequestEvent"},
        ]
        result = filter_events(events, "pr")
        assert len(result) == 2

    def test_filter_issue(self):
        events = [
            {"type": "PushEvent"},
            {"type": "IssuesEvent"},
            {"type": "IssueCommentEvent"},
        ]
        result = filter_events(events, "issue")
        assert len(result) == 2

    def test_filter_commit(self):
        events = [
            {"type": "PushEvent"},
            {"type": "PushEvent"},
            {"type": "PullRequestEvent"},
        ]
        result = filter_events(events, "commit")
        assert len(result) == 2

    def test_filter_fork(self):
        events = [
            {"type": "ForkEvent"},
            {"type": "PushEvent"},
        ]
        result = filter_events(events, "fork")
        assert len(result) == 1


class TestSummarizeEvents:
    def test_empty_events(self):
        result = summarize_events([])
        assert result["total"] == 0
        assert result["commits"] == 0

    def test_with_data(self):
        events = [
            {"type": "PushEvent", "payload": {"commits": [{"id": "a"}, {"id": "b"}]}},
            {"type": "PushEvent", "payload": {"commits": [{"id": "c"}]}},
            {"type": "PullRequestEvent", "payload": {"action": "opened", "pull_request": {"merged": False}}},
            {"type": "PullRequestEvent", "payload": {"action": "closed", "pull_request": {"merged": True}}},
            {"type": "PullRequestReviewEvent", "payload": {}},
            {"type": "IssuesEvent", "payload": {"action": "opened"}},
            {"type": "ForkEvent", "payload": {}},
            {"type": "WatchEvent", "payload": {}},
            {"type": "PushEvent", "repo": {"name": "a"}, "payload": {"commits": []}},
            {"type": "PushEvent", "repo": {"name": "b"}, "payload": {"commits": []}},
        ]
        result = summarize_events(events)
        assert result["commits"] == 3
        assert result["prs_opened"] == 1
        assert result["prs_merged"] == 1
        assert result["reviews"] == 1
        assert result["issues_opened"] == 1
        assert result["forks"] == 1
        assert result["stars"] == 1


class TestFormatDailyPost:
    def test_no_events(self):
        result = format_daily_post([], {}, [])
        assert "No public GitHub activity" in result

    def test_with_events(self):
        events = [
            {
                "type": "PushEvent",
                "repo": {"name": "andyholst/llama-ai"},
                "payload": {"commits": [{"message": "feat: test", "id": "abc1234"}]},
                "created_at": "2026-09-09T00:00:00Z",
            },
            {
                "type": "PullRequestEvent",
                "repo": {"name": "andyholst/llama-ai"},
                "payload": {"action": "opened", "pull_request": {"title": "New PR", "number": 1, "merged": False}},
                "created_at": "2026-09-09T00:00:00Z",
            },
        ]
        user = {"login": "andyholst"}
        repos = [
            {
                "name": "llama-ai",
                "stargazers_count": 5,
                "forks_count": 2,
                "description": "test repo",
                "language": "Python",
                "html_url": "https://github.com/andyholst/llama-ai",
            }
        ]
        result = format_daily_post(events, user, repos)
        assert "andyholst" in result
        assert "GitHub Pulse" in result
        assert "#OpenSource" in result
