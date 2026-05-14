"""Generate CMIP7 experiment setup and forcings guidance pages."""

from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from local.activities import get_activity_definition
from local.branching import render_parent_information
from local.experiment_descriptions import render_experiment_description
from local.experiment_pairs import render_related_experiments, sort_experiment_slugs
from local.rendering import (
    block,
    join_blocks,
    render_activity_index_link,
    render_activity_urls,
    render_experiment_requirements,
    render_front_matter,
    render_link,
)
from local.rendering import (
    render_pages as render_page_map,
)
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
class ExperimentPage:
    """A full experiment setup and forcings guidance page."""

    slug: str
    experiment_setup: str
    forcing_headlines: str
    notes: str
    versions_to_use: str
    getting_the_data: str
    pre_description_note: str = ""
    parent_experiment_extra: str = ""

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
            self.pre_description_note,
            render_experiment_description(experiment.description),
            render_experiment_metadata_line(
                experiment=experiment,
                responsible_activity=responsible_activity,
            ),
            render_activity_urls(urls_from_term(responsible_activity)),
            render_related_experiments(self.slug, page_slugs=page_slugs),
            "## Experiment set up",
            self.experiment_setup,
            "### Timing, length and ensemble size",
            render_experiment_requirements(experiment),
            "### Parent experiment",
            render_parent_information(
                experiment,
                page_slugs=page_slugs,
                extra=self.parent_experiment_extra,
            ),
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


def render_experiment_metadata_line(*, experiment, responsible_activity) -> str:
    """Render the activity and tier metadata line for an experiment page."""
    if responsible_activity.id == "scenariomip":
        tier_label = (
            f"See {render_activity_index_link(responsible_activity)} information"
        )
    else:
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


def experiment_pages() -> tuple[ExperimentPage, ...]:
    """Return generated experiment pages grouped by responsible activity."""
    from local.activity_pages.aerchemmip import AERCHEMMIP_EXPERIMENT_PAGES
    from local.activity_pages.c4mip import C4MIP_EXPERIMENT_PAGES
    from local.activity_pages.cfmip import CFMIP_EXPERIMENT_PAGES
    from local.activity_pages.cmip import CMIP_EXPERIMENT_PAGES
    from local.activity_pages.scenariomip import SCENARIOMIP_EXPERIMENT_PAGES

    return (
        *_sort_experiment_pages(CMIP_EXPERIMENT_PAGES),
        *_sort_experiment_pages(AERCHEMMIP_EXPERIMENT_PAGES),
        *_sort_experiment_pages(CFMIP_EXPERIMENT_PAGES),
        *_sort_experiment_pages(C4MIP_EXPERIMENT_PAGES),
        *_sort_experiment_pages(SCENARIOMIP_EXPERIMENT_PAGES),
    )


def _sort_experiment_pages(
    pages: Iterable[ExperimentPage],
) -> tuple[ExperimentPage, ...]:
    """Sort experiment pages using the displayed experiment-list ordering."""
    page_lookup = {page.slug: page for page in pages}
    return tuple(
        page_lookup[slug] for slug in sort_experiment_slugs(page_lookup.keys())
    )


def content_pages() -> tuple[ExperimentPage | SimplePage, ...]:
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
                    "scen7-h-aq",
                    "scen7-vl-aer",
                    "scen7-vl-aq",
                ),
            ),
            IndexActivity(
                activity_id="cfmip",
                experiment_slugs=("abrupt-2xco2", "abrupt-0p5xco2"),
            ),
            IndexActivity(
                activity_id="c4mip",
                experiment_slugs=("1pctco2-bgc", "1pctco2-rad"),
            ),
            IndexActivity(
                activity_id="scenariomip",
                experiment_slugs=("scen7-vl",),
            ),
        ),
    ),
)


def render_activity_section(
    activity: IndexActivity,
    *,
    page_lookup: Mapping[str, ExperimentPage | SimplePage],
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
            sections.append(render_activity_section(activity, page_lookup=page_lookup))

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
