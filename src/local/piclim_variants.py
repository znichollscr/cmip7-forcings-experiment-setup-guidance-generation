"""Helpers for piClim variants that use historical forcing values."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from local.forcing_versions import (
    cmip_forcing_ids_except,
    source_ids_for_cmip_forcing_combination,
)
from local.guidance import (
    HISTORICAL_LINK,
    PI_CLIM_CONTROL_LINK,
    PICLIM_TIME_AXIS,
    ExperimentPage,
)
from local.rendering import (
    join_blocks,
    join_lines,
    render_data_access_body,
)
from local.vocab import get_experiment


@dataclass(frozen=True)
class HistoricalForcing:
    """A forcing that should use historical-experiment values."""

    forcing_id: str
    label: str


def make_piclim_historical_forcing_variant_page(
    *,
    slug: str,
    historical_forcings: Sequence[HistoricalForcing],
    extra_setup: str = "",
    extra_getting_the_data: str = "",
) -> ExperimentPage:
    """Create a piClim variant whose specified forcings come from historical."""
    if not historical_forcings:
        msg = "At least one historical forcing must be specified."
        raise ValueError(msg)

    return ExperimentPage(
        slug=slug,
        experiment_setup=join_blocks(
            (
                "This simulation uses the same forcings as "
                "[piClim-control](./piclim-control.md), except for the "
                f"{pluralize('forcing', historical_forcings)} listed below."
            ),
            render_historical_forcing_setup(historical_forcings),
            "The 2021 values should be prescribed on repeat throughout the simulation.",
            extra_setup,
            PICLIM_TIME_AXIS,
        ).strip(),
        forcing_headlines=(
            "See general headlines for the "
            "[`piClim-control` simulation](./piclim-control.md)."
        ),
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK}.",
        versions_to_use=render_historical_forcing_versions(historical_forcings),
        getting_the_data=render_data_access_body(
            experiment_name=get_experiment(slug).drs_name,
            source_ids=source_ids_for_piclim_historical_forcing_variant(
                historical_forcings,
            ),
            extra=extra_getting_the_data,
        ),
    )


def render_historical_forcing_setup(
    historical_forcings: Sequence[HistoricalForcing],
) -> str:
    """Render setup text for piClim historical forcing overrides."""
    return join_blocks(
        (
            f"The following {pluralize('forcing', historical_forcings)} should "
            f"use 2021 values from the {HISTORICAL_LINK}:"
        ),
        render_historical_forcing_list(historical_forcings),
    ).strip()


def render_historical_forcing_versions(
    historical_forcings: Sequence[HistoricalForcing],
) -> str:
    """Render version guidance for piClim historical forcing overrides."""
    return join_blocks(
        (
            f"For the {pluralize('forcing', historical_forcings)} listed below, "
            f"the forcing version relevant for this simulation is the same as "
            f"for the {HISTORICAL_LINK}:"
        ),
        render_historical_forcing_list(historical_forcings),
        join_lines(
            "For all other forcings,",
            (
                "the forcing versions relevant for this simulation are the "
                f"same as for the {PI_CLIM_CONTROL_LINK}."
            ),
        ),
    ).strip()


def render_historical_forcing_list(
    historical_forcings: Sequence[HistoricalForcing],
) -> str:
    """Render historical forcing labels as a markdown list."""
    return "\n".join(f"- {forcing.label}" for forcing in historical_forcings)


def source_ids_for_piclim_historical_forcing_variant(
    historical_forcings: Sequence[HistoricalForcing],
) -> tuple[str, ...]:
    """Return source IDs for a piClim historical-forcing variant."""
    historical_forcing_ids = tuple(
        forcing.forcing_id for forcing in historical_forcings
    )
    return source_ids_for_cmip_forcing_combination(
        fixed_forcing_ids=cmip_forcing_ids_except(
            *historical_forcing_ids,
            "aerosol-optical-properties",
        ),
        transient_forcing_ids=historical_forcing_ids,
    )


def pluralize(word: str, values: Sequence[object]) -> str:
    """Pluralize a regular noun based on the number of values."""
    if len(values) == 1:
        return word

    return f"{word}s"
