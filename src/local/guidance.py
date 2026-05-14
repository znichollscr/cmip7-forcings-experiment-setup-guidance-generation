"""Generate CMIP7 experiment setup and forcings guidance pages."""

from __future__ import annotations

import json
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Union

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT.parent
    / "cmip7-guidance"
    / "docs"
    / "CMIP7"
    / "Experiment_set_up_and_Forcings"
)

ForcingValue = Union[Sequence[str], str, None]


@dataclass(frozen=True)
class CheckResult:
    """The result of comparing rendered pages with files on disk."""

    missing: tuple[Path, ...]
    changed: tuple[Path, ...]
    extra: tuple[Path, ...]

    @property
    def ok(self) -> bool:
        """Whether the generated output matches the files on disk."""
        return not self.missing and not self.changed and not self.extra


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


@dataclass(frozen=True)
class ExperimentPage:
    """A full experiment setup and forcings guidance page."""

    slug: str
    title: str
    display_name: str
    responsible_activity: str
    description: str
    experiment_setup: str
    parent_experiment: str
    forcing_headlines: str
    notes: str
    versions_to_use: str
    getting_the_data: str
    pre_description_note: str = ""

    def render(self) -> str:
        """Render the page as markdown."""
        return join_blocks(
            render_front_matter(self.title),
            f"# {self.title}",
            ESGVOC_ACTIVITY_TODO,
            f"Responsible activity: {self.responsible_activity}",
            self.pre_description_note,
            ESGVOC_DESCRIPTION_TODO,
            self.description,
            "## Experiment set up",
            self.experiment_setup,
            "### Parent experiment",
            PARENT_EXPERIMENT_TODO,
            self.parent_experiment,
            "## Forcings",
            "### General headlines",
            self.forcing_headlines,
            "### Notes",
            self.notes,
            "### Versions to use",
            self.versions_to_use,
            "### Getting the data",
            self.getting_the_data,
        )


@dataclass(frozen=True)
class SimplePage:
    """A markdown page with front matter and a body."""

    slug: str
    title: str
    display_name: str
    body: str
    front_matter_title: str | None = None

    def render(self) -> str:
        """Render the page as markdown."""
        return join_blocks(
            render_front_matter(self.front_matter_title or self.title),
            f"# {self.title}",
            self.body,
        )


@dataclass(frozen=True)
class IndexActivity:
    """A MIP/activity entry on the guidance index page."""

    heading: str
    description: str
    experiment_slugs: tuple[str, ...]
    extra_markdown: str = ""


@dataclass(frozen=True)
class IndexGroup:
    """A group of activities on the guidance index page."""

    heading: str
    activities: tuple[IndexActivity, ...]


def block(text: str) -> str:
    """Return a dedented markdown block without surrounding blank lines."""
    return dedent(text).strip("\n")


def join_blocks(*parts: str) -> str:
    """Join markdown blocks with one blank line and a trailing newline."""
    return "\n\n".join(part.strip("\n") for part in parts if part.strip()) + "\n"


def join_lines(*parts: str) -> str:
    """Join markdown lines without paragraph breaks."""
    return "\n".join(part.strip("\n") for part in parts if part.strip())


def render_front_matter(title: str) -> str:
    """Render Jekyll front matter for a guidance page."""
    return block(
        f"""
        ---
        layout: default
        title: {title}
        ---
        """
    )


def render_link(label: str, slug: str) -> str:
    """Render a relative markdown link to another generated page."""
    return f"[{label}](./{slug}.md)"


def render_forcing_reference_list(
    forcing_references: Sequence[ForcingReference],
) -> str:
    """Render the list of forcing reference pages."""
    lines = ["The following pages give further information on each forcing:"]
    lines.extend(
        f"- {reference.label}: [{reference.display_url}]({reference.url})"
        for reference in forcing_references
    )
    return "\n\n".join((lines[0], "\n".join(lines[1:])))


def render_forcing_value(value: ForcingValue) -> str:
    """Render one forcing version value in compact JSON style."""
    if value is None:
        return "null"

    if isinstance(value, str):
        return json.dumps(value)

    return f"[{', '.join(json.dumps(item) for item in value)}]"


def render_versions_json(forcing_versions: Mapping[str, ForcingValue]) -> str:
    """Render forcing versions as a JSON code block."""
    lines = ["```json", "{"]
    forcing_items = tuple(forcing_versions.items())

    for index, (forcing_id, value) in enumerate(forcing_items):
        comma = "," if index < len(forcing_items) - 1 else ""
        lines.append(
            f"    {json.dumps(forcing_id)}: {render_forcing_value(value)}{comma}"
        )

    lines.extend(("}", "```"))
    return "\n".join(lines)


def render_versions_body(
    forcing_versions: Mapping[str, ForcingValue],
    *,
    include_multiple_options_note: bool = True,
) -> str:
    """Render the standard forcing versions section body."""
    multiple_options_note = ""
    if include_multiple_options_note:
        multiple_options_note = block(
            """
            Where there is more than one source ID listed,
            this either indicates that you may need data from multiple source IDs
            or that multiple options are acceptable
            (because, e.g., fixes were made but re-running is not required).
            Please see the guidance pages linked above for details.
            """
        )

    return join_blocks(
        block(
            """
            The forcings relevant for this simulation are listed below.
            For each forcing, we provide the version(s), in the form of "source ID(s)",
            which should be used when running this simulation.
            """
        ),
        multiple_options_note,
        render_versions_json(forcing_versions),
    ).strip()


NON_DOWNLOADABLE_FORCING_VALUES = {"not-available-yet"}


def source_ids_from_forcing_versions(
    *forcing_versions: Mapping[str, ForcingValue],
    source_id_indexes: Mapping[str, int] | None = None,
) -> tuple[str, ...]:
    """Derive ESGF-downloadable source IDs from forcing-version mappings."""
    source_id_indexes = source_id_indexes or {}
    source_ids: list[str] = []
    seen: set[str] = set()

    for forcing_version in forcing_versions:
        for forcing_id, value in forcing_version.items():
            if value is None:
                continue

            if isinstance(value, str):
                selected_source_ids = (
                    () if value in NON_DOWNLOADABLE_FORCING_VALUES else (value,)
                )
            elif forcing_id in source_id_indexes:
                selected_source_ids = (value[source_id_indexes[forcing_id]],)
            else:
                selected_source_ids = tuple(value)

            for source_id in selected_source_ids:
                if source_id in seen:
                    continue

                source_ids.append(source_id)
                seen.add(source_id)

    return tuple(source_ids)


def render_data_access_body(
    *,
    experiment_name: str,
    source_ids: Sequence[str],
) -> str:
    """Render the standard data-access section body."""
    return join_blocks(
        DATA_ACCESS_INTRO,
        block(
            """
            If you install [esgpull](https://esgf.github.io/esgf-download/),
            you can download all the data associated with the source IDs above with the script shown below.
            Note that this will download all the data associated with these source IDs,
            which is likely to be much more data than you actually need to run your model.
            """
        ),
        render_esgpull_script(experiment_name=experiment_name, source_ids=source_ids),
    ).strip()


