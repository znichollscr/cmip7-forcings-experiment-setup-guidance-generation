"""Experiment-description rendering helpers."""

from __future__ import annotations

from local.experiment_dates import historical_end_year
from local.vocab import PROJECT_ID

CMIP6_HISTORICAL_END_YEAR = 2014
CMIP6_PROJECT_LABEL = "CMIP6"


def present_day_values_explanation() -> str:
    """Return the exact esgvoc present-day-values explanation to replace."""
    project_label = PROJECT_ID.upper()
    return (
        "typically the last year of the `historical` simulation within the same "
        "CMIP era e.g. "
        f"{CMIP6_HISTORICAL_END_YEAR} values for {CMIP6_PROJECT_LABEL}, "
        f"{historical_end_year()} values for {project_label}"
    )


def present_day_values_replacement() -> str:
    """Return the replacement present-day-values explanation."""
    return f"{historical_end_year()} in {PROJECT_ID.upper()}"


def render_experiment_description(description: str) -> str:
    """Render an esgvoc experiment description with local wording adjustments."""
    return present_day_values_replacement().join(
        description.split(present_day_values_explanation())
    )
