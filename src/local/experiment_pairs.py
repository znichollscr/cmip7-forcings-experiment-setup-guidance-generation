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
    left_to_right_text: str = (
        "is the emissions-driven counterpart to this concentration-driven "
        "experiment."
    )
    right_to_left_text: str = (
        "is the concentration-driven counterpart to this emissions-driven "
        "experiment."
    )

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

    def related_slug_from(self, slug: str) -> str | None:
        """Return the other slug in the pair if ``slug`` belongs to this pair."""
        if slug == self.left_slug:
            return self.right_slug

        if slug == self.right_slug:
            return self.left_slug

        return None


EMISSIONS_CONCENTRATION_EXPERIMENT_PAIRS: tuple[ExperimentPair, ...] = (
    ExperimentPair(
        left_slug="picontrol-spinup",
        right_slug="esm-picontrol-spinup",
    ),
    ExperimentPair(
        left_slug="picontrol",
        right_slug="esm-picontrol",
    ),
    ExperimentPair(
        left_slug="historical",
        right_slug="esm-hist",
    ),
)

AQ_AER_LEFT_TO_RIGHT_TEXT = (
    "is the corresponding interactive-chemistry experiment for models "
    "that include interactive chemistry."
)
AQ_AER_RIGHT_TO_LEFT_TEXT = (
    "is the corresponding non-interactive-chemistry experiment for "
    "models that do not include interactive chemistry."
)


def make_aq_aer_experiment_pair(*, aer_slug: str, aq_slug: str) -> ExperimentPair:
    """Create an AQ/Aer experiment pair."""
    return ExperimentPair(
        left_slug=aer_slug,
        right_slug=aq_slug,
        left_to_right_text=AQ_AER_LEFT_TO_RIGHT_TEXT,
        right_to_left_text=AQ_AER_RIGHT_TO_LEFT_TEXT,
    )


AQ_AER_EXPERIMENT_PAIRS: tuple[ExperimentPair, ...] = (
    make_aq_aer_experiment_pair(aer_slug="hist-piaer", aq_slug="hist-piaq"),
    make_aq_aer_experiment_pair(aer_slug="scen7-h-aer", aq_slug="scen7-h-aq"),
    make_aq_aer_experiment_pair(aer_slug="scen7-vl-aer", aq_slug="scen7-vl-aq"),
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
        # TODO: put experiment_pairs on ExperimentPage somehow
        # rather than hiding them here (class method?)
        experiment_pairs = _experiment_pairs_for_page_slugs(page_slugs)

    references_by_slug = {
        related_slug: reference
        for pair in experiment_pairs
        if (related_slug := pair.related_slug_from(slug)) is not None
        if (reference := pair.reference_from(slug, page_slugs=page_slugs))
    }
    if not references_by_slug:
        return ""

    return join_blocks(
        "## Related experiments",
        "\n".join(
            f"- {references_by_slug[related_slug]}"
            for related_slug in sort_experiment_slugs(references_by_slug)
        ),
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

        pairs.append(make_aq_aer_experiment_pair(aer_slug=aer_slug, aq_slug=aq_slug))

    return tuple(pairs)


def _pair_key(pair: ExperimentPair) -> frozenset[str]:
    """Return an order-independent key for a pair."""
    return frozenset((pair.left_slug, pair.right_slug))


def sort_experiment_slugs(slugs: Iterable[str]) -> tuple[str, ...]:
    """Sort experiment slugs, placing paired ``esm-*`` slugs after their pair."""
    slug_tuple = tuple(slugs)
    paired_sort_keys = _paired_sort_keys(slug_tuple)
    return tuple(
        sorted(
            slug_tuple,
            key=lambda slug: paired_sort_keys.get(
                slug, (slug.lower(), 0, slug.lower())
            ),
        )
    )


def _paired_sort_keys(slugs: Iterable[str]) -> dict[str, tuple[str, int, str]]:
    """Return sort-key overrides for recognised experiment pairs."""
    slug_set = set(slugs)
    paired_sort_keys: dict[str, tuple[str, int, str]] = {}

    for pair in EXPERIMENT_PAIRS:
        _add_pair_sort_keys(
            pair.left_slug,
            pair.right_slug,
            slug_set=slug_set,
            paired_sort_keys=paired_sort_keys,
        )

    for emissions_slug in (slug for slug in slug_set if slug.startswith("esm-")):
        concentration_slug = emissions_slug.removeprefix("esm-")
        _add_pair_sort_keys(
            concentration_slug,
            emissions_slug,
            slug_set=slug_set,
            paired_sort_keys=paired_sort_keys,
        )

    for aer_slug in (slug for slug in slug_set if slug.endswith("aer")):
        aq_slug = f"{aer_slug[:-3]}aq"
        _add_pair_sort_keys(
            aer_slug,
            aq_slug,
            slug_set=slug_set,
            paired_sort_keys=paired_sort_keys,
        )

    return paired_sort_keys


def _add_pair_sort_keys(
    left_slug: str,
    right_slug: str,
    *,
    slug_set: set[str],
    paired_sort_keys: dict[str, tuple[str, int, str]],
) -> None:
    """Add sort-key overrides for a pair if both slugs are present."""
    if left_slug not in slug_set or right_slug not in slug_set:
        return

    primary_key = left_slug.lower()
    paired_sort_keys.setdefault(left_slug, (primary_key, 0, left_slug.lower()))
    paired_sort_keys.setdefault(right_slug, (primary_key, 1, right_slug.lower()))


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
