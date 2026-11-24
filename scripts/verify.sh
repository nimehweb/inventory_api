#!/usr/bin/env bash
#
# Run the project's checks and test suite.
#
#   bash scripts/verify.sh
#
# Uses the running `web` container when Docker Compose is up, and falls back to
# a local virtual environment otherwise.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

manage() {
  if docker compose ps --status running --services 2>/dev/null | grep -qx web; then
    docker compose exec -T web python "$@"
  elif [[ -x .venv/bin/python ]]; then
    .venv/bin/python "$@"
  else
    python3 "$@"
  fi
}

printf '\n==> django check\n'
manage manage.py check

printf '\n==> migration drift check\n'
manage manage.py makemigrations --check --dry-run

printf '\n==> test suite\n'
set +e
manage manage.py test -v 2
TEST_STATUS=$?
set -e

printf '\nTest suite exit code: %s\n' "$TEST_STATUS"
