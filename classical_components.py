#!/usr/bin/env python3
"""
Classical Logic Components

Concrete implementations of the logic-specific components for Classical
Propositional Logic, including branch management, closure detection, 
model extraction, and subsumption checking.
"""

from typing import List, Set, Optional, Dict, Any
from dataclasses import dataclass
from copy import deepcopy

from tableau_rules import (
    BranchInterface, BranchFactory, ClosureDetector, ModelExtractor,
    LiteralRecognizer, SubsumptionDetector
)
from formula import Formula, Atom, Negation


@dataclass
class ClassicalModel:
    """A two-valued model for classical propositional logic"""
    assignments: Dict[str, bool]
    
    def __str__(self) -> str:
        if not self.assignments:
            return "{}"
        
        sorted_items = sorted(self.assignments.items())
        assignment_strs = [f"{atom}={str(value).lower()}" for atom, value in sorted_items]
        return "{" + ", ".join(assignment_strs) + "}"
    
    def __repr__(self) -> str:
        return f"ClassicalModel({self.assignments})"
    
    def satisfies(self, formula: Formula) -> bool:
        """Check if this model satisfies the given formula"""
        return self._evaluate_formula(formula)
    
    def _evaluate_formula(self, formula: Formula) -> bool:
        """Recursively evaluate a formula under this model"""
        from formula import Conjunction, Disjunction, Implication
        
        if isinstance(formula, Atom):
            return self.assignments.get(formula.name, False)
        elif isinstance(formula, Negation):
            return not self._evaluate_formula(formula.operand)
        elif isinstance(formula, Conjunction):
            return (self._evaluate_formula(formula.left) and 
                   self._evaluate_formula(formula.right))
        elif isinstance(formula, Disjunction):
            return (self._evaluate_formula(formula.left) or 
                   self._evaluate_formula(formula.right))
        elif isinstance(formula, Implication):
            return (not self._evaluate_formula(formula.antecedent) or 
                   self._evaluate_formula(formula.consequent))
        else:
            raise ValueError(f"Unknown formula type: {type(formula)}")


class ClassicalBranch(BranchInterface):
    """Branch implementation for classical propositional logic"""
    
    def __init__(self, branch_id: int, formulas: List[Formula] = None):
        self._id = branch_id
        self._formulas = list(formulas) if formulas else []
        self._is_closed = False
        self._closure_reason = None
        
        # Performance optimization: index literals for fast closure detection
        self._positive_literals: Set[str] = set()
        self._negative_literals: Set[str] = set()
        self._update_literal_index()
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def is_closed(self) -> bool:
        return self._is_closed
    
    @property
    def formulas(self) -> List[Formula]:
        return list(self._formulas)  # Return copy to prevent external modification
    
    @property
    def closure_reason(self) -> Optional[str]:
        return self._closure_reason
    
    def add_formula(self, formula: Formula) -> None:
        """Add a formula to this branch and update closure status"""
        if formula not in self._formulas:
            self._formulas.append(formula)
            self._update_literal_index_for_formula(formula)
            self._check_closure()
    
    def add_formulas(self, formulas: List[Formula]) -> None:
        """Add multiple formulas efficiently"""
        new_formulas = [f for f in formulas if f not in self._formulas]
        if new_formulas:
            self._formulas.extend(new_formulas)
            for formula in new_formulas:
                self._update_literal_index_for_formula(formula)
            self._check_closure()
    
    def _update_literal_index(self) -> None:
        """Rebuild the complete literal index"""
        self._positive_literals.clear()
        self._negative_literals.clear()
        
        for formula in self._formulas:
            self._update_literal_index_for_formula(formula)
    
    def _update_literal_index_for_formula(self, formula: Formula) -> None:
        """Update literal index for a single formula"""
        if isinstance(formula, Atom):
            self._positive_literals.add(formula.name)
        elif isinstance(formula, Negation) and isinstance(formula.operand, Atom):
            self._negative_literals.add(formula.operand.name)
    
    def _check_closure(self) -> None:
        """Check if this branch contains a contradiction"""
        if self._is_closed:
            return  # Already closed
        
        # Look for complementary literals (A and ¬A)
        contradictory_atoms = self._positive_literals & self._negative_literals
        if contradictory_atoms:
            self._is_closed = True
            atom_name = next(iter(contradictory_atoms))  # Get one contradictory atom
            self._closure_reason = f"Contradiction: {atom_name} and ¬{atom_name}"
    
    def get_literal_assignment(self) -> Dict[str, bool]:
        """Extract boolean assignments from literals in this branch"""
        assignments = {}
        
        # Positive literals are assigned true
        for atom_name in self._positive_literals:
            assignments[atom_name] = True
        
        # Negative literals are assigned false  
        for atom_name in self._negative_literals:
            assignments[atom_name] = False
        
        return assignments
    
    def copy(self) -> 'ClassicalBranch':
        """Create a deep copy of this branch"""
        new_branch = ClassicalBranch(self._id, self._formulas.copy())
        new_branch._is_closed = self._is_closed
        new_branch._closure_reason = self._closure_reason
        return new_branch
    
    def __str__(self) -> str:
        status = "CLOSED" if self._is_closed else "OPEN"
        formula_strs = [str(f) for f in self._formulas]
        return f"Branch {self._id} ({status}): [{', '.join(formula_strs)}]"
    
    def __repr__(self) -> str:
        return f"ClassicalBranch(id={self._id}, formulas={len(self._formulas)}, closed={self._is_closed})"


