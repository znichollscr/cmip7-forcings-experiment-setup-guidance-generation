"""Forcing reference page definitions."""

from __future__ import annotations

from dataclasses import dataclass

from local.rendering import render_forcing_reference_list


@dataclass(frozen=True)
class ForcingReference:
    """A reference page for a forcing dataset family."""

    label: str
    overview_slug: str

    @property
    def url(self) -> str:
        """The URL for the forcing dataset overview page."""
        return (
            "https://input4mips-cvs.readthedocs.io/en/latest/"
            f"dataset-overviews/{self.overview_slug}/"
        )

    @property
    def display_url(self) -> str:
        """The compact URL displayed in the rendered markdown."""
        return (
            "input4mips-cvs.readthedocs.io/dataset-overviews/" f"{self.overview_slug}"
        )


COMMON_FORCING_REFERENCES = (
    ForcingReference(
        "anthropogenic emissions",
        "anthropogenic-slcf-co2-emissions",
    ),
    ForcingReference(
        "biomass burning emissions",
        "open-biomass-burning-emissions",
    ),
    ForcingReference("land use", "land-use"),
    ForcingReference("greenhouse gas concentrations", "greenhouse-gas-concentrations"),
    ForcingReference(
        "stratospheric aerosol forcing",
        "stratospheric-volcanic-so2-emissions-aod",
    ),
    ForcingReference("ozone", "ozone"),
    ForcingReference("nitrogen deposition", "nitrogen-deposition"),
    ForcingReference("solar", "solar"),
    ForcingReference(
        "aerosol optical properties",
        "aerosol-optical-properties-macv2-sp",
    ),
    ForcingReference("population density", "population"),
)

AMIP_FORCING_REFERENCES = (
    ForcingReference(
        "AMIP sea-surface temperature and sea-ice boundary forcing",
        "amip-sst-sea-ice-boundary-forcing",
    ),
)

COMMON_FORCING_NOTES = render_forcing_reference_list(COMMON_FORCING_REFERENCES)
