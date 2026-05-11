#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python3 scripts/mose_db.py init
python3 scripts/mose_db.py import-snapshot --input reference-data/convergence-master.json
python3 scripts/mose_db.py export-dashboard-json --output reference-data/convergence-master.json
python3 scripts/mose_db.py status
