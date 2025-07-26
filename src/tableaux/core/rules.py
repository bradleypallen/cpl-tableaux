#!/usr/bin/env python3
"""
Declarative rule specification system for tableau methods.

This module provides a DSL for specifying tableau rules in a declarative way,
making it easy to define rules for new logic systems without writing
procedural code.
"""

from abc import ABC, abstractmethod
from typing import List, Set, Dict, Optional, Callable, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import re

from ..core.formula import Formula, CompoundFormula, AtomicFormula, Predicate, Variable, Constant
from ..core.signs import Sign, SignedFormula


class RuleType(Enum):
    """Types of tableau rules."""
    ALPHA = "alpha"  # Non-branching rules
    BETA = "beta"    # Branching rules
    GAMMA = "gamma"  # Universal quantifier rules
    DELTA = "delta"  # Existential quantifier rules
    SPECIAL = "special"  # Custom rules with special behavior


@dataclass
class RulePattern:
    """Pattern for matching signed formulas in rules."""
    sign_pattern: str  # e.g., "T", "F", "U", etc.
    formula_pattern: str  # e.g., "A ' B", "�A", etc.
    
    def matches(self, signed_formula: SignedFormula) -> Optional[Dict[str, Formula]]:
        """
        Check if a signed formula matches this pattern.
        Returns a dict mapping pattern variables to actual formulas if match succeeds.
        """
        # Check sign match
        if not self._sign_matches(signed_formula.sign):
            return None
        
        # Check formula pattern match
        return self._formula_matches(signed_formula.formula)
    
    def _sign_matches(self, sign: Sign) -> bool:
        """Check if sign matches the pattern."""
        return str(sign) == self.sign_pattern
    
    def _formula_matches(self, formula: Formula) -> Optional[Dict[str, Formula]]:
        """
        Match formula against pattern, returning variable bindings.
        Enhanced to handle first-order restricted quantifier patterns.
        """
        pattern = self.formula_pattern.strip()
        
        # Handle atomic patterns (single uppercase variable matches any formula)
        if pattern.isupper() and len(pattern) == 1:
            return {pattern: formula}
        
        # Handle restricted quantifier patterns like "[∀X P(X)]Q(X)" or "[∃X P(X)]Q(X)"
        if pattern.startswith('[') and ']' in pattern:
            return self._match_restricted_quantifier(pattern, formula)
        
        # Handle negation patterns like "~A"
        if pattern.startswith('~'):
            sub_pattern = pattern[1:].strip()
            if (isinstance(formula, CompoundFormula) and 
                formula.get_main_connective() == "~" and
                len(formula.get_subformulas()) == 1):
                return self._formula_matches_helper(sub_pattern, formula.get_subformulas()[0])
            return None
        
        # Handle binary connective patterns like "A & B", "A | B", "A -> B"
        for conn in ['&', '|', '->', '←', '↔']:
            if f' {conn} ' in pattern:
                return self._match_binary_connective(pattern, formula, conn)
        
        # Handle simple variable patterns
        pattern_parts = pattern.split()
        if len(pattern_parts) == 1 and pattern_parts[0].isupper():
            return {pattern_parts[0]: formula}
        
        return None
    
    def _match_restricted_quantifier(self, pattern: str, formula: Formula) -> Optional[Dict[str, Formula]]:
        """Match restricted quantifier patterns like '[∀X P(X)]Q(X)' against actual formulas."""
        from ..core.formula import RestrictedUniversalFormula, RestrictedExistentialFormula
        
        # Parse pattern like "[∀X P(X)]Q(X)" or "[∃X P(X)]Q(X)"
        if not (pattern.startswith('[') and ']' in pattern):
            return None
        
        bracket_end = pattern.find(']')
        quantifier_part = pattern[1:bracket_end]  # "∀X P(X)" or "∃X P(X)"
        matrix_part = pattern[bracket_end+1:]     # "Q(X)"
        
        # Determine quantifier type
        if quantifier_part.startswith('∀'):
            expected_type = RestrictedUniversalFormula
            quantifier = '∀'
        elif quantifier_part.startswith('∃'):
            expected_type = RestrictedExistentialFormula
            quantifier = '∃'
        else:
            return None
        
        # Check if formula is of the expected type
        if not isinstance(formula, expected_type):
            return None
        
        # Extract the restriction and matrix from the actual formula
        # For restricted quantifier formulas, we have:
        # - formula.restriction: the P(X) part
        # - formula.matrix: the Q(X) part
        
        # Return bindings that map P to restriction and Q to matrix
        # This allows the tableau rules to work with P(c) and Q(c) patterns
        return {
            'P': formula.restriction,  # Maps to the restriction part
            'Q': formula.matrix        # Maps to the matrix part
        }
    
    def _match_binary_connective(self, pattern: str, formula: Formula, conn: str) -> Optional[Dict[str, Formula]]:
        """Match binary connective patterns like 'A & B' against formulas."""
        parts = pattern.split(f' {conn} ')
        if len(parts) != 2:
            return None
        
        left_pattern, right_pattern = parts
        left_pattern = left_pattern.strip()
        right_pattern = right_pattern.strip()
        
        # Check if formula matches the connective
        if (isinstance(formula, CompoundFormula) and
            formula.get_main_connective() == conn and
            len(formula.get_subformulas()) == 2):
            
            left_formula, right_formula = formula.get_subformulas()
            
            # Try to match both subformulas
            left_bindings = self._formula_matches_helper(left_pattern, left_formula)
            if left_bindings is None:
                return None
            
            right_bindings = self._formula_matches_helper(right_pattern, right_formula)
            if right_bindings is None:
                return None
            
            # Check for conflicts in variable bindings
            for var in left_bindings:
                if var in right_bindings and left_bindings[var] != right_bindings[var]:
                    return None
            
            # Merge bindings
            result = left_bindings.copy()
            result.update(right_bindings)
            return result
        
        return None
    
    def _formula_matches_helper(self, pattern: str, formula: Formula) -> Optional[Dict[str, Formula]]:
        """Helper method for recursive pattern matching."""
        # Create a temporary RulePattern to reuse the matching logic
        temp_pattern = RulePattern("dummy", pattern)
        return temp_pattern._formula_matches(formula)


