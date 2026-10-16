#!/usr/bin/env python3
"""Report upstream changes and S23 review points without merging or changing source."""

import argparse
import json
from pathlib import Path
import subprocess
import sys


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def report(root: Path, config: dict, fetch: bool = False) -> dict:
    upstream = config["ghostsam"]
    actual_url = git(root, "remote", "get-url", "upstream")
    if actual_url != upstream["upstream_url"]:
        raise RuntimeError(f"Unexpected upstream URL: {actual_url}")
    if fetch:
        git(root, "fetch", "--no-tags", "upstream", upstream["default_branch"])
    baseline = git(root, "rev-parse", "--verify", f'{upstream["baseline"]}^{{commit}}')
    target = git(root, "rev-parse", "--verify", f'{upstream["tracking_ref"]}^{{commit}}')
    git(root, "merge-base", "--is-ancestor", baseline, target)
    reviewed = git(root, "rev-parse", "--verify", f'{upstream.get("reviewed_commit", baseline)}^{{commit}}')
    git(root, "merge-base", "--is-ancestor", baseline, reviewed)
    git(root, "merge-base", "--is-ancestor", reviewed, target)
    incoming = git(root, "diff", "--name-only", baseline, target).splitlines()
    local = git(root, "diff", "--name-only", baseline, "HEAD").splitlines()
    local_paths = set(local)
    review = [
        path for path in incoming
        if path in local_paths or any(path.startswith(prefix) for prefix in config["review_prefixes"])
    ]
    return {
        "baseline": baseline,
        "upstream": target,
        "reviewed": reviewed,
        "unreviewed_commits": git(root, "log", "--oneline", f"{reviewed}..{target}").splitlines(),
        "adopted_changes": upstream.get("adopted_changes", []),
        "incoming_commits": git(root, "log", "--oneline", f"{baseline}..{target}").splitlines(),
        "incoming_paths": incoming,
        "review_paths": review,
        "working_tree_changes": git(root, "status", "--short").splitlines(),
        "kernelsu": config["kernelsu"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Refresh upstream/main first")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable report")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        config = json.loads((root / "maintenance/s23-baseline.json").read_text(encoding="utf-8"))
        result = report(root, config, args.fetch)
    except (KeyError, OSError, RuntimeError, ValueError) as error:
        print(f"check-upstream: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    else:
        print(f'Baseline: {result["baseline"]}')
        print(f'Upstream: {result["upstream"]}')
        print(f'Reviewed through: {result["reviewed"]}')
        print(f'New commits awaiting review: {len(result["unreviewed_commits"])}')
        print(f'Upstream commits since the integrated baseline: {len(result["incoming_commits"])}')
        for commit in result["incoming_commits"]:
            print(f"  {commit}")
        print(f'Files requiring S23 review: {len(result["review_paths"])}')
        for path in result["review_paths"]:
            print(f"  {path}")
        print(f'Pinned KernelSU: {result["kernelsu"]["revision"]}')
        print("Reviewed commits are not automatically adopted; see the recorded review decisions.")
        if result["working_tree_changes"]:
            print("Working tree has local changes; preserve them before a future merge.")
        print("Report complete. No merge or source changes were performed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
