#!/usr/bin/env python3
"""Fetch GitHub fork history and render a cumulative SVG trend chart."""

import argparse
import datetime as dt
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, help="GitHub repository as owner/name")
    parser.add_argument("--output", default="assets/fork-trend.svg")
    parser.add_argument("--api-url", default="https://api.github.com")
    return parser.parse_args()


def request_json(url, token):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "git-project-intelligence-fork-trend",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API returned {exc.code}: {message}") from exc


def fetch_repository(api_url, repository, token):
    encoded = urllib.parse.quote(repository, safe="/")
    return request_json(f"{api_url.rstrip('/')}/repos/{encoded}", token)


def fetch_forks(api_url, repository, token):
    encoded = urllib.parse.quote(repository, safe="/")
    forks = []
    page = 1
    while True:
        url = (
            f"{api_url.rstrip('/')}/repos/{encoded}/forks"
            f"?per_page=100&sort=oldest&page={page}"
        )
        batch = request_json(url, token)
        if not isinstance(batch, list):
            raise RuntimeError("GitHub forks response was not a list")
        forks.extend(batch)
        if len(batch) < 100:
            return forks
        page += 1


def parse_github_time(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def cumulative_series(created_at, forks, today):
    start = parse_github_time(created_at).date()
    if today < start:
        raise RuntimeError("repository creation date is in the future")
    counts = {}
    for fork in forks:
        created = fork.get("created_at")
        if created:
            day = parse_github_time(created).date()
            counts[day] = counts.get(day, 0) + 1

    dates = []
    values = []
    cumulative = 0
    day = start
    while day <= today:
        cumulative += counts.get(day, 0)
        dates.append(day)
        values.append(cumulative)
        day += dt.timedelta(days=1)
    return dates, values


def escape_xml(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def tick_indexes(length, maximum=6):
    if length <= maximum:
        return list(range(length))
    return sorted({round(index * (length - 1) / (maximum - 1)) for index in range(maximum)})


def render_svg(repository, dates, values, generated_at):
    width, height = 960, 360
    left, right, top, bottom = 72, 72, 54, 62
    plot_width = width - left - right
    plot_height = height - top - bottom
    maximum = max(max(values), 1)

    def x(index):
        return left if len(values) == 1 else left + index * plot_width / (len(values) - 1)

    def y(value):
        return top + plot_height - value * plot_height / maximum

    points = " ".join(f"{x(index):.1f},{y(value):.1f}" for index, value in enumerate(values))
    area_points = f"{left},{top + plot_height} {points} {left + plot_width},{top + plot_height}"
    x_ticks = tick_indexes(len(dates))
    y_values = sorted({0, maximum // 2, maximum})
    total = values[-1]

    grid = []
    labels = []
    for value in y_values:
        position = y(value)
        grid.append(
            f'<line x1="{left}" y1="{position:.1f}" x2="{left + plot_width}" '
            'y2="{0:.1f}" class="grid"/>'.format(position)
        )
        labels.append(
            f'<text x="{left - 12}" y="{position + 4:.1f}" text-anchor="end" '
            f'class="axis-label">{value}</text>'
        )
    for index in x_ticks:
        position = x(index)
        labels.append(
            f'<text x="{position:.1f}" y="{top + plot_height + 30}" text-anchor="middle" '
            f'class="axis-label">{dates[index].isoformat()}</text>'
        )

    empty_note = "" if total else (
        f'<text x="{left + plot_width / 2:.1f}" y="{top + plot_height / 2:.1f}" '
        'text-anchor="middle" class="empty">No forks yet</text>'
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Cumulative GitHub fork trend for {escape_xml(repository)}</title>
  <desc id="desc">{total} cumulative forks from {dates[0].isoformat()} through {dates[-1].isoformat()}.</desc>
  <style>
    .background {{ fill: #ffffff; }}
    .title {{ fill: #1f2328; font: 600 18px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .meta {{ fill: #656d76; font: 12px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .axis-label {{ fill: #656d76; font: 11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .grid {{ stroke: #d8dee4; stroke-width: 1; }}
    .area {{ fill: #ddf4ff; }}
    .line {{ fill: none; stroke: #0969da; stroke-width: 3; stroke-linejoin: round; stroke-linecap: round; }}
    .empty {{ fill: #656d76; font: 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    @media (prefers-color-scheme: dark) {{
      .background {{ fill: #0d1117; }}
      .title {{ fill: #e6edf3; }}
      .meta, .axis-label, .empty {{ fill: #8d96a0; }}
      .grid {{ stroke: #30363d; }}
      .area {{ fill: #0c2d6b; }}
      .line {{ stroke: #58a6ff; }}
    }}
  </style>
  <rect class="background" width="100%" height="100%" rx="6"/>
  <text x="{left}" y="28" class="title">Cumulative GitHub Forks</text>
  <text x="{width - right}" y="28" text-anchor="end" class="meta">Updated {generated_at}</text>
  {''.join(grid)}
  {''.join(labels)}
  <polygon points="{area_points}" class="area"/>
  <polyline points="{points}" class="line"/>
  {empty_note}
</svg>
'''


def main():
    args = parse_args()
    token = os.environ.get("GITHUB_TOKEN")
    repository = fetch_repository(args.api_url, args.repository, token)
    forks = fetch_forks(args.api_url, args.repository, token)
    now = dt.datetime.now(dt.timezone.utc)
    dates, values = cumulative_series(repository["created_at"], forks, now.date())
    rendered = render_svg(args.repository, dates, values, now.strftime("%Y-%m-%d UTC"))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except (KeyError, OSError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"error: {exc}")
