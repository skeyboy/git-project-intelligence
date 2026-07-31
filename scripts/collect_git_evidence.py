#!/usr/bin/env python3
"""Collect bounded, read-only Git evidence as JSON using only the standard library."""

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path


FIELD = "\x1f"
RECORD = "\x1e"


def git(repo, *args):
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--revision", default="HEAD")
    parser.add_argument("--since")
    parser.add_argument("--until")
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--max-commits", type=int, default=2000)
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument("--output", help="Write JSON to this path; stdout when omitted")
    return parser.parse_args()


def main():
    args = parse_args()
    repo = Path(args.repo).resolve()
    root = Path(git(repo, "rev-parse", "--show-toplevel").strip())
    head = git(root, "rev-parse", args.revision).strip()
    branch = git(root, "branch", "--show-current").strip()
    shallow = git(root, "rev-parse", "--is-shallow-repository").strip() == "true"

    log_args = [
        "log", args.revision, f"--max-count={max(1, args.max_commits)}",
        "--date=iso-strict", f"--format={RECORD}%H{FIELD}%aN{FIELD}%aE{FIELD}%aI{FIELD}%s",
        "--numstat", "--no-renames",
    ]
    if args.since:
        log_args.append(f"--since={args.since}")
    if args.until:
        log_args.append(f"--until={args.until}")
    if args.path:
        log_args.extend(["--", *args.path])

    raw = git(root, *log_args)
    commits = []
    author_stats = collections.defaultdict(lambda: {"commits": 0, "added": 0, "deleted": 0, "files": collections.Counter()})
    file_stats = collections.Counter()

    for block in raw.split(RECORD):
        block = block.strip("\n")
        if not block:
            continue
        lines = block.splitlines()
        fields = lines[0].split(FIELD)
        if len(fields) != 5:
            continue
        sha, name, email, authored_at, subject = fields
        files = []
        added_total = deleted_total = 0
        for line in lines[1:]:
            parts = line.split("\t", 2)
            if len(parts) != 3:
                continue
            added, deleted, path = parts
            added_n = int(added) if added.isdigit() else 0
            deleted_n = int(deleted) if deleted.isdigit() else 0
            files.append({"path": path, "added": added_n, "deleted": deleted_n, "binary": added == "-"})
            added_total += added_n
            deleted_total += deleted_n
            file_stats[path] += 1
            author_stats[(name, email)]["files"][path] += 1
        stats = author_stats[(name, email)]
        stats["commits"] += 1
        stats["added"] += added_total
        stats["deleted"] += deleted_total
        commits.append({"sha": sha, "author_name": name, "author_email": email, "authored_at": authored_at, "subject": subject, "files": files})

    authors = []
    for (name, email), stats in sorted(author_stats.items(), key=lambda item: (-item[1]["commits"], item[0])):
        authors.append({
            "name": name,
            "email": email,
            "commits": stats["commits"],
            "added": stats["added"],
            "deleted": stats["deleted"],
            "top_files": [{"path": path, "commits": count} for path, count in stats["files"].most_common(args.top)],
        })

    payload = {
        "repository": str(root),
        "revision": args.revision,
        "head": head,
        "branch": branch,
        "shallow": shallow,
        "filters": {"since": args.since, "until": args.until, "paths": args.path, "max_commits": args.max_commits},
        "commit_count": len(commits),
        "authors": authors,
        "hot_files": [{"path": path, "commits": count} for path, count in file_stats.most_common(args.top)],
        "commits": commits,
        "caveats": ["Author aliases are not merged.", "Rename detection is disabled for deterministic bounded collection.", "Line counts are descriptive and must not be used as productivity scores."],
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
