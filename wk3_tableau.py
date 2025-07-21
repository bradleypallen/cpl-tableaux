#!/usr/bin/env python3
"""
Weak Kleene Logic Tableau Implementation

Extends the tableau system to support three-valued weak Kleene logic
with proper three-valued branching and closure detection.
"""

from abc import ABC, abstractmethod
from typing import List, Set, Optional, Tuple, Dict, Union
from dataclasses import dataclass
from enum import Enum
import copy

from truth_value import TruthValue, t, f, e
from wk3_model import WK3Model
from formula import Formula, Atom, Negation, Conjunction, Disjunction, Implication, RuleType
from tableau import TableauNode  # Reuse the node structure


@dataclass
class WK3Assignment:
    """Represents a three-valued assignment to an atom"""
    atom_name: str
    value: TruthValue
    
    def __str__(self) -> str:
        return f"{self.atom_name}={self.value}"
    
    def __repr__(self) -> str:
        return f"WK3Assignment({self.atom_name}, {self.value})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, WK3Assignment):
            return False
        return self.atom_name == other.atom_name and self.value == other.value
    
    def __hash__(self) -> int:
        return hash((self.atom_name, self.value))


class WK3Branch:
    """Branch in a weak Kleene tableau with three-valued assignments"""
    
    def __init__(self, branch_id: int, formulas: Set[Formula] = None, 
                 assignments: Set[WK3Assignment] = None, parent: Optional['WK3Branch'] = None):
        self.id = branch_id
        self.parent = parent
        
        # Store formulas and assignments separately
        self.local_formulas: Set[Formula] = formulas if formulas is not None else set()
        self.local_assignments: Set[WK3Assignment] = assignments if assignments is not None else set()
        
        # Track processed formulas to prevent infinite expansion
        self.local_processed_formulas: Set[Formula] = set()
        
        self.is_closed = False
        self.closure_reason: Optional[Tuple[WK3Assignment, WK3Assignment]] = None
        
        # Three-valued literal indexing for fast closure detection
        self.atom_assignments: Dict[str, Set[TruthValue]] = {}  # atom -> set of assigned values
        
        # Cycle detection
        self._state_signatures: List[int] = []
        self._signatures_enabled = False
        
        self._rebuild_assignment_index()
        self._check_closure_optimized()
        
        # Enable signature tracking after initialization
        self._signatures_enabled = True
        self._update_signature()
    
    @property
    def formulas(self) -> Set[Formula]:
        """Get all formulas in this branch (including inherited from parents)"""
        all_formulas = set(self.local_formulas)
        current = self.parent
        while current is not None:
            all_formulas.update(current.local_formulas)
            current = current.parent
        return all_formulas
    
    @property
    def assignments(self) -> Set[WK3Assignment]:
        """Get all assignments in this branch (including inherited from parents)"""
        all_assignments = set(self.local_assignments)
        current = self.parent
        while current is not None:
            all_assignments.update(current.local_assignments)
            current = current.parent
        return all_assignments
    
    @property
    def processed_formulas(self) -> Set[Formula]:
        """Get all processed formulas in this branch (including inherited from parents)"""
        all_processed = set(self.local_processed_formulas)
        current = self.parent
        while current is not None:
            all_processed.update(current.local_processed_formulas)
            current = current.parent
        return all_processed
    
    def add_formula(self, formula: Formula):
        """Add a formula to this branch"""
        self.local_formulas.add(formula)
        self._update_signature()
    
    def add_assignment(self, assignment: WK3Assignment):
        """Add a three-valued assignment to this branch"""
        self.local_assignments.add(assignment)
        self._update_assignment_index(assignment)
        self._check_closure_optimized()
        self._update_signature()
    
    def add_atom_value(self, atom_name: str, value: TruthValue):
        """Convenience method to add an atom assignment"""
        assignment = WK3Assignment(atom_name, value)
        self.add_assignment(assignment)
    
    def copy_with_new_id(self, new_id: int) -> 'WK3Branch':
        """Create a copy of this branch with a new ID"""
        new_branch = WK3Branch(new_id, parent=self)
        # Copy the processed formulas to the new branch
        new_branch.local_processed_formulas.update(self.processed_formulas)
        return new_branch
    
    def create_child_with_formula(self, new_id: int, formula: Formula) -> 'WK3Branch':
        """Create a child branch with an additional formula"""
        child_branch = WK3Branch(new_id, formulas={formula}, parent=self)
        return child_branch
    
    def create_child_with_assignment(self, new_id: int, assignment: WK3Assignment) -> 'WK3Branch':
        """Create a child branch with an additional assignment"""
        child_branch = WK3Branch(new_id, assignments={assignment}, parent=self)
        return child_branch
    
    def _rebuild_assignment_index(self):
        """Rebuild the assignment index from all assignments in the branch"""
        self.atom_assignments.clear()
        
        for assignment in self.assignments:
            if assignment.atom_name not in self.atom_assignments:
                self.atom_assignments[assignment.atom_name] = set()
            self.atom_assignments[assignment.atom_name].add(assignment.value)
    
    def _update_assignment_index(self, assignment: WK3Assignment):
        """Update assignment index with a new assignment"""
        if assignment.atom_name not in self.atom_assignments:
            self.atom_assignments[assignment.atom_name] = set()
        self.atom_assignments[assignment.atom_name].add(assignment.value)
    
    def _check_closure_optimized(self):
        """Check for closure: an atom cannot be both true and false"""
        if self.is_closed:
            return
        
        for atom_name, values in self.atom_assignments.items():
            # Closure occurs if an atom is assigned both t and f
            if t in values and f in values:
                # Found contradiction
                t_assignment = WK3Assignment(atom_name, t)
                f_assignment = WK3Assignment(atom_name, f)
                
                self.is_closed = True
                self.closure_reason = (t_assignment, f_assignment)
                return
    
    def get_expandable_formulas(self) -> List[Formula]:
        """Get all non-literal formulas that can be expanded"""
        if self.is_closed:
            return []
        
        expandable = []
        for formula in self.formulas:
            if not formula.is_literal():
                # Only expand formulas that haven't been processed yet
                if not self._is_formula_processed(formula):
                    expandable.append(formula)
        
        return self._prioritize_formulas(expandable)
    
    def _is_formula_processed(self, formula: Formula) -> bool:
        """Check if a formula has already been processed (converted to assignments)"""
        return formula in self.processed_formulas
    
    def mark_formula_processed(self, formula: Formula):
        """Mark a formula as processed"""
        self.local_processed_formulas.add(formula)
    
    def _prioritize_formulas(self, formulas: List[Formula]) -> List[Formula]:
        """Prioritize formulas for expansion (same strategy as classical tableaux)"""
        def get_priority(formula: Formula) -> int:
            # Double negations - highest priority (0)
            if isinstance(formula, Negation) and isinstance(formula.operand, Negation):
                return 0
            
            # α-formulas (non-branching) - high priority (1)
            if isinstance(formula, Conjunction):
                return 1
            if isinstance(formula, Negation) and isinstance(formula.operand, Disjunction):
                return 1
                
            # β-formulas (branching) - medium priority (2)  
            if isinstance(formula, Disjunction):
                return 2
            if isinstance(formula, Negation) and isinstance(formula.operand, Conjunction):
                return 2
                
            # Implications - lower priority (3)
            if isinstance(formula, Implication):
                return 3
            if isinstance(formula, Negation) and isinstance(formula.operand, Implication):
                return 3
                
            # Default - lowest priority (4)
            return 4
        
        return sorted(formulas, key=get_priority)
    
    def subsumes(self, other: 'WK3Branch') -> bool:
        """Check if this branch subsumes another branch"""
        if self.is_closed or other.is_closed:
            return False
            
        # This branch subsumes other if all its formulas and assignments are in other
        return (self.formulas.issubset(other.formulas) and 
                self.assignments.issubset(other.assignments))
    
    def _update_signature(self):
        """Update the state signature for cycle detection"""
        if not hasattr(self, '_signatures_enabled') or not self._signatures_enabled:
            return
            
        try:
            current_state = (self.formulas, self.assignments)
            # Create a stable hash of the current state
            formula_strings = sorted([str(f) for f in current_state[0]])
            assignment_strings = sorted([str(a) for a in current_state[1]])
            signature = hash(tuple(formula_strings + assignment_strings))
            self._state_signatures.append(signature)
        except RecursionError:
            pass
    
    def has_cycle(self) -> bool:
        """Detect if this branch has encountered a cycle"""
        if len(self._state_signatures) < 2:
            return False
        
        current_signature = self._state_signatures[-1]
        return current_signature in self._state_signatures[:-1]
    
    def extract_model(self) -> Optional[WK3Model]:
        """Extract a weak Kleene model from this branch if it's open and fully expanded"""
        if self.is_closed or len(self.get_expandable_formulas()) > 0:
            return None
        
        # Extract assignments from this branch
        assignment_dict = {}
        
        # Add explicit assignments
        for assignment in self.assignments:
            # Use the most recent assignment if there are duplicates
            assignment_dict[assignment.atom_name] = assignment.value
        
        # For any atoms mentioned in formulas but not assigned, assign 'e'
        all_atoms = set()
        for formula in self.formulas:
            all_atoms.update(self._extract_atoms(formula))
        
        for atom_name in all_atoms:
            if atom_name not in assignment_dict:
                assignment_dict[atom_name] = e
        
        return WK3Model(assignment_dict)
    
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


