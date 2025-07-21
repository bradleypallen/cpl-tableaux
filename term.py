#!/usr/bin/env python3
"""
Term Hierarchy for First-Order Logic

Defines the term structure for predicate logic including constants and variables.
Uses lexical conventions: lowercase for constants, uppercase for variables.
"""

from abc import ABC, abstractmethod
from typing import Set, List, Dict, Union


class Term(ABC):
    """Abstract base class for all terms in first-order logic"""
    
    @abstractmethod
    def is_ground(self) -> bool:
        """Check if term contains no variables"""
        pass
    
    @abstractmethod
    def get_variables(self) -> Set[str]:
        """Get all variable names in this term"""
        pass
    
    @abstractmethod
    def substitute(self, substitution: Dict[str, 'Term']) -> 'Term':
        """Apply a substitution to this term"""
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """String representation of the term"""
        pass
    
    @abstractmethod
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        pass


class Constant(Term):
    """
    Represents an individual constant in first-order logic.
    Constants must start with lowercase letters following standard convention.
    
    Examples: john, mary, c1, c2, a, b
    """
    
    def __init__(self, name: str):
        if not name or not isinstance(name, str):
            raise ValueError("Constant name must be a non-empty string")
        
        if not name[0].islower() and not name[0].isdigit():
            raise ValueError(f"Constant names must start with lowercase letter or digit: '{name}'")
        
        if not name.replace('_', '').isalnum():
            raise ValueError(f"Constant names must be alphanumeric (with underscores): '{name}'")
        
        self.name = name
    
    def is_ground(self) -> bool:
        """Constants are always ground (contain no variables)"""
        return True
    
    def get_variables(self) -> Set[str]:
        """Constants contain no variables"""
        return set()
    
    def substitute(self, substitution: Dict[str, Term]) -> Term:
        """Constants are not affected by substitution"""
        return self
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Constant('{self.name}')"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Constant) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(('constant', self.name))


class Variable(Term):
    """
    Represents a variable in first-order logic.
    Variables must start with uppercase letters following standard convention.
    
    Examples: X, Y, Z, Person, Object
    """
    
    def __init__(self, name: str):
        if not name or not isinstance(name, str):
            raise ValueError("Variable name must be a non-empty string")
        
        if not name[0].isupper():
            raise ValueError(f"Variable names must start with uppercase letter: '{name}'")
        
        if not name.replace('_', '').isalnum():
            raise ValueError(f"Variable names must be alphanumeric (with underscores): '{name}'")
        
        self.name = name
    
    def is_ground(self) -> bool:
        """Variables are never ground"""
        return False
    
    def get_variables(self) -> Set[str]:
        """Return the variable name"""
        return {self.name}
    
    def substitute(self, substitution: Dict[str, Term]) -> Term:
        """Apply substitution - replace this variable if it's in the substitution"""
        return substitution.get(self.name, self)
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Variable('{self.name}')"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Variable) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(('variable', self.name))


class FunctionApplication(Term):
    """
    Represents a function application f(t1, t2, ..., tn).
    This class is prepared for future extension but not used in the ground formula phase.
    
    Examples: f(john, mary), successor(0), plus(X, Y)
    """
    
    def __init__(self, function_name: str, args: List[Term]):
        if not function_name or not isinstance(function_name, str):
            raise ValueError("Function name must be a non-empty string")
        
        if not function_name[0].islower():
            raise ValueError(f"Function names must start with lowercase letter: '{function_name}'")
        
        if not isinstance(args, list):
            raise ValueError("Function arguments must be a list")
        
        self.function_name = function_name
        self.args = args
    
    @property
    def arity(self) -> int:
        """Return the number of arguments"""
        return len(self.args)
    
    def is_ground(self) -> bool:
        """Function application is ground if all arguments are ground"""
        return all(arg.is_ground() for arg in self.args)
    
    def get_variables(self) -> Set[str]:
        """Return all variables in the arguments"""
        variables = set()
        for arg in self.args:
            variables.update(arg.get_variables())
        return variables
    
    def substitute(self, substitution: Dict[str, Term]) -> Term:
        """Apply substitution to all arguments"""
        new_args = [arg.substitute(substitution) for arg in self.args]
        return FunctionApplication(self.function_name, new_args)
    
    def __str__(self) -> str:
        if self.arity == 0:
            return self.function_name
        args_str = ', '.join(str(arg) for arg in self.args)
        return f"{self.function_name}({args_str})"
    
    def __repr__(self) -> str:
        return f"FunctionApplication('{self.function_name}', {self.args})"
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, FunctionApplication) and 
                self.function_name == other.function_name and 
                self.args == other.args)
    
    def __hash__(self) -> int:
        return hash(('function', self.function_name, tuple(self.args)))


# Utility functions for term manipulation

def is_valid_constant_name(name: str) -> bool:
    """Check if a name is valid for a constant"""
    if not name or not isinstance(name, str):
        return False
    return ((name[0].islower() or name[0].isdigit()) and 
            name.replace('_', '').isalnum())


def is_valid_variable_name(name: str) -> bool:
    """Check if a name is valid for a variable"""
    if not name or not isinstance(name, str):
        return False
    return name[0].isupper() and name.replace('_', '').isalnum()


def parse_term(term_str: str) -> Term:
    """
    Parse a string into a Term object.
    For now, only supports constants. Variables will be added when quantifiers are implemented.
    """
    term_str = term_str.strip()
    
    if not term_str:
        raise ValueError("Empty term string")
    
    # For now, only support constants (ground terms only)
    if term_str[0].islower() or term_str[0].isdigit():
        return Constant(term_str)
    elif term_str[0].isupper():
        raise ValueError(f"Variables not supported in ground formula mode: '{term_str}'\n"
                        f"Use lowercase for constants: john, mary, c1")
    else:
        raise ValueError(f"Invalid term syntax: '{term_str}'")


def extract_terms(terms: List[Term]) -> Set[str]:
    """Extract all term names from a list of terms"""
    names = set()
    for term in terms:
        if isinstance(term, (Constant, Variable)):
            names.add(term.name)
        elif isinstance(term, FunctionApplication):
            names.add(term.function_name)
            names.update(extract_terms(term.args))
    return names


# Export commonly used items
__all__ = [
    'Term', 'Constant', 'Variable', 'FunctionApplication',
    'is_valid_constant_name', 'is_valid_variable_name', 'parse_term', 'extract_terms'
]