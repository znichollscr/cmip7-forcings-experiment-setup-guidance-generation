"""Markdown rendering helpers for generated guidance pages."""

from __future__ import annotations

import json
import re
from collections.abc import Collection, Mapping, Sequence
from datetime import date, datetime
from textwrap import TextWrapper, dedent
from typing import TYPE_CHECKING, Any, Protocol

from local.forcing_versions import (
    ForcingValue,
    acceptable_forcing_values,
    recommended_forcing_value,
)

if TYPE_CHECKING:
    from local.forcing_references import ForcingReference


MARKDOWN_WRAP_WIDTH = 120
LIST_ITEM_RE = re.compile(r"^(\s*(?:[-*+]|\d+[.])\s+)(.*)$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
MARKDOWN_LINK_SPACE = "\x07"
START_OF_YEAR_MONTH = 1
START_OF_YEAR_DAY = 1
END_OF_YEAR_MONTH = 12
END_OF_YEAR_DAY = 31
SENTENCE_BOUNDARY_RE = re.compile(
    r"(?P<sentence_end>(?<!\be\.g)(?<!\bi\.e)(?<!\bvs)(?<!\betc)[.!?][)`\"']*)"
    r"\s+(?=[`\"'(\[]?[A-Z])"
)
MISSING_SENTENCE_SPACE_RE = re.compile(
    r"(?P<sentence_end>(?<!\be\.g)(?<!\bi\.e)(?<!\bvs)(?<!\betc)[.!?][)`\"']*)"
    r"(?=[A-Z])"
)


class RenderablePage(Protocol):
    """A page object that can be rendered to markdown."""

    slug: str

    def render(self, *, page_slugs: Collection[str] | None = None) -> str:
        """Render the page as markdown."""


def block(text: str) -> str:
    """Return a dedented markdown block without surrounding blank lines."""
    return dedent(text).strip("\n")


def join_blocks(*parts: str) -> str:
    """Join markdown blocks with one blank line and a trailing newline."""
    return "\n\n".join(part.strip("\n") for part in parts if part.strip()) + "\n"


def join_lines(*parts: str) -> str:
    """Join markdown lines without paragraph breaks."""
    return "\n".join(part.strip("\n") for part in parts if part.strip())


def wrap_markdown(markdown: str, *, width: int = MARKDOWN_WRAP_WIDTH) -> str:
    """Wrap generated markdown prose at sentence boundaries or ``width``."""
    lines = markdown.rstrip("\n").splitlines()
    wrapped: list[str] = []
    paragraph: list[str] = []
    index = 0
    preserved_block_end: str | None = None
    front_matter_line_count = _front_matter_line_count(lines)

    def flush_paragraph() -> None:
        if not paragraph:
            return

        wrapped.extend(_wrap_paragraph(paragraph, width=width))
        paragraph.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if index < front_matter_line_count:
            wrapped.append(line)
            index += 1
            continue

        if preserved_block_end is not None:
            wrapped.append(line)
            if preserved_block_end in stripped:
                preserved_block_end = None
            index += 1
            continue

        if block_end := _preserved_block_end(stripped):
            flush_paragraph()
            wrapped.append(line)
            preserved_block_end = block_end
            index += 1
            continue

        if not stripped:
            flush_paragraph()
            wrapped.append(line)
            index += 1
            continue

        if _should_preserve_line(line):
            flush_paragraph()
            wrapped.append(line)
            index += 1
            continue

        list_item_match = LIST_ITEM_RE.match(line)
        if list_item_match:
            flush_paragraph()
            wrapped.extend(
                _wrap_list_item(
                    list_item_match.group(1),
                    list_item_match.group(2),
                    width=width,
                )
            )
            index += 1
            continue

        paragraph.append(line)
        index += 1

    flush_paragraph()
    return "\n".join(wrapped) + "\n"


def _preserved_block_end(stripped_line: str) -> str | None:
    """Return the end marker for markdown blocks that should not be wrapped."""
    if stripped_line.startswith("```"):
        return "```"

    if stripped_line.startswith("<!--") and "-->" not in stripped_line:
        return "-->"

    return None


def _front_matter_line_count(lines: Sequence[str]) -> int:
    """Return the number of leading front-matter lines."""
    if not lines or lines[0].strip() != "---":
        return 0

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return index + 1

    return 0


def _should_preserve_line(line: str) -> bool:
    """Return whether a markdown line should be left exactly as rendered."""
    stripped = line.strip()
    return (
        stripped.startswith("#")
        or stripped.startswith("!!!")
        or stripped.startswith("Responsible activity:")
        or stripped.startswith("<!--")
        or stripped.startswith("<figure")
        or stripped.startswith("</figure")
        or stripped.startswith("<img")
        or stripped.startswith("<figcaption")
        or stripped.startswith("</figcaption")
    )


def _wrap_paragraph(lines: Sequence[str], *, width: int) -> list[str]:
    """Wrap one markdown paragraph."""
    indent = re.match(r"\s*", lines[0]).group(0)
    text = " ".join(line.strip() for line in lines)
    return _wrap_sentences(
        text,
        width=width,
        first_indent=indent,
        subsequent_indent=indent,
        next_sentence_indent=indent,
    )


def _wrap_list_item(marker: str, text: str, *, width: int) -> list[str]:
    """Wrap a single markdown list item."""
    continuation_indent = " " * len(marker)
    return _wrap_sentences(
        text.strip(),
        width=width,
        first_indent=marker,
        subsequent_indent=continuation_indent,
        next_sentence_indent=continuation_indent,
    )


def _wrap_sentences(
    text: str,
    *,
    width: int,
    first_indent: str = "",
    subsequent_indent: str = "",
    next_sentence_indent: str | None = None,
) -> list[str]:
    """Wrap text, preferring one sentence per line."""
    lines: list[str] = []
    sentence_indent = first_indent
    next_sentence_indent = (
        first_indent if next_sentence_indent is None else next_sentence_indent
    )

    for sentence in _split_sentences(text):
        lines.extend(
            _wrap_sentence(
                sentence,
                width=width,
                initial_indent=sentence_indent,
                subsequent_indent=subsequent_indent,
            )
        )
        sentence_indent = next_sentence_indent

    return lines


def _wrap_sentence(
    sentence: str,
    *,
    width: int,
    initial_indent: str,
    subsequent_indent: str,
) -> list[str]:
    """Wrap a sentence without breaking long URLs or markdown links."""
    protected_sentence = _protect_markdown_links(sentence)
    if _first_token_exceeds_width(
        protected_sentence,
        initial_indent=initial_indent,
        width=width,
    ):
        return [f"{initial_indent}{_restore_markdown_links(protected_sentence)}"]

    wrapper = TextWrapper(
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False,
    )
    return [
        _restore_markdown_links(line)
        for line in (wrapper.wrap(protected_sentence) or [initial_indent.rstrip()])
    ]


def _first_token_exceeds_width(
    sentence: str,
    *,
    initial_indent: str,
    width: int,
) -> bool:
    """Return whether wrapping would leave an empty marker-only first line."""
    first_token = sentence.split(maxsplit=1)[0]
    return len(initial_indent) + len(first_token) > width


def _split_sentences(text: str) -> tuple[str, ...]:
    """Split text at sentence boundaries while keeping punctuation."""
    normalised = " ".join(text.split())
    normalised = MISSING_SENTENCE_SPACE_RE.sub(
        lambda match: f"{match.group('sentence_end')} ",
        normalised,
    )
    marked = SENTENCE_BOUNDARY_RE.sub(
        lambda match: f"{match.group('sentence_end')}\0",
        normalised,
    )
    return tuple(
        sentence.strip() for sentence in marked.split("\0") if sentence.strip()
    )


def _protect_markdown_links(text: str) -> str:
    """Hide spaces inside markdown links from the text wrapper."""
    return MARKDOWN_LINK_RE.sub(
        lambda match: match.group(0).replace(" ", MARKDOWN_LINK_SPACE),
        text,
    )


def _restore_markdown_links(text: str) -> str:
    """Restore spaces inside markdown links after wrapping."""
    return text.replace(MARKDOWN_LINK_SPACE, " ")


def render_front_matter(title: str) -> str:
    """Render Jekyll front matter for a guidance page."""
    return block(
        f"""
        ---
        layout: default
        title: {json.dumps(title)}
        ---
        """
    )


def render_link(label: str, slug: str) -> str:
    """Render a relative markdown link to another generated page."""
    return f"[{label}](./{slug}.md)"


def render_external_link(label: str, url: str) -> str:
    """Render an external markdown link."""
    return f"[{label}]({url})"


def render_activity_index_link(activity: Any) -> str:
    """Render a link to an activity section on the index page."""
    return f"[{activity.drs_name}](./index.md#{activity.id})"


def render_url_list(urls: Sequence[str]) -> str:
    """Render a compact list of external URL links."""
    if len(urls) == 1:
        return render_external_link("URL", urls[0])

    return ", ".join(
        render_external_link(f"URL {index}", url)
        for index, url in enumerate(urls, start=1)
    )


def render_url_bullet_list(urls: Sequence[str]) -> str:
    """Render external URL links as a markdown bullet list."""
    return "\n".join(f"- {render_external_link(url, url)}" for url in urls)


def render_term_reference(label: str, urls: Sequence[str]) -> str:
    """Render a controlled-vocabulary term with links to its URLs."""
    if not urls:
        return label

    if len(urls) == 1:
        return render_external_link(label, urls[0])

    return f"{label} ({render_url_list(urls)})"


def render_activity_urls(urls: Sequence[str]) -> str:
    """Render activity URLs as further-information links."""
    if not urls:
        return ""

    return join_blocks(
        join_lines(
            "These pages are intended to help with implementation of these experiments. "
            "If you notice something that is unclear, "
            "please [raise an issue](https://github.com/WCRP-CMIP/cmip7-guidance/issues/new). "
            "For the full background of the experiments, please see the following URLs:",
        ),
        render_url_bullet_list(urls),
    ).strip()


def render_experiment_requirements(experiment: Any) -> str:
    """Render experiment timing, length, and ensemble requirements."""
    return join_blocks(
        render_start_end_dates(experiment),
        render_minimum_simulation_length(experiment),
        render_minimum_ensemble_size(experiment),
    ).strip()


def render_start_end_dates(experiment: Any) -> str:
    """Render start and end date requirements from an esgvoc experiment."""
    start_date = format_timestamp(getattr(experiment, "start_timestamp", None))
    end_date = format_timestamp(getattr(experiment, "end_timestamp", None))

    if start_date and end_date:
        return (
            f"The simulation output should start on {start_date} "
            f"and end on {end_date}."
        )

    if start_date:
        return (
            f"The simulation output should start on {start_date}. "
            "The CMIP7 CVs do not define a fixed end date for this simulation."
        )

    if end_date:
        return (
            f"The simulation output should end on {end_date}. "
            "The CMIP7 CVs do not define a fixed start date for this simulation."
        )

    return "The CMIP7 CVs do not define fixed start or end dates for this simulation."


def render_minimum_simulation_length(experiment: Any) -> str:
    """Render minimum simulation length from an esgvoc experiment."""
    start_timestamp = getattr(experiment, "start_timestamp", None)
    end_timestamp = getattr(experiment, "end_timestamp", None)
    if start_timestamp is not None and end_timestamp is not None:
        start_date = _required_date_from_timestamp(
            start_timestamp,
            timestamp_name="start_timestamp",
            experiment=experiment,
        )
        end_date = _required_date_from_timestamp(
            end_timestamp,
            timestamp_name="end_timestamp",
            experiment=experiment,
        )
        return (
            "Simulations should be "
            f"{format_number(_simulation_years(start_date, end_date, experiment))} "
            "years in length."
        )

    minimum_years = getattr(experiment, "min_number_yrs_per_sim", None)
    if minimum_years is None:
        return (
            "The CMIP7 CVs do not define a minimum simulation length for this "
            "experiment."
        )

    return (
        "Simulations should be at least "
        f"{format_number(minimum_years)} years in length."
    )


def render_minimum_ensemble_size(experiment: Any) -> str:
    """Render minimum ensemble size from an esgvoc experiment."""
    minimum_ensemble_size = getattr(experiment, "min_ensemble_size", None)
    if minimum_ensemble_size is None:
        return ""

    if minimum_ensemble_size == 1:
        return "Only one ensemble member is required."

    return f"At least {minimum_ensemble_size} ensemble members are required."


def format_timestamp(timestamp: Any) -> str:
    """Format an esgvoc timestamp as an ISO date."""
    timestamp_date = date_from_timestamp(timestamp)
    if timestamp_date is None:
        return ""

    return timestamp_date.isoformat()


def date_from_timestamp(timestamp: Any) -> date | None:
    """Return the date part of a CV timestamp."""
    if timestamp is None:
        return None

    if isinstance(timestamp, datetime):
        return timestamp.date()

    if isinstance(timestamp, date):
        return timestamp

    date_method = getattr(timestamp, "date", None)
    if callable(date_method):
        return date_method()

    return None


def _required_date_from_timestamp(
    timestamp: Any,
    *,
    timestamp_name: str,
    experiment: Any,
) -> date:
    """Return a date from a specified timestamp, failing if unsupported."""
    timestamp_date = date_from_timestamp(timestamp)
    if timestamp_date is not None:
        return timestamp_date

    experiment_id = getattr(experiment, "id", experiment)
    msg = (
        f"Cannot calculate exact simulation years for {experiment_id!r}: "
        f"{timestamp_name} has unsupported value {timestamp!r}."
    )
    raise NotImplementedError(msg)


def _simulation_years(start_date: date, end_date: date, experiment: Any) -> int:
    """Return exact simulation years for whole-year start/end dates."""
    if (
        start_date.month != START_OF_YEAR_MONTH
        or start_date.day != START_OF_YEAR_DAY
        or end_date.month != END_OF_YEAR_MONTH
        or end_date.day != END_OF_YEAR_DAY
    ):
        experiment_id = getattr(experiment, "id", experiment)
        msg = (
            f"Cannot calculate exact simulation years for {experiment_id!r}: "
            f"start date is {start_date.isoformat()} and end date is "
            f"{end_date.isoformat()}."
        )
        raise NotImplementedError(msg)

    return end_date.year - start_date.year + 1


def format_number(value: float) -> str:
    """Format a numeric CV value without a redundant decimal."""
    float_value = float(value)
    if float_value.is_integer():
        return str(int(float_value))

    return str(value)


def same_as_versions(label: str, slug: str) -> str:
    """Render a short versions section for experiments sharing another setup."""
    return (
        "The forcings relevant for this simulation are the same as for the "
        f"{render_link(label, slug)}."
    )


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


def render_forcing_value(
    value: ForcingValue,
) -> Any:
    """Render one forcing version value as a JSON-serialisable object."""
    if value.recommended is None and not value.acceptable:
        return None

    rendered_value: dict[str, Any] = {
        "recommended": recommended_forcing_value(value=value),
    }
    acceptable_values = acceptable_forcing_values(value=value)
    if acceptable_values:
        rendered_value["acceptable"] = list(acceptable_values)

    return rendered_value


def render_versions_json(
    forcing_versions: Mapping[str, ForcingValue],
) -> str:
    """Render forcing versions as a JSON code block."""
    rendered_versions = {
        forcing_id: render_forcing_value(value)
        for forcing_id, value in forcing_versions.items()
    }

    return "\n".join(("```json", json.dumps(rendered_versions, indent=4), "```"))


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
            Where acceptable versions are listed,
            these are acceptable for use but are not the recommended version
            (because, e.g., fixes were made but re-running is not required).
            The data-retrieval script below only includes recommended versions.
            Please see the guidance pages linked above for details.
            """
        )

    return join_blocks(
        block(
            """
            The forcings relevant for this simulation are listed below.
            For each forcing, we provide the version(s), in the form of "source ID(s)",
            which should be used when running this simulation.
            The recommended version is the version we recommend using.
            Any acceptable versions are acceptable for use, but are not recommended.
            """
        ),
        multiple_options_note,
        render_versions_json(forcing_versions),
    ).strip()


DATA_ACCESS_INTRO = join_blocks(
    block(
        """
        The data is available on ESGF and searchable [via metagrid](https://esgf-node.ornl.gov/search?project=input4MIPs&versionType=all&activeFacets=%7B%22mip_era%22%3A%22CMIP7%22%7D),
        although this method of finding and downloading the data can involve a lot of clicking.
        """
    ),
    (
        "Having said this, please also note: the aerosol optical properties "
        "based on the MACv2-SP parameterisation are not distributed via the ESGF; "
        "please see their [specific guidance section]"
        "(https://input4mips-cvs.readthedocs.io/en/latest/dataset-overviews/"
        "aerosol-optical-properties-macv2-sp/#datasets-for-cmip7-phases) "
        "for data access information."
    ),
).strip()


def render_data_access_body(
    *,
    experiment_name: str,
    source_ids: Sequence[str],
    extra: str = "",
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
        extra,
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


def render_pages(pages: Sequence[RenderablePage]) -> dict[str, str]:
    """Render guidance pages keyed by output filename."""
    page_slugs = frozenset(page.slug for page in pages)
    return {
        f"{page.slug}.md": wrap_markdown(page.render(page_slugs=page_slugs))
        for page in pages
    }
