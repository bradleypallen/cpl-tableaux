#!/usr/bin/env python3
"""
Abstract sign system for tableau methods.

This module provides the sign system abstraction that allows different logics
to define their own signed formula notation (e.g., T/F for classical, 
T/F/U for three-valued, T/F/M/N for epistemic, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Set, Dict, Optional, List
from dataclasses import dataclass

from .formula import Formula
from .semantics import TruthValue


class Sign(ABC):
    """Abstract base class for signs in tableau systems."""
    
    @abstractmethod
    def __str__(self) -> str:
        """String representation of the sign."""
        pass
    
    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Check equality with another sign."""
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        pass
    
    @abstractmethod
    def is_contradictory_with(self, other: 'Sign') -> bool:
        """Check if this sign contradicts another sign."""
        pass
    
    @abstractmethod
    def get_symbol(self) -> str:
        """Get the symbol representing this sign."""
        pass


@dataclass(frozen=True)
class SignedFormula:
    """A formula with a sign attached."""
    sign: Sign
    formula: Formula
    
    def __str__(self) -> str:
        return f"{self.sign}:{self.formula}"
    
    def __hash__(self) -> int:
        return hash((self.sign, self.formula))


class SignSystem(ABC):
    """Abstract base class for sign systems."""
    
    @abstractmethod
    def signs(self) -> Set[Sign]:
        """Return all signs in this system."""
        pass
    
    @abstractmethod
    def truth_conditions(self, sign: Sign) -> Set[TruthValue]:
        """Return the truth values that satisfy this sign."""
        pass
    
    @abstractmethod
    def sign_for_truth_value(self, value: TruthValue) -> Sign:
        """Return the sign corresponding to a truth value."""
        pass
    
    def find_contradictions(self, signed_formulas: List[SignedFormula]) -> List[tuple]:
        """Find all contradictory pairs in a list of signed formulas."""
        contradictions = []
        for i, sf1 in enumerate(signed_formulas):
            for j, sf2 in enumerate(signed_formulas[i+1:], i+1):
                if (sf1.formula == sf2.formula and 
                    sf1.sign.is_contradictory_with(sf2.sign)):
                    contradictions.append((sf1, sf2))
        return contradictions


class ClassicalSign(Sign):
    """Signs for classical logic (T/F)."""
    
    def __init__(self, polarity: bool):
        self.polarity = polarity  # True for T, False for F
    
    def __str__(self) -> str:
        return "T" if self.polarity else "F"
    
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ClassicalSign) and self.polarity == other.polarity
    
    def __hash__(self) -> int:
        return hash(("classical", self.polarity))
    
    def is_contradictory_with(self, other: Sign) -> bool:
        if not isinstance(other, ClassicalSign):
            return False
        return self.polarity != other.polarity
    
    def get_symbol(self) -> str:
        return "T" if self.polarity else "F"


class ThreeValuedSign(Sign):
    """Signs for three-valued logic (T/F/U)."""
    
    def __init__(self, value: str):
        if value not in ["T", "F", "U"]:
            raise ValueError(f"Invalid three-valued sign: {value}")
        self.value = value
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ThreeValuedSign) and self.value == other.value
    
    def __hash__(self) -> int:
        return hash(("three-valued", self.value))
    
    def is_contradictory_with(self, other: Sign) -> bool:
        if not isinstance(other, ThreeValuedSign):
            return False
        # In three-valued logic, only T and F contradict
        return (self.value == "T" and other.value == "F") or \
               (self.value == "F" and other.value == "T")
    
    def get_symbol(self) -> str:
        return self.value


