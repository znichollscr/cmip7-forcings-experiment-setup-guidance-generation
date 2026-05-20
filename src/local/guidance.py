"""Generate CMIP7 experiment setup and forcings guidance pages."""

from __future__ import annotations

import json
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from local.activities import get_activity_definition
from local.branching import (
    render_parent_and_branching_information,
    render_parent_information,
)
from local.experiment_descriptions import render_experiment_description
from local.experiment_pairs import (
    get_experiment_pairs,
    render_experiment_pair_info,
    render_related_experiments,
    sort_experiment_slugs,
)
from local.forcings import (
    NOT_AVAILABLE_YET,
    ForcingSpecification,
    Input4MIPsBasedForcingSpecification,
    NonInput4MIPsBasedForcingSpecification,
)
from local.mip_co_chair_review import NoCoChairReview
from local.output_time_axis import EsgvocDrivenOutputTimeAxisInformation
from local.rendering import (
    block,
    join_blocks,
    join_lines,
    render_activity_index_link,
    render_activity_urls,
    render_activity_urls_v2,
    render_experiment_requirements,
    render_front_matter,
    render_link,
    render_list_human_like,
)
from local.rendering import (
    render_pages as render_page_map,
)

# TODO: rename vocab to esgvoc
# TODO: import the module then use namespaced access instead
from local.vocab import (
    get_activity,
    get_experiment,
    get_responsible_activity,
    urls_from_term,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT.parent
    / "cmip7-guidance"
    / "docs"
    / "CMIP7"
    / "Experiment_set_up_and_Forcings"
)


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
class ExperimentPageOld:
    """A full experiment setup and forcings guidance page."""

    slug: str
    experiment_setup: str
    forcing_headlines: str
    notes: str
    versions_to_use: str
    getting_the_data: str
    pre_description_note: str = ""
    parent_experiment_extra: str = ""
    include_parent_information: bool = True

    @property
    def experiment(self):
        """Return this page's esgvoc experiment term."""
        return get_experiment(self.slug)

    @property
    def display_name(self) -> str:
        """Return this experiment's DRS name."""
        return self.experiment.drs_name

    @property
    def title(self) -> str:
        """Return this page's generated title."""
        return f"Experiment Setup and Forcings Guidance: {self.display_name}"

    def render(self, *, page_slugs: Collection[str] | None = None) -> str:
        """Render the page as markdown."""
        experiment = self.experiment
        responsible_activity = get_responsible_activity(experiment)
        page_slugs = page_slugs or frozenset()

        return join_blocks(
            render_front_matter(self.title),
            f"# {self.title}",
            # TODO: remove this and just use a function for altering the esgvoc description
            self.pre_description_note,
            # TODO: make this an ExperimentPage parameter
            render_experiment_description(experiment.description),
            # TODO: make this an ExperimentPage parameter
            render_experiment_metadata_line(
                experiment=experiment,
                responsible_activity=responsible_activity,
            ),
            render_activity_urls(urls_from_term(responsible_activity)),
            render_related_experiments(self.slug, page_slugs=page_slugs),
            "## Experiment set up",
            # TODO: check that some overall general, consistent description bit
            # is consistently here
            self.experiment_setup,
            "### Timing, length and ensemble size",
            # TODO: add branching and parent experiment info in here.
            # "Branching, timing, simulation length and ensemble size"
            # TODO: then add an extra section for further set up notes
            render_experiment_requirements(experiment),
            (
                join_blocks(
                    "### Parent experiment",
                    render_parent_information(
                        experiment,
                        page_slugs=page_slugs,
                        extra=self.parent_experiment_extra,
                    ),
                )
                # TODO: alter, should put "No parent experiment" or similar
                # if there is no parent experiment rather than just skipping this block
                if self.include_parent_information
                else ""
            ),
            "## Forcings",
            "### General headlines",
            # TODO: check what is consistently here
            self.forcing_headlines,
            "### Notes",
            # TODO: check whether the content here is consistently
            # about details of implementation, leaving general headlines above
            # for information about whether the experiments are fixed, transient
            # or a mix.
            self.notes,
            "### Versions to use",
            # TODO: somehow make this more standard:
            # each page should either render JSON
            # or point to other pages
            # (but ideally not a blend of these two)
            self.versions_to_use,
            "### Getting the data",
            # TODO: add sections to this to help make clear what comes from what
            self.getting_the_data,
        )


