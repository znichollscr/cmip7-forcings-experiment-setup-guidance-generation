"""
Forcings details
"""

# TODO: move other forcings content into this module
from .experiment_forcings_specifications import HISTORICAL_FORCINGS_SPECIFICATION
from .specification import (
    ForcingSpecification,
    Input4MIPsBasedForcingSpecification,
    NonInput4MIPsBasedForcingSpecification,
    OtherExperimentBasedForcingSpecification,
)

__all__ = [
    "HISTORICAL_FORCINGS_SPECIFICATION",
    "ESGFBasedForcingSpecification",
    "ForcingSpecification",
    "NonESGFBasedForcingSpecification",
    "OtherExperimentBasedForcingSpecification",
]
