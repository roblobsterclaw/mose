#!/bin/bash
# MOSE Buy Zone — daily cron wrapper
# Runs Mon-Fri at 9:40 AM ET via crontab
# Logs to /tmp/mose_buyzone_cron.log

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"
LOG="/tmp/mose_buyzone_cron.log"

echo "=== $(date) ===" >> "$LOG"
/usr/bin/python3 /Users/joemac/Documents/mose/scripts/daily_buyzone_email.py >> "$LOG" 2>&1
echo "--- done ---" >> "$LOG"
