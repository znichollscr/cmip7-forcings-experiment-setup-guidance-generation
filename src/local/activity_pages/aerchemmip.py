"""AerChemMIP experiment guidance pages."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from local.forcing_references import COMMON_FORCING_NOTES
from local.forcing_versions import (
    CMIP_FORCING_VERSIONS,
    SCEN7_H_FORCING_VERSIONS,
    SCEN7_VL_FORCING_VERSIONS,
    ForcingValue,
    cmip_forcing_ids_except,
    forcing_ids_except,
    merge_source_ids,
    select_forcing_versions,
    source_ids_for_cmip_forcing_combination,
    source_ids_from_forcing_versions,
)
from local.guidance import (
    HISTORICAL_LINK,
    PI_CONTROL_LINK,
    ExperimentPage,
)
from local.piclim_variants import (
    HistoricalForcing,
    make_piclim_historical_forcing_variant_page,
)
from local.rendering import (
    block,
    date_from_timestamp,
    join_blocks,
    join_lines,
    render_data_access_body,
)
from local.vocab import get_experiment

SCEN7_AERCHEM_FORCING_IDS = ("anthropogenic-emissions",)
SCEN7_NON_DOWNLOADABLE_FORCING_IDS = ("aerosol-optical-properties",)

SCEN7_AER_FORCING_LABEL = (
    "aerosol and tropospheric non-methane ozone precursor emissions"
)
SCEN7_AQ_FORCING_LABEL = (
    "anthropogenic non-CH4 tropospheric ozone precursor emissions, "
    "aerosols and aerosol precursor emissions"
)
HISTORICAL_EXPERIMENT_ID = "historical"


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


def historical_end_year() -> int:
    """Return the last year of the historical experiment."""
    historical_experiment = get_experiment(HISTORICAL_EXPERIMENT_ID)
    end_date = date_from_timestamp(
        getattr(historical_experiment, "end_timestamp", None)
    )
    if end_date is None:
        msg = (
            "Cannot determine the historical end year because the CMIP7 CVs do "
            "not define a supported end timestamp for 'historical'."
        )
        raise ValueError(msg)

    return end_date.year


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


def make_scen7_aerchem_page(spec: Scen7AerChemPageSpec) -> ExperimentPage:
    """Create an AerChemMIP scenario-variant page."""
    experiment_name = get_experiment(spec.slug).drs_name
    forcing_label = (
        SCEN7_AQ_FORCING_LABEL
        if spec.include_interactive_chemistry
        else SCEN7_AER_FORCING_LABEL
    )
    chemistry_capability = (
        "include interactive chemistry"
        if spec.include_interactive_chemistry
        else "do not include interactive chemistry"
    )

    return ExperimentPage(
        slug=spec.slug,
        experiment_setup=join_blocks(
            f"The `{experiment_name}` simulation is a variant of the `{spec.base_scenario_name}` simulation.",
            f"The {forcing_label} should {spec.aerchem_setup_source}.",
            f"All other forcings should evolve as in `{spec.base_scenario_name}`.",
            f"`{experiment_name}` is for models that {chemistry_capability}.",
        ).strip(),
        forcing_headlines=join_lines(
            f"The `{experiment_name}` experiment is a time-varying forcings experiment,",
            f"combining {forcing_label} from {spec.aerchem_versions_source}",
            f"with all other forcings from the `{spec.base_scenario_name}` simulation.",
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=join_blocks(
            join_lines(
                f"For {forcing_label},",
                f"the relevant forcing is the same as for {spec.aerchem_versions_source}.",
            ),
            join_lines(
                "For all other forcings,",
                "the forcing versions relevant for this simulation are the same as for "
                f"the `{spec.base_scenario_name}` simulation.",
            ),
        ).strip(),
        getting_the_data=render_data_access_body(
            experiment_name=experiment_name,
            source_ids=source_ids_for_scen7_aerchem_variant(
                aerchem_forcing_versions=spec.aerchem_forcing_versions,
                base_forcing_versions=spec.base_forcing_versions,
            ),
        ),
    )


AERCHEMMIP_EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    make_piclim_historical_forcing_variant_page(
        slug="piclim-ch4",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="greenhouse-gas-concentrations",
                label="methane concentrations or emissions (as appropriate for the model)",
            ),
        ),
    ),
    make_piclim_historical_forcing_variant_page(
        slug="piclim-n2o",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="greenhouse-gas-concentrations",
                label="nitrous oxide concentrations or emissions (as appropriate for the model)",
            ),
        ),
    ),
    make_piclim_historical_forcing_variant_page(
        slug="piclim-nox",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="anthropogenic-emissions",
                label="nitrogen oxides (NOx) emissions",
            ),
        ),
    ),
    make_piclim_historical_forcing_variant_page(
        slug="piclim-ods",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="greenhouse-gas-concentrations",
                label="ozone-depleting substance concentrations",
            ),
        ),
    ),
    make_piclim_historical_forcing_variant_page(
        slug="piclim-so2",
        historical_forcings=(
            HistoricalForcing(
                forcing_id="anthropogenic-emissions",
                label="sulfur dioxide (SO<sub>2</sub>) emissions",
            ),
        ),
    ),
    ExperimentPage(
        slug="hist-piaer",
        experiment_setup=join_blocks(
            # TODO: remove this
            "<!-- TODO: check this with someone who knows what they're reading -->",
            # TODO: Get this from esgvoc instead
            block(
                """
                The `hist-piAer` simulation is a simple variant of the [historical simulation](./historical.md)
                where aerosol and tropospheric non-methane ozone precursor emissions are kept at pre-industrial levels.
                `hist-piAer` is for models that do not include interactive chemistry.
                """
            ),
        ).strip(),
        parent_experiment_extra=(
            "This branch time should match the branch time used for "
            f"initialising the {HISTORICAL_LINK}."
        ),
        forcing_headlines=block(
            """
            The `hist-piAer` experiment is a time-varying forcings experiment,
            except for aerosol and tropospheric non-methane ozone precursor emissions which should be fixed.
            """
        ),
        notes=f"See notes for the {PI_CONTROL_LINK} and {HISTORICAL_LINK}.",
        versions_to_use=join_blocks(
            join_lines(
                "For aerosol and tropospheric non-methane ozone precursor emissions",
                f"the relevant forcing is the same as for the {PI_CONTROL_LINK}.",
            ),
            join_lines(
                "For all other forcings,",
                f"the forcing versions relevant for this simulation are the same as for the {HISTORICAL_LINK}.",
            ),
        ).strip(),
        getting_the_data=render_data_access_body(
            experiment_name="hist-piAer",
            source_ids=source_ids_for_cmip_forcing_combination(
                fixed_forcing_ids=("anthropogenic-emissions",),
                transient_forcing_ids=cmip_forcing_ids_except(
                    "anthropogenic-emissions",
                    "aerosol-optical-properties",
                ),
            ),
        ),
    ),
    ExperimentPage(
        slug="hist-piaq",
        experiment_setup=join_blocks(
            # TODO: remove this
            "<!-- TODO: check this with someone who knows what they're reading -->",
            # TODO: Get this from esgvoc instead
            block(
                """
                The `hist-piAQ` simulation is a simple variant of the [historical simulation](./historical.md)
                where aerosol and tropospheric non-methane ozone precursor emissions are kept at pre-industrial levels.
                `hist-piAQ` is for models that include interactive chemistry.
                """
            ),
        ).strip(),
        parent_experiment_extra=(
            "This branch time should match the branch time used for "
            f"initialising the {HISTORICAL_LINK}."
        ),
        forcing_headlines=block(
            """
            The `hist-piAQ` experiment is a time-varying forcings experiment,
            except for aerosol and tropospheric non-methane ozone precursor emissions which should be fixed.
            """
        ),
        notes=f"See notes for the {PI_CONTROL_LINK} and {HISTORICAL_LINK}.",
        versions_to_use=join_blocks(
            join_lines(
                "For aerosol and tropospheric non-methane ozone precursor emissions",
                f"the relevant forcing is the same as for the {PI_CONTROL_LINK}.",
            ),
            join_lines(
                "For all other forcings,",
                f"the forcing versions relevant for this simulation are the same as for the {HISTORICAL_LINK}.",
            ),
        ).strip(),
        getting_the_data=render_data_access_body(
            experiment_name="hist-piAQ",
            source_ids=source_ids_for_cmip_forcing_combination(
                fixed_forcing_ids=("anthropogenic-emissions",),
                transient_forcing_ids=cmip_forcing_ids_except(
                    "anthropogenic-emissions",
                    "aerosol-optical-properties",
                ),
            ),
        ),
    ),
    make_scen7_aerchem_page(
        Scen7AerChemPageSpec(
            slug="scen7-h-aer",
            base_scenario_name="scen7-h",
            aerchem_setup_source=historical_end_year_setup_source(),
            aerchem_versions_source=historical_end_year_versions_source(),
            aerchem_forcing_versions=CMIP_FORCING_VERSIONS,
            base_forcing_versions=SCEN7_H_FORCING_VERSIONS,
            include_interactive_chemistry=False,
        )
    ),
    make_scen7_aerchem_page(
        Scen7AerChemPageSpec(
            slug="scen7-h-aq",
            base_scenario_name="scen7-h",
            aerchem_setup_source=historical_end_year_setup_source(),
            aerchem_versions_source=historical_end_year_versions_source(),
            aerchem_forcing_versions=CMIP_FORCING_VERSIONS,
            base_forcing_versions=SCEN7_H_FORCING_VERSIONS,
            include_interactive_chemistry=True,
        )
    ),
    make_scen7_aerchem_page(
        Scen7AerChemPageSpec(
            slug="scen7-vl-aer",
            base_scenario_name="scen7-vl",
            aerchem_setup_source="evolve as in the `scen7-h` simulation",
            aerchem_versions_source="the `scen7-h` simulation",
            aerchem_forcing_versions=SCEN7_H_FORCING_VERSIONS,
            base_forcing_versions=SCEN7_VL_FORCING_VERSIONS,
            include_interactive_chemistry=False,
        )
    ),
    make_scen7_aerchem_page(
        Scen7AerChemPageSpec(
            slug="scen7-vl-aq",
            base_scenario_name="scen7-vl",
            aerchem_setup_source="evolve as in the `scen7-h` simulation",
            aerchem_versions_source="the `scen7-h` simulation",
            aerchem_forcing_versions=SCEN7_H_FORCING_VERSIONS,
            base_forcing_versions=SCEN7_VL_FORCING_VERSIONS,
            include_interactive_chemistry=True,
        )
    ),
)
