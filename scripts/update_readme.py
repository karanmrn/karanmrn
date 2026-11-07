#!/usr/bin/env python3
"""Refresh the generated sections of README.md from the GitHub GraphQL API.

Every number in the README comes from this script, so the numbers are never
typed by hand. The script rewrites only the text between marker comments:

    <!-- generated:NAME:start --> ... <!-- generated:NAME:end -->

Sections: "pubmaxx", "contributions" and "activity".

Usage:
    GITHUB_TOKEN=... python3 scripts/update_readme.py [--readme README.md]

The token needs no scopes. Only public data is read and written.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request

LOGIN = "karanmrn"
PUBMAXX_REPO = "Singularityszn/pubmax"

# Repositories that are not open-source projects (for example a take-home
# test). They are left out of the contributions table.
HIDDEN_REPOS = {"sbms4d/wasb_sql_test"}

API_URL = "https://api.github.com/graphql"


class GitHub:
    def __init__(self, token: str) -> None:
        self.token = token

    def query(self, query: str, variables: dict | None = None) -> dict:
        body = json.dumps({"query": query, "variables": variables or {}}).encode()
        request = urllib.request.Request(
            API_URL,
            data=body,
            headers={
                "Authorization": f"bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": f"{LOGIN}-readme-updater",
            },
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
        if payload.get("errors"):
            raise RuntimeError(json.dumps(payload["errors"], indent=2))
        return payload["data"]

    def pr_count(self, repo: str, state: str) -> int:
        search = f"repo:{repo} type:pr author:{LOGIN} {state}"
        data = self.query(
            "query($q: String!) { search(query: $q, type: ISSUE) { issueCount } }",
            {"q": search},
        )
        return data["search"]["issueCount"]

    def calendar(self, start: dt.datetime | None = None, end: dt.datetime | None = None) -> dict:
        data = self.query(
            """
            query($login: String!, $from: DateTime, $to: DateTime) {
              user(login: $login) {
                contributionsCollection(from: $from, to: $to) {
                  contributionYears
                  totalCommitContributions
                  totalPullRequestContributions
                  totalPullRequestReviewContributions
                  totalIssueContributions
                  contributionCalendar {
                    totalContributions
                    weeks { contributionDays { date contributionCount } }
                  }
                }
              }
            }
            """,
            {
                "login": LOGIN,
                "from": start.isoformat() if start else None,
                "to": end.isoformat() if end else None,
            },
        )
        return data["user"]["contributionsCollection"]

    def contributed_repos(self) -> list[dict]:
        data = self.query(
            """
            query($login: String!) {
              user(login: $login) {
                repositoriesContributedTo(
                  first: 100
                  contributionTypes: [PULL_REQUEST]
                  includeUserRepositories: false
                  privacy: PUBLIC
                ) {
                  nodes { nameWithOwner url description isPrivate }
                }
              }
            }
            """,
            {"login": LOGIN},
        )
        return data["user"]["repositoriesContributedTo"]["nodes"]


def daily_counts(collection: dict) -> dict[str, int]:
    return {
        day["date"]: day["contributionCount"]
        for week in collection["contributionCalendar"]["weeks"]
        for day in week["contributionDays"]
    }


def longest_streak(days: dict[str, int]) -> int:
    best = run = 0
    previous = None
    for date in sorted(days):
        current = dt.date.fromisoformat(date)
        if days[date] > 0:
            run = run + 1 if previous and current - previous == dt.timedelta(days=1) else 1
            best = max(best, run)
        else:
            run = 0
        previous = current
    return best


def current_streak(days: dict[str, int], today: dt.date) -> int:
    """Count active days that end today, or yesterday if today has no activity yet."""
    day = today if days.get(today.isoformat(), 0) > 0 else today - dt.timedelta(days=1)
    streak = 0
    while days.get(day.isoformat(), 0) > 0:
        streak += 1
        day -= dt.timedelta(days=1)
    return streak


def pr_search_url(repo: str, state: str) -> str:
    query = urllib.parse.quote_plus(f"is:pr author:{LOGIN} {state}")
    return f"https://github.com/{repo}/pulls?q={query}"


def human_date(date: dt.date) -> str:
    return f"{date.day} {date:%B %Y}"


def fmt(number: int) -> str:
    return f"{number:,}"


def render_pubmaxx(gh: GitHub) -> str:
    merged = gh.pr_count(PUBMAXX_REPO, "is:merged")
    return (
        f"So far: [{fmt(merged)} merged pull requests]"
        f"({pr_search_url(PUBMAXX_REPO, 'is:merged')}) in "
        f"[{PUBMAXX_REPO}](https://github.com/{PUBMAXX_REPO})."
    )


def render_contributions(gh: GitHub) -> str:
    rows = []
    for repo in gh.contributed_repos():
        name = repo["nameWithOwner"]
        if repo["isPrivate"] or name in HIDDEN_REPOS or name == PUBMAXX_REPO:
            continue
        merged = gh.pr_count(name, "is:merged")
        opened = gh.pr_count(name, "is:open")
        if merged + opened == 0:
            continue
        rows.append((merged, opened, name, repo["url"], repo["description"] or ""))
    rows.sort(key=lambda row: (-row[0], -row[1], row[2].lower()))

    lines = [
        "| Project | What it is | Merged | Open |",
        "| --- | --- | ---: | ---: |",
    ]
    for merged, opened, name, url, description in rows:
        merged_cell = f"[{merged}]({pr_search_url(name, 'is:merged')})" if merged else "0"
        open_cell = f"[{opened}]({pr_search_url(name, 'is:open')})" if opened else "0"
        description = description.replace("|", "\\|").strip()
        lines.append(f"| [{name}]({url}) | {description} | {merged_cell} | {open_cell} |")
    return "\n".join(lines)


def render_activity(gh: GitHub, now: dt.datetime) -> str:
    today = now.date()
    last_year = gh.calendar()
    recent = daily_counts(last_year)

    all_days: dict[str, int] = {}
    for year in last_year["contributionYears"]:
        start = dt.datetime(year, 1, 1, tzinfo=dt.UTC)
        end = min(dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.UTC), now)
        first, last = start.date().isoformat(), end.date().isoformat()
        all_days.update(
            {date: count for date, count in daily_counts(gh.calendar(start, end)).items() if first <= date <= last}
        )
    first_year = min(last_year["contributionYears"])

    recent_active = sum(1 for count in recent.values() if count > 0)
    lifetime_active = sum(1 for count in all_days.values() if count > 0)
    lifetime_total = sum(all_days.values())

    since = human_date(dt.date.fromisoformat(min(recent)))
    rows = [
        (f"Contributions since {since}", fmt(last_year["contributionCalendar"]["totalContributions"])),
        (f"Active days since {since}", f"{fmt(recent_active)} of {fmt(len(recent))}"),
        ("Current streak", f"{fmt(current_streak(all_days, today))} days"),
        ("Longest streak", f"{fmt(longest_streak(all_days))} days"),
        (f"Active days since {first_year}", fmt(lifetime_active)),
        (f"Contributions since {first_year}", fmt(lifetime_total)),
    ]
    breakdown = (
        f"Since {since}: {fmt(last_year['totalCommitContributions'])} commits, "
        f"{fmt(last_year['totalPullRequestContributions'])} pull requests, "
        f"{fmt(last_year['totalPullRequestReviewContributions'])} reviews and "
        f"{fmt(last_year['totalIssueContributions'])} issues."
    )
    lines = ["| What | Number |", "| --- | ---: |"]
    lines += [f"| {label} | {value} |" for label, value in rows]
    lines += [
        "",
        breakdown,
        "",
        (
            f"<sub>Updated {human_date(today)} (UTC) from the GitHub GraphQL API. "
            "A streak is a run of days with at least one public contribution. "
            "The total above the graph can differ slightly from this table.</sub>"
        ),
    ]
    return "\n".join(lines)


def replace_section(readme: str, name: str, body: str) -> str:
    pattern = re.compile(
        rf"(<!-- generated:{name}:start -->\n)(?:.*?\n)?(<!-- generated:{name}:end -->)",
        re.DOTALL,
    )
    if not pattern.search(readme):
        raise SystemExit(f"README is missing the markers for section '{name}'")
    return pattern.sub(lambda match: match.group(1) + body + "\n" + match.group(2), readme)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--readme", default="README.md")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("Set GITHUB_TOKEN or GH_TOKEN.", file=sys.stderr)
        return 1

    gh = GitHub(token)
    now = dt.datetime.now(dt.UTC)
    with open(args.readme, encoding="utf-8") as handle:
        readme = handle.read()

    readme = replace_section(readme, "pubmaxx", render_pubmaxx(gh))
    readme = replace_section(readme, "contributions", render_contributions(gh))
    readme = replace_section(readme, "activity", render_activity(gh, now))

    with open(args.readme, "w", encoding="utf-8") as handle:
        handle.write(readme)
    return 0


if __name__ == "__main__":
    sys.exit(main())