class ClassicalBranchFactory(BranchFactory):
    """Factory for creating classical logic branches"""
    
    def create_branch(self, branch_id: int, formulas: List[Formula] = None) -> BranchInterface:
        """Create a new classical branch"""
        return ClassicalBranch(branch_id, formulas)
    
    def copy_branch(self, source_branch: BranchInterface, new_id: int) -> BranchInterface:
        """Create a copy of a branch with a new ID"""
        if not isinstance(source_branch, ClassicalBranch):
            raise ValueError(f"Expected ClassicalBranch, got {type(source_branch)}")
        
        new_branch = source_branch.copy()
        new_branch._id = new_id
        return new_branch


class ClassicalClosureDetector(ClosureDetector):
    """Closure detector for classical propositional logic"""
    
    def is_closed(self, branch: BranchInterface) -> bool:
        """Check if branch contains complementary literals"""
        if isinstance(branch, ClassicalBranch):
            return branch.is_closed
        
        # Fallback for generic branch interface
        return self._generic_closure_check(branch)
    
    def _generic_closure_check(self, branch: BranchInterface) -> bool:
        """Generic closure check for any branch implementation"""
        positive_atoms = set()
        negative_atoms = set()
        
        for formula in branch.formulas:
            if isinstance(formula, Atom):
                positive_atoms.add(formula.name)
            elif isinstance(formula, Negation) and isinstance(formula.operand, Atom):
                negative_atoms.add(formula.operand.name)
        
        return bool(positive_atoms & negative_atoms)
    
    def get_closure_reason(self, branch: BranchInterface) -> Optional[str]:
        """Get explanation for why branch is closed"""
        if isinstance(branch, ClassicalBranch):
            return branch.closure_reason
        
        # Generic fallback
        if self._generic_closure_check(branch):
            return "Contains complementary literals"
        return None


class ClassicalModelExtractor(ModelExtractor):
    """Model extractor for classical propositional logic"""
    
    def extract_model(self, branch: BranchInterface) -> ClassicalModel:
        """Extract a two-valued model from an open branch"""
        if branch.is_closed:
            raise ValueError("Cannot extract model from closed branch")
        
        if isinstance(branch, ClassicalBranch):
            assignments = branch.get_literal_assignment()
        else:
            # Generic fallback
            assignments = self._extract_generic_assignments(branch)
        
        return ClassicalModel(assignments)
    
    def _extract_generic_assignments(self, branch: BranchInterface) -> Dict[str, bool]:
        """Extract assignments from any branch implementation"""
        assignments = {}
        
        for formula in branch.formulas:
            if isinstance(formula, Atom):
                assignments[formula.name] = True
            elif isinstance(formula, Negation) and isinstance(formula.operand, Atom):
                assignments[formula.operand.name] = False
        
        return assignments
    
    def extract_all_models(self, branches: List[BranchInterface]) -> List[ClassicalModel]:
        """Extract models from all open branches"""
        models = []
        
        for branch in branches:
            if not branch.is_closed:
                model = self.extract_model(branch)
                models.append(model)
        
        return models


class ClassicalLiteralRecognizer(LiteralRecognizer):
    """Recognizer for classical propositional literals"""
    
    def is_literal(self, formula: Formula) -> bool:
        """Check if formula is a literal (atom or negated atom)"""
        if isinstance(formula, Atom):
            return True
        elif isinstance(formula, Negation) and isinstance(formula.operand, Atom):
            return True
        else:
            return False
    
    def get_literal_value(self, formula: Formula, branch: BranchInterface) -> Optional[bool]:
        """Get the truth value of a literal in the branch context"""
        if not self.is_literal(formula):
            return None
        
        if isinstance(formula, Atom):
            return True
        elif isinstance(formula, Negation) and isinstance(formula.operand, Atom):
            return False
        else:
            return None


class ClassicalSubsumptionDetector(SubsumptionDetector):
    """Subsumption detector for classical branches"""
    
    def is_subsumed(self, branch: BranchInterface, other_branches: List[BranchInterface]) -> bool:
        """Check if branch is subsumed by any other branch"""
        if branch.is_closed:
            return False  # Closed branches are not subsumed
        
        branch_formulas = set(str(f) for f in branch.formulas)
        
        for other in other_branches:
            if other.id == branch.id or other.is_closed:
                continue
            
            other_formulas = set(str(f) for f in other.formulas)
            
            # Branch is subsumed if its formulas are a superset of another's
            if branch_formulas.issuperset(other_formulas) and branch_formulas != other_formulas:
                return True
        
        return False
    
    def remove_subsumed_branches(self, branches: List[BranchInterface]) -> List[BranchInterface]:
        """Remove all subsumed branches from the list"""
        if len(branches) <= 1:
            return branches
        
        non_subsumed = []
        
        for branch in branches:
            if not self.is_subsumed(branch, branches):
                non_subsumed.append(branch)
        
        return non_subsumed


# Factory function for creating all classical components
def create_classical_components():
    """Create a complete set of classical logic components"""
    return {
        'branch_factory': ClassicalBranchFactory(),
        'closure_detector': ClassicalClosureDetector(),
        'model_extractor': ClassicalModelExtractor(),
        'literal_recognizer': ClassicalLiteralRecognizer(),
        'subsumption_detector': ClassicalSubsumptionDetector()
    }


# Export all component classes and factory
__all__ = [
    'ClassicalModel',
    'ClassicalBranch',
    'ClassicalBranchFactory',
    'ClassicalClosureDetector', 
    'ClassicalModelExtractor',
    'ClassicalLiteralRecognizer',
    'ClassicalSubsumptionDetector',
    'create_classical_components'
]