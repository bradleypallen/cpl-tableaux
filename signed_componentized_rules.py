#!/usr/bin/env python3
"""
Signed Componentized Rules

Adapts signed tableau rules to work with the componentized architecture.
Bridges the signed tableau rule system with the abstract TableauRule interface.
"""

from typing import List, Optional, Union
from enum import Enum

from formula import Formula, RuleType
from tableau_rules import TableauRule, RuleContext, RuleApplication
from signed_formula import SignedFormula, T, F, T3, F3, U
from signed_tableau_rules import SignedRuleRegistry as SignedRuleRegistryCore, SignedTableauRule, SignedRuleResult
from signed_components import SignedBranchAdapter


class SignedRuleAdapter(TableauRule):
    """
    Adapter that wraps a SignedTableauRule to work with the componentized architecture.
    Converts between Formula/BranchInterface and SignedFormula/SignedBranch.
    """
    
    def __init__(self, signed_rule: SignedTableauRule, sign_system: str = "classical"):
        self.signed_rule = signed_rule
        self.sign_system = sign_system
        self._rule_type = self._convert_rule_type()
    
    def _convert_rule_type(self) -> RuleType:
        """Convert signed rule type to componentized rule type"""
        # Map signed rule types to existing RuleType enum values
        mapping = {
            "T∧": RuleType.CONJUNCTION,
            "F∧": RuleType.NEG_CONJUNCTION,
            "T∨": RuleType.DISJUNCTION,
            "F∨": RuleType.NEG_DISJUNCTION,
            "T→": RuleType.IMPLICATION,
            "F→": RuleType.NEG_IMPLICATION,
            "T¬": RuleType.DOUBLE_NEGATION,  # Close enough
            "F¬": RuleType.DOUBLE_NEGATION,
            "T¬¬": RuleType.DOUBLE_NEGATION,
            "F¬¬": RuleType.DOUBLE_NEGATION,
        }
        
        rule_type_str = str(self.signed_rule.rule_type.value)
        return mapping.get(rule_type_str, RuleType.CONJUNCTION)  # Default fallback
    
    @property
    def name(self) -> str:
        """Human-readable name for this rule"""
        return f"Signed({self.signed_rule.name})"
    
    @property
    def rule_type(self) -> RuleType:
        return self._rule_type
    
    @property
    def is_alpha_rule(self) -> bool:
        return self.signed_rule.is_alpha_rule()
    
    @property
    def is_beta_rule(self) -> bool:
        return self.signed_rule.is_beta_rule()
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if this rule applies to a formula"""
        # Convert formula to signed formula and test
        signed_formula = self._formula_to_signed(formula)
        return self.signed_rule.applies_to(signed_formula)
    
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply the rule to a formula in the given context"""
        # Convert formula to signed formula
        signed_formula = self._formula_to_signed(formula)
        
        # Apply the signed rule
        signed_result = self.signed_rule.apply(signed_formula)
        
        # Convert result back to componentized format
        return self._convert_result(signed_result, context)
    
    def _formula_to_signed(self, formula: Formula) -> SignedFormula:
        """Convert a Formula to a SignedFormula (default to T:formula)"""
        if self.sign_system == "classical":
            return T(formula)
        elif self.sign_system == "three_valued":
            return T3(formula)
        else:
            return T(formula)
    
    def _convert_result(self, signed_result: SignedRuleResult, context: RuleContext) -> RuleApplication:
        """Convert SignedRuleResult to RuleResult"""
        branch_count = signed_result.branch_count
        formulas_for_branches = []
        
        for signed_branch_formulas in signed_result.branches:
            # Convert signed formulas back to formulas
            branch_formulas = [sf.formula for sf in signed_branch_formulas]
            formulas_for_branches.append(branch_formulas)
        
        return RuleApplication(
            branch_count=branch_count,
            formulas_for_branches=formulas_for_branches
        )


class SignedRuleRegistry:
    """Registry that provides signed rules as componentized rules"""
    
    def __init__(self, sign_system: str = "classical"):
        self.sign_system = sign_system
        self.signed_registry = SignedRuleRegistryCore()
        self._rule_cache = {}
    
    def get_rules(self) -> List[TableauRule]:
        """Get all rules as componentized TableauRule objects"""
        if self.sign_system not in self._rule_cache:
            adapted_rules = []
            
            for signed_rule in self.signed_registry.rules:
                # Only include rules that work with this sign system
                if self.sign_system in signed_rule.sign_systems:
                    adapted_rule = SignedRuleAdapter(signed_rule, self.sign_system)
                    adapted_rules.append(adapted_rule)
            
            self._rule_cache[self.sign_system] = adapted_rules
        
        return self._rule_cache[self.sign_system]
    
    def find_applicable_rules(self, formula: Formula) -> List[TableauRule]:
        """Find rules applicable to a formula"""
        applicable = []
        
        for rule in self.get_rules():
            if rule.applies_to(formula):
                applicable.append(rule)
        
        return applicable
    
    def get_best_rule(self, formula: Formula) -> Optional[TableauRule]:
        """Get the best rule for a formula (α-rules prioritized)"""
        applicable = self.find_applicable_rules(formula)
        if not applicable:
            return None
        
        # Sort by priority: α-rules (priority 1) before β-rules (priority 2)
        return min(applicable, key=lambda r: 1 if r.is_alpha_rule else 2)


def get_classical_signed_rules() -> List[TableauRule]:
    """Get classical signed tableau rules as componentized rules"""
    registry = SignedRuleRegistry("classical")
    return registry.get_rules()


def get_three_valued_signed_rules() -> List[TableauRule]:
    """Get three-valued signed tableau rules as componentized rules"""
    registry = SignedRuleRegistry("three_valued")
    return registry.get_rules()


def get_signed_rules(sign_system: str) -> List[TableauRule]:
    """Get signed tableau rules for any sign system"""
    registry = SignedRuleRegistry(sign_system)
    return registry.get_rules()


# Enhanced rule creation for specific use cases

def create_signed_wk3_rules() -> List[TableauRule]:
    """Create WK3-specific signed tableau rules"""
    # WK3 uses three-valued signs but may need custom rule priorities
    return get_three_valued_signed_rules()


def create_hybrid_signed_rules(base_system: str, extensions: List[str] = None) -> List[TableauRule]:
    """Create hybrid rule sets combining multiple sign systems"""
    base_rules = get_signed_rules(base_system)
    
    if extensions:
        for ext_system in extensions:
            ext_rules = get_signed_rules(ext_system)
            # Add non-duplicate rules
            for rule in ext_rules:
                if not any(r.rule_type == rule.rule_type for r in base_rules):
                    base_rules.append(rule)
    
    return base_rules


# Export main classes and functions
__all__ = [
    'SignedRuleAdapter', 'SignedRuleRegistry',
    'get_classical_signed_rules', 'get_three_valued_signed_rules', 'get_signed_rules',
    'create_signed_wk3_rules', 'create_hybrid_signed_rules'
]