class RenderableBranchInformation(Protocol):
    """Branch information that can be rendered"""

    def render(self, experiment: ExperimentPage) -> str:
        """Render the branch information as a string"""


class RenderableMIPCoChairReviewInformation(Protocol):
    """MIP co-chair information that can be rendered"""

    def render(self, experiment: ExperimentPage) -> str:
        """Render the MIP co-chair information as a string"""


class RenderableOutputTimeAxisInformation(Protocol):
    """Output time axis information that can be rendered"""

    def render(self, experiment: ExperimentPage) -> str:
        """Render the output time axis information as a string"""


@dataclass(frozen=True)
class ExperimentPage:
    """
    Experiment setup and forcings guidance page
    """

    id_esgvoc: str
    """
    ID used by esgvoc, typically just the lowercase version of the experiment's DRS name
    """

    forcings: ForcingSpecification
    """
    Forcing specification for use in this experiment
    """

    branch_information: str | RenderableBranchInformation | None = None
    """
    Branch information
    """

    experiment_setup_notes: str = ""
    """
    Experiment setup notes

    These appear immediately after the "Experiment setup" header.
    They should be used for headline descriptions
    that don't appear elsewhere.
    """

    mip_co_chair_review: RenderableMIPCoChairReviewInformation | None = field(
        default_factory=NoCoChairReview
    )
    """
    MIP co-chair review information
    """

    output_time_axis_info: str | RenderableOutputTimeAxisInformation | None = field(
        default_factory=EsgvocDrivenOutputTimeAxisInformation
    )
    """
    Output time axis information
    """

    render_description: Callable[[str], str] | None = None
    """
    Function to use to render the description

    Receives the esgvoc description as input.

    If `None`, the esgvoc description is used in the page directly.
    """

    # TODO: remove when we remove ExperimentPageOld
    # (can replace with drs_name everywhere)
    @property
    def display_name(self):
        """Temporary mapping to drs_name"""
        return self.experiment_esgvoc.drs_name

    @property
    def drs_name(self):
        """
        DRS (directory reference syntax) name

        More commonly just called the 'experiment name'
        and thought of as the 'display name'.
        """
        return self.experiment_esgvoc.drs_name

    # TODO: add type hints to return type
    @property
    def experiment_esgvoc(self):
        """Return this page's esgvoc experiment term."""
        return get_experiment(self.id_esgvoc)

    # TODO: add type hints to return type
    @property
    def parent_experiment_esgvoc(self):  # EsgvocExperiment | None
        """Return this page's esgvoc parent experiment term."""
        parent_experiment_esgvoc_raw = self.experiment_esgvoc.parent_experiment
        if parent_experiment_esgvoc_raw is None:
            return None

        if isinstance(parent_experiment_esgvoc_raw, str):
            parent_experiment_esgvoc = get_experiment(parent_experiment_esgvoc_raw)
        else:
            parent_experiment_esgvoc = parent_experiment_esgvoc_raw

        return parent_experiment_esgvoc

    # TODO: remove when we remove ExperimentPageOld
    # (can replace with id_esgvoc everywhere)
    @property
    def slug(self):
        """Temporary mapping to id_esgvoc"""
        return self.id_esgvoc

    def render(self) -> str:
        """Render the page as markdown."""
        experiment_esgvoc = self.experiment_esgvoc
        responsible_activity_esgvoc = get_responsible_activity(experiment_esgvoc)
        responsible_activity = get_activity_definition(responsible_activity_esgvoc.id)
        # page_slugs = page_slugs or frozenset()

        title = f"Experiment Setup and Forcings Guidance: {self.display_name}"
        description = (
            self.render_description(experiment_esgvoc.description)
            if self.render_description is not None
            else experiment_esgvoc.description
        )

        activity_info = join_lines(
            f"- Responsible activity: {render_activity_index_link(responsible_activity_esgvoc)}",
            f"- Tier: {responsible_activity.get_tier(self.id_esgvoc)}",
            f"- MIP co-chair review: {self.mip_co_chair_review.render(self)}",
        )

        # These have to be defined in their own module.
        # This is a bit like a database lookup.
        experiment_pairs = get_experiment_pairs(self.id_esgvoc)
        experiment_pair_info = (
            render_experiment_pair_info(
                experiment_pairs,
                target_id_esgvoc=self.id_esgvoc,
            )
            if experiment_pairs
            else ""
        )

        parent_experiment_and_branching_info = (
            render_parent_and_branching_information(self)
            if self.experiment_esgvoc.parent_experiment is not None
            else f"{self.drs_name} does not have a parent experiment."
        )

        return join_blocks(
            render_front_matter(title),
            f"# {title}",
            description,
            activity_info,
            render_activity_urls_v2(urls_from_term(responsible_activity_esgvoc)),
            experiment_pair_info,
            "## Experiment set up",
            # Headline notes that don't belong elsewhere
            self.experiment_setup_notes,
            "### Parent experiment and branching",
            parent_experiment_and_branching_info,
            "### Output time axis",
            self.render_output_time_axis_info(),
            "### Minimum ensemble size",
            self.render_minimum_ensemble_size_info(),
            "## Forcings",
            self.render_forcing_info(header_level_min=3),
        )

    def render_branch_information(self) -> str:
        """
        Render the branch information
        """
        if self.branch_information is None:
            # breakpoint()
            msg = f"{type(self.branch_information)=} ({self.id_esgvoc=})"
            raise TypeError(msg)

        if isinstance(self.branch_information, str):
            branch_information = self.branch_information

        else:
            branch_information = self.branch_information.render(self)

        return branch_information

    def render_forcing_info(self, header_level_min: int) -> str:
        """
        Render the forcing information
        """
        # TODO: clean this up
        internal_data_link = "[data](#data)"

        specific_forcings = self.forcings.specific_forcings
        specific_forcings_input4mips_based = tuple(
            v
            for v in specific_forcings
            if isinstance(v, Input4MIPsBasedForcingSpecification)
        )
        specific_forcings_not_input4mips_based = tuple(
            v
            for v in specific_forcings
            if isinstance(v, NonInput4MIPsBasedForcingSpecification)
        )

        other_experiment_based_forcings = self.forcings.other_experiment_based_forcings
        other_experiment_based_forcings_without_modifications_info = tuple(
            v for v in other_experiment_based_forcings if not v.user_modifications
        )
        other_experiment_based_forcings_with_modifications_info = tuple(
            v for v in other_experiment_based_forcings if v.user_modifications
        )

        if other_experiment_based_forcings_without_modifications_info:
            source_experiment_ids_set = set(
                v.experiment_esgvoc_id
                for v in other_experiment_based_forcings_without_modifications_info
            )
            if (
                not specific_forcings
                and not other_experiment_based_forcings_with_modifications_info
                and len(source_experiment_ids_set) == 1
            ):
                source_experiment = get_experiment(
                    next(iter(source_experiment_ids_set))
                )
                source_experiment_link = render_link(
                    source_experiment.drs_name, source_experiment.id
                )
                data_described_on_other_experiment_pages = f"All data is described on the {source_experiment_link} experiment page."

            else:
                breakpoint()
                raise NotImplementedError

        else:
            data_described_on_other_experiment_pages = join_lines(
                "No data is described on other experiment pages. ",
                f"Please see the other {internal_data_link} sub-sections for details of the forcings data to use for this experiment.",
            )

        if other_experiment_based_forcings_with_modifications_info:
            modifications_list = []
            all_forcings_by_slug = {
                v.forcing_slug: v for v in self.forcings.all_forcings
            }
            for v in other_experiment_based_forcings_with_modifications_info:
                source_forcing = all_forcings_by_slug[v.forcing_slug]
                source_experiment = get_experiment(v.experiment_esgvoc_id)
                source_experiment_link = render_link(
                    source_experiment.drs_name, source_experiment.id
                )
                modifications_list.append(
                    f"- for {source_forcing.label}, use the forcings from {source_experiment.drs_name} but {v.user_modifications}".replace(
                        f" {source_experiment.drs_name} ", f" {source_experiment_link} "
                    ).replace(
                        f" {source_experiment.id} ", f" {source_experiment_link} "
                    )
                )

            data_described_on_other_experiment_pages_with_modifications = join_blocks(
                join_lines(
                    "For the following forcings, please use data from the specified experiment ",
                    "with the specified modification. ",
                ),
                join_lines(*modifications_list),
            )

        else:
            data_described_on_other_experiment_pages_with_modifications = join_lines(
                "No data described on other experiment pages requires modifications by you. ",
                f"Please see the other {internal_data_link} sub-sections for details of the forcings data to use for this experiment.",
            )

        input4mips_based_forcings_versions_simple_json = {}
        if specific_forcings_input4mips_based:
            recommended_source_ids = []
            any_forcings_unavailable = False
            for v in specific_forcings_input4mips_based:
                input4mips_based_forcings_versions_simple_json[v.forcing_slug] = {
                    "human_readable_name": v.label,
                    "recommended_versions": v.recommended_versions,
                    "acceptable_versions": v.acceptable_versions,
                }
                if v.recommended_versions != (NOT_AVAILABLE_YET,):
                    recommended_source_ids.extend(v.recommended_versions)
                else:
                    any_forcings_unavailable = True

            if any_forcings_unavailable:
                esgpull_download_script_start = "The available"

            else:
                esgpull_download_script_start = "The"

            esgpull_download_script = join_blocks(
                # TODO: clean up use of block vs. join_lines vs. join_blocks, do we really need them all?
                block(f"""
                        {esgpull_download_script_start} data is on ESGF and searchable [via metagrid](https://esgf-node.ornl.gov/search?project=input4MIPs&versionType=all&activeFacets=%7B%22mip_era%22%3A%22CMIP7%22%7D),
                        although this method of finding and downloading the data can involve a lot of clicking.
                    """),
                block("""
                        If you install [esgpull](https://esgf.github.io/esgf-download/),
                        you can download all the data associated with the recommended source IDs above
                        using the script given below.
                        Note that this will download all the data associated with these source IDs,
                        which is likely to be much more data than you actually need to run your model.
                    """),
                block(f"""
                        ```bash
                        #!/bin/bash

                        EXPERIMENT_NAME="{self.drs_name}"

                        ## You may need to run the below if you haven't already done it once with esgpull
                        # esgpull self install
                        ## You may also need to run this step to get the data to download
                        # esgpull config api.index_node esgf-node.ornl.gov/esgf-1-5-bridge
                        esgpull add --track --tag ${{EXPERIMENT_NAME}} source_id:{','.join(sorted(set(recommended_source_ids)))}
                        esgpull update --tag ${{EXPERIMENT_NAME}} --yes
                        esgpull download --tag ${{EXPERIMENT_NAME}}
                        ```
                    """),
            )

            data_availablity_specific_input4mips_based = join_blocks(
                f"{'#' * (header_level_min + 2)} Versions to use",
                join_lines(
                    "For each forcing available via input4MIPs, we provide the version(s), "
                    "called 'source ID(s)' in the file's metadata, which should be used when running this simulation. ",
                    "The recommended version(s) are the version(s) we recommend using. ",
                    "Any acceptable versions can be used "
                    "(you are not obliged to re-run simulations that used them).",
                    "Please see the guidance pages linked under each forcing for full details.",
                ),
                join_blocks(
                    *(
                        join_lines(
                            f"- {v.label}",
                            f"    - recommended source IDs: {', '.join(v.recommended_versions)}",
                            (
                                f"    - acceptable source IDs: {', '.join(v.acceptable_versions)}"
                                if v.acceptable_versions
                                else ""
                            ),
                            (f"    - notes: {v.notes}" if v.notes else ""),
                            (
                                f"    - further guidance: {v.rendered_input4mips_cvs_link}"
                                if v.rendered_input4mips_cvs_link
                                else ""
                            ),
                        )
                        for v in specific_forcings_input4mips_based
                    )
                ),
                f"{'#' * (header_level_min + 3)} JSON",
                join_lines(
                    "For easier parsing with machines, we also present the information given above as JSON.",
                ),
                # TODO: see if I can make this a collapsible block
                "\n".join(
                    (
                        "```json",
                        json.dumps(
                            input4mips_based_forcings_versions_simple_json, indent=4
                        ),
                        "```",
                    )
                ),
                f"{'#' * (header_level_min + 3)} Download via esgpull",
                # TODO: see if I can make this a collapsible block
                esgpull_download_script,
            )

        else:
            data_availablity_specific_input4mips_based = join_lines(
                "No ESGF-based data is described specifically on this page. ",
                f"Please see the other {internal_data_link} sub-sections for details of the forcings data to use for this experiment.",
            )

        if specific_forcings_not_input4mips_based:
            data_availability_specific_not_input4mips_based = join_blocks(
                *(
                    join_lines(
                        f"- {v.label}",
                        (f"    - notes: {v.notes}" if v.notes else ""),
                        (
                            f"    - further guidance: {v.rendered_input4mips_cvs_link}"
                            if v.rendered_input4mips_cvs_link
                            else ""
                        ),
                    )
                    for v in specific_forcings_not_input4mips_based
                )
            )

        else:
            data_availability_specific_not_input4mips_based = join_lines(
                "No input4MIPs-based data is described specifically on this page. ",
                f"Please see the other {internal_data_link} sub-sections for details of the forcings data to use for this experiment.",
            )

        res = join_blocks(
            join_lines(
                "The following information will help you identify the forcings to use. "
                "However, we can't define every single detail "
                "because there can be lots of subjective steps between the raw forcings data "
                "and model inputs (e.g. interpolation, re-aggregation, supplementation with other information). "
                "If further guidance would be helpful, "
                "please [raise an issue](https://github.com/WCRP-CMIP/cmip7-guidance/issues/new)."
            ),
            f"{'#' * header_level_min} General headlines",
            self.render_forcing_fixed_or_transient_or_mix_info(),
            f"{'#' * header_level_min} Data",
            join_lines(
                "Here we make a distinction between "
                "data that is described on other experiment pages, "
                "data that is described on other experiment pages with modifications you have to make yourself, "
                "data available via ESGF's input4MIPs project "
                "and data distributed via other channels."
            ),
            f"{'#' * (header_level_min + 1)} Data described on other experiment pages",
            data_described_on_other_experiment_pages,
            f"{'#' * (header_level_min + 1)} Data described on other experiment pages with modifications you have to make",
            data_described_on_other_experiment_pages_with_modifications,
            f"{'#' * (header_level_min + 1)} Data available via input4MIPs",
            data_availablity_specific_input4mips_based,
            f"{'#' * (header_level_min + 1)} Data not available via input4MIPs",
            data_availability_specific_not_input4mips_based,
        )

        return res

    def render_forcing_fixed_or_transient_or_mix_info(self) -> str:
        """
        Render information about whether forcings for a given experiment are fixed, transient or both
        """
        if all(v.fixed for v in self.forcings.all_forcings):
            res = f"The {self.drs_name} experiment is a fixed forcings experiment."

        elif all(not v.fixed for v in self.forcings.all_forcings):
            res = f"The {self.drs_name} experiment is a transient forcings experiment."

        else:
            fixed_forcings_names = render_list_human_like(
                *(v.label for v in self.forcings.all_forcings if v.fixed)
            )
            transient_forcings_names = render_list_human_like(
                *(v.label for v in self.forcings.all_forcings if not v.fixed)
            )
            res = join_lines(
                f"The {self.drs_name} experiment uses a mix of fixed and transient forcings.",
                f"The fixed forcings are: {fixed_forcings_names}."
                f"The transient forcings are: {transient_forcings_names}.",
            )

        return res

    def render_minimum_ensemble_size_info(self) -> str:
        """
        Render the minimum ensemble size information
        """
        min_ensemble_size = self.experiment_esgvoc.min_ensemble_size
        if not isinstance(min_ensemble_size, int):
            raise TypeError(min_ensemble_size)

        if min_ensemble_size == 1:
            res = "Only one ensemble member is required."

        else:
            res = f"At least {min_ensemble_size} ensemble members are required."

        return res

    def render_output_time_axis_info(self) -> str:
        """
        Render the output time axis information
        """
        if isinstance(self.output_time_axis_info, str):
            output_time_axis_info = self.output_time_axis_info

        else:
            output_time_axis_info = self.output_time_axis_info.render(self)

        return output_time_axis_info


