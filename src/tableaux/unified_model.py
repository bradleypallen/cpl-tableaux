#!/usr/bin/env python3
"""
Unified Model Interface for All Tableau Systems

Provides a consistent model interface across classical, weak Kleene, and wKrQ logic systems.
All tableau systems will return models that implement the same interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Union, Optional, Any
from dataclasses import dataclass

from .tableau_core import TruthValue, t, f, e, weakKleeneOperators, Formula, Atom, Negation, Conjunction, Disjunction, Implication



class UnifiedModel(ABC):
    """Abstract base class for all model types across different logic systems"""
    
    @abstractmethod
    def satisfies(self, formula: Formula) -> Union[bool, TruthValue]:
        """
        Evaluate if this model satisfies the given formula.
        
        Returns:
            - bool for classical logic (True/False)
            - TruthValue for multi-valued logics (t/f/e or others)
        """
        pass
    
    @abstractmethod
    def is_satisfying(self, formula: Formula) -> bool:
        """
        Check if this model classically satisfies the formula.
        Always returns bool regardless of logic system.
        """
        pass
    
    @abstractmethod
    def get_assignment(self, atom_name: str) -> Union[bool, TruthValue]:
        """Get the truth value assigned to an atom"""
        pass
    
    @property
    @abstractmethod
    def assignments(self) -> Dict[str, Union[bool, TruthValue]]:
        """Get all atom assignments as a dictionary"""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """String representation of the model"""
        pass


@dataclass
class ClassicalModel(UnifiedModel):
    """Unified model for classical two-valued logic"""
    
    _assignments: Dict[str, bool]
    
    def __init__(self, assignments: Dict[str, Union[bool, TruthValue]]):
        """Initialize with flexible input types"""
        self._assignments = {}
        for atom, value in assignments.items():
            if isinstance(value, bool):
                self._assignments[atom] = value
            elif isinstance(value, TruthValue):
                # Convert TruthValue to bool for classical logic
                self._assignments[atom] = value.to_bool()
            elif hasattr(value, 'value'):
                # Handle objects with .value attribute
                self._assignments[atom] = bool(value.value)
            else:
                self._assignments[atom] = bool(value)
    
    def satisfies(self, formula: Formula) -> bool:
        """Evaluate formula under classical semantics"""
        return self._evaluate_classical(formula)
    
    def is_satisfying(self, formula: Formula) -> bool:
        """Check if model classically satisfies formula"""
        return self.satisfies(formula)
    
    def get_assignment(self, atom_name: str) -> bool:
        """Get boolean assignment for atom"""
        return self._assignments.get(atom_name, False)
    
    @property
    def assignments(self) -> Dict[str, bool]:
        """Get all assignments"""
        return self._assignments.copy()
    
    def _evaluate_classical(self, formula) -> bool:
        """Evaluate formula using classical truth conditions"""
        if isinstance(formula, Atom):
            return self._assignments.get(formula.name, False)
        elif isinstance(formula, Negation):
            return not self._evaluate_classical(formula.operand)
        elif isinstance(formula, Conjunction):
            return (self._evaluate_classical(formula.left) and 
                   self._evaluate_classical(formula.right))
        elif isinstance(formula, Disjunction):
            return (self._evaluate_classical(formula.left) or 
                   self._evaluate_classical(formula.right))
        elif isinstance(formula, Implication):
            return (not self._evaluate_classical(formula.antecedent) or 
                   self._evaluate_classical(formula.consequent))
        else:
            raise ValueError(f"Unknown formula type: {type(formula)}")
    
    def __str__(self) -> str:
        if not self._assignments:
            return "{}"
        
        sorted_items = sorted(self._assignments.items())
        assignment_strs = [f"{atom}={str(value).lower()}" for atom, value in sorted_items]
        return "{" + ", ".join(assignment_strs) + "}"
    
    def __repr__(self) -> str:
        return f"ClassicalModel({self._assignments})"


@dataclass  
class weakKleeneModel(UnifiedModel):
    """Unified model for weak Kleene three-valued logic"""
    
    _assignments: Dict[str, TruthValue]
    
    def __init__(self, assignments: Dict[str, Union[TruthValue, bool, str]]):
        """Initialize with flexible input types"""
        self._assignments = {}
        for atom, value in assignments.items():
            if isinstance(value, TruthValue):
                self._assignments[atom] = value
            elif isinstance(value, bool):
                self._assignments[atom] = TruthValue.from_bool(value)
            elif isinstance(value, str):
                self._assignments[atom] = TruthValue.from_string(value)
            else:
                raise ValueError(f"Invalid truth value type for {atom}: {type(value)}")
    
    def satisfies(self, formula: Formula) -> TruthValue:
        """Evaluate formula under weak Kleene semantics"""
        return self._evaluate_wk3(formula)
    
    def is_satisfying(self, formula: Formula) -> bool:
        """Check if model classically satisfies formula (evaluates to t)"""
        return self._evaluate_wk3(formula) == t
    
    def get_assignment(self, atom_name: str) -> TruthValue:
        """Get truth value assignment for atom"""
        return self._assignments.get(atom_name, e)
    
    @property
    def assignments(self) -> Dict[str, TruthValue]:
        """Get all assignments"""
        return self._assignments.copy()
    
    def _evaluate_wk3(self, formula) -> TruthValue:
        """Evaluate formula using weak Kleene semantics"""
        if isinstance(formula, Atom):
            return self._assignments.get(formula.name, e)
        elif isinstance(formula, Negation):
            operand_value = self._evaluate_wk3(formula.operand)
            return weakKleeneOperators.negation(operand_value)
        elif isinstance(formula, Conjunction):
            left_value = self._evaluate_wk3(formula.left)
            right_value = self._evaluate_wk3(formula.right)
            return weakKleeneOperators.conjunction(left_value, right_value)
        elif isinstance(formula, Disjunction):
            left_value = self._evaluate_wk3(formula.left)  
            right_value = self._evaluate_wk3(formula.right)
            return weakKleeneOperators.disjunction(left_value, right_value)
        elif isinstance(formula, Implication):
            antecedent_value = self._evaluate_wk3(formula.antecedent)
            consequent_value = self._evaluate_wk3(formula.consequent)
            return weakKleeneOperators.implication(antecedent_value, consequent_value)
        else:
            raise ValueError(f"Unknown formula type: {type(formula)}")
    
    def __str__(self) -> str:
        if not self._assignments:
            return "{}"
        
        sorted_items = sorted(self._assignments.items())
        assignment_strs = [f"{atom}={value}" for atom, value in sorted_items]
        return "{" + ", ".join(assignment_strs) + "}"
    
    def __repr__(self) -> str:
        return f"weakKleeneModel({self._assignments})"


@dataclass
class WkrqModel(UnifiedModel):
    """Unified model for wKrQ four-valued logic"""
    
    _assignments: Dict[str, str]  # T, F, M, N
    
    def __init__(self, assignments: Dict[str, Union[str, Any]]):
        """Initialize with flexible input types"""
        self._assignments = {}
        for atom, value in assignments.items():
            if isinstance(value, str) and value in {'T', 'F', 'M', 'N'}:
                self._assignments[atom] = value
            else:
                # Convert other types to string representation
                self._assignments[atom] = str(value)
    
    def satisfies(self, formula: Formula) -> str:
        """Evaluate formula under wKrQ semantics"""
        return self._evaluate_wkrq(formula)
    
    def is_satisfying(self, formula: Formula) -> bool:
        """Check if model classically satisfies formula (evaluates to T)"""
        return self._evaluate_wkrq(formula) == 'T'
    
    def get_assignment(self, atom_name: str) -> str:
        """Get epistemic value assignment for atom"""
        return self._assignments.get(atom_name, 'M')  # Default to "may be true"
    
    @property
    def assignments(self) -> Dict[str, str]:
        """Get all assignments"""
        return self._assignments.copy()
    
    def _evaluate_wkrq(self, formula: Formula) -> str:
        """Evaluate formula using wKrQ epistemic semantics"""
        # Simplified wKrQ evaluation - extend as needed
        if isinstance(formula, Atom):
            return self._assignments.get(formula.name, 'M')
        elif isinstance(formula, Negation):
            operand_value = self._evaluate_wkrq(formula.operand)
            # Negation in wKrQ: T->F, F->T, M->N, N->M
            negation_map = {'T': 'F', 'F': 'T', 'M': 'N', 'N': 'M'}
            return negation_map.get(operand_value, 'M')
        elif isinstance(formula, Conjunction):
            left_value = self._evaluate_wkrq(formula.left)
            right_value = self._evaluate_wkrq(formula.right)
            # Simplified conjunction - proper wKrQ semantics would be more complex
            if left_value == 'T' and right_value == 'T':
                return 'T'
            elif left_value == 'F' or right_value == 'F':
                return 'F'
            else:
                return 'M'  # Default to "may be true"
        # Add other operators as needed
        else:
            return 'M'  # Default for unknown cases
    
    def __str__(self) -> str:
        if not self._assignments:
            return "{}"
        
        sorted_items = sorted(self._assignments.items())
        assignment_strs = [f"{atom}={value}" for atom, value in sorted_items]
        return "{" + ", ".join(assignment_strs) + "}"
    
    def __repr__(self) -> str:
        return f"WkrqModel({self._assignments})"




# Backward compatibility aliases
Model = ClassicalModel  # For legacy code expecting "Model"

# Export all unified model types
__all__ = [
    'UnifiedModel', 'ClassicalModel', 'weakKleeneModel', 'WkrqModel', 
    'Model'
]