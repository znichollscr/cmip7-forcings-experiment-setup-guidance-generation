"""
Forcings specification
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from local.forcing_references import ALL_FORCING_REFERENCES, ForcingReference
from local.rendering import render_external_link


@dataclass(frozen=True)
class Input4MIPsBasedForcingSpecification:
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
    Acceptable, but not recommended, versions (i.e. source IDs) of this forcing

    These might be older versions that have the same data but not metadata
    or versions that were superseded late without a requirement to re-run.
    """

    notes: str | None = None
    """
    Further information about this forcing specification
    """

    @property
    def reference(self) -> ForcingReference:
        """Get the reference to use for this forcing"""
        return ALL_FORCING_REFERENCES[self.forcing_slug]

    @property
    def label(self) -> str:
        """Get the label to use for this forcing"""
        return self.reference.label

    @property
    def rendered_input4mips_cvs_link(self) -> str | None:
        """Get the rendered input4MIPs CVs link for this forcing"""
        return render_input4mips_cvs_link(self.forcing_slug)


@dataclass(frozen=True)
class NonInput4MIPsBasedForcingSpecification:
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

    label_override: str | None = None
    """
    Override to use for labelling this forcing
    """

    @property
    def reference(self) -> ForcingReference:
        """Get the reference to use for this forcing"""
        return ALL_FORCING_REFERENCES[self.forcing_slug]

    @property
    def label(self) -> str:
        """Get the label to use for this forcing"""
        if self.label_override:
            return self.label_override

        return self.reference.label

    @property
    def rendered_input4mips_cvs_link(self) -> str | None:
        """Get the rendered input4MIPs CVs link for this forcing"""
        return render_input4mips_cvs_link(self.forcing_slug)


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

    fixed_override: bool | None = None
    """
    Should the fixed or transient status of the forcing being used be overridden?
    """


@dataclass(frozen=True)
class ForcingSpecification:
    """
    Forcing specification for an experiment
    """

    specific_forcings: tuple[
        Input4MIPsBasedForcingSpecification | NonInput4MIPsBasedForcingSpecification,
        ...,
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
    ) -> tuple[
        Input4MIPsBasedForcingSpecification | NonInput4MIPsBasedForcingSpecification,
        ...,
    ]:
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

        experiment_pages_by_id = {page.id_esgvoc: page for page in experiment_pages()}
        resolved_forcings = [*self.specific_forcings]

        for forcing in self.other_experiment_based_forcings:
            source_experiment = experiment_pages_by_id[forcing.experiment_esgvoc_id]
            source_experiment_forcings_by_slug = {
                forcing.forcing_slug: forcing
                for forcing in source_experiment.forcings.all_forcings
            }
            keep = source_experiment_forcings_by_slug[forcing.forcing_slug]
            if isinstance(forcing.fixed_override, bool):
                keep = replace(keep, fixed=forcing.fixed_override)

            resolved_forcings.append(keep)

        res = tuple(resolved_forcings)

        return res


def render_input4mips_cvs_link(forcing_slug: str) -> str | None:
    """
    Render input4MIPs CVs link for a given forcing slug
    """
    try:
        reference = ALL_FORCING_REFERENCES[forcing_slug]
    except KeyError:
        return None

    return render_external_link(reference.display_url, reference.url)
