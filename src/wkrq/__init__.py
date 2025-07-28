"""
wKrQ - Weak Kleene logic with restricted quantification.

A three-valued logic system with restricted quantifiers for first-order reasoning.
Based on Ferguson (2021) semantics with tableau-based theorem proving.
"""

from .formula import (
    Formula, PropositionalAtom, PredicateFormula, 
    Variable, Constant, Term,
    RestrictedExistentialFormula, RestrictedUniversalFormula
)
from .semantics import WeakKleeneSemantics, TruthValue
from .signs import Sign, SignedFormula, T, F, M, N
from .tableau import Tableau, TableauResult, solve, valid, entails
from .parser import parse, parse_inference
from .api import check_inference, Inference

__version__ = "1.0.0"

__all__ = [
    # Core types
    "Formula", "PropositionalAtom", "PredicateFormula",
    "Variable", "Constant", "Term",
    "RestrictedExistentialFormula", "RestrictedUniversalFormula",
    
    # Semantics
    "WeakKleeneSemantics", "TruthValue",
    
    # Signs
    "Sign", "SignedFormula", "T", "F", "M", "N",
    
    # Tableau
    "Tableau", "TableauResult", 
    
    # Main functions
    "solve", "valid", "entails", "parse", "parse_inference",
    "check_inference", "Inference"
]