#!/usr/bin/env python3
"""Create GitHub issues asking MIP co-chairs to review the guidance pages.

For every activity in the generated experiments, this creates one issue on the
``cmip7-guidance`` repository inviting that activity's co-chairs to review their
experiment pages, then immediately adds a follow-up comment tagging the CMIP IPO.

The ``--dry-run`` option prints the issue titles, bodies and comments that would
be created rather than touching GitHub.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Annotated

import typer

from local.experiment_pairs import sort_experiment_slugs
from local.guidance import INDEX_GROUPS
from local.vocab import get_activity, get_experiment

# The guidance lives in the WCRP-CMIP/cmip7-guidance repository, so that is
# where the review issues need to be raised.
GUIDANCE_REPO = "WCRP-CMIP/cmip7-guidance"

# Base URL for the published experiment pages. The final path segment is the
# experiment *id* (the page slug), not its display name, matching the links
# generated between experiment pages.
EXPERIMENT_PAGE_BASE_URL = (
    "https://wcrp-cmip.github.io/cmip7-guidance/docs/CMIP7/"
    "Experiment_set_up_and_Forcings"
)

IPO_COMMENT = (
    "@cmip-ipo can you please contact the relevant MIP co-chairs "
    "to help get engagement here, thanks"
)


@dataclass(frozen=True)
class IssuePlan:
    """An issue (plus follow-up comment) to be created for one activity."""

    activity_id: str
    title: str
    body: str
    comment: str


def experiment_page_url(experiment_id: str) -> str:
    """Return the published page URL for an experiment id.

    The URL is built from the experiment *id* (page slug), not its display
    name, so that it matches the cross-links between experiment pages.
    """
    return f"{EXPERIMENT_PAGE_BASE_URL}/{experiment_id}/"


def render_experiment_links(experiment_ids: tuple[str, ...]) -> str:
    """Render the numbered list of experiment page links."""
    lines = []
    for experiment_id in sort_experiment_slugs(experiment_ids):
        display_name = get_experiment(experiment_id).drs_name
        url = experiment_page_url(experiment_id)
        lines.append(f"1. [{display_name}]({url})")

    return "\n".join(lines)


def build_issue_body(activity_name: str, experiment_ids: tuple[str, ...]) -> str:
    """Build the issue body for one activity."""
    return "\n".join(
        (
            f"Hi {activity_name} co-chairs,",
            "",
            "We have created entries for all of your AFT experiments. "
            "We would now like you to review these to check for any errors. "
            "For the AFT, your experiment pages are:",
            "",
            render_experiment_links(experiment_ids),
            "",
            "If you spot any errors, please simply comment here or open up a "
            "pull request with the fixes you would like and tag @znichollscr.",
            "We will then try and get these fixed asap.",
        )
    )


def build_issue_plans() -> tuple[IssuePlan, ...]:
    """Build an issue plan for every activity across the index groups."""
    plans: list[IssuePlan] = []
    for group in INDEX_GROUPS:
        for activity in group.activities:
            activity_name = get_activity(activity.activity_id).drs_name
            plans.append(
                IssuePlan(
                    activity_id=activity.activity_id,
                    title=(
                        f"{activity_name} MIP co-chair review of "
                        "experiment setup and forcings guidance"
                    ),
                    body=build_issue_body(activity_name, activity.experiment_slugs),
                    comment=IPO_COMMENT,
                )
            )

    return tuple(plans)


def print_dry_run(plans: tuple[IssuePlan, ...]) -> None:
    """Print the issues and comments that would be created."""
    for plan in plans:
        typer.echo("=" * 80)
        typer.echo(f"Activity: {plan.activity_id}")
        typer.echo(f"Title: {plan.title}")
        typer.echo("")
        typer.echo("Body:")
        typer.echo(plan.body)
        typer.echo("")
        typer.echo("Comment:")
        typer.echo(plan.comment)
        typer.echo("")


def resolve_gh() -> str:
    """Return the full path to the ``gh`` executable."""
    gh = shutil.which("gh")
    if gh is None:
        msg = "Could not find the 'gh' CLI on PATH. Install it from https://cli.github.com/."
        raise typer.BadParameter(msg)

    return gh


def create_issue(plan: IssuePlan, *, gh: str, repo: str) -> str:
    """Create the issue on GitHub and return its URL."""
    result = subprocess.run(  # noqa: S603  # fixed argument list, gh resolved from PATH
        [
            gh,
            "issue",
            "create",
            "--repo",
            repo,
            "--title",
            plan.title,
            "--body",
            plan.body,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip().splitlines()[-1]


def comment_on_issue(issue_url: str, comment: str, *, gh: str, repo: str) -> None:
    """Add a comment to an existing issue."""
    subprocess.run(  # noqa: S603  # fixed argument list, gh resolved from PATH
        [
            gh,
            "issue",
            "comment",
            issue_url,
            "--repo",
            repo,
            "--body",
            comment,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def main(
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help=(
                "Print the issue titles, bodies and comments that would be "
                "created rather than creating them on GitHub."
            ),
        ),
    ] = False,
    repo: Annotated[
        str,
        typer.Option(
            "--repo",
            help="GitHub repository (owner/name) to create the issues in.",
        ),
    ] = GUIDANCE_REPO,
) -> None:
    """Create MIP co-chair review issues for every generated activity."""
    plans = build_issue_plans()

    if dry_run:
        print_dry_run(plans)
        typer.echo(f"Dry run: {len(plans)} issues would be created in {repo}.")
        return

    gh = resolve_gh()
    for plan in plans:
        issue_url = create_issue(plan, gh=gh, repo=repo)
        typer.echo(f"Created issue for {plan.activity_id}: {issue_url}")
        comment_on_issue(issue_url, plan.comment, gh=gh, repo=repo)
        typer.echo(f"  Commented on {issue_url}")

    typer.echo(f"Created {len(plans)} issues in {repo}.")


if __name__ == "__main__":
    typer.run(main)
