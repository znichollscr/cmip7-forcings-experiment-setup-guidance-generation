"""Shared building blocks for the abrupt CO2 scaling experiment guidance pages.

Several activities define `abrupt-*xCO2` experiments that branch from
`piControl` and instantly rescale the CO2 concentrations (CFMIP's `abrupt-2xCO2`
and `abrupt-0p5xCO2`, CMIP's `abrupt-4xCO2`). They share the same forcing layout
and setup-notes wording, so this module provides a single factory for that
pattern.
"""

from __future__ import annotations

from local.branching import BranchFromParentAtAnyTime
from local.forcings import (
    PICONTROL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import (
    PI_CONTROL_LINK,
    ExperimentPage,
    RenderableMIPCoChairReviewInformation,
)
from local.rendering import join_blocks

GREENHOUSE_GAS_CONCENTRATIONS_SLUG = "greenhouse-gas-concentrations"


def make_abrupt_co2_page(
    id_esgvoc: str,
    *,
    mip_co_chair_review: RenderableMIPCoChairReviewInformation,
    scaling_action: str,
    scaling_factor_phrase: str,
    co2_modification: str,
    greenhouse_gas_source_experiment_id: str = "picontrol",
) -> ExperimentPage:
    """
    Make an abrupt CO2 scaling page

    `scaling_action` is the noun used in the headline (e.g. `doubling`),
    `scaling_factor_phrase` describes the target concentration (e.g. `two
    times`), and `co2_modification` is the instruction applied to the greenhouse
    gas concentrations (e.g. `double the CO<sub>2</sub> concentrations`). All
    `piControl` forcings other than the greenhouse gas concentrations are used
    as-is; the greenhouse gas concentrations come from
    `greenhouse_gas_source_experiment_id` with `co2_modification` applied.
    """
    return ExperimentPage(
        id_esgvoc=id_esgvoc,
        branch_information=BranchFromParentAtAnyTime(),
        experiment_setup_notes=join_blocks(
            f"The abrupt CO<sub>2</sub> {scaling_action} experiment is a simple branch from the {PI_CONTROL_LINK}. ",
            "After branching, the atmospheric CO<sub>2</sub> concentrations should "
            f"be set to {scaling_factor_phrase} the CO<sub>2</sub> concentrations used in the piControl experiment.",
        ),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug != GREENHOUSE_GAS_CONCENTRATIONS_SLUG
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=GREENHOUSE_GAS_CONCENTRATIONS_SLUG,
                    experiment_esgvoc_id=greenhouse_gas_source_experiment_id,
                    user_modifications=co2_modification,
                ),
            )
        ),
        mip_co_chair_review=mip_co_chair_review,
    )
