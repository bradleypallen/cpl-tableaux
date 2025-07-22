#!/usr/bin/env python3
"""
Built-in Logic Systems

Defines and registers the standard logic systems supported by the tableau framework:
- Classical Propositional Logic (CPL)
- Weak Kleene Logic (WK3)
- Extension points for future logics
"""

from logic_system import LogicSystem, LogicSystemConfig, register_logic_system
from classical_rules import get_classical_rules
from classical_components import create_classical_components
from wk3_rules import get_wk3_rules
from wk3_components import create_wk3_components
from wkrq_logic import create_wkrq_logic_system


def create_classical_logic_system() -> LogicSystem:
    """Create the Classical Propositional Logic system"""
    
    config = LogicSystemConfig(
        name="Classical Propositional Logic",
        description="Two-valued logic with truth values {true, false}",
        supports_quantifiers=False,
        supports_modality=False,
        truth_values=2,
        metadata={
            "aliases": ["CPL", "classical", "prop"],
            "standard": True,
            "complete": True,
            "sound": True
        }
    )
    
    rules = get_classical_rules()
    components = create_classical_components()
    
    return LogicSystem(
        config=config,
        rules=rules,
        branch_factory=components['branch_factory'],
        closure_detector=components['closure_detector'],
        model_extractor=components['model_extractor'],
        literal_recognizer=components['literal_recognizer'],
        subsumption_detector=components['subsumption_detector']
    )


def create_wk3_logic_system() -> LogicSystem:
    """Create the Weak Kleene Logic (WK3) system"""
    
    config = LogicSystemConfig(
        name="Weak Kleene Logic",
        description="Three-valued logic with truth values {true, false, undefined}",
        supports_quantifiers=False,
        supports_modality=False,
        truth_values=3,
        metadata={
            "aliases": ["WK3", "wk3", "weak-kleene"],
            "standard": True,
            "complete": True,
            "sound": True,
            "truth_values": ["t", "f", "e"]
        }
    )
    
    rules = get_wk3_rules()
    components = create_wk3_components()
    
    return LogicSystem(
        config=config,
        rules=rules,
        branch_factory=components['branch_factory'],
        closure_detector=components['closure_detector'],
        model_extractor=components['model_extractor'],
        literal_recognizer=components['literal_recognizer'],
        subsumption_detector=components['subsumption_detector']
    )


def register_builtin_logics():
    """Register all built-in logic systems"""
    
    # Register Classical Logic with multiple aliases
    classical_system = create_classical_logic_system()
    register_logic_system("classical", classical_system)
    register_logic_system("CPL", classical_system)
    register_logic_system("prop", classical_system)
    register_logic_system("propositional", classical_system)
    
    # Register WK3 Logic with multiple aliases
    wk3_system = create_wk3_logic_system()
    register_logic_system("wk3", wk3_system)
    register_logic_system("WK3", wk3_system)
    register_logic_system("weak-kleene", wk3_system)
    register_logic_system("weak_kleene", wk3_system)
    
    # Register wKrQ Logic with multiple aliases
    wkrq_system = create_wkrq_logic_system()
    register_logic_system("wkrq", wkrq_system)
    register_logic_system("wKrQ", wkrq_system)
    register_logic_system("restricted-kleene", wkrq_system)
    register_logic_system("fol-wk3", wkrq_system)


# Framework for future logic extensions

def create_fde_logic_system() -> LogicSystem:
    """
    Placeholder for First-Degree Entailment (FDE) - four-valued logic.
    This demonstrates how new logics can be added to the framework.
    """
    config = LogicSystemConfig(
        name="First-Degree Entailment",
        description="Four-valued logic with values {true, false, both, neither}",
        supports_quantifiers=False,
        supports_modality=False,
        truth_values=4,
        metadata={
            "aliases": ["FDE", "fde"],
            "standard": False,
            "complete": True,
            "sound": True,
            "status": "placeholder",
            "truth_values": ["t", "f", "b", "n"]
        }
    )
    
    # For now, use classical components as placeholder
    # In a real implementation, we'd create FDE-specific rules and components
    rules = get_classical_rules()  # Placeholder
    components = create_classical_components()  # Placeholder
    
    return LogicSystem(
        config=config,
        rules=rules,
        branch_factory=components['branch_factory'],
        closure_detector=components['closure_detector'],
        model_extractor=components['model_extractor'],
        literal_recognizer=components['literal_recognizer'],
        subsumption_detector=components['subsumption_detector']
    )


def create_modal_logic_system() -> LogicSystem:
    """
    Placeholder for Modal Logic (K, T, S4, S5).
    This demonstrates extension points for modal reasoning.
    """
    config = LogicSystemConfig(
        name="Modal Logic K",
        description="Basic modal logic with necessity and possibility operators",
        supports_quantifiers=False,
        supports_modality=True,
        truth_values=2,
        metadata={
            "aliases": ["modal", "K"],
            "standard": False,
            "complete": True,
            "sound": True,
            "status": "placeholder",
            "operators": ["□", "◊"]
        }
    )
    
    # Placeholder implementation
    rules = get_classical_rules()
    components = create_classical_components()
    
    return LogicSystem(
        config=config,
        rules=rules,
        branch_factory=components['branch_factory'],
        closure_detector=components['closure_detector'],
        model_extractor=components['model_extractor'],
        literal_recognizer=components['literal_recognizer'],
        subsumption_detector=components['subsumption_detector']
    )


def register_experimental_logics():
    """Register experimental/placeholder logic systems for development"""
    
    # These are placeholders to demonstrate extensibility
    # register_logic_system("fde", create_fde_logic_system())
    # register_logic_system("modal", create_modal_logic_system())
    pass


# Validation and utility functions

def validate_all_builtin_logics():
    """Validate all built-in logic systems for completeness"""
    from logic_system import list_logic_systems, get_logic_system
    
    validation_results = {}
    
    for logic_name in list_logic_systems():
        system = get_logic_system(logic_name)
        if system:
            warnings = system.validate_completeness()
            validation_results[logic_name] = warnings
    
    return validation_results


def describe_all_logics():
    """Get descriptions of all registered logic systems"""
    from logic_system import list_logic_systems, get_logic_system
    
    descriptions = []
    
    for logic_name in sorted(list_logic_systems()):
        system = get_logic_system(logic_name)
        if system:
            descriptions.append(f"\n{logic_name}:")
            descriptions.append(system.describe())
            descriptions.append("-" * 60)
    
    return "\n".join(descriptions)


# Initialize built-in logics when module is imported
def initialize():
    """Initialize the built-in logic systems"""
    register_builtin_logics()
    register_experimental_logics()


# Export main functions
__all__ = [
    'create_classical_logic_system',
    'create_wk3_logic_system',
    'create_wkrq_logic_system',
    'register_builtin_logics',
    'validate_all_builtin_logics',
    'describe_all_logics',
    'initialize'
]


# Auto-initialize when imported
initialize()