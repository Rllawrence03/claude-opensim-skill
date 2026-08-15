#!/usr/bin/env python3
"""
Checks GitHub for updates to this skill.

Compares the local repo's HEAD commit against the tip of the same branch
on the "origin" remote, via `git ls-remote`. This reuses whatever git
credentials already work for cloning (SSH key, cached HTTPS auth), so it
works for private repos too -- unlike the unauthenticated GitHub REST API.

Meant to be run at most once per Claude session (see SKILL.md), since it
makes a network call.

Usage:
  python check_updates.py

Prints JSON to stdout, one of:
  {"up_to_date": true, "local_sha": "...", "remote_sha": "...",
   "branch": "...", "compare_url": "..."}
  {"error": "..."}   on any failure (not a git checkout, no network, etc.)
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_git(*args, timeout=15):
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def parse_owner_repo(remote_url: str):
    """Best-effort github.com owner/repo for the compare_url. None if unparseable."""
    match = re.search(r"github\.com[:/]([^/]+)/([^/.]+?)(\.git)?$", remote_url.strip())
    return (match.group(1), match.group(2)) if match else None


def main():
    try:
        local_sha = run_git("rev-parse", "HEAD")
        branch = run_git("rev-parse", "--abbrev-ref", "HEAD")
        remote_url = run_git("remote", "get-url", "origin")
        ls_remote = run_git("ls-remote", "origin", f"refs/heads/{branch}", timeout=15)
    except (RuntimeError, subprocess.TimeoutExpired) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    if not ls_remote:
        print(json.dumps({"error": f"branch '{branch}' not found on origin"}))
        sys.exit(1)

    remote_sha = ls_remote.split()[0]
    result = {
        "up_to_date": local_sha == remote_sha,
        "local_sha": local_sha,
        "remote_sha": remote_sha,
        "branch": branch,
    }
    owner_repo = parse_owner_repo(remote_url)
    if owner_repo:
        owner, repo = owner_repo
        result["compare_url"] = f"https://github.com/{owner}/{repo}/compare/{local_sha}...{remote_sha}"

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
