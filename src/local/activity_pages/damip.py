"""DAMIP experiment guidance pages."""

from __future__ import annotations

from dataclasses import dataclass

from local.branching import BranchAtSameTimeAsOtherExperiment
from local.forcings import (
    HISTORICAL_FORCINGS_SPECIFICATION,
    PICONTROL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import (
    ExperimentPage,
)

# TODO: split out a `render_link_for_experiment` function


@dataclass(frozen=True)
class HistoricalForcingPageSpec:
    """Inputs needed to create a DAMIP historical-forcing page."""

    id_esgvoc: str
    historical_forcing_ids: tuple[str, ...]


def make_historical_forcing_page(spec: HistoricalForcingPageSpec) -> ExperimentPage:
    """Create a DAMIP page using selected historical forcings."""
    # experiment_name = get_experiment(spec.id_esgvoc).drs_name

    return ExperimentPage(
        id_esgvoc=spec.id_esgvoc,
        branch_information=BranchAtSameTimeAsOtherExperiment("historical"),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in spec.historical_forcing_ids
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="scen7-m",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in spec.historical_forcing_ids
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug not in spec.historical_forcing_ids
                ),
            ),
        ),
    )


DAMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    make_historical_forcing_page(
        HistoricalForcingPageSpec(
            id_esgvoc="hist-aer",
            historical_forcing_ids=(
                "anthropogenic-slcf-co2-emissions",
                "open-biomass-burning-emissions",
            ),
        )
    ),
    make_historical_forcing_page(
        HistoricalForcingPageSpec(
            id_esgvoc="hist-ghg",
            historical_forcing_ids=("greenhouse-gas-concentrations",),
        )
    ),
    make_historical_forcing_page(
        HistoricalForcingPageSpec(
            id_esgvoc="hist-nat",
            historical_forcing_ids=(
                "solar",
                "stratospheric-volcanic-so2-emissions-aod",
            ),
        )
    ),
)
