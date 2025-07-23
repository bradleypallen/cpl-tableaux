#!/usr/bin/env python3
"""
Signed Tableau System

A general-purpose signed tableau implementation that works with any sign system,
following the standard approach in tableau literature (Smullyan, Priest, Fitting).
"""

from typing import List, Set, Dict, Optional, Union, Tuple, Any
from dataclasses import dataclass
import copy

from formula import Formula, Atom
from signed_formula import SignedFormula, Sign, SignRegistry
from signed_tableau_rules import SignedRuleRegistry, SignedTableauRule, SignedRuleResult
from tableau import TableauNode  # Reuse existing node structure
from formula import RuleType


@dataclass
class SignedModel:
    """A model for signed tableaux - maps formulas to their signs"""
    assignments: Dict[Formula, Sign]
    sign_system: str
    
    def satisfies(self, signed_formula: SignedFormula) -> bool:
        """Check if this model satisfies a signed formula"""
        if signed_formula.formula in self.assignments:
            return self.assignments[signed_formula.formula] == signed_formula.sign
        return False
    
    def __str__(self) -> str:
        if not self.assignments:
            return f"SignedModel({self.sign_system}): {{}}"
        
        items = []
        for formula, sign in self.assignments.items():
            items.append(f"{sign}:{formula}")
        
        return f"SignedModel({self.sign_system}): {{{', '.join(items)}}}"


class SignedBranch:
    """A branch in a signed tableau"""
    
    def __init__(self, branch_id: int, signed_formulas: Set[SignedFormula] = None, 
                 parent: Optional['SignedBranch'] = None):
        self.id = branch_id
        self.parent = parent
        
        # Store signed formulas
        self.local_signed_formulas: Set[SignedFormula] = (
            signed_formulas if signed_formulas is not None else set()
        )
        
        # Track processed formulas to prevent infinite expansion
        self.processed_signed_formulas: Set[SignedFormula] = set()
        
        self.is_closed = False
        self.closure_reason: Optional[Tuple[SignedFormula, SignedFormula]] = None
        
        # Optimization: index by formula for fast contradiction detection
        self.formula_to_signs: Dict[Formula, Set[Sign]] = {}
        
        self._rebuild_formula_index()
        self._check_closure()
    
    @property
    def signed_formulas(self) -> Set[SignedFormula]:
        """Get all signed formulas in this branch (including inherited)"""
        all_formulas = set(self.local_signed_formulas)
        current = self.parent
        while current is not None:
            all_formulas.update(current.local_signed_formulas)
            current = current.parent
        return all_formulas
    
    def add_signed_formula(self, signed_formula: SignedFormula):
        """Add a signed formula to this branch"""
        self.local_signed_formulas.add(signed_formula)
        self._add_to_formula_index(signed_formula)
        self._check_closure()
    
    def add_signed_formulas(self, signed_formulas: List[SignedFormula]):
        """Add multiple signed formulas to this branch"""
        for sf in signed_formulas:
            self.local_signed_formulas.add(sf)
            self._add_to_formula_index(sf)
        self._check_closure()
    
    def _rebuild_formula_index(self):
        """Rebuild the formula-to-signs index"""
        self.formula_to_signs.clear()
        for signed_formula in self.signed_formulas:
            self._add_to_formula_index(signed_formula)
    
    def _add_to_formula_index(self, signed_formula: SignedFormula):
        """Add a signed formula to the index"""
        formula = signed_formula.formula
        if formula not in self.formula_to_signs:
            self.formula_to_signs[formula] = set()
        self.formula_to_signs[formula].add(signed_formula.sign)
    
    def _check_closure(self):
        """Check if this branch should be closed due to contradictions"""
        if self.is_closed:
            return
        
        # Look for contradictory signed formulas
        for formula, signs in self.formula_to_signs.items():
            signs_list = list(signs)
            for i, sign1 in enumerate(signs_list):
                for j, sign2 in enumerate(signs_list[i+1:], i+1):
                    if sign1.is_contradictory_with(sign2):
                        # Found contradiction - close branch
                        sf1 = SignedFormula(sign1, formula)
                        sf2 = SignedFormula(sign2, formula)
                        self.is_closed = True
                        self.closure_reason = (sf1, sf2)
                        return
    
    def get_expandable_signed_formulas(self, rule_registry: SignedRuleRegistry,
                                     sign_system: str = "classical") -> List[SignedFormula]:
        """Get signed formulas that can be expanded with rules"""
        expandable = []
        
        for signed_formula in self.signed_formulas:
            if signed_formula in self.processed_signed_formulas:
                continue
                
            # Check if any rule applies
            applicable_rules = rule_registry.find_applicable_rules(signed_formula, sign_system)
            if applicable_rules:
                expandable.append(signed_formula)
        
        # Sort by complexity (simpler formulas first) and rule priority
        def get_priority(sf: SignedFormula) -> Tuple[int, int]:
            rule = rule_registry.get_best_rule(sf, sign_system)
            rule_priority = rule.get_priority() if rule else 999
            formula_complexity = sf.get_complexity()
            return (rule_priority, formula_complexity)
        
        return sorted(expandable, key=get_priority)
    
    def mark_processed(self, signed_formula: SignedFormula):
        """Mark a signed formula as processed"""
        self.processed_signed_formulas.add(signed_formula)
    
    def extract_model(self, sign_system: str = "classical") -> Optional[SignedModel]:
        """Extract a model from this open, fully expanded branch"""
        if self.is_closed:
            return None
        
        # Extract assignments for atomic formulas
        assignments = {}
        for signed_formula in self.signed_formulas:
            if signed_formula.formula.is_atomic():
                assignments[signed_formula.formula] = signed_formula.sign
        
        # For unassigned atoms, we need to assign them consistently
        # This is a simplified approach - full model completion is more complex
        
        return SignedModel(assignments, sign_system)
    
    def subsumes(self, other: 'SignedBranch') -> bool:
        """Check if this branch subsumes another (for optimization)"""
        if self.is_closed or other.is_closed:
            return False
        return self.signed_formulas.issubset(other.signed_formulas)


