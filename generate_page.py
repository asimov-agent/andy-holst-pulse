#!/usr/bin/env python3
"""Generate a fancy HTML dashboard of Andy Holst's GitHub activity."""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from collections import defaultdict

GITHUB_USER = "andyholst"
API_BASE = f"https://api.github.com/users/{GITHUB_USER}"

# Color palette for repos
REPO_COLORS = [
    "#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7",
    "#dfe6e9", "#fd79a8", "#a29bfe", "#6c5ce7", "#00b894",
    "#e17055", "#fdcb6e", "#e84393", "#00cec9", "#fab1a0",
]

def gh_api(path: str):
    url = f"{API_BASE}/{path}"
    result = subprocess.run(
        ["curl", "-s", "-H", "Accept: application/vnd.github+json", url],
        capture_output=True, text=True, timeout=30
    )
    try:
        return json.loads(result.stdout)
    except:
        return []

def get_events():
    return gh_api("events/public?per_page=100")

def get_user():
    return gh_api("")

def get_repos():
    return gh_api("repos?per_page=100&sort=updated")

def format_relative(dt_str):
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff = now - dt
    if diff.days > 0:
        return f"{diff.days}d ago"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    mins = diff.seconds // 60
    return f"{mins}m ago"

def event_icon(etype):
    icons = {
        "PushEvent": "📦",
        "PullRequestEvent": "🔀",
        "PullRequestReviewEvent": "👀",
        "CreateEvent": "🌱",
        "ForkEvent": "🍴",
        "WatchEvent": "⭐",
        "IssueCommentEvent": "💬",
        "IssuesEvent": "🐛",
        "ReleaseEvent": "🚀",
        "DeleteEvent": "🗑️",
    }
    return icons.get(etype, "✨")

def event_description(e):
    etype = e["type"]
    repo = e["repo"].get("name", "").split("/")[-1]
    payload = e["payload"]

    if etype == "PushEvent":
        commits = payload.get("commits", [])
        count = len(commits)
        if count == 1:
            msg = commits[0]["message"].split("\n")[0][:60]
            return f"Pushed 1 commit to <b>{repo}</b>: <i>{msg}</i>"
        return f"Pushed <b>{count}</b> commits to <b>{repo}</b>"

    elif etype == "PullRequestEvent":
        pr = payload.get("pull_request", {})
        title = pr.get("title", "?")[:60]
        action = payload.get("action", "?")
        merged = pr.get("merged", False)
        if action == "opened":
            return f"Opened PR on <b>{repo}</b>: <i>{title}</i>"
        elif action == "closed" and merged:
            return f"✅ Merged PR on <b>{repo}</b>: <i>{title}</i>"
        elif action == "closed":
            return f"Closed PR on <b>{repo}</b>: <i>{title}</i>"
        return f"PR [{action}] on <b>{repo}</b>"

    elif etype == "PullRequestReviewEvent":
        return f"👀 Reviewed a PR on <b>{repo}</b>"

    elif etype == "CreateEvent":
        ref = payload.get("ref", "?")
        rtype = payload.get("ref_type", "?")
        return f"🌱 Created {rtype} <b>{ref}</b> in <b>{repo}</b>"

    elif etype == "ForkEvent":
        return f"🍴 Forked <b>{repo}</b>"

    elif etype == "WatchEvent":
        return f"⭐ Starred <b>{repo}</b>"

    elif etype == "IssueCommentEvent":
        return f"💬 Commented on an issue in <b>{repo}</b>"

    elif etype == "ReleaseEvent":
        return f"🚀 Released on <b>{repo}</b>"

    return f"{event_icon(etype)} {etype} on <b>{repo}</b>"

