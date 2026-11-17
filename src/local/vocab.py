"""Access helpers for the installed CMIP7 esgvoc controlled vocabulary."""

from __future__ import annotations

from functools import cache
from typing import Any

import esgvoc.api as ev

from local.cv_text import cv_text_to_markdown

PROJECT_ID = "cmip7"


class VocabularyLookupError(LookupError):
    """Raised when a required CMIP7 vocabulary term is unavailable."""


@cache
def get_term(term_id: str) -> Any:
    """Return a term from the active CMIP7 esgvoc database."""
    term = ev.get_term_in_project(PROJECT_ID, term_id)
    if term is None:
        msg = (
            f"Could not find {term_id!r} in the active {PROJECT_ID!r} "
            "esgvoc database. Run `uv run esgvoc use cmip7@latest`."
        )
        raise VocabularyLookupError(msg)

    return term


def get_experiment(experiment_id: str) -> Any:
    """Return an experiment term from the active CMIP7 esgvoc database."""
    term = get_term(experiment_id)
    if getattr(term, "type", None) != "experiment":
        term_type = getattr(term, "type", None)
        msg = f"{experiment_id!r} is a {term_type!r}, not an experiment."
        raise VocabularyLookupError(msg)

    return term


def get_activity(activity_id: str) -> Any:
    """Return an activity term from the active CMIP7 esgvoc database."""
    term = get_term(activity_id)
    if getattr(term, "type", None) != "activity":
        msg = f"{activity_id!r} is a {getattr(term, 'type', None)!r}, not an activity."
        raise VocabularyLookupError(msg)

    return term


def get_responsible_activity(experiment: Any) -> Any:
    """Return the responsible activity term for an experiment."""
    return get_activity(experiment.activity)


def urls_from_term(term: Any) -> tuple[str, ...]:
    """Return URL strings from an esgvoc term that has a `urls` attribute."""
    return tuple(str(url) for url in term.urls)


def description_from_term(term: Any) -> str:
    """Return an esgvoc term's description, converted to markdown.

    Any LaTeX or HTML markup in the CVs is converted
    (see [`cv_text_to_markdown`][local.cv_text.cv_text_to_markdown]).
    """
    return cv_text_to_markdown(term.description)


def citations_from_term(term: Any) -> tuple[str, ...]:
    """Return citation strings from an esgvoc term that has a `references` attribute.

    Any LaTeX or HTML markup in the CVs is converted
    (see [`cv_text_to_markdown`][local.cv_text.cv_text_to_markdown]).
    Whitespace (including newlines and non-breaking spaces) is then collapsed
    so each citation renders as a single markdown list item.
    """
    return tuple(
        " ".join(cv_text_to_markdown(str(v["citation"])).split())
        for v in term.references
    )
