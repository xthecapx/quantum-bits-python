"""
Quantum Bits Python - A framework for analyzing and validating quantum code execution quality.
"""

from .base_validator import BaseValidator
from .experiment import FlipCoinValidator

__version__ = "0.1.0"
__all__ = ["BaseValidator", "FlipCoinValidator"] 