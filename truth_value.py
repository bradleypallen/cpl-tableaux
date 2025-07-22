#!/usr/bin/env python3
"""
Truth Value System for Weak Kleene Logic

Defines the three-valued truth system for weak Kleene logic with truth values:
- t (true)
- f (false) 
- e (undefined/gap)
"""

from enum import Enum
from typing import Union, Set, Tuple


class TruthValue(Enum):
    """Three-valued truth system for weak Kleene logic"""
    
    TRUE = 't'
    FALSE = 'f'
    UNDEFINED = 'e'
    
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
            'e': cls.UNDEFINED,
            'true': cls.TRUE,
            'false': cls.FALSE,
            'neither': cls.UNDEFINED,
            'undefined': cls.UNDEFINED,
            'gap': cls.UNDEFINED
        }
        
        normalized = value.lower().strip()
        if normalized in value_map:
            return value_map[normalized]
        else:
            raise ValueError(f"Invalid truth value: {value}")
    
    def to_bool(self) -> Union[bool, None]:
        """Convert to boolean (None for UNDEFINED)"""
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
e = TruthValue.UNDEFINED


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


class RestrictedQuantifierOperators:
    """Implementation of restricted Kleene quantifiers from Ferguson (2024)"""
    
    @staticmethod
    def restricted_existential(value_pairs: Set[Tuple[TruthValue, TruthValue]]) -> TruthValue:
        """
        Implement ∃̌(X) from Ferguson (2024) Definition 3
        
        For a nonempty set X ⊆ V₃²:
        ∃̌(X) = t  if ⟨t,t⟩ ∈ X
               e  if for all ⟨u,v⟩ ∈ X, either u = e or v = e  
               f  if ⟨t,t⟩ ∉ X and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e
        """
        if not value_pairs:
            raise ValueError("Empty set not allowed for restricted quantifiers")
        
        # Check if ⟨t,t⟩ ∈ X
        if (t, t) in value_pairs:
            return t
            
        # Check if for all ⟨u,v⟩ ∈ X, either u = e or v = e
        if all(u == e or v == e for u, v in value_pairs):
            return e
            
        # Otherwise: ⟨t,t⟩ ∉ X and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e
        return f
    
    @staticmethod
    def restricted_universal(value_pairs: Set[Tuple[TruthValue, TruthValue]]) -> TruthValue:
        """
        Implement ∀̌(X) from Ferguson (2024) Definition 3
        
        For a nonempty set X ⊆ V₃²:
        ∀̌(X) = t  if ⟨t,f⟩, ⟨t,e⟩ ∉ X and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e
               e  if for all ⟨u,v⟩ ∈ X, either u = e or v = e
               f  if {⟨t,f⟩, ⟨t,e⟩} ∩ X ≠ ∅ and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e  
        """
        if not value_pairs:
            raise ValueError("Empty set not allowed for restricted quantifiers")
            
        # Check if for all ⟨u,v⟩ ∈ X, either u = e or v = e
        if all(u == e or v == e for u, v in value_pairs):
            return e
            
        # Check if {⟨t,f⟩, ⟨t,e⟩} ∩ X ≠ ∅ and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e
        has_critical_pairs = (t, f) in value_pairs or (t, e) in value_pairs
        has_non_undefined_pair = any(u != e and v != e for u, v in value_pairs)
        
        if has_critical_pairs and has_non_undefined_pair:
            return f
            
        # Otherwise: ⟨t,f⟩, ⟨t,e⟩ ∉ X and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e  
        if has_non_undefined_pair:
            return t
            
        return e  # Fallback case


# Export commonly used items
__all__ = [
    'TruthValue', 't', 'f', 'e', 'WeakKleeneOperators', 'RestrictedQuantifierOperators'
]