#!/bin/bash
# MOSE Dashboard Deploy Script
# Safe deploy — preserves data/ and reference-data/ folders

set -e

REPO="roblobsterclaw/mose"
BRANCH="gh-pages"

echo "Deploying MOSE Dashboard to GitHub Pages..."
git add -A
git commit -m "MOSE Dashboard update $(date '+%Y-%m-%d %H:%M')"
git push origin main

# Deploy to gh-pages (creates branch if needed)
git push origin `git subtree split --prefix . main`:gh-pages --force

echo "Live at: https://roblobsterclaw.github.io/mose/"
