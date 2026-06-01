"""CFMIP experiment guidance pages."""

from __future__ import annotations

from local.branching import BranchFromParentAtAnyTime
from local.forcings import (
    HISTORICAL_FORCINGS_SPECIFICATION,
    PICONTROL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import (
    PI_CONTROL_LINK,
    ExperimentPage,
)
from local.mip_co_chair_review import get_pending_review_aft_experiments
from local.rendering import (
    join_blocks,
)

CFMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        id_esgvoc="amip-p4k",
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="amip-sst-sea-ice-boundary-forcing",
                    experiment_esgvoc_id="amip",
                    user_modifications="add 4K to sea-surface temperatures in ice-free regions",
                ),
            ),
        ),
        mip_co_chair_review=get_pending_review_aft_experiments("cfmip"),
    ),
    ExperimentPage(
        id_esgvoc="amip-piforcing",
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="amip-sst-sea-ice-boundary-forcing",
                    experiment_esgvoc_id="amip",
                ),
            ),
        ),
        mip_co_chair_review=get_pending_review_aft_experiments("cfmip"),
    ),
    ExperimentPage(
        id_esgvoc="abrupt-2xco2",
        branch_information=BranchFromParentAtAnyTime(),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug != "greenhouse-gas-concentrations"
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                        user_modifications="double the CO<sub>2</sub> concentrations",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug == "greenhouse-gas-concentrations"
                ),
            )
        ),
        experiment_setup_notes=join_blocks(
            f"The abrupt CO<sub>2</sub> doubling experiment is a simple branch from the {PI_CONTROL_LINK}. ",
            "After branching, the atmospheric CO<sub>2</sub> concentrations should "
            "be set to two times the CO<sub>2</sub> concentrations used in the piControl experiment.",
        ),
        mip_co_chair_review=get_pending_review_aft_experiments("cfmip"),
    ),
    ExperimentPage(
        id_esgvoc="abrupt-0p5xco2",
        branch_information=BranchFromParentAtAnyTime(),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug != "greenhouse-gas-concentrations"
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                        user_modifications="halve the CO<sub>2</sub> concentrations",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug == "greenhouse-gas-concentrations"
                ),
            )
        ),
        experiment_setup_notes=join_blocks(
            f"The abrupt CO<sub>2</sub> halving experiment is a simple branch from the {PI_CONTROL_LINK}. ",
            "After branching, the atmospheric CO<sub>2</sub> concentrations should "
            "be set to half the CO<sub>2</sub> concentrations used in the piControl experiment.",
        ),
        mip_co_chair_review=get_pending_review_aft_experiments("cfmip"),
    ),
)
