"""Shared building blocks for `piClim-*` experiment guidance pages.

Several activities (CMIP, AerChemMIP, RFMIP) define `piClim-*` experiments
that follow the same pattern: branch at the same time as `piClim-control`,
take the `piControl` forcings except for a few which instead come from
`historical` (fixed to the final historical year), and use the
`piClim-control` sea-surface temperature forcing. This module provides a
single factory for that pattern so the activities do not have to repeat it.
"""

from __future__ import annotations

from collections.abc import Callable

from local.branching import BranchAtSameTimeAsOtherExperiment
from local.forcings import (
    HISTORICAL_FORCINGS_SPECIFICATION,
    PICONTROL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import ExperimentPage, RenderableMIPCoChairReviewInformation
from local.output_time_axis import PiClimOutputTimeAxisInformation
from local.vocab import get_experiment

LAST_HISTORICAL_YEAR = get_experiment("historical").end_timestamp.year


def make_piclim_based_page(
    id_esgvoc: str,
    *,
    mip_co_chair_review: RenderableMIPCoChairReviewInformation,
    forcing_slugs_historical_last_year: tuple[str, ...],
    historical_last_year: int = LAST_HISTORICAL_YEAR,
    user_modifications: str | None = None,
    render_description: Callable[[str], str] = lambda x: x,
) -> ExperimentPage:
    """
    Make a piClim-* page

    The forcings identified by `forcing_slugs_historical_last_year` are taken
    from the `historical` experiment (fixed to `historical_last_year`),
    while all other `piControl` forcings are used as-is.
    """
    if user_modifications is None:
        user_modifications = f"apply the {historical_last_year} value on repeat"

    res = ExperimentPage(
        id_esgvoc=id_esgvoc,
        branch_information=BranchAtSameTimeAsOtherExperiment("piclim-control"),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug not in forcing_slugs_historical_last_year
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                        user_modifications=user_modifications,
                        fixed_override=True,
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in forcing_slugs_historical_last_year
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="sst-forcing",
                    experiment_esgvoc_id="piclim-control",
                ),
            ),
        ),
        output_time_axis_info=PiClimOutputTimeAxisInformation(),
        render_description=render_description,
        mip_co_chair_review=mip_co_chair_review,
    )

    return res
