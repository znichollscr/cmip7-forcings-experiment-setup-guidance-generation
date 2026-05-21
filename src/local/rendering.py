"""Markdown rendering helpers for generated guidance pages."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from textwrap import TextWrapper, dedent
from typing import Any, Protocol

MARKDOWN_WRAP_WIDTH = 120
LIST_ITEM_RE = re.compile(r"^(\s*(?:[-*+]|\d+[.])\s+)(.*)$")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
MARKDOWN_LINK_SPACE = "\x07"
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
            item_wrapped, consumed = _wrap_list_item_at(
                lines,
                index=index,
                marker=list_item_match.group(1),
                width=width,
            )
            wrapped.extend(item_wrapped)
            index += consumed
            continue

        paragraph.append(line)
        index += 1

    flush_paragraph()
    return "\n".join(wrapped) + "\n"


def _preserved_block_end(stripped_line: str) -> str | None:
    """Return the end marker for markdown blocks that should not be wrapped."""
    if stripped_line.startswith("```"):
        return "```"

    if stripped_line == "$$":
        return "$$"

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


def _wrap_list_item_at(
    lines: Sequence[str],
    *,
    index: int,
    marker: str,
    width: int,
) -> tuple[list[str], int]:
    """Wrap the list item starting at ``index``."""
    item_lines, consumed = _collect_list_item_lines(lines[index:], marker=marker)
    return _wrap_list_item(item_lines, marker=marker, width=width), consumed


def _wrap_list_item(lines: Sequence[str], *, marker: str, width: int) -> list[str]:
    """Wrap a single markdown list item."""
    continuation_indent = " " * len(marker)
    block_indent = " " * (len(marker) + 2)
    wrapped: list[str] = []
    paragraph: list[str] = []
    preserved_block_end: str | None = None
    first_paragraph = True

    first_line_match = LIST_ITEM_RE.match(lines[0])
    if first_line_match is None:
        return []

    paragraph.append(first_line_match.group(2))

    def flush_paragraph() -> None:
        nonlocal first_paragraph
        if not paragraph:
            return

        first_indent = marker if first_paragraph else block_indent
        subsequent_indent = continuation_indent if first_paragraph else block_indent
        wrapped.extend(
            _wrap_sentences(
                " ".join(line.strip() for line in paragraph),
                width=width,
                first_indent=first_indent,
                subsequent_indent=subsequent_indent,
                next_sentence_indent=subsequent_indent,
            )
        )
        paragraph.clear()
        first_paragraph = False

    for line in lines[1:]:
        stripped = line.strip()

        if preserved_block_end is not None:
            wrapped.append(line)
            if preserved_block_end in stripped:
                preserved_block_end = None
            continue

        if not stripped:
            flush_paragraph()
            wrapped.append("")
            continue

        if block_end := _preserved_block_end(stripped):
            flush_paragraph()
            wrapped.append(line)
            preserved_block_end = block_end
            continue

        if _should_preserve_line(line):
            flush_paragraph()
            wrapped.append(line)
            continue

        paragraph.append(line)

    flush_paragraph()
    return wrapped


def _collect_list_item_lines(
    lines: Sequence[str],
    *,
    marker: str,
) -> tuple[list[str], int]:
    """Collect the lines that belong to a list item."""
    continuation_indent = len(marker)
    item_lines: list[str] = [lines[0]]
    index = 1

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if not stripped:
            item_lines.append(line)
            index += 1
            continue

        next_item_match = LIST_ITEM_RE.match(line)
        if next_item_match:
            break

        if len(line) - len(line.lstrip()) < continuation_indent:
            break

        item_lines.append(line)
        index += 1

    return item_lines, index


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


# TODO: rename
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


# TODO: delete when everything is transitioned
def render_activity_urls(urls: Sequence[str]) -> str:
    """Render activity URLs as further-information links."""
    # TODO: alter so first sentence below is always included
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


def render_activity_urls_v2(urls: Sequence[str]) -> str:
    """Render activity URLs as further-information links."""
    blocks = [
        join_lines(
            "This page is intended to help with implementation. "
            "If you notice something that is unclear, "
            "please [raise an issue](https://github.com/WCRP-CMIP/cmip7-guidance/issues/new)."
        )
    ]
    if urls:
        blocks.extend(
            [
                "For the full background of the experiment, please see the following URLs:",
                render_url_bullet_list(urls),
            ]
        )

    res = join_blocks(*blocks).strip()

    return res


def render_pages(pages: Sequence[RenderablePage]) -> dict[str, str]:
    """Render guidance pages keyed by output filename."""
    res = {}
    for page in pages:
        raw = page.render()

        res[f"{page.slug}.md"] = wrap_markdown(raw)

    return res


def render_list_human_like(*parts: str) -> str:
    """
    Render a list like a human i.e. using 'and' between the last two elements.
    """
    if len(parts) < 1:
        msg = "Need some parts"
        raise ValueError(msg)

    if len(parts) == 1:
        return parts[0]

    res = f"{', '.join(parts[:-1])} and {parts[-1]}"

    return res


def only_keep_first_sentence(inval: str) -> str:
    """
    Only keep the first sentence
    """
    first_sentence = inval.split(".")[0]
    res = f"{first_sentence}."

    return res
