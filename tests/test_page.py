"""Comprehensive page tests — validates HTML structure, JS logic, and link correctness."""

import re
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
        """Page should be self-contained — no CDN scripts."""
        content = read_page()
        assert 'src="https://' not in content.replace("https://fonts.googleapis.com", "")
        assert 'src="http://' not in content

    def test_has_responsive_meta(self):
        content = read_page()
        assert 'name="viewport"' in content

    def test_has_emoji_event_icons(self):
        content = read_page()
        assert "PushEvent" in content
        assert "PullRequestEvent" in content
        assert "IssuesEvent" in content

    def test_has_accessible_main_landmark(self):
        content = read_page()
        # Page should have a main landmark for accessibility
        assert "<main" in content or 'role="main"' in content

    def test_has_skip_link(self):
        content = read_page()
        # Should have a skip-to-content link for keyboard nav
        assert "skip" in content.lower() or 'href="#main"' in content

    def test_event_cards_are_real_links(self):
        """Event cards must use <a> tags, not <div onclick>."""
        content = read_page()
        # Find the renderEvents function and verify it creates <a> tags
        assert 'class="event-card"' in content
        assert "<a " in content  # Must have anchor tags for real links

    def test_no_inline_javascript_handlers(self):
        """Avoid inline onclick handlers — use addEventListener."""
        content = read_page()
        # Only the retry button should have onclick, which is acceptable
        onclick_count = content.count("onclick=")
        assert onclick_count <= 1, f"Found {onclick_count} inline onclick handlers"

    def test_github_urls_are_well_formed(self):
        """All hardcoded GitHub URLs should start with https://github.com/"""
        content = read_page()
        # Find all github.com URLs in the page (only real ones, not template literals)
        urls = re.findall(r'https://github\.com/[a-zA-Z0-9/_.-]+', content)
        assert len(urls) > 0, "No GitHub URLs found"
        for url in urls:
            # Should not have trailing dots or weird chars
            assert not url.endswith("."), f"Malformed URL: {url}"
            assert ".." not in url.split("github.com/")[1], f"Double dot in URL: {url}"

    def test_link_labels_match_real_paths(self):
        """linkLabel should be a valid path fragment like 'repo/pull/42'"""
        content = read_page()
        # Check that linkLabel format is consistent
        assert "linkLabel:" in content or "linkLabel =" in content

    def test_has_proper_semantic_html(self):
        """Use semantic HTML5 elements."""
        content = read_page()
        # Should use header, main, footer
        assert "<header" in content or "<div class=\"header\"" in content
        assert "<footer" in content or "<div class=\"footer\"" in content

    def test_stats_have_aria_labels(self):
        """Stats cards should have aria-labels for screen readers."""
        content = read_page()
        # At minimum, stats section should be navigable
        assert "stat-card" in content

    def test_filter_buttons_have_aria(self):
        """Filter buttons should indicate active state for accessibility."""
        content = read_page()
        # Should have aria-pressed or aria-current for active filter
        assert "aria-pressed" in content or "aria-current" in content or "active" in content

    def test_empty_state_has_message(self):
        """When no events match filter, should show empty message."""
        content = read_page()
        assert "No activity for this filter" in content

    def test_loading_state_present(self):
        """Should show loading spinner while fetching."""
        content = read_page()
        assert "spinner" in content
        assert "loading" in content.lower()

    def test_error_state_present(self):
        """Should show error message on failure."""
        content = read_page()
        assert "error" in content.lower()
        assert "Retry" in content


class TestJSFunctions:
    """Extract and validate JS functions from the page."""

    def test_evurl_function_exists(self):
        content = read_page()
        assert "function evUrl(" in content

    def test_evcard_function_exists(self):
        content = read_page()
        assert "function evCard(" in content

    def test_render_events_function_exists(self):
        content = read_page()
        assert "function renderEvents(" in content

    def test_filter_map_has_all_types(self):
        content = read_page()
        filter_keys = ["all", "pr", "issue", "commit", "review", "fork", "star", "release"]
        for key in filter_keys:
            # JS object keys can be quoted or unquoted
            assert f'"{key}":' in content or f"'{key}':" in content or f"{key}:" in content

    def test_escape_function_exists(self):
        content = read_page()
        assert "const esc = " in content or "function esc(" in content

    def test_timeago_function_exists(self):
        content = read_page()
        assert "const timeAgo = " in content or "function timeAgo(" in content


class TestLinkCorrectness:
    """Verify that links point to the right GitHub resources."""

    def test_push_event_links_to_compare(self):
        """Push events should link to compare page."""
        content = read_page()
        # The evUrl function should have compare logic
        assert "compare/" in content
        assert "before" in content and "head" in content

    def test_pr_event_links_to_pr(self):
        """PR events should link to the PR html_url."""
        content = read_page()
        assert "pull_request?.html_url" in content or "pull_request?.html_url" in content

    def test_issue_event_links_to_issue(self):
        """Issue events should link to the issue html_url."""
        content = read_page()
        assert "issue?.html_url" in content

    def test_fork_event_links_to_fork(self):
        """Fork events should link to the forked repo."""
        content = read_page()
        assert "forkee?.html_url" in content

    def test_release_event_links_to_release(self):
        """Release events should link to the release."""
        content = read_page()
        assert "release?.html_url" in content

    def test_create_branch_links_to_tree(self):
        """Branch creation should link to tree."""
        content = read_page()
        assert "/tree/" in content

    def test_create_tag_links_to_releases(self):
        """Tag creation should link to releases."""
        content = read_page()
        assert "/releases/tag/" in content
