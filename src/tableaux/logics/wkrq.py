#!/usr/bin/env python3
"""
wKrQ four-valued epistemic logic plugin.

This module implements the wKrQ four-valued epistemic logic system 
as a plugin for the modular tableau framework.
"""

from ..core.formula import (ConnectiveSpec, PropositionalAtom, CompoundFormula, 
                          PredicateFormula, Variable, Constant, Term,
                          RestrictedExistentialFormula, RestrictedUniversalFormula)
from ..core.semantics import FourValuedTruthSystem, TruthValue
from ..core.signs import SignSystem, Sign, SignedFormula
from ..core.rules import RuleType, TableauRule, RulePattern
from .logic_system import LogicSystem
from typing import Set, List
from dataclasses import dataclass


class WkrqTruthSystem(FourValuedTruthSystem):
    """wKrQ four-valued truth system with custom semantics."""
    
    def __init__(self):
        super().__init__()
        # Define wKrQ-specific truth values
        self.TRUE = TruthValue("t", "true")
        self.FALSE = TruthValue("f", "false") 
        self.NEITHER = TruthValue("n", "neither")
        self.BOTH = TruthValue("b", "both")
    
    def truth_values(self) -> Set[TruthValue]:
        return {self.TRUE, self.FALSE, self.NEITHER, self.BOTH}
    
    def designated_values(self) -> Set[TruthValue]:
        return {self.TRUE, self.BOTH}
    
    def get_operation(self, connective: str):
        operations = {
            "'": self._conjunction,
            "&": self._conjunction,
            "(": self._disjunction,
            "|": self._disjunction,
            "�": self._negation,
            "~": self._negation,
            "�": self._implication,
            "->": self._implication,
        }
        return operations.get(connective)
    
    def _conjunction(self, a: TruthValue, b: TruthValue) -> TruthValue:
        """wKrQ conjunction truth table."""
        if a == self.TRUE and b == self.TRUE:
            return self.TRUE
        elif (a == self.FALSE or b == self.FALSE):
            return self.FALSE
        elif (a == self.NEITHER or b == self.NEITHER):
            return self.NEITHER
        else:  # BOTH cases
            return self.BOTH
    
    def _disjunction(self, a: TruthValue, b: TruthValue) -> TruthValue:
        """wKrQ disjunction truth table."""
        if a == self.FALSE and b == self.FALSE:
            return self.FALSE
        elif (a == self.TRUE or b == self.TRUE):
            return self.TRUE
        elif (a == self.NEITHER or b == self.NEITHER):
            return self.NEITHER
        else:  # BOTH cases
            return self.BOTH
    
    def _negation(self, a: TruthValue) -> TruthValue:
        """wKrQ negation truth table."""
        if a == self.TRUE:
            return self.FALSE
        elif a == self.FALSE:
            return self.TRUE
        elif a == self.NEITHER:
            return self.NEITHER
        else:  # BOTH
            return self.BOTH
    
    def _implication(self, a: TruthValue, b: TruthValue) -> TruthValue:
        """wKrQ implication truth table."""
        if a == self.TRUE and b == self.FALSE:
            return self.FALSE
        elif a == self.FALSE:
            return self.TRUE
        elif b == self.TRUE:
            return self.TRUE
        elif (a == self.NEITHER or b == self.NEITHER):
            return self.NEITHER
        else:  # BOTH cases
            return self.BOTH


class WkrqSign(Sign):
    """Signs for wKrQ logic (T/F/M/N)."""
    
    def __init__(self, value: str):
        if value not in ["T", "F", "M", "N"]:
            raise ValueError(f"Invalid wKrQ sign: {value}")
        self.value = value
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        return isinstance(other, WkrqSign) and self.value == other.value
    
    def __hash__(self) -> int:
        return hash(("wkrq", self.value))
    
    def is_contradictory_with(self, other: Sign) -> bool:
        if not isinstance(other, WkrqSign):
            return False
        # In wKrQ, only T and F contradict
        return (self.value == "T" and other.value == "F") or \
               (self.value == "F" and other.value == "T")
    
    def get_symbol(self) -> str:
        return self.value


