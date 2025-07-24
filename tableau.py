#!/usr/bin/env python3
"""
Semantic Tableau Implementation for Classical Propositional Logic

Implements a complete tableau procedure with proper branching and closure detection.
"""

from abc import ABC, abstractmethod
from typing import List, Set, Optional, Tuple, Dict, Union
from dataclasses import dataclass as dc
from dataclasses import dataclass
from enum import Enum
import copy

from formula import (
    Formula, Atom, Predicate, Negation, Conjunction, Disjunction, Implication,
    RuleType
)

@dc
class Model:
    """
    A truth assignment that satisfies a formula or formula set.
    Maps atomic propositions to boolean values.
    """
    assignment: Dict[str, bool]
    
    def satisfies(self, formula: Formula) -> bool:
        """Check if this model satisfies the given formula"""
        return self._evaluate(formula)
    
    def _evaluate(self, formula: Formula) -> bool:
        """Recursively evaluate a formula under this model"""
        if isinstance(formula, Atom):
            return self.assignment.get(formula.name, False)
        elif isinstance(formula, Negation):
            return not self._evaluate(formula.operand)
        elif isinstance(formula, Conjunction):
            return self._evaluate(formula.left) and self._evaluate(formula.right)
        elif isinstance(formula, Disjunction):
            return self._evaluate(formula.left) or self._evaluate(formula.right)
        elif isinstance(formula, Implication):
            return (not self._evaluate(formula.antecedent)) or self._evaluate(formula.consequent)
        else:
            raise ValueError(f"Unknown formula type: {type(formula)}")
    
    def __str__(self) -> str:
        """String representation of the model"""
        if not self.assignment:
            return "{}"
        
        true_atoms = [atom for atom, value in self.assignment.items() if value]
        false_atoms = [atom for atom, value in self.assignment.items() if not value]
        
        parts = []
        if true_atoms:
            parts.append(f"True: {{{', '.join(sorted(true_atoms))}}}")
        if false_atoms:
            parts.append(f"False: {{{', '.join(sorted(false_atoms))}}}")
        
        return " | ".join(parts) if parts else "{}"

