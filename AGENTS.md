---
name: andy-holst-pulse
description: "Dynamic GitHub activity dashboard for Andy Holst — design-first, strict PR-only workflow."
version: 2.1.0
---

# AGENTS.md — Andy Holst Pulse

**Follow this on every session. Zero exceptions.**

## ⚡ ZERO EXCEPTIONS — NO DIRECT PUSHES TO MAIN

**NEVER push directly to main. NEVER work on main directly. ZERO EXCEPTIONS.**

This applies to EVERY change without exception:

| Change Type | Direct push to main? | Required path |
|-------------|---------------------|---------------|
| Code changes | ❌ FORBIDDEN | Issue → Worktree → Branch → PR |
| Documentation (including THIS file) | ❌ FORBIDDEN | Issue → Worktree → Branch → PR |
| Reverts of bad commits | ❌ FORBIDDEN | Issue → Worktree → Branch → PR |
| Hotfixes | ❌ FORBIDDEN | Issue → Worktree → Branch → PR |
| CI/CD config changes | ❌ FORBIDDEN | Issue → Worktree → Branch → PR |
| Dependency updates | ❌ FORBIDDEN | Issue → Worktree → Branch → PR |

### Anti-patterns (things you must NEVER do)

1. **`git push origin main`** — This will be blocked by CI and is a workflow violation.
2. **Committing on a `main` checkout** — Always work in a worktree, never on the main branch directly.
3. **Skipping the issue** — If there is no issue, create one first. The issue is the root of truth.
4. **Long-lived branches without PRs** — Open the PR as soon as you have a first commit.
5. **Merging your own PR without CI green** — CI must pass before merge. No exceptions.
6. **Force-pushing to main** — Never. Force-push only to your own feature branch after rebase.

### Self-check before every commit

Before you run `git push`, verify:
- [ ] I am NOT on the `main` branch (`git branch --show-current` → should show `feat/...`)
- [ ] My branch was created from latest `origin/main` via `git worktree add`
- [ ] The PR is open and references the issue
- [ ] CI is green on the PR

If any check fails, STOP and fix before pushing.

---

## Repo purpose

Dynamic GitHub activity dashboard for [@andyholst](https://github.com/andyholst). Fully client-side — fetches live from GitHub API every page load. No build step, no server.

Live URL: https://asimov-agent.github.io/andy-holst-pulse/

## Workflow: Issue → Worktree → Branch → PR (MANDATORY)

### 1. Create GitHub Issue FIRST

```bash
gh issue create \
  --title "<title>" \
  --body-file /path/to/issue_body.md
```

The issue is the root of truth. It describes the goal, design/analysis, acceptance criteria, and task checklist. **Work cannot begin without an issue.**

### 2. Create Worktree Branch

```bash
cd /Users/andy/repository/git/andy-holst-pulse
git fetch origin main
git worktree add -b feat/<kebab-name> ../andy-holst-wt/<kebab-name> origin/main
cd ../andy-holst-wt/<kebab-name>
```

The worktree lives OUTSIDE the main checkout. This allows parallel work without collisions. **You NEVER branch from the local `main` checkout** — always branch from `origin/main` into a worktree.

### 3. Implement + Test Inside Worktree

```bash
cd ../andy-holst-wt/<kebab-name>
# Write code + tests
PYTHONPATH=src:scripts pytest tests/ -v
ruff check src/ tests/ scripts/
# Commit early and often
git add -A && git commit -m "feat: <description>"
```

**Commit your first change immediately** after creating files — don't let work go uncommitted.

### 4. Push + Open PR

```bash
git push -u origin feat/<kebab-name>
gh pr create \
  --base main \
  --head feat/<kebab-name> \
  --title "feat: <kebab-name>" \
  --body "Completes #<issue_number>."
```

Open the PR **immediately after the first push** — do not wait for work to be "done".

### 5. CI Must Be GREEN Before Merge

```bash
gh pr checks <N>  # verify all green
```

Only merge when:
- CI pipeline passes (lint + test)
- All tests pass
- No unresolved review threads

### 6. Merge + Cleanup

```bash
gh pr merge <N> --merge --delete-branch
git worktree remove ../andy-holst-wt/<kebab-name>
```

After merge, remove the worktree to keep the workspace clean.

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
- No cron runs until the user enables it by adding repo secrets and uncommenting the workflow

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
.github/workflows/pr-only-main.yml  # Block direct pushes to main
.github/workflows/daily-pulse.yml  # Daily post (disabled without secrets)
AGENTS.md                     # This file
```

## Testing

```bash
PYTHONPATH=src:scripts pytest tests/ -v
ruff check src/ tests/ scripts/
```

## CI Enforcement

The `.github/workflows/pr-only-main.yml` job runs on every push to `main` and **blocks any commit that did not come from a PR merge**. This is automated enforcement of the zero-exceptions rule.

## Current state

- Page: live, dynamic, accessible, filterable
- Tests: 96 passing
- CI: green
- Workflow enforcement: automated via pr-only-main.yml
- Posting: designed, implemented, tested — but disabled until user adds secrets

## Conventions

- Python 3.11+, type hints, stdlib preferred
- Conventional Commits (feat:, fix:, docs:, test:, ci:)
- Every PR references its issue
- Every PR must have CI green before merge
- Every commit is on a feature branch in a worktree — NEVER on main
