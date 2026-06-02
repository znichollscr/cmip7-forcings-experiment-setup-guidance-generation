"""CFMIP experiment guidance pages."""

from __future__ import annotations

from local.abrupt_co2_variants import make_abrupt_co2_page
from local.forcings import (
    HISTORICAL_FORCINGS_SPECIFICATION,
    PICONTROL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import (
    ExperimentPage,
)
from local.mip_co_chair_review import get_pending_review_aft_experiments

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
    make_abrupt_co2_page(
        "abrupt-2xco2",
        mip_co_chair_review=get_pending_review_aft_experiments("cfmip"),
        scaling_action="doubling",
        scaling_factor_phrase="two times",
        co2_modification="double the CO<sub>2</sub> concentrations",
    ),
    make_abrupt_co2_page(
        "abrupt-0p5xco2",
        mip_co_chair_review=get_pending_review_aft_experiments("cfmip"),
        scaling_action="halving",
        scaling_factor_phrase="half",
        co2_modification="halve the CO<sub>2</sub> concentrations",
    ),
)
