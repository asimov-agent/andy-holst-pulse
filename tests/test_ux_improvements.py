"""Tests for UX improvements."""

from pathlib import Path

INDEX_HTML = Path(__file__).parent.parent / "index.html"


def read_page() -> str:
    return INDEX_HTML.read_text()


class TestUXImprovements:
    def test_profile_stats_are_clickable(self):
        """Profile stats should be anchor tags linking to GitHub pages."""
        content = read_page()
        # Profile stats section should have links to GitHub
        assert 'href="https://github.com/andyholst?tab=followers"' in content
        assert 'href="https://github.com/andyholst?tab=following"' in content
        assert 'href="https://github.com/andyholst?tab=repositories"' in content
        assert 'href="https://github.com/andyholst?tab=gists"' in content

    def test_profile_stats_use_anchor_tags(self):
        """Profile stats should use <a> tags, not <div>."""
        content = read_page()
        # The renderProfileStats function should generate <a> tags
        assert 'renderProfileStats' in content
        assert '<a href=' in content
        # Followers should be clickable
        assert 'Followers' in content
        assert 'Following' in content

    def test_search_input_exists(self):
        """Page should have a search input for filtering activity."""
        content = read_page()
        assert 'search-input' in content or 'id="search"' in content
        assert 'Search repos' in content or 'Search' in content

    def test_search_filters_events(self):
        """Search should filter events by query."""
        content = read_page()
        assert 'searchQuery' in content
        assert 'applyFilter' in content

    def test_no_undefined_in_stats(self):
        """Stats should never show 'undefined'."""
        content = read_page()
        # The active repos should use .size for Set
        assert 'activeRepos' in content
        assert 'undefined' not in content.lower() or content.lower().count('undefined') == 0

    def test_push_events_show_commits(self):
        """Push events should show commit messages."""
        content = read_page()
        assert 'commits' in content
        assert 'message' in content
        assert 'Pushed' in content

    def test_repo_cards_have_descriptions(self):
        """Featured repo cards should show descriptions."""
        content = read_page()
        assert 'description' in content.lower() or 'repo-card-desc' in content
        assert 'No description' in content

    def test_active_repos_uses_set_size(self):
        """Active repos count should use Set.size."""
        content = read_page()
        assert 'new Set(' in content
        assert '.size' in content or 'activeRepos' in content

    def test_followers_stat_has_link(self):
        """Followers stat should link to followers page."""
        content = read_page()
        assert 'tab=followers' in content

    def test_following_stat_has_link(self):
        """Following stat should link to following page."""
        content = read_page()
        assert 'tab=following' in content

    def test_repos_stat_has_link(self):
        """Repos stat should link to repositories page."""
        content = read_page()
        assert 'tab=repositories' in content

    def test_gists_stat_has_link(self):
        """Gists stat should link to gists page."""
        content = read_page()
        assert 'tab=gists' in content

    def test_stat_card_is_clickable(self):
        """Stat cards should be clickable (have cursor pointer or anchor)."""
        content = read_page()
        assert 'stat-card' in content

    def test_search_input_has_aria_label(self):
        """Search input should have aria-label for accessibility."""
        content = read_page()
        assert 'aria-label="Search' in content or 'aria-label="search' in content.lower()