def generate_html(events, user, repos):
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%B %d, %Y at %H:%M UTC")

    # Stats
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    followers = user.get("followers", 0)
    following = user.get("following", 0)

    # Activity stats
    commits_count = sum(len(e["payload"].get("commits", [])) for e in events if e["type"] == "PushEvent")
    prs_opened = sum(1 for e in events if e["type"] == "PullRequestEvent" and e["payload"].get("action") == "opened")
    prs_merged = sum(1 for e in events if e["type"] == "PullRequestEvent" and e["payload"].get("pull_request", {}).get("merged"))
    repos_active = len(set(e["repo"].get("name", "") for e in events))

    # Repo activity counts
    repo_counts = defaultdict(int)
    for e in events:
        repo_counts[e["repo"].get("name", "").split("/")[-1]] += 1
    top_repos = sorted(repo_counts.items(), key=lambda x: -x[1])[:8]

    # Build events HTML
    events_html = ""
    for e in events[:50]:
        icon = event_icon(e["type"])
        desc = event_description(e)
        time = format_relative(e["created_at"])
        events_html += f'''
        <div class="event-item">
            <span class="event-icon">{icon}</span>
            <span class="event-desc">{desc}</span>
            <span class="event-time">{time}</span>
        </div>'''

    # Build repo bars
    max_count = max((c for _, c in top_repos), default=1)
    repo_bars = ""
    for i, (name, count) in enumerate(top_repos):
        color = REPO_COLORS[i % len(REPO_COLORS)]
        width = (count / max_count) * 100
        repo_bars += f'''
        <div class="repo-bar">
            <span class="repo-name">{name}</span>
            <div class="bar-track">
                <div class="bar-fill" style="width:{width}%;background:{color}"></div>
            </div>
            <span class="repo-count">{count}</span>
        </div>'''

    # Top repos cards
    repo_cards = ""
    for r in repos[:8]:
        name = r.get("name", "?")
        desc = (r.get("description") or "")[:80]
        stars = r.get("stargazers_count", 0)
        forks = r.get("forks_count", 0)
        lang = r.get("language") or ""
        color = REPO_COLORS[hash(name) % len(REPO_COLORS)]
        repo_cards += f'''
        <a href="{r.get("html_url", "#")}" class="repo-card" target="_blank">
            <div class="repo-card-header">
                <span class="repo-card-name">{name}</span>
                <span class="repo-card-lang" style="color:{color}">{lang}</span>
            </div>
            <p class="repo-card-desc">{desc}</p>
            <div class="repo-card-stats">
                <span>⭐ {stars}</span>
                <span>🍴 {forks}</span>
            </div>
        </a>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Andy Holst — GitHub Pulse</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #0a0a0f;
  --surface: #12121a;
  --surface2: #1a1a25;
  --border: #2a2a3a;
  --text: #e4e4ef;
  --text2: #9494a8;
  --accent: #6c5ce7;
  --accent2: #a29bfe;
  --green: #00b894;
  --red: #ff6b6b;
  --yellow: #ffeaa7;
  --blue: #74b9ff;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: 'Inter', -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  line-height: 1.6;
}}
.container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }}

/* Header */
.header {{
  display: flex; align-items: center; gap: 1.5rem;
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--border);
}}
.avatar {{
  width: 80px; height: 80px; border-radius: 50%;
  border: 3px solid var(--accent);
  box-shadow: 0 0 30px rgba(108,92,231,0.3);
}}
.header-info h1 {{
  font-size: 1.8rem; font-weight: 800;
  background: linear-gradient(135deg, var(--accent2), var(--blue));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.header-info .handle {{ color: var(--text2); font-size: 0.95rem; }}
.header-info .bio {{ color: var(--text2); font-size: 0.85rem; margin-top: 0.25rem; }}

/* Stats row */
.stats-row {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem; margin-bottom: 2.5rem;
}}
.stat-card {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 1.2rem; text-align: center;
  transition: transform 0.2s, border-color 0.2s;
}}
.stat-card:hover {{ transform: translateY(-2px); border-color: var(--accent); }}
.stat-value {{ font-size: 1.8rem; font-weight: 700; color: var(--accent2); }}
.stat-label {{ font-size: 0.75rem; color: var(--text2); text-transform: uppercase; letter-spacing: 0.5px; }}

/* Grid */
.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2.5rem; }}
@media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}

/* Section */
.section {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 16px; padding: 1.5rem;
}}
.section-title {{
  font-size: 1rem; font-weight: 600; margin-bottom: 1rem;
  display: flex; align-items: center; gap: 0.5rem;
  color: var(--text);
}}

/* Events */
.events-list {{ max-height: 600px; overflow-y: auto; }}
.event-item {{
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.6rem 0; border-bottom: 1px solid var(--border);
  font-size: 0.85rem;
}}
.event-item:last-child {{ border-bottom: none; }}
.event-icon {{ font-size: 1.1rem; flex-shrink: 0; }}
.event-desc {{ flex: 1; color: var(--text); }}
.event-desc i {{ color: var(--text2); font-style: normal; }}
.event-time {{ color: var(--text2); font-size: 0.75rem; flex-shrink: 0; font-family: 'JetBrains Mono', monospace; }}

/* Repo bars */
.repo-bar {{
  display: flex; align-items: center; gap: 0.75rem;
  margin-bottom: 0.6rem; font-size: 0.8rem;
}}
.repo-name {{ width: 100px; flex-shrink: 0; color: var(--text2); font-weight: 500; }}
.bar-track {{ flex: 1; height: 8px; background: var(--surface2); border-radius: 4px; overflow: hidden; }}
.bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.5s ease; }}
.repo-count {{ width: 25px; text-align: right; color: var(--text2); font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; }}

/* Repo cards */
.repos-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem; margin-bottom: 2.5rem;
}}
.repo-card {{
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 1.2rem; text-decoration: none; color: inherit;
  transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
}}
.repo-card:hover {{
  transform: translateY(-3px); border-color: var(--accent);
  box-shadow: 0 8px 30px rgba(108,92,231,0.15);
}}
.repo-card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}
.repo-card-name {{ font-weight: 600; font-size: 0.9rem; }}
.repo-card-lang {{ font-size: 0.7rem; font-weight: 600; }}
.repo-card-desc {{ font-size: 0.75rem; color: var(--text2); margin-bottom: 0.75rem; line-height: 1.4; }}
.repo-card-stats {{ display: flex; gap: 1rem; font-size: 0.75rem; color: var(--text2); }}

/* Footer */
.footer {{
  text-align: center; padding: 2rem 0; color: var(--text2);
  font-size: 0.8rem; border-top: 1px solid var(--border);
  margin-top: 2rem;
}}
.footer a {{ color: var(--accent2); text-decoration: none; }}
.footer a:hover {{ text-decoration: underline; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: var(--surface); }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}

/* Animations */
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.event-item, .repo-card, .stat-card {{ animation: fadeIn 0.4s ease both; }}
</style>
</head>
<body>
<div class="container">

<!-- Header -->
<div class="header">
  <img class="avatar" src="{user.get('avatar_url','')}" alt="Andy Holst">
  <div class="header-info">
    <h1>{user.get('name', 'Andy Holst')}</h1>
    <div class="handle">@{GITHUB_USER} · {user.get('location','Sweden')}</div>
    <div class="bio">{user.get('bio','DevSecOps Software Engineer & Business Owner')}</div>
  </div>
</div>

<!-- Stats -->
<div class="stats-row">
  <div class="stat-card">
    <div class="stat-value">{followers}</div>
    <div class="stat-label">Followers</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">{following}</div>
    <div class="stat-label">Following</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">{len(repos)}</div>
    <div class="stat-label">Repos</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">{total_stars}</div>
    <div class="stat-label">Stars</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">{total_forks}</div>
    <div class="stat-label">Forks</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">{len(events)}</div>
    <div class="stat-label">Recent Events</div>
  </div>
</div>

<!-- Activity Stats -->
<div class="stats-row" style="margin-bottom:2rem">
  <div class="stat-card" style="border-color:var(--green)">
    <div class="stat-value" style="color:var(--green)">{commits_count}</div>
    <div class="stat-label">Commits (30d)</div>
  </div>
  <div class="stat-card" style="border-color:var(--blue)">
    <div class="stat-value" style="color:var(--blue)">{prs_opened}</div>
    <div class="stat-label">PRs Opened</div>
  </div>
  <div class="stat-card" style="border-color:var(--accent)">
    <div class="stat-value" style="color:var(--accent2)">{prs_merged}</div>
    <div class="stat-label">PRs Merged</div>
  </div>
  <div class="stat-card" style="border-color:var(--yellow)">
    <div class="stat-value" style="color:var(--yellow)">{repos_active}</div>
    <div class="stat-label">Active Repos</div>
  </div>
</div>

<!-- Two column: Events + Repo Activity -->
<div class="grid">
  <div class="section">
    <div class="section-title">⚡ Recent Activity</div>
    <div class="events-list">
      {events_html}
    </div>
  </div>
  <div class="section">
    <div class="section-title">📊 Top Active Repos</div>
    {repo_bars}
  </div>
</div>

<!-- Repo Cards -->
<div class="section" style="margin-bottom:2rem">
  <div class="section-title">📦 Featured Repositories</div>
  <div class="repos-grid">
    {repo_cards}
  </div>
</div>

<!-- Footer -->
<div class="footer">
  <p>🔥 <b>GitHub Pulse</b> for <a href="https://github.com/{GITHUB_USER}">@{GITHUB_USER}</a></p>
  <p style="margin-top:0.5rem">
    <a href="https://docondee.com">🌐 docondee.com</a> ·
    <a href="https://x.com/andy_a_holst">𝕏 @andy_a_holst</a> ·
    <a href="https://linkedin.com/in/andy-holst-devops-software-engineer">💼 LinkedIn</a>
  </p>
  <p style="margin-top:0.75rem; opacity:0.6">Generated {date_str} · Auto-updates daily</p>
</div>

</div>
</body>
</html>'''
    return html

def main():
    print("🔍 Fetching data...", file=sys.stderr)

    user = get_user()
    events = get_events()
    repos = get_repos()

    print(f"  User: {user.get('login','?')}", file=sys.stderr)
    print(f"  Events: {len(events)}", file=sys.stderr)
    print(f"  Repos: {len(repos)}", file=sys.stderr)

    html = generate_html(events, user, repos)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    with open(output_path, "w") as f:
        f.write(html)

    print(f"✅ Generated {output_path}", file=sys.stderr)

if __name__ == "__main__":
    main()
