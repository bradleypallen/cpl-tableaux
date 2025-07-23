#!/usr/bin/env python3
"""
Signed Formula System for Multi-Valued Tableaux

Implements the standard signed formula approach used in tableau literature
for many-valued logics, following Smullyan's unified notation and extending
to multi-valued signs as found in Priest, Fitting, and other tableau texts.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import copy

from formula import Formula
from truth_value import TruthValue, t, f, e


class Sign(ABC):
    """Abstract base class for tableau signs"""
    
    @abstractmethod
    def __str__(self) -> str:
        """String representation of the sign"""
        pass
    
    @abstractmethod
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        """Hash for use in sets/dicts"""
        pass
    
    @abstractmethod
    def is_contradictory_with(self, other: 'Sign') -> bool:
        """Check if this sign contradicts another sign for closure detection"""
        pass
    
    @abstractmethod
    def get_truth_value(self) -> Optional[TruthValue]:
        """Get the truth value this sign represents (if applicable)"""
        pass


class ClassicalSign(Sign):
    """Classical two-valued signs: T (true) and F (false)"""
    
    def __init__(self, value: bool):
        self.value = value
    
    def __str__(self) -> str:
        return "T" if self.value else "F"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, ClassicalSign) and self.value == other.value
    
    def __hash__(self) -> int:
        return hash(("classical", self.value))
    
    def is_contradictory_with(self, other: 'Sign') -> bool:
        """T and F are contradictory"""
        return isinstance(other, ClassicalSign) and self.value != other.value
    
    def get_truth_value(self) -> TruthValue:
        return t if self.value else f


class ThreeValuedSign(Sign):
    """Three-valued signs: T (true), F (false), U (undefined/unknown)"""
    
    def __init__(self, value: TruthValue):
        if value not in {t, f, e}:
            raise ValueError(f"Invalid three-valued sign: {value}")
        self.value = value
    
    def __str__(self) -> str:
        if self.value == t:
            return "T"
        elif self.value == f:
            return "F"
        elif self.value == e:
            return "U"  # U for undefined/unknown (standard notation)
        else:
            raise ValueError(f"Unknown truth value: {self.value}")
    
    def __eq__(self, other) -> bool:
        return isinstance(other, ThreeValuedSign) and self.value == other.value
    
    def __hash__(self) -> int:
        return hash(("three_valued", self.value))
    
    def is_contradictory_with(self, other: 'Sign') -> bool:
        """
        Three-valued closure rules:
        - T and F are contradictory (classical)
        - T and U are NOT contradictory 
        - F and U are NOT contradictory
        - U and U are NOT contradictory
        
        This follows Priest's "Introduction to Non-Classical Logic"
        """
        if not isinstance(other, ThreeValuedSign):
            return False
        return (self.value == t and other.value == f) or (self.value == f and other.value == t)
    
    def get_truth_value(self) -> TruthValue:
        return self.value


class FourValuedSign(Sign):
    """Four-valued signs for First-Degree Entailment: T, F, B (both), N (neither)"""
    
    def __init__(self, designation: str):
        if designation not in {"T", "F", "B", "N"}:
            raise ValueError(f"Invalid four-valued sign: {designation}")
        self.designation = designation
    
    def __str__(self) -> str:
        return self.designation
    
    def __eq__(self, other) -> bool:
        return isinstance(other, FourValuedSign) and self.designation == other.designation
    
    def __hash__(self) -> int:
        return hash(("four_valued", self.designation))
    
    def is_contradictory_with(self, other: 'Sign') -> bool:
        """
        FDE closure rules (simplified):
        - T and F remain contradictory
        - B (both) is contradictory with N (neither)
        - Other combinations require more complex rules
        """
        if not isinstance(other, FourValuedSign):
            return False
        contradictory_pairs = {("T", "F"), ("F", "T"), ("B", "N"), ("N", "B")}
        return (self.designation, other.designation) in contradictory_pairs
    
    def get_truth_value(self) -> Optional[TruthValue]:
        """FDE doesn't map directly to TruthValue - return None"""
        return None


