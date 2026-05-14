"""Generic CV-derived experiment guidance pages."""

from __future__ import annotations

from local.guidance import ExperimentPage
from local.rendering import block

GENERIC_PAGE_NOTE = block(
    """
    !!! warning "Baseline generated page"

        This page is generated from the CMIP7 CVs because detailed guidance has not yet been added for this experiment.
        The responsible activity, description, timing, ensemble size and parent-experiment information are taken from
        the active CMIP7 CVs.
    """
)

GENERIC_EXPERIMENT_SETUP = block(
    """
    Detailed experiment setup guidance has not yet been added to the generator for this experiment.
    Please use the CMIP7 CV information on this page together with the responsible activity references above.
    """
)

GENERIC_FORCING_HEADLINES = block(
    """
    Detailed forcing guidance has not yet been added to the generator for this experiment.
    """
)

GENERIC_FORCING_NOTES = block(
    """
    No additional forcing notes have been written for this experiment yet.
    """
)

GENERIC_VERSIONS_TO_USE = block(
    """
    Specific input4MIPs source IDs for this experiment have not yet been encoded in the generator.
    """
)

GENERIC_GETTING_THE_DATA = block(
    """
    No data-retrieval script is generated for this experiment yet because the forcing versions have not been encoded in
    the generator.
    """
)


def make_generic_experiment_page(slug: str) -> ExperimentPage:
    """Create a baseline generated experiment page from esgvoc metadata."""
    return ExperimentPage(
        slug=slug,
        pre_description_note=GENERIC_PAGE_NOTE,
        experiment_setup=GENERIC_EXPERIMENT_SETUP,
        forcing_headlines=GENERIC_FORCING_HEADLINES,
        notes=GENERIC_FORCING_NOTES,
        versions_to_use=GENERIC_VERSIONS_TO_USE,
        getting_the_data=GENERIC_GETTING_THE_DATA,
    )
