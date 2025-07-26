#!/usr/bin/env python3
"""
Abstract semantics system for extensible logic framework.

This module provides abstractions for truth value systems and semantic operations
that can be customized for different logic systems.
"""

from abc import ABC, abstractmethod
from typing import Set, Dict, Callable, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class TruthValue:
    """A truth value in a logic system."""
    
    def __init__(self, symbol: str, name: str = None):
        self.symbol = symbol
        self.name = name or symbol
    
    def __str__(self) -> str:
        return self.symbol
    
    def __repr__(self) -> str:
        return f"TruthValue({self.symbol!r})"
    
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, TruthValue) and self.symbol == other.symbol
    
    def __hash__(self) -> int:
        return hash(self.symbol)


# Standard truth values for common systems
TRUE = TruthValue("t", "true")
FALSE = TruthValue("f", "false")
UNDEFINED = TruthValue("e", "undefined/error")
NEITHER = TruthValue("n", "neither")
BOTH = TruthValue("b", "both")


class TruthValueSystem(ABC):
    """Abstract base class for truth value systems."""
    
    @abstractmethod
    def truth_values(self) -> Set[TruthValue]:
        """Return the set of truth values in this system."""
        pass
    
    @abstractmethod
    def designated_values(self) -> Set[TruthValue]:
        """Return the set of designated (true-like) values."""
        pass
    
    @abstractmethod
    def get_operation(self, connective: str) -> Optional[Callable]:
        """Get the semantic operation for a connective."""
        pass
    
    def is_designated(self, value: TruthValue) -> bool:
        """Check if a value is designated."""
        return value in self.designated_values()
    
    def evaluate_formula(self, formula: 'Formula', valuation: Dict[str, TruthValue]) -> TruthValue:
        """Evaluate a formula under a valuation."""
        from .formula import Formula, AtomicFormula, CompoundFormula
        
        if isinstance(formula, AtomicFormula):
            atom_str = str(formula)
            if atom_str not in valuation:
                raise ValueError(f"No valuation for atom {atom_str}")
            return valuation[atom_str]
        
        elif isinstance(formula, CompoundFormula):
            connective = formula.get_main_connective()
            operation = self.get_operation(connective)
            if not operation:
                raise ValueError(f"No operation defined for connective {connective}")
            
            # Evaluate subformulas
            sub_values = [self.evaluate_formula(sub, valuation) for sub in formula.get_subformulas()]
            
            # Apply operation
            return operation(*sub_values)
        
        else:
            raise ValueError(f"Unknown formula type: {type(formula)}")


class ClassicalTruthValueSystem(TruthValueSystem):
    """Classical two-valued truth system."""
    
    def truth_values(self) -> Set[TruthValue]:
        return {TRUE, FALSE}
    
    def designated_values(self) -> Set[TruthValue]:
        return {TRUE}
    
    def get_operation(self, connective: str) -> Optional[Callable]:
        operations = {
            "'": self._conjunction,
            "&": self._conjunction,
            "(": self._disjunction,
            "|": self._disjunction,
            "~": self._negation,
            "->": self._implication,
        }
        return operations.get(connective)
    
    def _conjunction(self, a: TruthValue, b: TruthValue) -> TruthValue:
        return TRUE if a == TRUE and b == TRUE else FALSE
    
    def _disjunction(self, a: TruthValue, b: TruthValue) -> TruthValue:
        return FALSE if a == FALSE and b == FALSE else TRUE
    
    def _negation(self, a: TruthValue) -> TruthValue:
        return FALSE if a == TRUE else TRUE
    
    def _implication(self, a: TruthValue, b: TruthValue) -> TruthValue:
        return FALSE if a == TRUE and b == FALSE else TRUE


class WeakKleeneTruthValueSystem(TruthValueSystem):
    """Weak Kleene three-valued truth system."""
    
    def truth_values(self) -> Set[TruthValue]:
        return {TRUE, FALSE, UNDEFINED}
    
    def designated_values(self) -> Set[TruthValue]:
        return {TRUE}
    
    def get_operation(self, connective: str) -> Optional[Callable]:
        operations = {
            "'": self._conjunction,
            "&": self._conjunction,
            "(": self._disjunction,
            "|": self._disjunction,
            "~": self._negation,
            "->": self._implication,
        }
        return operations.get(connective)
    
    def _conjunction(self, a: TruthValue, b: TruthValue) -> TruthValue:
        if a == UNDEFINED or b == UNDEFINED:
            return UNDEFINED
        return TRUE if a == TRUE and b == TRUE else FALSE
    
    def _disjunction(self, a: TruthValue, b: TruthValue) -> TruthValue:
        if a == UNDEFINED or b == UNDEFINED:
            return UNDEFINED
        return FALSE if a == FALSE and b == FALSE else TRUE
    
    def _negation(self, a: TruthValue) -> TruthValue:
        if a == UNDEFINED:
            return UNDEFINED
        return FALSE if a == TRUE else TRUE
    
    def _implication(self, a: TruthValue, b: TruthValue) -> TruthValue:
        if a == UNDEFINED or b == UNDEFINED:
            return UNDEFINED
        return FALSE if a == TRUE and b == FALSE else TRUE


class FourValuedTruthSystem(TruthValueSystem):
    """Four-valued truth system (for FDE, wKrQ, etc.)."""
    
    def __init__(self, truth_ordering: Dict[TruthValue, Set[TruthValue]] = None):
        """
        Initialize with optional truth ordering.
        truth_ordering maps each value to the set of values it's less than or equal to.
        """
        self._truth_ordering = truth_ordering or {}
    
    def truth_values(self) -> Set[TruthValue]:
        return {TRUE, FALSE, NEITHER, BOTH}
    
    def designated_values(self) -> Set[TruthValue]:
        return {TRUE, BOTH}  # Standard for FDE
    
    def get_operation(self, connective: str) -> Optional[Callable]:
        # To be implemented by specific four-valued systems
        return None


@dataclass
class Model:
    """A semantic model for evaluating formulas."""
    valuation: Dict[str, TruthValue]
    truth_system: TruthValueSystem
    
    def satisfies(self, formula: 'Formula') -> bool:
        """Check if this model satisfies the formula."""
        value = self.truth_system.evaluate_formula(formula, self.valuation)
        return self.truth_system.is_designated(value)
    
    def evaluate(self, formula: 'Formula') -> TruthValue:
        """Evaluate the formula in this model."""
        return self.truth_system.evaluate_formula(formula, self.valuation)
    
    def __str__(self) -> str:
        assignments = ", ".join(f"{atom}={value}" for atom, value in sorted(self.valuation.items()))
        return f"{{{assignments}}}"


class SemanticConsequence:
    """Tools for checking semantic consequence relations."""
    
    @staticmethod
    def is_valid(formula: 'Formula', truth_system: TruthValueSystem) -> bool:
        """Check if formula is valid (true in all models)."""
        # This would require generating all possible valuations
        # For now, this is a placeholder
        raise NotImplementedError("Validity checking not yet implemented")
    
    @staticmethod
    def is_satisfiable(formula: 'Formula', truth_system: TruthValueSystem) -> bool:
        """Check if formula is satisfiable (true in some model)."""
        # This would require checking if tableau closes
        # For now, this is a placeholder
        raise NotImplementedError("Satisfiability checking not yet implemented")


# Backward compatibility
t = TRUE
f = FALSE
e = UNDEFINED