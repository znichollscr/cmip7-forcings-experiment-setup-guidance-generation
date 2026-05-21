"""C4MIP experiment guidance pages."""

from __future__ import annotations

from local.branching import (
    BranchAtSameTimeAsOtherExperiment,
    BranchFromParentAtAnyTime,
    BranchFromParentAtGivenYearStart,
)
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
    ExperimentPage(
        id_esgvoc="esm-flat10",
        branch_information=BranchFromParentAtAnyTime(),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug not in ("anthropogenic-slcf-co2-emissions")
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                        user_modifications="set the total CO<sub>2</sub> emissions to 10 PgC / yr",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in ("anthropogenic-slcf-co2-emissions")
                ),
            )
        ),
    ),
    ExperimentPage(
        id_esgvoc="esm-flat10-cdr",
        branch_information=BranchFromParentAtGivenYearStart(branch_year=101),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug not in ("anthropogenic-slcf-co2-emissions")
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="esm-flat10",
                        user_modifications=(
                            "starting from the 10 PgC / yr total CO<sub>2</sub> emissions "
                            "used in esm-flat10, "
                            "decrease the total CO<sub>2</sub> emissions by 0.2 PgC / yr "
                            "until the end of year 200 (200-12-31) "
                            "then hold total CO<sub>2</sub> emissions constant at -10 PgC / yr for 100 years "
                            "until the end of year 300 (300-12-31). "
                            "For the last 20 years, set the total CO<sub>2</sub> emissions to 0.0 PgC / yr."
                        ),
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in ("anthropogenic-slcf-co2-emissions")
                ),
            )
        ),
    ),
    ExperimentPage(
        id_esgvoc="esm-flat10-zec",
        branch_information=BranchFromParentAtGivenYearStart(branch_year=101),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                ),
            )
        ),
    ),
)