@dataclass
class TableauRule:
    """Declarative specification of a tableau rule."""
    name: str
    rule_type: RuleType
    premises: List[RulePattern]
    conclusions: List[List[Union[str, Callable]]]  # List of branches, each with patterns
    priority: int = 0
    constraints: List[Callable] = field(default_factory=list)
    
    def apply(self, signed_formulas: List[SignedFormula], logic_system=None) -> Optional[List[List[SignedFormula]]]:
        """
        Apply this rule to a list of signed formulas.
        Returns list of new branches if rule applies, None otherwise.
        """
        # Try to match all premises
        bindings = {}
        matched_formulas = []
        
        for premise in self.premises:
            match_found = False
            for sf in signed_formulas:
                if sf not in matched_formulas:
                    match = premise.matches(sf)
                    if match:
                        # Merge bindings, checking for conflicts
                        for var, formula in match.items():
                            if var in bindings and bindings[var] != formula:
                                # Conflict - this rule doesn't apply
                                return None
                            bindings[var] = formula
                        matched_formulas.append(sf)
                        match_found = True
                        break
            
            if not match_found:
                # Premise not satisfied
                return None
        
        # Check constraints
        for constraint in self.constraints:
            if not constraint(bindings, signed_formulas):
                return None
        
        # Generate conclusions
        new_branches = []
        for branch_patterns in self.conclusions:
            new_branch = []
            for pattern in branch_patterns:
                if isinstance(pattern, str):
                    # Parse and instantiate the pattern
                    new_sf = self._instantiate_pattern(pattern, bindings, logic_system)
                    if new_sf:
                        new_branch.append(new_sf)
                elif callable(pattern):
                    # Custom conclusion generator
                    result = pattern(bindings)
                    if isinstance(result, SignedFormula):
                        new_branch.append(result)
                    elif isinstance(result, list):
                        new_branch.extend(result)
            
            if new_branch:
                new_branches.append(new_branch)
        
        return new_branches if new_branches else None
    
    def _instantiate_pattern(self, pattern: str, bindings: Dict[str, Formula], logic_system=None) -> Optional[SignedFormula]:
        """Instantiate a conclusion pattern with bindings."""
        # Parse pattern like "T:A" or "F:(A ' B)"
        match = re.match(r"(\w+):(.+)", pattern)
        if not match:
            return None
        
        sign_str, formula_pattern = match.groups()
        
        # Create sign based on logic system context if available
        sign = None
        if logic_system and hasattr(logic_system, 'get_sign_system'):
            sign_system = logic_system.get_sign_system()
            # Try to create sign using the logic system's sign system
            for s in sign_system.signs():
                if str(s) == sign_str:
                    sign = s
                    break
        
        # Fallback to generic sign creation
        if sign is None:
            from ..core.signs import ClassicalSign, ThreeValuedSign, FourValuedSign
            # Order matters - check more specific types first
            if sign_str in ["M", "N"]:  # wKrQ specific signs
                sign = FourValuedSign(sign_str)
            elif sign_str == "U":  # Three-valued specific sign
                sign = ThreeValuedSign(sign_str)
            elif sign_str in ["T", "F"]:  # Could be any system
                # Default to classical for backward compatibility
                sign = ClassicalSign(sign_str == "T")
            else:
                return None
        
        # Instantiate formula pattern
        formula = self._instantiate_formula_pattern(formula_pattern, bindings)
        if not formula:
            return None
        
        return SignedFormula(sign, formula)
    
    def _instantiate_formula_pattern(self, pattern: str, bindings: Dict[str, Formula]) -> Optional[Formula]:
        """Instantiate a formula pattern with bindings."""
        pattern = pattern.strip()
        
        # Direct variable
        if pattern in bindings:
            return bindings[pattern]
        
        # Handle first-order patterns like P(c) or Q(c) 
        if '(' in pattern and pattern.endswith(')'):
            return self._instantiate_first_order_pattern(pattern, bindings)
        
        # Negation
        if pattern.startswith("~") and len(pattern) > 1:
            sub_pattern = pattern[1:].strip()
            sub = self._instantiate_formula_pattern(sub_pattern, bindings)
            if sub:
                from ..core.formula import CompoundFormula, ConnectiveSpec
                neg_spec = ConnectiveSpec("~", 1, 1, format_style="prefix")
                return CompoundFormula(neg_spec, sub)
        
        # Binary connectives (simplified)
        for conn in ["'", "(", "->"]:
            if conn in pattern:
                parts = pattern.split(conn)
                if len(parts) == 2:
                    left = self._instantiate_formula_pattern(parts[0].strip(), bindings)
                    right = self._instantiate_formula_pattern(parts[1].strip(), bindings)
                    if left and right:
                        from ..core.formula import CompoundFormula, ConnectiveSpec
                        spec = ConnectiveSpec(conn, 2, 2 if conn == "'" else 3)
                        return CompoundFormula(spec, left, right)
        
        return None
    
    def _instantiate_first_order_pattern(self, pattern: str, bindings: Dict[str, Formula]) -> Optional[Formula]:
        """Handle first-order patterns like P(c) or Q(c)."""
        
        # Parse pattern like "P(c)" or "Q(c)"
        paren_pos = pattern.find('(')
        if paren_pos == -1:
            return None
            
        pred_var = pattern[:paren_pos].strip()  # "P" or "Q"
        arg_pattern = pattern[paren_pos+1:-1].strip()  # "c"
        
        # Check if we have a binding for the predicate variable
        if pred_var not in bindings:
            return None
            
        base_formula = bindings[pred_var]
        
        # If arg_pattern is "c", we need to substitute a fresh constant
        if arg_pattern == "c":
            # Generate a fresh constant name
            fresh_constant = Constant(f"c{self._get_next_constant_id()}")
            
            # Substitute the fresh constant for variables in the base formula
            return self._substitute_variable_with_constant(base_formula, fresh_constant)
        
        return None
    
    def _get_next_constant_id(self) -> int:
        """Get the next available constant ID for fresh constant generation."""
        # Simple implementation - could be made more sophisticated
        if not hasattr(self, '_constant_counter'):
            self._constant_counter = 0
        self._constant_counter += 1
        return self._constant_counter
    
    def _substitute_variable_with_constant(self, formula: Formula, constant) -> Formula:
        """Substitute all variables in a formula with the given constant."""
        
        # Check by class name to avoid import issues
        if formula.__class__.__name__ == 'Predicate':
            # Replace all variables in the predicate with the constant
            new_terms = []
            for term in formula.terms:
                if term.__class__.__name__ == 'Variable':
                    new_terms.append(constant)
                else:
                    new_terms.append(term)
            
            # Create new predicate with substituted terms
            from ..core.formula import Predicate
            return Predicate(formula.name, new_terms)
        
        elif isinstance(formula, CompoundFormula):
            # Recursively substitute in subformulas
            new_subformulas = []
            for sub in formula.get_subformulas():
                new_sub = self._substitute_variable_with_constant(sub, constant)
                new_subformulas.append(new_sub)
            
            # Create new compound formula with substituted subformulas
            return CompoundFormula(formula.connective_spec, *new_subformulas)
        
        else:
            # For other formula types, return as-is
            return formula


