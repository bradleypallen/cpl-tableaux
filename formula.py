#!/usr/bin/env python3
"""
Semantic Tableau for Classical Propositional Logic

A proper implementation of the tableau method using systematic expansion
and complete decomposition of all formulas.
"""

from abc import ABC, abstractmethod
from typing import List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import term hierarchy for predicate support
try:
    from .term import Term, Constant, Variable
except ImportError:
    try:
        from term import Term, Constant, Variable
    except ImportError:
        # Fallback for systems without term.py
        Term = None
        Constant = None
        Variable = None

# Formula representation
class Formula(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @abstractmethod
    def is_atomic(self) -> bool:
        pass
    
    @abstractmethod
    def is_literal(self) -> bool:
        pass
    
    def is_ground(self) -> bool:
        """Check if this formula contains only ground terms (no variables)"""
        return True  # Default implementation for propositional formulas
    
    def get_variables(self) -> Set[str]:
        """Get all variable names in this formula"""
        return set()  # Default implementation for propositional formulas

class Predicate(Formula):
    """
    Represents an n-ary predicate R(t1, t2, ..., tn) where n >= 0.
    For n=0, this represents a propositional atom.
    
    Examples:
    - Predicate("P", []) represents propositional atom P
    - Predicate("Student", [Constant("john")]) represents Student(john)
    - Predicate("Loves", [Constant("john"), Constant("mary")]) represents Loves(john, mary)
    """
    
    def __init__(self, predicate_name: str, args: List['Term'] = None):
        if not predicate_name or not isinstance(predicate_name, str):
            raise ValueError("Predicate name must be a non-empty string")
        
        # Relaxed naming convention - allow both cases for backward compatibility
        self.predicate_name = predicate_name
        self.args = args if args is not None else []
        
        # Validate argument types if Term classes are available
        if Term is not None:
            for arg in self.args:
                if not isinstance(arg, Term):
                    raise ValueError(f"All arguments must be Term instances: {arg}")
    
    @property
    def arity(self) -> int:
        """Return the number of arguments (arity) of this predicate"""
        return len(self.args)
    
    def __str__(self) -> str:
        if self.arity == 0:
            return self.predicate_name  # P (propositional)
        args_str = ', '.join(str(arg) for arg in self.args)
        return f"{self.predicate_name}({args_str})"  # R(c1, c2, ..., cn)
    
    def is_atomic(self) -> bool:
        return True
    
    def is_literal(self) -> bool:
        return True
    
    def is_ground(self) -> bool:
        """Check if all arguments are ground (contain no variables)"""
        return all(arg.is_ground() for arg in self.args)
    
    def get_variables(self) -> Set[str]:
        """Get all variable names in the arguments"""
        variables = set()
        for arg in self.args:
            variables.update(arg.get_variables())
        return variables
    
    def __eq__(self, other):
        return (isinstance(other, Predicate) and 
                self.predicate_name == other.predicate_name and 
                self.args == other.args)
    
    def __hash__(self):
        return hash(('predicate', self.predicate_name, tuple(self.args)))


class Atom(Predicate):
    """
    Backward compatibility class for propositional atoms.
    An Atom is just a 0-ary Predicate.
    """
    
    def __init__(self, name: str):
        # Store original name for backward compatibility
        self._original_name = name
        super().__init__(name, [])
    
    @property
    def name(self) -> str:
        """Return the original name for backward compatibility"""
        return self._original_name
    
    def __str__(self) -> str:
        return self._original_name
    
    def __eq__(self, other):
        if isinstance(other, Atom):
            return self.name == other.name
        elif isinstance(other, Predicate):
            return (other.arity == 0 and 
                    other.predicate_name == self.name)
        return False
    
    def __hash__(self):
        return hash(self.name)  # Use original name for compatibility

class Negation(Formula):
    def __init__(self, operand: Formula):
        self.operand = operand
    
    def __str__(self) -> str:
        if isinstance(self.operand, (Atom, Predicate)) and self.operand.is_atomic():
            return f"¬{self.operand}"
        return f"¬({self.operand})"
    
    def is_atomic(self) -> bool:
        return isinstance(self.operand, (Atom, Predicate)) and self.operand.is_atomic()
    
    def is_literal(self) -> bool:
        return isinstance(self.operand, (Atom, Predicate)) and self.operand.is_atomic()
    
    def is_ground(self) -> bool:
        """Check if this formula contains only ground terms (no variables)"""
        return self.operand.is_ground()
    
    def get_variables(self) -> Set[str]:
        """Get all variable names in this formula"""
        return self.operand.get_variables()
    
    def __eq__(self, other):
        return isinstance(other, Negation) and self.operand == other.operand
    
    def __hash__(self):
        return hash(('neg', self.operand))

class Conjunction(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
    
    def __str__(self) -> str:
        return f"({self.left} ∧ {self.right})"
    
    def is_atomic(self) -> bool:
        return False
    
    def is_literal(self) -> bool:
        return False
    
    def __eq__(self, other):
        return isinstance(other, Conjunction) and self.left == other.left and self.right == other.right
    
    def __hash__(self):
        return hash(('and', self.left, self.right))
    
    def is_ground(self) -> bool:
        """Check if this formula contains only ground terms (no variables)"""
        return self.left.is_ground() and self.right.is_ground()
    
    def get_variables(self) -> Set[str]:
        """Get all variable names in this formula"""
        return self.left.get_variables() | self.right.get_variables()

class Disjunction(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
    
    def __str__(self) -> str:
        return f"({self.left} ∨ {self.right})"
    
    def is_atomic(self) -> bool:
        return False
    
    def is_literal(self) -> bool:
        return False
    
    def __eq__(self, other):
        return isinstance(other, Disjunction) and self.left == other.left and self.right == other.right
    
    def __hash__(self):
        return hash(('or', self.left, self.right))
    
    def is_ground(self) -> bool:
        """Check if this formula contains only ground terms (no variables)"""
        return self.left.is_ground() and self.right.is_ground()
    
    def get_variables(self) -> Set[str]:
        """Get all variable names in this formula"""
        return self.left.get_variables() | self.right.get_variables()

class Implication(Formula):
    def __init__(self, antecedent: Formula, consequent: Formula):
        self.antecedent = antecedent
        self.consequent = consequent
    
    def __str__(self) -> str:
        return f"({self.antecedent} → {self.consequent})"
    
    def is_atomic(self) -> bool:
        return False
    
    def is_literal(self) -> bool:
        return False
    
    def __eq__(self, other):
        return isinstance(other, Implication) and self.antecedent == other.antecedent and self.consequent == other.consequent
    
    def __hash__(self):
        return hash(('imp', self.antecedent, self.consequent))
    
    def is_ground(self) -> bool:
        """Check if this formula contains only ground terms (no variables)"""
        return self.antecedent.is_ground() and self.consequent.is_ground()
    
    def get_variables(self) -> Set[str]:
        """Get all variable names in this formula"""
        return self.antecedent.get_variables() | self.consequent.get_variables()


class RestrictedExistentialQuantifier(Formula):
    """
    Represents a restricted existential quantifier ∃̌xφ(x) from Ferguson (2024).
    
    This implements the restricted Kleene existential quantifier which differs from 
    classical existential quantification in its treatment of undefined values.
    """
    
    def __init__(self, variable: 'Variable', body: Formula):
        if Variable is None:
            raise ValueError("Variable class not available - ensure term.py is imported")
        
        if not isinstance(variable, Variable):
            raise ValueError("Variable must be an instance of Variable class")
        
        if not isinstance(body, Formula):
            raise ValueError("Body must be a Formula")
        
        self.variable = variable
        self.body = body
        self.quantifier_type = "restricted_existential"
    
    def __str__(self) -> str:
        return f"∃̌{self.variable.name}({self.body})"
    
    def is_atomic(self) -> bool:
        return False
    
    def is_literal(self) -> bool:
        return False
    
    def is_ground(self) -> bool:
        """Quantified formulas are never ground since they bind variables"""
        return False
    
    def get_variables(self) -> Set[str]:
        """Get free variables (bound variable excluded)"""
        body_vars = self.body.get_variables()
        body_vars.discard(self.variable.name)  # Remove bound variable
        return body_vars
    
    def substitute(self, old_var: 'Variable', new_term: 'Term') -> 'Formula':
        """Apply substitution, avoiding variable capture"""
        if self.variable.name == old_var.name:
            # Bound variable matches - no substitution needed
            return self
        
        # Substitute in body if the variable doesn't conflict with bound variable
        if hasattr(self.body, 'substitute'):
            new_body = self.body.substitute(old_var, new_term)
            return RestrictedExistentialQuantifier(self.variable, new_body)
        else:
            return self
    
    def __eq__(self, other):
        return (isinstance(other, RestrictedExistentialQuantifier) and 
                self.variable == other.variable and self.body == other.body)
    
    def __hash__(self):
        return hash(('restricted_exists', self.variable, self.body))


class RestrictedUniversalQuantifier(Formula):
    """
    Represents a restricted universal quantifier ∀̌xφ(x) from Ferguson (2024).
    
    This implements the restricted Kleene universal quantifier which differs from 
    classical universal quantification in its treatment of undefined values.
    """
    
    def __init__(self, variable: 'Variable', body: Formula):
        if Variable is None:
            raise ValueError("Variable class not available - ensure term.py is imported")
        
        if not isinstance(variable, Variable):
            raise ValueError("Variable must be an instance of Variable class")
        
        if not isinstance(body, Formula):
            raise ValueError("Body must be a Formula")
        
        self.variable = variable
        self.body = body
        self.quantifier_type = "restricted_universal"
    
    def __str__(self) -> str:
        return f"∀̌{self.variable.name}({self.body})"
    
    def is_atomic(self) -> bool:
        return False
    
    def is_literal(self) -> bool:
        return False
    
    def is_ground(self) -> bool:
        """Quantified formulas are never ground since they bind variables"""
        return False
    
    def get_variables(self) -> Set[str]:
        """Get free variables (bound variable excluded)"""
        body_vars = self.body.get_variables()
        body_vars.discard(self.variable.name)  # Remove bound variable
        return body_vars
    
    def substitute(self, old_var: 'Variable', new_term: 'Term') -> 'Formula':
        """Apply substitution, avoiding variable capture"""
        if self.variable.name == old_var.name:
            # Bound variable matches - no substitution needed
            return self
        
        # Substitute in body if the variable doesn't conflict with bound variable
        if hasattr(self.body, 'substitute'):
            new_body = self.body.substitute(old_var, new_term)
            return RestrictedUniversalQuantifier(self.variable, new_body)
        else:
            return self
    
    def __eq__(self, other):
        return (isinstance(other, RestrictedUniversalQuantifier) and 
                self.variable == other.variable and self.body == other.body)
    
    def __hash__(self):
        return hash(('restricted_forall', self.variable, self.body))


# Tableau data structures
class RuleType(Enum):
    INITIAL = "Initial"
    DOUBLE_NEGATION = "Double Negation"
    CONJUNCTION = "Conjunction"
    NEG_CONJUNCTION = "Negated Conjunction"  
    DISJUNCTION = "Disjunction"
    NEG_DISJUNCTION = "Negated Disjunction"
    IMPLICATION = "Implication"
    NEG_IMPLICATION = "Negated Implication"
    RESTRICTED_EXISTENTIAL = "Restricted Existential"
    RESTRICTED_UNIVERSAL = "Restricted Universal"

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
    def __init__(self, branch_id: int):
        self.id = branch_id
        self.formulas: Set[Formula] = set()
        self.is_closed = False
        self.closure_reason: Optional[Tuple[Formula, Formula]] = None
    
    def add_formula(self, formula: Formula):
        self.formulas.add(formula)
        self._check_closure()
    
    def _check_closure(self):
        """Check if branch contains a contradiction (A and ¬A)"""
        # First normalize all formulas by removing double negations
        normalized = set()
        for formula in self.formulas:
            normalized.add(self._normalize_formula(formula))
        
        # Check for contradictions in normalized formulas
        for formula in normalized:
            if isinstance(formula, Negation) and isinstance(formula.operand, Atom):
                # Check for ¬A
                atom = formula.operand
                if atom in normalized:
                    self.is_closed = True
                    self.closure_reason = (atom, formula)
                    return
            elif isinstance(formula, Atom):
                # Check for A
                neg_formula = Negation(formula)
                if neg_formula in normalized:
                    self.is_closed = True
                    self.closure_reason = (formula, neg_formula)
                    return
    
    def _normalize_formula(self, formula: Formula) -> Formula:
        """Remove double negations"""
        if isinstance(formula, Negation) and isinstance(formula.operand, Negation):
            return self._normalize_formula(formula.operand.operand)
        return formula
    
    def has_unexpanded_formulas(self) -> bool:
        """Check if branch has formulas that can still be expanded"""
        if self.is_closed:
            return False
        
        for formula in self.formulas:
            if not formula.is_literal():
                return True
        return False
    
    def get_next_formula_to_expand(self) -> Optional[Formula]:
        """Get the next non-literal formula to expand"""
        if self.is_closed:
            return None
        
        for formula in self.formulas:
            if not formula.is_literal():
                return formula
        return None

class Tableau:
    def __init__(self, initial_formula: Formula):
        self.initial_formula = initial_formula
        self.node_counter = 0
        self.branch_counter = 0
        self.root: Optional[TableauNode] = None
        self.branches: List[Branch] = []
        self.all_nodes: List[TableauNode] = []
        
    def build(self) -> bool:
        """Build the complete tableau. Returns True if satisfiable, False if unsatisfiable."""
        # Start with the formula itself (not negated) to test satisfiability
        
        # Create root node
        self.root = self._create_node(self.initial_formula, RuleType.INITIAL)
        
        # Create initial branch
        initial_branch = Branch(self._next_branch_id())
        initial_branch.add_formula(self.initial_formula)
        self.branches.append(initial_branch)
        
        # Expand systematically
        self._expand_all_branches()
        
        # Check result: satisfiable if any branch remains open
        open_branches = [b for b in self.branches if not b.is_closed]
        return len(open_branches) > 0
    
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
    
    def _expand_all_branches(self):
        """Systematically expand all branches until completion"""
        changed = True
        while changed:
            changed = False
            
            # Work on a copy of branches since we might add new ones
            current_branches = self.branches.copy()
            
            for branch in current_branches:
                if branch.has_unexpanded_formulas():
                    formula = branch.get_next_formula_to_expand()
                    if formula:
                        new_branches = self._expand_formula(formula, branch)
                        if new_branches:
                            changed = True
    
    def _expand_formula(self, formula: Formula, branch: Branch) -> List[Branch]:
        """Expand a formula according to tableau rules"""
        
        # Find the parent node for this formula
        parent_node = None
        for node in self.all_nodes:
            if node.formula == formula:
                parent_node = node
                break
        
        # Remove the formula being expanded from the branch first
        branch.formulas.discard(formula)
        
        # Double negation: ¬¬A → A
        if isinstance(formula, Negation) and isinstance(formula.operand, Negation):
            inner = formula.operand.operand
            node = self._create_node(inner, RuleType.DOUBLE_NEGATION, parent_node)
            branch.add_formula(inner)
            return []
        
        # Conjunction: A ∧ B → A, B (same branch)
        elif isinstance(formula, Conjunction):
            left_node = self._create_node(formula.left, RuleType.CONJUNCTION, parent_node)
            right_node = self._create_node(formula.right, RuleType.CONJUNCTION, parent_node)
            branch.add_formula(formula.left)
            branch.add_formula(formula.right)
            return []
        
        # Negated conjunction: ¬(A ∧ B) → ¬A ∨ ¬B (branching)
        elif isinstance(formula, Negation) and isinstance(formula.operand, Conjunction):
            conj = formula.operand
            left_neg = Negation(conj.left)
            right_neg = Negation(conj.right)
            
            # Create two new branches
            left_branch = Branch(self._next_branch_id())
            right_branch = Branch(self._next_branch_id())
            
            # Copy existing formulas to new branches (formula already removed)
            for f in branch.formulas:
                left_branch.add_formula(f)
                right_branch.add_formula(f)
            
            # Add the new formulas
            left_node = self._create_node(left_neg, RuleType.NEG_CONJUNCTION, parent_node)
            right_node = self._create_node(right_neg, RuleType.NEG_CONJUNCTION, parent_node)
            left_branch.add_formula(left_neg)
            right_branch.add_formula(right_neg)
            
            # Remove original branch and add new ones
            self.branches.remove(branch)
            self.branches.extend([left_branch, right_branch])
            return [left_branch, right_branch]
        
        # Disjunction: A ∨ B → A | B (branching)
        elif isinstance(formula, Disjunction):
            # Create two new branches
            left_branch = Branch(self._next_branch_id())
            right_branch = Branch(self._next_branch_id())
            
            # Copy existing formulas to new branches (formula already removed)
            for f in branch.formulas:
                left_branch.add_formula(f)
                right_branch.add_formula(f)
            
            # Add the new formulas
            left_node = self._create_node(formula.left, RuleType.DISJUNCTION, parent_node)
            right_node = self._create_node(formula.right, RuleType.DISJUNCTION, parent_node)
            left_branch.add_formula(formula.left)
            right_branch.add_formula(formula.right)
            
            # Remove original branch and add new ones
            self.branches.remove(branch)
            self.branches.extend([left_branch, right_branch])
            return [left_branch, right_branch]
        
        # Negated disjunction: ¬(A ∨ B) → ¬A ∧ ¬B (same branch)
        elif isinstance(formula, Negation) and isinstance(formula.operand, Disjunction):
            disj = formula.operand
            left_neg = Negation(disj.left)
            right_neg = Negation(disj.right)
            
            left_node = self._create_node(left_neg, RuleType.NEG_DISJUNCTION, parent_node)
            right_node = self._create_node(right_neg, RuleType.NEG_DISJUNCTION, parent_node)
            branch.add_formula(left_neg)
            branch.add_formula(right_neg)
            return []
        
        # Implication: A → B ≡ ¬A ∨ B (branching)
        elif isinstance(formula, Implication):
            neg_ant = Negation(formula.antecedent)
            
            # Create two new branches
            left_branch = Branch(self._next_branch_id())
            right_branch = Branch(self._next_branch_id())
            
            # Copy existing formulas to new branches (formula already removed)
            for f in branch.formulas:
                left_branch.add_formula(f)
                right_branch.add_formula(f)
            
            # Add the new formulas
            left_node = self._create_node(neg_ant, RuleType.IMPLICATION, parent_node)
            right_node = self._create_node(formula.consequent, RuleType.IMPLICATION, parent_node)
            left_branch.add_formula(neg_ant)
            right_branch.add_formula(formula.consequent)
            
            # Remove original branch and add new ones
            self.branches.remove(branch)
            self.branches.extend([left_branch, right_branch])
            return [left_branch, right_branch]
        
        # Negated implication: ¬(A → B) → A ∧ ¬B (same branch)
        elif isinstance(formula, Negation) and isinstance(formula.operand, Implication):
            impl = formula.operand
            neg_cons = Negation(impl.consequent)
            
            ant_node = self._create_node(impl.antecedent, RuleType.NEG_IMPLICATION, parent_node)
            neg_cons_node = self._create_node(neg_cons, RuleType.NEG_IMPLICATION, parent_node)
            branch.add_formula(impl.antecedent)
            branch.add_formula(neg_cons)
            return []
        
        return []
    
    def print_tree(self):
        """Print the tableau as a unified tree structure"""
        print("=" * 70)
        print("SEMANTIC TABLEAU TREE")
        print("=" * 70)
        print(f"Testing satisfiability of: {self.initial_formula}")
        print()
        
        if self.root:
            self._print_node_tree(self.root)
        
        print("\n" + "=" * 70)
        open_branches = [b for b in self.branches if not b.is_closed]
        if open_branches:
            print("✓ SATISFIABLE - Formula has satisfying interpretation(s)")
            print(f"Open branches: {[b.id for b in open_branches]}")
        else:
            print("✗ UNSATISFIABLE - All branches close")
        print("=" * 70)
    
    def _print_node_tree(self, node: TableauNode, prefix: str = "", is_last: bool = True, visited: set = None):
        """Print the tableau as a unified tree showing the formula decomposition"""
        if visited is None:
            visited = set()
        
        if node.id in visited:
            return
        visited.add(node.id)
        
        # Determine the rule description - show the rule that PRODUCED this node
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
        
        # Find which branch(es) this formula ends up in
        branch_info = self._get_branch_info_for_formula(node.formula)
        
        # Print the current node
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{node.id}: {node.formula}{branch_info}{rule_desc}")
        
        # Update prefix for children
        child_prefix = prefix + ("    " if is_last else "│   ")
        
        # Print children
        children = sorted(node.children, key=lambda x: x.id)
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            self._print_node_tree(child, child_prefix, is_last_child, visited)
    
    def _get_branch_info_for_formula(self, formula: Formula) -> str:
        """Get branch information for a formula"""
        # Find branches that contain this formula
        containing_branches = []
        for branch in self.branches:
            if formula in branch.formulas or any(self._formulas_equivalent(formula, f) for f in branch.formulas):
                status = "✗" if branch.is_closed else "✓"
                containing_branches.append(f"{branch.id}{status}")
        
        if containing_branches:
            return f" [Branch {', '.join(containing_branches)}]"
        return ""
    
    def _formulas_equivalent(self, f1: Formula, f2: Formula) -> bool:
        """Check if two formulas are equivalent (for branch tracking)"""
        # Simple equivalence check
        return str(f1) == str(f2)

# Example usage and testing
def test_tableau():
    """Test the tableau with some example formulas"""
    
    # Example 1: (p ∧ ¬p) - should be unsatisfiable
    p = Atom("p")
    formula1 = Conjunction(p, Negation(p))
    
    print("Testing: (p ∧ ¬p)")
    print("This should be UNSATISFIABLE (contradiction)")
    tableau1 = Tableau(formula1)
    result1 = tableau1.build()
    tableau1.print_tree()
    
    print("\n" + "="*70 + "\n")
    
    # Example 2: (p ∨ ¬p) - should be satisfiable (tautology)
    formula2 = Disjunction(p, Negation(p))
    
    print("Testing: (p ∨ ¬p)")
    tableau2 = Tableau(formula2)
    result2 = tableau2.build()
    tableau2.print_tree()
    
    print("\n" + "="*70 + "\n")
    
    # Example 3: Modus ponens: ((p → q) ∧ p) → q
    q = Atom("q")
    impl = Implication(p, q)
    premise = Conjunction(impl, p)
    formula3 = Implication(premise, q)
    
    print("Testing: ((p → q) ∧ p) → q")
    tableau3 = Tableau(formula3)
    result3 = tableau3.build()
    tableau3.print_tree()

if __name__ == "__main__":
    test_tableau()