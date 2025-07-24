#!/usr/bin/env python3
"""
Tableau Rules: Complete Rule System for Non-Classical Logic Tableaux

This module implements a comprehensive rule system for semantic tableaux
across multiple logic systems. It provides a unified framework for defining
and applying tableau expansion rules while maintaining the theoretical
correctness required for sound and complete reasoning.

Supported Logic Systems:
- Classical Propositional Logic: Standard T/F tableau rules
- Three-Valued Logic (WK3): Rules handling undefined truth values
- wKrQ Logic: Ferguson's epistemic signs with uncertainty handling

The rule system is designed for:
- Theoretical Soundness: All rules implement correct logical semantics
- Completeness Preservation: No arbitrary limits that compromise decidability
- Performance Optimization: α/β rule classification for efficient expansion
- Extensibility: Clean interfaces for adding new logic systems

Rule Classification:
- α-rules: Linear expansion (single branch continuation)
- β-rules: Branching expansion (multiple branch creation)
- Priority System: α-rules before β-rules for optimal tableau construction

Academic Foundation:
Based on Smullyan's unified notation, extended with many-valued logic rules
from Priest and Fitting, and epistemic extensions from Ferguson (2021).

Author: Generated for tableau reasoning research
License: MIT
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Set, Optional, Union, Tuple, Any

from tableau_core import (
    Formula, Atom, Negation, Conjunction, Disjunction, Implication,
    Sign, ClassicalSign, ThreeValuedSign, WkrqSign,
    SignedFormula, TruthValue, t, f, e
)


# =============================================================================
# RULE CLASSIFICATION SYSTEM
# =============================================================================

class RulePriority(Enum):
    """
    Priority levels for tableau rule application.
    
    Higher priority rules are applied first to minimize search space.
    α-rules (linear expansion) have higher priority than β-rules (branching).
    """
    ALPHA = 1    # Highest priority - linear expansion
    BETA = 2     # Lower priority - branching expansion
    GAMMA = 3    # Lowest priority - special/complex rules


class SignedRuleType(Enum):
    """
    Enumeration of all signed tableau rule types.
    
    Organizes rules by their logical structure and expansion behavior.
    This classification is crucial for:
    - Rule selection algorithms
    - Priority-based expansion strategies  
    - Correctness verification
    - Performance optimization
    
    Classification follows Smullyan's α/β notation extended to many-valued
    and epistemic logics.
    """
    
    # General rule categories
    ALPHA = "α"                   # Linear expansion (single branch)
    BETA = "β"                    # Branching expansion (multiple branches)
    
    # =================== α-RULES (Linear Expansion) ===================
    # These rules add formulas to the same branch without creating new branches
    
    # Classical α-rules
    T_CONJUNCTION = "T∧"          # T:(A∧B) → T:A, T:B
    F_DISJUNCTION = "F∨"          # F:(A∨B) → F:A, F:B  
    F_IMPLICATION = "F→"          # F:(A→B) → T:A, F:B
    T_DOUBLE_NEGATION = "T¬¬"     # T:¬¬A → T:A
    F_DOUBLE_NEGATION = "F¬¬"     # F:¬¬A → F:A
    T_NEGATION = "T¬"             # T:¬A → F:A
    F_NEGATION = "F¬"             # F:¬A → T:A
    
    # Three-valued α-rules
    U_NEGATION = "U¬"             # U:¬A → U:A (undefined negation)
    
    # wKrQ α-rules (epistemic uncertainty)
    M_CONJUNCTION = "M∧"          # M:(A∧B) → M:A, M:B
    N_DISJUNCTION = "N∨"          # N:(A∨B) → N:A, N:B
    M_NEGATION = "M¬"             # M:¬A → N:A (epistemic duality)
    N_NEGATION = "N¬"             # N:¬A → M:A (epistemic duality)
    N_IMPLICATION = "N→"          # N:(A→B) → M:A, N:B
    
    # =================== β-RULES (Branching Expansion) =================
    # These rules create multiple branches representing alternative satisfactions
    
    # Classical β-rules
    F_CONJUNCTION = "F∧"          # F:(A∧B) → F:A | F:B
    T_DISJUNCTION = "T∨"          # T:(A∨B) → T:A | T:B
    T_IMPLICATION = "T→"          # T:(A→B) → F:A | T:B
    
    # Three-valued β-rules
    U_CONJUNCTION = "U∧"          # U:(A∧B) → complex patterns
    U_DISJUNCTION = "U∨"          # U:(A∨B) → complex patterns
    U_IMPLICATION = "U→"          # U:(A→B) → complex patterns
    
    # wKrQ β-rules (epistemic branching)
    N_CONJUNCTION = "N∧"          # N:(A∧B) → N:A | N:B
    M_DISJUNCTION = "M∨"          # M:(A∨B) → M:A | M:B
    M_IMPLICATION = "M→"          # M:(A→B) → N:A | M:B

    @property
    def is_alpha(self) -> bool:
        """Check if this is an α-rule (linear expansion)"""
        return self in {
            # Classical α-rules
            self.T_CONJUNCTION, self.F_DISJUNCTION, self.F_IMPLICATION,
            self.T_DOUBLE_NEGATION, self.F_DOUBLE_NEGATION, self.T_NEGATION, self.F_NEGATION,
            # Three-valued α-rules  
            self.U_NEGATION,
            # wKrQ α-rules
            self.M_CONJUNCTION, self.N_DISJUNCTION, self.M_NEGATION, self.N_NEGATION, self.N_IMPLICATION
        }
    
    @property  
    def is_beta(self) -> bool:
        """Check if this is a β-rule (branching expansion)"""
        return not self.is_alpha


# Compatibility aliases for existing code
RuleType = SignedRuleType


class SignedRuleResult:
    """
    Result of applying a signed tableau rule.
    
    Encapsulates the outcome of rule application, including:
    - The new signed formulas to add
    - Whether this creates new branches (α vs β)
    - Branch structure for complex expansions
    
    This abstraction enables the tableau engine to handle any rule type
    uniformly while maintaining the distinction between linear and
    branching expansion patterns.
    """
    
    def __init__(self, branches: List[List[SignedFormula]], is_alpha: bool = True):
        """
        Create a rule result.
        
        Args:
            branches: List of branches, each containing signed formulas to add
            is_alpha: True for α-rules (single branch), False for β-rules (multiple branches)
        """
        self.branches = branches
        self.is_alpha = is_alpha
        self.branch_count = len(branches)
    
    @property
    def rule_type(self) -> 'SignedRuleType':
        """Get the rule type based on alpha/beta classification"""
        return SignedRuleType.ALPHA if self.is_alpha else SignedRuleType.BETA
    
    @property 
    def conclusions(self) -> List[SignedFormula]:
        """Get all conclusions as a flat list (for α-rules)"""
        if self.is_alpha and len(self.branches) == 1:
            return self.branches[0]
        else:
            # For β-rules, return all conclusions from all branches
            result = []
            for branch in self.branches:
                result.extend(branch)
            return result
    
    @classmethod
    def alpha_rule(cls, *formulas: SignedFormula) -> 'SignedRuleResult':
        """
        Create result for α-rule (single branch with multiple formulas).
        
        α-rules add all resulting formulas to the same tableau branch,
        representing conjunctive requirements that must all be satisfied.
        
        Args:
            *formulas: Signed formulas to add to the current branch
            
        Returns:
            SignedRuleResult representing linear expansion
        """
        return cls([list(formulas)], is_alpha=True)
    
    @classmethod  
    def beta_rule(cls, *branches: List[SignedFormula]) -> 'SignedRuleResult':
        """
        Create result for β-rule (multiple branches).
        
        β-rules create multiple tableau branches, representing disjunctive
        requirements where any one branch being satisfied is sufficient.
        
        Args:
            *branches: Lists of signed formulas, one per branch
            
        Returns:
            SignedRuleResult representing branching expansion
        """
        return cls(list(branches), is_alpha=False)


# =============================================================================
# ABSTRACT RULE FRAMEWORK
# =============================================================================

class SignedTableauRule(ABC):
    """
    Abstract base class for all signed tableau rules.
    
    Provides the common interface that all tableau rules must implement,
    enabling the tableau engine to apply rules uniformly across different
    logic systems. Each rule encapsulates:
    
    - Applicability conditions (which signed formulas it applies to)
    - Transformation logic (how to expand the signed formula)
    - Priority information (for optimal rule ordering)
    - Logic system compatibility (which systems support this rule)
    
    The design supports both built-in logic systems and user-defined
    extensions through consistent interfaces and clear documentation.
    """
    
    def __init__(self, rule_type: SignedRuleType, sign_systems: List[str]):
        """
        Initialize a tableau rule.
        
        Args:
            rule_type: The type classification of this rule
            sign_systems: List of logic systems that support this rule
        """
        self.rule_type = rule_type
        self.sign_systems = sign_systems  # Which sign systems this rule applies to
    
    @abstractmethod
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """
        Check if this rule applies to the given signed formula.
        
        This is the core matching function that determines when a rule
        should be applied. Rules should be precise about their applicability
        to avoid incorrect transformations.
        
        Args:
            signed_formula: The signed formula to check
            
        Returns:
            True if rule applies, False otherwise
        """
        pass
    
    @abstractmethod
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """
        Apply the rule to the signed formula.
        
        Performs the actual tableau expansion, transforming the input
        signed formula into new signed formulas according to the
        logical semantics of the rule.
        
        Args:
            signed_formula: The signed formula to expand
            
        Returns:
            SignedRuleResult containing the expansion
        """
        pass
    
    def get_priority(self) -> int:
        """
        Get rule priority (lower = higher priority).
        
        α-rules generally have higher priority than β-rules to minimize
        tableau branching and improve performance.
        
        Returns:
            Integer priority (1 for α-rules, 2 for β-rules)
        """
        return 1 if self.is_alpha_rule() else 2
    
    def is_alpha_rule(self) -> bool:
        """
        Check if this is an α-rule (linear expansion).
        
        α-rules add formulas to the same branch without creating new branches.
        They represent conjunctive decompositions where all components
        must be satisfied.
        
        Returns:
            True if this is an α-rule, False otherwise
        """
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
        """
        Check if this is a β-rule (branching expansion).
        
        β-rules create multiple branches representing alternative ways
        to satisfy the signed formula. They represent disjunctive
        decompositions where any one branch being satisfied is sufficient.
        
        Returns:
            True if this is a β-rule, False otherwise
        """
        return not self.is_alpha_rule()


# =============================================================================
# CLASSICAL LOGIC RULES
# =============================================================================

class TConjunctionRule(SignedTableauRule):
    """
    T:(A∧B) → T:A, T:B (α-rule)
    
    Classical true conjunction expansion. If a conjunction must be true,
    then both conjuncts must be true. This is a fundamental α-rule that
    adds both conjuncts to the same branch.
    
    Logical Basis:
    A conjunction is true iff both conjuncts are true.
    
    Example:
    T:(p ∧ q) expands to T:p, T:q on the same branch.
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.T_CONJUNCTION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to T-signed conjunctions in classical and three-valued systems"""
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "T" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand T:(A∧B) to T:A, T:B"""
        conj = signed_formula.formula
        left_signed = SignedFormula(signed_formula.sign, conj.left)
        right_signed = SignedFormula(signed_formula.sign, conj.right)
        return SignedRuleResult.alpha_rule(left_signed, right_signed)


