"""Generate CMIP7 experiment setup and forcings guidance pages."""

from __future__ import annotations

from collections.abc import Collection, Mapping
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
    """Return generated experiment pages grouped by responsible activity."""
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
    detailed_pages_by_slug = _pages_by_slug(detailed_pages)
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


def _pages_by_slug(
    pages: tuple[ExperimentPageOld, ...],
) -> dict[str, ExperimentPageOld]:
    """Return pages keyed by slug, failing on duplicates."""
    pages_by_slug: dict[str, ExperimentPageOld] = {}
    duplicate_slugs: list[str] = []
    for page in pages:
        if page.slug in pages_by_slug:
            duplicate_slugs.append(page.slug)
        pages_by_slug[page.slug] = page

    if duplicate_slugs:
        msg = f"Duplicate detailed experiment page slugs: {', '.join(duplicate_slugs)}."
        raise ValueError(msg)

    return pages_by_slug


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
