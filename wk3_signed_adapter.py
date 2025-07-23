#!/usr/bin/env python3
"""
WK3 Signed Tableau Adapter

Provides backward compatibility for the existing WK3 tableau API while using
the new signed tableau system internally. This allows existing code to work
unchanged while benefiting from the literature-standard signed approach.
"""

from typing import List, Union, Optional, Dict, Any
from dataclasses import dataclass

from formula import Formula, Atom
from signed_formula import SignedFormula, ThreeValuedSign, T3, F3, U
from signed_tableau import SignedTableau, three_valued_signed_tableau
from wk3_model import WK3Model
from truth_value import TruthValue, t, f, e


@dataclass 
class WK3SignedModel:
    """
    WK3 model that wraps a signed model for backward compatibility.
    Provides the same interface as the original WK3Model.
    """
    assignment: Dict[str, TruthValue]
    
    def satisfies(self, formula: Formula) -> TruthValue:
        """Evaluate a formula under this model using WK3 semantics"""
        return self._evaluate(formula)
    
    def get_value(self, atom_name: str) -> TruthValue:
        """Get the truth value assigned to an atom (for backward compatibility)"""
        return self.assignment.get(atom_name, e)
    
    def _evaluate(self, formula: Formula) -> TruthValue:
        """Recursively evaluate a formula using weak Kleene semantics"""
        from formula import Negation, Conjunction, Disjunction, Implication
        
        if isinstance(formula, Atom):
            return self.assignment.get(formula.name, e)
        elif isinstance(formula, Negation):
            operand_value = self._evaluate(formula.operand)
            if operand_value == t:
                return f
            elif operand_value == f:
                return t
            else:  # operand_value == e
                return e
        elif isinstance(formula, Conjunction):
            left_val = self._evaluate(formula.left)
            right_val = self._evaluate(formula.right)
            
            # WK3 conjunction: false if either is false, undefined if either undefined (and none false)
            if left_val == f or right_val == f:
                return f
            elif left_val == e or right_val == e:
                return e
            else:  # both true
                return t
        elif isinstance(formula, Disjunction):
            left_val = self._evaluate(formula.left)
            right_val = self._evaluate(formula.right)
            
            # WK3 disjunction: true if either is true, undefined if either undefined (and none true)
            if left_val == t or right_val == t:
                return t
            elif left_val == e or right_val == e:
                return e
            else:  # both false
                return f
        elif isinstance(formula, Implication):
            ant_val = self._evaluate(formula.antecedent)
            cons_val = self._evaluate(formula.consequent)
            
            # WK3 implication: A → B ≡ ¬A ∨ B in weak Kleene
            neg_ant = t if ant_val == f else (f if ant_val == t else e)
            
            # Now compute neg_ant ∨ cons_val
            if neg_ant == t or cons_val == t:
                return t
            elif neg_ant == e or cons_val == e:
                return e
            else:
                return f
        else:
            raise ValueError(f"Unknown formula type: {type(formula)}")
    
    def __str__(self) -> str:
        """String representation matching original WK3Model format"""
        if not self.assignment:
            return "{}"
        
        true_atoms = [atom for atom, value in self.assignment.items() if value == t]
        false_atoms = [atom for atom, value in self.assignment.items() if value == f]
        undefined_atoms = [atom for atom, value in self.assignment.items() if value == e]
        
        parts = []
        if true_atoms:
            parts.append(f"True: {{{', '.join(sorted(true_atoms))}}}")
        if false_atoms:
            parts.append(f"False: {{{', '.join(sorted(false_atoms))}}}")
        if undefined_atoms:
            parts.append(f"Undefined: {{{', '.join(sorted(undefined_atoms))}}}")
        
        return " | ".join(parts) if parts else "{}"


