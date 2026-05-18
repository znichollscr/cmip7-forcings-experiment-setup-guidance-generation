"""Branching text helpers for experiment guidance pages."""

from __future__ import annotations

import datetime as dt
from collections.abc import Collection
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from local.rendering import (
    join_blocks,
    render_activity_index_link,
    render_link,
    render_term_reference,
)
from local.vocab import get_activity, get_experiment

if TYPE_CHECKING:
    from local.guidance import ExperimentPage


class MissingParentExperimentPageError(ValueError):
    """Raised when a parent experiment has no generated guidance page."""


class UnexpectedPiClimControlBranchParentError(ValueError):
    """Raised when a piClim-control branch reference has the wrong parent."""


PICLIM_CONTROL_BRANCH_INFORMATION = "Same as `piClim-control`"
PICLIM_CONTROL_PARENT_EXPERIMENT_ID = "picontrol"


@dataclass(frozen=True)
class BranchFromParentAtAnyTime:
    """
    Branching from the parent experiment at any time
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the branch information as a string"""
        parent_experiment_esgvoc = experiment.parent_experiment_esgvoc
        if parent_experiment_esgvoc is None:
            msg = f"No parent experiment for {experiment.id_esgvoc}"
            raise AssertionError(msg)

        parent_experiment_link = render_link(
            parent_experiment_esgvoc.drs_name, parent_experiment_esgvoc.id
        )

        res = f"Branch from {parent_experiment_link} at a time of your choosing."

        return res


@dataclass(frozen=True)
class BranchFromParentAtTime:
    """
    Branching from the parent experiment at a specific time
    """

    branch_time: dt.datetime
    """
    Branch time
    """

    def render(self, experiment: ExperimentPage) -> str:
        """Render the branch information as a string"""
        parent_experiment_esgvoc = experiment.parent_experiment_esgvoc
        if parent_experiment_esgvoc is None:
            msg = f"No parent experiment for {experiment.id_esgvoc}"
            raise AssertionError(msg)

        parent_experiment_link = render_link(
            parent_experiment_esgvoc.drs_name, parent_experiment_esgvoc.id
        )

        formatted_time = self.branch_time.date().isoformat()
        res = f"Branch from {parent_experiment_link} at {formatted_time}."

        return res


def render_parent_information(
    experiment: Any,
    *,
    page_slugs: Collection[str],
    extra: str = "",
) -> str:
    """Render parent-experiment information from an esgvoc experiment term."""
    parent_experiment = _as_experiment(getattr(experiment, "parent_experiment", None))
    parent_activity = _as_activity(getattr(experiment, "parent_activity", None))
    parent_mip_era = getattr(experiment, "parent_mip_era", None)

    if parent_experiment is None:
        parent_summary = (
            f"`{experiment.drs_name}` has no parent experiment in the CMIP7 CVs."
        )
    else:
        parent_experiment_link = _render_parent_experiment_link(
            experiment=experiment,
            parent_experiment=parent_experiment,
            page_slugs=page_slugs,
        )
        parent_activity_suffix = ""
        if parent_activity is not None:
            parent_activity_suffix = (
                f" (part of {_render_parent_activity_link(parent_activity)})"
            )

        parent_summary = (
            f"`{experiment.drs_name}` branches from the "
            f"{parent_experiment_link} simulation{parent_activity_suffix}."
        )

    return join_blocks(
        parent_summary,
        _render_branch_information(
            experiment=experiment,
            parent_experiment=parent_experiment,
        ),
        (
            _render_parent_mip_era(parent_mip_era)
            if parent_experiment is not None
            else ""
        ),
        extra,
    ).strip()


