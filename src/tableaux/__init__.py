#!/usr/bin/env python3
"""
Modern Tableau Framework for Non-Classical Logics

This package provides a clean, extensible framework for semantic tableau 
systems supporting multiple logic systems through a plugin architecture.

Example usage:
    ```python
    from tableaux import LogicSystem
    
    # Create logic system
    classical = LogicSystem.classical()
    
    # Build formulas with natural syntax
    p, q = classical.atoms('p', 'q')
    formula = p.implies(q) & (p & ~q)
    
    # Solve directly
    result = classical.solve(formula)
    print(f"Satisfiable: {result.satisfiable}")
    print(f"Models: {result.models}")
    ```
"""

from .api import LogicSystem, TableauResult
from .core.formula import (Formula, Variable, Constant, PredicateFormula, 
                          RestrictedExistentialFormula, RestrictedUniversalFormula,
                          Predicate, Atom)
from .core.semantics import Model, TruthValue
from .core.tableau_engine import Tableau

__version__ = "0.1.0"
__all__ = [
    'LogicSystem', 
    'TableauResult',
    'Formula', 
    'Variable',
    'Constant', 
    'PredicateFormula',
    'RestrictedExistentialFormula',
    'RestrictedUniversalFormula',
    'Predicate',
    'Atom',
    'Model', 
    'TruthValue', 
    'Tableau'
]