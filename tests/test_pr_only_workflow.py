"""Tests for the PR-only workflow enforcement."""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
WORKFLOW_FILE = REPO_ROOT / ".github" / "workflows" / "pr-only-main.yml"


class TestPROnlyWorkflow:
    def test_workflow_file_exists(self):
        assert WORKFLOW_FILE.exists(), "pr-only-main.yml workflow must exist"

    def test_workflow_has_pr_check(self):
        content = WORKFLOW_FILE.read_text()
        assert "check-pr-only" in content or "Check if commit came from PR" in content

    def test_workflow_blocks_direct_push(self):
        content = WORKFLOW_FILE.read_text()
        assert "Direct push to main is NOT allowed" in content

    def test_workflow_allows_pr_merge(self):
        content = WORKFLOW_FILE.read_text()
        assert "Merge pull request" in content or "PR merge" in content
