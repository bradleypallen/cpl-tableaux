#!/usr/bin/env python3
"""
Weak Kleene Logic Model Implementation

Extends the model system to support three-valued logic with proper
evaluation of formulas under weak Kleene semantics.
"""

from typing import Dict, Set, Optional, Union
from dataclasses import dataclass

from truth_value import TruthValue, t, f, e, WeakKleeneOperators
from formula import Formula, Atom, Negation, Conjunction, Disjunction, Implication


@dataclass
class WK3Model:
    """
    A three-valued truth assignment for weak Kleene logic.
    Maps atomic propositions to TruthValue (t, f, or e).
    """
    assignment: Dict[str, TruthValue]
    
    def __init__(self, assignment: Optional[Dict[str, Union[TruthValue, bool, str]]] = None):
        """
        Initialize WK3Model with flexible input types.
        
        Args:
            assignment: Dict mapping atom names to truth values.
                       Values can be TruthValue, bool, or string.
        """
        self.assignment = {}
        if assignment:
            for atom, value in assignment.items():
                if isinstance(value, TruthValue):
                    self.assignment[atom] = value
                elif isinstance(value, bool):
                    self.assignment[atom] = TruthValue.from_bool(value)
                elif isinstance(value, str):
                    self.assignment[atom] = TruthValue.from_string(value)
                else:
                    raise ValueError(f"Invalid truth value type for {atom}: {type(value)}")
    
    def satisfies(self, formula: Formula) -> TruthValue:
        """
        Evaluate if this model satisfies the given formula.
        Returns the truth value of the formula under this model.
        """
        return self._evaluate(formula)
    
    def is_satisfying(self, formula: Formula) -> bool:
        """
        Check if this model satisfies the formula (classical notion).
        A formula is satisfied if it evaluates to true (t).
        """
        return self._evaluate(formula) == t
    
    def _evaluate(self, formula: Formula) -> TruthValue:
        """Recursively evaluate a formula under weak Kleene semantics"""
        if isinstance(formula, Atom):
            # Return assigned value, or 'e' if unassigned
            return self.assignment.get(formula.name, e)
        
        elif isinstance(formula, Negation):
            operand_value = self._evaluate(formula.operand)
            return WeakKleeneOperators.negation(operand_value)
        
        elif isinstance(formula, Conjunction):
            left_value = self._evaluate(formula.left)
            right_value = self._evaluate(formula.right)
            return WeakKleeneOperators.conjunction(left_value, right_value)
        
        elif isinstance(formula, Disjunction):
            left_value = self._evaluate(formula.left)
            right_value = self._evaluate(formula.right)
            return WeakKleeneOperators.disjunction(left_value, right_value)
        
        elif isinstance(formula, Implication):
            antecedent_value = self._evaluate(formula.antecedent)
            consequent_value = self._evaluate(formula.consequent)
            return WeakKleeneOperators.implication(antecedent_value, consequent_value)
        
        else:
            raise ValueError(f"Unknown formula type: {type(formula)}")
    
    def get_value(self, atom_name: str) -> TruthValue:
        """Get the truth value assigned to an atom"""
        return self.assignment.get(atom_name, e)
    
    def set_value(self, atom_name: str, value: Union[TruthValue, bool, str]):
        """Set the truth value for an atom"""
        if isinstance(value, TruthValue):
            self.assignment[atom_name] = value
        elif isinstance(value, bool):
            self.assignment[atom_name] = TruthValue.from_bool(value)
        elif isinstance(value, str):
            self.assignment[atom_name] = TruthValue.from_string(value)
        else:
            raise ValueError(f"Invalid truth value type: {type(value)}")
    
    def is_total(self, formula: Formula) -> bool:
        """Check if this model assigns values to all atoms in the formula"""
        atoms = self._extract_atoms(formula)
        return all(atom in self.assignment for atom in atoms)
    
    def is_partial(self, formula: Formula) -> bool:
        """Check if this model is partial (some atoms unassigned)"""
        return not self.is_total(formula)
    
    def extend(self, atom_name: str, value: Union[TruthValue, bool, str]) -> 'WK3Model':
        """Create a new model extending this one with an additional assignment"""
        new_assignment = self.assignment.copy()
        if isinstance(value, TruthValue):
            new_assignment[atom_name] = value
        elif isinstance(value, bool):
            new_assignment[atom_name] = TruthValue.from_bool(value)
        elif isinstance(value, str):
            new_assignment[atom_name] = TruthValue.from_string(value)
        else:
            raise ValueError(f"Invalid truth value type: {type(value)}")
        
        return WK3Model(new_assignment)
    
    def _extract_atoms(self, formula: Formula) -> Set[str]:
        """Extract all atom names from a formula"""
        if isinstance(formula, Atom):
            return {formula.name}
        elif isinstance(formula, Negation):
            return self._extract_atoms(formula.operand)
        elif isinstance(formula, (Conjunction, Disjunction)):
            return self._extract_atoms(formula.left) | self._extract_atoms(formula.right)
        elif isinstance(formula, Implication):
            return self._extract_atoms(formula.antecedent) | self._extract_atoms(formula.consequent)
        else:
            return set()
    
    def to_classical(self) -> Optional[Dict[str, bool]]:
        """
        Convert to classical model if possible.
        Returns None if any atom has value 'e'.
        """
        classical = {}
        for atom, value in self.assignment.items():
            if value == e:
                return None
            classical[atom] = (value == t)
        return classical
    
    def __str__(self) -> str:
        """String representation of the model"""
        if not self.assignment:
            return "{}"
        
        # Group by truth value
        true_atoms = [atom for atom, value in self.assignment.items() if value == t]
        false_atoms = [atom for atom, value in self.assignment.items() if value == f]
        undefined_atoms = [atom for atom, value in self.assignment.items() if value == e]
        
        parts = []
        if true_atoms:
            parts.append(f"t: {{{', '.join(sorted(true_atoms))}}}")
        if false_atoms:
            parts.append(f"f: {{{', '.join(sorted(false_atoms))}}}")
        if undefined_atoms:
            parts.append(f"e: {{{', '.join(sorted(undefined_atoms))}}}")
        
        return " | ".join(parts) if parts else "{}"
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"WK3Model({self.assignment})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, WK3Model):
            return False
        return self.assignment == other.assignment
    
    def __hash__(self) -> int:
        """Hash for use in sets/dicts"""
        return hash(tuple(sorted(self.assignment.items())))


# Backward compatibility: create classical model from WK3Model
def create_classical_model(wk3_model: WK3Model) -> Optional['Model']:
    """
    Create a classical Model from a WK3Model if possible.
    Returns None if the WK3Model contains 'e' values.
    """
    classical_assignment = wk3_model.to_classical()
    if classical_assignment is None:
        return None
    
    # Import here to avoid circular dependency
    from tableau import Model
    return Model(classical_assignment)


# Export commonly used items
__all__ = [
    'WK3Model', 'create_classical_model'
]