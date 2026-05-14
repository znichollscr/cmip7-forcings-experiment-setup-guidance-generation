"""Markdown rendering helpers for generated guidance pages."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from textwrap import dedent
from typing import TYPE_CHECKING, Protocol

from local.forcing_versions import ForcingValue

if TYPE_CHECKING:
    from local.forcing_references import ForcingReference


class RenderablePage(Protocol):
    """A page object that can be rendered to markdown."""

    slug: str

    def render(self) -> str:
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

    return join_lines(
        "Further information:",
        render_url_bullet_list(urls),
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


def render_pages(pages: Sequence[RenderablePage]) -> dict[str, str]:
    """Render guidance pages keyed by output filename."""
    return {f"{page.slug}.md": page.render() for page in pages}
