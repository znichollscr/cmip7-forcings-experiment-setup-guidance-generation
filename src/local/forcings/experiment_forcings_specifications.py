"""
Forcings specifications for specific experiments

Designed to be re-used and have these all in one place
"""

from __future__ import annotations

import dataclasses
from functools import partial

from local.vocab import get_experiment

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
                "the nitrogen deposition forcing should come from files "
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

picontrol_forcings_specification_specific_forcings = []
for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings:
    if v.forcing_slug in ("ozone", "nitrogen-deposition"):
        continue

    keep = dataclasses.replace(v, fixed=True)
    if keep.forcing_slug in (
        "stratospheric-volcanic-so2-emissions-aod",
        "solar",
    ):
        new_notes = (
            "The piControl forcing is not simply a repeat of 1850 values. "
            "Please use the specific piControl files provided."
        )
        if keep.notes:
            keep_notes = keep.notes[:1].upper() + keep.notes[1:]
            new_notes = f"{new_notes} {keep_notes}"

        keep = dataclasses.replace(
            keep,
            notes=new_notes,
        )

    picontrol_forcings_specification_specific_forcings.append(keep)

PICONTROL_FORCINGS_SPECIFICATION = ForcingSpecification(
    specific_forcings=(
        *picontrol_forcings_specification_specific_forcings,
        Input4MIPsBasedForcingSpecification(
            "ozone",
            fixed=True,
            recommended_versions=("FZJ-CMIP-ozone-1-2",),
            notes=(
                "The piControl forcing is not simply a repeat of 1850 values. "
                "Please use the specific piControl files provided. "
                "The ozone forcing should come from files "
                "with the source ID `FZJ-CMIP-ozone-1-2`. "
                "The release of `FZJ-CMIP-ozone-2-0` "
                "only affected the historical forcing data. "
                "`FZJ-CMIP-ozone-2-0` did not include "
                "any data for piControl simulations. "
                # TODO: check for inconsistent use of `experiment_name` throughout
            ),
        ),
        Input4MIPsBasedForcingSpecification(
            "nitrogen-deposition",
            fixed=True,
            recommended_versions=("FZJ-CMIP-nitrogen-2-0",),
            acceptable_versions=("FZJ-CMIP-nitrogen-1-2",),
            notes=(
                "the nitrogen deposition forcing should come from files "
                "with the source ID `FZJ-CMIP-nitrogen-2-0`. "
                "`FZJ-CMIP-nitrogen-2-0` was released quite late "
                "and the impact of the change is likely to be small, "
                "so if you have simulations based on `FZJ-CMIP-nitrogen-1-2`, "
                "you do not need to re-run them."
            ),
        ),
    )
)

HISTORICAL_FORCINGS_SPECIFICATION_AMIP_SSTS = Input4MIPsBasedForcingSpecification(
    "amip-sst-sea-ice-boundary-forcing",
    fixed=False,
    recommended_versions=("PCMDI-AMIP-1-1-10",),
)


def get_iam_based_emissions_scenario_forcings(
    forcing_slug: str,
    scenario_drs_name: str,
    scenario_short_name: str,
    biomass_burning: bool,
) -> Input4MIPsBasedForcingSpecification:
    """
    Get the IAM-based emissions forcings for a given scenario
    """
    common = "IIASA-IAMC-1-1-1"
    scenario_slug = scenario_short_name.replace("esm-", "")
    scenario_specific = f"IIASA-IAMC-{scenario_slug}-1-1-1"
    recommended_versions_l = [common, scenario_specific]

    if biomass_burning:
        notes = None

    else:
        scenario_specific_aviation_emms_fix = f"IIASA-IAMC-{scenario_slug}-1-1-2"
        recommended_versions_l.append(scenario_specific_aviation_emms_fix)

        notes = (
            "the aviation emissions should come from "
            f"`{scenario_specific_aviation_emms_fix}`. "
            f"`{scenario_specific_aviation_emms_fix}` was released quite late "
            "and the impact of the change is likely to be small, so if you have "
            f"simulations based on `{scenario_specific}`, "
            "you do not need to re-run them."
        )

    res = Input4MIPsBasedForcingSpecification(
        forcing_slug,
        fixed=False,
        recommended_versions=tuple(recommended_versions_l),
        notes=notes,
    )

    return res


