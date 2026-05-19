"""
Forcings details
"""

# TODO: move other forcings content into this module
from .experiment_forcings_specifications import HISTORICAL_FORCINGS_SPECIFICATION
from .specification import (
    ESGFBasedForcingSpecification,
    ForcingSpecification,
    NonESGFBasedForcingSpecification,
)

__all__ = [
    "HISTORICAL_FORCINGS_SPECIFICATION",
    "ESGFBasedForcingSpecification",
    "ForcingSpecification",
    "NonESGFBasedForcingSpecification",
]
