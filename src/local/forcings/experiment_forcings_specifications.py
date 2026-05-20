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
            notes=(
                "the ozone forcing should come from files "
                "with the source ID `FZJ-CMIP-ozone-2-0`. "
                "The CMIP Panel co-chairs are recommending that simulations "
                "based on `FZJ-CMIP-ozone-1-2` are re-run if possible. "
                "`FZJ-CMIP-ozone-2-0` was released quite late, "
                "so if you have simulations based on `FZJ-CMIP-ozone-1-2`, "
                "these would be of interest to the Forcings Task Team "
                "so please publish them "
                "([discussion of how to set the value for the forcing 'f' identifier in such files is ongoing](https://github.com/PCMDI/input4MIPs_CVs/issues/415))."  # noqa: E501
            ),
        ),
        ESGFBasedForcingSpecification(
            "nitrogen-deposition",
            fixed=False,
            recommended_versions=("FZJ-CMIP-nitrogen-2-0",),
            acceptable_versions=("FZJ-CMIP-nitrogen-1-2",),
            notes=(
                "the notrogen deposition forcing should come from files "
                "with the source ID `FZJ-CMIP-nitrogen-2-0`. "
                "`FZJ-CMIP-nitrogen-2-0` was released quite late "
                "and the impact of the change is likely to be small, "
                "so if you have simulations based on `FZJ-CMIP-nitrogen-1-2`, "
                "you do not need to re-run them."
                "Even if you have run pre-industrial control simulations "
                "with `FZJ-CMIP-nitrogen-1-2`, "
                "it is recommended to nonetheless run historical simulations "
                "with `FZJ-CMIP-nitrogen-2-0` because the discontinuity "
                "going from pre-industrial control `FZJ-CMIP-nitrogen-1-2` "
                "to historical `FZJ-CMIP-nitrogen-2-0` "
                "is expected to introduce smaller issues "
                "than using `FZJ-CMIP-nitrogen-1-2` over the historical period."
            ),
        ),
        ESGFBasedForcingSpecification(
            "solar",
            fixed=False,
            recommended_versions=("SOLARIS-HEPPA-CMIP-4-6",),
        ),
        NonESGFBasedForcingSpecification(
            "aerosol-optical-properties-macv2-sp",
            fixed=False,
            notes=(
                "Please see this "
                "[specific guidance section](https://input4mips-cvs.readthedocs.io/en/latest/dataset-overviews/aerosol-optical-properties-macv2-sp/#datasets-for-cmip7-phases) "  # noqa: E501
                "for data access and version information."
            ),
        ),
        ESGFBasedForcingSpecification(
            "population",
            fixed=False,
            recommended_versions=("PIK-CMIP-1-0-1",),
        ),
    )
)
