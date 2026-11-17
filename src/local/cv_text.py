r"""Conversion of controlled-vocabulary text (LaTeX/HTML markup) to markdown.

The CMIP7 controlled vocabularies (CVs) store some free text,
particularly citations, using LaTeX markup
(e.g. `H\\"ogner` or `2 {\\textdegree}C`)
and, occasionally, HTML (e.g. `&amp;` or `<i>...</i>`).
The guidance pages are markdown,
so we convert LaTeX to plain (Unicode) text with
[pylatexenc](https://pylatexenc.readthedocs.io/).
Inline HTML tags are left as they are because they render in markdown,
but HTML entities are decoded.
"""

from __future__ import annotations

import html
import re

from pylatexenc.latex2text import LatexNodes2Text

_LATEX_TO_TEXT = LatexNodes2Text(
    # CV prose uses `%` with its plain-text meaning (e.g. "1% per year"),
    # so we can't let it be treated as the start of a comment and dropped.
    keep_comments=True,
)

_PLAIN_TEXT_ESCAPES = {
    # Alignment character in LaTeX, but used as "and" in citations
    # (and appears in HTML entities like `&amp;`).
    "&": r"\&",
    # Non-breaking space in LaTeX, but used as "approximately" in CV prose.
    "~": r"\textasciitilde{}",
}
# Only unescaped characters, so e.g. `\&` and the `\~{n}` accent are untouched.
_PLAIN_TEXT_ESCAPES_PATTERN = re.compile(r"(?<!\\)([&~])")


def cv_text_to_markdown(text: str) -> str:
    """
    Convert controlled-vocabulary text to markdown

    Parameters
    ----------
    text
        Text from the CVs, possibly containing LaTeX and/or HTML markup

    Returns
    -------
    :
        Text with LaTeX converted to plain text and HTML entities decoded
    """
    escaped = _PLAIN_TEXT_ESCAPES_PATTERN.sub(
        lambda match: _PLAIN_TEXT_ESCAPES[match.group(1)], text
    )

    return html.unescape(_LATEX_TO_TEXT.latex_to_text(escaped))
