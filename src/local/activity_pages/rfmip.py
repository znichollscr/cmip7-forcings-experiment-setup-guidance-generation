"""RFMIP experiment guidance pages."""

from __future__ import annotations

from local.guidance import ExperimentPage
from local.piclim_variants import (
    HistoricalForcing,
    make_piclim_historical_forcing_variant_page,
)

RFMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    make_piclim_historical_forcing_variant_page(
        slug="piclim-aer",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="anthropogenic-emissions",
                label="anthropogenic aerosol emissions",
            ),
            HistoricalForcing(
                forcing_id="biomass-burning-emissions",
                label="biomass-burning aerosol emissions",
            ),
        ),
    ),
)
