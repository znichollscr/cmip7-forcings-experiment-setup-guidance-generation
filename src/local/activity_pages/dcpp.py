"""DCPP experiment guidance pages."""

from __future__ import annotations

from local.guidance import ExperimentPage
from local.rendering import block

DCPP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        id_esgvoc="dcppb-forecast-cmip6",
        experiment_setup_notes=block(
            """
            This is a CMIP6-era experiment that uses CMIP6-era forcings.
            No guidance is provided here about forcing versions or similar.
            It is assumed that you already know what you're doing.
            """
        ),
        forcings=None,  # CMIP6 era forcings
        # forcings=ForcingSpecification(
        #     other_experiment_based_forcings=tuple(
        #         OtherExperimentBasedForcingSpecification(
        #             forcing_slug=v.forcing_slug,
        #             experiment_esgvoc_id="ssp245",
        #         )
        #         for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
        #     ),
        # ),
    ),
)
