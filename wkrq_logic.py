#!/usr/bin/env python3
"""
wKrQ Logic System - Weak Kleene Logic with Restricted Quantifiers

Complete implementation of the wKrQ logic system based on:
Ferguson, Thomas Macaulay. "Tableaux and restricted quantification for systems 
related to weak Kleene logic." In International Conference on Automated Reasoning 
with Analytic Tableaux and Related Methods, pp. 3-19. Cham: Springer International 
Publishing, 2021.
"""

from typing import List, Dict, Any
from logic_system import LogicSystem, LogicSystemConfig
from tableau_rules import TableauRule

# Import WK3 propositional rules
from wk3_rules import get_wk3_rules

# Import wKrQ-specific components
from wkrq_rules import RestrictedExistentialRule, RestrictedUniversalRule
from wkrq_components import (
    WKrQ_BranchFactory, 
    WKrQ_ClosureDetector, 
    WKrQ_ModelExtractor
)


def get_wkrq_rules() -> List[TableauRule]:
    """
    Get all tableau rules for wKrQ logic system.
    
    Combines:
    - WK3 propositional rules (inherited)
    - Restricted quantifier rules (new)
    """
    rules = []
    
    # Add all WK3 propositional rules
    rules.extend(get_wk3_rules())
    
    # Add wKrQ-specific quantifier rules
    rules.append(RestrictedExistentialRule())
    rules.append(RestrictedUniversalRule())
    
    return rules


def create_wkrq_components() -> Dict[str, Any]:
    """Create wKrQ-specific component implementations"""
    # Import WK3 components to inherit from them
    from wk3_components import create_wk3_components
    wk3_components = create_wk3_components()
    
    return {
        'branch_factory': WKrQ_BranchFactory(),
        'closure_detector': WKrQ_ClosureDetector(),
        'model_extractor': WKrQ_ModelExtractor(),
        'literal_recognizer': wk3_components['literal_recognizer'],  # Inherit from WK3
        'subsumption_detector': wk3_components['subsumption_detector']  # Inherit from WK3
    }


def create_wkrq_logic_system() -> LogicSystem:
    """
    Create the wKrQ (Weak Kleene Logic with Restricted Quantifiers) system.
    
    Based on Ferguson (2021) with:
    - Three-valued semantics {t, f, e}
    - Restricted quantifiers ∃̌ and ∀̌
    - First-order domain reasoning
    - Complete tableau calculus
    """
    
    config = LogicSystemConfig(
        name="Weak Kleene Logic with Restricted Quantifiers (wKrQ)",
        description="Three-valued first-order logic with restricted Kleene quantifiers ∃̌ and ∀̌",
        supports_quantifiers=True,
        supports_modality=False,
        truth_values=3,
        metadata={
            "aliases": ["wkrq", "wKrQ", "restricted-kleene", "fol-wk3"],
            "standard": False,
            "complete": True,
            "sound": True,
            "truth_values": ["t", "f", "e"],
            "quantifiers": ["∃̌", "∀̌"],
            "reference": "Ferguson (2021) 'Tableaux and restricted quantification for systems related to weak Kleene logic'",
            "domain_support": True,
            "witness_generation": True
        }
    )
    
    rules = get_wkrq_rules()
    components = create_wkrq_components()
    
    return LogicSystem(
        config=config,
        rules=rules,
        branch_factory=components['branch_factory'],
        closure_detector=components['closure_detector'],
        model_extractor=components['model_extractor'],
        literal_recognizer=components['literal_recognizer'],
        subsumption_detector=components['subsumption_detector']
    )


# Convenience functions for external use

def wkrq_tableau(formula):
    """
    Create a wKrQ tableau for the given formula.
    Convenience function for the componentized interface.
    """
    from componentized_tableau import ComponentizedTableau
    return ComponentizedTableau(formula, "wkrq")


def wkrq_satisfiable(formula) -> bool:
    """Check if formula is satisfiable in wKrQ logic"""
    tableau = wkrq_tableau(formula)
    return tableau.build()


def wkrq_models(formula):
    """Extract all wKrQ models that satisfy the formula"""
    tableau = wkrq_tableau(formula)
    if tableau.build():
        return tableau.extract_all_models()
    else:
        return []


# Export main functions
__all__ = [
    'create_wkrq_logic_system',
    'get_wkrq_rules',
    'create_wkrq_components', 
    'wkrq_tableau',
    'wkrq_satisfiable',
    'wkrq_models'
]