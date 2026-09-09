---
name: andy-holst-pulse
description: "Dynamic GitHub activity dashboard for Andy Holst — design-first with issue→worktree→PR workflow."
version: 1.2.0
---

# AGENTS.md — Andy Holst Pulse

**Follow this on every session.**

## Repo purpose

Dynamic GitHub activity dashboard for [@andyholst](https://github.com/andyholst). Fully client-side — fetches live from GitHub API every page load. No build step, no server.

Live URL: https://asimov-agent.github.io/andy-holst-pulse/

## Design principles

1. **Client-side only.** Pure HTML + JS + CSS. Zero external JS dependencies.
2. **Real links everywhere.** Every activity item links to the actual GitHub resource.
3. **Accessible.** Semantic HTML, ARIA labels, skip-link, keyboard navigable.
4. **Filterable.** Users can filter by: All, PRs, Issues, Commits, Reviews, Forks, Stars, Releases.
5. **Self-contained.** The page works standalone — no backend, no API keys needed for viewing.

## Capability: Daily social posting (optional)

The codebase includes poster classes (`XPoster`, `LinkedInPoster`) that enable posting daily activity summaries to X/Twitter and LinkedIn.

This is **design-only until secrets are configured**:
- The daily-pulse workflow (`.github/workflows/daily-pulse.yml`) exists but has posting steps commented out
- Posters gracefully skip when API secrets are missing
- No cron runs until the user enables it by:
  1. Adding repo secrets (`X_API_KEY`, `X_API_SECRET`, etc.)
  2. Uncommenting the posting steps in the workflow

## Workflow: Issue → Worktree → Branch → PR

**NEVER push directly to main. NEVER work on main directly.**

### 1. Create GitHub Issue FIRST

Design the issue with clear goal, acceptance criteria, and task checklist.

```bash
gh issue create \
  --title "<title>" \
  --body "## Goal

## Design / Analysis

## Acceptance Criteria
- [ ] 

## Tasks
- [ ] "
```

### 2. Create Worktree Branch

```bash
cd /Users/andy/repository/git/andy-holst-pulse
git fetch origin main
git worktree add -b feat/<kebab-name> ../andy-holst-wt/<kebab-name> origin/main
cd ../andy-holst-wt/<kebab-name>
```

### 3. Implement + Test

- Write code + tests together
- Run `PYTHONPATH=src:scripts pytest tests/ -v`
- Run `ruff check src/ tests/ scripts/`
- Commit early and often

### 4. Open PR

```bash
cd ../andy-holst-wt/<kebab-name>
git push -u origin feat/<kebab-name>
gh pr create --base main --head feat/<kebab-name> \
  --title "feat: <kebab-name>" \
  --body "Completes #<issue_number>."
```

### 5. CI Must Be GREEN

```bash
gh pr checks <N>
```

### 6. Merge + Cleanup

```bash
gh pr merge <N> --merge --delete-branch
git worktree remove ../andy-holst-wt/<kebab-name>
```

## Folder structure

```
index.html                    # Main page (root for GitHub Pages)
src/pulse.py                  # GitHub API core + formatting
src/x_poster.py               # X/Twitter poster (optional)
src/linkedin_poster.py        # LinkedIn poster (optional)
scripts/daily_pulse.py        # CLI: generate + post (optional)
tests/test_pulse.py           # Core logic tests
tests/test_page.py            # Page structure + accessibility tests
tests/test_posters.py         # Poster tests
tests/test_daily_pulse.py     # CLI tests
.github/workflows/ci.yml      # Lint + test on push/PR
.github/workflows/daily-pulse.yml  # Daily post (disabled without secrets)
AGENTS.md                     # This file
```

## Testing

```bash
PYTHONPATH=src:scripts pytest tests/ -v
ruff check src/ tests/ scripts/
```

## Current state

- Page: live, dynamic, accessible, filterable
- Tests: 78 passing
- CI: green
- Posting: designed, implemented, tested — but disabled until user adds secrets

## Conventions

- Python 3.11+, type hints, stdlib preferred
- Conventional Commits (feat:, fix:, docs:, test:, ci:)
- Every PR references its issue
- Every PR must have CI green before merge
