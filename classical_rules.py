#!/usr/bin/env python3
"""
Classical Logic Tableau Rules

Concrete implementations of tableau expansion rules for Classical Propositional Logic.
These rules implement the standard tableau method for two-valued logic.
"""

from typing import List
from tableau_rules import TableauRule, RuleType, RuleApplication, RuleContext
from formula import Formula, Negation, Conjunction, Disjunction, Implication, Atom


class DoubleNegationRule(TableauRule):
    """Rule for double negation elimination: ¬¬A → A"""
    
    @property
    def name(self) -> str:
        return "Double Negation Elimination"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.DOUBLE_NEGATION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is ¬¬A"""
        return (isinstance(formula, Negation) and 
                isinstance(formula.operand, Negation))
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply ¬¬A → A"""
        if not self.applies_to(formula):
            raise ValueError(f"Double negation rule does not apply to {formula}")
        
        # Extract A from ¬¬A
        inner_formula = formula.operand.operand  # ¬¬A → A
        
        return RuleApplication(
            formulas_for_branches=[[inner_formula]],
            branch_count=1,
            metadata={"rule": "double_negation", "original": str(formula)}
        )


class ConjunctionRule(TableauRule):
    """Rule for conjunction: A ∧ B → A, B"""
    
    @property
    def name(self) -> str:
        return "Conjunction Elimination"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.CONJUNCTION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is A ∧ B"""
        return isinstance(formula, Conjunction)
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply A ∧ B → A, B (same branch)"""
        if not self.applies_to(formula):
            raise ValueError(f"Conjunction rule does not apply to {formula}")
        
        # Both conjuncts go to the same branch
        return RuleApplication(
            formulas_for_branches=[[formula.left, formula.right]],
            branch_count=1,
            metadata={"rule": "conjunction", "original": str(formula)}
        )


class DisjunctionRule(TableauRule):
    """Rule for disjunction: A ∨ B → A | B"""
    
    @property
    def name(self) -> str:
        return "Disjunction Elimination" 
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.DISJUNCTION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is A ∨ B"""
        return isinstance(formula, Disjunction)
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply A ∨ B → A | B (branching)"""
        if not self.applies_to(formula):
            raise ValueError(f"Disjunction rule does not apply to {formula}")
        
        # Each disjunct goes to a separate branch
        return RuleApplication(
            formulas_for_branches=[[formula.left], [formula.right]],
            branch_count=2,
            metadata={"rule": "disjunction", "original": str(formula)}
        )


class ImplicationRule(TableauRule):
    """Rule for implication: A → B becomes ¬A | B"""
    
    @property
    def name(self) -> str:
        return "Implication Elimination"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.IMPLICATION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is A → B"""
        return isinstance(formula, Implication)
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply A → B → ¬A | B (branching)"""
        if not self.applies_to(formula):
            raise ValueError(f"Implication rule does not apply to {formula}")
        
        # A → B becomes ¬A | B, so we branch on ¬A and B
        neg_antecedent = Negation(formula.antecedent)
        
        return RuleApplication(
            formulas_for_branches=[[neg_antecedent], [formula.consequent]],
            branch_count=2,
            metadata={"rule": "implication", "original": str(formula)}
        )


class NegatedConjunctionRule(TableauRule):
    """Rule for negated conjunction: ¬(A ∧ B) → ¬A | ¬B"""
    
    @property
    def name(self) -> str:
        return "Negated Conjunction (De Morgan)"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.NEG_CONJUNCTION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is ¬(A ∧ B)"""
        return (isinstance(formula, Negation) and 
                isinstance(formula.operand, Conjunction))
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply ¬(A ∧ B) → ¬A | ¬B (branching)"""
        if not self.applies_to(formula):
            raise ValueError(f"Negated conjunction rule does not apply to {formula}")
        
        conjunction = formula.operand
        neg_left = Negation(conjunction.left)
        neg_right = Negation(conjunction.right)
        
        return RuleApplication(
            formulas_for_branches=[[neg_left], [neg_right]],
            branch_count=2,
            metadata={"rule": "negated_conjunction", "original": str(formula)}
        )


class NegatedDisjunctionRule(TableauRule):
    """Rule for negated disjunction: ¬(A ∨ B) → ¬A, ¬B"""
    
    @property
    def name(self) -> str:
        return "Negated Disjunction (De Morgan)"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.NEG_DISJUNCTION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is ¬(A ∨ B)"""
        return (isinstance(formula, Negation) and 
                isinstance(formula.operand, Disjunction))
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply ¬(A ∨ B) → ¬A, ¬B (same branch)"""
        if not self.applies_to(formula):
            raise ValueError(f"Negated disjunction rule does not apply to {formula}")
        
        disjunction = formula.operand
        neg_left = Negation(disjunction.left)
        neg_right = Negation(disjunction.right)
        
        return RuleApplication(
            formulas_for_branches=[[neg_left, neg_right]],
            branch_count=1,
            metadata={"rule": "negated_disjunction", "original": str(formula)}
        )


class NegatedImplicationRule(TableauRule):
    """Rule for negated implication: ¬(A → B) → A, ¬B"""
    
    @property
    def name(self) -> str:
        return "Negated Implication"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.NEG_IMPLICATION
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if formula is ¬(A → B)"""
        return (isinstance(formula, Negation) and 
                isinstance(formula.operand, Implication))
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply ¬(A → B) → A, ¬B (same branch)"""
        if not self.applies_to(formula):
            raise ValueError(f"Negated implication rule does not apply to {formula}")
        
        implication = formula.operand
        antecedent = implication.antecedent
        neg_consequent = Negation(implication.consequent)
        
        return RuleApplication(
            formulas_for_branches=[[antecedent, neg_consequent]],
            branch_count=1,
            metadata={"rule": "negated_implication", "original": str(formula)}
        )


def get_classical_rules() -> List[TableauRule]:
    """Get the complete set of classical propositional logic tableau rules"""
    return [
        DoubleNegationRule(),
        ConjunctionRule(),
        DisjunctionRule(), 
        ImplicationRule(),
        NegatedConjunctionRule(),
        NegatedDisjunctionRule(),
        NegatedImplicationRule()
    ]


# Export rule classes and factory function
__all__ = [
    'DoubleNegationRule',
    'ConjunctionRule', 
    'DisjunctionRule',
    'ImplicationRule',
    'NegatedConjunctionRule',
    'NegatedDisjunctionRule',
    'NegatedImplicationRule',
    'get_classical_rules'
]