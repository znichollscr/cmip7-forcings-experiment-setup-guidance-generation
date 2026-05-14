"""Generate CMIP7 experiment setup and forcings guidance pages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from local.rendering import (
    block,
    join_blocks,
    join_lines,
    render_front_matter,
    render_link,
)
from local.rendering import (
    render_pages as render_page_map,
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


def experiment_pages() -> tuple[ExperimentPage, ...]:
    """Return generated experiment pages grouped by responsible activity."""
    from local.activity_pages.aerchemmip import AERCHEMMIP_EXPERIMENT_PAGES
    from local.activity_pages.c4mip import C4MIP_EXPERIMENT_PAGES
    from local.activity_pages.cfmip import CFMIP_EXPERIMENT_PAGES
    from local.activity_pages.cmip import CMIP_EXPERIMENT_PAGES
    from local.activity_pages.scenariomip import SCENARIOMIP_EXPERIMENT_PAGES

    return (
        *CMIP_EXPERIMENT_PAGES,
        *AERCHEMMIP_EXPERIMENT_PAGES,
        *CFMIP_EXPERIMENT_PAGES,
        *C4MIP_EXPERIMENT_PAGES,
        *SCENARIOMIP_EXPERIMENT_PAGES,
    )


def placeholder_pages() -> tuple[SimplePage, ...]:
    """Return generated placeholder pages grouped by responsible activity."""
    from local.activity_pages.aerchemmip import AERCHEMMIP_PLACEHOLDER_PAGES

    return AERCHEMMIP_PLACEHOLDER_PAGES


def content_pages() -> tuple[ExperimentPage | SimplePage, ...]:
    """Return all generated content pages except the index page."""
    return (*experiment_pages(), *placeholder_pages())


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


def make_index_page(
    pages: tuple[ExperimentPage | SimplePage, ...] | None = None,
) -> SimplePage:
    """Create the generated index page."""
    if pages is None:
        pages = content_pages()

    page_lookup = {page.slug: page for page in pages}
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
