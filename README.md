# Andy Holst — GitHub Pulse

Dynamic GitHub activity dashboard for [@andyholst](https://github.com/andyholst).

**Live page:** https://asimov-agent.github.io/andy-holst-pulse/

## What

- **index.html** — Self-contained client-side dashboard. Fetches live from GitHub API every page load. No build step, no backend.
- **src/pulse.py** — Shared core: fetches GitHub events + formats activity summaries. Used by the daily-post script and the page.
- **scripts/daily_pulse.py** — CLI entrypoint that generates a daily post and pushes to X/LinkedIn.
- **tests/** — Pytest suite covering core logic, formatting, and page structure.
- **.github/workflows/** — CI (lint + test) and daily-post cron.

## Project structure

```
.
├── AGENTS.md                    # Agent workflow doc
├── README.md                    # This file
├── index.html                   # Dynamic pulse page (entry at root for GitHub Pages)
├── requirements.txt             # Runtime deps
├── requirements-dev.txt         # Dev deps (pytest, ruff, etc.)
├── src/
│   ├── __init__.py
│   ├── pulse.py                 # GitHub API + formatting core
│   ├── x_poster.py              # X/Twitter posting
│   └── linkedin_poster.py       # LinkedIn posting
├── scripts/
│   ├── daily_pulse.py           # CLI: generate + post daily pulse
│   ├── run_local_server.py      # Dev server for local preview
│   ├── issue_worker_prompt.md   # Autonomous issue-worker cron prompt
│   └── install_cron.sh          # Install/update the issue-worker cron job
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Mock fixtures
│   ├── test_pulse.py            # Core logic tests
│   ├── test_posters.py          # Poster tests
│   └── test_page.py             # Page structure tests
└── .github/
    └── workflows/
        ├── ci.yml               # Lint + test on PR/push
        └── daily-pulse.yml      # Daily social post
```

## Running locally

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Preview page locally
python scripts/run_local_server.py

# Generate a daily post (dry-run, no actual posting)
python scripts/daily_pulse.py --dry-run

# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/ scripts/
```

## CI

- **ci.yml** — Runs on every push and PR. Lints with `ruff`, runs full pytest suite.
- **pr-only-main.yml** — Blocks direct pushes to main. All changes MUST go through PR.
- **daily-pulse.yml** — Runs at 09:00 UTC daily. Generates pulse, posts to X + LinkedIn, saves log.

## Workflow

All changes follow: **Issue → Worktree → Branch → PR → Merge**

**Zero exceptions.** No direct pushes to main — ever. Docs, reverts, hotfixes all go through PR.

CI enforces this: [pr-only-main.yml](.github/workflows/pr-only-main.yml) blocks any commit that did not come from a PR merge.

See [AGENTS.md](AGENTS.md) for the full workflow documentation.

## Autonomous issue worker

A Hermes cron job polls for open issues every 20 minutes and drives each one through the full workflow — worktree, implementation, tests, PR, CI gate, merge, cleanup. The job is defined by two files in the repo:

| File | Purpose |
|------|---------|
| `scripts/issue_worker_prompt.md` | The self-contained prompt the agent follows |
| `scripts/install_cron.sh` | Idempotent install/update script |

### Install or update

```bash
./scripts/install_cron.sh
```

This creates (or updates) the `andy-holst-pulse-issue-worker` cron job:

```bash
hermes cron list                          # verify it exists
hermes cron status                        # check scheduler is running
hermes cron run andy-holst-pulse-issue-worker   # trigger manually
```

### How it works

1. Polls `gh issue list --state open`
2. Skips issues that already have a live PR
3. For each remaining issue: worktree → implement → test → push → PR → CI green → **merge** → cleanup
4. Merge only happens when: CI green ✅ + approval ✅ + no open threads ✅
5. For single-account repos, it relaxes `required_approving_review_count` to 0, merges, then restores protection

### Requirements

- `gh` CLI installed and authenticated
- `hermes` CLI installed with gateway running (`hermes gateway start`)
- `GITHUB_TOKEN` or `GH_TOKEN` in repo `.env` (for push/PR/merge)

## Setup for posting to social

Set these repo secrets for the daily-pulse workflow:

| Secret | Source |
|--------|--------|
| `X_API_KEY` | https://developer.x.com/en/portal/dashboard |
| `X_API_SECRET` | same |
| `X_ACCESS_TOKEN` | same |
| `X_ACCESS_SECRET` | same |
| `X_BEARER_TOKEN` | same |
| `LINKEDIN_CLIENT_ID` | https://developer.linkedin.com/ |
| `LINKEDIN_CLIENT_SECRET` | same |
| `LINKEDIN_ACCESS_TOKEN` | same |

## License

MIT
