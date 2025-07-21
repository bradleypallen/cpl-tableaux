#!/usr/bin/env python3
"""
WK3 Logic Components

Concrete implementations of the logic-specific components for Weak Kleene Logic (WK3),
including three-valued branch management, closure detection, and model extraction.
"""

from typing import List, Set, Optional, Dict, Any
from dataclasses import dataclass
from copy import deepcopy

from tableau_rules import (
    BranchInterface, BranchFactory, ClosureDetector, ModelExtractor,
    LiteralRecognizer, SubsumptionDetector
)
from formula import Formula, Atom, Negation
from truth_value import TruthValue, t, f, e
from wk3_model import WK3Model


class WK3Branch(BranchInterface):
    """Branch implementation for WK3 three-valued logic"""
    
    def __init__(self, branch_id: int, formulas: List[Formula] = None):
        self._id = branch_id
        self._formulas = list(formulas) if formulas else []
        self._assignments = {}  # Dict[str, TruthValue] - atom assignments
        self._is_closed = False
        self._closure_reason = None
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def is_closed(self) -> bool:
        return self._is_closed
    
    @property
    def formulas(self) -> List[Formula]:
        return list(self._formulas)
    
    @property
    def assignments(self) -> Dict[str, TruthValue]:
        """Get current three-valued assignments"""
        return dict(self._assignments)
    
    @property
    def closure_reason(self) -> Optional[str]:
        return self._closure_reason
    
    def add_formula(self, formula: Formula) -> None:
        """Add a formula to this branch"""
        if formula not in self._formulas:
            self._formulas.append(formula)
            self._process_formula_for_assignment(formula)
            self._check_closure()
    
    def add_formulas(self, formulas: List[Formula]) -> None:
        """Add multiple formulas efficiently"""
        new_formulas = [f for f in formulas if f not in self._formulas]
        if new_formulas:
            self._formulas.extend(new_formulas)
            for formula in new_formulas:
                self._process_formula_for_assignment(formula)
            self._check_closure()
    
    def add_assignment(self, atom_name: str, value: TruthValue) -> None:
        """Add a three-valued assignment directly"""
        if atom_name in self._assignments:
            # Check for conflict
            if self._assignments[atom_name] != value:
                # Conflicting assignments - close the branch
                self._is_closed = True
                self._closure_reason = f"Conflicting assignments: {atom_name}={self._assignments[atom_name]} and {atom_name}={value}"
                return
        else:
            self._assignments[atom_name] = value
            self._check_closure()
    
    def _process_formula_for_assignment(self, formula: Formula) -> None:
        """
        Process a formula to see if it can be converted to an assignment.
        In WK3, literals should eventually become assignments.
        """
        if isinstance(formula, Atom):
            # Positive literal: this atom should be true or undefined
            # For now, we don't automatically assign - the tableau expansion will handle this
            pass
        elif isinstance(formula, Negation) and isinstance(formula.operand, Atom):
            # Negative literal: this atom should be false or undefined
            pass
    
    def _check_closure(self) -> None:
        """
        Check if this branch is closed.
        In WK3, a branch is closed only if an atom has both t and f assignments.
        """
        if self._is_closed:
            return
        
        # Look for contradictory assignments (A=t and A=f)
        # Note: A=e is compatible with both A=t and A=f assignments in some interpretations
        # But direct conflicting assignments (t vs f) close the branch
        
        # This is already handled in add_assignment method
        pass
    
    def get_wk3_model(self) -> WK3Model:
        """Extract a WK3 model from this branch"""
        if self.is_closed:
            raise ValueError("Cannot extract model from closed branch")
        
        return WK3Model(self._assignments)
    
    def copy(self) -> 'WK3Branch':
        """Create a deep copy of this branch"""
        new_branch = WK3Branch(self._id, self._formulas.copy())
        new_branch._assignments = self._assignments.copy()
        new_branch._is_closed = self._is_closed
        new_branch._closure_reason = self._closure_reason
        return new_branch
    
    def copy_with_assignment(self, atom_name: str, value: TruthValue) -> 'WK3Branch':
        """Create a copy of this branch with an additional assignment"""
        new_branch = self.copy()
        new_branch.add_assignment(atom_name, value)
        return new_branch
    
    def __str__(self) -> str:
        status = "CLOSED" if self._is_closed else "OPEN"
        formula_strs = [str(f) for f in self._formulas]
        assignment_strs = [f"{atom}={value}" for atom, value in self._assignments.items()]
        
        parts = []
        if formula_strs:
            parts.append(f"Formulas: [{', '.join(formula_strs)}]")
        if assignment_strs:
            parts.append(f"Assignments: [{', '.join(assignment_strs)}]")
        
        content = "; ".join(parts) if parts else "Empty"
        return f"WK3Branch {self._id} ({status}): {content}"
    
    def __repr__(self) -> str:
        return f"WK3Branch(id={self._id}, formulas={len(self._formulas)}, assignments={len(self._assignments)}, closed={self._is_closed})"


