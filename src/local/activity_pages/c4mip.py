"""C4MIP experiment guidance pages."""

from __future__ import annotations

from local.branching import BranchAtSameTimeAsOtherExperiment
from local.forcings import (
    PICONTROL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import (
    ONEPCTCO2_LINK,
    ExperimentPage,
)
from local.output_time_axis import RecommendSameAsOtherExperimentTimeAxisInformation
from local.rendering import (
    block,
    join_blocks,
)

# TODO: reduce duplication with 1pctco2
C4MIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        id_esgvoc="1pctco2-bgc",
        branch_information=BranchAtSameTimeAsOtherExperiment("1pctco2"),
        experiment_setup_notes=join_blocks(
            f"The 1pctCO2-bgc simulation has the same forcing setup as the {ONEPCTCO2_LINK}.",
            block(
                """
                The difference is that your model should be configured such that the carbon cycle
                only sees the change in atmospheric CO<sub>2</sub> concentrations
                and does not see any other changes (e.g. changes in atmospheric temperatures).
                """
            ),
        ),
        fixed_or_transient_or_mix_forcing_override=(
            "The 1pctCO2-bgc experiment is a fixed forcings experiment, "
            "except for CO<sub>2</sub> which is transient."
        ),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=tuple(
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=v.forcing_slug,
                    experiment_esgvoc_id="1pctco2",
                )
                for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
            )
        ),
        output_time_axis_info=RecommendSameAsOtherExperimentTimeAxisInformation(
            "1pctco2"
        ),
    ),
    ExperimentPage(
        id_esgvoc="1pctco2-rad",
        branch_information=BranchAtSameTimeAsOtherExperiment("1pctco2"),
        experiment_setup_notes=join_blocks(
            f"The 1pctCO2-bgc simulation has the same forcing setup as the {ONEPCTCO2_LINK}.",
            block(
                """
                The difference is that your model should be configured such that the carbon cycle
                only sees the change in radiation
                and does not see any other changes (e.g. changes in atmospheric CO<sub>2</sub> concentrations).
                """
            ),
        ),
        fixed_or_transient_or_mix_forcing_override=(
            "The 1pctCO2-bgc experiment is a fixed forcings experiment, "
            "except for CO<sub>2</sub> which is transient."
        ),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=tuple(
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=v.forcing_slug,
                    experiment_esgvoc_id="1pctco2",
                )
                for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
            )
        ),
        output_time_axis_info=RecommendSameAsOtherExperimentTimeAxisInformation(
            "1pctco2"
        ),
    ),
)
