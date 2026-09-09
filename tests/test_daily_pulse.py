"""Tests for the daily_pulse CLI."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add scripts dir to path for import
scripts_dir = str(Path(__file__).parent.parent / "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

import daily_pulse


class TestDailyPulse:
    @patch("sys.argv", ["daily_pulse", "--dry-run"])
    def test_dry_run_prints_post(self, capsys):
        """Dry run should print the post."""
        with patch("daily_pulse.get_user") as mock_user, \
             patch("daily_pulse.get_events") as mock_events, \
             patch("daily_pulse.get_repos") as mock_repos, \
             patch("daily_pulse.format_daily_post") as mock_format:
            
            mock_user.return_value = {"login": "andyholst"}
            mock_events.return_value = [
                {"type": "PushEvent", "repo": {"name": "andyholst/test"}, "payload": {"commits": [{"message": "test", "id": "abc1234"}]}}
            ]
            mock_repos.return_value = []
            mock_format.return_value = "Test post content"

            daily_pulse.main()

            captured = capsys.readouterr()
            assert "Test post content" in captured.out

    @patch("sys.argv", ["daily_pulse", "--dry-run"])
    def test_no_events_skips_post(self, capsys):
        """No events should skip posting."""
        with patch("daily_pulse.get_user") as mock_user, \
             patch("daily_pulse.get_events") as mock_events, \
             patch("daily_pulse.get_repos") as mock_repos:
            
            mock_user.return_value = {"login": "andyholst"}
            mock_events.return_value = []
            mock_repos.return_value = []

            daily_pulse.main()

            captured = capsys.readouterr()
            assert "😴" in captured.out

    @patch("sys.argv", ["daily_pulse"])
    def test_x_poster_not_configured(self, capsys):
        """Should warn when X API is not configured."""
        with patch("daily_pulse.get_user") as mock_user, \
             patch("daily_pulse.get_events") as mock_events, \
             patch("daily_pulse.get_repos") as mock_repos, \
             patch("daily_pulse.format_daily_post") as mock_format, \
             patch("daily_pulse.XPoster") as MockPoster:
            
            mock_user.return_value = {"login": "andyholst"}
            mock_events.return_value = [
                {"type": "PushEvent", "repo": {"name": "andyholst/test"}, "payload": {"commits": [{"message": "test", "id": "abc1234"}]}}
            ]
            mock_repos.return_value = []
            mock_format.return_value = "Test post"
            
            mock_poster = MagicMock()
            mock_poster.is_configured = False
            MockPoster.return_value = mock_poster

            daily_pulse.main()

            captured = capsys.readouterr()
            assert "not configured" in captured.out

    @patch("sys.argv", ["daily_pulse"])
    def test_linkedin_poster_not_configured(self, capsys):
        """Should warn when LinkedIn API is not configured."""
        with patch("daily_pulse.get_user") as mock_user, \
             patch("daily_pulse.get_events") as mock_events, \
             patch("daily_pulse.get_repos") as mock_repos, \
             patch("daily_pulse.format_daily_post") as mock_format, \
             patch("daily_pulse.XPoster"), \
             patch("daily_pulse.LinkedInPoster") as MockPoster:
            
            mock_user.return_value = {"login": "andyholst"}
            mock_events.return_value = [
                {"type": "PushEvent", "repo": {"name": "andyholst/test"}, "payload": {"commits": [{"message": "test", "id": "abc1234"}]}}
            ]
            mock_repos.return_value = []
            mock_format.return_value = "Test post"
            
            mock_poster = MagicMock()
            mock_poster.is_configured = False
            MockPoster.return_value = mock_poster

            daily_pulse.main()

            captured = capsys.readouterr()
            assert "not configured" in captured.out
