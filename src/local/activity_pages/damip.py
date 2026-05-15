"""DAMIP experiment guidance pages."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from local.forcing_references import COMMON_FORCING_NOTES
from local.forcing_versions import (
    HISTORICAL_FORCING_VERSIONS,
    PI_CONTROL_FORCING_VERSIONS,
    forcing_ids_except,
    merge_source_ids,
    scen7_forcing_versions_for_slug,
    select_forcing_versions,
    source_ids_from_forcing_versions,
)
from local.guidance import HISTORICAL_LINK, PI_CONTROL_LINK, ExperimentPage
from local.rendering import (
    join_blocks,
    join_lines,
    render_data_access_body,
    render_link,
)
from local.vocab import get_experiment

DAMIP_EXTENSION_SCENARIO_SLUG = "scen7-m"


@dataclass(frozen=True)
class HistoricalForcingPageSpec:
    """Inputs needed to create a DAMIP historical-forcing page."""

    slug: str
    historical_forcing_ids: tuple[str, ...]
    historical_forcing_label: str


def make_historical_forcing_page(spec: HistoricalForcingPageSpec) -> ExperimentPage:
    """Create a DAMIP page using selected historical forcings."""
    experiment_name = get_experiment(spec.slug).drs_name
    extension_scenario_link = damip_extension_scenario_link()

    return ExperimentPage(
        slug=spec.slug,
        experiment_setup=join_blocks(
            f"The `{experiment_name}` simulation is a branch from the {PI_CONTROL_LINK}.",
            (
                f"The {spec.historical_forcing_label} should evolve as in the "
                f"{HISTORICAL_LINK}."
            ),
            (
                f"For the extension beyond the historical simulation, the "
                f"{spec.historical_forcing_label} should follow the "
                f"{extension_scenario_link} scenario simulation."
            ),
            f"All other forcings should remain as in the {PI_CONTROL_LINK}.",
        ).strip(),
        forcing_headlines=join_lines(
            f"The `{experiment_name}` experiment combines historical",
            spec.historical_forcing_label,
            f"extended with the {extension_scenario_link} scenario,",
            "with piControl values for all other forcings.",
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=join_blocks(
            join_lines(
                f"For {spec.historical_forcing_label},",
                f"the relevant forcing is the same as for the {HISTORICAL_LINK},",
                f"then the {extension_scenario_link} scenario for the extension.",
            ),
            join_lines(
                "For all other forcings,",
                f"the forcing versions relevant for this simulation are the same as for the {PI_CONTROL_LINK}.",
            ),
        ).strip(),
        getting_the_data=render_data_access_body(
            experiment_name=experiment_name,
            source_ids=source_ids_for_historical_forcing_page(
                spec.historical_forcing_ids
            ),
        ),
    )


def damip_extension_scenario_name() -> str:
    """Return the display name of the scenario used for DAMIP extensions."""
    return get_experiment(DAMIP_EXTENSION_SCENARIO_SLUG).drs_name


def damip_extension_scenario_link() -> str:
    """Return a link to the scenario used for DAMIP extensions."""
    return render_link(
        f"`{damip_extension_scenario_name()}`",
        DAMIP_EXTENSION_SCENARIO_SLUG,
    )


def source_ids_for_historical_forcing_page(
    historical_forcing_ids: Sequence[str],
) -> tuple[str, ...]:
    """Derive source IDs for a DAMIP selected-historical-forcing page."""
    return merge_source_ids(
        source_ids_from_forcing_versions(
            select_forcing_versions(
                PI_CONTROL_FORCING_VERSIONS,
                forcing_ids_except(PI_CONTROL_FORCING_VERSIONS, *historical_forcing_ids),
            ),
        ),
        source_ids_from_forcing_versions(
            select_forcing_versions(
                HISTORICAL_FORCING_VERSIONS,
                historical_forcing_ids,
            ),
        ),
        source_ids_from_forcing_versions(
            select_forcing_versions(
                scen7_forcing_versions_for_slug(DAMIP_EXTENSION_SCENARIO_SLUG),
                historical_forcing_ids,
            ),
        ),
    )


DAMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    make_historical_forcing_page(
        HistoricalForcingPageSpec(
            slug="hist-aer",
            historical_forcing_ids=(
                "anthropogenic-emissions",
                "biomass-burning-emissions",
            ),
            historical_forcing_label=(
                "anthropogenic emissions and biomass-burning emissions"
            ),
        )
    ),
    make_historical_forcing_page(
        HistoricalForcingPageSpec(
            slug="hist-ghg",
            historical_forcing_ids=("greenhouse-gas-concentrations",),
            historical_forcing_label="greenhouse-gas concentrations",
        )
    ),
    make_historical_forcing_page(
        HistoricalForcingPageSpec(
            slug="hist-nat",
            historical_forcing_ids=(
                "solar",
                "stratospheric-aerosol-forcing",
            ),
            historical_forcing_label=(
                "natural forcings (solar and volcanic forcings)"
            ),
        )
    ),
)