def render_esgpull_script(
    *,
    experiment_name: str,
    source_ids: Sequence[str],
) -> str:
    """Render an esgpull download script for source IDs."""
    source_id_query = ",".join(source_ids)
    return block(
        f"""
        ```bash
        #!/bin/bash

        EXPERIMENT_NAME="{experiment_name}"

        esgpull add --track --tag ${{EXPERIMENT_NAME}} source_id:{source_id_query}
        esgpull update --tag ${{EXPERIMENT_NAME}} --yes
        esgpull download --tag ${{EXPERIMENT_NAME}}
        ```
        """
    )


def branch_from(
    *,
    experiment: str,
    parent: str,
    parent_activity: str,
    branch_instruction: str,
    extra: str = "",
) -> str:
    """Render parent-experiment branch information."""
    return join_blocks(
        (
            f"`{experiment}` branches from the `{parent}` simulation "
            f"(part of `{parent_activity}`)."
        ),
        branch_instruction,
        extra,
    ).strip()


ESGVOC_ACTIVITY_TODO = (
    "<!-- TODO: get this information from esgvoc "
    "(add reference URLs at that point) -->"
)
ESGVOC_DESCRIPTION_TODO = "<!-- TODO: get this one line description from esgvoc -->"
SETUP_GENERATION_TODO = (
    "<!-- TODO: consider whether we can generate these sentences automatically "
    "based on esgvoc -->"
)
EXPERIMENT_NAME_CONVENTION_TODO = (
    "<!-- TODO: decide and then consistently apply some convention about whether "
    "experiment names are always surround by backticks `` or not -->"
)
PARENT_EXPERIMENT_TODO = block(
    """
    <!--
        TODO: use esgvoc to fill out the template
        `<experiment-name>` branches from the `<parent-experiment-name>` simulation (part of `<parent-experiment-activity>`).
    -->
    """
)
PICLIM_PARENT_TODO = "<!-- TODO: check if there is meant to be a spinup -->"

PI_CONTROL_LINK = render_link("piControl simulation", "picontrol")
ESM_PI_CONTROL_LINK = render_link("esm-piControl simulation", "esm-picontrol")
HISTORICAL_LINK = render_link("historical simulation", "historical")
ONEPCTCO2_LINK = render_link("1pctCO2 simulation", "1pctco2")
PI_CLIM_CONTROL_LINK = render_link("piClim-control simulation", "piclim-control")
ABRUPT_4XCO2_LINK = render_link("abrupt-4xCO2 simulation", "abrupt-4xco2")

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

CMIP_FORCING_VERSIONS = OrderedDict(
    (
        (
            "anthropogenic-emissions",
            ("CEDS-CMIP-2025-04-18", "CEDS-CMIP-2025-04-18-supplemental"),
        ),
        ("biomass-burning-emissions", ("DRES-CMIP-BB4CMIP7-2-0",)),
        ("land-use", ("UofMD-landState-3-1-1",)),
        ("greenhouse-gas-concentrations", ("CR-CMIP-1-0-0",)),
        ("stratospheric-aerosol-forcing", ("UOEXETER-CMIP-2-2-1",)),
        ("ozone", ("FZJ-CMIP-ozone-1-2", "FZJ-CMIP-ozone-2-0")),
        ("nitrogen-deposition", ("FZJ-CMIP-nitrogen-1-2", "FZJ-CMIP-nitrogen-2-0")),
        ("solar", ("SOLARIS-HEPPA-CMIP-4-6",)),
        ("aerosol-optical-properties", None),
        ("population-density", ("PIK-CMIP-1-0-1",)),
    )
)

CMIP_FIXED_SOURCE_ID_INDEXES = {
    "nitrogen-deposition": 0,
    "ozone": 0,
}

CMIP_TRANSIENT_SOURCE_ID_INDEXES = {
    "nitrogen-deposition": 0,
    "ozone": 1,
}

SCEN7_VL_FORCING_VERSIONS = OrderedDict(
    (
        ("anthropogenic-emissions", ("IIASA-IAMC-vl-1-0-0",)),
        ("biomass-burning-emissions", ("IIASA-IAMC-vl-1-0-0",)),
        ("land-use", "not-available-yet"),
        ("greenhouse-gas-concentrations", ("CR-vl-1-0-0",)),
        ("stratospheric-aerosol-forcing", ("UOEXETER-ScenarioMIP-2-2-2",)),
        ("ozone", "not-available-yet"),
        ("nitrogen-deposition", "not-available-yet"),
        ("solar", ("SOLARIS-HEPPA-ScenarioMIP-4-6",)),
        ("aerosol-optical-properties", None),
        ("population-density", ("PIK-vl-1-0-0",)),
    )
)

AMIP_FORCING_VERSIONS = OrderedDict(
    (
        (
            "amip-sea-surface-temperature-and-sea-ice-boundary-forcing",
            ("PCMDI-AMIP-1-1-10",),
        ),
    )
)

DATA_ACCESS_INTRO = block(
    """
    The data is available on ESGF and searchable [via metagrid](https://esgf-node.ornl.gov/search?project=input4MIPs&versionType=all&activeFacets=%7B%22mip_era%22%3A%22CMIP7%22%7D),
    although this method of finding and downloading the data can involve a lot of clicking.
    Having said this, please also note: the aerosol optical properties based on the MACv2-SP parameterisation are not distributed via the ESGF.
    <!-- TODO: add CI to check all URLs are live -->
    Please see [their specific guidance section](https://input4mips-cvs.readthedocs.io/en/latest/dataset-overviews/aerosol-optical-properties-macv2-sp/#datasets-for-cmip7-phases)
    for data access information.
    """
)

COMMON_FORCING_NOTES = render_forcing_reference_list(COMMON_FORCING_REFERENCES)

TIME_AXIS_CAN_BE_ARBITRARY = block(
    """
    The start-time of the simulation is not tied to a particular year but, rather, can be chosen arbitrarily
    (e.g., year 200 or year 1850 or year 1).
    However, it is easier for analysts if the start-time is consistent with the branching time in the parent experiment
    (e.g., if the the simulation branches from year 200 in the parent experiment,
    then the start time in the child experiment would be set to year 200).
    """
)

PICLIM_TIME_AXIS = block(
    """
    It is recommended that you use the same time axis as you use for your [piClim-control](./piclim-control.md) output
    to make life easy for analysts of your output
    (although this is not enforced so you are technically free to start the time axis of your outputs at whatever year you like).
    Simulations should be at least 30 years in length.
    Only one ensemble member is required.
    """
)

AERCHEMMIP_UNCERTAIN_NOTE = block(
    """
    Note, the information on this page is likely not correct.
    We are awaiting documentation of the forcings for the AerChemMIP CMIP7 AFT experiments.
    Some details may be available in [Fiedler et al](https://doi.org/10.5194/egusphere-2025-5669) (preprint)
    and information on AerChemMIP can be found via the [CMIP IPO website](https://wcrp-cmip.org/mips/aerchemmip2/).
    Please see [issue #124](https://github.com/WCRP-CMIP/cmip7-guidance/issues/124)
    to track progress resolving this.
    """
)