class WkrqSignSystem(SignSystem):
    """Sign system for wKrQ logic."""
    
    def __init__(self):
        self.T = WkrqSign("T")
        self.F = WkrqSign("F")
        self.M = WkrqSign("M") 
        self.N = WkrqSign("N")
    
    def signs(self) -> Set[Sign]:
        return {self.T, self.F, self.M, self.N}
    
    def truth_conditions(self, sign: Sign) -> Set[TruthValue]:
        from ..core.signs import FourValuedSign
        truth_system = WkrqTruthSystem()
        
        # Handle both WkrqSign and FourValuedSign types
        if isinstance(sign, WkrqSign):
            sign_value = sign.value
        elif isinstance(sign, FourValuedSign):
            sign_value = sign.value
        else:
            raise ValueError(f"Unknown sign type: {type(sign)}")
        
        if sign_value == "T":
            return {truth_system.TRUE}
        elif sign_value == "F":
            return {truth_system.FALSE}
        elif sign_value == "M":
            return {truth_system.BOTH}
        elif sign_value == "N":
            return {truth_system.NEITHER}
        else:
            raise ValueError(f"Unknown sign: {sign}")
    
    def sign_for_truth_value(self, value: TruthValue) -> Sign:
        truth_system = WkrqTruthSystem()
        if value == truth_system.TRUE:
            return self.T
        elif value == truth_system.FALSE:
            return self.F
        elif value == truth_system.BOTH:
            return self.M
        elif value == truth_system.NEITHER:
            return self.N
        else:
            raise ValueError(f"No wKrQ sign for truth value: {value}")


