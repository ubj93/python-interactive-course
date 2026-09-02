#!/bin/sh
# Install the repository's git hooks (blocks commits and pushes to main).
set -e
cd "$(dirname "$0")/.."
git config core.hooksPath tools/hooks
echo "git hooks installed (core.hooksPath = tools/hooks)"