AERCHEMMIP_PLACEHOLDER_NOTE = block(
    """
    Note, the information to put on this page is still being clarified.
    We are awaiting documentation of the forcings for the AerChemMIP CMIP7 AFT experiments.
    Some details may be available in [Fiedler et al](https://doi.org/10.5194/egusphere-2025-5669) (preprint)
    and information on AerChemMIP can be found via the [CMIP IPO website](https://wcrp-cmip.org/mips/aerchemmip2/).
    Please see [issue #124](https://github.com/WCRP-CMIP/cmip7-guidance/issues/124)
    to track progress resolving this.
    """
)


def same_as_versions(label: str, slug: str) -> str:
    """Render a short versions section for experiments sharing another setup."""
    return (
        "The forcings relevant for this simulation are the same as for the "
        f"{render_link(label, slug)}."
    )


def see_instructions(label: str, slug: str, extra: str = "") -> str:
    """Render a short data-access section that points to another page."""
    return join_blocks(
        f"See instructions for the {render_link(label, slug)}.", extra
    ).strip()


def make_piclim_variant_page(
    *,
    slug: str,
    title: str,
    display_name: str,
    description: str,
    forcing_change: str,
    version_forcing_label: str,
    responsible_activity: str = "AerChemMIP",
) -> ExperimentPage:
    """Create a piClim present-day forcing variant page."""
    return ExperimentPage(
        slug=slug,
        title=title,
        display_name=display_name,
        responsible_activity=responsible_activity,
        description=description,
        experiment_setup=join_blocks(
            join_lines(
                (
                    f"The {display_name} simulation uses the same forcings as "
                    "[piClim-control](./piclim-control.md),"
                ),
                forcing_change,
            ),
            "The 2021 values should be prescribed on repeat throughout the simulation.",
            SETUP_GENERATION_TODO,
            PICLIM_TIME_AXIS,
        ).strip(),
        parent_experiment=join_blocks(
            PICLIM_PARENT_TODO,
            f"`{display_name}` does not branch from another simulation.",
        ).strip(),
        forcing_headlines=(
            "See general headlines for the "
            "[`piClim-control` simulation](./piclim-control.md)."
        ),
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK}.",
        versions_to_use=join_blocks(
            join_lines(
                f"For the {version_forcing_label},",
                f"the forcing version relevant for this simulation is the same as for the {HISTORICAL_LINK}.",
            ),
            join_lines(
                "For all other forcings,",
                f"the forcing versions relevant for this simulation are the same as for the {PI_CLIM_CONTROL_LINK}.",
            ),
        ).strip(),
        getting_the_data=f"See instructions for the {PI_CLIM_CONTROL_LINK} and {HISTORICAL_LINK}.",
    )


