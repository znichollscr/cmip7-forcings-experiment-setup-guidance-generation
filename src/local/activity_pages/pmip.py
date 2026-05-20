"""PMIP experiment guidance pages."""

from __future__ import annotations

from local.branching import BranchFromParentAtAnyTime
from local.forcings import (
    PICONTROL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import (
    ExperimentPage,
)
from local.output_time_axis import RecommendContinueFromBranchPointTimeAxisInformation
from local.rendering import block

PMIP_EXPERIMENT_PAGES = (
    ExperimentPage(
        id_esgvoc="abrupt-127k",
        branch_information=BranchFromParentAtAnyTime(),
        experiment_setup_notes=block(
            """
            The boundary conditions should be adjusted according to Table 1 of
            [Sime et al., 2025](https://egusphere.copernicus.org/preprints/2025/egusphere-2025-3531/).
            (Note that this paper is still under review, when it is published or there is an update,
            we will copy the table in here.)
            You have to make these adjustments yourself, there are no specific forcing files provided.
            """
        ),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug not in ("greenhouse-gas-concentrations", "solar")
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                        user_modifications=(
                            "adjusted according to Table 1 of "
                            "[Sime et al., 2025](https://egusphere.copernicus.org/preprints/2025/egusphere-2025-3531/)"
                        ),
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in ("greenhouse-gas-concentrations", "solar")
                ),
            )
        ),
        output_time_axis_info=RecommendContinueFromBranchPointTimeAxisInformation(),
    ),
)
