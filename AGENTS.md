---
name: andy-holst-pulse
description: "Dynamic GitHub activity dashboard for Andy Holst with deep links, filtering, and strict issue→worktree→PR workflow."
version: 1.1.0
---

# AGENTS.md — Andy Holst Pulse

Behavior file for agent workflow in this repo. **Follow this on every session.**

## Repo purpose

Dynamic GitHub activity dashboard for [@andyholst](https://github.com/andyholst). Fully client-side — fetches live from GitHub API. Posts daily summaries to X/LinkedIn.

Live URL: https://asimov-agent.github.io/andy-holst-pulse/

## Workflow: Issue → Worktree → Branch → PR (MANDATORY)

**NEVER push directly to main. NEVER work on main directly.**

Every piece of work MUST follow this pipeline:

### 1. Create GitHub Issue FIRST

```bash
gh issue create --title "<title>" --body "## Goal\n\n## Acceptance Criteria\n\n## Tasks\n- [ ] "
```

The issue is the root of truth. It describes the goal, acceptance criteria, and task checklist.

### 2. Create Worktree Branch

```bash
cd /Users/andy/repository/git/andy-holst-pulse
git fetch origin main
git worktree add -b feat/<kebab-name> ../llama-ai-wt/<kebab-name> origin/main
cd ../llama-ai-wt/<kebab-name>
```

The worktree lives OUTSIDE the main checkout (sibling dir). This allows parallel work without collisions.

### 3. Implement + Test Inside Worktree

Inside the worktree:
- Write code
- Write tests
- Run `pytest tests/ -v` locally
- Run `ruff check src/ tests/ scripts/`
- Commit early and often (at least one unique commit immediately after creating files)

### 4. Push + Open PR

```bash
cd ../llama-ai-wt/<kebab-name>
git push -u origin feat/<kebab-name>
gh pr create --base main --head feat/<kebab-name> \
    --title "feat: <kebab-name>" \
    --body "Completes #<issue_number>.\n\n## Changes\n\n## Test Plan\n- [ ] CI green\n- [ ] All tests pass"
```

### 5. CI Must Be GREEN Before Merge

The PR will only be merged when:
- CI pipeline passes (lint + test)
- All tests pass
- No unresolved review threads

```bash
gh pr checks <N>  # verify all green
```

### 6. Merge + Cleanup

```bash
gh pr merge <N> --merge --delete-branch
git worktree remove ../llama-ai-wt/<kebab-name>
```

## Must-follow rules

1. **GitHub-first issue discipline.** Every work item → GitHub issue first → worktree branch → implement → PR. No direct pushes to main.
2. **Client-side only.** No build step, no bundler, no server. Pure HTML + JS + CSS. GitHub Pages serves `index.html`.
3. **Real links everywhere.** Every activity item must link to the actual GitHub resource (PR, issue, commit, review).
4. **Filterable views.** Page must have filter buttons: All, PRs, Issues, Commits, Reviews, Forks, Stars.
5. **Summary content.** Each activity must show descriptive summary — PR description, issue title/body excerpt, commit messages.
6. **Deep CI.** Every feature must have tests. CI runs lint + test on every PR.
7. **Test before claim.** Never report done without real `pytest` + CI green.
8. **Commit early on worktrees.** Make a first unique commit immediately after creating files, or the auto-cleaner may delete your worktree.

## Folder structure

```
index.html                  # Main page (root for GitHub Pages)
src/
  pulse.py                  # GitHub API core + formatting
  x_poster.py               # X/Twitter poster
  linkedin_poster.py        # LinkedIn poster
scripts/
  daily_pulse.py            # CLI: generate + post
  run_local_server.py       # Dev server
tests/
  conftest.py               # Mock fixtures
  test_pulse.py             # Core logic tests
  test_page.py              # Page structure tests
  test_posters.py           # Poster tests
specs/changes/              # OpenSpec changes (if applicable)
.github/workflows/
  ci.yml                    # Lint + test on PR/push
  daily-pulse.yml           # Daily social post cron
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest tests/ -v                    # all tests
pytest tests/test_pulse.py -v       # core logic only
pytest tests/test_page.py -v        # page structure only
ruff check src/ tests/ scripts/     # lint
```

## CI pipeline

- **ci.yml**: runs on push + PR. Steps: lint → test → build check → page validation
- **daily-pulse.yml**: 09:00 UTC daily. Generate post → log → post to X/LinkedIn

## Social posting secrets

Set in GitHub repo secrets:
- `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`, `X_BEARER_TOKEN`
- `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`, `LINKEDIN_ACCESS_TOKEN`

## Conventions

- Python 3.11+, type hints everywhere
- Conventional Commits (feat:, fix:, docs:, test:, ci:)
- No external JS/CDN dependencies on the page (zero-dependency, fully self-contained)
- All emoji rendered via Unicode (no image dependencies)
- Every PR must reference the issue it closes
- Every PR must have CI green before merge

## Current Issues to Track

When starting/resuming work, always check open issues:

```bash
gh issue list --state open
```

Each open issue must have a worktree + PR in flight. If not, start work on it immediately.