EXPERIMENT_PAGES: tuple[ExperimentPage, ...] = (
    ExperimentPage(
        slug="picontrol",
        title="piControl Experiment Setup and Forcings Guidance",
        display_name="piControl",
        responsible_activity="CMIP",
        description=(
            "Pre-industrial control simulation with prescribed carbon dioxide "
            "concentrations (for prescribed carbon dioxide emissions, see "
            "`esm-piControl`). Used to characterise natural variability and "
            "unforced behaviour."
        ),
        experiment_setup=join_blocks(
            "The pre-industrial control simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied on repeat for the entirety of the simulation.",
            SETUP_GENERATION_TODO,
            block(
                """
                You are free to start the time axis of your outputs at whatever year you like
                (e.g. starting at year 1, or 1850, or year 500).
                Simulations should be at least 400 years in length.
                Only one ensemble member is required.
                """
            ),
        ).strip(),
        parent_experiment=branch_from(
            experiment="piControl",
            parent="piControl-spinup",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl-spinup` at a time of your choosing.",
        ),
        forcing_headlines=block(
            """
            The `piControl` experiment is a fixed forcings experiment.
            However, it can require some care to use the correct forcings for `piControl`.
            This is particularly true for stratospheric aerosol forcing, ozone and solar
            as the `piControl` values for these forcings aren't simply a repeat of 1850 values.
            Please read the guidance pages linked under [notes](#notes)
            to ensure that you use the correct forcing values.
            """
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=render_versions_body(CMIP_FORCING_VERSIONS),
        getting_the_data=render_data_access_body(
            experiment_name="piControl",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_FIXED_SOURCE_ID_INDEXES,
            ),
        ),
    ),
    ExperimentPage(
        slug="esm-picontrol",
        title="esm-piControl Experiment Setup and Forcings Guidance",
        display_name="esm-piControl",
        responsible_activity="CMIP",
        description=(
            "Pre-industrial control simulation with prescribed carbon dioxide "
            "emissions (for prescribed carbon dioxide concentrations, see "
            "`piControl`). Used to characterise natural variability and "
            "unforced behaviour."
        ),
        experiment_setup=join_blocks(
            "The emissions-driven pre-industrial control simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied on repeat for the entirety of the simulation.",
            SETUP_GENERATION_TODO,
            block(
                """
                You are free to start the time axis of your outputs at whatever year you like
                (e.g. starting at year 1, or 1850, or year 500).
                Simulations should be at least 400 years in length.
                Only one ensemble member is required.
                """
            ),
        ).strip(),
        parent_experiment=branch_from(
            experiment="esm-piControl",
            parent="esm-piControl-spinup",
            parent_activity="CMIP",
            branch_instruction=(
                "Branch from `esm-piControl-spinup` at a time of your choosing."
            ),
        ),
        forcing_headlines=block(
            """
            The `esm-piControl` experiment is a fixed forcings experiment.
            However, it can require some care to use the correct forcings for `esm-piControl`.
            This is particularly true for stratospheric aerosol forcing, ozone and solar
            as the `esm-piControl` values for these forcings aren't simply a repeat of 1850 values.
            Please read the guidance pages linked under [notes](#notes)
            to ensure that you use the correct forcing values.
            """
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=render_versions_body(CMIP_FORCING_VERSIONS),
        getting_the_data=render_data_access_body(
            experiment_name="esm-piControl",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_FIXED_SOURCE_ID_INDEXES,
            ),
        ),
    ),
    ExperimentPage(
        slug="historical",
        title="historical Experiment Setup and Forcings Guidance",
        display_name="historical",
        responsible_activity="CMIP",
        description=(
            "Simulation of the climate of the recent past (typically meaning "
            "1850 to present-day) with prescribed carbon dioxide concentrations "
            "(for prescribed carbon dioxide emissions, see `esm-hist`)."
        ),
        experiment_setup=join_blocks(
            "The historical simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation.",
            SETUP_GENERATION_TODO,
            "The simulation output should start on 1850-01-01 and end on 2021-12-31.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="historical",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
        ),
        forcing_headlines=block(
            """
            The `historical` experiment is a time-varying forcings experiment.
            Please note that the ozone forcing should come from files with the source ID `FZJ-CMIP-ozone-2-0`.
            `FZJ-CMIP-ozone-2-0` was released quite late, so if you have simulations based on `FZJ-CMIP-ozone-1-2`,
            these would also be of interest to the Forcings Task Team so please publish them
            ([discussion of how to set the value for the forcing 'f' identifier in such files is ongoing](https://github.com/PCMDI/input4MIPs_CVs/issues/415)).
            """
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=render_versions_body(CMIP_FORCING_VERSIONS),
        getting_the_data=render_data_access_body(
            experiment_name="historical",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_TRANSIENT_SOURCE_ID_INDEXES,
            ),
        ),
    ),
    ExperimentPage(
        slug="esm-hist",
        title="esm-hist Experiment Setup and Forcings Guidance",
        display_name="esm-hist",
        responsible_activity="CMIP",
        description=(
            "Simulation of the climate of the recent past (typically meaning "
            "1850 to present-day) with prescribed carbon dioxide emissions "
            "(for prescribed carbon dioxide concentrations, see `historical`)."
        ),
        experiment_setup=join_blocks(
            "The emissions-driven historical simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation.",
            SETUP_GENERATION_TODO,
            "The simulation output should start on 1850-01-01 and end on 2021-12-31.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="esm-hist",
            parent="esm-piControl",
            parent_activity="CMIP",
            branch_instruction=(
                "Branch from `esm-piControl` at a time of your choosing."
            ),
        ),
        forcing_headlines=block(
            """
            The `esm-hist` experiment is a time-varying forcings experiment.
            Please note that the ozone forcing should come from files with the source ID `FZJ-CMIP-ozone-2-0`.
            `FZJ-CMIP-ozone-2-0` was released quite late, so if you have simulations based on `FZJ-CMIP-ozone-1-2`,
            these would also be of interest to the Forcings Task Team so please publish them
            ([discussion of how to set the value for the forcing 'f' identifier in such files is ongoing](https://github.com/PCMDI/input4MIPs_CVs/issues/415)).
            """
        ),
        notes=COMMON_FORCING_NOTES,
        versions_to_use=render_versions_body(CMIP_FORCING_VERSIONS),
        getting_the_data=render_data_access_body(
            experiment_name="esm-hist",
            source_ids=source_ids_from_forcing_versions(
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_TRANSIENT_SOURCE_ID_INDEXES,
            ),
        ),
    ),
    ExperimentPage(
        slug="1pctco2",
        title="1pctCO2 Experiment Setup and Forcings Guidance",
        display_name="1pctCO2",
        responsible_activity="CMIP",
        description=(
            "1% per year increase in atmospheric carbon dioxide levels. "
            "All other conditions are kept the same as piControl."
        ),
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The 1pctCO2 simulation is a simple branch from the {PI_CONTROL_LINK}.",
            "After branching, the atmospheric CO<sub>2</sub> concentrations should increase at one percent per year throughout the simulation.",
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
            "Simulations should be at least 150 years in length.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="1pctCO2",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
        ),
        forcing_headlines=(
            "The `1pctCO2` experiment is a fixed forcings experiment, "
            "except for CO<sub>2</sub> which is transient."
        ),
        notes=f"See notes for the {PI_CONTROL_LINK}.",
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=join_blocks(
            see_instructions("piControl simulation", "picontrol"),
            "You have to increase the atmospheric CO<sub>2</sub> concentrations at one percent per year yourself.",
            block(
                """
                <!---
                    TODO: discuss with Matt/someone else the specific implementation instructions.
                    Set concentrations in first year to be higher than piControl
                    (because, if you don't do this and you have a linear increase,
                    then you'd have to drop concentrations in January of the first year in order to get the average correct)
                    TODO: check formula rendering
                -->
                The annual-average concentrations should increase following the formula c(y) = c_0 * 1.01 ** (y - y_0 - 1),
                where c is the annual-average concentration in year y and y_0 is the first year of the `1pctCO2` simulation
                (i.e. average atmospheric CO<sub>2</sub> concentrations in the first year of the `1pctCO2` simulation
                should be higher than in `piControl`).
                It is up to you to decide whether you apply your concentrations as a series of step changes
                (constant over each year) or as a steady linear increase
                (such that e.g. concentrations in December are higher than those in January)
                that results in the correct annual average being applied.
                """
            ),
        ).strip(),
    ),
    ExperimentPage(
        slug="1pctco2-bgc",
        title="1pctCO2-bgc Experiment Setup and Forcings Guidance",
        display_name="1pctCO2-bgc",
        responsible_activity="C4MIP",
        description=(
            "Biogeochemically coupled simulation (i.e. the carbon cycle only "
            "'sees' the increase in atmospheric carbon dioxide, not any change "
            "in temperature) of a 1% per year increase in atmospheric carbon "
            "dioxide levels. All other conditions are kept the same as piControl."
        ),
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The 1pctCO2-bgc simulation has the same forcing setup as the {ONEPCTCO2_LINK}.",
            block(
                """
                The difference is that your model should be configured such that the carbon cycle
                only sees the change in atmospheric CO<sub>2</sub> concentrations
                and does not see any other changes (e.g. changes in atmospheric temperatures).
                """
            ),
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
            "Simulations should be at least 150 years in length.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="1pctCO2-bgc",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
        ),
        forcing_headlines=f"See general headlines for the {ONEPCTCO2_LINK}.",
        notes=f"See notes for the {ONEPCTCO2_LINK}.",
        versions_to_use=same_as_versions("1pctCO2 simulation", "1pctco2"),
        getting_the_data=see_instructions("1pctCO2 simulation", "1pctco2"),
    ),
    ExperimentPage(
        slug="1pctco2-rad",
        title="1pctCO2-rad Experiment Setup and Forcings Guidance",
        display_name="1pctCO2-rad",
        responsible_activity="C4MIP",
        description=(
            "Radiatively coupled simulation (i.e. the carbon cycle only 'sees' "
            "the increase in temperature, not any change in atmospheric carbon "
            "dioxide) of a 1% per year increase in atmospheric carbon dioxide "
            "levels. All other conditions are kept the same as piControl."
        ),
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The 1pctCO2-rad simulation has the same forcing setup as the {ONEPCTCO2_LINK}.",
            block(
                """
                The difference is that your model should be configured such that the carbon cycle
                only sees the change in radiation
                and does not see any other changes (e.g. changes in atmospheric CO<sub>2</sub> concentrations).
                """
            ),
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
            "Simulations should be at least 150 years in length.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="1pctCO2-rad",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
        ),
        forcing_headlines=f"See general headlines for the {ONEPCTCO2_LINK}.",
        notes=f"See notes for the {ONEPCTCO2_LINK}.",
        versions_to_use=same_as_versions("1pctCO2 simulation", "1pctco2"),
        getting_the_data=see_instructions("1pctCO2 simulation", "1pctco2"),
    ),
    ExperimentPage(
        slug="abrupt-4xco2",
        title="abrupt-4xCO2 Experiment Setup and Forcings Guidance",
        display_name="abrupt-4xCO2",
        responsible_activity="CMIP",
        description=(
            "Abrupt quadrupling of atmospheric carbon dioxide levels. "
            "All other conditions are kept the same as piControl."
        ),
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The abrupt CO<sub>2</sub> quadrupling simulation is a simple branch from the {PI_CONTROL_LINK}.",
            block(
                """
                After branching, the atmospheric CO<sub>2</sub> concentrations should be set to four times
                the concentrations used in the `piControl` simulation.
                """
            ),
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
            "Simulations should be at least 300 years in length.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="abrupt-4xCO2",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
        ),
        forcing_headlines=(
            "The `abrupt-4xCO2` experiment is a fixed forcings experiment.\n"
            f"For further general headlines, please see the general headlines for the {PI_CONTROL_LINK}."
        ),
        notes=f"See notes for the {PI_CONTROL_LINK}.",
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=join_blocks(
            see_instructions("piControl simulation", "picontrol"),
            "You have to quadruple the atmospheric CO<sub>2</sub> concentrations yourself.",
        ).strip(),
    ),
    ExperimentPage(
        slug="abrupt-2xco2",
        title="abrupt-2xCO2 Experiment Setup and Forcings Guidance",
        display_name="abrupt-2xCO2",
        responsible_activity="CFMIP",
        description=(
            "Abrupt doubling of atmospheric carbon dioxide levels. "
            "All other conditions are kept the same as piControl."
        ),
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The abrupt CO<sub>2</sub> doubling simulation is a simple branch from the {PI_CONTROL_LINK}.",
            block(
                """
                After branching, the atmospheric CO<sub>2</sub> concentrations should be set to two times
                the concentrations used in the `piControl` simulation.
                """
            ),
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
            "Simulations should be at least 300 years in length.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="abrupt-2xCO2",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
        ),
        forcing_headlines=f"See general headlines for the {ABRUPT_4XCO2_LINK}.",
        notes=f"See notes for the {PI_CONTROL_LINK}.",
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=join_blocks(
            see_instructions("piControl simulation", "picontrol"),
            "You have to double the atmospheric CO<sub>2</sub> concentrations yourself.",
        ).strip(),
    ),
    ExperimentPage(
        slug="abrupt-0p5xco2",
        title="abrupt-0p5xCO2 Experiment Setup and Forcings Guidance",
        display_name="abrupt-0p5xCO2",
        responsible_activity="CFMIP",
        description=(
            "Abrupt halving of atmospheric carbon dioxide levels. "
            "All other conditions are kept the same as piControl."
        ),
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            f"The abrupt CO<sub>2</sub> halving simulation is a simple branch from the {PI_CONTROL_LINK}.",
            block(
                """
                After branching, the atmospheric CO<sub>2</sub> concentrations should be set to half
                the concentrations used in the `piControl` simulation.
                """
            ),
            SETUP_GENERATION_TODO,
            TIME_AXIS_CAN_BE_ARBITRARY,
            "Simulations should be at least 300 years in length.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="abrupt-0p5xCO2",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
        ),
        forcing_headlines=f"See general headlines for the {ABRUPT_4XCO2_LINK}.",
        notes=f"See notes for the {PI_CONTROL_LINK}.",
        versions_to_use=same_as_versions("piControl simulation", "picontrol"),
        getting_the_data=join_blocks(
            see_instructions("piControl simulation", "picontrol"),
            "You have to halve the atmospheric CO<sub>2</sub> concentrations yourself.",
        ).strip(),
    ),
    ExperimentPage(
        slug="piclim-control",
        title="piClim-control Experiment Setup and Forcings Guidance",
        display_name="piClim-control",
        responsible_activity="CMIP",
        description=(
            "Baseline for effective radiative forcing (ERF) calculations. "
            "`piControl` with prescribed sea-surface temperatures and sea-ice "
            "concentrations."
        ),
        experiment_setup=join_blocks(
            join_lines(
                "The piClim-control simulation uses the same forcings as [piControl](./picontrol.md),",
                "with the extra specification that sea-surface temperatures and sea-ice concentrations are prescribed.",
            ),
            block(
                """
                The prescribed sea-surface temperatures and sea-ice concentrations
                must come from a (monthly varying, annually repeating)
                climatology taken from at least 30 years of your [pre-industrial control](./picontrol.md) simulation
                (i.e. these forcings are derived from your model output from one of your own simulations,
                they are not provided by a forcings provider).
                """
            ),
            SETUP_GENERATION_TODO,
            block(
                """
                The start-time of the simulation is not tied to a particular year but, rather, can be chosen arbitrarily
                (e.g., year 200 or year 1850 or year 1).
                If you have no other strong feeling, then it may be clearest to set the start-time
                to be equal to the middle of the period over which the climatology was taken from the pre-industrial control experiment.
                For example, if your climatology is taken over the years 120-150 in the pre-industrial control experiment,
                then you could start the time axis of your `piClim-control` at 135.
                Simulations should be at least 30 years in length.
                Only one ensemble member is required.
                """
            ),
        ).strip(),
        parent_experiment=join_blocks(
            PICLIM_PARENT_TODO,
            "`piClim-control` does not branch from another simulation.",
        ).strip(),
        forcing_headlines=(
            "The `piClim-control` experiment is a fixed forcings experiment.\n"
            f"For further general headlines, please see the general headlines for the {PI_CONTROL_LINK}."
        ),
        notes=f"See notes for the {PI_CONTROL_LINK}.",
        versions_to_use=join_blocks(
            same_as_versions("piControl simulation", "picontrol"),
            block(
                """
                As noted above, the prescribed sea-surface temperatures and sea-ice concentrations
                must come from model output from one of your own simulations,
                they are not provided by a forcings provider.
                We recommend including information in your `piClim-control` output
                that identifies the `piControl` simulation and time period used to generate
                the prescribed sea-surface temperatures and sea-ice concentrations.
                """
            ),
        ).strip(),
        getting_the_data=join_blocks(
            see_instructions("piControl simulation", "picontrol"),
            block(
                """
                As noted above, the prescribed sea-surface temperatures and sea-ice concentrations
                must come from model output from one of your own simulations,
                they are not provided by a forcings provider.
                """
            ),
        ).strip(),
    ),
    ExperimentPage(
        slug="piclim-4xco2",
        title="piClim-4xCO2 Experiment Setup and Forcings Guidance",
        display_name="piClim-4xCO2",
        responsible_activity="CMIP",
        description=(
            "In combination with `piClim-control`, quantifies a quadrupling of "
            "atmospheric carbon dioxide's (4xCO2's) effective radiative forcing "
            "(ERF). Same as `piClim-control`, except atmospheric carbon dioxide "
            "concentrations are set to four times `piControl` levels."
        ),
        experiment_setup=join_blocks(
            join_lines(
                "The piClim-4xCO2 simulation uses the same forcings as [piClim-control](./piclim-control.md),",
                block(
                    """
                    except atmospheric CO<sub>2</sub> concentrations
                    are set to four times the concentrations used in the [piClim-control](./piclim-control.md) simulation.
                    """
                ),
            ),
            SETUP_GENERATION_TODO,
            PICLIM_TIME_AXIS,
        ).strip(),
        parent_experiment=join_blocks(
            PICLIM_PARENT_TODO,
            "`piClim-4xCO2` does not branch from another simulation.",
        ).strip(),
        forcing_headlines=(
            "See general headlines for the "
            "[`piClim-control` simulation](./piclim-control.md)."
        ),
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK}.",
        versions_to_use=same_as_versions("piClim-control simulation", "piclim-control"),
        getting_the_data=join_blocks(
            see_instructions("piClim-control simulation", "piclim-control"),
            "You have to quadruple the atmospheric CO<sub>2</sub> concentrations yourself.",
        ).strip(),
    ),
    ExperimentPage(
        slug="piclim-anthro",
        title="piClim-anthro Experiment Setup and Forcings Guidance",
        display_name="piClim-anthro",
        responsible_activity="CMIP",
        description=block(
            """
            In combination with `piClim-control`, quantifies present-day total anthropogenic effective radiative forcing (ERF).
            Same as `piClim-control`, except all anthropogenic forcings use present-day values
            (in CMIP defined as the last year of the `historical` simulation within the same CMIP era i.e. 2021 values for CMIP7).
            """
        ),
        experiment_setup=join_blocks(
            join_lines(
                "The piClim-anthro simulation uses the same forcings as [piClim-control](./piclim-control.md),",
                "except all anthropogenic forcings use 2021 values.",
            ),
            "The 2021 values should be prescribed on repeat throughout the simulation.",
            block(
                """
                Here, all anthropogenic forcings means all forcings included in the [historical](./historical.md) simulation
                except for solar and stratospheric aerosol forcing
                (these two forcings should remain as in [piClim-control](./piclim-control.md)).
                """
            ),
            SETUP_GENERATION_TODO,
            PICLIM_TIME_AXIS,
        ).strip(),
        parent_experiment=join_blocks(
            PICLIM_PARENT_TODO,
            "`piClim-anthro` does not branch from another simulation.",
        ).strip(),
        forcing_headlines=(
            "See general headlines for the "
            "[`piClim-control` simulation](./piclim-control.md)."
        ),
        notes=f"See notes for the {PI_CLIM_CONTROL_LINK}.",
        versions_to_use=join_blocks(
            join_lines(
                "For natural forcings i.e. solar and stratospheric aerosol forcing,",
                "and the prescribed sea-surface temperatures and sea-ice concentrations",
                f"the relevant forcing is the same as for the {PI_CLIM_CONTROL_LINK}.",
            ),
            join_lines(
                "For all other forcings i.e. anthropogenic forcings,",
                f"the forcing versions relevant for this simulation are the same as for the {HISTORICAL_LINK}.",
            ),
        ).strip(),
        getting_the_data=f"See instructions for the {PI_CLIM_CONTROL_LINK} and {HISTORICAL_LINK}.",
    ),
    make_piclim_variant_page(
        slug="piclim-ch4",
        title="piClim-CH4 Experiment Setup and Forcings Guidance",
        display_name="piClim-CH4",
        description=block(
            """
            In combination with `piClim-control`, quantifies present-day methane effective radiative forcing (ERF).
            Same as `piClim-control`, except methane concentrations or emissions (as appropriate for the model) use present-day values
            (in CMIP defined as the last year of the `historical` simulation within the same CMIP era i.e. 2021 values for CMIP7).
            """
        ),
        forcing_change=(
            "except the atmospheric methane concentration forcing uses 2021 values."
        ),
        version_forcing_label="methane forcing",
    ),
    make_piclim_variant_page(
        slug="piclim-n2o",
        title="piClim-N2O Experiment Setup and Forcings Guidance",
        display_name="piClim-N2O",
        description=block(
            """
            In combination with `piClim-control`, quantifies present-day nitrous oxide effective radiative forcing (ERF).
            Same as `piClim-control`, except nitrous oxide concentrations or emissions (as appropriate for the model) use present-day values
            (in CMIP defined as the last year of the `historical` simulation within the same CMIP era i.e. 2021 values for CMIP7).
            """
        ),
        forcing_change=(
            "except the atmospheric nitrous oxide concentration forcing uses 2021 values."
        ),
        version_forcing_label="nitrous oxide forcing",
    ),
    make_piclim_variant_page(
        slug="piclim-nox",
        title="piClim-NOx Experiment Setup and Forcings Guidance",
        display_name="piClim-NOx",
        description=block(
            """
            In combination with `piClim-control`, quantifies present-day nitrogen oxides (NOx) effective radiative forcing (ERF).
            Same as `piClim-control`, except nitrogen oxides (NOx) emissions use present-day values
            (in CMIP defined as the last year of the `historical` simulation within the same CMIP era i.e. 2021 values for CMIP7).
            """
        ),
        forcing_change="except the NOx emissions forcing uses 2021 values.",
        version_forcing_label="nitrogen oxides (NOx) forcing",
    ),
    make_piclim_variant_page(
        slug="piclim-ods",
        title="piClim-ODS Experiment Setup and Forcings Guidance",
        display_name="piClim-ODS",
        description=block(
            """
            In combination with `piClim-control`, quantifies present-day ozone-depleting substances' effective radiative forcing (ERF).
            Same as `piClim-control`, except ozone-depleting substances concentrations use present-day values
            (in CMIP defined as the last year of the `historical` simulation within the same CMIP era i.e. 2021 values for CMIP7).
            """
        ),
        forcing_change=join_blocks(
            "except emissions of ozone-depleting substances use 2021 values.",
            "<!-- TODO: check the above, I don't think this is correct... -->",
        ).strip(),
        version_forcing_label="ozone-depleting substance forcing",
    ),
    make_piclim_variant_page(
        slug="piclim-so2",
        title="piClim-SO2 Experiment Setup and Forcings Guidance",
        display_name="piClim-SO2",
        description=block(
            """
            In combination with `piClim-control`, quantifies present-day sulfur (dioxide) effective radiative forcing (ERF).
            Same as `piClim-control`, except sulfur emissions use present-day values
            (in CMIP defined as the last year of the `historical` simulation within the same CMIP era i.e. 2021 values for CMIP7).
            """
        ),
        forcing_change=(
            "except emissions of sulfur dioxide (SO<sub>2</sub>) use 2021 values."
        ),
        version_forcing_label="sulfur dioxide (SO2) emissions",
    ),
    ExperimentPage(
        slug="hist-piaer",
        title="hist-piAer Experiment Setup and Forcings Guidance",
        display_name="hist-piAer",
        responsible_activity="AerChemMIP",
        pre_description_note=AERCHEMMIP_UNCERTAIN_NOTE,
        description=join_blocks(
            "<!-- TODO: check this with someone who knows what they're reading -->",
            (
                "In combination with `historical`, allows for evaluation of "
                "the air quality and climate effect of historical aerosol and "
                "tropospheric non-methane ozone precursor emissions in models "
                "without interactive chemistry (for models with interactive "
                "chemistry, see `hist-piAQ`)."
            ),
        ).strip(),
        experiment_setup=join_blocks(
            "<!-- TODO: check this with someone who knows what they're reading -->",
            EXPERIMENT_NAME_CONVENTION_TODO,
            block(
                """
                The `hist-piAer` simulation is a simple variant of the [historical simulation](./historical.md)
                where aerosol and tropospheric non-methane ozone precursor emissions are kept at pre-industrial levels.
                `hist-piAer` is for models that do not include interactive chemistry.
                For models with interactive chemistry, please see [hist-piAQ](./hist-piaq.md) instead.
                """
            ),
            SETUP_GENERATION_TODO,
            "The simulation output should start on 1850-01-01 and end on 2021-12-31.",
            "<!-- TODO: double check, dunne et al. says 6?! -->",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="hist-piAer",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
            extra=(
                "This branch time should match the branch time used for "
                f"initialising the {HISTORICAL_LINK}."
            ),
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
        getting_the_data=f"See instructions for the {PI_CONTROL_LINK} and {HISTORICAL_LINK}.",
    ),
    ExperimentPage(
        slug="hist-piaq",
        title="hist-piAQ Experiment Setup and Forcings Guidance",
        display_name="hist-piAQ",
        responsible_activity="AerChemMIP",
        pre_description_note=AERCHEMMIP_UNCERTAIN_NOTE,
        description=join_blocks(
            "<!-- TODO: check this with someone who knows what they're reading -->",
            (
                "In combination with `historical`, allows for evaluation of "
                "the air quality and climate effect of historical aerosol and "
                "tropospheric non-methane ozone precursor emissions in models "
                "with interactive chemistry (for models without interactive "
                "chemistry, see `hist-piAer`)."
            ),
        ).strip(),
        experiment_setup=join_blocks(
            "<!-- TODO: check this with someone who knows what they're reading -->",
            EXPERIMENT_NAME_CONVENTION_TODO,
            block(
                """
                The `hist-piAQ` simulation is a simple variant of the [historical simulation](./historical.md)
                where aerosol and tropospheric non-methane ozone precursor emissions are kept at pre-industrial levels.
                `hist-piAQ` is for models that include interactive chemistry.
                For models without interactive chemistry, please see [hist-piAer](./hist-piaer.md) instead.
                """
            ),
            SETUP_GENERATION_TODO,
            "The simulation output should start on 1850-01-01 and end on 2021-12-31.",
            "<!-- TODO: double check, dunne et al. says 6?! -->",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="hist-piAQ",
            parent="piControl",
            parent_activity="CMIP",
            branch_instruction="Branch from `piControl` at a time of your choosing.",
            extra=(
                "This branch time should match the branch time used for "
                f"initialising the {HISTORICAL_LINK}."
            ),
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
        getting_the_data=f"See instructions for the {PI_CONTROL_LINK} and {HISTORICAL_LINK}.",
    ),
    ExperimentPage(
        slug="scen7-vl",
        title="scen7-vl Experiment Setup and Forcings Guidance",
        display_name="scen7-vl",
        responsible_activity="ScenarioMIP",
        description=(
            "PLACEHOLDER TBC. CMIP7 ScenarioMIP very low emissions future. "
            "Run with prescribed carbon dioxide concentrations "
            "(for prescribed carbon dioxide emissions, see `esm-scen7-vl`)."
        ),
        experiment_setup=join_blocks(
            "The CMIP7 very low scenario simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation.",
            SETUP_GENERATION_TODO,
            "The simulation output should start on 2022-01-01 and end on 2100-12-31.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment=branch_from(
            experiment="scen7-vl",
            parent="historical",
            parent_activity="CMIP",
            branch_instruction="Branch from `historical` at 2022-01-01.",
        ),
        forcing_headlines="The `scen7-vl` experiment is a time-varying forcings experiment.",
        notes=COMMON_FORCING_NOTES,
        versions_to_use=render_versions_body(
            SCEN7_VL_FORCING_VERSIONS,
            include_multiple_options_note=False,
        ),
        getting_the_data=render_data_access_body(
            experiment_name="scen7-vl",
            source_ids=source_ids_from_forcing_versions(SCEN7_VL_FORCING_VERSIONS),
        ),
    ),
    ExperimentPage(
        slug="amip",
        title="amip Experiment Setup and Forcings Guidance",
        display_name="amip",
        responsible_activity="CMIP",
        description=(
            "Atmosphere-only simulation with prescribed sea surface temperatures "
            "(SSTs) and sea-ice concentrations."
        ),
        experiment_setup=join_blocks(
            EXPERIMENT_NAME_CONVENTION_TODO,
            "The amip simulation uses a specific set of forcings (see [forcings](#forcings)).",
            "These should be applied as transient (i.e. time-changing) forcings over the length of the simulation.",
            SETUP_GENERATION_TODO,
            "The simulation output should start on 1979-01-01 and end on 2021-12-31.",
            "Only one ensemble member is required.",
        ).strip(),
        parent_experiment="`amip` has no parent experiment.",
        forcing_headlines="The `amip` experiment is a time-varying forcings experiment.",
        notes=join_blocks(
            f"See notes for the {PI_CONTROL_LINK}.",
            (
                "The following pages give further information on each forcing "
                f"beyond the ones used in the {HISTORICAL_LINK}:"
            ),
            "\n".join(
                f"- {reference.label}: [{reference.display_url}]({reference.url})"
                for reference in AMIP_FORCING_REFERENCES
            ),
        ).strip(),
        versions_to_use=join_blocks(
            join_lines(
                f"The forcings relevant for this simulation are the same as for the {HISTORICAL_LINK}",
                "with the addition of the SST and sea-ice forcing.",
                (
                    'For this additional forcing, we provide the version(s), in the form of "source ID(s)",'
                ),
                "which should be used when running this simulation.",
                f"For all other forcings, please see the information on the {HISTORICAL_LINK} page.",
            ),
            "<!-- TODO: auto-generate and just duplicate the information rather than forcing people to other pages -->",
            render_versions_json(AMIP_FORCING_VERSIONS),
        ).strip(),
        getting_the_data=render_data_access_body(
            experiment_name="amip",
            source_ids=source_ids_from_forcing_versions(
                AMIP_FORCING_VERSIONS,
                CMIP_FORCING_VERSIONS,
                source_id_indexes=CMIP_TRANSIENT_SOURCE_ID_INDEXES,
            ),
        ),
    ),
)

PLACEHOLDER_PAGES: tuple[SimplePage, ...] = (
    SimplePage(
        slug="scen7-vl-aer",
        title="scen7-vl-Aer Experiment Setup and Forcings Guidance",
        display_name="scen7-vl-Aer",
        body=AERCHEMMIP_PLACEHOLDER_NOTE,
    ),
    SimplePage(
        slug="scen7-vl-aq",
        title="scen7-vl-AQ Experiment Setup and Forcings Guidance",
        display_name="scen7-vl-AQ",
        body=join_blocks(
            "Interactive chemistry equivalent of scen7-vl-Aer.",
            AERCHEMMIP_PLACEHOLDER_NOTE,
        ).strip(),
    ),
    SimplePage(
        slug="scen7-h-aer",
        title="scen7-h-Aer Experiment Setup and Forcings Guidance",
        display_name="scen7-h-Aer",
        body=AERCHEMMIP_PLACEHOLDER_NOTE,
    ),
    SimplePage(
        slug="scen7-h-aq",
        title="scen7-h-AQ Experiment Setup and Forcings Guidance",
        display_name="scen7-h-AQ",
        body=join_blocks(
            "Interactive chemistry equivalent of scen7-h-Aer.",
            AERCHEMMIP_PLACEHOLDER_NOTE,
        ).strip(),
    ),
)

CONTENT_PAGES = EXPERIMENT_PAGES + PLACEHOLDER_PAGES

INDEX_INTRO = block(
    """
    !!! tip "Documentation under development"

        The contents of these pages are currently in development.
        Their format and content will evolve as feedback is received on the drafts.
        We will remove this tip once the guidance is stable.
        If you have any feedback, please feel free to raise an issue at
        https://github.com/WCRP-CMIP/cmip7-guidance/issues/new and tag @znichollscr.

    These pages provide guidance on the experimental setup and forcings to be used in CMIP7.
    They are updated regularly, hence should be considered the current source of guidance.
    The papers which describe the experiments in the scientific literature are the original source and key reference,
    but they may still contain errors which cannot be fixed after publication so should not be relied upon in isolation.
    [The papers](https://gmd.copernicus.org/articles/special_issue1315.html) also provide further information about each simulation than what is provided here,
    such as the motivation, history and results from previous CMIP phases.

    These pages specify the intended way to run each simulation.
    However, we understand that modelling groups sometimes need to make changes for a variety of reasons.
    We are currently discussing a mechanism for modeling centers to document these alterations in a central, publicly accessible location
    (for example, [discussion of how to choose values for the forcing 'f' identifier is ongoing](https://github.com/PCMDI/input4MIPs_CVs/issues/415)).
    When these discussions are finalised, these guidance pages will be updated.
    <!-- TODO: do we have a section to cross-link to? -->

    <!--- TODO: alter this page so that the MIP headings are auto-generated and inject the MIP descriptions from esgvoc. -->
    """
)

SCENARIOMIP_EXTRA = block(
    """
    The priority of ScenarioMIP experiments (expressed as Tier 1 and 2) is summarized in the flowchart below, which is based on Table 1 of [Van Vuuren et al. 2026](https://gmd.copernicus.org/articles/19/2627/2026/).
    Emissions-driven experiments, indicated in yellow, have names beginning with `esm-`.

    - If your model is capable of running in emissions-driven mode, ScenarioMIP request emissions-driven scenarios, and additionally the concentration-driven experiment `scen7-m`, at Tier-1 (highest priority).
    - If your model will run only the concentration-driven experiments, ScenarioMIP request all concentration-driven scenarios at Tier-1.

    If you are running in emissions-driven mode, you are welcome to run other scenarios in concentration-driven mode, but they have not been assigned a specific tier (i.e., are lowest priority).

    <figure>
      <img src="figures/ScenarioMIP-tiers_v3.svg">
      <figcaption>ScenarioMIP experiments, with emissions-driven experiments indicated in yellow.</figcaption>
    </figure>
    """
)

INDEX_GROUPS = (
    IndexGroup(
        heading="DECK experiments",
        activities=(
            IndexActivity(
                heading="CMIP",
                description=(
                    "CMIP core common experiments i.e. the DECK "
                    "(Diagnostic, Evaluation and Characterization of Klima)."
                ),
                experiment_slugs=(
                    "picontrol",
                    "esm-picontrol",
                    "historical",
                    "esm-hist",
                    "1pctco2",
                    "abrupt-4xco2",
                    "piclim-control",
                    "piclim-anthro",
                    "piclim-4xco2",
                    "amip",
                ),
            ),
        ),
    ),
    IndexGroup(
        heading="Assessment Fast Track (AFT) experiments",
        activities=(
            IndexActivity(
                heading="AerChemMIP",
                description=(
                    "Aerosols and chemistry model intercomparison project: "
                    "exploration of aerosol chemistry."
                ),
                experiment_slugs=(
                    "piclim-ch4",
                    "piclim-n2o",
                    "piclim-nox",
                    "piclim-ods",
                    "piclim-so2",
                    "hist-piaer",
                    "hist-piaq",
                    "scen7-vl-aer",
                    "scen7-vl-aq",
                    "scen7-h-aer",
                    "scen7-h-aq",
                ),
            ),
            IndexActivity(
                heading="CFMIP",
                description=block(
                    """
                    Cloud feedback model intercomparison project.
                    Focussed primarily on cloud feedbacks with a secondary focus on understanding of response to
                    forcing, model biases, circulation, regional-scale precipitation, and non-linear changes.
                    """
                ),
                experiment_slugs=("abrupt-2xco2", "abrupt-0p5xco2"),
            ),
            IndexActivity(
                heading="C4MIP",
                description=(
                    "Coupled climate carbon cycle model intercomparison project: "
                    "exploration of the response of the coupled carbon-climate system."
                ),
                experiment_slugs=("1pctco2-bgc", "1pctco2-rad"),
            ),
            IndexActivity(
                heading="ScenarioMIP",
                description=block(
                    """
                    Future scenario experiments.
                    Exploration of the future climate under a (selected) range of possible boundary conditions.
                    """
                ),
                experiment_slugs=("scen7-vl",),
                extra_markdown=SCENARIOMIP_EXTRA,
            ),
        ),
    ),
)


def make_index_page() -> SimplePage:
    """Create the generated index page."""
    page_lookup = {page.slug: page for page in CONTENT_PAGES}
    sections = [INDEX_INTRO]

    for group in INDEX_GROUPS:
        sections.append(f"## {group.heading}")

        for activity in group.activities:
            links = [
                f"1. [{page_lookup[slug].display_name}](./{slug}.md)"
                for slug in activity.experiment_slugs
            ]
            sections.append(
                join_blocks(
                    f"### {activity.heading}",
                    "<!-- TODO: get this from esgvoc automatically -->",
                    activity.description,
                    "\n".join(links),
                    activity.extra_markdown,
                ).strip()
            )

    return SimplePage(
        slug="index",
        title="CMIP7 Experiment Setup and Forcings Guidance",
        display_name="Overview",
        body=join_blocks(*sections).strip(),
        front_matter_title="Overview",
    )


def all_pages() -> tuple[SimplePage | ExperimentPage, ...]:
    """Return all generated pages in write order."""
    return (make_index_page(), *CONTENT_PAGES)


def render_pages() -> dict[str, str]:
    """Render all guidance pages keyed by output filename."""
    return {f"{page.slug}.md": page.render() for page in all_pages()}


def write_pages(output_dir: Path) -> tuple[Path, ...]:
    """Write all generated pages to an output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for filename, content in render_pages().items():
        path = output_dir / filename
        path.write_text(content, encoding="utf-8")
        written.append(path)

    return tuple(written)


def check_pages(output_dir: Path) -> CheckResult:
    """Compare generated pages with an output directory."""
    rendered_pages = render_pages()
    missing: list[Path] = []
    changed: list[Path] = []

    for filename, content in rendered_pages.items():
        path = output_dir / filename
        if not path.exists():
            missing.append(path)
            continue

        if path.read_text(encoding="utf-8") != content:
            changed.append(path)

    extra = tuple(
        sorted(
            (
                path
                for path in output_dir.glob("*.md")
                if path.name not in rendered_pages
            ),
            key=lambda path: path.name,
        )
    )

    return CheckResult(
        missing=tuple(missing),
        changed=tuple(changed),
        extra=extra,
    )


__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "CheckResult",
    "all_pages",
    "check_pages",
    "render_pages",
    "write_pages",
]