def render_experiment_metadata_line(*, experiment, responsible_activity) -> str:
    """Render the activity and tier metadata line for an experiment page."""
    if responsible_activity.id == "scenariomip":
        tier_label = (
            f"See {render_activity_index_link(responsible_activity)} information"
        )
    else:
        # TODO: switch to ValueError
        tier = getattr(experiment, "tier", None)
        tier_label = "not defined" if tier is None else str(tier)

    return (
        f"Responsible activity: {render_activity_index_link(responsible_activity)}. "
        f"Tier: {tier_label}"
    )


@dataclass(frozen=True)
class SimplePage:
    """A markdown page with front matter and a body."""

    slug: str
    title: str
    display_name: str
    body: str
    front_matter_title: str | None = None

    def render(self, *, page_slugs: Collection[str] | None = None) -> str:
        """Render the page as markdown."""
        return join_blocks(
            render_front_matter(self.front_matter_title or self.title),
            f"# {self.title}",
            self.body,
        )


@dataclass(frozen=True)
class IndexActivity:
    """A MIP/activity entry on the guidance index page."""

    activity_id: str
    experiment_slugs: tuple[str, ...]


@dataclass(frozen=True)
class IndexGroup:
    """A group of activities on the guidance index page."""

    heading: str
    activities: tuple[IndexActivity, ...]


