#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 work/build.py
python3 scripts/localize.py
