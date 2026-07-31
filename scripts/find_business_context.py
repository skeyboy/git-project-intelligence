#!/usr/bin/env python3
"""Find keyword-linked code and Git history as business-analysis evidence."""

import argparse
import collections
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


FIELD = "\x1f"
RECORD = "\x1e"


def run(command, cwd, check=True):
    result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or f"command failed: {command[0]}")
    return result


def git(repo, *args):
    return run(["git", *args], repo).stdout


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--keyword", action="append", required=True)
    parser.add_argument("--revision", default="HEAD")
    parser.add_argument("--all-branches", action="store_true")
    parser.add_argument("--max-files", type=int, default=50)
    parser.add_argument("--max-commits", type=int, default=30)
    parser.add_argument("--samples-per-file", type=int, default=3)
    parser.add_argument("--output")
    return parser.parse_args()


def parse_commits(raw):
    commits = []
    for item in raw.split(RECORD):
        item = item.strip()
        if not item:
            continue
        fields = item.split(FIELD)
        if len(fields) == 4:
            commits.append(dict(zip(("sha", "authored_at", "author", "subject"), fields)))
    return commits


def main():
    args = parse_args()
    repo = Path(args.repo).resolve()
    root = Path(git(repo, "rev-parse", "--show-toplevel").strip())
    keywords = list(dict.fromkeys(item.strip() for item in args.keyword if item.strip()))
    if not keywords:
        raise RuntimeError("at least one non-empty keyword is required")
    if not shutil.which("rg"):
        raise RuntimeError("rg is required for current-code discovery")

    matches = collections.defaultdict(lambda: {"match_count": 0, "samples": []})
    command = ["rg", "--json", "--ignore-case", "--fixed-strings"]
    for keyword in keywords:
        command.extend(["-e", keyword])
    command.extend(["--glob", "!.git/**", "--glob", "!node_modules/**", "--glob", "!dist/**", "--glob", "!build/**", "."])
    result = run(command, root, check=False)
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.strip() or "rg failed")
    for line in result.stdout.splitlines():
        event = json.loads(line)
        if event.get("type") != "match":
            continue
        data = event["data"]
        path = data["path"]["text"]
        entry = matches[path]
        entry["match_count"] += len(data.get("submatches", [])) or 1
        if len(entry["samples"]) < max(1, args.samples_per_file):
            entry["samples"].append({"line": data["line_number"], "text": data["lines"]["text"].strip()[:300]})

    lowered = [keyword.casefold() for keyword in keywords]
    filenames = []
    files_result = run(["rg", "--files", "--glob", "!.git/**", "--glob", "!node_modules/**", "--glob", "!dist/**", "--glob", "!build/**"], root, check=False)
    if files_result.returncode in (0, 1):
        filenames = [path for path in files_result.stdout.splitlines() if any(word in path.casefold() for word in lowered)]

    pattern = "|".join(re.escape(keyword) for keyword in keywords)
    scope = "--all" if args.all_branches else args.revision
    log_format = f"{RECORD}%H{FIELD}%aI{FIELD}%aN{FIELD}%s"
    message_raw = git(root, "log", scope, f"--max-count={max(1, args.max_commits)}", "--extended-regexp", "--regexp-ignore-case", f"--grep={pattern}", f"--format={log_format}")
    change_raw = git(root, "log", scope, f"--max-count={max(1, args.max_commits)}", f"-G{pattern}", f"--format={log_format}")

    ranked_files = sorted(
        ({"path": path, **data} for path, data in matches.items()),
        key=lambda item: (-item["match_count"], item["path"]),
    )[: max(1, args.max_files)]
    payload = {
        "repository": str(root),
        "head": git(root, "rev-parse", args.revision).strip(),
        "scope": "all branches" if args.all_branches else args.revision,
        "keywords": keywords,
        "current_code_matches": ranked_files,
        "filename_matches": filenames[: max(1, args.max_files)],
        "commit_message_matches": parse_commits(message_raw),
        "diff_content_matches": parse_commits(change_raw),
        "caveats": [
            "Keyword matches are discovery seeds, not proof of business meaning.",
            "Generated, vendored, localized, stale, or dead files may rank highly.",
            "Trace candidate entry points through current runtime behavior before drawing conclusions.",
        ],
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
