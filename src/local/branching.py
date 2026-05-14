"""Branching text helpers for experiment guidance pages."""

from __future__ import annotations

from collections.abc import Collection
from typing import Any

from local.rendering import join_blocks, render_link, render_term_reference
from local.vocab import get_activity, get_experiment


class MissingParentExperimentPageError(ValueError):
    """Raised when a parent experiment has no generated guidance page."""


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
            parent_activity_suffix = f" (part of {parent_activity.drs_name})"

        parent_summary = (
            f"`{experiment.drs_name}` branches from the "
            f"{parent_experiment_link} simulation{parent_activity_suffix}."
        )

    return join_blocks(
        parent_summary,
        _sentence(getattr(experiment, "branch_information", None)),
        _render_parent_mip_era(parent_mip_era),
        extra,
    ).strip()


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

    return f"Parent MIP era: {render_term_reference(parent_mip_era.drs_name, urls)}."


def _sentence(text: str | None) -> str:
    """Return text with sentence-ending punctuation."""
    if not text:
        return ""

    stripped = text.strip()
    if stripped.endswith((".", "!", "?")):
        return stripped

    return f"{stripped}."
