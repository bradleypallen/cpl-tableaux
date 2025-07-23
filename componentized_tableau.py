#!/usr/bin/env python3
"""
Componentized Tableau Engine

A unified tableau implementation that works with any LogicSystem,
replacing the hardcoded rule logic with pluggable components while
preserving existing optimizations and performance characteristics.
"""

from typing import List, Union, Optional, Set, Dict, Any
from copy import deepcopy
from collections import deque

from formula import Formula, Atom
from tableau_rules import BranchInterface, RuleContext, TableauRule
from logic_system import LogicSystem, get_logic_system
from tableau import TableauNode  # Reuse existing node structure


class ComponentizedTableau:
    """
    Unified tableau engine that works with any logic system.
    
    This class replaces the hardcoded rule logic in tableau.py and wk3_tableau.py
    with a pluggable component system while preserving all existing optimizations.
    """
    
    def __init__(self, formula: Union[Formula, List[Formula]], 
                 logic_system: Union[str, LogicSystem],
                 track_tree: bool = True):
        """
        Create a componentized tableau.
        
        Args:
            formula: Formula(s) to test for satisfiability
            logic_system: Logic system name or LogicSystem instance
            track_tree: Whether to build tree structure for visualization
        """
        # Handle logic system parameter
        if isinstance(logic_system, str):
            self.logic_system = get_logic_system(logic_system)
            if self.logic_system is None:
                raise ValueError(f"Unknown logic system: {logic_system}")
        else:
            self.logic_system = logic_system
        
        # Handle formula parameter
        if isinstance(formula, list):
            self.initial_formulas = formula
        else:
            self.initial_formulas = [formula]
        
        self.track_tree = track_tree
        
        # Initialize tableau state
        self.branches: List[BranchInterface] = []
        self.next_branch_id = 1
        self.root = None
        self.built = False
        
        # Statistics
        self.rule_applications = 0
        self.branch_creations = 0
        self.node_counter = 0
        
        # Build initial branch
        self._initialize_tableau()
    
    def _initialize_tableau(self):
        """Initialize the tableau with the root branch"""
        initial_branch = self.logic_system.create_branch(0, self.initial_formulas)
        self.branches = [initial_branch]
        
        if self.track_tree:
            # Create root node with initial formulas
            from formula import RuleType
            self.root = TableauNode(
                id=self._get_next_node_id(),
                formula=self.initial_formulas[0] if self.initial_formulas else Atom("dummy"),
                rule_applied=RuleType.INITIAL
            )
    
    def build(self) -> bool:
        """
        Build the complete tableau and return satisfiability.
        
        Returns:
            True if satisfiable, False if unsatisfiable
        """
        if self.built:
            return self.is_satisfiable()
        
        # Main tableau construction loop
        while True:
            # Find branches that need expansion
            expandable_branches = self._get_expandable_branches()
            
            if not expandable_branches:
                break  # No more expansion possible
            
            # Apply optimizations before expansion
            self._apply_subsumption_elimination()
            
            # Expand one branch (prioritize α-rules)
            branch = expandable_branches[0]
            self._expand_branch(branch)
        
        self.built = True
        return self.is_satisfiable()
    
    def _get_expandable_branches(self) -> List[BranchInterface]:
        """Get branches that can still be expanded"""
        expandable = []
        
        for branch in self.branches:
            if branch.is_closed:
                continue
            
            # Check if branch has formulas that can be expanded
            expandable_formulas = self._get_expandable_formulas(branch)
            if expandable_formulas:
                expandable.append(branch)
        
        return expandable
    
    def _get_expandable_formulas(self, branch: BranchInterface) -> List[Formula]:
        """Get formulas in branch that can be expanded with rules"""
        expandable = []
        
        for formula in branch.formulas:
            # Check if any rule applies to this formula
            applicable_rules = self.logic_system.find_applicable_rules(formula)
            if applicable_rules:
                expandable.append(formula)
        
        # Apply formula prioritization (α-rules before β-rules)
        return self._prioritize_formulas(expandable)
    
    def _prioritize_formulas(self, formulas: List[Formula]) -> List[Formula]:
        """
        Prioritize formulas for expansion (α-rules before β-rules).
        This preserves the existing optimization from the original implementation.
        """
        alpha_formulas = []
        beta_formulas = []
        other_formulas = []
        
        for formula in formulas:
            best_rule = self.logic_system.get_best_rule(formula)
            if best_rule:
                if best_rule.is_alpha_rule:
                    alpha_formulas.append(formula)
                elif best_rule.is_beta_rule:
                    beta_formulas.append(formula)
                else:
                    other_formulas.append(formula)
            else:
                other_formulas.append(formula)
        
        # Return in priority order: α-rules first, then β-rules, then others
        return alpha_formulas + beta_formulas + other_formulas
    
    def _expand_branch(self, branch: BranchInterface):
        """Expand a single branch by applying one rule"""
        expandable_formulas = self._get_expandable_formulas(branch)
        
        if not expandable_formulas:
            return  # Nothing to expand
        
        # Take the highest priority formula
        formula = expandable_formulas[0]
        
        # Get the best rule for this formula
        rule = self.logic_system.get_best_rule(formula)
        if not rule:
            return
        
        # Apply the rule
        self._apply_rule(rule, formula, branch)
        self.rule_applications += 1
    
    def _apply_rule(self, rule: TableauRule, formula: Formula, branch: BranchInterface):
        """Apply a rule to a formula in a branch"""
        
        # Create rule context
        context = RuleContext(
            tableau=self,
            branch=branch,
            parent_node=self._find_node_for_branch(branch) if self.track_tree else None
        )
        
        # Apply the rule
        result = self.logic_system.apply_rule(rule, formula, context)
        
        # Handle the result
        if result.branch_count == 1:
            # α-rule: add formulas to same branch
            new_formulas = result.formulas_for_branches[0]
            branch.add_formulas(new_formulas)
            
            # Update tree structure if tracking
            if self.track_tree and context.parent_node:
                for new_formula in new_formulas:
                    from formula import RuleType
                    new_node = TableauNode(
                        id=self._get_next_node_id(),
                        formula=new_formula,
                        rule_applied=rule.rule_type,
                        parent=context.parent_node
                    )
        
        else:
            # β-rule: create new branches
            self._handle_branching_rule(rule, formula, branch, result, context)
        
        # Remove the expanded formula from the original branch
        if formula in branch.formulas:
            branch._formulas.remove(formula)  # Direct access to avoid triggering checks
    
    def _handle_branching_rule(self, rule: TableauRule, formula: Formula, 
                              original_branch: BranchInterface, result, context):
        """Handle rules that create multiple branches"""
        
        # Remove original branch from the active list
        if original_branch in self.branches:
            self.branches.remove(original_branch)
        
        new_branches = []
        
        for branch_formulas in result.formulas_for_branches:
            # Create new branch by copying original
            new_branch = self.logic_system.copy_branch(original_branch, self.next_branch_id)
            self.next_branch_id += 1
            self.branch_creations += 1
            
            # Remove the expanded formula from new branch
            if formula in new_branch.formulas:
                new_branch._formulas.remove(formula)
            
            # Add new formulas
            new_branch.add_formulas(branch_formulas)
            
            new_branches.append(new_branch)
            
            # Update tree structure if tracking
            if self.track_tree and context.parent_node:
                for new_formula in branch_formulas:
                    new_node = TableauNode(
                        id=self._get_next_node_id(),
                        formula=new_formula,
                        rule_applied=rule.rule_type,
                        parent=context.parent_node
                    )
        
        # Add new branches to active list
        self.branches.extend(new_branches)
    
    def _get_next_node_id(self) -> int:
        """Get next available node ID"""
        self.node_counter += 1
        return self.node_counter
    
    def _find_node_for_branch(self, branch: BranchInterface) -> Optional[TableauNode]:
        """Find the tree node corresponding to a branch (for tree tracking)"""
        # This is a simplified implementation
        # In a full implementation, we'd maintain a branch-to-node mapping
        return self.root
    
    def _apply_subsumption_elimination(self):
        """Apply subsumption elimination optimization"""
        before_count = len(self.branches)
        self.branches = self.logic_system.remove_subsumed_branches(self.branches)
        after_count = len(self.branches)
        
        if after_count < before_count:
            # Subsumption eliminated some branches
            pass
    
    def is_satisfiable(self) -> bool:
        """Check if the formula set is satisfiable"""
        return any(not branch.is_closed for branch in self.branches)
    
    def extract_all_models(self):
        """Extract all satisfying models"""
        if not self.built:
            self.build()
        
        open_branches = [b for b in self.branches if not b.is_closed]
        return self.logic_system.extract_all_models(open_branches)
    
    def get_sample_model(self):
        """Get one satisfying model"""
        if not self.built:
            self.build()
        
        for branch in self.branches:
            if not branch.is_closed:
                return self.logic_system.extract_model(branch)
        
        return None
    
    def build_with_models(self):
        """Build tableau and return (satisfiable, models)"""
        satisfiable = self.build()
        models = self.extract_all_models() if satisfiable else []
        return satisfiable, models
    
    def print_tree(self):
        """Print the tableau tree (if tree tracking is enabled)"""
        if not self.track_tree or not self.root:
            print("Tree tracking disabled or no tree available")
            return
        
        print("Tableau Tree:")
        print("=" * 50)
        self._print_node(self.root, "")
        print()
        
        # Print branch summary
        open_branches = [b for b in self.branches if not b.is_closed]
        closed_branches = [b for b in self.branches if b.is_closed]
        
        print(f"Summary:")
        print(f"  Total branches: {len(self.branches)}")
        print(f"  Open branches: {len(open_branches)}")
        print(f"  Closed branches: {len(closed_branches)}")
        print(f"  Rule applications: {self.rule_applications}")
        
        if open_branches:
            print(f"  SATISFIABLE - Open branch IDs: {[b.id for b in open_branches]}")
        else:
            print(f"  UNSATISFIABLE - All branches closed")
    
    def _print_node(self, node: TableauNode, prefix: str):
        """Recursively print tree nodes"""
        # Show the single formula for this node
        formula_str = str(node.formula)
        rule_str = f" ({node.rule_applied.name})" if hasattr(node.rule_applied, 'name') else f" ({node.rule_applied})" if node.rule_applied else ""
        print(f"{prefix}├─ {formula_str}{rule_str}")
        
        for i, child in enumerate(node.children):
            is_last = (i == len(node.children) - 1)
            child_prefix = prefix + ("    " if is_last else "│   ")
            self._print_node(child, child_prefix)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tableau construction statistics"""
        open_branches = [b for b in self.branches if not b.is_closed]
        closed_branches = [b for b in self.branches if b.is_closed]
        
        return {
            "logic_system": self.logic_system.config.name,
            "initial_formulas": len(self.initial_formulas),
            "total_branches": len(self.branches),
            "open_branches": len(open_branches),
            "closed_branches": len(closed_branches),
            "rule_applications": self.rule_applications,
            "branch_creations": self.branch_creations,
            "satisfiable": len(open_branches) > 0,
            "rules_used": len(self.logic_system.rules)
        }
    
    def describe(self) -> str:
        """Get a description of this tableau"""
        stats = self.get_statistics()
        
        description = f"Componentized Tableau\n"
        description += f"Logic System: {stats['logic_system']}\n"
        description += f"Initial Formulas: {stats['initial_formulas']}\n" 
        description += f"Result: {'SATISFIABLE' if stats['satisfiable'] else 'UNSATISFIABLE'}\n"
        description += f"Branches: {stats['total_branches']} ({stats['open_branches']} open, {stats['closed_branches']} closed)\n"
        description += f"Rule Applications: {stats['rule_applications']}\n"
        
        return description


# Convenience functions that mirror the original tableau.py API

def classical_tableau(formula: Union[Formula, List[Formula]], 
                     track_tree: bool = True) -> ComponentizedTableau:
    """Create a classical logic tableau"""
    return ComponentizedTableau(formula, "classical", track_tree)


def wk3_tableau(formula: Union[Formula, List[Formula]], 
               track_tree: bool = True) -> ComponentizedTableau:
    """Create a WK3 logic tableau"""
    return ComponentizedTableau(formula, "wk3", track_tree)


# Export main classes and functions
__all__ = [
    'ComponentizedTableau',
    'classical_tableau',
    'wk3_tableau'
]