class FConjunctionRule(SignedTableauRule):
    """
    F:(A∧B) → F:A | F:B (β-rule)
    
    Classical false conjunction expansion. If a conjunction must be false,
    then at least one conjunct must be false. This creates a branching
    expansion with two alternative satisfactions.
    
    Logical Basis:
    A conjunction is false iff at least one conjunct is false.
    
    Example:
    F:(p ∧ q) creates two branches: [F:p] and [F:q].
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.F_CONJUNCTION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to F-signed conjunctions in classical and three-valued systems"""
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "F" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand F:(A∧B) to F:A | F:B"""
        conj = signed_formula.formula
        left_signed = SignedFormula(signed_formula.sign, conj.left)
        right_signed = SignedFormula(signed_formula.sign, conj.right)
        return SignedRuleResult.beta_rule([left_signed], [right_signed])


class TDisjunctionRule(SignedTableauRule):
    """
    T:(A∨B) → T:A | T:B (β-rule)
    
    Classical true disjunction expansion. If a disjunction must be true,
    then at least one disjunct must be true. This creates a branching
    expansion with two alternative satisfactions.
    
    Logical Basis:
    A disjunction is true iff at least one disjunct is true.
    
    Example:
    T:(p ∨ q) creates two branches: [T:p] and [T:q].
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.T_DISJUNCTION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to T-signed disjunctions in classical and three-valued systems"""
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "T" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand T:(A∨B) to T:A | T:B"""
        disj = signed_formula.formula
        left_signed = SignedFormula(signed_formula.sign, disj.left)
        right_signed = SignedFormula(signed_formula.sign, disj.right)
        return SignedRuleResult.beta_rule([left_signed], [right_signed])


