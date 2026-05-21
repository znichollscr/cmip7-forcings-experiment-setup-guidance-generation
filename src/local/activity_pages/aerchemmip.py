"""AerChemMIP experiment guidance pages."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from local.branching import BranchAtSameTimeAsOtherExperiment, BranchFromParentEnd
from local.experiment_dates import historical_end_year
from local.forcing_versions import (
    ForcingValue,
    forcing_ids_except,
    merge_source_ids,
    select_forcing_versions,
    source_ids_from_forcing_versions,
)
from local.forcings import (
    HISTORICAL_FORCINGS_SPECIFICATION,
    PICONTROL_FORCINGS_SPECIFICATION,
    ForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)
from local.guidance import (
    HISTORICAL_LINK,
    PI_CONTROL_LINK,
    ExperimentPage,
)
from local.output_time_axis import (
    PiClimOutputTimeAxisInformation,
)
from local.rendering import (
    only_keep_first_sentence,
)

from .cmip import LAST_HISTORICAL_YEAR

PRE_INDUSTRIAL_YEAR = 1850
SCEN7_AERCHEM_FORCING_IDS = ("anthropogenic-emissions",)
SCEN7_NON_DOWNLOADABLE_FORCING_IDS = ("aerosol-optical-properties",)

SCEN7_AER_FORCING_LABEL = (
    "aerosol and tropospheric non-methane ozone precursor emissions"
)
SCEN7_AQ_FORCING_LABEL = (
    "anthropogenic non-CH4 tropospheric ozone precursor emissions, "
    "aerosols and aerosol precursor emissions"
)


@dataclass(frozen=True)
class Scen7AerChemPageSpec:
    """Inputs needed to create an AerChemMIP scenario-variant page."""

    slug: str
    base_scenario_name: str
    aerchem_setup_source: str
    aerchem_versions_source: str
    aerchem_forcing_versions: Mapping[str, ForcingValue]
    base_forcing_versions: Mapping[str, ForcingValue]
    include_interactive_chemistry: bool


def historical_end_year_setup_source() -> str:
    """Render the setup source text for fixed historical-end-year forcings."""
    return (
        "be held fixed at "
        f"{historical_end_year()} values from the historical simulation"
    )


def historical_end_year_versions_source() -> str:
    """Render the versions source text for fixed historical-end-year forcings."""
    return f"the {historical_end_year()} values in the {HISTORICAL_LINK}"


def source_ids_for_scen7_aerchem_variant(
    *,
    aerchem_forcing_versions: Mapping[str, ForcingValue],
    base_forcing_versions: Mapping[str, ForcingValue],
) -> tuple[str, ...]:
    """Derive source IDs for a scen7 AerChemMIP scenario-variant page."""
    return merge_source_ids(
        source_ids_from_forcing_versions(
            select_forcing_versions(
                aerchem_forcing_versions,
                SCEN7_AERCHEM_FORCING_IDS,
            )
        ),
        source_ids_from_forcing_versions(
            select_forcing_versions(
                base_forcing_versions,
                forcing_ids_except(
                    base_forcing_versions,
                    *SCEN7_AERCHEM_FORCING_IDS,
                    *SCEN7_NON_DOWNLOADABLE_FORCING_IDS,
                ),
            )
        ),
    )


def make_piclim_based_page(
    id_esgvoc: str,
    forcing_slugs_historical_last_year: tuple[str, ...],
    historical_last_year: int = LAST_HISTORICAL_YEAR,
    user_modifications: str | None = None,
    render_description: Callable[[str], str] = lambda x: x,
) -> ExperimentPage:
    """
    Make a piClim-* page
    """
    if user_modifications is None:
        user_modifications = f"apply the {historical_last_year} value on repeat"

    res = ExperimentPage(
        id_esgvoc=id_esgvoc,
        branch_information=BranchAtSameTimeAsOtherExperiment("piclim-control"),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="picontrol",
                    )
                    for v in PICONTROL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug not in forcing_slugs_historical_last_year
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                        user_modifications=user_modifications,
                        fixed_override=True,
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in forcing_slugs_historical_last_year
                ),
                OtherExperimentBasedForcingSpecification(
                    forcing_slug="sst-forcing",
                    experiment_esgvoc_id="piclim-control",
                ),
            ),
        ),
        output_time_axis_info=PiClimOutputTimeAxisInformation(),
        render_description=render_description,
    )

    return res


# TODO: re-use something like this elsewhere
def make_hist_star_page(
    id_esgvoc: str,
    forcing_slugs_historical_modified: tuple[str, ...],
    user_modifications: str | None = None,
    render_description: Callable[[str], str] = lambda x: x,
) -> ExperimentPage:
    """
    Make a hist-* page
    """
    res = ExperimentPage(
        id_esgvoc=id_esgvoc,
        branch_information=BranchAtSameTimeAsOtherExperiment("historical"),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug not in forcing_slugs_historical_modified
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                        user_modifications=user_modifications,
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in forcing_slugs_historical_modified
                ),
            ),
        ),
        render_description=render_description,
    )

    return res


def make_aerchemmip_scen7_vl_based_page(
    id_esgvoc: str,
    forcing_slugs_scen7_h: tuple[str, ...],
    user_modifications_text: str,
    render_description: Callable[[str], str] = lambda x: x,
) -> ExperimentPage:
    """
    Make a scen7-vl* AerChemMIP page
    """
    res = ExperimentPage(
        id_esgvoc=id_esgvoc,
        branch_information=BranchFromParentEnd(),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="scen7-h",
                        user_modifications=f"only for {user_modifications_text}. ",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in forcing_slugs_scen7_h
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="scen7-vl",
                        user_modifications=f"only for everything except {user_modifications_text}.",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in forcing_slugs_scen7_h
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="scen7-vl",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug not in forcing_slugs_scen7_h
                ),
            ),
        ),
        render_description=render_description,
    )

    return res


def make_aerchemmip_scen7_h_based_page(
    id_esgvoc: str,
    forcing_slugs_historical_constant: tuple[str, ...],
    user_modifications_text: str,
    render_description: Callable[[str], str] = lambda x: x,
) -> ExperimentPage:
    """
    Make a scen7-h* AerChemMIP page
    """
    res = ExperimentPage(
        id_esgvoc=id_esgvoc,
        branch_information=BranchFromParentEnd(),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=(
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="scen7-h",
                        user_modifications=f"only for everything except {user_modifications_text}.",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in forcing_slugs_historical_constant
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="historical",
                        user_modifications=(
                            f"only for {user_modifications_text}. "
                            f"These forcings should be fixed to {LAST_HISTORICAL_YEAR} values."
                        ),
                        fixed_override=True,
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug in forcing_slugs_historical_constant
                ),
                *(
                    OtherExperimentBasedForcingSpecification(
                        forcing_slug=v.forcing_slug,
                        experiment_esgvoc_id="scen7-h",
                    )
                    for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
                    if v.forcing_slug not in forcing_slugs_historical_constant
                ),
            ),
        ),
        render_description=render_description,
    )

    return res


# TODO: use something like this elsewhere
def make_aerchemmip_esm_variant_page(
    id_esgvoc: str,
    render_description: Callable[[str], str] = lambda x: x,
) -> ExperimentPage:
    """
    Make a esm-scen7-* AerChemMIP page
    """
    res = ExperimentPage(
        id_esgvoc=id_esgvoc,
        branch_information=BranchFromParentEnd(),
        forcings=ForcingSpecification(
            other_experiment_based_forcings=tuple(
                OtherExperimentBasedForcingSpecification(
                    forcing_slug=v.forcing_slug,
                    experiment_esgvoc_id=id_esgvoc.replace("esm-", ""),
                )
                for v in HISTORICAL_FORCINGS_SPECIFICATION.specific_forcings
            ),
        ),
        render_description=render_description,
    )

    return res


AERCHEMMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    make_piclim_based_page(
        "piclim-ch4",
        forcing_slugs_historical_last_year=("greenhouse-gas-concentrations",),
        user_modifications=(
            f"apply the {LAST_HISTORICAL_YEAR} methane (CH<sub>4</sub>) concentrations or emissions "
            "(as appropriate for your model) value on repeat "
            f"and the {PRE_INDUSTRIAL_YEAR} value on repeat for all other species"
        ),
        render_description=only_keep_first_sentence,
    ),
    make_piclim_based_page(
        "piclim-n2o",
        forcing_slugs_historical_last_year=("greenhouse-gas-concentrations",),
        user_modifications=(
            f"apply the {LAST_HISTORICAL_YEAR} nitrous oxide (N<sub>2</sub>O) concentrations or emissions "
            "(as appropriate for your model) value on repeat "
            f"and the {PRE_INDUSTRIAL_YEAR} value on repeat for all other species"
        ),
        render_description=only_keep_first_sentence,
    ),
    make_piclim_based_page(
        "piclim-nox",
        # TODO: check if anthro and biomass or just anthro
        forcing_slugs_historical_last_year=(
            "anthropogenic-slcf-co2-emissions",
            "open-biomass-burning-emissions",
        ),
        user_modifications=(
            f"apply the {LAST_HISTORICAL_YEAR} nitrogen oxide (NO<sub>x</sub>) emissions "
            "value on repeat "
            f"and the {PRE_INDUSTRIAL_YEAR} value on repeat for all other species"
        ),
        render_description=only_keep_first_sentence,
    ),
    make_piclim_based_page(
        "piclim-ods",
        forcing_slugs_historical_last_year=("greenhouse-gas-concentrations",),
        user_modifications=(
            f"apply the {LAST_HISTORICAL_YEAR} ozone-depleting substances (ODS) concentrations "
            "(as appropriate for your model) value on repeat "
            f"and the {PRE_INDUSTRIAL_YEAR} value on repeat for all other species"
        ),
        render_description=only_keep_first_sentence,
    ),
    make_piclim_based_page(
        "piclim-so2",
        # TODO: check if anthro and biomass or just anthro
        forcing_slugs_historical_last_year=(
            "anthropogenic-slcf-co2-emissions",
            "open-biomass-burning-emissions",
        ),
        user_modifications=(
            f"apply the {LAST_HISTORICAL_YEAR} sulfur dioxide (SO<sub>2</sub>) emissions "
            "value on repeat "
            f"and the {PRE_INDUSTRIAL_YEAR} value on repeat for all other species"
        ),
        render_description=only_keep_first_sentence,
    ),
    make_hist_star_page(
        "hist-piaer",
        forcing_slugs_historical_modified=tuple(
            (
                # TODO: check if biomass burning is meant to be included
                "anthropogenic-slcf-co2-emissions",
                "open-biomass-burning-emissions",
            )
        ),
        user_modifications=(
            "BC, OC, NH<sub>3</sub> and SO<sub>2</sub> emissions "
            f"should be fixed to  {PI_CONTROL_LINK} values"
        ),
        # Probably better to keep this off as it will help people spot errors more easily
        # render_description=lambda x: (
        #     f"{only_keep_first_sentence(x)} "
        #     "Intended for models without interactive chemistry. "
        #     "Identical to hist-piAer in AerChemMIP phase 1."
        # ),
    ),
    make_hist_star_page(
        "hist-piaq",
        forcing_slugs_historical_modified=tuple(
            (
                # TODO: check if biomass burning is meant to be included
                "anthropogenic-slcf-co2-emissions",
                "open-biomass-burning-emissions",
            )
        ),
        user_modifications=(
            "aerosol (BC, OC, NH<sub>3</sub>, SO<sub>2</sub>) "
            "and tropospheric non-methane ozone precursor emissions (NMVOCs, CO, NO<sub>x</sub>) "
            f"should be fixed to  {PI_CONTROL_LINK} values"
        ),
        # Probably better to keep this off as it will help people spot errors more easily
        # render_description=lambda x: (
        #     f"{only_keep_first_sentence(x)} "
        #     "Intended for models with interactive chemistry. "
        # ),
    ),
    make_aerchemmip_scen7_h_based_page(
        "scen7-h-aer",
        forcing_slugs_historical_constant=tuple(
            (
                # TODO: check if biomass burning is meant to be included
                "anthropogenic-slcf-co2-emissions",
                "open-biomass-burning-emissions",
            )
        ),
        user_modifications_text=(
            "aerosol (BC, OC, NH<sub>3</sub>, SO<sub>2</sub>) emissions"
        ),
    ),
    make_aerchemmip_esm_variant_page("esm-scen7-h-aer"),
    make_aerchemmip_scen7_h_based_page(
        "scen7-h-aq",
        forcing_slugs_historical_constant=tuple(
            (
                # TODO: check if biomass burning is meant to be included
                "anthropogenic-slcf-co2-emissions",
                "open-biomass-burning-emissions",
            )
        ),
        user_modifications_text=(
            "aerosol (BC, OC, NH<sub>3</sub>, SO<sub>2</sub>) "
            "and tropospheric non-methane ozone precursor emissions (NMVOCs, CO, NO<sub>x</sub>)"
        ),
    ),
    make_aerchemmip_esm_variant_page("esm-scen7-h-aq"),
    make_aerchemmip_scen7_vl_based_page(
        "scen7-vl-aer",
        forcing_slugs_scen7_h=tuple(
            (
                # TODO: check if biomass burning is meant to be included
                "anthropogenic-slcf-co2-emissions",
                "open-biomass-burning-emissions",
            )
        ),
        user_modifications_text=(
            "aerosol (BC, OC, NH<sub>3</sub>, SO<sub>2</sub>) emissions"
        ),
    ),
    make_aerchemmip_esm_variant_page("esm-scen7-vl-aer"),
    make_aerchemmip_scen7_vl_based_page(
        "scen7-vl-aq",
        forcing_slugs_scen7_h=tuple(
            (
                # TODO: check if biomass burning is meant to be included
                "anthropogenic-slcf-co2-emissions",
                "open-biomass-burning-emissions",
            )
        ),
        user_modifications_text=(
            "aerosol (BC, OC, NH<sub>3</sub>, SO<sub>2</sub>) "
            "and tropospheric non-methane ozone precursor emissions (NMVOCs, CO, NO<sub>x</sub>)"
        ),
    ),
    make_aerchemmip_esm_variant_page("esm-scen7-vl-aq"),
)
