"""
Forcings specifications for specific experiments

Designed to be re-used and have these all in one place
"""

from __future__ import annotations

import dataclasses

from .specification import (
    ForcingSpecification,
    Input4MIPsBasedForcingSpecification,
    NonInput4MIPsBasedForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)

NOT_AVAILABLE_YET = "not-available-yet"

SIMPLE_PLUMES_SPECIFICATION = NonInput4MIPsBasedForcingSpecification(
    "aerosol-optical-properties-macv2-sp",
    fixed=False,
    notes=(
        "Please see this "
        "[specific guidance section](https://input4mips-cvs.readthedocs.io/en/latest/dataset-overviews/aerosol-optical-properties-macv2-sp/#datasets-for-cmip7-phases) "  # noqa: E501
        "for data access and version information."
    ),
)

HISTORICAL_FORCINGS_SPECIFICATION = ForcingSpecification(
    specific_forcings=(
        Input4MIPsBasedForcingSpecification(
            "anthropogenic-slcf-co2-emissions",
            fixed=False,
            recommended_versions=(
                "CEDS-CMIP-2025-04-18",
                "CEDS-CMIP-2025-04-18-supplemental",
            ),
        ),
        Input4MIPsBasedForcingSpecification(
            "open-biomass-burning-emissions",
            fixed=False,
            recommended_versions=("DRES-CMIP-BB4CMIP7-2-0",),
        ),
        Input4MIPsBasedForcingSpecification(
            "land-use",
            fixed=False,
            recommended_versions=("UofMD-landState-3-1-2",),
            acceptable_versions=("UofMD-landState-3-1-1",),
        ),
        Input4MIPsBasedForcingSpecification(
            "greenhouse-gas-concentrations",
            fixed=False,
            recommended_versions=("CR-CMIP-1-0-0",),
        ),
        Input4MIPsBasedForcingSpecification(
            "stratospheric-volcanic-so2-emissions-aod",
            fixed=False,
            recommended_versions=("UOEXETER-CMIP-2-2-1",),
        ),
        Input4MIPsBasedForcingSpecification(
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
        Input4MIPsBasedForcingSpecification(
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
        Input4MIPsBasedForcingSpecification(
            "solar",
            fixed=False,
            recommended_versions=("SOLARIS-HEPPA-CMIP-4-6",),
        ),
        SIMPLE_PLUMES_SPECIFICATION,
        Input4MIPsBasedForcingSpecification(
            "population",
            fixed=False,
            recommended_versions=("PIK-CMIP-1-0-1",),
        ),
    )
)


def get_iam_based_emissions_scenario_forcings(
    forcing_slug: str,
    scenario_drs_name: str,
    scenario_short_name: str,
) -> Input4MIPsBasedForcingSpecification:
    """
    Get the IAM-based emissions forcings for a given scenario
    """
    if scenario_drs_name.endswith("ext"):
        return Input4MIPsBasedForcingSpecification(
            forcing_slug,
            fixed=False,
            recommended_versions=(NOT_AVAILABLE_YET,),
            notes="In preparation",
        )

    common = "IIASA-IAMC-1-1-1"
    scenario_specific = f"IIASA-IAMC-{scenario_short_name}-1-1-1"

    res = Input4MIPsBasedForcingSpecification(
        forcing_slug,
        fixed=False,
        recommended_versions=(scenario_specific, common),
    )

    return res


def get_land_use_scenario_forcings(
    forcing_slug: str, scenario_drs_name: str, scenario_short_name: str
) -> Input4MIPsBasedForcingSpecification:
    """
    Get the land-use forcings for a given scenario
    """
    if scenario_drs_name.endswith("ext") or scenario_short_name not in {"vl", "h"}:
        return Input4MIPsBasedForcingSpecification(
            forcing_slug,
            fixed=False,
            recommended_versions=(NOT_AVAILABLE_YET,),
            notes="In preparation",
        )

    scenario_specific = f"UofMD-landState-{scenario_short_name}-3-1-1"
    scenario_specific_alternate = scenario_specific.replace("3-1-1", "3-1")

    res = Input4MIPsBasedForcingSpecification(
        forcing_slug,
        fixed=False,
        recommended_versions=(scenario_specific,),
        acceptable_versions=(scenario_specific_alternate,),
    )

    return res


def get_ghg_concentrations_scenario_forcings(
    forcing_slug: str,
    scenario_drs_name: str,
    scenario_short_name: str,
) -> Input4MIPsBasedForcingSpecification:
    """
    Get the greenhouse-gas concentrations forcings for a given scenario
    """
    scenario_specific = f"CR-{scenario_short_name}-1-1-0"
    if scenario_drs_name in {"vl", "h"}:
        acceptable_versions = (scenario_specific.replace("1-1-0", "1-0-0"),)
    else:
        acceptable_versions = ()

    res = Input4MIPsBasedForcingSpecification(
        forcing_slug,
        fixed=False,
        recommended_versions=(scenario_specific,),
        acceptable_versions=acceptable_versions,
    )

    return res


def get_ozone_scenario_forcings(
    forcing_slug: str,
    scenario_drs_name: str,
    scenario_short_name: str,
) -> Input4MIPsBasedForcingSpecification | OtherExperimentBasedForcingSpecification:
    """
    Get the ozone forcings for a given scenario
    """
    if scenario_drs_name.endswith("ext"):
        scenario = scenario_drs_name.replace("-ext", "").lower()

        return OtherExperimentBasedForcingSpecification(
            forcing_slug,
            experiment_esgvoc_id=scenario,
            # Constant extension
            user_modifications=(
                f"hold forcings constant after the end of the {scenario} data"
            ),
        )

    if scenario_short_name not in {"vl", "h"}:
        return Input4MIPsBasedForcingSpecification(
            forcing_slug,
            fixed=False,
            recommended_versions=(NOT_AVAILABLE_YET,),
            notes="In preparation",
        )

    scenario_specific = f"FZJ-CMIP-ozone-{scenario_short_name}-1-0"

    res = Input4MIPsBasedForcingSpecification(
        forcing_slug,
        fixed=False,
        recommended_versions=(scenario_specific,),
    )

    return res


def get_nitrogen_deposition_scenario_forcings(
    forcing_slug: str,
    scenario_drs_name: str,
    scenario_short_name: str,
) -> Input4MIPsBasedForcingSpecification | OtherExperimentBasedForcingSpecification:
    """
    Get the nitrogen deposition forcings for a given scenario
    """
    if scenario_short_name.endswith("ext"):
        scenario = scenario_drs_name.replace("-ext", "").lower()

        return OtherExperimentBasedForcingSpecification(
            forcing_slug,
            experiment_esgvoc_id=scenario,
            # Constant extension
            user_modifications=(
                f"hold forcings constant after the end of the {scenario} data"
            ),
        )

    if scenario_short_name not in {"vl", "h"}:
        return Input4MIPsBasedForcingSpecification(
            forcing_slug,
            fixed=False,
            recommended_versions=(NOT_AVAILABLE_YET,),
            notes="In preparation",
        )

    scenario_specific = f"FZJ-CMIP-nitrogen-{scenario_short_name}-1-0"

    res = Input4MIPsBasedForcingSpecification(
        forcing_slug,
        fixed=False,
        recommended_versions=(scenario_specific,),
    )

    return res


def get_solar_scenario_forcings(
    forcing_slug: str,
    scenario_drs_name: str,
    scenario_short_name: str,
) -> Input4MIPsBasedForcingSpecification:
    """
    Get the solar forcings for a given scenario
    """
    res = Input4MIPsBasedForcingSpecification(
        forcing_slug,
        fixed=False,
        recommended_versions=("SOLARIS-HEPPA-ScenarioMIP-4-6",),
        notes=(
            "If running beyond the time period provided in the data, "
            # TODO: try and get guidance on when that last solar cycle is
            "simply repeat the last solar cycle."
        )
        if scenario_drs_name.endswith("ext")
        else None,
    )

    return res


def get_simple_plumes_forcings(
    forcing_slug: str,
    scenario_drs_name: str,
    scenario_short_name: str,
) -> NonInput4MIPsBasedForcingSpecification:
    """
    Get the simple forcings for a given scenario
    """
    if scenario_drs_name.endswith("ext"):
        # Not available yet, waiting on emissions
        res = dataclasses.replace(
            SIMPLE_PLUMES_SPECIFICATION,
            notes="In preparation, waiting on the emissions to be available",
        )

    else:
        res = SIMPLE_PLUMES_SPECIFICATION

    return res


def get_population_density_scenario_forcings(
    forcing_slug: str,
    scenario_drs_name: str,
    scenario_short_name: str,
) -> Input4MIPsBasedForcingSpecification:
    """
    Get the population density forcings for a given scenario
    """
    scenario_specific = f"PIK-{scenario_short_name}-1-0-0"

    res = Input4MIPsBasedForcingSpecification(
        forcing_slug,
        fixed=False,
        recommended_versions=(scenario_specific,),
    )

    return res


GET_SCEN7_FORCINGS_BY_FORCING_TYPE = {
    "anthropogenic-slcf-co2-emissions": get_iam_based_emissions_scenario_forcings,
    "open-biomass-burning-emissions": get_iam_based_emissions_scenario_forcings,
    "land-use": get_land_use_scenario_forcings,
    "greenhouse-gas-concentrations": get_ghg_concentrations_scenario_forcings,
    "stratospheric-volcanic-so2-emissions-aod": lambda forcing_slug,
    x,
    y: Input4MIPsBasedForcingSpecification(
        forcing_slug,
        fixed=False,
        recommended_versions=("UOEXETER-ScenarioMIP-2-2-2",),
    ),
    "ozone": get_ozone_scenario_forcings,
    "nitrogen-deposition": get_nitrogen_deposition_scenario_forcings,
    "solar": get_solar_scenario_forcings,
    "aerosol-optical-properties-macv2-sp": get_simple_plumes_forcings,
    "population": get_population_density_scenario_forcings,
}


def get_scen7_forcing_specification(
    scenario_drs_name: str,
) -> ForcingSpecification:
    """Return ScenarioMIP forcing specification for a given scenario."""
    init_kwargs = {"specific_forcings": [], "other_experiment_based_forcings": []}
    for forcing_slug in (
        v.forcing_slug for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
    ):
        scenario_short_name = scenario_drs_name.replace("scen7-", "")
        specification = GET_SCEN7_FORCINGS_BY_FORCING_TYPE[forcing_slug](
            forcing_slug, scenario_drs_name, scenario_short_name
        )
        if isinstance(specification, OtherExperimentBasedForcingSpecification):
            init_kwargs["other_experiment_based_forcings"].append(specification)

        else:
            init_kwargs["specific_forcings"].append(specification)

    return ForcingSpecification(
        specific_forcings=tuple(init_kwargs["specific_forcings"]),
        other_experiment_based_forcings=tuple(
            init_kwargs["other_experiment_based_forcings"]
        ),
    )