class SignedTableau:
    """A signed tableau system that works with any sign system"""
    
    def __init__(self, initial_signed_formulas: Union[SignedFormula, List[SignedFormula]],
                 sign_system: str = "classical"):
        # Handle both single formula and list
        if isinstance(initial_signed_formulas, SignedFormula):
            self.initial_signed_formulas = [initial_signed_formulas]
        else:
            self.initial_signed_formulas = initial_signed_formulas
        
        self.sign_system = sign_system
        self.rule_registry = SignedRuleRegistry()
        
        # Tableau state
        self.node_counter = 0
        self.branch_counter = 0
        self.root_nodes: List[TableauNode] = []
        self.branches: List[SignedBranch] = []
        self.all_nodes: List[TableauNode] = []
        
        # Statistics
        self.rule_applications = 0
        self.branch_creations = 0
        
        # Built flag
        self.built = False
    
    def build(self) -> bool:
        """Build the signed tableau. Returns True if satisfiable."""
        if self.built:
            return self.is_satisfiable()
        
        # Create initial branch with all signed formulas
        initial_branch = SignedBranch(self._next_branch_id())
        for sf in self.initial_signed_formulas:
            initial_branch.add_signed_formula(sf)
        self.branches.append(initial_branch)
        
        # Create root nodes for tree structure
        for sf in self.initial_signed_formulas:
            root_node = self._create_node(sf, RuleType.INITIAL)
            self.root_nodes.append(root_node)
        
        # Main expansion loop
        while True:
            expansion_occurred = False
            
            # Early satisfiability check
            if self._has_satisfying_branch():
                break
            
            # Process each branch
            branches_to_process = self.branches.copy()
            
            for branch in branches_to_process:
                if branch.is_closed:
                    continue
                
                expandable = branch.get_expandable_signed_formulas(
                    self.rule_registry, self.sign_system
                )
                
                if expandable:
                    # Expand the first (highest priority) signed formula
                    signed_formula = expandable[0]
                    new_branches = self._expand_signed_formula_in_branch(
                        signed_formula, branch
                    )
                    if new_branches:
                        expansion_occurred = True
                        break  # Process one expansion per iteration
            
            if not expansion_occurred:
                break  # No more expansions possible
        
        self.built = True
        return self.is_satisfiable()
    
    def _expand_signed_formula_in_branch(self, signed_formula: SignedFormula, 
                                       branch: SignedBranch) -> List[SignedBranch]:
        """Expand a signed formula in a branch using tableau rules"""
        
        # Get the best rule for this signed formula
        rule = self.rule_registry.get_best_rule(signed_formula, self.sign_system)
        if not rule:
            return [branch]  # No applicable rule
        
        # Apply the rule
        result = rule.apply(signed_formula)
        self.rule_applications += 1
        
        # Mark the formula as processed
        branch.mark_processed(signed_formula)
        
        if result.is_alpha:
            # α-rule: add formulas to same branch
            if result.branches:
                branch.add_signed_formulas(result.branches[0])
            return [branch]
        else:
            # β-rule: create new branches
            new_branches = []
            
            # Remove the original branch
            if branch in self.branches:
                self.branches.remove(branch)
            
            for branch_formulas in result.branches:
                # Create new branch with existing formulas (except the expanded one)
                remaining_formulas = set(branch.signed_formulas) - {signed_formula}
                new_branch = SignedBranch(
                    self._next_branch_id(), 
                    signed_formulas=remaining_formulas
                )
                
                # Add the new formulas from the rule
                new_branch.add_signed_formulas(branch_formulas)
                
                # Copy processed formulas
                new_branch.processed_signed_formulas = branch.processed_signed_formulas.copy()
                new_branch.processed_signed_formulas.add(signed_formula)
                
                new_branches.append(new_branch)
                self.branch_creations += 1
            
            # Add new branches to active list
            self.branches.extend(new_branches)
            return new_branches
    
    def _next_branch_id(self) -> int:
        """Get next branch ID"""
        self.branch_counter += 1
        return self.branch_counter
    
    def _create_node(self, signed_formula: SignedFormula, rule_type: RuleType) -> TableauNode:
        """Create a tableau node (for tree structure)"""
        self.node_counter += 1
        node = TableauNode(
            id=self.node_counter,
            formula=signed_formula.formula,  # Store the formula part
            rule_applied=rule_type
        )
        self.all_nodes.append(node)
        return node
    
    def _has_satisfying_branch(self) -> bool:
        """Check if there's at least one satisfying branch"""
        for branch in self.branches:
            if not branch.is_closed:
                # Check if branch is fully expanded
                expandable = branch.get_expandable_signed_formulas(
                    self.rule_registry, self.sign_system
                )
                if not expandable:
                    return True  # Open and fully expanded
        return False
    
    def is_satisfiable(self) -> bool:
        """Check if the signed formula set is satisfiable"""
        return any(not branch.is_closed for branch in self.branches)
    
    def extract_all_models(self) -> List[SignedModel]:
        """Extract all satisfying models"""
        if not self.built:
            self.build()
        
        models = []
        for branch in self.branches:
            if not branch.is_closed:
                model = branch.extract_model(self.sign_system)
                if model:
                    models.append(model)
        
        return models
    
    def get_sample_model(self) -> Optional[SignedModel]:
        """Get one satisfying model"""
        models = self.extract_all_models()
        return models[0] if models else None
    
    def print_tableau(self):
        """Print the signed tableau"""
        print("=" * 70)
        print(f"SIGNED TABLEAU ({self.sign_system.upper()})")
        print("=" * 70)
        
        if len(self.initial_signed_formulas) == 1:
            print(f"Testing satisfiability of: {self.initial_signed_formulas[0]}")
        else:
            print(f"Testing satisfiability of {len(self.initial_signed_formulas)} signed formulas:")
            for i, sf in enumerate(self.initial_signed_formulas, 1):
                print(f"  {i}. {sf}")
        print()
        
        # Print branch summary
        open_branches = [b for b in self.branches if not b.is_closed]
        closed_branches = [b for b in self.branches if b.is_closed]
        
        print(f"Total branches: {len(self.branches)}")
        print(f"Open branches: {len(open_branches)}")
        print(f"Closed branches: {len(closed_branches)}")
        print(f"Rule applications: {self.rule_applications}")
        
        if open_branches:
            print("✓ SATISFIABLE")
            print("\nSample model:")
            model = self.get_sample_model()
            if model:
                print(f"  {model}")
        else:
            print("✗ UNSATISFIABLE")
        
        print("=" * 70)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tableau construction statistics"""
        open_branches = [b for b in self.branches if not b.is_closed]
        closed_branches = [b for b in self.branches if b.is_closed]
        
        return {
            "sign_system": self.sign_system,
            "initial_formulas": len(self.initial_signed_formulas),
            "total_branches": len(self.branches),
            "open_branches": len(open_branches),
            "closed_branches": len(closed_branches),
            "rule_applications": self.rule_applications,
            "branch_creations": self.branch_creations,
            "satisfiable": len(open_branches) > 0
        }


# Convenience functions for creating signed tableaux

def classical_signed_tableau(signed_formulas: Union[SignedFormula, List[SignedFormula]]) -> SignedTableau:
    """Create a classical signed tableau"""
    return SignedTableau(signed_formulas, "classical")

def three_valued_signed_tableau(signed_formulas: Union[SignedFormula, List[SignedFormula]]) -> SignedTableau:
    """Create a three-valued signed tableau"""  
    return SignedTableau(signed_formulas, "three_valued")


# Export main classes
__all__ = [
    'SignedModel', 'SignedBranch', 'SignedTableau',
    'classical_signed_tableau', 'three_valued_signed_tableau'
]