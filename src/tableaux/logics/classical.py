#!/usr/bin/env python3
"""
Classical propositional logic plugin.

This module implements classical two-valued logic as a plugin for the
modular tableau framework, demonstrating how to define new logic systems.
"""

from ..core.formula import ConnectiveSpec, PropositionalAtom, CompoundFormula
from ..core.semantics import ClassicalTruthValueSystem
from ..core.signs import ClassicalSignSystem
from ..core.rules import alpha_rule, beta_rule, RuleType, TableauRule, RulePattern
from .logic_system import LogicSystem


class ClassicalLogic(LogicSystem):
    """Classical propositional logic system."""
    
    def initialize(self):
        """Initialize classical logic with connectives, semantics, and rules."""
        # Add connectives
        self.add_connective(ConnectiveSpec("'", 2, 3, "left", "infix"))  # conjunction
        self.add_connective(ConnectiveSpec("&", 2, 3, "left", "infix"))  # conjunction (alt)
        # Note: '(' is not a connective, it's a grouping symbol handled by the parser  
        self.add_connective(ConnectiveSpec("|", 2, 2, "left", "infix"))  # disjunction (alt)
        self.add_connective(ConnectiveSpec("~", 1, 4, "none", "prefix"))  # negation
        self.add_connective(ConnectiveSpec("->", 2, 1, "right", "infix"))  # implication
        
        # Set semantic systems
        self.set_truth_system(ClassicalTruthValueSystem())
        self.set_sign_system(ClassicalSignSystem())
        
        # Add tableau rules
        self._add_classical_rules()
    
    def _add_classical_rules(self):
        """Add all classical logic tableau rules."""
        
        # T-Conjunction rule (alpha)
        self.add_rule(TableauRule(
            name="T-Conjunction",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "A ' B")],
            conclusions=[["T:A", "T:B"]],
            priority=1
        ))
        
        # F-Conjunction rule (beta)
        self.add_rule(TableauRule(
            name="F-Conjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("F", "A ' B")],
            conclusions=[["F:A"], ["F:B"]],
            priority=2
        ))
        
        # T-Disjunction rule (beta)
        self.add_rule(TableauRule(
            name="T-Disjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("T", "A | B")],
            conclusions=[["T:A"], ["T:B"]],
            priority=2
        ))
        
        # F-Disjunction rule (alpha)
        self.add_rule(TableauRule(
            name="F-Disjunction",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "A | B")],
            conclusions=[["F:A", "F:B"]],
            priority=1
        ))
        
        # T-Negation rule (alpha)
        self.add_rule(TableauRule(
            name="T-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "~ A")],
            conclusions=[["F:A"]],
            priority=1
        ))
        
        # F-Negation rule (alpha)
        self.add_rule(TableauRule(
            name="F-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "~ A")],
            conclusions=[["T:A"]],
            priority=1
        ))
        
        # T-Implication rule (beta)
        self.add_rule(TableauRule(
            name="T-Implication",
            rule_type=RuleType.BETA,
            premises=[RulePattern("T", "A -> B")],
            conclusions=[["F:A"], ["T:B"]],
            priority=2
        ))
        
        # F-Implication rule (alpha)
        self.add_rule(TableauRule(
            name="F-Implication",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "A -> B")],
            conclusions=[["T:A", "F:B"]],
            priority=1
        ))
        
        # Alternative conjunction symbol rules
        self.add_rule(TableauRule(
            name="T-Conjunction-Alt",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "A & B")],
            conclusions=[["T:A", "T:B"]],
            priority=1
        ))
        
        self.add_rule(TableauRule(
            name="F-Conjunction-Alt",
            rule_type=RuleType.BETA,
            premises=[RulePattern("F", "A & B")],
            conclusions=[["F:A"], ["F:B"]],
            priority=2
        ))
        
        # Alternative disjunction symbol rules
        self.add_rule(TableauRule(
            name="T-Disjunction-Alt",
            rule_type=RuleType.BETA,
            premises=[RulePattern("T", "A | B")],
            conclusions=[["T:A"], ["T:B"]],
            priority=2
        ))
        
        self.add_rule(TableauRule(
            name="F-Disjunction-Alt",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "A | B")],
            conclusions=[["F:A", "F:B"]],
            priority=1
        ))
        
        # Alternative negation symbol rules
        self.add_rule(TableauRule(
            name="T-Negation-Alt",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "~ A")],
            conclusions=[["F:A"]],
            priority=1
        ))
        
        self.add_rule(TableauRule(
            name="F-Negation-Alt",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "~ A")],
            conclusions=[["T:A"]],
            priority=1
        ))
        
        # Alternative implication symbol rules
        self.add_rule(TableauRule(
            name="T-Implication-Alt",
            rule_type=RuleType.BETA,
            premises=[RulePattern("T", "A -> B")],
            conclusions=[["F:A"], ["T:B"]],
            priority=2
        ))
        
        self.add_rule(TableauRule(
            name="F-Implication-Alt",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "A -> B")],
            conclusions=[["T:A", "F:B"]],
            priority=1
        ))


# Convenience functions for classical logic
def Atom(name: str) -> PropositionalAtom:
    """Create a propositional atom."""
    return PropositionalAtom(name)


def Negation(formula) -> CompoundFormula:
    """Create a negation."""
    neg_spec = ConnectiveSpec("~", 1, 4, format_style="prefix")
    return CompoundFormula(neg_spec, formula)


def Conjunction(left, right) -> CompoundFormula:
    """Create a conjunction."""
    conj_spec = ConnectiveSpec("'", 2, 3)
    return CompoundFormula(conj_spec, left, right)


def Disjunction(left, right) -> CompoundFormula:
    """Create a disjunction."""
    disj_spec = ConnectiveSpec("|", 2, 2)
    return CompoundFormula(disj_spec, left, right)


def Implication(left, right) -> CompoundFormula:
    """Create an implication."""
    impl_spec = ConnectiveSpec("->", 2, 1, "right")
    return CompoundFormula(impl_spec, left, right)