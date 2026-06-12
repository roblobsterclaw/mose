# MOSE Security Lockdown — Status & Remaining Steps

Last updated: 2026-06-12

## Done in the repo (this branch)

- `joes-holdings.json`: real Truist account numbers removed; accounts now use
  generic ids (`account-1` …). The dashboard no longer renders account numbers.
- Dashboard password is no longer stored in plaintext in `index.html` (SHA-256
  hash comparison instead). NOTE: this only deters casual source-readers — on a
  public static site the JSON data files are still directly fetchable.

## Steps only Joe can do (in priority order)

### 1. Purge account numbers from git history

The old account numbers remain in every historical commit of a PUBLIC repo.
After this branch is merged, run on the Mac mini:

```bash
pip install git-filter-repo
cd "/Users/joemac/Documents/Codex CLI Projects/mission-control-dashboard/Codex 1/MOSE DASHBOARD"
git filter-repo --replace-text <(printf 'WA7-228511\nWA7-228512\nWA7-228509\n' | sed 's/$/==>REDACTED/')
git push origin --force --all
```

Then contact GitHub Support (https://support.github.com) and ask them to clear
cached views of the repository, since force-pushes don't purge GitHub's caches.

### 2. Make the repository private (recommended)

GitHub Pages on the free plan requires a public repo. Options:
- GitHub Pro (~$4/mo): private repo + Pages still works.
- Or move hosting: Cloudflare Pages free tier supports private repos and adds
  Cloudflare Access (real login) in front of the site.
- Or serve it from the Mac mini over Tailscale (fully private, no hosting bill).

### 3. Lock the Firebase Realtime Database

The dashboard syncs watchlist state to
`https://jfl-ttd-default-rtdb.firebaseio.com/mose` with no auth — anyone with
the URL can read AND overwrite it. In the Firebase console → Realtime
Database → Rules, restrict the `/mose` path (at minimum to authenticated
users, ideally to your own UID), then add Firebase Auth (anonymous sign-in
tied to a secret, or email login) to the dashboard's sync calls.

### 4. Change the dashboard password

The old one (`soccer12`) shipped in plaintext in a public repo for weeks —
assume it is known. Generate the new hash with:

```bash
python3 -c "import hashlib;print(hashlib.sha256('NEWPASS'.encode()).hexdigest())"
```

and paste it into `PW_HASH` in `index.html`.
