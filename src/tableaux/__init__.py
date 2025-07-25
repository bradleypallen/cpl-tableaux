"""
Semantic Tableau System

A Python implementation of semantic tableau methods for automated theorem proving,
supporting multiple logic systems including classical propositional logic and 
three-valued weak Kleene logic.
"""

__version__ = "0.1.0"
__author__ = "Bradley Allen"
__license__ = "MIT"

# Import all public APIs from tableau_core
from .tableau_core import (
    # Formula classes
    Formula,
    Atom,
    Negation,
    Conjunction,
    Disjunction,
    Implication,
    Predicate,
    Term,
    Constant,
    Variable,
    FunctionApplication,
    RestrictedExistentialFormula,
    RestrictedUniversalFormula,
    
    # Truth values
    TruthValue,
    t, f, e,
    
    # Operators
    weakKleeneOperators,
    
    # Signed formulas
    SignedFormula,
    T, F,
    T3, F3, U,
    TF, FF, M, N,
    
    # Tableau functions
    classical_signed_tableau,
    three_valued_signed_tableau,
    wkrq_signed_tableau,
    ferguson_signed_tableau,
    
    # Parser
    parse_formula,
    
    # Mode-aware system
    LogicMode,
    ModeError,
    PropositionalBuilder,
    FirstOrderBuilder,
    propositional_tableau,
    first_order_tableau,
)

# Import model classes from unified_model
from .unified_model import (
    UnifiedModel,
    ClassicalModel,
    weakKleeneModel,
    WkrqModel,
    Model,  # Backward compatibility alias
)

# Import CLI for programmatic access
from .cli import main as cli_main

__all__ = [
    # Version info
    "__version__",
    
    # Formula classes
    "Formula",
    "Atom",
    "Negation",
    "Conjunction",
    "Disjunction", 
    "Implication",
    "Predicate",
    "Term",
    "Constant",
    "Variable",
    
    # Truth values
    "TruthValue",
    "t", "f", "e",
    
    # Operators
    "weakKleeneOperators",
    
    # Signed formulas
    "SignedFormula",
    "T", "F",
    "T3", "F3", "U",
    "TF", "FF", "M", "N",
    
    # Tableau functions
    "classical_signed_tableau",
    "three_valued_signed_tableau",
    "wkrq_signed_tableau",
    "ferguson_signed_tableau",
    
    # Parser
    "parse_formula",
    
    # Mode-aware system
    "LogicMode",
    "ModeError", 
    "PropositionalBuilder",
    "FirstOrderBuilder",
    "propositional_tableau",
    "first_order_tableau",
    
    # Model classes
    "UnifiedModel",
    "ClassicalModel",
    "weakKleeneModel",
    "WkrqModel",
    "Model",
    
    # CLI
    "cli_main",
]