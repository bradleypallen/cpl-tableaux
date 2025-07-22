#!/usr/bin/env python3
"""
wKrQ Components - Branch Management and Model Extraction

Implements the component interfaces for wKrQ (Weak Kleene Logic with 
Restricted Quantifiers) including branch management with domain tracking
and three-valued model extraction.
"""

from typing import List, Set, Dict, Optional, Any
from tableau_rules import BranchInterface
from formula import Formula, Predicate, Negation, RestrictedExistentialQuantifier, RestrictedUniversalQuantifier
from term import Constant, Variable, Term
from truth_value import TruthValue, t, f, e, WeakKleeneOperators, RestrictedQuantifierOperators


class WKrQ_Branch(BranchInterface):
    """
    Branch implementation for wKrQ with three-valued assignments and domain management.
    
    Extends standard branching with:
    - Three-valued truth assignments for atomic predicates
    - Domain tracking for quantifier instantiation
    - Fresh constant generation for witnesses
    - Quantifier application tracking
    """
    
    def __init__(self, branch_id: int, formulas: List[Formula] = None):
        self._id = branch_id
        self._formulas = list(formulas) if formulas else []
        self._is_closed = False
        self._closure_reason: Optional[str] = None
        
        # Three-valued assignments for atomic formulas
        # Key format: "predicate_name(arg1,arg2,...)" -> TruthValue
        self._assignments: Dict[str, TruthValue] = {}
        
        # Domain management for quantifiers
        self._domain: Set[Constant] = set()
        self._fresh_constant_counter = 0
        
        # Quantifier tracking
        self._applied_universals: Set[str] = set()  # Track applied ∀̌ formulas
        self._generated_witnesses: Dict[str, List[Constant]] = {}  # ∃̌ witnesses
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def is_closed(self) -> bool:
        return self._is_closed
    
    @property
    def formulas(self) -> List[Formula]:
        return self._formulas.copy()
    
    def add_formula(self, formula: Formula) -> None:
        """Add formula and check for closure"""
        if formula not in self._formulas:
            self._formulas.append(formula)
            self._check_closure()
    
    def copy(self) -> 'WKrQ_Branch':
        """Create deep copy of this branch"""
        new_branch = WKrQ_Branch(self._id, self._formulas.copy())
        new_branch._assignments = self._assignments.copy()
        new_branch._domain = self._domain.copy()
        new_branch._fresh_constant_counter = self._fresh_constant_counter
        new_branch._applied_universals = self._applied_universals.copy()
        new_branch._generated_witnesses = {
            k: v.copy() for k, v in self._generated_witnesses.items()
        }
        new_branch._is_closed = self._is_closed
        new_branch._closure_reason = self._closure_reason
        return new_branch
    
    def close_branch(self, reason: str) -> None:
        """Manually close branch with reason"""
        self._is_closed = True
        self._closure_reason = reason
    
    # Domain management methods
    
    def add_to_domain(self, constant: Constant) -> None:
        """Add constant to the domain of quantification"""
        self._domain.add(constant)
        
        # Re-apply any universal quantifiers with new constant
        self._trigger_universal_reapplication()
    
    def generate_fresh_constant(self, base_name: str = "c") -> Constant:
        """Generate a fresh constant for witness generation"""
        while True:
            candidate_name = f"{base_name}_{self._fresh_constant_counter}"
            self._fresh_constant_counter += 1
            
            # Check if this name conflicts with existing constants
            if not any(c.name == candidate_name for c in self._domain):
                fresh_constant = Constant(candidate_name)
                self.add_to_domain(fresh_constant)
                return fresh_constant
    
    def get_domain_constants(self) -> List[Constant]:
        """Get all constants in the current domain"""
        return list(self._domain)
    
    # Three-valued assignment methods
    
    def add_predicate_assignment(self, predicate_key: str, value: TruthValue) -> None:
        """Add three-valued assignment for predicate"""
        existing = self._assignments.get(predicate_key)
        
        if existing is not None and existing != value:
            # Check for three-valued contradiction
            if existing in [t, f] and value in [t, f] and existing != value:
                self.close_branch(f"Three-valued contradiction: {predicate_key}={existing} vs {predicate_key}={value}")
            elif existing != e and value != e and existing != value:
                self.close_branch(f"Truth value conflict: {predicate_key}={existing} vs {predicate_key}={value}")
        else:
            self._assignments[predicate_key] = value
    
    def get_predicate_assignment(self, predicate_key: str) -> Optional[TruthValue]:
        """Get assignment for predicate (None if unassigned)"""
        return self._assignments.get(predicate_key)
    
    def get_all_assignments(self) -> Dict[str, TruthValue]:
        """Get copy of all predicate assignments"""
        return self._assignments.copy()
    
    # Quantifier tracking methods
    
    def mark_universal_applied(self, formula_key: str) -> None:
        """Mark universal quantifier as applied"""
        self._applied_universals.add(formula_key)
    
    def is_universal_applied(self, formula_key: str) -> bool:
        """Check if universal quantifier has been applied"""
        return formula_key in self._applied_universals
    
    def add_existential_witness(self, formula_key: str, constant: Constant) -> None:
        """Track witness constant for existential quantifier"""
        if formula_key not in self._generated_witnesses:
            self._generated_witnesses[formula_key] = []
        self._generated_witnesses[formula_key].append(constant)
    
    def get_existential_witnesses(self, formula_key: str) -> List[Constant]:
        """Get witness constants for existential quantifier"""
        return self._generated_witnesses.get(formula_key, [])
    
    # Private methods
    
    def _check_closure(self) -> None:
        """Check if branch contains a three-valued contradiction"""
        if self._is_closed:
            return
        
        # Extract atomic assignments from formulas
        for formula in self._formulas:
            self._process_formula_for_closure(formula)
    
    def _process_formula_for_closure(self, formula: Formula) -> None:
        """Process formula to extract atomic assignments and check closure"""
        if isinstance(formula, Predicate):
            # Positive atomic formula
            key = self._predicate_to_key(formula)
            if key:
                self.add_predicate_assignment(key, t)
        
        elif isinstance(formula, Negation) and isinstance(formula.operand, Predicate):
            # Negative atomic formula
            key = self._predicate_to_key(formula.operand)
            if key:
                self.add_predicate_assignment(key, f)
    
    def _predicate_to_key(self, predicate: Predicate) -> Optional[str]:
        """Convert predicate to string key for assignment tracking"""
        try:
            if predicate.arity == 0:
                return predicate.predicate_name
            
            args_str = ','.join(str(arg) for arg in predicate.args)
            return f"{predicate.predicate_name}({args_str})"
        except Exception:
            return None
    
    def _trigger_universal_reapplication(self) -> None:
        """Trigger re-application of universal quantifiers when domain changes"""
        # This would be handled by the tableau engine in practice
        # For now, we just track that the domain has changed
        pass


