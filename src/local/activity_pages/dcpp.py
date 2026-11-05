"""DCPP experiment guidance pages."""

from __future__ import annotations

from local.forcings import ForcingsInformationNotProvided
from local.guidance import ExperimentPage
from local.mip_co_chair_review import CompleteReview
from local.rendering import block
from local.tags import AFT

DCPP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        id_esgvoc="dcppb-forecast-cmip6",
        experiment_setup_notes=block(
            """
            This is a CMIP6-era experiment that uses CMIP6-era forcings.
            For detailed guidance about the experiment setup, please see the
            [DCPP guidance pages](https://www.wcrp-esmo.org/projects-and-panels/dcpp/dcpp-resources)
            (look at the "DCPP contribution to CMIP7 AFT" header).
            For guidance on how to set the `variant_label` of your output, please the
            [dedicated guidance](../Global_Attributes.md#5-notes-on-variant_label).
            """
        ),
        forcings=ForcingsInformationNotProvided(),
        mip_co_chair_review=CompleteReview(
            "https://github.com/WCRP-CMIP/cmip7-guidance/issues/207"
        ),
        tags=(AFT,),
    ),
)
