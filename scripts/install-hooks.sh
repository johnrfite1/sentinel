#!/usr/bin/env bash
# Point git at the tracked hooks directory so the secret guard travels with the
# repository instead of living in one machine's .git (A-007).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath .githooks
chmod +x .githooks/* scripts/*.sh
echo "hooks installed: core.hooksPath=.githooks"
