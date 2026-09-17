#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required. Install Node.js 20 or later, then run ./run.sh again." >&2
  exit 1
fi
exec node server.mjs
