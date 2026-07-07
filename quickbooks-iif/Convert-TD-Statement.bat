@echo off
REM ===================================================================
REM  Double-click this to start the "drop a PDF, get an IIF" watcher.
REM  Requires Python 3 installed (python.org) with PyMuPDF:
REM      pip install -r requirements.txt
REM  Then drop TD Bank statement PDFs into the "inbox" folder.
REM ===================================================================
cd /d "%~dp0"
python watch_inbox.py
pause
