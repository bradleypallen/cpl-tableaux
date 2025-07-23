#!/usr/bin/env python3
"""
Signed Tableau Components

Components for integrating signed tableaux with the componentized architecture.
Provides signed tableau implementations of the abstract component interfaces.
"""

from typing import List, Dict, Set, Optional, Union, Any
from abc import ABC, abstractmethod

from formula import Formula, Atom
from signed_formula import SignedFormula, Sign, ClassicalSign, ThreeValuedSign, T, F, T3, F3, U
from signed_tableau import SignedTableau, SignedBranch, SignedModel
from tableau_rules import BranchInterface, RuleContext, TableauRule


class SignedBranchAdapter(BranchInterface):
    """
    Adapter that makes SignedBranch compatible with the componentized architecture.
    Wraps a SignedBranch to provide the BranchInterface.
    """
    
    def __init__(self, signed_branch: SignedBranch, logic_name: str = "classical"):
        self.signed_branch = signed_branch
        self.logic_name = logic_name
        self._formulas_cache = None
    
    @property
    def id(self) -> int:
        return self.signed_branch.id
    
    @property
    def is_closed(self) -> bool:
        return self.signed_branch.is_closed
    
    @property
    def formulas(self) -> List[Formula]:
        """Get formulas from signed formulas (cache for performance)"""
        if self._formulas_cache is None:
            self._formulas_cache = [sf.formula for sf in self.signed_branch.signed_formulas]
        return self._formulas_cache
    
    @property
    def signed_formulas(self) -> Set[SignedFormula]:
        """Get signed formulas directly"""
        return self.signed_branch.signed_formulas
    
    def add_formula(self, formula: Formula):
        """Add a formula as a signed formula (default to T:formula)"""
        if self.logic_name == "classical":
            signed_formula = T(formula)
        elif self.logic_name == "three_valued":
            signed_formula = T3(formula)
        else:
            # Default to T:formula
            signed_formula = T(formula)
        
        self.signed_branch.add_signed_formula(signed_formula)
        self._formulas_cache = None  # Invalidate cache
    
    def add_formulas(self, formulas: List[Formula]):
        """Add multiple formulas"""
        for formula in formulas:
            self.add_formula(formula)
    
    def add_signed_formula(self, signed_formula: SignedFormula):
        """Add a signed formula directly"""
        self.signed_branch.add_signed_formula(signed_formula)
        self._formulas_cache = None
    
    def add_signed_formulas(self, signed_formulas: List[SignedFormula]):
        """Add multiple signed formulas"""
        for sf in signed_formulas:
            self.signed_branch.add_signed_formula(sf)
        self._formulas_cache = None
    
    def get_domain_constants(self) -> List[Any]:
        """Get domain constants (for first-order logic)"""
        # Basic implementation - extract constants from formulas
        constants = []
        for formula in self.formulas:
            if hasattr(formula, 'args'):  # Predicate with arguments
                for arg in formula.args:
                    if hasattr(arg, 'name') and arg not in constants:
                        constants.append(arg)
        return constants
    
    def get_all_assignments(self) -> Dict[str, Any]:
        """Get truth assignments (convert from signed formulas)"""
        assignments = {}
        
        for signed_formula in self.signed_branch.signed_formulas:
            if signed_formula.formula.is_atomic():
                atom_str = str(signed_formula.formula)
                sign_str = str(signed_formula.sign)
                assignments[atom_str] = sign_str
        
        return assignments


class SignedBranchFactory:
    """Factory for creating signed branches"""
    
    def __init__(self, sign_system: str = "classical"):
        self.sign_system = sign_system
    
    def create_branch(self, branch_id: int, formulas: List[Formula] = None) -> SignedBranchAdapter:
        """Create a new signed branch"""
        signed_formulas = set()
        
        if formulas:
            for formula in formulas:
                if self.sign_system == "classical":
                    signed_formulas.add(T(formula))
                elif self.sign_system == "three_valued":
                    signed_formulas.add(T3(formula))
                else:
                    signed_formulas.add(T(formula))
        
        signed_branch = SignedBranch(branch_id, signed_formulas)
        return SignedBranchAdapter(signed_branch, self.sign_system)
    
    def copy_branch(self, original_branch: SignedBranchAdapter, new_id: int) -> SignedBranchAdapter:
        """Copy a signed branch with a new ID"""
        new_signed_formulas = set(original_branch.signed_branch.signed_formulas)
        new_signed_branch = SignedBranch(new_id, new_signed_formulas)
        return SignedBranchAdapter(new_signed_branch, self.sign_system)


