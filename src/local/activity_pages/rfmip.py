"""RFMIP experiment guidance pages."""

from __future__ import annotations

from local.branching import BranchAtSameTimeAsOtherExperiment
from local.forcings import (
    HISTORICAL_FORCINGS_SPECIFICATION,
    PICONTROL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import (
    HISTORICAL_LINK,
    ExperimentPage,
)
from local.mip_co_chair_review import get_pending_review_aft_experiments
from local.output_time_axis import PiClimOutputTimeAxisInformation
from local.rendering import (
    block,
    only_keep_first_sentence,
    render_link,
)
from local.vocab import get_experiment

from .cmip import LAST_HISTORICAL_YEAR

# TODO: split out a `render_link_for_experiment` function
SCEN7_M = get_experiment("scen7-m")
SCEN7_M_LINK = render_link(SCEN7_M.drs_name, SCEN7_M.id)

PICLIM_CONTROL = get_experiment("piclim-control")
PICLIM_CONTROL_LINK = render_link(PICLIM_CONTROL.drs_name, PICLIM_CONTROL.id)


RFMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        id_esgvoc="piclim-aer",
        branch_information=BranchAtSameTimeAsOtherExperiment("piclim-control"),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug
                    not in (
                        "anthropogenic-slcf-co2-emissions",
                        "open-biomass-burning-emissions",
                    )
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                        user_modifications=f"apply the {LAST_HISTORICAL_YEAR} value on repeat",
                        fixed_override=True,
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug
                    in (
                        "anthropogenic-slcf-co2-emissions",
                        "open-biomass-burning-emissions",
                    )
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="sst-forcing",
                    experiment_esgvoc_id="piclim-control",
                ),
            ),
        ),
        output_time_axis_info=PiClimOutputTimeAxisInformation(),
        render_description=only_keep_first_sentence,
        mip_co_chair_review=get_pending_review_aft_experiments("rfmip"),
    ),
    ExperimentPage(
        id_esgvoc="piclim-histaer",
        branch_information=BranchAtSameTimeAsOtherExperiment("piclim-control"),
        experiment_setup_notes=block(
            f"""
            piClim-histaer is the same setup as {PICLIM_CONTROL_LINK},
            except aerosol emissions follow the {HISTORICAL_LINK} experiment
            then the {SCEN7_M_LINK} experiment.
            """
        ),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug
                    in (
                        "anthropogenic-slcf-co2-emissions",
                        "open-biomass-burning-emissions",
                    )
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="scen7-m",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug
                    in (
                        "anthropogenic-slcf-co2-emissions",
                        "open-biomass-burning-emissions",
                    )
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug
                    not in (
                        "anthropogenic-slcf-co2-emissions",
                        "open-biomass-burning-emissions",
                    )
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="sst-forcing",
                    experiment_esgvoc_id="piclim-control",
                ),
            ),
        ),
        mip_co_chair_review=get_pending_review_aft_experiments("rfmip"),
    ),
    ExperimentPage(
        id_esgvoc="piclim-histall",
        branch_information=BranchAtSameTimeAsOtherExperiment("piclim-control"),
        experiment_setup_notes=block(
            f"""
            piClim-histaer is the same setup as {PICLIM_CONTROL_LINK},
            except all forcings follow the {HISTORICAL_LINK} experiment
            then the {SCEN7_M_LINK} experiment.
            """
        ),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="scen7-m",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="sst-forcing",
                    experiment_esgvoc_id="piclim-control",
                ),
            ),
        ),
        mip_co_chair_review=get_pending_review_aft_experiments("rfmip"),
    ),
)
