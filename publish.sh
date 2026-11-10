#!/bin/sh
set -eu

cd "$(dirname "$0")"
python3 sync.py "$@"
git add -A -- content docs site.zip

if ! git diff --cached --quiet; then
  git commit -m "Sync knowledge base $(date +%F)"
fi

git push origin main
