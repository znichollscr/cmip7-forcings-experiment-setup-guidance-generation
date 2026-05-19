"""
Forcings specifications for specific experiments

Designed to be re-used and have these all in one place
"""

from __future__ import annotations

from .specification import (
    ESGFBasedForcingSpecification,
    ForcingSpecification,
    NonESGFBasedForcingSpecification,
)

HISTORICAL_FORCINGS_SPECIFICATION = ForcingSpecification(
    specific_forcings=(
        ESGFBasedForcingSpecification(
            "anthropogenic-slcf-co2-emissions",
            fixed=False,
            recommended_versions=(
                "CEDS-CMIP-2025-04-18",
                "CEDS-CMIP-2025-04-18-supplemental",
            ),
        ),
        ESGFBasedForcingSpecification(
            "open-biomass-burning-emissions",
            fixed=False,
            recommended_versions=("DRES-CMIP-BB4CMIP7-2-0",),
        ),
        ESGFBasedForcingSpecification(
            "land-use",
            fixed=False,
            recommended_versions=("UofMD-landState-3-1-2",),
            acceptable_versions=("UofMD-landState-3-1-1",),
        ),
        ESGFBasedForcingSpecification(
            "greenhouse-gas-concentrations",
            fixed=False,
            recommended_versions=("CR-CMIP-1-0-0",),
        ),
        ESGFBasedForcingSpecification(
            "stratospheric-volcanic-so2-emissions-aod",
            fixed=False,
            recommended_versions=("UOEXETER-CMIP-2-2-1",),
        ),
        ESGFBasedForcingSpecification(
            "ozone",
            fixed=False,
            recommended_versions=("FZJ-CMIP-ozone-2-0",),
            acceptable_versions=("FZJ-CMIP-ozone-1-2",),
            # # TODO: add notes about issues here
            # notes=""
        ),
        ESGFBasedForcingSpecification(
            "nitrogen-deposition",
            fixed=False,
            recommended_versions=("FZJ-CMIP-nitrogen-2-0",),
            acceptable_versions=("FZJ-CMIP-nitrogen-1-2",),
            # # TODO: add notes about issues here
            # notes=""
        ),
        ESGFBasedForcingSpecification(
            "solar",
            fixed=False,
            recommended_versions=("SOLARIS-HEPPA-CMIP-4-6",),
            # # TODO: add notes about issues here
            # notes=""
        ),
        NonESGFBasedForcingSpecification(
            "aerosol-optical-properties-macv2-sp",
            fixed=False,
            # TODO: notes about where to get this
            # notes="",
        ),
        ESGFBasedForcingSpecification(
            "population",
            fixed=False,
            recommended_versions=("PIK-CMIP-1-0-1",),
        ),
    )
)
