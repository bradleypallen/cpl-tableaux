#!/usr/bin/env python3
"""
Abstract formula system for extensible logic framework.

This module provides the base abstractions for formulas that can be extended
by different logic systems. The design allows for easy addition of new
connectives and formula types without modifying core code.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Set, Dict, Any, Union
from dataclasses import dataclass


class Formula(ABC):
    """Abstract base class for all formulas."""
    
    @abstractmethod
    def __str__(self) -> str:
        """Return string representation of the formula."""
        pass
    
    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Check equality with another formula."""
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        """Return hash for use in sets and dicts."""
        pass
    
    @abstractmethod
    def get_main_connective(self) -> Optional[str]:
        """Return the main connective symbol, or None for atoms."""
        pass
    
    @abstractmethod
    def get_subformulas(self) -> List['Formula']:
        """Return list of immediate subformulas."""
        pass
    
    @abstractmethod
    def get_atoms(self) -> Set[str]:
        """Return set of all atom names in the formula."""
        pass
    
    @abstractmethod
    def substitute(self, mapping: Dict[str, 'Formula']) -> 'Formula':
        """Substitute atoms according to mapping."""
        pass
    
    @abstractmethod
    def is_atomic(self) -> bool:
        """Check if this is an atomic formula."""
        pass
    
    def complexity(self) -> int:
        """Return the complexity (number of connectives) of the formula."""
        if self.is_atomic():
            return 0
        return 1 + sum(sub.complexity() for sub in self.get_subformulas())


class AtomicFormula(Formula):
    """Base class for atomic formulas (propositional atoms, predicates, etc.)."""
    
    def get_main_connective(self) -> Optional[str]:
        return None
    
    def get_subformulas(self) -> List[Formula]:
        return []
    
    def is_atomic(self) -> bool:
        return True


class PropositionalAtom(AtomicFormula):
    """A propositional atom (variable)."""
    
    def __init__(self, name: str):
        if not name:
            raise ValueError("Atom name cannot be empty")
        self.name = name
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, PropositionalAtom) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(('atom', self.name))
    
    def get_atoms(self) -> Set[str]:
        return {self.name}
    
    def substitute(self, mapping: Dict[str, Formula]) -> Formula:
        return mapping.get(self.name, self)


@dataclass
class ConnectiveSpec:
    """Specification for a logical connective."""
    symbol: str
    arity: int
    precedence: int
    associativity: str = "left"  # left, right, none
    format_style: str = "infix"  # infix, prefix, postfix, functional
    
    def format_formula(self, subformulas: List[Formula]) -> str:
        """Format the compound formula based on style."""
        if len(subformulas) != self.arity:
            raise ValueError(f"{self.symbol} requires {self.arity} arguments")
        
        if self.format_style == "infix" and self.arity == 2:
            return f"({subformulas[0]} {self.symbol} {subformulas[1]})"
        elif self.format_style == "prefix":
            if self.arity == 1:
                # For unary prefix operators like negation, don't add parentheses
                return f"{self.symbol}{subformulas[0]}"
            else:
                args = " ".join(str(f) for f in subformulas)
                return f"{self.symbol}({args})"
        elif self.format_style == "functional":
            args = ", ".join(str(f) for f in subformulas)
            return f"{self.symbol}({args})"
        else:
            raise ValueError(f"Unsupported format style: {self.format_style}")


class CompoundFormula(Formula):
    """A compound formula built from a connective and subformulas."""
    
    def __init__(self, connective: Union[str, ConnectiveSpec], *subformulas: Formula):
        if isinstance(connective, str):
            # For backward compatibility - will be replaced by proper spec
            self.connective_symbol = connective
            self.connective_spec = None
        else:
            self.connective_symbol = connective.symbol
            self.connective_spec = connective
        
        self.subformulas = list(subformulas)
        
        # Validate arity if we have a spec
        if self.connective_spec and len(self.subformulas) != self.connective_spec.arity:
            raise ValueError(
                f"{self.connective_symbol} requires {self.connective_spec.arity} "
                f"arguments, got {len(self.subformulas)}"
            )
    
    def __str__(self) -> str:
        if self.connective_spec:
            return self.connective_spec.format_formula(self.subformulas)
        else:
            # Fallback for backward compatibility
            if len(self.subformulas) == 1:
                return f"{self.connective_symbol}{self.subformulas[0]}"
            elif len(self.subformulas) == 2:
                return f"({self.subformulas[0]} {self.connective_symbol} {self.subformulas[1]})"
            else:
                args = ", ".join(str(f) for f in self.subformulas)
                return f"{self.connective_symbol}({args})"
    
    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, CompoundFormula) and 
                self.connective_symbol == other.connective_symbol and
                self.subformulas == other.subformulas)
    
    def __hash__(self) -> int:
        return hash((self.connective_symbol, tuple(self.subformulas)))
    
    def get_main_connective(self) -> Optional[str]:
        return self.connective_symbol
    
    def get_subformulas(self) -> List[Formula]:
        return self.subformulas.copy()
    
    def get_atoms(self) -> Set[str]:
        atoms = set()
        for sub in self.subformulas:
            atoms.update(sub.get_atoms())
        return atoms
    
    def substitute(self, mapping: Dict[str, Formula]) -> Formula:
        new_subs = [sub.substitute(mapping) for sub in self.subformulas]
        if self.connective_spec:
            return CompoundFormula(self.connective_spec, *new_subs)
        else:
            return CompoundFormula(self.connective_symbol, *new_subs)
    
    def is_atomic(self) -> bool:
        return False