class FourValuedSign(Sign):
    """Signs for four-valued logic (e.g., T/F/M/N for wKrQ)."""
    
    def __init__(self, value: str):
        if value not in ["T", "F", "M", "N"]:
            raise ValueError(f"Invalid four-valued sign: {value}")
        self.value = value
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, FourValuedSign) and self.value == other.value
    
    def __hash__(self) -> int:
        return hash(("four-valued", self.value))
    
    def is_contradictory_with(self, other: Sign) -> bool:
        if not isinstance(other, FourValuedSign):
            return False
        # In wKrQ, only T and F contradict
        return (self.value == "T" and other.value == "F") or \
               (self.value == "F" and other.value == "T")
    
    def get_symbol(self) -> str:
        return self.value


class ClassicalSignSystem(SignSystem):
    """Sign system for classical logic."""
    
    def __init__(self):
        self.T = ClassicalSign(True)
        self.F = ClassicalSign(False)
    
    def signs(self) -> Set[Sign]:
        return {self.T, self.F}
    
    def truth_conditions(self, sign: Sign) -> Set[TruthValue]:
        from .semantics import TRUE, FALSE
        if isinstance(sign, ClassicalSign):
            if sign.polarity:  # True polarity = T sign
                return {TRUE}
            else:  # False polarity = F sign
                return {FALSE}
        else:
            raise ValueError(f"Unknown sign: {sign}")
    
    def sign_for_truth_value(self, value: TruthValue) -> Sign:
        from .semantics import TRUE, FALSE
        if value == TRUE:
            return self.T
        elif value == FALSE:
            return self.F
        else:
            raise ValueError(f"No classical sign for truth value: {value}")


class ThreeValuedSignSystem(SignSystem):
    """Sign system for three-valued logic."""
    
    def __init__(self):
        self.T = ThreeValuedSign("T")
        self.F = ThreeValuedSign("F")
        self.U = ThreeValuedSign("U")
    
    def signs(self) -> Set[Sign]:
        return {self.T, self.F, self.U}
    
    def truth_conditions(self, sign: Sign) -> Set[TruthValue]:
        from .semantics import TRUE, FALSE, UNDEFINED
        if isinstance(sign, ThreeValuedSign):
            if sign.value == "T":
                return {TRUE}
            elif sign.value == "F":
                return {FALSE}
            elif sign.value == "U":
                return {UNDEFINED}
        else:
            raise ValueError(f"Unknown sign: {sign}")
    
    def sign_for_truth_value(self, value: TruthValue) -> Sign:
        from .semantics import TRUE, FALSE, UNDEFINED
        if value == TRUE:
            return self.T
        elif value == FALSE:
            return self.F
        elif value == UNDEFINED:
            return self.U
        else:
            raise ValueError(f"No three-valued sign for truth value: {value}")


# Backward compatibility functions
def T(formula: Formula) -> SignedFormula:
    """Create a classically true signed formula."""
    return SignedFormula(ClassicalSign(True), formula)


def F(formula: Formula) -> SignedFormula:
    """Create a classically false signed formula."""
    return SignedFormula(ClassicalSign(False), formula)


def T3(formula: Formula) -> SignedFormula:
    """Create a three-valued true signed formula."""
    return SignedFormula(ThreeValuedSign("T"), formula)


def F3(formula: Formula) -> SignedFormula:
    """Create a three-valued false signed formula."""
    return SignedFormula(ThreeValuedSign("F"), formula)


def U(formula: Formula) -> SignedFormula:
    """Create a three-valued undefined signed formula."""
    return SignedFormula(ThreeValuedSign("U"), formula)


def TF(formula: Formula) -> SignedFormula:
    """Create a four-valued true signed formula (wKrQ)."""
    return SignedFormula(FourValuedSign("T"), formula)


def FF(formula: Formula) -> SignedFormula:
    """Create a four-valued false signed formula (wKrQ)."""
    return SignedFormula(FourValuedSign("F"), formula)


def M(formula: Formula) -> SignedFormula:
    """Create a four-valued M signed formula (wKrQ)."""
    return SignedFormula(FourValuedSign("M"), formula)


def N(formula: Formula) -> SignedFormula:
    """Create a four-valued N signed formula (wKrQ)."""
    return SignedFormula(FourValuedSign("N"), formula)