class WkrqLogic(LogicSystem):
    """wKrQ four-valued epistemic logic system."""
    
    def initialize(self):
        """Initialize wKrQ logic with connectives, semantics, and rules."""
        # Add connectives (same as other systems)
        self.add_connective(ConnectiveSpec("'", 2, 3, "left", "infix"))  # conjunction
        self.add_connective(ConnectiveSpec("&", 2, 3, "left", "infix"))  # conjunction (alt)
        self.add_connective(ConnectiveSpec("|", 2, 2, "left", "infix"))  # disjunction
        self.add_connective(ConnectiveSpec("~", 1, 4, "none", "prefix"))  # negation
        self.add_connective(ConnectiveSpec("->", 2, 1, "right", "infix"))  # implication
        
        # Set semantic systems
        self.set_truth_system(WkrqTruthSystem())
        self.set_sign_system(WkrqSignSystem())
        
        # Add tableau rules
        self._add_wkrq_rules()
    
    def _add_wkrq_rules(self):
        """Add all wKrQ logic tableau rules."""
        
        # T-Conjunction rules
        self.add_rule(TableauRule(
            name="T-Conjunction",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "A ' B")],
            conclusions=[["T:A", "T:B"]],
            priority=1
        ))
        
        # F-Conjunction rules
        self.add_rule(TableauRule(
            name="F-Conjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("F", "A ' B")],
            conclusions=[["F:A"], ["F:B"]],
            priority=2
        ))
        
        # M-Conjunction rules  
        self.add_rule(TableauRule(
            name="M-Conjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("M", "A ' B")],
            conclusions=[["M:A"], ["M:B"]],
            priority=2
        ))
        
        # N-Conjunction rules
        self.add_rule(TableauRule(
            name="N-Conjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("N", "A ' B")],
            conclusions=[["N:A"], ["N:B"]],
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
        
        # M-Disjunction rules
        self.add_rule(TableauRule(
            name="M-Disjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("M", "A ( B")],
            conclusions=[["M:A"], ["M:B"]],
            priority=2
        ))
        
        # N-Disjunction rules
        self.add_rule(TableauRule(
            name="N-Disjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("N", "A ( B")],
            conclusions=[["N:A"], ["N:B"]],
            priority=2
        ))
        
        # Negation rules (all signs map to themselves in wKrQ negation)
        self.add_rule(TableauRule(
            name="T-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "~ A")],
            conclusions=[["F:A"]],
            priority=1
        ))
        
        self.add_rule(TableauRule(
            name="F-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "~ A")],
            conclusions=[["T:A"]],
            priority=1
        ))
        
        self.add_rule(TableauRule(
            name="M-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("M", "~ A")],
            conclusions=[["M:A"]],
            priority=1
        ))
        
        self.add_rule(TableauRule(
            name="N-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("N", "~ A")],
            conclusions=[["N:A"]],
            priority=1
        ))
        
        # Implication rules
        self.add_rule(TableauRule(
            name="T-Implication",
            rule_type=RuleType.BETA,
            premises=[RulePattern("T", "A -> B")],
            conclusions=[["F:A"], ["T:B"]],
            priority=2
        ))
        
        self.add_rule(TableauRule(
            name="F-Implication",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "A -> B")],
            conclusions=[["T:A", "F:B"]],
            priority=1
        ))
        
        self.add_rule(TableauRule(
            name="M-Implication",
            rule_type=RuleType.BETA,
            premises=[RulePattern("M", "A -> B")],
            conclusions=[["M:A"], ["M:B"]],
            priority=2
        ))
        
        self.add_rule(TableauRule(
            name="N-Implication",
            rule_type=RuleType.BETA,
            premises=[RulePattern("N", "A -> B")],
            conclusions=[["N:A"], ["N:B"]],
            priority=2
        ))
        
        # Alternative symbol rules (similar pattern for &, |, ~, ->)
        # [Additional rules for alternative symbols would follow the same pattern]
        
        # First-order tableau rules for restricted quantifiers
        self._add_first_order_rules()
    
    def _add_first_order_rules(self):
        """Add first-order tableau rules for restricted quantifiers."""
        
        # T-Restricted-Existential: T:[∃X P(X)]Q(X) → T:P(c) ∧ T:Q(c) for fresh constant c
        self.add_rule(TableauRule(
            name="T-Restricted-Existential",
            rule_type=RuleType.ALPHA,  # Non-branching: introduces new instance
            premises=[RulePattern("T", "[∃X P(X)]Q(X)")],
            conclusions=[["T:P(c)", "T:Q(c)"]],  # Fresh constant c
            priority=1
        ))
        
        # F-Restricted-Existential: F:[∃X P(X)]Q(X) → F:P(c) ∨ F:Q(c) for all constants c
        self.add_rule(TableauRule(
            name="F-Restricted-Existential", 
            rule_type=RuleType.BETA,  # Branching: must fail for all or succeed for some
            premises=[RulePattern("F", "[∃X P(X)]Q(X)")],
            conclusions=[["F:P(c)"], ["F:Q(c)"]],  # All constants c in domain
            priority=2
        ))
        
        # M-Restricted-Existential: M:[∃X P(X)]Q(X) → M:P(c) ∧ M:Q(c) (epistemic uncertainty)
        self.add_rule(TableauRule(
            name="M-Restricted-Existential",
            rule_type=RuleType.ALPHA,  # Non-branching: may exist with uncertainty
            premises=[RulePattern("M", "[∃X P(X)]Q(X)")],
            conclusions=[["M:P(c)", "M:Q(c)"]],  # Fresh constant c
            priority=1
        ))
        
        # N-Restricted-Existential: N:[∃X P(X)]Q(X) → N:P(c) ∨ N:Q(c) (need not exist)
        self.add_rule(TableauRule(
            name="N-Restricted-Existential",
            rule_type=RuleType.BETA,  # Branching: need not be true
            premises=[RulePattern("N", "[∃X P(X)]Q(X)")],
            conclusions=[["N:P(c)"], ["N:Q(c)"]],
            priority=2
        ))
        
        # T-Restricted-Universal: T:[∀X P(X)]Q(X) → T:P(c) → T:Q(c) for all constants c
        self.add_rule(TableauRule(
            name="T-Restricted-Universal",
            rule_type=RuleType.ALPHA,  # Non-branching: must hold for all in domain
            premises=[RulePattern("T", "[∀X P(X)]Q(X)")],
            conclusions=[["F:P(c)", "T:Q(c)"]],  # P(c) → Q(c) for all c
            priority=1
        ))
        
        # F-Restricted-Universal: F:[∀X P(X)]Q(X) → T:P(c) ∧ F:Q(c) for fresh constant c
        self.add_rule(TableauRule(
            name="F-Restricted-Universal",
            rule_type=RuleType.ALPHA,  # Non-branching: counterexample exists
            premises=[RulePattern("F", "[∀X P(X)]Q(X)")],
            conclusions=[["T:P(c)", "F:Q(c)"]],  # Fresh constant c as counterexample
            priority=1
        ))
        
        # M-Restricted-Universal: M:[∀X P(X)]Q(X) → M:P(c) → M:Q(c) (epistemic uncertainty)
        self.add_rule(TableauRule(
            name="M-Restricted-Universal",
            rule_type=RuleType.ALPHA,  # Non-branching: uncertain for all
            premises=[RulePattern("M", "[∀X P(X)]Q(X)")],
            conclusions=[["N:P(c)", "M:Q(c)"]],  # May not satisfy restriction, may satisfy matrix
            priority=1
        ))
        
        # N-Restricted-Universal: N:[∀X P(X)]Q(X) → N:P(c) → N:Q(c) (need not be universal)
        self.add_rule(TableauRule(
            name="N-Restricted-Universal", 
            rule_type=RuleType.ALPHA,  # Non-branching: need not hold universally
            premises=[RulePattern("N", "[∀X P(X)]Q(X)")],
            conclusions=[["T:P(c)", "N:Q(c)"]],  # Fresh constant c where restriction holds but matrix need not
            priority=1
        ))


# Convenience functions for wKrQ logic
def Atom(name: str) -> PropositionalAtom:
    """Create a propositional atom."""
    return PropositionalAtom(name)


def Var(name: str) -> Variable:
    """Create a first-order variable."""
    from ..core.formula import Variable as VariableClass
    return VariableClass(name)


def Predicate(name: str, terms: List[Term]) -> PredicateFormula:
    """Create a predicate formula."""
    return PredicateFormula(name, terms)


def RestrictedExists(variable: Variable, restriction: PredicateFormula, matrix: PredicateFormula) -> RestrictedExistentialFormula:
    """Create a restricted existential quantifier: [∃X P(X)]Q(X)"""
    return RestrictedExistentialFormula(variable, restriction, matrix)


def RestrictedForall(variable: Variable, restriction: PredicateFormula, matrix: PredicateFormula) -> RestrictedUniversalFormula:
    """Create a restricted universal quantifier: [∀X P(X)]Q(X)"""
    return RestrictedUniversalFormula(variable, restriction, matrix)


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


# Convenience functions for wKrQ signed formulas
def TF(formula) -> SignedFormula:
    """Create a wKrQ true signed formula."""
    return SignedFormula(WkrqSign("T"), formula)


def FF(formula) -> SignedFormula:
    """Create a wKrQ false signed formula."""
    return SignedFormula(WkrqSign("F"), formula)


def M(formula) -> SignedFormula:
    """Create a wKrQ both signed formula."""
    return SignedFormula(WkrqSign("M"), formula)


def N(formula) -> SignedFormula:
    """Create a wKrQ neither signed formula."""
    return SignedFormula(WkrqSign("N"), formula)