#!/bin/bash
# Double-click this on macOS to start the "drop a PDF, get an IIF" watcher.
# First-time setup in Terminal:  pip3 install -r requirements.txt
cd "$(dirname "$0")"
python3 watch_inbox.py
