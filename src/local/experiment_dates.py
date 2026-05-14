"""Experiment-date helpers derived from esgvoc."""

from __future__ import annotations

from local.rendering import date_from_timestamp
from local.vocab import get_experiment

HISTORICAL_EXPERIMENT_ID = "historical"


def historical_end_year() -> int:
    """Return the last year of the historical experiment."""
    historical_experiment = get_experiment(HISTORICAL_EXPERIMENT_ID)
    end_date = date_from_timestamp(
        getattr(historical_experiment, "end_timestamp", None)
    )
    if end_date is None:
        msg = (
            "Cannot determine the historical end year because the CMIP7 CVs do "
            "not define a supported end timestamp for 'historical'."
        )
        raise ValueError(msg)

    return end_date.year
