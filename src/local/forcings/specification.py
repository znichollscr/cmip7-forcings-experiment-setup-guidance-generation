"""
Forcings specification
"""

from __future__ import annotations

from dataclasses import dataclass

from local.forcing_references import ALL_FORCING_REFERENCES
from local.rendering import render_external_link


@dataclass(frozen=True)
class ESGFBasedForcingSpecification:
    """
    Specification of an ESGF-based forcing to use
    """

    forcing_slug: str
    """
    Slug of the forcing
    """

    fixed: bool
    """
    Is this forcing applied as fixed (static or repeating)?

    Or is it transient (time-changing)?
    """

    recommended_versions: tuple[str, ...]
    """
    Recommended versions (i.e. source IDs) of this forcing
    """

    acceptable_versions: tuple[str, ...] = ()
    """
    Acceptable, but not rceommended, versions (i.e. source IDs) of this forcing

    These might be older versions that have the same data but not metadata
    or versions that were superseded late without a requirement to re-run.
    """

    notes: str | None = None
    """
    Further information about this forcing specification
    """

    @property
    def reference(self) -> str:
        """Get the reference to use for this forcing"""
        return ALL_FORCING_REFERENCES[self.forcing_slug]

    @property
    def label(self) -> str:
        """Get the label to use for this forcing"""
        return self.reference.label

    @property
    def rendered_input4mips_cvs_link(self) -> str | None:
        """Get the rendered input4MIPs CVs link for this forcing"""
        try:
            reference = self.reference
            res = render_external_link(reference.display_url, reference.url)

        except KeyError:
            res = None

        return res


@dataclass(frozen=True)
class NonESGFBasedForcingSpecification:
    """
    Specification of an non-ESGF-based forcing to use
    """

    forcing_slug: str
    """
    Slug of the forcing
    """

    fixed: bool
    """
    Is this forcing applied as fixed (static or repeating)?

    Or is it transient (time-changing)?
    """

    notes: str | None = None
    """
    Further information about this forcing specification
    """

    @property
    def reference(self) -> str:
        """Get the reference to use for this forcing"""
        return ALL_FORCING_REFERENCES[self.forcing_slug]

    @property
    def label(self) -> str:
        """Get the label to use for this forcing"""
        return self.reference.label

    @property
    def rendered_input4mips_cvs_link(self) -> str | None:
        """Get the rendered input4MIPs CVs link for this forcing"""
        try:
            reference = self.reference
            res = render_external_link(reference.display_url, reference.url)

        except KeyError:
            res = None

        return res


@dataclass(frozen=True)
class OtherExperimentBasedForcingSpecification:
    """
    Specification of forcing to use from a different experiment
    """

    forcing_slug: str
    """
    Slug of the forcing to use from another experiment
    """

    experiment_esgvoc_id: str
    """
    ID of the other experiment (as defined by esgvoc)
    """

    user_modifications: str | None = None
    """
    Modifications which the user must make by hand
    """


@dataclass(frozen=True)
class ForcingSpecification:
    """
    Forcing specification for an experiment
    """

    specific_forcings: tuple[
        ESGFBasedForcingSpecification | NonESGFBasedForcingSpecification, ...
    ] = ()
    """
    Specifications of specific forcings
    """

    other_experiment_based_forcings: tuple[
        OtherExperimentBasedForcingSpecification, ...
    ] = ()
    """
    Forcings based on other experiments
    """

    @property
    def all_forcings(
        self,
    ) -> tuple[ESGFBasedForcingSpecification | NonESGFBasedForcingSpecification, ...]:
        """
        Get all forcing specifications, including resolving those from other experiments

        Returns
        -------
        :
            All forcing specifications
        """
        if not self.other_experiment_based_forcings:
            return self.specific_forcings

        from local.guidance import experiment_pages

        all_experiment_pages = experiment_pages()
        raise NotImplementedError