PI_CONTROL_LINK = render_link("piControl simulation", "picontrol")
ESM_PI_CONTROL_LINK = render_link("esm-piControl simulation", "esm-picontrol")
HISTORICAL_LINK = render_link("historical simulation", "historical")
ONEPCTCO2_LINK = render_link("1pctCO2 simulation", "1pctco2")
PI_CLIM_CONTROL_LINK = render_link("piClim-control simulation", "piclim-control")
ABRUPT_4XCO2_LINK = render_link("abrupt-4xCO2 simulation", "abrupt-4xco2")


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
    """
)


def experiment_pages() -> tuple[ExperimentPageOld, ...]:
    """Return generated experiment pages."""
    from local.activity_pages.aerchemmip import AERCHEMMIP_EXPERIMENT_PAGES
    from local.activity_pages.c4mip import C4MIP_EXPERIMENT_PAGES
    from local.activity_pages.cfmip import CFMIP_EXPERIMENT_PAGES
    from local.activity_pages.cmip import CMIP_EXPERIMENT_PAGES
    from local.activity_pages.damip import DAMIP_EXPERIMENT_PAGES
    from local.activity_pages.geomip import GEOMIP_EXPERIMENT_PAGES
    from local.activity_pages.pmip import PMIP_EXPERIMENT_PAGES
    from local.activity_pages.rfmip import RFMIP_EXPERIMENT_PAGES
    from local.activity_pages.scenariomip import SCENARIOMIP_EXPERIMENT_PAGES

    detailed_pages = (
        *CMIP_EXPERIMENT_PAGES,
        *AERCHEMMIP_EXPERIMENT_PAGES,
        *CFMIP_EXPERIMENT_PAGES,
        *C4MIP_EXPERIMENT_PAGES,
        *DAMIP_EXPERIMENT_PAGES,
        *GEOMIP_EXPERIMENT_PAGES,
        *PMIP_EXPERIMENT_PAGES,
        *RFMIP_EXPERIMENT_PAGES,
        *SCENARIOMIP_EXPERIMENT_PAGES,
    )
    detailed_pages_by_slug = pages_by_id_esgvoc(detailed_pages)
    _validate_experiment_slugs_to_generate(detailed_pages_by_slug)

    return tuple(detailed_pages_by_slug[slug] for slug in EXPERIMENT_SLUGS_TO_GENERATE)


def content_pages() -> tuple[ExperimentPageOld | SimplePage, ...]:
    """Return all generated content pages except the index page."""
    return experiment_pages()


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
    The papers also provide further information about each simulation than what is provided here,
    such as the motivation, history and results from previous CMIP phases.

    These pages specify the intended way to run each simulation.
    However, we understand that modelling groups sometimes need to make changes for a variety of reasons.
    We are currently discussing a mechanism for modeling centers to document these alterations in a central, publicly accessible location
    (for example, [discussion of how to choose values for the forcing 'f' identifier is ongoing](https://github.com/PCMDI/input4MIPs_CVs/issues/415)).
    When these discussions are finalised, these guidance pages will be updated.
    <!-- TODO: do we have a section to cross-link to? -->

    """
)