class WK3SignedTableau:
    """
    WK3 tableau that uses signed tableaux internally but provides the same
    API as the original WK3Tableau for backward compatibility.
    """
    
    def __init__(self, initial_formulas: Union[Formula, List[Formula]]):
        # Handle both single formula and list
        if isinstance(initial_formulas, Formula):
            self.initial_formulas = [initial_formulas]
        else:
            self.initial_formulas = initial_formulas
        
        # For WK3 satisfiability, we test if NOT F:formula (i.e., formula is not false)
        # This allows formula to be either true or undefined
        from signed_formula import F3
        self.initial_signed_formulas = [F3(f) for f in self.initial_formulas]
        
        # Create the internal signed tableau to test unsatisfiability of F:formula
        self.signed_tableau = SignedTableau(self.initial_signed_formulas, "three_valued")
        
        # Expose compatibility attributes
        self.branches = []  # Will be populated after building
        self.built = False
        
        # Statistics
        self.rule_applications = 0
        self.branch_creations = 0
    
    def build(self) -> bool:
        """Build the tableau and return satisfiability"""
        # In WK3, a formula is satisfiable if it can be T (true) OR U (undefined)
        # Test both T:formula and U:formula
        
        t_satisfiable = False
        u_satisfiable = False
        
        # Test T:formula (can it be true?)
        for f in self.initial_formulas:
            t_tableau = SignedTableau([T3(f)], "three_valued")
            if t_tableau.build():
                t_satisfiable = True
                break
        
        # Test U:formula (can it be undefined?)
        if not t_satisfiable:  # Only check undefined if not already satisfiable as true
            for f in self.initial_formulas:
                u_tableau = SignedTableau([U(f)], "three_valued")
                if u_tableau.build():
                    u_satisfiable = True
                    break
        
        # Store the successful tableau for compatibility
        if t_satisfiable:
            self.signed_tableau = SignedTableau([T3(self.initial_formulas[0])], "three_valued")
            self.signed_tableau.build()
        elif u_satisfiable:
            self.signed_tableau = SignedTableau([U(self.initial_formulas[0])], "three_valued")
            self.signed_tableau.build()
        else:
            # Use F:formula tableau to show unsatisfiability
            pass
        
        self.built = True
        
        # Update compatibility attributes
        self.rule_applications = self.signed_tableau.rule_applications
        self.branch_creations = self.signed_tableau.branch_creations
        
        # Convert signed branches to WK3Branch-like objects for compatibility
        self._create_compatibility_branches()
        
        return t_satisfiable or u_satisfiable
    
    def _create_compatibility_branches(self):
        """Create WK3Branch-like objects for backward compatibility"""
        self.branches = []
        
        for signed_branch in self.signed_tableau.branches:
            # Create a simple branch-like object with the essential attributes
            compat_branch = type('WK3CompatBranch', (), {
                'id': signed_branch.id,
                'is_closed': signed_branch.is_closed,
                'signed_formulas': signed_branch.signed_formulas,
                'closure_reason': signed_branch.closure_reason
            })()
            
            self.branches.append(compat_branch)
    
    def is_satisfiable(self) -> bool:
        """Check if the formula set is satisfiable"""
        if not self.built:
            return self.build()
        # The build() method already computed WK3 satisfiability correctly
        return self.signed_tableau.is_satisfiable()
    
    def extract_all_models(self) -> List[WK3SignedModel]:
        """Extract all WK3 models from the signed tableau"""
        if not self.built:
            self.build()
        
        signed_models = self.signed_tableau.extract_all_models()
        wk3_models = []
        
        for signed_model in signed_models:
            # Convert signed model to WK3 model format
            wk3_assignment = {}
            
            for formula, sign in signed_model.assignments.items():
                if isinstance(formula, Atom):
                    atom_name = formula.name
                    if isinstance(sign, ThreeValuedSign):
                        wk3_assignment[atom_name] = sign.get_truth_value()
            
            # For atoms not explicitly assigned, assign undefined
            all_atoms = set()
            for formula in self.initial_formulas:
                all_atoms.update(self._extract_atoms(formula))
            
            for atom_name in all_atoms:
                if atom_name not in wk3_assignment:
                    wk3_assignment[atom_name] = e
            
            wk3_models.append(WK3SignedModel(wk3_assignment))
        
        return wk3_models
    
    def get_sample_model(self) -> Optional[WK3SignedModel]:
        """Get one satisfying model"""
        models = self.extract_all_models()
        return models[0] if models else None
    
    def _extract_atoms(self, formula: Formula) -> set:
        """Extract all atom names from a formula"""
        if isinstance(formula, Atom):
            return {formula.name}
        elif hasattr(formula, 'operand'):  # Negation
            return self._extract_atoms(formula.operand)
        elif hasattr(formula, 'left') and hasattr(formula, 'right'):  # Binary operators
            return self._extract_atoms(formula.left) | self._extract_atoms(formula.right)
        elif hasattr(formula, 'antecedent') and hasattr(formula, 'consequent'):  # Implication
            return self._extract_atoms(formula.antecedent) | self._extract_atoms(formula.consequent)
        else:
            return set()
    
    def print_tree(self):
        """Print the tableau tree (delegated to signed tableau)"""
        if not self.built:
            self.build()
        self.signed_tableau.print_tableau()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tableau statistics"""
        if not self.built:
            self.build()
        
        stats = self.signed_tableau.get_statistics()
        # Add WK3-specific information
        stats.update({
            "logic_system": "WK3 (via signed tableaux)",
            "sign_system": "three_valued",
            "truth_values": ["t", "f", "e"]
        })
        
        return stats


# Convenience functions that maintain the original API

def wk3_tableau(formula: Union[Formula, List[Formula]]) -> WK3SignedTableau:
    """Create a WK3 tableau using signed tableaux internally"""
    return WK3SignedTableau(formula)

def wk3_satisfiable(formula: Union[Formula, List[Formula]]) -> bool:
    """Test WK3 satisfiability using signed tableaux"""
    tableau = wk3_tableau(formula)
    return tableau.build()

def wk3_models(formula: Union[Formula, List[Formula]]) -> List[WK3SignedModel]:
    """Extract all WK3 models using signed tableaux"""
    tableau = wk3_tableau(formula)
    tableau.build()
    return tableau.extract_all_models()


# Export the main classes and functions
__all__ = [
    'WK3SignedModel', 'WK3SignedTableau',
    'wk3_tableau', 'wk3_satisfiable', 'wk3_models'
]