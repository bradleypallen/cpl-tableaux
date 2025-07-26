"""
Logic system plugins for the modular tableau framework.

This module contains implementations of specific logic systems as plugins,
including classical logic, weak Kleene logic, wKrQ epistemic logic, and
the registry system for managing them.
"""

from . import logic_system
from . import classical
from . import weak_kleene
from . import wkrq

__all__ = ['logic_system', 'classical', 'weak_kleene', 'wkrq']