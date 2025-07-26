#!/usr/bin/env python3
"""
Weak Kleene three-valued logic plugin.

This module implements weak Kleene three-valued logic as a plugin for the
modular tableau framework.
"""

from ..core.formula import ConnectiveSpec, PropositionalAtom, CompoundFormula
from ..core.semantics import WeakKleeneTruthValueSystem
from ..core.signs import ThreeValuedSignSystem
from ..core.rules import RuleType, TableauRule, RulePattern
from .logic_system import LogicSystem


class WeakKleeneLogic(LogicSystem):
    """Weak Kleene three-valued logic system."""
    
    def initialize(self):
        """Initialize weak Kleene logic with connectives, semantics, and rules."""
        # Add connectives (same as classical)
        self.add_connective(ConnectiveSpec("'", 2, 3, "left", "infix"))  # conjunction
        self.add_connective(ConnectiveSpec("&", 2, 3, "left", "infix"))  # conjunction (alt)
        self.add_connective(ConnectiveSpec("|", 2, 2, "left", "infix"))  # disjunction
        self.add_connective(ConnectiveSpec("~", 1, 4, "none", "prefix"))  # negation
        self.add_connective(ConnectiveSpec("->", 2, 1, "right", "infix"))  # implication
        
        # Set semantic systems  
        self.set_truth_system(WeakKleeneTruthValueSystem())
        self.set_sign_system(ThreeValuedSignSystem())
        
        # Add tableau rules
        self._add_weak_kleene_rules()
    
    def _add_weak_kleene_rules(self):
        """Add all weak Kleene logic tableau rules."""
        
        # T-Conjunction rules
        self.add_rule(TableauRule(
            name="T-Conjunction",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "A ' B")],
            conclusions=[["T:A", "T:B"]],
            priority=1
        ))
        
        # F-Conjunction rules (more complex in three-valued logic)
        self.add_rule(TableauRule(
            name="F-Conjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("F", "A ' B")],
            conclusions=[["F:A"], ["F:B"], ["U:A"], ["U:B"]],
            priority=2
        ))
        
        # U-Conjunction rules
        self.add_rule(TableauRule(
            name="U-Conjunction-1",
            rule_type=RuleType.BETA,
            premises=[RulePattern("U", "A ' B")],
            conclusions=[["U:A"], ["U:B"]],
            priority=2
        ))
        
        # T-Disjunction rules
        self.add_rule(TableauRule(
            name="T-Disjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("T", "A ( B")],
            conclusions=[["T:A"], ["T:B"]],
            priority=2
        ))
        
        # F-Disjunction rules
        self.add_rule(TableauRule(
            name="F-Disjunction",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "A ( B")],
            conclusions=[["F:A", "F:B"]],
            priority=1
        ))
        
        # U-Disjunction rules
        self.add_rule(TableauRule(
            name="U-Disjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("U", "A ( B")],
            conclusions=[["U:A"], ["U:B"]],
            priority=2
        ))
        
        # T-Negation rules
        self.add_rule(TableauRule(
            name="T-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "~ A")],
            conclusions=[["F:A"]],
            priority=1
        ))
        
        # F-Negation rules
        self.add_rule(TableauRule(
            name="F-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "~ A")],
            conclusions=[["T:A"]],
            priority=1
        ))
        
        # U-Negation rules
        self.add_rule(TableauRule(
            name="U-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("U", "~ A")],
            conclusions=[["U:A"]],
            priority=1
        ))
        
        # T-Implication rules
        self.add_rule(TableauRule(
            name="T-Implication",
            rule_type=RuleType.BETA,
            premises=[RulePattern("T", "A -> B")],
            conclusions=[["F:A"], ["T:B"]],
            priority=2
        ))
        
        # F-Implication rules
        self.add_rule(TableauRule(
            name="F-Implication",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "A -> B")],
            conclusions=[["T:A", "F:B"]],
            priority=1
        ))
        
        # U-Implication rules
        self.add_rule(TableauRule(
            name="U-Implication",
            rule_type=RuleType.BETA,
            premises=[RulePattern("U", "A -> B")],
            conclusions=[["U:A"], ["U:B"]],
            priority=2
        ))
        
        # Alternative symbols (conjunction)
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
            conclusions=[["F:A"], ["F:B"], ["U:A"], ["U:B"]],
            priority=2
        ))
        
        self.add_rule(TableauRule(
            name="U-Conjunction-Alt",
            rule_type=RuleType.BETA,
            premises=[RulePattern("U", "A & B")],
            conclusions=[["U:A"], ["U:B"]],
            priority=2
        ))
        
        # Alternative symbols (disjunction)
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
        
        self.add_rule(TableauRule(
            name="U-Disjunction-Alt",
            rule_type=RuleType.BETA,
            premises=[RulePattern("U", "A | B")],
            conclusions=[["U:A"], ["U:B"]],
            priority=2
        ))
        
        # Alternative symbols (negation)
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
        
        self.add_rule(TableauRule(
            name="U-Negation-Alt",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("U", "~ A")],
            conclusions=[["U:A"]],
            priority=1
        ))
        
        # Alternative symbols (implication)
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
        
        self.add_rule(TableauRule(
            name="U-Implication-Alt",
            rule_type=RuleType.BETA,
            premises=[RulePattern("U", "A -> B")],
            conclusions=[["U:A"], ["U:B"]],
            priority=2
        ))


# Convenience functions for weak Kleene logic
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