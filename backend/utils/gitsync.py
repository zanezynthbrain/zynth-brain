"""Push the bot's live output to GitHub so Obsidian (Obsidian Git) pulls it.

The running bot on Railway has an ephemeral disk and never pushed to GitHub, so
its daily notes/data never reached the repo (or your Obsidian). This closes that
gap: it commits the vault notes + key data files to the repo via the GitHub Git
Data API — one clean commit, only when something actually changed.

Gracefully inert until configured. Set in Railway → Variables:
  GIT_SYNC_TOKEN   = a GitHub token with repo read/write on zynth-brain
                     (the SAME token you use in Obsidian Git)
  GIT_SYNC_REPO    = owner/repo   (optional, default zanezynthbrain/zynth-brain)
  GIT_SYNC_BRANCH  = branch       (optional, default main)

Only vault markdown + a few JSON data files are pushed — never .env or secrets.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path

import httpx

from utils.logging_config import get_logger

logger = get_logger("gitsync")

_API = "https://api.github.com"

# Files to publish (paths relative to the backend/ working dir). Repo path is
# prefixed with "backend/". Globs expand; missing files are skipped.
_INCLUDE_GLOBS = ["outputs/proposal_pool/vault/**/*.md"]
_INCLUDE_FILES = [
    "outputs/proposal_pool/prospects.json",
    "outputs/proposal_pool/leads.json",
    "outputs/proposal_pool/tasks.json",
    "outputs/proposal_pool/activity.json",
    "outputs/proposal_pool/business_state.json",
    "outputs/proposal_pool/suppliers_extra.json",
    "outputs/proposal_pool/venues_extra.json",
]


def _cfg() -> tuple[str, str, str]:
    return (
        os.getenv("GIT_SYNC_TOKEN", ""),
        os.getenv("GIT_SYNC_REPO", "zanezynthbrain/zynth-brain"),
        os.getenv("GIT_SYNC_BRANCH", "main"),
    )


def is_configured() -> bool:
    return bool(os.getenv("GIT_SYNC_TOKEN"))


def _collect() -> list[Path]:
    paths: list[Path] = []
    for g in _INCLUDE_GLOBS:
        paths.extend(sorted(Path(".").glob(g)))
    for f in _INCLUDE_FILES:
        p = Path(f)
        if p.exists():
            paths.append(p)
    return [p for p in paths if p.is_file()]


async def sync(message: str = "chore: sync ZYNTH vault + data") -> tuple[bool, str]:
    """Commit vault + data to GitHub in one commit (only if changed)."""
    token, repo, branch = _cfg()
    if not token:
        return False, "not configured (set GIT_SYNC_TOKEN)"
    files = _collect()
    if not files:
        return True, "nothing to sync yet"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    try:
        async with httpx.AsyncClient(timeout=45, headers=headers, trust_env=True) as c:
            # 1. current branch head
            r = await c.get(f"{_API}/repos/{repo}/git/ref/heads/{branch}")
            if r.status_code >= 300:
                return False, f"ref {r.status_code}: {r.text[:120]}"
            base_sha = r.json()["object"]["sha"]
            r = await c.get(f"{_API}/repos/{repo}/git/commits/{base_sha}")
            base_tree = r.json()["tree"]["sha"]

            # 2. blobs
            tree_entries = []
            for p in files:
                content = p.read_bytes()
                rb = await c.post(
                    f"{_API}/repos/{repo}/git/blobs",
                    json={"content": base64.b64encode(content).decode(), "encoding": "base64"},
                )
                if rb.status_code >= 300:
                    logger.info("blob failed for %s: %s", p, rb.status_code)
                    continue
                tree_entries.append({
                    "path": f"backend/{p.as_posix()}",
                    "mode": "100644", "type": "blob", "sha": rb.json()["sha"],
                })
            if not tree_entries:
                return False, "no blobs created"

            # 3. tree
            rt = await c.post(
                f"{_API}/repos/{repo}/git/trees",
                json={"base_tree": base_tree, "tree": tree_entries},
            )
            if rt.status_code >= 300:
                return False, f"tree {rt.status_code}: {rt.text[:120]}"
            new_tree = rt.json()["sha"]
            if new_tree == base_tree:
                return True, "already up to date (nothing changed)"

            # 4. commit + move ref
            rc = await c.post(
                f"{_API}/repos/{repo}/git/commits",
                json={"message": message, "tree": new_tree, "parents": [base_sha]},
            )
            if rc.status_code >= 300:
                return False, f"commit {rc.status_code}: {rc.text[:120]}"
            new_commit = rc.json()["sha"]
            rp = await c.patch(
                f"{_API}/repos/{repo}/git/refs/heads/{branch}",
                json={"sha": new_commit, "force": False},
            )
            if rp.status_code >= 300:
                return False, f"ref-update {rp.status_code}: {rp.text[:120]}"
    except Exception as exc:
        logger.info("git sync failed: %s", type(exc).__name__)
        return False, f"error: {str(exc)[:140]}"

    logger.info("git sync: pushed %d files", len(tree_entries))
    return True, f"pushed {len(tree_entries)} files to {repo}@{branch}"