class WKrQ_Model:
    """
    Three-valued first-order model for wKrQ logic.
    
    Represents a complete interpretation with:
    - Domain of individuals (constants)
    - Three-valued predicate assignments
    - Support for restricted quantifier evaluation
    """
    
    def __init__(self, domain: Dict[str, Constant], predicate_assignments: Dict[str, TruthValue]):
        self.domain = domain  # constant_name -> Constant object
        self.predicate_assignments = predicate_assignments  # predicate_key -> TruthValue
    
    def evaluate(self, formula: Formula) -> TruthValue:
        """Evaluate formula under this three-valued first-order model"""
        return self._evaluate_recursive(formula)
    
    def _evaluate_recursive(self, formula: Formula) -> TruthValue:
        """Recursive formula evaluation"""
        if isinstance(formula, Predicate):
            key = self._predicate_to_key(formula)
            return self.predicate_assignments.get(key, e)  # Default to undefined
        
        elif isinstance(formula, Negation):
            operand_value = self._evaluate_recursive(formula.operand)
            return WeakKleeneOperators.negation(operand_value)
        
        elif isinstance(formula, Conjunction):
            left_value = self._evaluate_recursive(formula.left)
            right_value = self._evaluate_recursive(formula.right)
            return WeakKleeneOperators.conjunction(left_value, right_value)
        
        elif isinstance(formula, Disjunction):
            left_value = self._evaluate_recursive(formula.left)
            right_value = self._evaluate_recursive(formula.right)
            return WeakKleeneOperators.disjunction(left_value, right_value)
        
        elif isinstance(formula, Implication):
            ante_value = self._evaluate_recursive(formula.antecedent)
            cons_value = self._evaluate_recursive(formula.consequent)
            return WeakKleeneOperators.implication(ante_value, cons_value)
        
        elif isinstance(formula, RestrictedExistentialQuantifier):
            return self._evaluate_restricted_existential(formula)
        
        elif isinstance(formula, RestrictedUniversalQuantifier):
            return self._evaluate_restricted_universal(formula)
        
        else:
            # Unknown formula type
            return e
    
    def _evaluate_restricted_existential(self, formula: RestrictedExistentialQuantifier) -> TruthValue:
        """Evaluate ∃̌xφ(x) using restricted quantifier semantics"""
        value_pairs = set()
        
        for constant in self.domain.values():
            # Create instantiated formula
            instantiated = self._substitute_variable(formula.body, formula.variable, constant)
            
            # For ∃̌, we need pairs ⟨φ(c), φ(c)⟩ (simplified case)
            value = self._evaluate_recursive(instantiated)
            value_pairs.add((value, value))
        
        if not value_pairs:
            return e  # Empty domain
        
        return RestrictedQuantifierOperators.restricted_existential(value_pairs)
    
    def _evaluate_restricted_universal(self, formula: RestrictedUniversalQuantifier) -> TruthValue:
        """Evaluate ∀̌xφ(x) using restricted quantifier semantics"""
        value_pairs = set()
        
        for constant in self.domain.values():
            # Create instantiated formula
            instantiated = self._substitute_variable(formula.body, formula.variable, constant)
            
            # For ∀̌, we need pairs ⟨φ(c), ¬φ(c)⟩
            value = self._evaluate_recursive(instantiated)
            neg_value = WeakKleeneOperators.negation(value)
            value_pairs.add((value, neg_value))
        
        if not value_pairs:
            return e  # Empty domain
        
        return RestrictedQuantifierOperators.restricted_universal(value_pairs)
    
    def _substitute_variable(self, formula: Formula, variable: Variable, constant: Constant) -> Formula:
        """Substitute variable with constant in formula"""
        # This would need proper implementation based on formula structure
        # For now, return formula unchanged (placeholder)
        return formula
    
    def _predicate_to_key(self, predicate: Predicate) -> str:
        """Convert predicate to string key"""
        if predicate.arity == 0:
            return predicate.predicate_name
        
        args_str = ','.join(str(arg) for arg in predicate.args)
        return f"{predicate.predicate_name}({args_str})"


