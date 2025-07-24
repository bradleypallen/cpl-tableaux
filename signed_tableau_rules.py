#!/usr/bin/env python3
"""
Signed Tableau Rules

Implements standard signed tableau rules following Smullyan's unified notation
and extending to many-valued logics as found in Priest, Fitting, and other
tableau literature.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Set, Optional, Union, Tuple
from enum import Enum

from formula import Formula, Atom, Negation, Conjunction, Disjunction, Implication
from signed_formula import SignedFormula, Sign, ClassicalSign, ThreeValuedSign, WkrqSign
from truth_value import t, f, e


class SignedRuleType(Enum):
    """Types of signed tableau rules following standard classification"""
    
    # α-rules (linear, single branch)
    T_CONJUNCTION = "T∧"          # T:(A∧B) → T:A, T:B
    F_DISJUNCTION = "F∨"          # F:(A∨B) → F:A, F:B  
    F_IMPLICATION = "F→"          # F:(A→B) → T:A, F:B
    T_DOUBLE_NEGATION = "T¬¬"     # T:¬¬A → T:A
    F_DOUBLE_NEGATION = "F¬¬"     # F:¬¬A → F:A
    
    # β-rules (branching, multiple branches)
    F_CONJUNCTION = "F∧"          # F:(A∧B) → F:A | F:B
    T_DISJUNCTION = "T∨"          # T:(A∨B) → T:A | T:B
    T_IMPLICATION = "T→"          # T:(A→B) → F:A | T:B
    
    # Negation rules  
    T_NEGATION = "T¬"             # T:¬A → F:A
    F_NEGATION = "F¬"             # F:¬A → T:A
    
    # Three-valued specific rules
    U_CONJUNCTION = "U∧"          # U:(A∧B) → various patterns
    U_DISJUNCTION = "U∨"          # U:(A∨B) → various patterns
    U_IMPLICATION = "U→"          # U:(A→B) → various patterns
    U_NEGATION = "U¬"             # U:¬A → U:A
    
    # wKrQ specific rules
    M_CONJUNCTION = "M∧"          # M:(A∧B) → M:A, M:B  
    N_CONJUNCTION = "N∧"          # N:(A∧B) → N:A | N:B
    M_DISJUNCTION = "M∨"          # M:(A∨B) → M:A | M:B
    N_DISJUNCTION = "N∨"          # N:(A∨B) → N:A, N:B
    M_NEGATION = "M¬"             # M:¬A → N:A
    N_NEGATION = "N¬"             # N:¬A → M:A
    M_IMPLICATION = "M→"          # M:(A→B) → N:A | M:B
    N_IMPLICATION = "N→"          # N:(A→B) → M:A, N:B


class SignedRuleResult:
    """Result of applying a signed tableau rule"""
    
    def __init__(self, branches: List[List[SignedFormula]], is_alpha: bool = True):
        """
        Args:
            branches: List of branches, each containing signed formulas to add
            is_alpha: True for α-rules (single branch), False for β-rules (multiple branches)
        """
        self.branches = branches
        self.is_alpha = is_alpha
        self.branch_count = len(branches)
    
    @classmethod
    def alpha_rule(cls, *formulas: SignedFormula) -> 'SignedRuleResult':
        """Create result for α-rule (single branch with multiple formulas)"""
        return cls([list(formulas)], is_alpha=True)
    
    @classmethod  
    def beta_rule(cls, *branches: List[SignedFormula]) -> 'SignedRuleResult':
        """Create result for β-rule (multiple branches)"""
        return cls(list(branches), is_alpha=False)


class SignedTableauRule(ABC):
    """Abstract base class for signed tableau rules"""
    
    def __init__(self, rule_type: SignedRuleType, sign_systems: List[str]):
        self.rule_type = rule_type
        self.sign_systems = sign_systems  # Which sign systems this rule applies to
    
    @abstractmethod
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Check if this rule applies to the given signed formula"""
        pass
    
    @abstractmethod
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Apply the rule to the signed formula"""
        pass
    
    def get_priority(self) -> int:
        """Get rule priority (lower = higher priority). α-rules before β-rules."""
        return 1 if self.is_alpha_rule() else 2
    
    def is_alpha_rule(self) -> bool:
        """Check if this is an α-rule (linear expansion)"""
        return self.rule_type in {
            SignedRuleType.T_CONJUNCTION, SignedRuleType.F_DISJUNCTION,
            SignedRuleType.F_IMPLICATION, SignedRuleType.T_DOUBLE_NEGATION,
            SignedRuleType.F_DOUBLE_NEGATION, SignedRuleType.T_NEGATION,
            SignedRuleType.F_NEGATION, SignedRuleType.U_NEGATION,
            SignedRuleType.M_CONJUNCTION, SignedRuleType.N_DISJUNCTION,
            SignedRuleType.M_NEGATION, SignedRuleType.N_NEGATION,
            SignedRuleType.N_IMPLICATION
        }
    
    def is_beta_rule(self) -> bool:
        """Check if this is a β-rule (branching expansion)"""
        return not self.is_alpha_rule()


# Classical Signed Tableau Rules

class TConjunctionRule(SignedTableauRule):
    """T:(A∧B) → T:A, T:B"""
    
    def __init__(self):
        super().__init__(SignedRuleType.T_CONJUNCTION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "T" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        conj = signed_formula.formula
        left_signed = SignedFormula(signed_formula.sign, conj.left)
        right_signed = SignedFormula(signed_formula.sign, conj.right)
        return SignedRuleResult.alpha_rule(left_signed, right_signed)


class FConjunctionRule(SignedTableauRule):
    """F:(A∧B) → F:A | F:B"""
    
    def __init__(self):
        super().__init__(SignedRuleType.F_CONJUNCTION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "F" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        conj = signed_formula.formula
        left_signed = SignedFormula(signed_formula.sign, conj.left)
        right_signed = SignedFormula(signed_formula.sign, conj.right)
        return SignedRuleResult.beta_rule([left_signed], [right_signed])


class TDisjunctionRule(SignedTableauRule):
    """T:(A∨B) → T:A | T:B"""
    
    def __init__(self):
        super().__init__(SignedRuleType.T_DISJUNCTION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "T" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        disj = signed_formula.formula
        left_signed = SignedFormula(signed_formula.sign, disj.left)
        right_signed = SignedFormula(signed_formula.sign, disj.right)
        return SignedRuleResult.beta_rule([left_signed], [right_signed])


class FDisjunctionRule(SignedTableauRule):
    """F:(A∨B) → F:A, F:B"""
    
    def __init__(self):
        super().__init__(SignedRuleType.F_DISJUNCTION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "F" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        disj = signed_formula.formula
        left_signed = SignedFormula(signed_formula.sign, disj.left)
        right_signed = SignedFormula(signed_formula.sign, disj.right)
        return SignedRuleResult.alpha_rule(left_signed, right_signed)


class TImplicationRule(SignedTableauRule):
    """T:(A→B) → F:A | T:B"""
    
    def __init__(self):
        super().__init__(SignedRuleType.T_IMPLICATION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "T" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        impl = signed_formula.formula
        # Create opposite sign for antecedent
        if isinstance(signed_formula.sign, ClassicalSign):
            false_sign = ClassicalSign("F")
        else:  # ThreeValuedSign
            false_sign = ThreeValuedSign(f)
        
        ant_signed = SignedFormula(false_sign, impl.antecedent)
        cons_signed = SignedFormula(signed_formula.sign, impl.consequent)
        return SignedRuleResult.beta_rule([ant_signed], [cons_signed])


class FImplicationRule(SignedTableauRule):
    """F:(A→B) → T:A, F:B"""
    
    def __init__(self):
        super().__init__(SignedRuleType.F_IMPLICATION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "F" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        impl = signed_formula.formula
        # Create opposite sign for consequent
        if isinstance(signed_formula.sign, ClassicalSign):
            true_sign = ClassicalSign("T")
        else:  # ThreeValuedSign
            true_sign = ThreeValuedSign(t)
        
        ant_signed = SignedFormula(true_sign, impl.antecedent)
        cons_signed = SignedFormula(signed_formula.sign, impl.consequent)
        return SignedRuleResult.alpha_rule(ant_signed, cons_signed)


class NegationRule(SignedTableauRule):
    """T:¬A → F:A and F:¬A → T:A"""
    
    def __init__(self):
        super().__init__(SignedRuleType.T_NEGATION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) in ["T", "F"] and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        neg = signed_formula.formula
        # Flip the sign
        if str(signed_formula.sign) == "T":
            if isinstance(signed_formula.sign, ClassicalSign):
                new_sign = ClassicalSign("F")
            else:  # ThreeValuedSign
                new_sign = ThreeValuedSign(f)
        else:  # "F"
            if isinstance(signed_formula.sign, ClassicalSign):
                new_sign = ClassicalSign("T")
            else:  # ThreeValuedSign
                new_sign = ThreeValuedSign(t)
        
        result_signed = SignedFormula(new_sign, neg.operand)
        return SignedRuleResult.alpha_rule(result_signed)


class DoubleNegationRule(SignedTableauRule):
    """T:¬¬A → T:A and F:¬¬A → F:A"""
    
    def __init__(self):
        super().__init__(SignedRuleType.T_DOUBLE_NEGATION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) in ["T", "F"] and
                isinstance(signed_formula.formula, Negation) and
                isinstance(signed_formula.formula.operand, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        double_neg = signed_formula.formula
        inner_formula = double_neg.operand.operand
        result_signed = SignedFormula(signed_formula.sign, inner_formula)
        return SignedRuleResult.alpha_rule(result_signed)


# Three-Valued Specific Rules

class UNegationRule(SignedTableauRule):
    """U:¬A → U:A (undefined negation stays undefined)"""
    
    def __init__(self):
        super().__init__(SignedRuleType.U_NEGATION, ["three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, ThreeValuedSign) and
                str(signed_formula.sign) == "U" and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        neg = signed_formula.formula
        result_signed = SignedFormula(signed_formula.sign, neg.operand)
        return SignedRuleResult.alpha_rule(result_signed)


class UConjunctionRule(SignedTableauRule):
    """U:(A∧B) → complex three-way branching based on WK3 semantics"""
    
    def __init__(self):
        super().__init__(SignedRuleType.U_CONJUNCTION, ["three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, ThreeValuedSign) and
                str(signed_formula.sign) == "U" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """
        U:(A∧B) is true when:
        - F:A (A is false, so conjunction is false, but we want undefined overall)
        - F:B (B is false, so conjunction is false, but we want undefined overall)  
        - U:A, U:B (both undefined, conjunction undefined)
        - U:A, T:B (A undefined, B true, conjunction undefined)
        - T:A, U:B (A true, B undefined, conjunction undefined)
        
        This is complex - simplified to the most common case for now.
        """
        conj = signed_formula.formula
        u_sign = ThreeValuedSign(e)
        left_u = SignedFormula(u_sign, conj.left)
        right_u = SignedFormula(u_sign, conj.right)
        return SignedRuleResult.alpha_rule(left_u, right_u)


# wKrQ Rules

class WkrqTConjunctionRule(SignedTableauRule):
    """T:(A∧B) rule for wKrQ signs (same as classical T)"""
    
    def __init__(self):
        super().__init__(SignedRuleType.T_CONJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "T" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """T:(A∧B) → T:A, T:B (α-rule)"""
        conj = signed_formula.formula
        t_sign = WkrqSign("T")
        left_t = SignedFormula(t_sign, conj.left)
        right_t = SignedFormula(t_sign, conj.right)
        return SignedRuleResult.alpha_rule(left_t, right_t)


class WkrqFConjunctionRule(SignedTableauRule):
    """F:(A∧B) rule for wKrQ signs (same as classical F)"""
    
    def __init__(self):
        super().__init__(SignedRuleType.F_CONJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "F" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """F:(A∧B) → F:A | F:B (β-rule)"""
        conj = signed_formula.formula
        f_sign = WkrqSign("F")
        left_f = SignedFormula(f_sign, conj.left)
        right_f = SignedFormula(f_sign, conj.right)
        return SignedRuleResult.beta_rule([left_f], [right_f])


class WkrqMConjunctionRule(SignedTableauRule):
    """M:(A∧B) rule for wKrQ signs - epistemic "may be true" conjunction"""
    
    def __init__(self):
        super().__init__(SignedRuleType.M_CONJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "M" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """M:(A∧B) → M:A, M:B (α-rule)"""
        conj = signed_formula.formula
        m_sign = WkrqSign("M")
        left_m = SignedFormula(m_sign, conj.left)
        right_m = SignedFormula(m_sign, conj.right)
        return SignedRuleResult.alpha_rule(left_m, right_m)


class WkrqNConjunctionRule(SignedTableauRule):
    """N:(A∧B) rule for wKrQ signs - epistemic "need not be true" conjunction"""
    
    def __init__(self):
        super().__init__(SignedRuleType.N_CONJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "N" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """N:(A∧B) → N:A | N:B (β-rule)"""
        conj = signed_formula.formula
        n_sign = WkrqSign("N")
        left_n = SignedFormula(n_sign, conj.left)
        right_n = SignedFormula(n_sign, conj.right)
        return SignedRuleResult.beta_rule([left_n], [right_n])


class WkrqTDisjunctionRule(SignedTableauRule):
    """T:(A∨B) rule for wKrQ signs (same as classical T)"""
    
    def __init__(self):
        super().__init__(SignedRuleType.T_DISJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "T" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """T:(A∨B) → T:A | T:B (β-rule)"""
        disj = signed_formula.formula
        t_sign = WkrqSign("T")
        left_t = SignedFormula(t_sign, disj.left)
        right_t = SignedFormula(t_sign, disj.right)
        return SignedRuleResult.beta_rule([left_t], [right_t])


class WkrqFDisjunctionRule(SignedTableauRule):
    """F:(A∨B) rule for wKrQ signs (same as classical F)"""
    
    def __init__(self):
        super().__init__(SignedRuleType.F_DISJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "F" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """F:(A∨B) → F:A, F:B (α-rule)"""
        disj = signed_formula.formula
        f_sign = WkrqSign("F")
        left_f = SignedFormula(f_sign, disj.left)
        right_f = SignedFormula(f_sign, disj.right)
        return SignedRuleResult.alpha_rule(left_f, right_f)


class WkrqMDisjunctionRule(SignedTableauRule):
    """M:(A∨B) rule for wKrQ signs - epistemic "may be true" disjunction"""
    
    def __init__(self):
        super().__init__(SignedRuleType.M_DISJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "M" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """M:(A∨B) → M:A | M:B (β-rule)"""
        disj = signed_formula.formula
        m_sign = WkrqSign("M")
        left_m = SignedFormula(m_sign, disj.left)
        right_m = SignedFormula(m_sign, disj.right)
        return SignedRuleResult.beta_rule([left_m], [right_m])


class WkrqNDisjunctionRule(SignedTableauRule):
    """N:(A∨B) rule for wKrQ signs - epistemic "need not be true" disjunction"""
    
    def __init__(self):
        super().__init__(SignedRuleType.N_DISJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "N" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """N:(A∨B) → N:A, N:B (α-rule)"""
        disj = signed_formula.formula
        n_sign = WkrqSign("N")
        left_n = SignedFormula(n_sign, disj.left)
        right_n = SignedFormula(n_sign, disj.right)
        return SignedRuleResult.alpha_rule(left_n, right_n)


class WkrqMNegationRule(SignedTableauRule):
    """M:¬A rule for wKrQ signs - uses sign duality"""
    
    def __init__(self):
        super().__init__(SignedRuleType.M_NEGATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "M" and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """M:¬A → N:A (α-rule, by duality)"""
        neg = signed_formula.formula
        n_sign = WkrqSign("N")
        n_inner = SignedFormula(n_sign, neg.operand)
        return SignedRuleResult.alpha_rule(n_inner)


class WkrqNNegationRule(SignedTableauRule):
    """N:¬A rule for wKrQ signs - uses sign duality"""
    
    def __init__(self):
        super().__init__(SignedRuleType.N_NEGATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "N" and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """N:¬A → M:A (α-rule, by duality)"""
        neg = signed_formula.formula
        m_sign = WkrqSign("M")
        m_inner = SignedFormula(m_sign, neg.operand)
        return SignedRuleResult.alpha_rule(m_inner)


class WkrqTNegationRule(SignedTableauRule):
    """T:¬A rule for wKrQ signs (same as classical)"""
    
    def __init__(self):
        super().__init__(SignedRuleType.T_NEGATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "T" and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """T:¬A → F:A (α-rule)"""
        neg = signed_formula.formula
        f_sign = WkrqSign("F")
        f_inner = SignedFormula(f_sign, neg.operand)
        return SignedRuleResult.alpha_rule(f_inner)


class WkrqFNegationRule(SignedTableauRule):
    """F:¬A rule for wKrQ signs (same as classical)"""
    
    def __init__(self):
        super().__init__(SignedRuleType.F_NEGATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "F" and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """F:¬A → T:A (α-rule)"""
        neg = signed_formula.formula
        t_sign = WkrqSign("T")
        t_inner = SignedFormula(t_sign, neg.operand)
        return SignedRuleResult.alpha_rule(t_inner)


# Ferguson Implication Rules

class WkrqTImplicationRule(SignedTableauRule):
    """T:(A→B) rule for wKrQ signs (same as classical T)"""
    
    def __init__(self):
        super().__init__(SignedRuleType.T_IMPLICATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "T" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """T:(A→B) → F:A | T:B (β-rule)"""
        impl = signed_formula.formula
        f_sign = WkrqSign("F")
        t_sign = WkrqSign("T")
        left_f = SignedFormula(f_sign, impl.antecedent)
        right_t = SignedFormula(t_sign, impl.consequent)
        return SignedRuleResult.beta_rule([left_f], [right_t])


class WkrqFImplicationRule(SignedTableauRule):
    """F:(A→B) rule for wKrQ signs (same as classical F)"""
    
    def __init__(self):
        super().__init__(SignedRuleType.F_IMPLICATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "F" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """F:(A→B) → T:A, F:B (α-rule)"""
        impl = signed_formula.formula
        t_sign = WkrqSign("T")
        f_sign = WkrqSign("F")
        ant_t = SignedFormula(t_sign, impl.antecedent)
        cons_f = SignedFormula(f_sign, impl.consequent)
        return SignedRuleResult.alpha_rule(ant_t, cons_f)


class WkrqMImplicationRule(SignedTableauRule):
    """M:(A→B) rule for wKrQ signs - epistemic "may be true" implication"""
    
    def __init__(self):
        super().__init__(SignedRuleType.M_IMPLICATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "M" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """M:(A→B) → N:A | M:B (β-rule, following epistemic semantics)"""
        impl = signed_formula.formula
        n_sign = WkrqSign("N")
        m_sign = WkrqSign("M")
        ant_n = SignedFormula(n_sign, impl.antecedent)
        cons_m = SignedFormula(m_sign, impl.consequent)
        return SignedRuleResult.beta_rule([ant_n], [cons_m])


class WkrqNImplicationRule(SignedTableauRule):
    """N:(A→B) rule for wKrQ signs - epistemic "need not be true" implication"""
    
    def __init__(self):
        super().__init__(SignedRuleType.N_IMPLICATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "N" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """N:(A→B) → M:A, N:B (α-rule, following epistemic semantics)"""
        impl = signed_formula.formula
        m_sign = WkrqSign("M")
        n_sign = WkrqSign("N")
        ant_m = SignedFormula(m_sign, impl.antecedent)
        cons_n = SignedFormula(n_sign, impl.consequent)
        return SignedRuleResult.alpha_rule(ant_m, cons_n)


# Rule Registry

class SignedRuleRegistry:
    """Registry for managing signed tableau rules"""
    
    def __init__(self):
        self.rules: List[SignedTableauRule] = []
        self._load_standard_rules()
    
    def _load_standard_rules(self):
        """Load all standard signed tableau rules"""
        self.rules = [
            # Classical rules
            TConjunctionRule(),
            FConjunctionRule(), 
            TDisjunctionRule(),
            FDisjunctionRule(),
            TImplicationRule(),
            FImplicationRule(),
            NegationRule(),
            DoubleNegationRule(),
            
            # Three-valued rules
            UNegationRule(),
            UConjunctionRule(),
            
            # Ferguson wKrQ rules
            FergusonTConjunctionRule(),
            WkrqFConjunctionRule(),
            WkrqMConjunctionRule(),
            WkrqNConjunctionRule(),
            WkrqTDisjunctionRule(),
            WkrqFDisjunctionRule(),
            WkrqMDisjunctionRule(),
            WkrqNDisjunctionRule(),
            WkrqTImplicationRule(),
            WkrqFImplicationRule(),
            WkrqMImplicationRule(),
            WkrqNImplicationRule(),
            WkrqTNegationRule(),
            WkrqFNegationRule(),
            WkrqMNegationRule(),
            WkrqNNegationRule(),
        ]
    
    def find_applicable_rules(self, signed_formula: SignedFormula, 
                            sign_system: str = "classical") -> List[SignedTableauRule]:
        """Find rules that apply to the given signed formula"""
        applicable = []
        for rule in self.rules:
            if (sign_system in rule.sign_systems and 
                rule.applies_to(signed_formula)):
                applicable.append(rule)
        return applicable
    
    def get_best_rule(self, signed_formula: SignedFormula,
                     sign_system: str = "classical") -> Optional[SignedTableauRule]:
        """Get the best rule to apply (highest priority)"""
        applicable = self.find_applicable_rules(signed_formula, sign_system)
        if not applicable:
            return None
        return min(applicable, key=lambda r: r.get_priority())
    
    def add_rule(self, rule: SignedTableauRule):
        """Add a custom rule to the registry"""
        self.rules.append(rule)


# Export main classes
__all__ = [
    'SignedRuleType', 'SignedRuleResult', 'SignedTableauRule',
    'TConjunctionRule', 'FConjunctionRule', 'TDisjunctionRule', 'FDisjunctionRule',
    'TImplicationRule', 'FImplicationRule', 'NegationRule', 'DoubleNegationRule',
    'UNegationRule', 'UConjunctionRule', 'SignedRuleRegistry',
    'FergusonTConjunctionRule', 'WkrqFConjunctionRule', 'WkrqMConjunctionRule', 'WkrqNConjunctionRule',
    'WkrqTDisjunctionRule', 'WkrqFDisjunctionRule', 'WkrqMDisjunctionRule', 'WkrqNDisjunctionRule',
    'WkrqTImplicationRule', 'WkrqFImplicationRule', 'WkrqMImplicationRule', 'WkrqNImplicationRule',
    'WkrqTNegationRule', 'WkrqFNegationRule', 'WkrqMNegationRule', 'WkrqNNegationRule'
]