class WK3BranchFactory(BranchFactory):
    """Factory for creating WK3 logic branches"""
    
    def create_branch(self, branch_id: int, formulas: List[Formula] = None) -> BranchInterface:
        """Create a new WK3 branch"""
        return WK3Branch(branch_id, formulas)
    
    def copy_branch(self, source_branch: BranchInterface, new_id: int) -> BranchInterface:
        """Create a copy of a branch with a new ID"""
        if not isinstance(source_branch, WK3Branch):
            raise ValueError(f"Expected WK3Branch, got {type(source_branch)}")
        
        new_branch = source_branch.copy()
        new_branch._id = new_id
        return new_branch


class WK3ClosureDetector(ClosureDetector):
    """Closure detector for WK3 logic"""
    
    def is_closed(self, branch: BranchInterface) -> bool:
        """
        Check if branch is closed.
        In WK3, a branch is closed only if an atom has conflicting assignments (t and f).
        """
        if isinstance(branch, WK3Branch):
            return branch.is_closed
        
        # Generic fallback - shouldn't happen with proper WK3 usage
        return False
    
    def get_closure_reason(self, branch: BranchInterface) -> Optional[str]:
        """Get explanation for why branch is closed"""
        if isinstance(branch, WK3Branch):
            return branch.closure_reason
        return None


class WK3ModelExtractor(ModelExtractor):
    """Model extractor for WK3 logic"""
    
    def extract_model(self, branch: BranchInterface) -> WK3Model:
        """Extract a three-valued model from an open branch"""
        if branch.is_closed:
            raise ValueError("Cannot extract model from closed branch")
        
        if isinstance(branch, WK3Branch):
            return branch.get_wk3_model()
        else:
            # Generic fallback
            return WK3Model({})
    
    def extract_all_models(self, branches: List[BranchInterface]) -> List[WK3Model]:
        """Extract models from all open branches"""
        models = []
        
        for branch in branches:
            if not branch.is_closed:
                model = self.extract_model(branch)
                models.append(model)
        
        return models


class WK3LiteralRecognizer(LiteralRecognizer):
    """Recognizer for WK3 literals"""
    
    def is_literal(self, formula: Formula) -> bool:
        """
        Check if formula is a literal.
        In WK3, literals are atoms or negated atoms that need assignment processing.
        """
        if isinstance(formula, Atom):
            return True
        elif isinstance(formula, Negation) and isinstance(formula.operand, Atom):
            return True
        else:
            return False
    
    def get_literal_value(self, formula: Formula, branch: BranchInterface) -> Optional[TruthValue]:
        """Get the three-valued assignment for a literal"""
        if not self.is_literal(formula):
            return None
        
        if not isinstance(branch, WK3Branch):
            return None
        
        if isinstance(formula, Atom):
            return branch.assignments.get(formula.name)
        elif isinstance(formula, Negation) and isinstance(formula.operand, Atom):
            atom_value = branch.assignments.get(formula.operand.name)
            if atom_value is not None:
                # Return negation of the atom's value
                return atom_value.negate()
            return None
        else:
            return None


class WK3SubsumptionDetector(SubsumptionDetector):
    """Subsumption detector for WK3 branches"""
    
    def is_subsumed(self, branch: BranchInterface, other_branches: List[BranchInterface]) -> bool:
        """Check if branch is subsumed by any other branch"""
        if branch.is_closed:
            return False
        
        if not isinstance(branch, WK3Branch):
            return False
        
        branch_formulas = set(str(f) for f in branch.formulas)
        branch_assignments = branch.assignments
        
        for other in other_branches:
            if other.id == branch.id or other.is_closed or not isinstance(other, WK3Branch):
                continue
            
            other_formulas = set(str(f) for f in other.formulas)
            other_assignments = other.assignments
            
            # Branch is subsumed if another branch has fewer formulas and assignments
            # but covers the same logical space
            formulas_subsumed = branch_formulas.issuperset(other_formulas)
            assignments_subsumed = self._assignments_subsumed(branch_assignments, other_assignments)
            
            if formulas_subsumed and assignments_subsumed and (
                branch_formulas != other_formulas or branch_assignments != other_assignments):
                return True
        
        return False
    
    def _assignments_subsumed(self, branch_assignments: Dict[str, TruthValue], 
                             other_assignments: Dict[str, TruthValue]) -> bool:
        """Check if branch assignments are subsumed by other assignments"""
        # Branch is subsumed if it has all the assignments of the other branch
        for atom, value in other_assignments.items():
            if atom not in branch_assignments or branch_assignments[atom] != value:
                return False
        return True
    
    def remove_subsumed_branches(self, branches: List[BranchInterface]) -> List[BranchInterface]:
        """Remove all subsumed branches from the list"""
        if len(branches) <= 1:
            return branches
        
        non_subsumed = []
        
        for branch in branches:
            if not self.is_subsumed(branch, branches):
                non_subsumed.append(branch)
        
        return non_subsumed


# Factory function for creating all WK3 components
def create_wk3_components():
    """Create a complete set of WK3 logic components"""
    return {
        'branch_factory': WK3BranchFactory(),
        'closure_detector': WK3ClosureDetector(),
        'model_extractor': WK3ModelExtractor(),
        'literal_recognizer': WK3LiteralRecognizer(),
        'subsumption_detector': WK3SubsumptionDetector()
    }


# Export all component classes and factory
__all__ = [
    'WK3Branch',
    'WK3BranchFactory',
    'WK3ClosureDetector',
    'WK3ModelExtractor',
    'WK3LiteralRecognizer', 
    'WK3SubsumptionDetector',
    'create_wk3_components'
]