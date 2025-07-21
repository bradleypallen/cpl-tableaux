#!/usr/bin/env python3
"""
Logic Mode System for Tableaux Reasoner

Provides clear separation between propositional logic and first-order logic modes.
Each mode has its own syntax rules, validation, and formula construction.
"""

from enum import Enum, auto
from typing import Set, List, Optional, Union
from dataclasses import dataclass

class LogicMode(Enum):
    """Enumeration of supported logic modes"""
    PROPOSITIONAL = auto()  # Classical propositional logic
    FIRST_ORDER = auto()    # First-order predicate logic
    
    def __str__(self) -> str:
        return self.name.lower().replace('_', '-')
    
    @classmethod
    def from_string(cls, mode_str: str) -> 'LogicMode':
        """Parse LogicMode from string"""
        mode_str = mode_str.lower().strip()
        if mode_str in ('prop', 'propositional', 'cpl'):
            return cls.PROPOSITIONAL
        elif mode_str in ('fol', 'first-order', 'predicate'):
            return cls.FIRST_ORDER
        else:
            raise ValueError(f"Unknown logic mode: {mode_str}")


@dataclass
class ModeConfig:
    """Configuration for a specific logic mode"""
    mode: LogicMode
    allow_atoms: bool = True
    allow_predicates: bool = False  
    allow_variables: bool = False
    allow_quantifiers: bool = False
    
    # Naming conventions
    atom_case: Optional[str] = None  # 'lower', 'upper', or None (any)
    predicate_case: Optional[str] = None  # 'lower', 'upper', or None (any)
    constant_case: Optional[str] = None  # 'lower', 'upper', or None (any)  
    variable_case: Optional[str] = None  # 'lower', 'upper', or None (any)


# Predefined mode configurations
PROPOSITIONAL_CONFIG = ModeConfig(
    mode=LogicMode.PROPOSITIONAL,
    allow_atoms=True,
    allow_predicates=False,
    allow_variables=False,
    allow_quantifiers=False,
    atom_case='lower',  # p, q, r
)

FIRST_ORDER_CONFIG = ModeConfig(
    mode=LogicMode.FIRST_ORDER,
    allow_atoms=False,  # Use 0-ary predicates instead
    allow_predicates=True,
    allow_variables=False,  # Phase 1: ground formulas only
    allow_quantifiers=False,  # Phase 1: no quantifiers yet
    predicate_case='upper',  # P, Student, Mortal
    constant_case='lower',   # john, mary, c1
)

# Mode registry
MODE_CONFIGS = {
    LogicMode.PROPOSITIONAL: PROPOSITIONAL_CONFIG,
    LogicMode.FIRST_ORDER: FIRST_ORDER_CONFIG,
}


class ModeValidator:
    """Validates formulas and terms according to logic mode rules"""
    
    def __init__(self, config: ModeConfig):
        self.config = config
    
    def validate_atom_name(self, name: str) -> bool:
        """Validate atom name according to mode rules"""
        if not self.config.allow_atoms:
            return False
        
        if self.config.atom_case == 'lower':
            return name.islower() or name[0].islower()
        elif self.config.atom_case == 'upper':  
            return name.isupper() or name[0].isupper()
        else:
            return True  # Any case allowed
    
    def validate_predicate_name(self, name: str) -> bool:
        """Validate predicate name according to mode rules"""
        if not self.config.allow_predicates:
            return False
        
        if self.config.predicate_case == 'lower':
            return name.islower() or name[0].islower()
        elif self.config.predicate_case == 'upper':
            return name.isupper() or name[0].isupper()
        else:
            return True  # Any case allowed
    
    def validate_constant_name(self, name: str) -> bool:
        """Validate constant name according to mode rules"""
        if self.config.constant_case == 'lower':
            return name.islower() or name[0].islower()
        elif self.config.constant_case == 'upper':
            return name.isupper() or name[0].isupper()
        else:
            return True  # Any case allowed
    
    def validate_variable_name(self, name: str) -> bool:
        """Validate variable name according to mode rules"""
        if not self.config.allow_variables:
            return False
        
        if self.config.variable_case == 'lower':
            return name.islower() or name[0].islower()
        elif self.config.variable_case == 'upper':
            return name.isupper() or name[0].isupper()
        else:
            return True  # Any case allowed
    
    def get_syntax_description(self) -> str:
        """Get human-readable syntax description for this mode"""
        if self.config.mode == LogicMode.PROPOSITIONAL:
            return ("Propositional Logic Syntax:\n"
                   "- Atoms: lowercase letters (p, q, r, atom1)\n"
                   "- Operators: ∧ (and), ∨ (or), → (implies), ¬ (not)\n"
                   "- Example: (p ∧ q) → r")
        
        elif self.config.mode == LogicMode.FIRST_ORDER:
            return ("First-Order Logic Syntax:\n"
                   "- Predicates: uppercase names (P, Student, Loves)\n"
                   "- Constants: lowercase names (john, mary, c1)\n"
                   "- Ground formulas only (no variables yet)\n"
                   "- Example: Student(john) ∧ Loves(john, mary)")
        
        else:
            return f"Syntax for {self.config.mode}: Not yet defined"
    
    def get_error_suggestions(self, invalid_name: str, name_type: str) -> str:
        """Get helpful error suggestions for invalid names"""
        if self.config.mode == LogicMode.PROPOSITIONAL:
            if name_type == "atom":
                return f"Use lowercase for atoms: '{invalid_name.lower()}' instead of '{invalid_name}'"
        
        elif self.config.mode == LogicMode.FIRST_ORDER:
            if name_type == "predicate":
                return f"Use uppercase for predicates: '{invalid_name.capitalize()}' instead of '{invalid_name}'"
            elif name_type == "constant":
                return f"Use lowercase for constants: '{invalid_name.lower()}' instead of '{invalid_name}'"
            elif name_type == "variable":
                return "Variables not yet supported in ground formula mode"
        
        return f"Invalid {name_type} name: {invalid_name}"


class ModeError(Exception):
    """Exception raised when operations violate logic mode constraints"""
    
    def __init__(self, message: str, mode: LogicMode, suggestions: Optional[str] = None):
        super().__init__(message)
        self.mode = mode
        self.suggestions = suggestions
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.suggestions:
            return f"{base_msg}\n{self.suggestions}"
        return base_msg


def get_mode_config(mode: LogicMode) -> ModeConfig:
    """Get configuration for a specific logic mode"""
    return MODE_CONFIGS[mode]


def get_mode_validator(mode: LogicMode) -> ModeValidator:
    """Get validator for a specific logic mode"""
    config = get_mode_config(mode)
    return ModeValidator(config)


def detect_mode_from_syntax(formula_str: str) -> LogicMode:
    """
    Attempt to detect logic mode from formula syntax.
    This is a heuristic and may not always be accurate.
    """
    # Simple heuristics
    if '(' in formula_str and ')' in formula_str:
        # Likely contains predicate applications
        return LogicMode.FIRST_ORDER
    elif any(c.islower() for c in formula_str if c.isalpha()):
        # Contains lowercase letters - likely propositional
        return LogicMode.PROPOSITIONAL
    else:
        # Default to propositional for backward compatibility
        return LogicMode.PROPOSITIONAL


# Export commonly used items
__all__ = [
    'LogicMode', 'ModeConfig', 'ModeValidator', 'ModeError',
    'PROPOSITIONAL_CONFIG', 'FIRST_ORDER_CONFIG',
    'get_mode_config', 'get_mode_validator', 'detect_mode_from_syntax'
]