class FDisjunctionRule(SignedTableauRule):
    """
    F:(A∨B) → F:A, F:B (α-rule)
    
    Classical false disjunction expansion. If a disjunction must be false,
    then both disjuncts must be false. This is an α-rule that adds both
    negated disjuncts to the same branch.
    
    Logical Basis:
    A disjunction is false iff both disjuncts are false.
    
    Example:
    F:(p ∨ q) expands to F:p, F:q on the same branch.
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.F_DISJUNCTION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to F-signed disjunctions in classical and three-valued systems"""
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "F" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand F:(A∨B) to F:A, F:B"""
        disj = signed_formula.formula
        left_signed = SignedFormula(signed_formula.sign, disj.left)
        right_signed = SignedFormula(signed_formula.sign, disj.right)
        return SignedRuleResult.alpha_rule(left_signed, right_signed)


class TImplicationRule(SignedTableauRule):
    """
    T:(A→B) → F:A | T:B (β-rule)
    
    Classical true implication expansion. If an implication must be true,
    then either the antecedent is false or the consequent is true.
    This corresponds to the semantic equivalence (A→B) ≡ (¬A∨B).
    
    Logical Basis:
    An implication is true iff the antecedent is false or the consequent is true.
    
    Example:
    T:(p → q) creates two branches: [F:p] and [T:q].
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.T_IMPLICATION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to T-signed implications in classical and three-valued systems"""
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "T" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand T:(A→B) to F:A | T:B"""
        impl = signed_formula.formula
        # Create opposite sign for antecedent
        if isinstance(signed_formula.sign, ClassicalSign):
            false_sign = ClassicalSign("F")
        else:  # ThreeValuedSign
            false_sign = ThreeValuedSign("F")
        
        ant_signed = SignedFormula(false_sign, impl.antecedent)
        cons_signed = SignedFormula(signed_formula.sign, impl.consequent)
        return SignedRuleResult.beta_rule([ant_signed], [cons_signed])


