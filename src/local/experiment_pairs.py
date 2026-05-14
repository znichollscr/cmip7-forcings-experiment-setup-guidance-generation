"""Experiment pair definitions and rendering helpers."""

from __future__ import annotations

from collections.abc import Collection, Iterable
from dataclasses import dataclass

from local.rendering import join_blocks, render_link
from local.vocab import get_experiment


class MissingRelatedExperimentPageError(ValueError):
    """Raised when a related experiment has no generated guidance page."""


@dataclass(frozen=True)
class ExperimentPair:
    """A pair of experiments that should cross-reference each other."""

    left_slug: str
    right_slug: str
    left_to_right_text: str
    right_to_left_text: str

    def reference_from(
        self,
        slug: str,
        *,
        page_slugs: Collection[str],
    ) -> str | None:
        """Render a reference from ``slug`` to the other experiment in the pair."""
        if slug == self.left_slug:
            return _render_reference(
                source_slug=slug,
                target_slug=self.right_slug,
                text=self.left_to_right_text,
                page_slugs=page_slugs,
            )

        if slug == self.right_slug:
            return _render_reference(
                source_slug=slug,
                target_slug=self.left_slug,
                text=self.right_to_left_text,
                page_slugs=page_slugs,
            )

        return None


EMISSIONS_CONCENTRATION_EXPERIMENT_PAIRS: tuple[ExperimentPair, ...] = (
    ExperimentPair(
        left_slug="picontrol-spinup",
        right_slug="esm-picontrol-spinup",
        left_to_right_text=(
            "is the emissions-driven counterpart to this concentration-driven "
            "spin-up experiment."
        ),
        right_to_left_text=(
            "is the concentration-driven counterpart to this emissions-driven "
            "spin-up experiment."
        ),
    ),
    ExperimentPair(
        left_slug="picontrol",
        right_slug="esm-picontrol",
        left_to_right_text=(
            "is the emissions-driven counterpart to this concentration-driven "
            "control experiment."
        ),
        right_to_left_text=(
            "is the concentration-driven counterpart to this emissions-driven "
            "control experiment."
        ),
    ),
    ExperimentPair(
        left_slug="historical",
        right_slug="esm-hist",
        left_to_right_text=(
            "is the emissions-driven counterpart to this concentration-driven "
            "historical experiment."
        ),
        right_to_left_text=(
            "is the concentration-driven counterpart to this emissions-driven "
            "historical experiment."
        ),
    ),
)

AQ_AER_EXPERIMENT_PAIRS: tuple[ExperimentPair, ...] = (
    ExperimentPair(
        left_slug="hist-piaer",
        right_slug="hist-piaq",
        left_to_right_text=(
            "is the corresponding interactive-chemistry experiment for models "
            "that include interactive chemistry."
        ),
        right_to_left_text=(
            "is the corresponding non-interactive-chemistry experiment for "
            "models that do not include interactive chemistry."
        ),
    ),
)

EXPERIMENT_PAIRS: tuple[ExperimentPair, ...] = (
    *EMISSIONS_CONCENTRATION_EXPERIMENT_PAIRS,
    *AQ_AER_EXPERIMENT_PAIRS,
)


def render_related_experiments(
    slug: str,
    *,
    page_slugs: Collection[str],
    experiment_pairs: Iterable[ExperimentPair] | None = None,
) -> str:
    """Render related-experiment cross-references for a page."""
    if experiment_pairs is None:
        experiment_pairs = _experiment_pairs_for_page_slugs(page_slugs)

    references = tuple(
        reference
        for pair in experiment_pairs
        if (reference := pair.reference_from(slug, page_slugs=page_slugs))
    )
    if not references:
        return ""

    return join_blocks(
        "## Related experiments",
        "\n".join(f"- {reference}" for reference in references),
    ).strip()


def _experiment_pairs_for_page_slugs(
    page_slugs: Collection[str],
) -> tuple[ExperimentPair, ...]:
    """Return explicit and inferred experiment pairs for generated pages."""
    pairs = list(EXPERIMENT_PAIRS)
    pair_keys = {_pair_key(pair) for pair in pairs}

    for pair in (
        *_automatic_emissions_concentration_pairs(page_slugs),
        *_automatic_aq_aer_pairs(page_slugs),
    ):
        pair_key = _pair_key(pair)
        if pair_key in pair_keys:
            continue

        pairs.append(pair)
        pair_keys.add(pair_key)

    return tuple(pairs)


def _automatic_emissions_concentration_pairs(
    page_slugs: Collection[str],
) -> tuple[ExperimentPair, ...]:
    """Infer ``esm-*`` and concentration-driven pairs with matching slugs."""
    pairs: list[ExperimentPair] = []
    for emissions_slug in sorted(
        slug for slug in page_slugs if slug.startswith("esm-")
    ):
        concentration_slug = emissions_slug.removeprefix("esm-")
        if concentration_slug not in page_slugs:
            continue

        pairs.append(
            ExperimentPair(
                left_slug=concentration_slug,
                right_slug=emissions_slug,
                left_to_right_text=(
                    "is the emissions-driven counterpart to this "
                    "concentration-driven experiment."
                ),
                right_to_left_text=(
                    "is the concentration-driven counterpart to this "
                    "emissions-driven experiment."
                ),
            )
        )

    return tuple(pairs)


def _automatic_aq_aer_pairs(
    page_slugs: Collection[str],
) -> tuple[ExperimentPair, ...]:
    """Infer ``*Aer`` and ``*AQ`` pairs with matching slugs."""
    pairs: list[ExperimentPair] = []
    for aer_slug in sorted(slug for slug in page_slugs if slug.endswith("aer")):
        aq_slug = f"{aer_slug[:-3]}aq"
        if aq_slug not in page_slugs:
            continue

        pairs.append(
            ExperimentPair(
                left_slug=aer_slug,
                right_slug=aq_slug,
                left_to_right_text=(
                    "is the corresponding AQ experiment for models that include "
                    "interactive chemistry."
                ),
                right_to_left_text=(
                    "is the corresponding Aer experiment for models that do not "
                    "include interactive chemistry."
                ),
            )
        )

    return tuple(pairs)


def _pair_key(pair: ExperimentPair) -> frozenset[str]:
    """Return an order-independent key for a pair."""
    return frozenset((pair.left_slug, pair.right_slug))


def _render_reference(
    *,
    source_slug: str,
    target_slug: str,
    text: str,
    page_slugs: Collection[str],
) -> str:
    """Render one related experiment reference, failing if the page is missing."""
    if target_slug not in page_slugs:
        msg = (
            f"Experiment {source_slug!r} is paired with related experiment "
            f"{target_slug!r}, but no generated page with slug {target_slug!r} "
            "exists."
        )
        raise MissingRelatedExperimentPageError(msg)

    target_experiment = get_experiment(target_slug)
    return f"{render_link(target_experiment.drs_name, target_slug)} {text}"