# Backward compatibility aliases
Atom = PropositionalAtom


class PredicateFormula(AtomicFormula):
    """A predicate applied to terms (for first-order logic)."""
    
    def __init__(self, predicate_name: str, terms: List['Term']):
        self.predicate_name = predicate_name
        self.terms = terms
    
    def __str__(self) -> str:
        if not self.terms:
            return self.predicate_name
        term_str = ", ".join(str(t) for t in self.terms)
        return f"{self.predicate_name}({term_str})"
    
    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, PredicateFormula) and
                self.predicate_name == other.predicate_name and
                self.terms == other.terms)
    
    def __hash__(self) -> int:
        return hash(('predicate', self.predicate_name, tuple(self.terms)))
    
    def get_atoms(self) -> Set[str]:
        # For first-order logic, we might track predicate names differently
        return {str(self)}
    
    def substitute(self, mapping: Dict[str, Formula]) -> Formula:
        # For now, predicates don't substitute
        return self


class Term(ABC):
    """Abstract base class for terms in first-order logic."""
    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        pass


class Constant(Term):
    """A constant term."""
    
    def __init__(self, name: str):
        self.name = name
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Constant) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(('constant', self.name))


class Variable(Term):
    """A variable term."""
    
    def __init__(self, name: str):
        self.name = name
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Variable) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(('variable', self.name))


class FunctionApplication(Term):
    """A function applied to terms."""
    
    def __init__(self, function_name: str, terms: List[Term]):
        self.function_name = function_name
        self.terms = terms
    
    def __str__(self) -> str:
        if not self.terms:
            return self.function_name
        term_str = ", ".join(str(t) for t in self.terms)
        return f"{self.function_name}({term_str})"
    
    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, FunctionApplication) and
                self.function_name == other.function_name and
                self.terms == other.terms)
    
    def __hash__(self) -> int:
        return hash(('function', self.function_name, tuple(self.terms)))


class RestrictedQuantifierFormula(CompoundFormula):
    """Base class for restricted quantifier formulas in wKrQ logic."""
    
    def __init__(self, quantifier: str, variable: Variable, restriction: Formula, matrix: Formula):
        """
        Create a restricted quantifier formula.
        
        Args:
            quantifier: "∃" for existential, "∀" for universal
            variable: The bound variable
            restriction: The restriction formula (e.g., Student(X))  
            matrix: The matrix formula (e.g., Human(X))
        """
        # Create a dummy connective spec for the quantifier
        spec = ConnectiveSpec(quantifier, 2, 0, "none", "prefix")
        super().__init__(spec, restriction, matrix)
        self.quantifier = quantifier
        self.variable = variable
        self.restriction = restriction
        self.matrix = matrix
    
    def __str__(self) -> str:
        return f"[{self.quantifier}{self.variable} {self.restriction}]{self.matrix}"
    
    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, RestrictedQuantifierFormula) and
                self.quantifier == other.quantifier and
                self.variable == other.variable and
                self.restriction == other.restriction and
                self.matrix == other.matrix)
    
    def __hash__(self) -> int:
        return hash(('restricted_quantifier', self.quantifier, self.variable, 
                    self.restriction, self.matrix))
    
    def get_atoms(self) -> Set[str]:
        atoms = set()
        atoms.update(self.restriction.get_atoms())
        atoms.update(self.matrix.get_atoms())
        return atoms
    
    def substitute(self, mapping: Dict[str, Formula]) -> Formula:
        # Don't substitute the bound variable
        filtered_mapping = {k: v for k, v in mapping.items() if k != str(self.variable)}
        new_restriction = self.restriction.substitute(filtered_mapping)
        new_matrix = self.matrix.substitute(filtered_mapping)
        return self.__class__(self.quantifier, self.variable, new_restriction, new_matrix)


class RestrictedExistentialFormula(RestrictedQuantifierFormula):
    """Restricted existential quantifier: [∃X P(X)]Q(X)"""
    
    def __init__(self, variable: Variable, restriction: Formula, matrix: Formula):
        super().__init__("∃", variable, restriction, matrix)


class RestrictedUniversalFormula(RestrictedQuantifierFormula):
    """Restricted universal quantifier: [∀X P(X)]Q(X)"""
    
    def __init__(self, variable: Variable, restriction: Formula, matrix: Formula):
        super().__init__("∀", variable, restriction, matrix)


# Helper functions for first-order logic construction
def Predicate(name: str, terms: List[Term]) -> PredicateFormula:
    """Helper function to create predicate formulas."""
    return PredicateFormula(name, terms)

def Atom(name: str) -> PropositionalAtom:
    """Helper function to create propositional atoms."""
    return PropositionalAtom(name)