class SignedClosureDetector:
    """Closure detector for signed tableaux"""
    
    def __init__(self, sign_system: str = "classical"):
        self.sign_system = sign_system
    
    def is_closed(self, branch: SignedBranchAdapter) -> bool:
        """Check if a signed branch is closed"""
        return branch.signed_branch.is_closed
    
    def get_closure_reason(self, branch: SignedBranchAdapter) -> Optional[str]:
        """Get the reason for closure"""
        if branch.signed_branch.closure_reason:
            sf1, sf2 = branch.signed_branch.closure_reason
            return f"Contradiction: {sf1} and {sf2}"
        return None


class SignedModelExtractor:
    """Model extractor for signed tableaux"""
    
    def __init__(self, sign_system: str = "classical"):
        self.sign_system = sign_system
    
    def extract_model(self, branch: SignedBranchAdapter) -> Optional[Dict[str, Any]]:
        """Extract a model from an open signed branch"""
        if branch.is_closed:
            return None
        
        signed_model = branch.signed_branch.extract_model(self.sign_system)
        if not signed_model:
            return None
        
        # Convert signed model to regular model format
        model = {}
        for formula, sign in signed_model.assignments.items():
            if isinstance(formula, Atom):
                if isinstance(sign, ClassicalSign):
                    model[formula.name] = sign.value
                elif isinstance(sign, ThreeValuedSign):
                    model[formula.name] = sign.get_truth_value()
                else:
                    model[formula.name] = str(sign)
        
        return model
    
    def extract_all_models(self, branches: List[SignedBranchAdapter]) -> List[Dict[str, Any]]:
        """Extract all models from open branches"""
        models = []
        for branch in branches:
            if not branch.is_closed:
                model = self.extract_model(branch)
                if model:
                    models.append(model)
        return models


class SignedLiteralRecognizer:
    """Literal recognizer for signed tableaux"""
    
    def __init__(self, sign_system: str = "classical"):
        self.sign_system = sign_system
    
    def is_literal(self, signed_formula: SignedFormula) -> bool:
        """Check if a signed formula is a literal"""
        return signed_formula.is_literal()
    
    def is_positive_literal(self, signed_formula: SignedFormula) -> bool:
        """Check if a signed formula is a positive literal"""
        return (signed_formula.is_literal() and 
                signed_formula.formula.is_atomic() and
                str(signed_formula.sign) == "T")
    
    def is_negative_literal(self, signed_formula: SignedFormula) -> bool:
        """Check if a signed formula is a negative literal"""
        from formula import Negation
        return (signed_formula.is_literal() and 
                isinstance(signed_formula.formula, Negation) and
                signed_formula.formula.operand.is_atomic() and
                str(signed_formula.sign) == "T")


class SignedSubsumptionDetector:
    """Subsumption detector for signed tableaux"""
    
    def __init__(self, sign_system: str = "classical"):
        self.sign_system = sign_system
    
    def subsumes(self, branch1: SignedBranchAdapter, branch2: SignedBranchAdapter) -> bool:
        """Check if branch1 subsumes branch2"""
        return branch1.signed_branch.subsumes(branch2.signed_branch)
    
    def remove_subsumed_branches(self, branches: List[SignedBranchAdapter]) -> List[SignedBranchAdapter]:
        """Remove subsumed branches from the list"""
        filtered_branches = []
        
        for i, branch in enumerate(branches):
            is_subsumed = False
            
            for j, other_branch in enumerate(branches):
                if i != j and other_branch.signed_branch.subsumes(branch.signed_branch):
                    is_subsumed = True
                    break
            
            if not is_subsumed:
                filtered_branches.append(branch)
        
        return filtered_branches


def create_signed_components(sign_system: str = "classical") -> Dict[str, Any]:
    """Create signed tableau components for a given sign system"""
    
    return {
        'branch_factory': SignedBranchFactory(sign_system),
        'closure_detector': SignedClosureDetector(sign_system),
        'model_extractor': SignedModelExtractor(sign_system),
        'literal_recognizer': SignedLiteralRecognizer(sign_system),
        'subsumption_detector': SignedSubsumptionDetector(sign_system)
    }


def create_classical_signed_components() -> Dict[str, Any]:
    """Create classical signed tableau components"""
    return create_signed_components("classical")


def create_three_valued_signed_components() -> Dict[str, Any]:
    """Create three-valued signed tableau components"""
    return create_signed_components("three_valued")


# Export main classes and functions
__all__ = [
    'SignedBranchAdapter', 'SignedBranchFactory', 'SignedClosureDetector',
    'SignedModelExtractor', 'SignedLiteralRecognizer', 'SignedSubsumptionDetector',
    'create_signed_components', 'create_classical_signed_components', 
    'create_three_valued_signed_components'
]