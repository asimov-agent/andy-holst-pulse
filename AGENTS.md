---
name: andy-holst-pulse
description: "Dynamic GitHub activity dashboard for Andy Holst with deep links, filtering, and OpenSpec workflow."
version: 1.0.0
---

# AGENTS.md — Andy Holst Pulse

Behavior file for agent workflow in this repo. Follow this on every session.

## Repo purpose

Dynamic GitHub activity dashboard for [@andyholst](https://github.com/andyholst). Fully client-side — fetches live from GitHub API. Posts daily summaries to X/LinkedIn.

Live URL: https://asimov-agent.github.io/andy-holst-pulse/

## Must-follow rules

1. **GitHub-first issue discipline.** Every work item → GitHub issue first → OpenSpec change → implement → PR. No direct pushes to main.
2. **Client-side only.** No build step, no bundler, no server. Pure HTML + JS + CSS. GitHub Pages serves `index.html`.
3. **Real links everywhere.** Every activity item must link to the actual GitHub resource (PR, issue, commit, review).
4. **Filterable views.** Page must have filter buttons: All, PRs, Issues, Commits, Reviews, Forks, Stars.
5. **Summary content.** Each activity must show descriptive summary — PR description, issue title/body excerpt, commit messages.
6. **Deep CI.** Every feature must have tests. CI runs lint + test on every PR.
7. **Test before claim.** Never report done without real `pytest` + CI green.
8. **OpenSpec is the referee.** If anything drifts between issue, OpenSpec, code, and tests — fix it.

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
specs/changes/              # OpenSpec changes
.github/workflows/
  ci.yml                    # Lint + test on PR/push
  daily-pulse.yml           # Daily social post cron
```

## OpenSpec workflow

For every change:
1. Create GitHub issue describing the goal
2. `make openspec-new NAME=<kebab-name>` (via container)
3. Write proposal.md + specs/<cap>/spec.md + tasks.md
4. Implement, tick tasks, validate with `make openspec-validate NAME=<name>`
5. Open PR, CI green, merge

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
