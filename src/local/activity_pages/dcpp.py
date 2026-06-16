"""DCPP experiment guidance pages."""

from __future__ import annotations

from local.guidance import ExperimentPage
from local.mip_co_chair_review import get_pending_review_aft_experiments
from local.rendering import block

DCPP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        id_esgvoc="dcppb-forecast-cmip6",
        experiment_setup_notes=block(
            """
            This is a CMIP6-era experiment that uses CMIP6-era forcings.
            For detailed guidance about the experiment setup,
            please see the [DCPP guidance pages](https://www.wcrp-esmo.org/projects-and-panels/dcpp/dcpp-resources)
            (look at the "DCPP contribution to CMIP7 AFT" header).
            For guidance on how to set the `variant_label` of your output,
            please the [dedicated guidance](../Global_Attributes.md#5-notes-on-variant_label).
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
        mip_co_chair_review=get_pending_review_aft_experiments("dcpp"),
    ),
)
