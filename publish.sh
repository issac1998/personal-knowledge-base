#!/bin/sh
set -eu

cd "$(dirname "$0")"
python3 sync.py "$@"
git add -A -- content docs site.zip

if ! git diff --cached --quiet; then
  git commit -m "Sync knowledge base $(date +%F)"
fi

env -u HTTPS_PROXY -u HTTP_PROXY -u ALL_PROXY git push origin main
