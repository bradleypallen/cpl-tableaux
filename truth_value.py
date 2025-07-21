#!/usr/bin/env python3
"""
Truth Value System for Weak Kleene Logic

Defines the three-valued truth system for weak Kleene logic with truth values:
- t (true)
- f (false) 
- e (neither/undefined/gap)
"""

from enum import Enum
from typing import Union


class TruthValue(Enum):
    """Three-valued truth system for weak Kleene logic"""
    
    TRUE = 't'
    FALSE = 'f'
    NEITHER = 'e'
    
    def __str__(self) -> str:
        """String representation using lowercase letters"""
        return self.value
    
    def __repr__(self) -> str:
        """Detailed representation for debugging"""
        return f"TruthValue.{self.name}"
    
    @classmethod
    def from_bool(cls, value: bool) -> 'TruthValue':
        """Convert boolean to TruthValue (for classical logic compatibility)"""
        return cls.TRUE if value else cls.FALSE
    
    @classmethod
    def from_string(cls, value: str) -> 'TruthValue':
        """Parse TruthValue from string representation"""
        value_map = {
            't': cls.TRUE,
            'f': cls.FALSE,
            'e': cls.NEITHER,
            'true': cls.TRUE,
            'false': cls.FALSE,
            'neither': cls.NEITHER,
            'undefined': cls.NEITHER,
            'gap': cls.NEITHER
        }
        
        normalized = value.lower().strip()
        if normalized in value_map:
            return value_map[normalized]
        else:
            raise ValueError(f"Invalid truth value: {value}")
    
    def to_bool(self) -> Union[bool, None]:
        """Convert to boolean (None for NEITHER)"""
        if self == TruthValue.TRUE:
            return True
        elif self == TruthValue.FALSE:
            return False
        else:
            return None
    
    def is_classical(self) -> bool:
        """Check if this is a classical (true/false) value"""
        return self in (TruthValue.TRUE, TruthValue.FALSE)


# Convenience aliases
t = TruthValue.TRUE
f = TruthValue.FALSE
e = TruthValue.NEITHER


class WeakKleeneOperators:
    """Implementation of weak Kleene logic truth tables"""
    
    @staticmethod
    def negation(a: TruthValue) -> TruthValue:
        """Weak Kleene negation: ¬A"""
        if a == t:
            return f
        elif a == f:
            return t
        else:  # a == e
            return e
    
    @staticmethod
    def conjunction(a: TruthValue, b: TruthValue) -> TruthValue:
        """Weak Kleene conjunction: A ∧ B"""
        # In weak Kleene, any operation with 'e' returns 'e'
        if a == e or b == e:
            return e
        # If both are true, result is true
        elif a == t and b == t:
            return t
        # Otherwise (at least one is false), result is false
        else:
            return f
    
    @staticmethod
    def disjunction(a: TruthValue, b: TruthValue) -> TruthValue:
        """Weak Kleene disjunction: A ∨ B"""
        # In weak Kleene, any operation with 'e' returns 'e'
        if a == e or b == e:
            return e
        # If either operand is true, result is true
        elif a == t or b == t:
            return t
        # Otherwise (both are false), result is false
        else:
            return f
    
    @staticmethod
    def implication(a: TruthValue, b: TruthValue) -> TruthValue:
        """Weak Kleene implication: A → B"""
        # In weak Kleene, any operation with 'e' returns 'e'
        if a == e or b == e:
            return e
        # If antecedent is false, result is true
        elif a == f:
            return t
        # If antecedent is true and consequent is true, result is true
        elif a == t and b == t:
            return t
        # If antecedent is true and consequent is false, result is false
        elif a == t and b == f:
            return f
        else:
            return e  # Should not reach here
    
    @staticmethod
    def biconditional(a: TruthValue, b: TruthValue) -> TruthValue:
        """Weak Kleene biconditional: A ↔ B (derived from (A → B) ∧ (B → A))"""
        left = WeakKleeneOperators.implication(a, b)
        right = WeakKleeneOperators.implication(b, a)
        return WeakKleeneOperators.conjunction(left, right)


# Export commonly used items
__all__ = [
    'TruthValue', 't', 'f', 'e', 'WeakKleeneOperators'
]