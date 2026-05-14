"""Experiment-description rendering helpers."""

from __future__ import annotations

from local.experiment_dates import historical_end_year

PRESENT_DAY_VALUES_EXPLANATION = (
    "typically the last year of the `historical` simulation within the same "
    "CMIP era e.g. 2014 values for CMIP6, 2021 values for CMIP7"
)


def render_experiment_description(description: str) -> str:
    """Render an esgvoc experiment description with local wording adjustments."""
    return f"{historical_end_year()} in CMIP7".join(
        description.split(PRESENT_DAY_VALUES_EXPLANATION)
    )