def render_parent_and_branching_information(experiment: ExperimentPage) -> str:
    """Render parent-experiment information"""
    parent_experiment_esgvoc = experiment.experiment_esgvoc.parent_experiment
    if parent_experiment_esgvoc is None:
        msg = (
            f"{experiment.experiment_esgvoc.drs_name} doesn't have a parent experiment"
        )
        raise AssertionError(msg)

    if isinstance(parent_experiment_esgvoc, str):
        parent_experiment_esgvoc = get_experiment(parent_experiment_esgvoc)

    parent_activity_esgvoc = experiment.experiment_esgvoc.parent_activity
    if parent_activity_esgvoc is None:
        msg = f"{experiment.experiment_esgvoc.drs_name} doesn't have a parent activity"
        raise AssertionError(msg)

    if isinstance(parent_activity_esgvoc, str):
        parent_activity_esgvoc = get_activity(parent_activity_esgvoc)

    parent_mip_era = experiment.experiment_esgvoc.parent_mip_era
    if parent_mip_era is None:
        msg = f"{experiment.experiment_esgvoc.drs_name} doesn't have a parent mip_era"
        raise AssertionError(msg)

    if isinstance(parent_mip_era, str):
        raise TypeError(f"{type(parent_mip_era)=}")

    # TODO: push check that parent page exists into higher-up layers
    parent_experiment_link = render_link(
        parent_experiment_esgvoc.drs_name, parent_experiment_esgvoc.id
    )
    parent_activity_link = render_activity_index_link(parent_activity_esgvoc)

    parent_information = (
        f"The `{experiment.drs_name}` experiment branches from the "
        f"{parent_experiment_link} experiment (part of {parent_activity_link}). "
        "The parent experiment's MIP era is "
        f"{render_term_reference(parent_mip_era.drs_name, (parent_mip_era.url,))}."
    )

    branch_information = experiment.render_branch_information()

    # Options for branching information:
    # 1. branch at time of choosing
    # 1. branch at time of choosing, but ideally line up with other experiment
    # 1. branch at time of choosing, suggest [this approach]
    # 1. branch at end of parent experiment
    # 1. branch at end of parent experiment plus one day
    # 1. branch at specific time in parent experiment
    # 1. no parent experiment therefore no branching
    # 1. fully custom override

    res = join_blocks(
        parent_information,
        branch_information,
    )

    return res


def _render_parent_experiment_link(
    *,
    experiment: Any,
    parent_experiment: Any,
    page_slugs: Collection[str],
) -> str:
    """Render a link to the parent experiment page, failing if it is missing."""
    parent_slug = parent_experiment.id
    if parent_slug not in page_slugs:
        msg = (
            f"Experiment {experiment.id!r} branches from parent experiment "
            f"{parent_slug!r}, but no generated page with slug {parent_slug!r} "
            "exists."
        )
        raise MissingParentExperimentPageError(msg)

    return render_link(parent_experiment.drs_name, parent_slug)


def _render_branch_information(
    *,
    experiment: Any,
    parent_experiment: Any | None,
) -> str:
    """Render branch information from an esgvoc experiment term."""
    branch_information = getattr(experiment, "branch_information", None)
    if branch_information == PICLIM_CONTROL_BRANCH_INFORMATION:
        _check_piclim_control_parent(experiment, parent_experiment)
        return (
            f"Branch from {parent_experiment.drs_name} at the same time as "
            "piClim-control."
        )

    return _sentence(branch_information)


def _check_piclim_control_parent(
    experiment: Any,
    parent_experiment: Any | None,
) -> None:
    """Validate parent experiment for piClim-control branch references."""
    parent_experiment_id = getattr(parent_experiment, "id", None)
    if parent_experiment_id == PICLIM_CONTROL_PARENT_EXPERIMENT_ID:
        return

    msg = (
        f"Experiment {experiment.id!r} has branch information "
        f"{PICLIM_CONTROL_BRANCH_INFORMATION!r}, but its parent experiment is "
        f"{parent_experiment_id!r} rather than "
        f"{PICLIM_CONTROL_PARENT_EXPERIMENT_ID!r}."
    )
    raise UnexpectedPiClimControlBranchParentError(msg)


def _render_parent_activity_link(parent_activity: Any) -> str:
    """Render a link to the parent activity section on the index page."""
    return render_activity_index_link(parent_activity)


def _as_activity(activity: Any) -> Any | None:
    """Return an activity term from either an activity term or id."""
    if activity is None:
        return None

    if isinstance(activity, str):
        return get_activity(activity)

    return activity


def _as_experiment(experiment: Any) -> Any | None:
    """Return an experiment term from either an experiment term or id."""
    if experiment is None:
        return None

    if isinstance(experiment, str):
        return get_experiment(experiment)

    return experiment


def _render_parent_mip_era(parent_mip_era: Any) -> str:
    """Render parent MIP era information from an esgvoc term."""
    if parent_mip_era is None:
        return ""

    urls = ()
    url = getattr(parent_mip_era, "url", None)
    if url is not None:
        urls = (str(url),)

    return (
        "The parent experiment comes from "
        f"{render_term_reference(parent_mip_era.drs_name, urls)}."
    )


def _sentence(text: str | None) -> str:
    """Return text with sentence-ending punctuation."""
    if not text:
        return ""

    stripped = text.strip()
    if stripped.endswith((".", "!", "?")):
        return stripped

    return f"{stripped}."