def get_land_use_scenario_forcings(
    forcing_slug: str, scenario_drs_name: str, scenario_short_name: str
) -> Input4MIPsBasedForcingSpecification:
    """
    Get the land-use forcings for a given scenario
    """
    if scenario_drs_name.endswith("ext") or scenario_short_name not in {"vl", "h", "m"}:
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


def get_volcanic_scenario_forcings(
    forcing_slug: str,
    scenario_drs_name: str,
    scenario_short_name: str,
) -> Input4MIPsBasedForcingSpecification | OtherExperimentBasedForcingSpecification:
    """
    Get the volcanic forcings for a given scenario
    """
    if scenario_drs_name.endswith("ext"):
        return get_scenario_extension_forcing_for_constant_extension(
            forcing_slug, scenario_drs_name
        )

    res = Input4MIPsBasedForcingSpecification(
        forcing_slug,
        fixed=False,
        recommended_versions=("UOEXETER-ScenarioMIP-2-2-2",),
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
        return get_scenario_extension_forcing_for_constant_extension(
            forcing_slug, scenario_drs_name
        )

    if scenario_short_name not in {"vl", "h", "hl", "m"}:
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
    if scenario_drs_name.endswith("ext"):
        return get_scenario_extension_forcing_for_constant_extension(
            forcing_slug, scenario_drs_name
        )

    if scenario_short_name not in {"vl", "h", "hl", "m"}:
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
        # Checked via email with Bernd.
        # Subject "Extending solar data beyond 2300"
        notes=(
            "If running beyond the time period provided in the data, "
            "repeat the data, starting with 24 August 2038 "
            "(i.e. for 2300-01-01, use data from 2038-08-24, "
            "for 2300-01-02, use data from 2038-08-25 etc.)."
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
            notes="In preparation, will be made available at https://zenodo.org/records/21671953",
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


def get_scenario_extension_forcing_for_constant_extension(
    forcing_slug: str, scenario_drs_name: str
) -> OtherExperimentBasedForcingSpecification:
    """Return scenario extension forcing by just keeping scenario forcing constant."""
    scenario = scenario_drs_name.replace("-ext", "").lower()
    scenario_esgvoc = get_experiment(scenario)
    scenario_last_year = scenario_esgvoc.end_timestamp.year
    return OtherExperimentBasedForcingSpecification(
        forcing_slug,
        experiment_esgvoc_id=scenario,
        user_modifications=f"hold forcings constant at {scenario_last_year} levels",
        fixed_override=True,
    )


GET_SCEN7_FORCINGS_BY_FORCING_TYPE = {
    "anthropogenic-slcf-co2-emissions": partial(
        get_iam_based_emissions_scenario_forcings, biomass_burning=False
    ),
    "open-biomass-burning-emissions": partial(
        get_iam_based_emissions_scenario_forcings, biomass_burning=True
    ),
    "land-use": get_land_use_scenario_forcings,
    "greenhouse-gas-concentrations": get_ghg_concentrations_scenario_forcings,
    "stratospheric-volcanic-so2-emissions-aod": get_volcanic_scenario_forcings,
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


def get_iam_based_emissions_polmip_vl_cf_forcings(
    forcing_slug: str,
    scenario_drs_name: str,
) -> dict[str, list[Input4MIPsBasedForcingSpecification]]:
    """
    Get the IAM-based emissions forcings for PolMIP vl-cf variants
    """
    common = "IIASA-IAMC-1-1-1"

    scenario_slug = scenario_drs_name.replace("esm-", "")
    vl_cf_source_id = f"IIASA-IAMC-{scenario_slug}-1-1-1"
    recommended_versions_l = [common, vl_cf_source_id]

    is_emissions_driven = "esm-" in scenario_drs_name
    if not is_emissions_driven:
        # Nothing to specify
        res_specific = []

    else:
        is_extension = scenario_drs_name.endswith("-ext")
        if is_extension:
            if is_emissions_driven:
                non_co2_sources = ["esm-scen7-vl-ext"]
            else:
                non_co2_sources = ["scen7-vl-ext"]

        elif is_emissions_driven:
            non_co2_sources = ["esm-hist", "esm-scen7-vl"]

        else:
            non_co2_sources = ["historical", "scen7-vl"]

        non_co2_sources_str = (
            f"`{non_co2_sources[0]}`"
            if len(non_co2_sources) == 1
            else f"`{'`, `'.join(non_co2_sources[:-1])}` and `{non_co2_sources[-1]}`"
        )
        res_specific = [
            Input4MIPsBasedForcingSpecification(
                forcing_slug,
                fixed=False,
                recommended_versions=tuple(recommended_versions_l),
                notes=(
                    "All anthropogenic emissions forcings "
                    "other than CO<sub>2</sub> emissions must come from "
                    f"the forcings used for {non_co2_sources_str}"
                ),
            )
        ]

    res_other = [
        OtherExperimentBasedForcingSpecification(
            forcing_slug,
            experiment_esgvoc_id=experiment_id,
        )
        for experiment_id in non_co2_sources
    ]

    res = {
        "specific_forcings": res_specific,
        "other_experiment_based_forcings": res_other,
    }

    return res


def get_ghg_concentrations_polmip_vl_cf_forcings(
    forcing_slug: str,
    scenario_drs_name: str,
) -> list[Input4MIPsBasedForcingSpecification]:
    """
    Get the greenhouse-gas concentrations forcings for a given scenario
    """
    scenario_slug = scenario_drs_name.replace("esm-", "")
    scenario_short_name = scenario_slug.replace("scen7-", "")

    scenario_specific = f"CR-{scenario_short_name}-1-1-0"
    acceptable_versions = ()

    res = {
        "specific_forcings": [
            Input4MIPsBasedForcingSpecification(
                forcing_slug,
                fixed=False,
                recommended_versions=(scenario_specific,),
                acceptable_versions=acceptable_versions,
            )
        ],
        "other_experiment_based_forcings": [],
    }

    return res


GET_POLMIP_VL_CF_FORCINGS_BY_FORCING_TYPE = {
    "anthropogenic-slcf-co2-emissions": get_iam_based_emissions_polmip_vl_cf_forcings,
    "greenhouse-gas-concentrations": get_ghg_concentrations_polmip_vl_cf_forcings,
}


def get_polmip_vl_cf_forcing_specification_purely_vl_based(
    forcing_slug: str,
    scenario_drs_name: str,
) -> list[OtherExperimentBasedForcingSpecification]:
    """
    Get PolMIP vl-cf variatn forcing specifcations for forcings that are purely vl based
    """
    is_extension = scenario_drs_name.endswith("-ext")

    scen7_drs_name = scenario_drs_name.replace("vl-cf", "scen7-vl")
    if is_extension:
        res = [
            OtherExperimentBasedForcingSpecification(
                forcing_slug=forcing_slug,
                experiment_esgvoc_id=scen7_drs_name.lower(),
                user_modifications=None,
            )
        ]

    else:
        res = [
            OtherExperimentBasedForcingSpecification(
                forcing_slug=forcing_slug,
                experiment_esgvoc_id="historical",
                user_modifications=None,
            ),
            OtherExperimentBasedForcingSpecification(
                forcing_slug=forcing_slug,
                experiment_esgvoc_id=scen7_drs_name.lower(),
                user_modifications=None,
            ),
        ]

    return res


def get_polmip_vl_cf_forcing_specification(
    scenario_drs_name: str,
) -> ForcingSpecification:
    """Return PolMIP forcing specification for a `vl-cf` scenario."""
    init_kwargs = {"specific_forcings": [], "other_experiment_based_forcings": []}

    co2_emissions_driven = scenario_drs_name.startswith("esm-")
    vl_cf_specific_slugs = ("greenhouse-gas-concentrations",)
    esm_vl_cf_specific_slugs = (
        "anthropogenic-slcf-co2-emissions",
        *vl_cf_specific_slugs,
    )

    for forcing_slug in (
        v.forcing_slug for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
    ):
        use_vl_cf = (
            co2_emissions_driven and (forcing_slug in esm_vl_cf_specific_slugs)
        ) or (not co2_emissions_driven and (forcing_slug in vl_cf_specific_slugs))

        if use_vl_cf:
            specification = GET_POLMIP_VL_CF_FORCINGS_BY_FORCING_TYPE[forcing_slug](
                forcing_slug, scenario_drs_name
            )
            init_kwargs["specific_forcings"].extend(specification["specific_forcings"])
            init_kwargs["other_experiment_based_forcings"].extend(
                specification["other_experiment_based_forcings"]
            )

        else:
            specifications = get_polmip_vl_cf_forcing_specification_purely_vl_based(
                forcing_slug, scenario_drs_name
            )
            init_kwargs["other_experiment_based_forcings"].extend(specifications)

    return ForcingSpecification(
        specific_forcings=tuple(init_kwargs["specific_forcings"]),
        other_experiment_based_forcings=tuple(
            init_kwargs["other_experiment_based_forcings"]
        ),
    )