class RuleSet:
    """Collection of tableau rules with efficient lookup."""
    
    def __init__(self):
        self.rules: List[TableauRule] = []
        self._rules_by_type: Dict[RuleType, List[TableauRule]] = {
            rt: [] for rt in RuleType
        }
    
    def add_rule(self, rule: TableauRule):
        """Add a rule to the set."""
        self.rules.append(rule)
        self._rules_by_type[rule.rule_type].append(rule)
        # Sort by priority
        self._rules_by_type[rule.rule_type].sort(key=lambda r: r.priority, reverse=True)
    
    def get_applicable_rules(self, signed_formulas: List[SignedFormula],
                           rule_type: Optional[RuleType] = None, logic_system=None) -> List[TableauRule]:
        """Get all rules that could apply to the given signed formulas."""
        if rule_type:
            rules_to_check = self._rules_by_type[rule_type]
        else:
            rules_to_check = self.rules
        
        applicable = []
        for rule in rules_to_check:
            if rule.apply(signed_formulas, logic_system) is not None:
                applicable.append(rule)
        
        return applicable
    
    def apply_first_applicable(self, signed_formulas: List[SignedFormula],
                             prefer_type: Optional[RuleType] = None, logic_system=None) -> Optional[Tuple[TableauRule, List[List[SignedFormula]]]]:
        """Apply the first applicable rule, returning the rule and result."""
        # Try preferred type first
        if prefer_type:
            for rule in self._rules_by_type[prefer_type]:
                result = rule.apply(signed_formulas, logic_system)
                if result is not None:
                    return (rule, result)
        
        # Try all rules in priority order
        for rule in sorted(self.rules, key=lambda r: r.priority, reverse=True):
            result = rule.apply(signed_formulas, logic_system)
            if result is not None:
                return (rule, result)
        
        return None


# Convenience functions for creating rules
def alpha_rule(name: str, premise: str, conclusion1: str, conclusion2: str, priority: int = 1) -> TableauRule:
    """Create a simple alpha (non-branching) rule."""
    sign, formula = premise.split(":", 1)
    return TableauRule(
        name=name,
        rule_type=RuleType.ALPHA,
        premises=[RulePattern(sign, formula)],
        conclusions=[[conclusion1, conclusion2]],
        priority=priority
    )


def beta_rule(name: str, premise: str, branch1: str, branch2: str, priority: int = 2) -> TableauRule:
    """Create a simple beta (branching) rule."""
    sign, formula = premise.split(":", 1)
    return TableauRule(
        name=name,
        rule_type=RuleType.BETA,
        premises=[RulePattern(sign, formula)],
        conclusions=[[branch1], [branch2]],
        priority=priority
    )