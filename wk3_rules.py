#!/usr/bin/env python3
"""
WK3 Logic Tableau Rules

Concrete implementations of tableau expansion rules for Weak Kleene Logic (WK3).
These rules implement the tableau method for three-valued logic with truth values t, f, e.
"""

from typing import List
from tableau_rules import TableauRule, RuleType, RuleApplication, RuleContext
from formula import Formula, Negation, Conjunction, Disjunction, Implication, Atom
from truth_value import TruthValue, t, f, e


class WK3DoubleNegationRule(TableauRule):
    """WK3 rule for double negation elimination: ¬¬A → A"""
    
    @property
    def name(self) -> str:
        return "WK3 Double Negation Elimination"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.DOUBLE_NEGATION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is ¬¬A"""
        return (isinstance(formula, Negation) and 
                isinstance(formula.operand, Negation))
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply ¬¬A → A (same as classical)"""
        if not self.applies_to(formula):
            raise ValueError(f"WK3 double negation rule does not apply to {formula}")
        
        # Extract A from ¬¬A
        inner_formula = formula.operand.operand
        
        return RuleApplication(
            formulas_for_branches=[[inner_formula]],
            branch_count=1,
            metadata={"rule": "wk3_double_negation", "original": str(formula)}
        )


class WK3ConjunctionRule(TableauRule):
    """WK3 rule for conjunction: A ∧ B → A, B"""
    
    @property
    def name(self) -> str:
        return "WK3 Conjunction Elimination"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.CONJUNCTION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is A ∧ B"""
        return isinstance(formula, Conjunction)
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply A ∧ B → A, B (same as classical)"""
        if not self.applies_to(formula):
            raise ValueError(f"WK3 conjunction rule does not apply to {formula}")
        
        return RuleApplication(
            formulas_for_branches=[[formula.left, formula.right]],
            branch_count=1,
            metadata={"rule": "wk3_conjunction", "original": str(formula)}
        )


class WK3DisjunctionRule(TableauRule):
    """WK3 rule for disjunction: A ∨ B → A | B"""
    
    @property
    def name(self) -> str:
        return "WK3 Disjunction Elimination"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.DISJUNCTION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is A ∨ B"""
        return isinstance(formula, Disjunction)
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply A ∨ B → A | B (same as classical)"""
        if not self.applies_to(formula):
            raise ValueError(f"WK3 disjunction rule does not apply to {formula}")
        
        return RuleApplication(
            formulas_for_branches=[[formula.left], [formula.right]],
            branch_count=2,
            metadata={"rule": "wk3_disjunction", "original": str(formula)}
        )


class WK3ImplicationRule(TableauRule):
    """WK3 rule for implication: A → B becomes ¬A | B"""
    
    @property
    def name(self) -> str:
        return "WK3 Implication Elimination"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.IMPLICATION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is A → B"""
        return isinstance(formula, Implication)
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply A → B → ¬A | B (same as classical)"""
        if not self.applies_to(formula):
            raise ValueError(f"WK3 implication rule does not apply to {formula}")
        
        neg_antecedent = Negation(formula.antecedent)
        
        return RuleApplication(
            formulas_for_branches=[[neg_antecedent], [formula.consequent]],
            branch_count=2,
            metadata={"rule": "wk3_implication", "original": str(formula)}
        )


class WK3NegatedConjunctionRule(TableauRule):
    """WK3 rule for negated conjunction: ¬(A ∧ B) → ¬A | ¬B"""
    
    @property
    def name(self) -> str:
        return "WK3 Negated Conjunction (De Morgan)"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.NEG_CONJUNCTION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is ¬(A ∧ B)"""
        return (isinstance(formula, Negation) and 
                isinstance(formula.operand, Conjunction))
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply ¬(A ∧ B) → ¬A | ¬B (same as classical)"""
        if not self.applies_to(formula):
            raise ValueError(f"WK3 negated conjunction rule does not apply to {formula}")
        
        conjunction = formula.operand
        neg_left = Negation(conjunction.left)
        neg_right = Negation(conjunction.right)
        
        return RuleApplication(
            formulas_for_branches=[[neg_left], [neg_right]],
            branch_count=2,
            metadata={"rule": "wk3_negated_conjunction", "original": str(formula)}
        )


class WK3NegatedDisjunctionRule(TableauRule):
    """WK3 rule for negated disjunction: ¬(A ∨ B) → ¬A, ¬B"""
    
    @property
    def name(self) -> str:
        return "WK3 Negated Disjunction (De Morgan)"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.NEG_DISJUNCTION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is ¬(A ∨ B)"""
        return (isinstance(formula, Negation) and 
                isinstance(formula.operand, Disjunction))
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply ¬(A ∨ B) → ¬A, ¬B (same as classical)"""
        if not self.applies_to(formula):
            raise ValueError(f"WK3 negated disjunction rule does not apply to {formula}")
        
        disjunction = formula.operand
        neg_left = Negation(disjunction.left)
        neg_right = Negation(disjunction.right)
        
        return RuleApplication(
            formulas_for_branches=[[neg_left, neg_right]],
            branch_count=1,
            metadata={"rule": "wk3_negated_disjunction", "original": str(formula)}
        )