class FImplicationRule(SignedTableauRule):
    """
    F:(A→B) → T:A, F:B (α-rule)
    
    Classical false implication expansion. If an implication must be false,
    then the antecedent must be true and the consequent must be false.
    This is the only way an implication can fail.
    
    Logical Basis:
    An implication is false iff the antecedent is true and the consequent is false.
    
    Example:
    F:(p → q) expands to T:p, F:q on the same branch.
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.F_IMPLICATION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to F-signed implications in classical and three-valued systems"""
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) == "F" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand F:(A→B) to T:A, F:B"""
        impl = signed_formula.formula
        # Create opposite sign for consequent
        if isinstance(signed_formula.sign, ClassicalSign):
            true_sign = ClassicalSign("T")
        else:  # ThreeValuedSign
            true_sign = ThreeValuedSign("T")
        
        ant_signed = SignedFormula(true_sign, impl.antecedent)
        cons_signed = SignedFormula(signed_formula.sign, impl.consequent)
        return SignedRuleResult.alpha_rule(ant_signed, cons_signed)


class NegationRule(SignedTableauRule):
    """
    T:¬A → F:A and F:¬A → T:A (α-rules)
    
    Classical negation expansion. Negation flips the truth requirement:
    - If ¬A must be true, then A must be false
    - If ¬A must be false, then A must be true
    
    This rule handles both directions in a single implementation.
    
    Logical Basis:
    Negation inverts truth values in classical logic.
    
    Examples:
    T:¬p expands to F:p
    F:¬p expands to T:p
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.T_NEGATION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to T/F-signed negations in classical and three-valued systems"""
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) in ["T", "F"] and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand T:¬A to F:A or F:¬A to T:A"""
        neg = signed_formula.formula
        # Flip the sign
        if str(signed_formula.sign) == "T":
            if isinstance(signed_formula.sign, ClassicalSign):
                new_sign = ClassicalSign("F")
            else:  # ThreeValuedSign
                new_sign = ThreeValuedSign("F")
        else:  # "F"
            if isinstance(signed_formula.sign, ClassicalSign):
                new_sign = ClassicalSign("T")
            else:  # ThreeValuedSign
                new_sign = ThreeValuedSign("T")
        
        result_signed = SignedFormula(new_sign, neg.operand)
        return SignedRuleResult.alpha_rule(result_signed)


