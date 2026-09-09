#!/usr/bin/env bash
# Install / update the autonomous issue-worker cron job from repo definition.
# Idempotent: running again updates the existing job rather than duplicating it.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROMPT_FILE="${REPO}/scripts/issue_worker_prompt.md"
JOB_NAME="andy-holst-pulse-issue-worker"
SCHEDULE="*/20 * * * *"

if [ ! -f "$PROMPT_FILE" ]; then
  echo "[install] PROMPT FILE NOT FOUND: ${PROMPT_FILE}"
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "[install] gh CLI not found — install it first: brew install gh"
  exit 1
fi

if ! command -v hermes >/dev/null 2>&1; then
  echo "[install] hermes CLI not found — install it first: see https://hermes-agent.nousresearch.com/install.sh"
  exit 1
fi

# Check if job already exists (parse the job list output)
EXISTING="$(hermes cron list 2>/dev/null | grep -B1 "Name:.*${JOB_NAME}" | head -1 | awk '{print $1}' || true)"

PROMPT_CONTENT="$(cat "${PROMPT_FILE}")"

if [ -n "${EXISTING:-}" ]; then
  echo "[install] Updating existing job ${EXISTING}..."
  hermes cron edit "${EXISTING}" \
    --schedule "${SCHEDULE}" \
    --prompt "${PROMPT_CONTENT}" \
    --workdir "${REPO}" \
    --deliver origin \
    --skill github-activity-dashboard \
    --skill github-issue-to-pr
else
  echo "[install] Creating new cron job..."
  hermes cron create "${SCHEDULE}" \
    --name "${JOB_NAME}" \
    --prompt "${PROMPT_CONTENT}" \
    --workdir "${REPO}" \
    --deliver origin \
    --skill github-activity-dashboard \
    --skill github-issue-to-pr
fi

echo "[install] Done. Verify with: hermes cron list"