class WK3NegatedImplicationRule(TableauRule):
    """WK3 rule for negated implication: ¬(A → B) → A, ¬B"""
    
    @property
    def name(self) -> str:
        return "WK3 Negated Implication"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.NEG_IMPLICATION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is ¬(A → B)"""
        return (isinstance(formula, Negation) and 
                isinstance(formula.operand, Implication))
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply ¬(A → B) → A, ¬B (same as classical)"""
        if not self.applies_to(formula):
            raise ValueError(f"WK3 negated implication rule does not apply to {formula}")
        
        implication = formula.operand
        antecedent = implication.antecedent
        neg_consequent = Negation(implication.consequent)
        
        return RuleApplication(
            formulas_for_branches=[[antecedent, neg_consequent]],
            branch_count=1,
            metadata={"rule": "wk3_negated_implication", "original": str(formula)}
        )


# Special WK3 rules for handling atoms/literals
class WK3AtomAssignmentRule(TableauRule):
    """
    WK3-specific rule for converting atoms to assignments.
    In WK3, atoms need to be converted to three-valued assignments.
    """
    
    @property
    def name(self) -> str:
        return "WK3 Atom Assignment"
    
    @property
    def rule_type(self) -> RuleType:
        # This is a special WK3 rule type, not in the standard classification
        return RuleType.DOUBLE_NEGATION  # Reuse existing type for priority
    
    @property
    def priority(self) -> int:
        # Give this rule very low priority so it only applies after all other rules
        return 10
    
    def applies_to(self, formula: Formula) -> bool:
        """Apply to positive atoms"""
        return isinstance(formula, Atom)
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Convert atom to three-valued assignment branches"""
        if not self.applies_to(formula):
            raise ValueError(f"WK3 atom assignment rule does not apply to {formula}")
        
        # In WK3 tableau, an atom A generates three branches: A=t, A=f, A=e
        # But we need to represent this differently since we're working with formulas
        # The WK3Branch will handle the actual assignment logic
        
        # For now, we don't expand atoms further - the WK3 components will handle this
        return RuleApplication(
            formulas_for_branches=[[formula]],  # Keep the atom as-is
            branch_count=1,
            metadata={
                "rule": "wk3_atom_assignment", 
                "original": str(formula),
                "requires_wk3_processing": True
            }
        )


class WK3NegatedAtomAssignmentRule(TableauRule):
    """WK3-specific rule for converting negated atoms to assignments"""
    
    @property
    def name(self) -> str:
        return "WK3 Negated Atom Assignment"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.DOUBLE_NEGATION  # Reuse for priority
    
    @property
    def priority(self) -> int:
        return 10  # Low priority
    
    def applies_to(self, formula: Formula) -> bool:
        """Apply to negated atoms"""
        return (isinstance(formula, Negation) and 
                isinstance(formula.operand, Atom))
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Convert negated atom to assignment"""
        if not self.applies_to(formula):
            raise ValueError(f"WK3 negated atom assignment rule does not apply to {formula}")
        
        # Similar to positive atoms, let WK3 components handle the assignment logic
        return RuleApplication(
            formulas_for_branches=[[formula]],
            branch_count=1,
            metadata={
                "rule": "wk3_negated_atom_assignment",
                "original": str(formula),
                "requires_wk3_processing": True
            }
        )


def get_wk3_rules() -> List[TableauRule]:
    """Get the complete set of WK3 tableau rules"""
    return [
        WK3DoubleNegationRule(),
        WK3ConjunctionRule(),
        WK3DisjunctionRule(),
        WK3ImplicationRule(),
        WK3NegatedConjunctionRule(),
        WK3NegatedDisjunctionRule(),
        WK3NegatedImplicationRule(),
        WK3AtomAssignmentRule(),
        WK3NegatedAtomAssignmentRule()
    ]


# Export rule classes and factory function
__all__ = [
    'WK3DoubleNegationRule',
    'WK3ConjunctionRule',
    'WK3DisjunctionRule', 
    'WK3ImplicationRule',
    'WK3NegatedConjunctionRule',
    'WK3NegatedDisjunctionRule',
    'WK3NegatedImplicationRule',
    'WK3AtomAssignmentRule',
    'WK3NegatedAtomAssignmentRule',
    'get_wk3_rules'
]