@dataclass(frozen=True)
class SignedFormula:
    """
    A signed formula: Sign:Formula
    
    This is the standard representation in tableau literature.
    Examples: T:p, F:(p∧q), U:¬r
    """
    sign: Sign
    formula: Formula
    
    def __str__(self) -> str:
        return f"{self.sign}:{self.formula}"
    
    def __repr__(self) -> str:
        return f"SignedFormula({self.sign}, {self.formula})"
    
    def is_contradictory_with(self, other: 'SignedFormula') -> bool:
        """
        Check if this signed formula contradicts another.
        Standard rule: Same formula with contradictory signs.
        """
        return (self.formula == other.formula and 
                self.sign.is_contradictory_with(other.sign))
    
    def is_atomic(self) -> bool:
        """Check if this is a signed atomic formula"""
        return self.formula.is_atomic()
    
    def is_literal(self) -> bool:
        """Check if this is a signed literal (atom or negated atom)"""
        return self.formula.is_literal()
    
    def get_complexity(self) -> int:
        """Get formula complexity for prioritization"""
        return self.formula.get_complexity()


class SignRegistry:
    """Registry for managing different sign systems"""
    
    _sign_systems: Dict[str, Any] = {}
    
    @classmethod
    def register_sign_system(cls, name: str, sign_class: type, 
                           create_signs_func: callable) -> None:
        """Register a new sign system"""
        cls._sign_systems[name] = {
            'sign_class': sign_class,
            'create_signs': create_signs_func
        }
    
    @classmethod
    def get_signs(cls, system_name: str) -> List[Sign]:
        """Get all signs for a given system"""
        if system_name not in cls._sign_systems:
            raise ValueError(f"Unknown sign system: {system_name}")
        return cls._sign_systems[system_name]['create_signs']()
    
    @classmethod
    def get_sign_class(cls, system_name: str) -> type:
        """Get the sign class for a system"""
        if system_name not in cls._sign_systems:
            raise ValueError(f"Unknown sign system: {system_name}")
        return cls._sign_systems[system_name]['sign_class']


# Register built-in sign systems
def _create_classical_signs() -> List[Sign]:
    """Create classical T/F signs"""
    return [ClassicalSign(True), ClassicalSign(False)]

def _create_three_valued_signs() -> List[Sign]:
    """Create three-valued T/F/U signs"""  
    return [ThreeValuedSign(t), ThreeValuedSign(f), ThreeValuedSign(e)]

def _create_four_valued_signs() -> List[Sign]:
    """Create four-valued T/F/B/N signs"""
    return [FourValuedSign(d) for d in ["T", "F", "B", "N"]]

SignRegistry.register_sign_system("classical", ClassicalSign, _create_classical_signs)
SignRegistry.register_sign_system("three_valued", ThreeValuedSign, _create_three_valued_signs)
SignRegistry.register_sign_system("four_valued", FourValuedSign, _create_four_valued_signs)


# Convenience functions for creating signed formulas
def T(formula: Formula) -> SignedFormula:
    """Create T:formula (true signed formula)"""
    return SignedFormula(ClassicalSign(True), formula)

def F(formula: Formula) -> SignedFormula:
    """Create F:formula (false signed formula)"""
    return SignedFormula(ClassicalSign(False), formula)

def U(formula: Formula) -> SignedFormula:
    """Create U:formula (undefined signed formula)"""
    return SignedFormula(ThreeValuedSign(e), formula)

def T3(formula: Formula) -> SignedFormula:
    """Create T:formula for three-valued logic"""
    return SignedFormula(ThreeValuedSign(t), formula)

def F3(formula: Formula) -> SignedFormula:
    """Create F:formula for three-valued logic"""
    return SignedFormula(ThreeValuedSign(f), formula)


# Export main classes and functions
__all__ = [
    'Sign', 'ClassicalSign', 'ThreeValuedSign', 'FourValuedSign',
    'SignedFormula', 'SignRegistry',
    'T', 'F', 'U', 'T3', 'F3'
]