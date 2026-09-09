"""Page structure tests — validates index.html has all required elements."""

from pathlib import Path

INDEX_HTML = Path(__file__).parent.parent / "index.html"


def read_page() -> str:
    return INDEX_HTML.read_text()


class TestPageStructure:
    def test_page_exists(self):
        assert INDEX_HTML.exists(), "index.html must exist at repo root"

    def test_has_doctype(self):
        content = read_page()
        assert content.strip().startswith("<!DOCTYPE html>")

    def test_has_title(self):
        content = read_page()
        assert "<title>" in content
        assert "Andy Holst" in content
        assert "GitHub Pulse" in content

    def test_has_filter_buttons(self):
        content = read_page()
        required_filters = ["all", "pr", "issue", "commit", "review", "fork", "star", "release"]
        for f in required_filters:
            assert f'data-filter="{f}"' in content, f"Missing filter button: {f}"

    def test_has_live_indicator(self):
        content = read_page()
        assert "live-dot" in content or "LIVE" in content

    def test_has_stats_sections(self):
        content = read_page()
        assert 'id="profile-stats"' in content
        assert 'id="activity-stats"' in content
        assert 'id="events-list"' in content
        assert 'id="repo-bars"' in content
        assert 'id="repos-grid"' in content

    def test_has_api_fetch(self):
        content = read_page()
        assert "api.github.com" in content
        assert "fetch" in content.lower()

    def test_has_github_user_reference(self):
        content = read_page()
        assert "andyholst" in content

    def test_has_footer_links(self):
        content = read_page()
        assert "docondee.com" in content
        assert "x.com/andy_a_holst" in content or "twitter" in content.lower()
        assert "linkedin" in content.lower()

    def test_no_external_dependencies(self):
        """Page should be self-contained — no CDN scripts or Google APIs."""
        content = read_page()
        # We allow fonts.googleapis.com for fonts but nothing else external
        assert 'src="https://' not in content.replace("https://fonts.googleapis.com", "")
        assert 'src="http://' not in content

    def test_has_responsive_meta(self):
        content = read_page()
        assert 'name="viewport"' in content

    def test_has_emoji_event_icons(self):
        content = read_page()
        # Check that JS has event icon mapping (keys may be quoted or unquoted)
        assert "PushEvent" in content
        assert "PullRequestEvent" in content
        assert "IssuesEvent" in content