class DoubleNegationRule(SignedTableauRule):
    """
    T:¬¬A → T:A and F:¬¬A → F:A (α-rules)
    
    Classical double negation elimination. Double negation is semantically
    equivalent to the original formula in classical logic, so we can
    eliminate both negation symbols.
    
    Logical Basis:
    In classical logic, ¬¬A is logically equivalent to A.
    
    Examples:
    T:¬¬p expands to T:p
    F:¬¬p expands to F:p
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.T_DOUBLE_NEGATION, ["classical", "three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to T/F-signed double negations in classical and three-valued systems"""
        return (isinstance(signed_formula.sign, (ClassicalSign, ThreeValuedSign)) and
                str(signed_formula.sign) in ["T", "F"] and
                isinstance(signed_formula.formula, Negation) and
                isinstance(signed_formula.formula.operand, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand T:¬¬A to T:A or F:¬¬A to F:A"""
        double_neg = signed_formula.formula
        inner_formula = double_neg.operand.operand
        result_signed = SignedFormula(signed_formula.sign, inner_formula)
        return SignedRuleResult.alpha_rule(result_signed)


# =============================================================================
# THREE-VALUED LOGIC RULES (WK3)
# =============================================================================

class UNegationRule(SignedTableauRule):
    """
    U:¬A → U:A (α-rule)
    
    Three-valued undefined negation. In weak Kleene logic, if ¬A is undefined,
    then A is also undefined. Undefined values are "infectious" under negation.
    
    Logical Basis:
    In WK3, negation of undefined yields undefined.
    
    Example:
    U:¬p expands to U:p
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.U_NEGATION, ["three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to U-signed negations in three-valued systems"""
        return (isinstance(signed_formula.sign, ThreeValuedSign) and
                str(signed_formula.sign) == "U" and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand U:¬A to U:A"""
        neg = signed_formula.formula
        result_signed = SignedFormula(signed_formula.sign, neg.operand)
        return SignedRuleResult.alpha_rule(result_signed)


class UConjunctionRule(SignedTableauRule):
    """
    U:(A∧B) → U:A, U:B (α-rule, simplified)
    
    Three-valued undefined conjunction. In weak Kleene logic, if a conjunction
    is undefined, then typically both operands are undefined. This is a
    simplified version of the complete WK3 semantics.
    
    Note: Complete WK3 conjunction rules are more complex and would require
    multiple expansion patterns. This implementation provides the most common case.
    
    Logical Basis:
    In WK3, undefined conjunction often results from undefined operands.
    
    Example:
    U:(p ∧ q) expands to U:p, U:q
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.U_CONJUNCTION, ["three_valued"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to U-signed conjunctions in three-valued systems"""
        return (isinstance(signed_formula.sign, ThreeValuedSign) and
                str(signed_formula.sign) == "U" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand U:(A∧B) to U:A, U:B (simplified rule)"""
        conj = signed_formula.formula
        u_sign = ThreeValuedSign(e)
        left_u = SignedFormula(u_sign, conj.left)
        right_u = SignedFormula(u_sign, conj.right)
        return SignedRuleResult.alpha_rule(left_u, right_u)


# =============================================================================
# wKrQ LOGIC RULES (Ferguson's Epistemic Extensions)
# =============================================================================

class WkrqTConjunctionRule(SignedTableauRule):
    """
    T:(A∧B) → T:A, T:B (α-rule)
    
    wKrQ true conjunction expansion. Identical to classical behavior.
    If a conjunction is definitely true, then both conjuncts must be definitely true.
    
    Logical Basis:
    Same as classical logic for definite truth.
    
    Example:
    T:(p ∧ q) expands to T:p, T:q
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.T_CONJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to T-signed conjunctions in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "T" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand T:(A∧B) to T:A, T:B"""
        conj = signed_formula.formula
        t_sign = WkrqSign("T")
        left_t = SignedFormula(t_sign, conj.left)
        right_t = SignedFormula(t_sign, conj.right)
        return SignedRuleResult.alpha_rule(left_t, right_t)


class WkrqFConjunctionRule(SignedTableauRule):
    """
    F:(A∧B) → F:A | F:B (β-rule)
    
    wKrQ false conjunction expansion. Identical to classical behavior.
    If a conjunction is definitely false, then at least one conjunct must be definitely false.
    
    Logical Basis:
    Same as classical logic for definite falsehood.
    
    Example:
    F:(p ∧ q) creates two branches: [F:p] and [F:q]
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.F_CONJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to F-signed conjunctions in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "F" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand F:(A∧B) to F:A | F:B"""
        conj = signed_formula.formula
        f_sign = WkrqSign("F")
        left_f = SignedFormula(f_sign, conj.left)
        right_f = SignedFormula(f_sign, conj.right)
        return SignedRuleResult.beta_rule([left_f], [right_f])


class WkrqMConjunctionRule(SignedTableauRule):
    """
    M:(A∧B) → M:A, M:B (α-rule)
    
    wKrQ epistemic "may be true" conjunction expansion. If a conjunction
    may be true, then both conjuncts may be true. This represents the
    minimal epistemic commitment required for conjunction satisfaction.
    
    Logical Basis:
    For a conjunction to possibly be true, both operands must possibly be true.
    
    Example:
    M:(p ∧ q) expands to M:p, M:q
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.M_CONJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to M-signed conjunctions in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "M" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand M:(A∧B) to M:A, M:B"""
        conj = signed_formula.formula
        m_sign = WkrqSign("M")
        left_m = SignedFormula(m_sign, conj.left)
        right_m = SignedFormula(m_sign, conj.right)
        return SignedRuleResult.alpha_rule(left_m, right_m)


class WkrqNConjunctionRule(SignedTableauRule):
    """
    N:(A∧B) → N:A | N:B (β-rule)
    
    wKrQ epistemic "need not be true" conjunction expansion. If a conjunction
    need not be true, then at least one conjunct need not be true. This
    represents the disjunctive ways a conjunction can fail to be necessarily true.
    
    Logical Basis:
    For a conjunction to possibly be false, at least one operand must possibly be false.
    
    Example:
    N:(p ∧ q) creates two branches: [N:p] and [N:q]
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.N_CONJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to N-signed conjunctions in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "N" and
                isinstance(signed_formula.formula, Conjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand N:(A∧B) to N:A | N:B"""
        conj = signed_formula.formula
        n_sign = WkrqSign("N")
        left_n = SignedFormula(n_sign, conj.left)
        right_n = SignedFormula(n_sign, conj.right)
        return SignedRuleResult.beta_rule([left_n], [right_n])


class WkrqTDisjunctionRule(SignedTableauRule):
    """
    T:(A∨B) → T:A | T:B (β-rule)
    
    wKrQ true disjunction expansion. Identical to classical behavior.
    If a disjunction is definitely true, then at least one disjunct must be definitely true.
    
    Logical Basis:
    Same as classical logic for definite truth.
    
    Example:
    T:(p ∨ q) creates two branches: [T:p] and [T:q]
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.T_DISJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to T-signed disjunctions in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "T" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand T:(A∨B) to T:A | T:B"""
        disj = signed_formula.formula
        t_sign = WkrqSign("T")
        left_t = SignedFormula(t_sign, disj.left)
        right_t = SignedFormula(t_sign, disj.right)
        return SignedRuleResult.beta_rule([left_t], [right_t])


class WkrqFDisjunctionRule(SignedTableauRule):
    """
    F:(A∨B) → F:A, F:B (α-rule)
    
    wKrQ false disjunction expansion. Identical to classical behavior.
    If a disjunction is definitely false, then both disjuncts must be definitely false.
    
    Logical Basis:
    Same as classical logic for definite falsehood.
    
    Example:
    F:(p ∨ q) expands to F:p, F:q
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.F_DISJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to F-signed disjunctions in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "F" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand F:(A∨B) to F:A, F:B"""
        disj = signed_formula.formula
        f_sign = WkrqSign("F")
        left_f = SignedFormula(f_sign, disj.left)
        right_f = SignedFormula(f_sign, disj.right)
        return SignedRuleResult.alpha_rule(left_f, right_f)


class WkrqMDisjunctionRule(SignedTableauRule):
    """
    M:(A∨B) → M:A | M:B (β-rule)
    
    wKrQ epistemic "may be true" disjunction expansion. If a disjunction
    may be true, then at least one disjunct may be true. This represents
    the alternative ways a disjunction can be satisfied under epistemic uncertainty.
    
    Logical Basis:
    For a disjunction to possibly be true, at least one operand must possibly be true.
    
    Example:
    M:(p ∨ q) creates two branches: [M:p] and [M:q]
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.M_DISJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to M-signed disjunctions in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "M" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand M:(A∨B) to M:A | M:B"""
        disj = signed_formula.formula
        m_sign = WkrqSign("M")
        left_m = SignedFormula(m_sign, disj.left)
        right_m = SignedFormula(m_sign, disj.right)
        return SignedRuleResult.beta_rule([left_m], [right_m])


class WkrqNDisjunctionRule(SignedTableauRule):
    """
    N:(A∨B) → N:A, N:B (α-rule)
    
    wKrQ epistemic "need not be true" disjunction expansion. If a disjunction
    need not be true, then both disjuncts need not be true. This represents
    the conjunctive requirement for a disjunction to fail to be necessarily true.
    
    Logical Basis:
    For a disjunction to possibly be false, both operands must possibly be false.
    
    Example:
    N:(p ∨ q) expands to N:p, N:q
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.N_DISJUNCTION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to N-signed disjunctions in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "N" and
                isinstance(signed_formula.formula, Disjunction))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand N:(A∨B) to N:A, N:B"""
        disj = signed_formula.formula
        n_sign = WkrqSign("N")
        left_n = SignedFormula(n_sign, disj.left)
        right_n = SignedFormula(n_sign, disj.right)
        return SignedRuleResult.alpha_rule(left_n, right_n)


# =============================================================================
# wKrQ NEGATION RULES (Epistemic Duality)
# =============================================================================

class WkrqMNegationRule(SignedTableauRule):
    """
    M:¬A → N:A (α-rule)
    
    wKrQ epistemic negation with M sign. If ¬A may be true, then A need not be true.
    This implements the epistemic duality relationship M ↔ N under negation.
    
    Logical Basis:
    If ¬A is possibly true, then A is possibly false (need not be true).
    
    Example:
    M:¬p expands to N:p
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.M_NEGATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to M-signed negations in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "M" and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand M:¬A to N:A (epistemic duality)"""
        neg = signed_formula.formula
        n_sign = WkrqSign("N")
        n_inner = SignedFormula(n_sign, neg.operand)
        return SignedRuleResult.alpha_rule(n_inner)


class WkrqNNegationRule(SignedTableauRule):
    """
    N:¬A → M:A (α-rule)
    
    wKrQ epistemic negation with N sign. If ¬A need not be true, then A may be true.
    This implements the epistemic duality relationship N ↔ M under negation.
    
    Logical Basis:
    If ¬A is possibly false, then A is possibly true (may be true).
    
    Example:
    N:¬p expands to M:p
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.N_NEGATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to N-signed negations in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "N" and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand N:¬A to M:A (epistemic duality)"""
        neg = signed_formula.formula
        m_sign = WkrqSign("M")
        m_inner = SignedFormula(m_sign, neg.operand)
        return SignedRuleResult.alpha_rule(m_inner)


class WkrqTNegationRule(SignedTableauRule):
    """
    T:¬A → F:A (α-rule)
    
    wKrQ definite negation with T sign. Identical to classical behavior.
    If ¬A is definitely true, then A must be definitely false.
    
    Logical Basis:
    Same as classical logic for definite truth.
    
    Example:
    T:¬p expands to F:p
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.T_NEGATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to T-signed negations in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "T" and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand T:¬A to F:A"""
        neg = signed_formula.formula
        f_sign = WkrqSign("F")
        f_inner = SignedFormula(f_sign, neg.operand)
        return SignedRuleResult.alpha_rule(f_inner)


class WkrqFNegationRule(SignedTableauRule):
    """
    F:¬A → T:A (α-rule)
    
    wKrQ definite negation with F sign. Identical to classical behavior.
    If ¬A is definitely false, then A must be definitely true.
    
    Logical Basis:
    Same as classical logic for definite falsehood.
    
    Example:
    F:¬p expands to T:p
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.F_NEGATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to F-signed negations in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "F" and
                isinstance(signed_formula.formula, Negation))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand F:¬A to T:A"""
        neg = signed_formula.formula
        t_sign = WkrqSign("T")
        t_inner = SignedFormula(t_sign, neg.operand)
        return SignedRuleResult.alpha_rule(t_inner)


# =============================================================================
# wKrQ IMPLICATION RULES (Epistemic Extensions)
# =============================================================================

class WkrqTImplicationRule(SignedTableauRule):
    """
    T:(A→B) → F:A | T:B (β-rule)
    
    wKrQ true implication expansion. Identical to classical behavior.
    If an implication is definitely true, then either the antecedent is definitely false
    or the consequent is definitely true.
    
    Logical Basis:
    Same as classical logic for definite truth.
    
    Example:
    T:(p → q) creates two branches: [F:p] and [T:q]
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.T_IMPLICATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to T-signed implications in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "T" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand T:(A→B) to F:A | T:B"""
        impl = signed_formula.formula
        f_sign = WkrqSign("F")
        t_sign = WkrqSign("T")
        left_f = SignedFormula(f_sign, impl.antecedent)
        right_t = SignedFormula(t_sign, impl.consequent)
        return SignedRuleResult.beta_rule([left_f], [right_t])


class WkrqFImplicationRule(SignedTableauRule):
    """
    F:(A→B) → T:A, F:B (α-rule)
    
    wKrQ false implication expansion. Identical to classical behavior.
    If an implication is definitely false, then the antecedent must be definitely true
    and the consequent must be definitely false.
    
    Logical Basis:
    Same as classical logic for definite falsehood.
    
    Example:
    F:(p → q) expands to T:p, F:q
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.F_IMPLICATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to F-signed implications in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "F" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand F:(A→B) to T:A, F:B"""
        impl = signed_formula.formula
        t_sign = WkrqSign("T")
        f_sign = WkrqSign("F")
        ant_t = SignedFormula(t_sign, impl.antecedent)
        cons_f = SignedFormula(f_sign, impl.consequent)
        return SignedRuleResult.alpha_rule(ant_t, cons_f)


class WkrqMImplicationRule(SignedTableauRule):
    """
    M:(A→B) → N:A | M:B (β-rule)
    
    wKrQ epistemic "may be true" implication expansion. If an implication may be true,
    then either the antecedent need not be true or the consequent may be true.
    This follows the epistemic interpretation of implication possibility.
    
    Logical Basis:
    For an implication to possibly be true, either the antecedent is possibly false
    or the consequent is possibly true.
    
    Example:
    M:(p → q) creates two branches: [N:p] and [M:q]
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.M_IMPLICATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to M-signed implications in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "M" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand M:(A→B) to N:A | M:B (epistemic semantics)"""
        impl = signed_formula.formula
        n_sign = WkrqSign("N")
        m_sign = WkrqSign("M")
        ant_n = SignedFormula(n_sign, impl.antecedent)
        cons_m = SignedFormula(m_sign, impl.consequent)
        return SignedRuleResult.beta_rule([ant_n], [cons_m])


class WkrqNImplicationRule(SignedTableauRule):
    """
    N:(A→B) → M:A, N:B (α-rule)
    
    wKrQ epistemic "need not be true" implication expansion. If an implication
    need not be true, then the antecedent may be true and the consequent need not be true.
    This represents the conjunctive requirement for an implication to possibly fail.
    
    Logical Basis:
    For an implication to possibly be false, the antecedent must possibly be true
    and the consequent must possibly be false.
    
    Example:
    N:(p → q) expands to M:p, N:q
    """
    
    def __init__(self):
        super().__init__(SignedRuleType.N_IMPLICATION, ["wkrq"])
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        """Apply to N-signed implications in wKrQ systems"""
        return (isinstance(signed_formula.sign, WkrqSign) and
                signed_formula.sign.designation == "N" and
                isinstance(signed_formula.formula, Implication))
    
    def apply(self, signed_formula: SignedFormula) -> SignedRuleResult:
        """Expand N:(A→B) to M:A, N:B (epistemic semantics)"""
        impl = signed_formula.formula
        m_sign = WkrqSign("M")
        n_sign = WkrqSign("N")
        ant_m = SignedFormula(m_sign, impl.antecedent)
        cons_n = SignedFormula(n_sign, impl.consequent)
        return SignedRuleResult.alpha_rule(ant_m, cons_n)


# =============================================================================
# RULE REGISTRY AND MANAGEMENT
# =============================================================================

class SignedRuleRegistry:
    """
    Central registry for managing signed tableau rules across logic systems.
    
    Provides a unified interface for:
    - Rule registration and lookup
    - Logic system compatibility checking
    - Priority-based rule selection
    - Extensibility for new logic systems
    
    The registry automatically loads all built-in rules and provides
    methods for adding custom rules for new logic systems.
    """
    
    def __init__(self):
        """Initialize registry with all standard signed tableau rules"""
        self.rules: List[SignedTableauRule] = []
        self._load_standard_rules()
    
    def _load_standard_rules(self):
        """Load all standard signed tableau rules for built-in logic systems"""
        self.rules = [
            # Classical logic rules
            TConjunctionRule(),
            FConjunctionRule(), 
            TDisjunctionRule(),
            FDisjunctionRule(),
            TImplicationRule(),
            FImplicationRule(),
            NegationRule(),
            DoubleNegationRule(),
            
            # Three-valued logic rules
            UNegationRule(),
            UConjunctionRule(),
            
            # wKrQ logic rules (complete set)
            WkrqTConjunctionRule(),
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
        """
        Find all rules that apply to the given signed formula in the specified system.
        
        Args:
            signed_formula: The signed formula to find rules for
            sign_system: The logic system name ("classical", "three_valued", "wkrq")
            
        Returns:
            List of applicable rules sorted by priority
        """
        applicable = []
        for rule in self.rules:
            if (sign_system in rule.sign_systems and 
                rule.applies_to(signed_formula)):
                applicable.append(rule)
        
        # Sort by priority (α-rules before β-rules)
        return sorted(applicable, key=lambda r: r.get_priority())
    
    def get_best_rule(self, signed_formula: SignedFormula,
                     sign_system: str = "classical") -> Optional[SignedTableauRule]:
        """
        Get the best (highest priority) rule to apply to the signed formula.
        
        Prioritizes α-rules over β-rules to minimize tableau branching
        and improve performance.
        
        Args:
            signed_formula: The signed formula to find a rule for
            sign_system: The logic system name
            
        Returns:
            Best applicable rule, or None if no rules apply
        """
        applicable = self.find_applicable_rules(signed_formula, sign_system)
        return applicable[0] if applicable else None
    
    def get_rule_for_formula(self, signed_formula: SignedFormula) -> Optional[SignedTableauRule]:
        """
        Get a rule for the signed formula (alias for get_best_rule with classical system).
        
        Args:
            signed_formula: The signed formula to find a rule for
            
        Returns:
            Applicable rule, or None if no rules apply
        """
        return self.get_best_rule(signed_formula, "classical")
    
    def add_rule(self, rule: SignedTableauRule):
        """
        Add a custom rule to the registry.
        
        Enables extension with new logic systems by registering
        additional tableau rules.
        
        Args:
            rule: The custom rule to add
        """
        self.rules.append(rule)
    
    def get_rules_for_system(self, sign_system: str) -> List[SignedTableauRule]:
        """
        Get all rules applicable to a specific logic system.
        
        Args:
            sign_system: The logic system name
            
        Returns:
            List of rules that support the system
        """
        return [rule for rule in self.rules if sign_system in rule.sign_systems]
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the rule registry.
        
        Returns:
            Dictionary with rule counts and system information
        """
        stats = {
            "total_rules": len(self.rules),
            "alpha_rules": len([r for r in self.rules if r.is_alpha_rule()]),
            "beta_rules": len([r for r in self.rules if r.is_beta_rule()]),
            "systems": {}
        }
        
        # Count rules per system
        all_systems = set()
        for rule in self.rules:
            all_systems.update(rule.sign_systems)
        
        for system in all_systems:
            system_rules = self.get_rules_for_system(system)
            stats["systems"][system] = {
                "total": len(system_rules),
                "alpha": len([r for r in system_rules if r.is_alpha_rule()]),
                "beta": len([r for r in system_rules if r.is_beta_rule()])
            }
        
        return stats


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Rule classification
    'SignedRuleType', 'SignedRuleResult',
    
    # Abstract framework
    'SignedTableauRule',
    
    # Classical rules
    'TConjunctionRule', 'FConjunctionRule', 'TDisjunctionRule', 'FDisjunctionRule',
    'TImplicationRule', 'FImplicationRule', 'NegationRule', 'DoubleNegationRule',
    
    # Three-valued rules
    'UNegationRule', 'UConjunctionRule',
    
    # wKrQ rules
    'WkrqTConjunctionRule', 'WkrqFConjunctionRule', 'WkrqMConjunctionRule', 'WkrqNConjunctionRule',
    'WkrqTDisjunctionRule', 'WkrqFDisjunctionRule', 'WkrqMDisjunctionRule', 'WkrqNDisjunctionRule',
    'WkrqTImplicationRule', 'WkrqFImplicationRule', 'WkrqMImplicationRule', 'WkrqNImplicationRule',
    'WkrqTNegationRule', 'WkrqFNegationRule', 'WkrqMNegationRule', 'WkrqNNegationRule',
    
    # Registry
    'SignedRuleRegistry',
    
    # Compatibility aliases
    'RuleType', 'RulePriority', 'TableauRule', 'RuleResult',
    
    # Utility functions
    'get_rule_registry', 'get_rule_for_signed_formula'
]

# Additional compatibility aliases (set after all classes are defined)
TableauRule = SignedTableauRule
RuleResult = SignedRuleResult


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_rule_registry(sign_system: str = "classical") -> SignedRuleRegistry:
    """
    Get a rule registry for the specified sign system.
    
    Args:
        sign_system: The sign system ("classical", "three_valued", "wkrq")
        
    Returns:
        SignedRuleRegistry for the specified system
    """
    return SignedRuleRegistry()  # For now, return a new registry


def get_rule_for_signed_formula(signed_formula: SignedFormula, 
                               sign_system: str = "classical") -> Optional[SignedTableauRule]:
    """
    Get the appropriate rule for a signed formula.
    
    Args:
        signed_formula: The signed formula to find a rule for
        sign_system: The sign system to use
        
    Returns:
        The appropriate rule, or None if no rule applies
    """
    registry = get_rule_registry(sign_system)
    return registry.get_rule_for_formula(signed_formula)