class WK3Tableau:
    """Weak Kleene logic tableau system"""
    
    def __init__(self, initial_formulas: Union[Formula, List[Formula]]):
        # Handle both single formula and list of formulas
        if isinstance(initial_formulas, Formula):
            self.initial_formulas = [initial_formulas]
        else:
            self.initial_formulas = initial_formulas
        
        self.node_counter = 0
        self.branch_counter = 0
        self.root_nodes: List[TableauNode] = []
        self.branches: List[WK3Branch] = []
        self.all_nodes: List[TableauNode] = []
    
    def build(self) -> bool:
        """Build the WK3 tableau. Returns True if satisfiable, False if unsatisfiable."""
        # Create root nodes and initial branch with all formulas
        for formula in self.initial_formulas:
            root_node = self._create_node(formula, RuleType.INITIAL)
            self.root_nodes.append(root_node)
        
        initial_branch = WK3Branch(self._next_branch_id())
        for formula in self.initial_formulas:
            initial_branch.add_formula(formula)
        self.branches.append(initial_branch)
        
        # Expand until no more expansion is possible
        while True:
            expansion_occurred = False
            
            # Early satisfiability detection
            if self._has_satisfying_branch():
                break
            
            # Process each branch
            branches_to_process = self.branches.copy()
            
            for branch in branches_to_process:
                if branch.is_closed:
                    continue
                
                expandable = branch.get_expandable_formulas()
                if expandable:
                    # Expand the first expandable formula
                    formula = expandable[0]
                    new_branches = self._expand_formula_in_branch(formula, branch)
                    if new_branches:
                        expansion_occurred = True
                        # Remove the original branch and add new ones
                        if branch in self.branches:
                            self.branches.remove(branch)
                        self.branches.extend(new_branches)
                        
                        # Apply subsumption elimination
                        self._eliminate_subsumed_branches()
                        break
            
            if not expansion_occurred:
                self._eliminate_subsumed_branches()
                break
        
        # Check if satisfiable
        open_branches = [b for b in self.branches if not b.is_closed]
        return len(open_branches) > 0
    
    def build_with_models(self) -> Tuple[bool, List[WK3Model]]:
        """Build the tableau and extract all satisfying models"""
        is_satisfiable = self.build()
        models = self.extract_all_models()
        return is_satisfiable, models
    
    def extract_all_models(self) -> List[WK3Model]:
        """Extract all satisfying models from open branches"""
        models = []
        for branch in self.branches:
            if not branch.is_closed:
                model = branch.extract_model()
                if model is not None:
                    models.append(model)
        return models
    
    def get_sample_model(self) -> Optional[WK3Model]:
        """Get one satisfying model, or None if unsatisfiable"""
        models = self.extract_all_models()
        return models[0] if models else None
    
    def _has_satisfying_branch(self) -> bool:
        """Check if we have a fully expanded open branch"""
        for branch in self.branches:
            if not branch.is_closed and len(branch.get_expandable_formulas()) == 0:
                return True
        return False
    
    def _eliminate_subsumed_branches(self):
        """Remove branches that are subsumed by other branches"""
        branches_to_remove = []
        
        for i, branch_a in enumerate(self.branches):
            if branch_a in branches_to_remove:
                continue
                
            for j, branch_b in enumerate(self.branches):
                if i != j and branch_b not in branches_to_remove:
                    if branch_a.subsumes(branch_b):
                        branches_to_remove.append(branch_b)
        
        for branch in branches_to_remove:
            if branch in self.branches:
                self.branches.remove(branch)
    
    def _create_node(self, formula: Formula, rule: RuleType, parent: Optional[TableauNode] = None) -> TableauNode:
        """Create a new tableau node"""
        node = TableauNode(
            id=self._next_node_id(),
            formula=formula,
            rule_applied=rule,
            parent=parent
        )
        if parent:
            parent.children.append(node)
        self.all_nodes.append(node)
        return node
    
    def _next_node_id(self) -> int:
        self.node_counter += 1
        return self.node_counter
    
    def _next_branch_id(self) -> int:
        self.branch_counter += 1
        return self.branch_counter
    
    def _expand_formula_in_branch(self, formula: Formula, branch: WK3Branch) -> List[WK3Branch]:
        """Expand a formula in a specific branch according to WK3 tableau rules"""
        
        # Find or create parent node
        parent_node = None
        for node in self.all_nodes:
            if node.formula == formula:
                parent_node = node
                break
        
        # Mark formula as processed first to prevent infinite loops
        branch.mark_formula_processed(formula)
        
        # Apply WK3 tableau rules
        if isinstance(formula, Atom):
            # Atoms are literals - they should not be expanded!
            # Just keep the branch as is
            return [branch]
        
        elif isinstance(formula, Negation):
            if isinstance(formula.operand, Negation):
                # Double negation: ¬¬A → A (simplified for WK3)
                inner = formula.operand.operand
                node = self._create_node(inner, RuleType.DOUBLE_NEGATION, parent_node)
                branch.add_formula(inner)
                return [branch]
            
            elif isinstance(formula.operand, Atom):
                # Negated atom - still a literal, no expansion needed
                return [branch]
            
            elif isinstance(formula.operand, Conjunction):
                # ¬(A ∧ B) → ¬A ∨ ¬B (De Morgan)
                left_neg = Negation(formula.operand.left)
                right_neg = Negation(formula.operand.right)
                disjunction = Disjunction(left_neg, right_neg)
                branch.add_formula(disjunction)
                return [branch]
            
            elif isinstance(formula.operand, Disjunction):
                # ¬(A ∨ B) → ¬A ∧ ¬B (De Morgan)
                left_neg = Negation(formula.operand.left)
                right_neg = Negation(formula.operand.right)
                branch.add_formula(left_neg)
                branch.add_formula(right_neg)
                return [branch]
        
        elif isinstance(formula, Conjunction):
            # A ∧ B: add both A and B to the branch (α-rule)
            node_left = self._create_node(formula.left, RuleType.CONJUNCTION, parent_node)
            node_right = self._create_node(formula.right, RuleType.CONJUNCTION, parent_node)
            branch.add_formula(formula.left)
            branch.add_formula(formula.right)
            return [branch]
        
        elif isinstance(formula, Disjunction):
            # A ∨ B: create two branches, one with A, one with B (β-rule)
            # Branch 1: A
            branch1 = branch.copy_with_new_id(self._next_branch_id())
            branch1.add_formula(formula.left)
            node_left = self._create_node(formula.left, RuleType.DISJUNCTION, parent_node)
            
            # Branch 2: B  
            branch2 = branch.copy_with_new_id(self._next_branch_id())
            branch2.add_formula(formula.right)
            node_right = self._create_node(formula.right, RuleType.DISJUNCTION, parent_node)
            
            return [branch1, branch2]
        
        elif isinstance(formula, Implication):
            # A → B ≡ ¬A ∨ B: create two branches
            # Branch 1: ¬A
            neg_antecedent = Negation(formula.antecedent)
            branch1 = branch.copy_with_new_id(self._next_branch_id())
            branch1.add_formula(neg_antecedent)
            node_left = self._create_node(neg_antecedent, RuleType.IMPLICATION, parent_node)
            
            # Branch 2: B
            branch2 = branch.copy_with_new_id(self._next_branch_id())
            branch2.add_formula(formula.consequent)
            node_right = self._create_node(formula.consequent, RuleType.IMPLICATION, parent_node)
            
            return [branch1, branch2]
        
        # If no rule applies, just return the original branch
        return [branch]
    
    def print_tree(self):
        """Print the WK3 tableau tree"""
        print("=" * 70)
        print("WEAK KLEENE SEMANTIC TABLEAU TREE")
        print("=" * 70)
        if len(self.initial_formulas) == 1:
            print(f"Testing satisfiability of: {self.initial_formulas[0]}")
        else:
            print(f"Testing satisfiability of {len(self.initial_formulas)} formulas:")
            for i, formula in enumerate(self.initial_formulas, 1):
                print(f"  {i}. {formula}")
        print()
        
        print("\n" + "=" * 70)
        open_branches = [b for b in self.branches if not b.is_closed]
        closed_branches = [b for b in self.branches if b.is_closed]
        
        print(f"Total branches: {len(self.branches)}")
        print(f"Open branches: {len(open_branches)} {[b.id for b in open_branches] if open_branches else ''}")
        print(f"Closed branches: {len(closed_branches)} {[b.id for b in closed_branches] if closed_branches else ''}")
        
        if open_branches:
            print("✓ SATISFIABLE - Formula has weak Kleene satisfying interpretation(s)")
            # Show sample models
            models = self.extract_all_models()
            if models:
                print(f"Sample models ({len(models)} total):")
                for i, model in enumerate(models[:3], 1):  # Show first 3 models
                    print(f"  Model {i}: {model}")
                if len(models) > 3:
                    print(f"  ... and {len(models) - 3} more")
        else:
            print("✗ UNSATISFIABLE - All branches close")
        print("=" * 70)


# Export commonly used items
__all__ = [
    'WK3Assignment', 'WK3Branch', 'WK3Tableau'
]