INDEX_GROUPS = (
    IndexGroup(
        heading="DECK experiments",
        activities=(
            IndexActivity(
                activity_id="cmip",
                experiment_slugs=(
                    "picontrol-spinup",
                    "picontrol",
                    "esm-picontrol-spinup",
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
                activity_id="aerchemmip",
                experiment_slugs=(
                    "piclim-ch4",
                    "piclim-n2o",
                    "piclim-nox",
                    "piclim-ods",
                    "piclim-so2",
                    "hist-piaer",
                    "hist-piaq",
                    "scen7-h-aer",
                    "esm-scen7-h-aer",
                    "scen7-h-aq",
                    "esm-scen7-h-aq",
                    "scen7-vl-aer",
                    "esm-scen7-vl-aer",
                    "scen7-vl-aq",
                    "esm-scen7-vl-aq",
                ),
            ),
            IndexActivity(
                activity_id="cfmip",
                experiment_slugs=(
                    "abrupt-2xco2",
                    "abrupt-0p5xco2",
                    "amip-p4k",
                    "amip-piforcing",
                ),
            ),
            IndexActivity(
                activity_id="c4mip",
                experiment_slugs=(
                    "1pctco2-bgc",
                    "1pctco2-rad",
                    # "esm-flat10",
                    # "esm-flat10-cdr",
                    # "esm-flat10-zec",
                ),
            ),
            IndexActivity(
                activity_id="scenariomip",
                experiment_slugs=(
                    "scen7-h",
                    "esm-scen7-h",
                    "scen7-h-ext",
                    "esm-scen7-h-ext",
                    "scen7-hl",
                    "esm-scen7-hl",
                    "scen7-hl-ext",
                    "esm-scen7-hl-ext",
                    "scen7-l",
                    "esm-scen7-l",
                    "scen7-l-ext",
                    "esm-scen7-l-ext",
                    "scen7-ln",
                    "esm-scen7-ln",
                    "scen7-ln-ext",
                    "esm-scen7-ln-ext",
                    "scen7-m",
                    "esm-scen7-m",
                    "scen7-m-ext",
                    "esm-scen7-m-ext",
                    "scen7-ml",
                    "esm-scen7-ml",
                    "scen7-ml-ext",
                    "esm-scen7-ml-ext",
                    "scen7-vl",
                    "esm-scen7-vl",
                    "scen7-vl-ext",
                    "esm-scen7-vl-ext",
                ),
            ),
            IndexActivity(
                activity_id="damip",
                experiment_slugs=("hist-aer", "hist-ghg", "hist-nat"),
            ),
            IndexActivity(
                activity_id="geomip",
                experiment_slugs=("g7-1p5k-sai",),
            ),
            IndexActivity(
                activity_id="pmip",
                experiment_slugs=("abrupt-127k",),
            ),
            IndexActivity(
                activity_id="rfmip",
                experiment_slugs=(
                    "piclim-aer",
                    "piclim-histaer",
                    "piclim-histall",
                ),
            ),
        ),
    ),
)

EXPERIMENT_SLUGS_TO_GENERATE = tuple(
    slug
    for group in INDEX_GROUPS
    for activity in group.activities
    for slug in activity.experiment_slugs
)


def render_activity_section(
    activity: IndexActivity,
    *,
    page_lookup: Mapping[str, ExperimentPageOld | SimplePage],
) -> str:
    """Render one activity section on the index page."""
    activity_definition = get_activity_definition(activity.activity_id)
    activity_term = get_activity(activity_definition.activity_id)
    activity_urls = urls_from_term(activity_term)
    links = [
        f"1. [{page_lookup[slug].display_name}](./{slug}.md)"
        for slug in sort_experiment_slugs(activity.experiment_slugs)
    ]

    return join_blocks(
        f"### {activity_term.drs_name}",
        activity_definition.description_from(activity_term.description),
        activity_definition.further_details,
        render_activity_urls(activity_urls),
        f"The following experiments are included in `{activity_term.drs_name}`:",
        "\n".join(links),
    ).strip()


def make_index_page(
    pages: tuple[ExperimentPageOld | SimplePage, ...] | None = None,
) -> SimplePage:
    """Create the generated index page."""
    if pages is None:
        pages = content_pages()

    page_lookup = {page.slug: page for page in pages}
    _validate_index_page_slugs(page_lookup)
    sections = [INDEX_INTRO]

    for group in INDEX_GROUPS:
        sections.append(f"## {group.heading}")

        for activity in group.activities:
            sections.append(render_activity_section(activity, page_lookup=page_lookup))

    return SimplePage(
        slug="index",
        title="CMIP7 Experiment Setup and Forcings Guidance",
        display_name="Overview",
        body=join_blocks(*sections).strip(),
        front_matter_title="Overview",
    )


def pages_by_id_esgvoc(
    pages: tuple[ExperimentPageOld, ...],
) -> dict[str, ExperimentPageOld]:
    """Return pages keyed by esgvoc id, failing on duplicates."""
    pages_by_id_esgvoc: dict[str, ExperimentPageOld] = {}
    duplicate_slugs: list[str] = []
    for page in pages:
        id_esgvoc = page.slug
        if id_esgvoc in pages_by_id_esgvoc:
            duplicate_slugs.append(id_esgvoc)

        pages_by_id_esgvoc[id_esgvoc] = page

    if duplicate_slugs:
        msg = f"Duplicate detailed experiment page slugs: {', '.join(duplicate_slugs)}."
        raise ValueError(msg)

    return pages_by_id_esgvoc


def _validate_experiment_slugs_to_generate(
    detailed_pages_by_slug: dict[str, ExperimentPageOld],
) -> None:
    """Validate the hard-coded experiment page inventory."""
    duplicate_slugs = _duplicate_slugs(EXPERIMENT_SLUGS_TO_GENERATE)
    if duplicate_slugs:
        msg = "Duplicate hard-coded experiment slugs: " f"{', '.join(duplicate_slugs)}."
        raise ValueError(msg)

    unlisted_detailed_pages = tuple(
        slug
        for slug in detailed_pages_by_slug
        if slug not in EXPERIMENT_SLUGS_TO_GENERATE
    )
    if unlisted_detailed_pages:
        msg = (
            "Detailed experiment pages are not listed in "
            f"EXPERIMENT_SLUGS_TO_GENERATE: {', '.join(unlisted_detailed_pages)}."
        )
        raise ValueError(msg)

    missing_detailed_pages = tuple(
        slug
        for slug in EXPERIMENT_SLUGS_TO_GENERATE
        if slug not in detailed_pages_by_slug
    )
    if missing_detailed_pages:
        msg = (
            "Cannot generate guidance pages with confidence because detailed page "
            "definitions are missing for these experiment slugs: "
            f"{', '.join(missing_detailed_pages)}."
        )
        raise ValueError(msg)

    for slug in EXPERIMENT_SLUGS_TO_GENERATE:
        get_experiment(slug)


def _duplicate_slugs(slugs: tuple[str, ...]) -> tuple[str, ...]:
    """Return duplicate slugs while preserving first duplicate order."""
    seen: set[str] = set()
    duplicates: list[str] = []
    for slug in slugs:
        if slug in seen and slug not in duplicates:
            duplicates.append(slug)

        seen.add(slug)

    return tuple(duplicates)


def _validate_index_page_slugs(
    page_lookup: dict[str, ExperimentPageOld | SimplePage],
) -> None:
    """Validate that all index entries have generated pages."""
    missing_slugs = tuple(
        slug for slug in EXPERIMENT_SLUGS_TO_GENERATE if slug not in page_lookup
    )
    if missing_slugs:
        msg = f"Index lists missing pages: {', '.join(missing_slugs)}."
        raise ValueError(msg)


def all_pages() -> tuple[SimplePage | ExperimentPageOld, ...]:
    """Return all generated pages in write order."""
    pages = content_pages()
    return (make_index_page(pages), *pages)


def write_pages(output_dir: Path) -> tuple[Path, ...]:
    """Write all generated pages to an output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for filename, content in render_page_map(all_pages()).items():
        path = output_dir / filename
        path.write_text(content, encoding="utf-8")
        written.append(path)

    return tuple(written)


def check_pages(output_dir: Path) -> CheckResult:
    """Compare generated pages with an output directory."""
    rendered_pages = render_page_map(all_pages())
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
    "write_pages",
]
