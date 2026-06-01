"""LMIP experiment guidance pages."""

from __future__ import annotations

from local.forcings import (
    HISTORICAL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    NonInput4MIPsBasedForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import ExperimentPage
from local.mip_co_chair_review import get_pending_review_aft_experiments
from local.rendering import block

LMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        id_esgvoc="land-hist",
        experiment_setup_notes=block(
            """
            Spinup of the land-only simulations should follow the TRENDY protocol
            ([van den Hurk et al (2016)](https://gmd.copernicus.org/articles/9/2809/2016/)).
            """
        ),
        forcings=ForcingSpecification(
            specific_forcings=(
                NonInput4MIPsBasedForcingSpecification(
                    "land-model-climate-weather-inputs",
                    fixed=False,
                    notes=(
                        "The default forcing data is from a corrected reanalysis product "
                        "that includes all the climate/weather inputs to drive a land model. "
                        "The dataset is typically referred to as CRUJRA. "
                        "CRUJRA Climate forcing data are provided by Ian Harris at UEA 1901-2024 "
                        "and available from the following website: "
                        "[crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.09](). "
                        "A 2nd historical forcing dataset is in development and would ideally also be run. "
                    ),
                    label_override="Land model climate and weather inputs",
                ),
            ),
            other_experiment_based_forcings=tuple(
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=v.forcing_slug,
                    experiment_esgvoc_id="historical",
                )
                for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
            ),
        ),
        mip_co_chair_review=get_pending_review_aft_experiments("lmip"),
    ),
)