@dataclass
class TableauNode:
    id: int
    formula: Formula
    rule_applied: Optional[RuleType] = None
    parent: Optional['TableauNode'] = None
    children: List['TableauNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

class Branch:
    def __init__(self, branch_id: int, formulas: Set[Formula] = None, parent: Optional['Branch'] = None):
        self.id = branch_id
        self.parent = parent
        
        # Incremental representation: store only local formulas
        self.local_formulas: Set[Formula] = formulas if formulas is not None else set()
        
        self.is_closed = False
        self.closure_reason: Optional[Tuple[Formula, Formula]] = None
        
        # Optimized literal indexing for fast closure detection
        self.positive_literals: Set[str] = set()  # Atom names (backward compatibility)
        self.negative_literals: Set[str] = set()  # Atom names from ¬Atom (backward compatibility)
        
        # Extended predicate indexing for n-ary predicates
        self.positive_predicates: Set[Formula] = set()  # Positive atomic formulas
        self.negative_predicates: Set[Formula] = set()  # Negated atomic formulas
        
        # Cycle detection: track formula set signatures for loop detection
        self._formula_signatures: List[int] = []  # Hash signatures of formula sets
        self._signatures_enabled = False  # Disable during initialization
        
        self._rebuild_literal_index()
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
    
    def add_formula(self, formula: Formula):
        self.local_formulas.add(formula)
        self._update_literal_index(formula)
        self._check_closure_optimized()
        self._update_signature()
    
    def copy_with_new_id(self, new_id: int) -> 'Branch':
        """Create a copy of this branch with a new ID using incremental representation"""
        # Create new branch with this branch as parent (incremental representation)
        new_branch = Branch(new_id, parent=self)
        # The constructor will rebuild the literal index automatically
        return new_branch
    
    def create_child_with_formula(self, new_id: int, formula: Formula) -> 'Branch':
        """Create a child branch with an additional formula"""
        child_branch = Branch(new_id, formulas={formula}, parent=self)
        return child_branch
    
    def _rebuild_literal_index(self):
        """Rebuild the literal index from all formulas in the branch"""
        self.positive_literals.clear()
        self.negative_literals.clear()
        self.positive_predicates.clear()
        self.negative_predicates.clear()
        
        for formula in self.formulas:
            self._update_literal_index(formula)
    
    def _update_literal_index(self, formula: Formula):
        """Update literal index with a new formula"""
        normalized = self._normalize_formula(formula)
        
        # Handle atomic formulas (both Atoms and Predicates)
        if isinstance(normalized, (Atom, Predicate)) and normalized.is_atomic():
            # Backward compatibility: still track atom names for old atoms
            if isinstance(normalized, Atom):
                self.positive_literals.add(normalized.name)
            # Track all atomic formulas in new system
            self.positive_predicates.add(normalized)
            
        elif isinstance(normalized, Negation) and isinstance(normalized.operand, (Atom, Predicate)):
            if normalized.operand.is_atomic():
                # Backward compatibility: still track atom names for old atoms
                if isinstance(normalized.operand, Atom):
                    self.negative_literals.add(normalized.operand.name)
                # Track all negated atomic formulas in new system
                self.negative_predicates.add(normalized.operand)
    
    def _check_closure_optimized(self):
        """Optimized closure detection using literal indexing - O(1) lookup"""
        if self.is_closed:
            return
        
        # Check for contradiction: if any atomic formula appears in both positive and negative
        contradicting_predicates = self.positive_predicates.intersection(self.negative_predicates)
        
        if contradicting_predicates:
            # Found contradiction - set closure reason with first contradicting predicate
            positive_predicate = next(iter(contradicting_predicates))
            negative_predicate = Negation(positive_predicate)
            
            self.is_closed = True
            self.closure_reason = (positive_predicate, negative_predicate)
            return
        
        # Backward compatibility: also check old atom-based indexing
        contradicting_atoms = self.positive_literals.intersection(self.negative_literals)
        
        if contradicting_atoms:
            # Found contradiction - set closure reason with first contradicting atom
            atom_name = next(iter(contradicting_atoms))
            positive_atom = Atom(atom_name)
            negative_atom = Negation(positive_atom)
            
            self.is_closed = True
            self.closure_reason = (positive_atom, negative_atom)
    
    def _normalize_formula(self, formula: Formula) -> Formula:
        """Remove double negations"""
        if isinstance(formula, Negation) and isinstance(formula.operand, Negation):
            return self._normalize_formula(formula.operand.operand)
        return formula
    
    def get_expandable_formulas(self) -> List[Formula]:
        """Get all non-literal formulas that can be expanded, prioritized by expansion strategy"""
        if self.is_closed:
            return []
        
        expandable = []
        for formula in self.formulas:
            if not formula.is_literal():
                expandable.append(formula)
        
        # Prioritize formulas for optimal expansion order
        return self._prioritize_formulas(expandable)
    
    def _prioritize_formulas(self, formulas: List[Formula]) -> List[Formula]:
        """
        Prioritize formulas for expansion to minimize branching and maximize early closure.
        Priority order:
        1. Double negations (¬¬A) - always simplify first
        2. Conjunctions and negated disjunctions (α-formulas) - don't branch
        3. Disjunctions and negated conjunctions (β-formulas) - cause branching
        4. Implications and negated implications - last (complex expansion)
        """
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
        
        # Sort by priority (lower number = higher priority)
        return sorted(formulas, key=get_priority)
    
    def subsumes(self, other: 'Branch') -> bool:
        """
        Check if this branch subsumes another branch.
        Branch A subsumes Branch B if A's formulas are a subset of B's formulas.
        In this case, B is redundant because any closure/satisfiability result
        for A also applies to B.
        """
        if self.is_closed or other.is_closed:
            return False  # Don't subsume closed branches
            
        # This branch subsumes other if all its formulas are in other
        return self.formulas.issubset(other.formulas)
    
    def _update_signature(self):
        """Update the formula set signature for cycle detection"""
        if not hasattr(self, '_signatures_enabled') or not self._signatures_enabled:
            return
            
        try:
            current_formulas = self.formulas
            # Create a stable hash of the current formula set
            formula_strings = sorted([str(f) for f in current_formulas])
            signature = hash(tuple(formula_strings))
            self._formula_signatures.append(signature)
        except RecursionError:
            # Avoid infinite recursion during initialization
            pass
    
    def has_cycle(self) -> bool:
        """
        Detect if this branch has encountered a cycle (repeated formula set).
        This is crucial for modal/temporal logics where infinite loops can occur.
        For CPL, this provides defensive detection of potential implementation bugs.
        """
        if len(self._formula_signatures) < 2:
            return False
        
        current_signature = self._formula_signatures[-1]
        # Check if current signature appeared before (indicating cycle)
        return current_signature in self._formula_signatures[:-1]
    
    def get_cycle_depth(self) -> int:
        """Get the depth at which the cycle was detected, or -1 if no cycle"""
        if not self.has_cycle():
            return -1
        
        current_signature = self._formula_signatures[-1]
        # Find first occurrence of this signature
        for i, sig in enumerate(self._formula_signatures[:-1]):
            if sig == current_signature:
                return len(self._formula_signatures) - 1 - i
        return -1
    
    def extract_model(self) -> Optional[Model]:
        """
        Extract a satisfying model from this branch if it's open and fully expanded.
        Returns None if the branch is closed or not fully expanded.
        """
        if self.is_closed or len(self.get_expandable_formulas()) > 0:
            return None
        
        # Extract truth assignments from literals in this branch
        assignment = {}
        
        # Start with explicit assignments from positive and negative literals
        for atom_name in self.positive_literals:
            assignment[atom_name] = True
        
        for atom_name in self.negative_literals:
            assignment[atom_name] = False
        
        # For any atoms not explicitly assigned, we can choose any value
        # Since this is a satisfying branch, any assignment to unmentioned atoms works
        all_atoms = set()
        for formula in self.formulas:
            all_atoms.update(self._extract_atoms(formula))
        
        # Set unassigned atoms to False (arbitrary choice - True would also work)
        for atom_name in all_atoms:
            if atom_name not in assignment:
                assignment[atom_name] = False
        
        return Model(assignment)
    
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

class Tableau:
    def __init__(self, initial_formulas: Union[Formula, List[Formula]]):
        # Handle both single formula and list of formulas
        if isinstance(initial_formulas, Formula):
            self.initial_formulas = [initial_formulas]
        else:
            self.initial_formulas = initial_formulas
        
        self.node_counter = 0
        self.branch_counter = 0
        self.root_nodes: List[TableauNode] = []
        self.branches: List[Branch] = []
        self.all_nodes: List[TableauNode] = []
        
    def build(self) -> bool:
        """Build the tableau. Returns True if satisfiable, False if unsatisfiable."""
        # Create root nodes and initial branch with all formulas
        for formula in self.initial_formulas:
            root_node = self._create_node(formula, RuleType.INITIAL)
            self.root_nodes.append(root_node)
        
        initial_branch = Branch(self._next_branch_id())
        for formula in self.initial_formulas:
            initial_branch.add_formula(formula)
        self.branches.append(initial_branch)
        
        # Expand until no more expansion is possible (proper termination)
        while True:
            expansion_occurred = False
            
            # Early satisfiability detection: check if we have a fully expanded open branch
            if self._has_satisfying_branch():
                break
            
            # Process each branch exactly once per iteration
            branches_to_process = self.branches.copy()
            
            for branch in branches_to_process:
                if branch.is_closed:
                    continue
                
                # Cycle detection: disabled for CPL (uncomment for modal/temporal logic extensions)
                # if branch.has_cycle():
                #     branch.is_closed = True
                #     branch.closure_reason = ("CYCLE_DETECTED", f"Cycle at depth {branch.get_cycle_depth()}")
                #     continue
                
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
                        
                        # Apply subsumption elimination after adding new branches
                        self._eliminate_subsumed_branches()
                        break  # Restart to maintain consistency
            
            # Apply subsumption elimination at end of iteration if no expansion occurred
            if not expansion_occurred:
                self._eliminate_subsumed_branches()
                break
        
        # Check if satisfiable
        open_branches = [b for b in self.branches if not b.is_closed]
        return len(open_branches) > 0
    
    def build_with_models(self) -> Tuple[bool, List[Model]]:
        """
        Build the tableau and extract all satisfying models.
        Returns (is_satisfiable, list_of_models).
        """
        is_satisfiable = self.build()
        models = self.extract_all_models()
        return is_satisfiable, models
    
    def extract_all_models(self) -> List[Model]:
        """Extract all satisfying models from open branches"""
        models = []
        for branch in self.branches:
            if not branch.is_closed:
                model = branch.extract_model()
                if model is not None:
                    models.append(model)
        return models
    
    def get_sample_model(self) -> Optional[Model]:
        """Get one satisfying model, or None if unsatisfiable"""
        models = self.extract_all_models()
        return models[0] if models else None
    
    def _has_satisfying_branch(self) -> bool:
        """
        Check if we have a branch that is fully expanded and open.
        A fully expanded branch contains only literals (atoms and negated atoms).
        If such a branch exists, the formula set is satisfiable.
        """
        for branch in self.branches:
            if not branch.is_closed and len(branch.get_expandable_formulas()) == 0:
                # Found an open branch with no expandable formulas = satisfying branch
                return True
        return False
    
    def _eliminate_subsumed_branches(self):
        """
        Remove branches that are subsumed by other branches.
        A branch B is subsumed by branch A if A's formulas ⊆ B's formulas.
        """
        branches_to_remove = []
        
        for i, branch_a in enumerate(self.branches):
            if branch_a in branches_to_remove:
                continue
                
            for j, branch_b in enumerate(self.branches):
                if i != j and branch_b not in branches_to_remove:
                    if branch_a.subsumes(branch_b):
                        # branch_a subsumes branch_b, so remove branch_b
                        branches_to_remove.append(branch_b)
        
        # Remove subsumed branches
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
    
    def _expand_formula_in_branch(self, formula: Formula, branch: Branch) -> List[Branch]:
        """Expand a formula in a specific branch"""
        
        # Find or create parent node
        parent_node = None
        for node in self.all_nodes:
            if node.formula == formula:
                parent_node = node
                break
        
        # Remove the formula being expanded from local formulas
        branch.local_formulas.discard(formula)
        
        # Apply tableau rules
        if isinstance(formula, Negation) and isinstance(formula.operand, Negation):
            # Double negation: ¬¬A → A
            inner = formula.operand.operand
            node = self._create_node(inner, RuleType.DOUBLE_NEGATION, parent_node)
            branch.add_formula(inner)
            return [branch]
        
        elif isinstance(formula, Conjunction):
            # Conjunction: A ∧ B → A, B (same branch)
            left_node = self._create_node(formula.left, RuleType.CONJUNCTION, parent_node)
            right_node = self._create_node(formula.right, RuleType.CONJUNCTION, parent_node)
            branch.add_formula(formula.left)
            branch.add_formula(formula.right)
            return [branch]
        
        elif isinstance(formula, Negation) and isinstance(formula.operand, Conjunction):
            # Negated conjunction: ¬(A ∧ B) → ¬A | ¬B (branching)
            conj = formula.operand
            left_neg = Negation(conj.left)
            right_neg = Negation(conj.right)
            
            # Create two child branches with current formulas (excluding the expanded formula)
            remaining_formulas = set(branch.formulas) - {formula}
            branch1 = Branch(self._next_branch_id(), formulas=set(remaining_formulas))
            branch1.add_formula(left_neg)
            branch2 = Branch(self._next_branch_id(), formulas=set(remaining_formulas))
            branch2.add_formula(right_neg)
            
            left_node = self._create_node(left_neg, RuleType.NEG_CONJUNCTION, parent_node)
            right_node = self._create_node(right_neg, RuleType.NEG_CONJUNCTION, parent_node)
            
            return [branch1, branch2]
        
        elif isinstance(formula, Disjunction):
            # Disjunction: A ∨ B → A | B (branching)
            remaining_formulas = set(branch.formulas) - {formula}
            branch1 = Branch(self._next_branch_id(), formulas=set(remaining_formulas))
            branch1.add_formula(formula.left)
            branch2 = Branch(self._next_branch_id(), formulas=set(remaining_formulas))
            branch2.add_formula(formula.right)
            
            left_node = self._create_node(formula.left, RuleType.DISJUNCTION, parent_node)
            right_node = self._create_node(formula.right, RuleType.DISJUNCTION, parent_node)
            
            return [branch1, branch2]
        
        elif isinstance(formula, Negation) and isinstance(formula.operand, Disjunction):
            # Negated disjunction: ¬(A ∨ B) → ¬A ∧ ¬B (same branch)
            disj = formula.operand
            left_neg = Negation(disj.left)
            right_neg = Negation(disj.right)
            
            left_node = self._create_node(left_neg, RuleType.NEG_DISJUNCTION, parent_node)
            right_node = self._create_node(right_neg, RuleType.NEG_DISJUNCTION, parent_node)
            
            branch.add_formula(left_neg)
            branch.add_formula(right_neg)
            return [branch]
        
        elif isinstance(formula, Implication):
            # Implication: A → B ≡ ¬A ∨ B (branching)
            neg_ant = Negation(formula.antecedent)
            
            remaining_formulas = set(branch.formulas) - {formula}
            branch1 = Branch(self._next_branch_id(), formulas=set(remaining_formulas))
            branch1.add_formula(neg_ant)
            branch2 = Branch(self._next_branch_id(), formulas=set(remaining_formulas))
            branch2.add_formula(formula.consequent)
            
            left_node = self._create_node(neg_ant, RuleType.IMPLICATION, parent_node)
            right_node = self._create_node(formula.consequent, RuleType.IMPLICATION, parent_node)
            
            return [branch1, branch2]
        
        elif isinstance(formula, Negation) and isinstance(formula.operand, Implication):
            # Negated implication: ¬(A → B) → A ∧ ¬B (same branch)
            impl = formula.operand
            neg_cons = Negation(impl.consequent)
            
            ant_node = self._create_node(impl.antecedent, RuleType.NEG_IMPLICATION, parent_node)
            neg_cons_node = self._create_node(neg_cons, RuleType.NEG_IMPLICATION, parent_node)
            
            branch.add_formula(impl.antecedent)
            branch.add_formula(neg_cons)
            return [branch]
        
        # If no rule applies, return the branch unchanged
        branch.local_formulas.add(formula)  # Add it back to local formulas
        return [branch]
    
    def print_tree(self):
        """Print the tableau tree"""
        print("=" * 70)
        print("SEMANTIC TABLEAU TREE")
        print("=" * 70)
        if len(self.initial_formulas) == 1:
            print(f"Testing satisfiability of: {self.initial_formulas[0]}")
        else:
            print(f"Testing satisfiability of {len(self.initial_formulas)} formulas:")
            for i, formula in enumerate(self.initial_formulas, 1):
                print(f"  {i}. {formula}")
        print()
        
        # Print each root node (if multiple initial formulas)
        if len(self.root_nodes) == 1:
            self._print_node_tree(self.root_nodes[0])
        else:
            # For multiple formulas, show them as separate initial nodes
            print("Initial formulas:")
            for i, root_node in enumerate(self.root_nodes):
                is_last_root = (i == len(self.root_nodes) - 1)
                connector = "└── " if is_last_root else "├── "
                print(f"{connector}{root_node.id}: {root_node.formula}")
            print()
            
            # Then show the expansion tree starting from first expandable nodes
            if self.all_nodes:
                # Find first non-initial node to start tree display
                expansion_nodes = [n for n in self.all_nodes if n.rule_applied != RuleType.INITIAL]
                if expansion_nodes:
                    # Group by parent relationships and print tree
                    printed_nodes = set()
                    for node in expansion_nodes:
                        if node.id not in printed_nodes:
                            self._print_node_tree(node, visited=printed_nodes)
        
        print("\n" + "=" * 70)
        open_branches = [b for b in self.branches if not b.is_closed]
        closed_branches = [b for b in self.branches if b.is_closed]
        
        print(f"Total branches: {len(self.branches)}")
        print(f"Open branches: {len(open_branches)} {[b.id for b in open_branches] if open_branches else ''}")
        print(f"Closed branches: {len(closed_branches)} {[b.id for b in closed_branches] if closed_branches else ''}")
        
        if open_branches:
            if len(self.initial_formulas) == 1:
                print("✓ SATISFIABLE - Formula has satisfying interpretation(s)")
            else:
                print("✓ SATISFIABLE - Formula set has satisfying interpretation(s)")
        else:
            if len(self.initial_formulas) == 1:
                print("✗ UNSATISFIABLE - All branches close")
            else:
                print("✗ UNSATISFIABLE - Formula set is inconsistent (all branches close)")
        print("=" * 70)
    
    def _print_node_tree(self, node: TableauNode, prefix: str = "", is_last: bool = True, visited: set = None):
        """Print the tree structure"""
        if visited is None:
            visited = set()
        
        if node.id in visited:
            return
        visited.add(node.id)
        
        # Rule description
        rule_desc = ""
        if node.rule_applied and node.rule_applied != RuleType.INITIAL:
            rule_map = {
                RuleType.DOUBLE_NEGATION: "by Double Negation (¬¬A → A)",
                RuleType.CONJUNCTION: "by Conjunction (A∧B → A, B)",
                RuleType.NEG_CONJUNCTION: "by Neg. Conjunction (¬(A∧B) → ¬A | ¬B)",
                RuleType.DISJUNCTION: "by Disjunction (A∨B → A | B)",
                RuleType.NEG_DISJUNCTION: "by Neg. Disjunction (¬(A∨B) → ¬A, ¬B)",
                RuleType.IMPLICATION: "by Implication (A→B → ¬A | B)",
                RuleType.NEG_IMPLICATION: "by Neg. Implication (¬(A→B) → A, ¬B)"
            }
            rule_desc = f" [{rule_map.get(node.rule_applied, str(node.rule_applied))}]"
        
        # Branch info
        branch_info = self._get_branch_info(node.formula)
        
        # Print node
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{node.id}: {node.formula}{branch_info}{rule_desc}")
        
        # Print children
        child_prefix = prefix + ("    " if is_last else "│   ")
        children = sorted(node.children, key=lambda x: x.id)
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            self._print_node_tree(child, child_prefix, is_last_child, visited)
    
    def _get_branch_info(self, formula: Formula) -> str:
        """Get branch information for a formula"""
        containing_branches = []
        for branch in self.branches:
            if formula in branch.formulas:
                status = "✗" if branch.is_closed else "✓"
                containing_branches.append(f"{branch.id}{status}")
        
        if containing_branches:
            return f" [Branch {', '.join(containing_branches)}]"
        return ""

# Test function
def demo_tableau():
    """Test the tableau with transitivity formulas"""
    from formula import Atom, Implication, Conjunction, Negation
    
    a = Atom("a")
    b = Atom("b") 
    c = Atom("c")
    
    impl_ab = Implication(a, b)
    impl_bc = Implication(b, c)
    premise = Conjunction(impl_ab, impl_bc)
    impl_ac = Implication(a, c)
    
    # Test 1: Transitivity (should be satisfiable/tautology)
    formula1 = Implication(premise, impl_ac)
    print("Testing Formula 1: ((a → b) ∧ (b → c)) → (a → c)")
    tableau1 = Tableau(formula1)
    result1 = tableau1.build()
    tableau1.print_tree()
    
    print("\n" + "="*100 + "\n")
    
    # Test 2: Negation of transitivity (should be unsatisfiable)
    formula2 = Implication(premise, Negation(impl_ac))
    print("Testing Formula 2: ((a → b) ∧ (b → c)) → ¬(a → c)")
    tableau2 = Tableau(formula2)
    result2 = tableau2.build()
    tableau2.print_tree()
    
    print("\n" + "="*100)
    print("LOGICAL CONSISTENCY CHECK:")
    print(f"Formula 1 result: {'SATISFIABLE' if result1 else 'UNSATISFIABLE'}")
    print(f"Formula 2 result: {'SATISFIABLE' if result2 else 'UNSATISFIABLE'}")
    
    if result1 and result2:
        print("❌ ERROR: Both cannot be satisfiable!")
    elif result1 and not result2:
        print("✅ CORRECT: Formula 1 is satisfiable, Formula 2 is unsatisfiable")
    else:
        print("⚠️  UNEXPECTED RESULTS")

if __name__ == "__main__":
    test_tableau()