class WKrQ_ModelExtractor:
    """
    Extracts three-valued first-order models from open wKrQ branches.
    
    Creates complete models by:
    - Extracting domain constants from the branch
    - Collecting three-valued predicate assignments
    - Providing default values for unassigned predicates
    """
    
    def extract_model(self, branch: WKrQ_Branch) -> WKrQ_Model:
        """Extract three-valued model from open branch"""
        if branch.is_closed:
            raise ValueError("Cannot extract model from closed branch")
        
        # Create domain from branch's domain constants
        domain = {}
        for constant in branch.get_domain_constants():
            domain[constant.name] = constant
        
        # If domain is empty, add at least one constant
        if not domain:
            default_constant = Constant("c_0")
            domain[default_constant.name] = default_constant
        
        # Extract predicate assignments from branch
        predicate_assignments = branch.get_all_assignments()
        
        # Create complete model
        return WKrQ_Model(domain, predicate_assignments)
    
    def extract_all_models(self, branches: List[WKrQ_Branch]) -> List[WKrQ_Model]:
        """Extract models from all open branches"""
        models = []
        for branch in branches:
            if not branch.is_closed:
                try:
                    model = self.extract_model(branch)
                    models.append(model)
                except Exception as e:
                    # Skip branches that cannot produce valid models
                    pass
        return models


# Component factory classes

class WKrQ_BranchFactory:
    """Factory for creating wKrQ branches"""
    
    def create_branch(self, branch_id: int, formulas: List[Formula] = None) -> WKrQ_Branch:
        """Create new wKrQ branch"""
        return WKrQ_Branch(branch_id, formulas)
    
    def copy_branch(self, original_branch: WKrQ_Branch, new_id: int) -> WKrQ_Branch:
        """Create copy of existing branch with new ID"""
        new_branch = original_branch.copy()
        new_branch._id = new_id
        return new_branch


class WKrQ_ClosureDetector:
    """Detects closure conditions specific to wKrQ logic"""
    
    def detect_closure(self, branch: WKrQ_Branch) -> Optional[str]:
        """Detect if branch should be closed"""
        if branch.is_closed:
            return branch._closure_reason
        
        # Additional closure detection logic could be added here
        return None


# Export all components
__all__ = [
    'WKrQ_Branch',
    'WKrQ_Model', 
    'WKrQ_ModelExtractor',
    'WKrQ_BranchFactory',
    'WKrQ_ClosureDetector'
]