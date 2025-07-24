#!/usr/bin/env python3
"""
Tableau Core: Unified Foundation for Non-Classical Logic Tableaux

This module provides the core abstractions for implementing semantic tableaux
for non-classical logics. It consolidates the essential components needed for
tableau-based reasoning: formulas, terms, truth values, and signed formulas.

The design prioritizes:
- Clarity: Each concept is clearly documented with examples
- Modularity: Clean abstractions that can be extended for new logics
- Completeness: Support for propositional and first-order constructs
- Performance: Efficient implementations for tableau algorithms

Architecture:
- Truth Values: Multi-valued truth systems (classical, three-valued, etc.)
- Terms: First-order logic terms (constants, variables, functions)
- Formulas: Propositional and predicate logic formula AST
- Signs: Tableau signs for different logic systems (T/F, T/F/U, T/F/M/N)
- Signed Formulas: The fundamental unit of tableau reasoning

Academic Foundation:
Based on standard tableau literature including Smullyan's unified notation,
Priest's many-valued tableaux, Fitting's first-order methods, and Ferguson's
epistemic extensions for weak Kleene logic with restricted quantifiers.

Author: Generated for tableau reasoning research
License: MIT
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Set, Dict, Optional, Union, Tuple, Any

# Import truth values from the original module to ensure compatibility
from truth_value import TruthValue, t, f, e
import copy


# =============================================================================
# TRUTH VALUE SYSTEM
# =============================================================================

# TruthValue, t, f, e are now imported from truth_value module above


# =============================================================================
# TERM HIERARCHY (First-Order Logic)
# =============================================================================

class Term(ABC):
    """
    Abstract base class for all terms in first-order logic.
    
    Terms represent individual objects in the domain of discourse.
    The hierarchy includes:
    - Constants: Individual objects (john, mary, c1)
    - Variables: Placeholders for objects (X, Y, Z)
    - Functions: Complex terms (f(john), g(X, mary))
    
    Design follows standard first-order logic conventions:
    - Constants start with lowercase letters
    - Variables start with uppercase letters
    - Functions have name + argument list
    
    This supports ground reasoning (no variables) and can be extended
    for full first-order logic with unification and quantifiers.
    """
    
    @abstractmethod
    def is_ground(self) -> bool:
        """
        Check if term contains no variables.
        
        Ground terms represent fully specified objects, while non-ground
        terms contain variables that need instantiation.
        
        Returns:
            True if term contains no variables, False otherwise
        """
        pass
    
    @abstractmethod
    def get_variables(self) -> Set[str]:
        """
        Get all variable names occurring in this term.
        
        Returns:
            Set of variable names as strings
        """
        pass
    
    @abstractmethod
    def substitute(self, substitution: Dict[str, 'Term']) -> 'Term':
        """
        Apply a substitution mapping to this term.
        
        Substitutions replace variables with other terms, enabling
        unification and instantiation in first-order reasoning.
        
        Args:
            substitution: Mapping from variable names to replacement terms
            
        Returns:
            New term with substitution applied
        """
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """String representation of the term"""
        pass
    
    @abstractmethod
    def __eq__(self, other) -> bool:
        """Equality comparison for terms"""
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        pass


class Constant(Term):
    """
    Individual constant in first-order logic.
    
    Constants represent specific individual objects in the domain.
    They follow the convention of starting with lowercase letters
    and being alphanumeric (with underscores allowed).
    
    Examples:
        john, mary, c1, c2, socrates, tweety, fido
    
    Constants are always ground (contain no variables) and are
    unaffected by substitutions.
    """
    
    def __init__(self, name: str):
        """
        Create a new constant.
        
        Args:
            name: Constant name (must start with lowercase letter/digit)
            
        Raises:
            ValueError: If name doesn't follow constant naming conventions
        """
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
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Constant) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(('constant', self.name))


class Variable(Term):
    """
    Variable in first-order logic.
    
    Variables represent placeholders for objects that can be instantiated
    through substitution or quantifier binding. They follow the convention
    of starting with uppercase letters.
    
    Examples:
        X, Y, Z, Person, Object, VAR1
    
    Variables are never ground and are the primary target of substitutions.
    """
    
    def __init__(self, name: str):
        """
        Create a new variable.
        
        Args:
            name: Variable name (must start with uppercase letter)
            
        Raises:
            ValueError: If name doesn't follow variable naming conventions
        """
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
        """Variable contains itself as the only variable"""
        return {self.name}
    
    def substitute(self, substitution: Dict[str, Term]) -> Term:
        """Apply substitution to variable"""
        return substitution.get(self.name, self)
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Variable) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(('variable', self.name))


class FunctionApplication(Term):
    """
    Function application in first-order logic.
    
    Represents the application of a function symbol to a list of terms.
    Function applications can represent complex terms like f(x, y) or 
    nested applications like g(f(x), h(y, z)).
    
    Examples:
        f(john, mary) - binary function application
        successor(0) - unary function application
        plus(X, Y) - function with variable arguments
    
    Function applications are ground if all their arguments are ground.
    """
    
    def __init__(self, function_name: str, args: List[Term]):
        """
        Create a new function application.
        
        Args:
            function_name: Name of the function symbol
            args: List of argument terms
            
        Raises:
            ValueError: If function name is invalid or args is empty
        """
        if not function_name or not isinstance(function_name, str):
            raise ValueError("Function name must be a non-empty string")
        
        if not function_name[0].islower():
            raise ValueError(f"Function names must start with lowercase letter: '{function_name}'")
        
        if not isinstance(args, list) or len(args) == 0:
            raise ValueError("Function applications must have at least one argument")
        
        if not all(isinstance(arg, Term) for arg in args):
            raise ValueError("All arguments must be Terms")
        
        self.function_name = function_name
        self.args = args
    
    def is_ground(self) -> bool:
        """Function application is ground if all arguments are ground"""
        return all(arg.is_ground() for arg in self.args)
    
    def get_variables(self) -> Set[str]:
        """Get all variables from all arguments"""
        variables = set()
        for arg in self.args:
            variables.update(arg.get_variables())
        return variables
    
    def substitute(self, substitution: Dict[str, Term]) -> Term:
        """Apply substitution to all arguments"""
        new_args = [arg.substitute(substitution) for arg in self.args]
        return FunctionApplication(self.function_name, new_args)
    
    def __str__(self) -> str:
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.function_name}({args_str})"
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, FunctionApplication) and 
                self.function_name == other.function_name and 
                self.args == other.args)
    
    def __hash__(self) -> int:
        return hash(('function', self.function_name, tuple(self.args)))


# =============================================================================
# FORMULA HIERARCHY (Propositional and Predicate Logic)
# =============================================================================

class Formula(ABC):
    """
    Abstract base class for all logical formulas.
    
    Represents the abstract syntax tree for logical formulas in both
    propositional and first-order logic. Supports:
    
    Propositional Logic:
    - Atoms: Basic propositions (p, q, r)
    - Negation: ¬φ
    - Conjunction: φ ∧ ψ  
    - Disjunction: φ ∨ ψ
    - Implication: φ → ψ
    
    First-Order Logic:
    - Predicates: P(t1, ..., tn)
    - Quantifiers: ∀X φ, ∃X φ (future extension)
    
    Each formula type implements tableau-specific methods for:
    - Complexity calculation (for rule prioritization)
    - Structural analysis (atomic, literal checking)
    - Ground checking (for first-order formulas)
    """
    
    @abstractmethod
    def __str__(self) -> str:
        """Human-readable string representation"""
        pass
    
    @abstractmethod
    def is_atomic(self) -> bool:
        """
        Check if formula is atomic (cannot be decomposed further).
        
        Atomic formulas include propositional atoms and predicates.
        Non-atomic formulas include connectives and quantifiers.
        
        Returns:
            True if formula is atomic, False otherwise
        """
        pass
    
    @abstractmethod
    def is_literal(self) -> bool:
        """
        Check if formula is a literal (atomic or negated atomic).
        
        Literals are the simplest formulas in tableau reasoning
        and don't require further decomposition.
        
        Returns:
            True if formula is literal, False otherwise
        """
        pass
    
    def is_ground(self) -> bool:
        """
        Check if formula contains only ground terms (no variables).
        
        Ground formulas are fully instantiated and ready for evaluation.
        Non-ground formulas contain variables requiring substitution.
        
        Returns:
            True if formula is ground, False otherwise
        """
        return True  # Default for propositional formulas
    
    def get_variables(self) -> Set[str]:
        """
        Get all variable names occurring in this formula.
        
        Returns:
            Set of variable names as strings
        """
        return set()  # Default for propositional formulas
    
    def get_complexity(self) -> int:
        """
        Calculate formula complexity for tableau rule prioritization.
        
        Simpler formulas (lower complexity) are expanded first to
        minimize tableau branching. Complexity is roughly the
        number of logical connectives.
        
        Returns:
            Integer complexity score
        """
        return 1  # Default complexity for atomic formulas
    
    def get_atoms(self) -> Set[str]:
        """
        Get all atomic propositions occurring in this formula.
        
        Returns:
            Set of atom names as strings
        """
        return set()  # Default for non-atomic formulas
    
    @abstractmethod
    def __eq__(self, other) -> bool:
        """Structural equality comparison"""
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        pass


class Atom(Formula):
    """
    Propositional atom - the simplest formula type.
    
    Atoms represent basic propositions that are either true or false.
    They have no internal structure and serve as the building blocks
    for complex formulas.
    
    Examples:
        p, q, r, raining, sunny, proposition1
    
    Atoms are both atomic and literal, have complexity 1, and are
    always ground (no variables).
    """
    
    def __init__(self, name: str):
        """
        Create a propositional atom.
        
        Args:
            name: Atom name (any non-empty string)
            
        Raises:
            ValueError: If name is empty or not a string
        """
        if not name or not isinstance(name, str):
            raise ValueError("Atom name must be a non-empty string")
        self.name = name
    
    def __str__(self) -> str:
        return self.name
    
    def is_atomic(self) -> bool:
        """Atoms are atomic by definition"""
        return True
    
    def is_literal(self) -> bool:
        """Atoms are literals"""
        return False  # Atoms need signs to be literals
    
    def get_complexity(self) -> int:
        """Atoms have minimal complexity"""
        return 1
    
    def get_atoms(self) -> Set[str]:
        """Return this atom's name"""
        return {self.name}
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Atom) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(('atom', self.name))


class Predicate(Formula):
    """
    n-ary predicate in first-order logic.
    
    Predicates represent relationships between objects in the domain.
    They consist of a predicate name and a list of term arguments.
    
    Examples:
        - P(john): Unary predicate
        - Loves(john, mary): Binary predicate  
        - Student(X): Predicate with variable
        - Between(a, b, c): Ternary predicate
        - P(): Zero-ary predicate (propositional atom)
    
    Predicates are atomic formulas and are literals. They are ground
    only if all their arguments are ground terms.
    """
    
    def __init__(self, predicate_name: str, args: List[Term] = None):
        """
        Create a predicate formula.
        
        Args:
            predicate_name: Name of the predicate relation
            args: List of term arguments (empty list for propositional atoms)
            
        Raises:
            ValueError: If predicate_name is invalid or args contain non-Terms
        """
        if not predicate_name or not isinstance(predicate_name, str):
            raise ValueError("Predicate name must be a non-empty string")
        
        self.predicate_name = predicate_name
        self.name = predicate_name  # Alias for compatibility
        self.args = args if args is not None else []
        self.terms = self.args  # Alias for compatibility
        
        # Validate argument types
        for arg in self.args:
            if not isinstance(arg, Term):
                raise ValueError(f"All arguments must be Term instances: {arg}")
    
    @property
    def arity(self) -> int:
        """Return the number of arguments (arity) of this predicate"""
        return len(self.args)
    
    def __str__(self) -> str:
        if self.arity == 0:
            return self.predicate_name  # P (propositional atom)
        args_str = ', '.join(str(arg) for arg in self.args)
        return f"{self.predicate_name}({args_str})"  # P(t1, t2, ...)
    
    def is_atomic(self) -> bool:
        """Predicates are atomic formulas"""
        return True
    
    def is_literal(self) -> bool:
        """Predicates are literals"""
        return True
    
    def is_ground(self) -> bool:
        """Predicate is ground if all arguments are ground"""
        return all(arg.is_ground() for arg in self.args)
    
    def get_variables(self) -> Set[str]:
        """Get all variables in the predicate arguments"""
        variables = set()
        for arg in self.args:
            variables.update(arg.get_variables())
        return variables
    
    def get_complexity(self) -> int:
        """Predicates have minimal complexity like atoms"""
        return 1
    
    def get_atoms(self) -> Set[str]:
        """Return this predicate's name as atomic proposition"""
        return {self.predicate_name}
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Predicate) and 
                self.predicate_name == other.predicate_name and
                self.args == other.args)
    
    def __hash__(self) -> int:
        return hash(('predicate', self.predicate_name, tuple(self.args)))


class Negation(Formula):
    """
    Logical negation: ¬φ
    
    Represents the negation of another formula. In tableau reasoning,
    negations are typically handled by special rules that flip signs
    rather than decomposing the formula structure.
    
    Examples:
        ¬p, ¬(p ∧ q), ¬∀X P(X)
    
    Negations are non-atomic but may be literals if they negate
    atomic formulas.
    """
    
    def __init__(self, operand: Formula):
        """
        Create a negation formula.
        
        Args:
            operand: The formula being negated
            
        Raises:
            ValueError: If operand is not a Formula
        """
        if not isinstance(operand, Formula):
            raise ValueError("Negation operand must be a Formula")
        self.operand = operand
    
    def __str__(self) -> str:
        # Add parentheses for complex operands
        if self.operand.is_atomic():
            return f"¬{self.operand}"
        else:
            return f"¬({self.operand})"
    
    def is_atomic(self) -> bool:
        """Negations are non-atomic (have internal structure)"""
        return False
    
    def is_literal(self) -> bool:
        """Negation is literal only if it negates an atomic formula"""
        return self.operand.is_atomic()
    
    def is_ground(self) -> bool:
        """Negation is ground if its operand is ground"""
        return self.operand.is_ground()
    
    def get_variables(self) -> Set[str]:
        """Variables in negation are variables in operand"""
        return self.operand.get_variables()
    
    def get_complexity(self) -> int:
        """Negation complexity is operand complexity + 1"""
        return self.operand.get_complexity() + 1
    
    def get_atoms(self) -> Set[str]:
        """Return atoms from the operand"""
        return self.operand.get_atoms()
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Negation) and self.operand == other.operand
    
    def __hash__(self) -> int:
        return hash(('negation', self.operand))


class Conjunction(Formula):
    """
    Logical conjunction: φ ∧ ψ
    
    Represents the logical AND of two formulas. In tableau reasoning,
    conjunctions typically create α-rules (linear expansion) where
    both conjuncts must be satisfied.
    
    Examples:
        p ∧ q, (p → q) ∧ (q → r), ∀X P(X) ∧ ∃Y Q(Y)
    
    Conjunctions are non-atomic and non-literal, requiring decomposition
    in tableau construction.
    """
    
    def __init__(self, left: Formula, right: Formula):
        """
        Create a conjunction formula.
        
        Args:
            left: Left conjunct
            right: Right conjunct
            
        Raises:
            ValueError: If operands are not Formulas
        """
        if not isinstance(left, Formula) or not isinstance(right, Formula):
            raise ValueError("Conjunction operands must be Formulas")
        self.left = left
        self.right = right
    
    def __str__(self) -> str:
        # Parenthesize complex operands for clarity
        left_str = str(self.left) if self.left.is_atomic() or isinstance(self.left, Negation) else f"({self.left})"
        right_str = str(self.right) if self.right.is_atomic() or isinstance(self.right, Negation) else f"({self.right})"
        return f"{left_str} ∧ {right_str}"
    
    def is_atomic(self) -> bool:
        """Conjunctions are non-atomic"""
        return False
    
    def is_literal(self) -> bool:
        """Conjunctions are never literals"""
        return False
    
    def is_ground(self) -> bool:
        """Conjunction is ground if both operands are ground"""
        return self.left.is_ground() and self.right.is_ground()
    
    def get_variables(self) -> Set[str]:
        """Variables in conjunction are union of operand variables"""
        return self.left.get_variables() | self.right.get_variables()
    
    def get_complexity(self) -> int:
        """Conjunction complexity is sum of operand complexities + 1"""
        return self.left.get_complexity() + self.right.get_complexity() + 1
    
    def get_atoms(self) -> Set[str]:
        """Return atoms from both operands"""
        return self.left.get_atoms() | self.right.get_atoms()
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Conjunction) and 
                self.left == other.left and self.right == other.right)
    
    def __hash__(self) -> int:
        return hash(('conjunction', self.left, self.right))


class Disjunction(Formula):
    """
    Logical disjunction: φ ∨ ψ
    
    Represents the logical OR of two formulas. In tableau reasoning,
    disjunctions typically create β-rules (branching expansion) where
    either disjunct can be satisfied.
    
    Examples:
        p ∨ q, (p ∧ q) ∨ (r ∧ s), ∃X P(X) ∨ ∀Y Q(Y)
    
    Disjunctions are non-atomic and non-literal, requiring decomposition
    with branching in tableau construction.
    """
    
    def __init__(self, left: Formula, right: Formula):
        """
        Create a disjunction formula.
        
        Args:
            left: Left disjunct
            right: Right disjunct
            
        Raises:
            ValueError: If operands are not Formulas
        """
        if not isinstance(left, Formula) or not isinstance(right, Formula):
            raise ValueError("Disjunction operands must be Formulas")
        self.left = left
        self.right = right
    
    def __str__(self) -> str:
        # Parenthesize complex operands for clarity
        left_str = str(self.left) if self.left.is_atomic() or isinstance(self.left, Negation) else f"({self.left})"
        right_str = str(self.right) if self.right.is_atomic() or isinstance(self.right, Negation) else f"({self.right})"
        return f"{left_str} ∨ {right_str}"
    
    def is_atomic(self) -> bool:
        """Disjunctions are non-atomic"""
        return False
    
    def is_literal(self) -> bool:
        """Disjunctions are never literals"""
        return False
    
    def is_ground(self) -> bool:
        """Disjunction is ground if both operands are ground"""
        return self.left.is_ground() and self.right.is_ground()
    
    def get_variables(self) -> Set[str]:
        """Variables in disjunction are union of operand variables"""
        return self.left.get_variables() | self.right.get_variables()
    
    def get_complexity(self) -> int:
        """Disjunction complexity is sum of operand complexities + 1"""
        return self.left.get_complexity() + self.right.get_complexity() + 1
    
    def get_atoms(self) -> Set[str]:
        """Return atoms from both operands"""
        return self.left.get_atoms() | self.right.get_atoms()
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Disjunction) and 
                self.left == other.left and self.right == other.right)
    
    def __hash__(self) -> int:
        return hash(('disjunction', self.left, self.right))


class Implication(Formula):
    """
    Logical implication: φ → ψ
    
    Represents material implication from antecedent to consequent.
    In tableau reasoning, implications typically create β-rules
    (branching expansion) equivalent to ¬φ ∨ ψ.
    
    Examples:
        p → q, (p ∧ q) → r, ∀X P(X) → ∃Y Q(Y)
    
    Implications are non-atomic and non-literal, requiring decomposition
    in tableau construction.
    """
    
    def __init__(self, antecedent: Formula, consequent: Formula):
        """
        Create an implication formula.
        
        Args:
            antecedent: The antecedent (if part)
            consequent: The consequent (then part)
            
        Raises:
            ValueError: If operands are not Formulas
        """
        if not isinstance(antecedent, Formula) or not isinstance(consequent, Formula):
            raise ValueError("Implication operands must be Formulas")
        self.antecedent = antecedent
        self.consequent = consequent
    
    def __str__(self) -> str:
        # Parenthesize complex operands for clarity
        ant_str = str(self.antecedent) if self.antecedent.is_atomic() or isinstance(self.antecedent, Negation) else f"({self.antecedent})"
        cons_str = str(self.consequent) if self.consequent.is_atomic() or isinstance(self.consequent, Negation) else f"({self.consequent})"
        return f"{ant_str} → {cons_str}"
    
    def is_atomic(self) -> bool:
        """Implications are non-atomic"""
        return False
    
    def is_literal(self) -> bool:
        """Implications are never literals"""
        return False
    
    def is_ground(self) -> bool:
        """Implication is ground if both operands are ground"""
        return self.antecedent.is_ground() and self.consequent.is_ground()
    
    def get_variables(self) -> Set[str]:
        """Variables in implication are union of operand variables"""
        return self.antecedent.get_variables() | self.consequent.get_variables()
    
    def get_complexity(self) -> int:
        """Implication complexity is sum of operand complexities + 1"""
        return self.antecedent.get_complexity() + self.consequent.get_complexity() + 1
    
    def get_atoms(self) -> Set[str]:
        """Return atoms from both operands"""
        return self.antecedent.get_atoms() | self.consequent.get_atoms()
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Implication) and 
                self.antecedent == other.antecedent and self.consequent == other.consequent)
    
    def __hash__(self) -> int:
        return hash(('implication', self.antecedent, self.consequent))


# =============================================================================
# SIGN SYSTEM (Tableau Signs for Different Logics)  
# =============================================================================

class Sign(ABC):
    """
    Abstract base class for tableau signs.
    
    Signs are labels attached to formulas in signed tableau systems,
    indicating how the formula should be interpreted in the current
    logic system. Different logic systems use different sign sets:
    
    - Classical Logic: T (true), F (false)
    - Three-valued Logic: T (true), F (false), U (undefined)  
    - wKrQ Logic: T (true), F (false), M (may be true), N (need not be true)
    
    Signs determine:
    - Which tableau rules apply to signed formulas
    - When branches close due to contradictory signs
    - How models are extracted from open branches
    
    The sign system is the key extension point for implementing new
    non-classical logics in the tableau framework.
    """
    
    @abstractmethod
    def __str__(self) -> str:
        """String representation of the sign"""
        pass
    
    @abstractmethod
    def __eq__(self, other) -> bool:
        """Equality comparison between signs"""
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        pass
    
    @abstractmethod
    def is_contradictory_with(self, other: 'Sign') -> bool:
        """
        Check if this sign contradicts another sign for branch closure.
        
        Contradictory signs on the same formula cause tableau branches
        to close, indicating unsatisfiability. Different logic systems
        have different contradiction patterns:
        
        - Classical: T contradicts F
        - Three-valued: T contradicts F (U doesn't contradict anything)
        - wKrQ: T contradicts F (M and N represent uncertainty)
        
        Args:
            other: Another sign to check for contradiction
            
        Returns:
            True if signs are contradictory, False otherwise
        """
        pass
    
    @abstractmethod
    def get_truth_value(self) -> Optional[TruthValue]:
        """
        Get the truth value this sign represents (if applicable).
        
        Maps tableau signs to semantic truth values. Some signs
        may not have direct truth value correspondences (e.g.,
        epistemic signs in wKrQ logic).
        
        Returns:
            Corresponding TruthValue or None if no mapping exists
        """
        pass


class ClassicalSign(Sign):
    """
    Classical two-valued signs: T (true) and F (false).
    
    The fundamental signs for classical propositional and first-order logic.
    Forms the basis for standard tableau methods where formulas are
    either required to be true (T) or false (F).
    
    Contradiction: T and F are contradictory on the same formula.
    
    Examples:
        T:p (p must be true)
        F:(p → q) (p → q must be false)
    """
    
    def __init__(self, designation: str):
        """
        Create a classical sign.
        
        Args:
            designation: "T" for true sign, "F" for false sign
        """
        if designation not in {"T", "F"}:
            raise ValueError(f"Invalid classical sign: {designation}")
        self.designation = designation
        self.value = designation == "T"
    
    def __str__(self) -> str:
        return self.designation
    
    def __eq__(self, other) -> bool:
        return isinstance(other, ClassicalSign) and self.designation == other.designation
    
    def __hash__(self) -> int:
        return hash(("classical", self.designation))
    
    def is_contradictory_with(self, other: 'Sign') -> bool:
        """T and F are contradictory in classical logic"""
        return isinstance(other, ClassicalSign) and self.value != other.value
    
    def get_truth_value(self) -> TruthValue:
        """Map to corresponding truth value"""
        return t if self.value else f


class ThreeValuedSign(Sign):
    """
    Three-valued signs: T (true), F (false), U (undefined).
    
    Extends classical signs with undefined (U) for weak Kleene logic
    and other three-valued systems. The undefined sign represents
    truth value gaps or incomplete information.
    
    Contradiction: Only T and F are contradictory. U represents
    uncertainty and doesn't create contradictions.
    
    Examples:
        T:p (p is true)
        F:p (p is false)
        U:p (p has no definite truth value)
    """
    
    def __init__(self, designation: str):
        """
        Create a three-valued sign.
        
        Args:
            designation: "T", "F", or "U" for three-valued signs
            
        Raises:
            ValueError: If designation is not valid
        """
        if designation not in {"T", "F", "U"}:
            raise ValueError(f"Invalid three-valued sign: {designation}")
        self.designation = designation
        
        # Map to internal truth values
        if designation == "T":
            self.value = t
        elif designation == "F":
            self.value = f
        elif designation == "U":
            self.value = e
    
    def __str__(self) -> str:
        return self.designation
    
    def __eq__(self, other) -> bool:
        return isinstance(other, ThreeValuedSign) and self.designation == other.designation
    
    def __hash__(self) -> int:
        return hash(("three_valued", self.designation))
    
    def is_contradictory_with(self, other: 'Sign') -> bool:
        """
        Three-valued closure rules:
        - T and F are contradictory (classical behavior)
        - T and U are NOT contradictory (both can coexist)
        - F and U are NOT contradictory (both can coexist)
        - U and U are NOT contradictory (uncertainty is consistent)
        """
        if not isinstance(other, ThreeValuedSign):
            return False
        
        # Only T and F create contradictions in three-valued logic
        return ((self.value == t and other.value == f) or 
                (self.value == f and other.value == t))
    
    def get_truth_value(self) -> TruthValue:
        """Direct mapping to truth value"""
        return self.value


class WkrqSign(Sign):
    """
    wKrQ signs: T, F, M (may be true), N (need not be true).
    
    Ferguson's four-valued signing system for weak Kleene logic with
    restricted quantifiers. Extends classical T/F with epistemic signs
    M and N for representing uncertainty without contradiction.
    
    Based on: Ferguson, Thomas Macaulay. "Tableaux and restricted 
    quantification for systems related to weak Kleene logic." TABLEAUX 2021.
    
    Signs:
    - T: definitely true (classical true)
    - F: definitely false (classical false)
    - M: may be true (possibly true, not necessarily false)
    - N: need not be true (possibly false, not necessarily true)
    
    Contradiction: Only T and F are contradictory. M and N represent
    epistemic uncertainty and can coexist without contradiction.
    
    Examples:
        T:p (p is definitely true)
        F:p (p is definitely false)
        M:p (p may be true - epistemic possibility)
        N:p (p need not be true - epistemic possibility of falsehood)
    """
    
    def __init__(self, designation: str):
        """
        Create a wKrQ sign.
        
        Args:
            designation: Sign designation ("T", "F", "M", or "N")
            
        Raises:
            ValueError: If designation is not a valid wKrQ sign
        """
        if designation not in {"T", "F", "M", "N"}:
            raise ValueError(f"Invalid wKrQ sign: {designation}")
        self.designation = designation
    
    def __str__(self) -> str:
        return self.designation
    
    def __eq__(self, other) -> bool:
        return isinstance(other, WkrqSign) and self.designation == other.designation
    
    def __hash__(self) -> int:
        return hash(("wkrq", self.designation))
    
    def is_contradictory_with(self, other: 'Sign') -> bool:
        """
        wKrQ closure rules based on Ferguson (2021):
        - T and F are contradictory (classical behavior)
        - M and N represent epistemic uncertainty and don't create contradictions
        - This allows reasoning under uncertainty without branch closure
        """
        if not isinstance(other, WkrqSign):
            return False
        
        # Only T and F create contradictions in wKrQ logic
        # M and N represent uncertainty and don't close branches
        contradictory_pairs = {("T", "F"), ("F", "T")}
        return (self.designation, other.designation) in contradictory_pairs
    
    def get_truth_value(self) -> Optional[TruthValue]:
        """
        Map wKrQ signs to truth values where possible:
        - T maps to true (t)
        - F maps to false (f)  
        - M and N represent uncertainty and map to undefined (e)
        """
        mapping = {
            "T": t,
            "F": f,
            "M": e,  # May be true -> undefined
            "N": e   # Need not be true -> undefined
        }
        return mapping.get(self.designation, e)
    
    def is_definite(self) -> bool:
        """Check if this is a definite sign (T or F)"""
        return self.designation in {"T", "F"}
    
    def is_epistemic(self) -> bool:
        """Check if this is an epistemic sign (M or N)"""
        return self.designation in {"M", "N"}
    
    def dual(self) -> 'WkrqSign':
        """
        Get the dual of this sign for negation rules.
        
        Duality relationships in wKrQ:
        - T ↔ F (classical duality)
        - M ↔ N (epistemic duality)
        
        Returns:
            Dual sign for use in negation tableau rules
        """
        dual_mapping = {
            "T": "F",
            "F": "T", 
            "M": "N",
            "N": "M"
        }
        return WkrqSign(dual_mapping[self.designation])


# =============================================================================
# SIGNED FORMULAS (The Core Unit of Tableau Reasoning)
# =============================================================================

@dataclass(frozen=True)
class SignedFormula:
    """
    A signed formula: the fundamental unit of tableau reasoning.
    
    Combines a logical formula with a tableau sign to indicate how
    the formula should be interpreted in the current context.
    This is the core abstraction that enables tableau methods to
    work across different logic systems.
    
    Structure: Sign:Formula
    Examples:
        T:p (p must be true)
        F:(p → q) (p → q must be false)
        U:(p ∧ q) (p ∧ q is undefined)
        M:∃X P(X) (∃X P(X) may be true)
    
    Signed formulas are:
    - Immutable (frozen dataclass) for safe use in sets/dicts
    - Hashable for efficient tableau branch management
    - Comparable for rule prioritization
    - Extensible to any sign system and formula type
    
    This abstraction enables the same tableau engine to work with
    classical logic, many-valued logics, modal logics, etc. by
    simply changing the sign system and rules.
    """
    
    sign: Sign
    formula: Formula
    
    def __str__(self) -> str:
        """Standard notation: Sign:Formula"""
        return f"{self.sign}:{self.formula}"
    
    def __post_init__(self):
        """Validate signed formula after creation"""
        if not isinstance(self.sign, Sign):
            raise ValueError(f"Sign must be a Sign instance: {self.sign}")
        if not isinstance(self.formula, Formula):
            raise ValueError(f"Formula must be a Formula instance: {self.formula}")
    
    def is_atomic(self) -> bool:
        """
        Check if the underlying formula is atomic.
        
        Atomic signed formulas don't require further tableau expansion
        and represent the base case for tableau construction.
        
        Returns:
            True if formula is atomic, False otherwise
        """
        return self.formula.is_atomic()
    
    def is_literal(self) -> bool:
        """
        Check if this signed formula is literal.
        
        Literal signed formulas (atomic or negated atomic) are typically
        not expanded further in tableau construction.
        
        Returns:
            True if formula is literal, False otherwise
        """
        # A signed formula is literal if:
        # 1. It's signed atomic formula (e.g., T:p, F:q)
        # 2. It's a signed negation of atomic formula (e.g., T:¬p, F:¬q)
        if self.formula.is_atomic():
            return True
        if isinstance(self.formula, Negation) and self.formula.operand.is_atomic():
            return True
        return False
    
    def is_ground(self) -> bool:
        """
        Check if the underlying formula is ground (no variables).
        
        Ground signed formulas are fully instantiated and ready for
        evaluation or model construction.
        
        Returns:
            True if formula is ground, False otherwise
        """
        return self.formula.is_ground()
    
    def get_complexity(self) -> int:
        """
        Get the complexity of the underlying formula.
        
        Used for prioritizing tableau rule applications - simpler
        formulas are typically expanded first to minimize branching.
        
        Returns:
            Integer complexity score
        """
        return self.formula.get_complexity()
    
    def get_variables(self) -> Set[str]:
        """
        Get all variables in the underlying formula.
        
        Returns:
            Set of variable names as strings
        """
        return self.formula.get_variables()
    
    def is_contradictory_with(self, other: 'SignedFormula') -> bool:
        """
        Check if this signed formula contradicts another.
        
        Two signed formulas contradict if they have the same formula
        but contradictory signs. This is the fundamental test for
        tableau branch closure.
        
        Args:
            other: Another signed formula to check for contradiction
            
        Returns:
            True if signed formulas contradict, False otherwise
        """
        return (self.formula == other.formula and 
                self.sign.is_contradictory_with(other.sign))


# =============================================================================
# CONVENIENCE FUNCTIONS FOR CREATING SIGNED FORMULAS
# =============================================================================

def T(formula: Formula) -> SignedFormula:
    """Create T:formula for classical logic (true)"""
    return SignedFormula(ClassicalSign("T"), formula)

def F(formula: Formula) -> SignedFormula:
    """Create F:formula for classical logic (false)"""
    return SignedFormula(ClassicalSign("F"), formula)

def T3(formula: Formula) -> SignedFormula:
    """Create T:formula for three-valued logic (true)"""
    return SignedFormula(ThreeValuedSign("T"), formula)

def F3(formula: Formula) -> SignedFormula:
    """Create F:formula for three-valued logic (false)"""
    return SignedFormula(ThreeValuedSign("F"), formula)

def U(formula: Formula) -> SignedFormula:
    """Create U:formula for three-valued logic (undefined)"""
    return SignedFormula(ThreeValuedSign("U"), formula)

def TF(formula: Formula) -> SignedFormula:
    """Create T:formula for wKrQ logic (definitely true)"""
    return SignedFormula(WkrqSign("T"), formula)

def FF(formula: Formula) -> SignedFormula:
    """Create F:formula for wKrQ logic (definitely false)"""
    return SignedFormula(WkrqSign("F"), formula)

def M(formula: Formula) -> SignedFormula:
    """Create M:formula for wKrQ logic (may be true)"""
    return SignedFormula(WkrqSign("M"), formula)

def N(formula: Formula) -> SignedFormula:
    """Create N:formula for wKrQ logic (need not be true)"""
    return SignedFormula(WkrqSign("N"), formula)


# =============================================================================
# SIGN SYSTEM REGISTRY
# =============================================================================

class SignRegistry:
    """
    Registry for managing different sign systems in tableau reasoning.
    
    Provides a centralized way to register and access sign systems
    for different logic systems. This enables the tableau engine
    to work with any logic by simply selecting the appropriate
    sign system.
    
    Built-in sign systems:
    - "classical": ClassicalSign (T, F)
    - "three_valued": ThreeValuedSign (T, F, U)
    - "wkrq": WkrqSign (T, F, M, N)
    
    New logic systems can be added by registering their sign classes
    and factory functions.
    """
    
    _sign_systems: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register_sign_system(cls, name: str, sign_class: type, factory_func=None):
        """
        Register a new sign system.
        
        Args:
            name: Unique name for the sign system
            sign_class: Sign class for this system
            factory_func: Optional function to create all signs in system
        """
        cls._sign_systems[name] = {
            "sign_class": sign_class,
            "factory": factory_func
        }
    
    @classmethod
    def get_sign_class(cls, system_name: str) -> type:
        """
        Get the sign class for a named system.
        
        Args:
            system_name: Name of the sign system
            
        Returns:
            Sign class for the system
            
        Raises:
            ValueError: If system is not registered
        """
        if system_name not in cls._sign_systems:
            raise ValueError(f"Unknown sign system: {system_name}")
        return cls._sign_systems[system_name]["sign_class"]
    
    @classmethod
    def get_all_signs(cls, system_name: str) -> List[Sign]:
        """
        Get all signs for a named system.
        
        Args:
            system_name: Name of the sign system
            
        Returns:
            List of all signs in the system
            
        Raises:
            ValueError: If system is not registered or has no factory
        """
        if system_name not in cls._sign_systems:
            raise ValueError(f"Unknown sign system: {system_name}")
        
        factory = cls._sign_systems[system_name]["factory"]
        if factory is None:
            raise ValueError(f"No factory function for sign system: {system_name}")
        
        return factory()
    
    @classmethod
    def list_systems(cls) -> List[str]:
        """
        List all registered sign systems.
        
        Returns:
            List of system names
        """
        return list(cls._sign_systems.keys())


# Register built-in sign systems
def _create_classical_signs() -> List[Sign]:
    """Create classical T/F signs"""
    return [ClassicalSign("T"), ClassicalSign("F")]

def _create_three_valued_signs() -> List[Sign]:
    """Create three-valued T/F/U signs"""
    return [ThreeValuedSign(t), ThreeValuedSign(f), ThreeValuedSign(e)]

def _create_wkrq_signs() -> List[Sign]:
    """Create wKrQ T/F/M/N signs"""
    return [WkrqSign("T"), WkrqSign("F"), WkrqSign("M"), WkrqSign("N")]

SignRegistry.register_sign_system("classical", ClassicalSign, _create_classical_signs)
SignRegistry.register_sign_system("three_valued", ThreeValuedSign, _create_three_valued_signs)
SignRegistry.register_sign_system("wkrq", WkrqSign, _create_wkrq_signs)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_signed_formula(sign: Sign, formula: Formula) -> SignedFormula:
    """
    Create a signed formula from a sign and formula.
    
    Args:
        sign: The sign to apply
        formula: The formula to sign
        
    Returns:
        SignedFormula combining the sign and formula
    """
    return SignedFormula(sign, formula)


def dual_sign(sign: Sign) -> Sign:
    """
    Get the dual of a sign (for negation rules).
    
    Args:
        sign: The original sign
        
    Returns:
        The dual sign
    """
    if hasattr(sign, 'dual'):
        return sign.dual()
    elif isinstance(sign, ClassicalSign):
        return ClassicalSign("F" if sign.designation == "T" else "T")
    elif isinstance(sign, ThreeValuedSign):
        if sign.value == t:
            return ThreeValuedSign(f)
        elif sign.value == f:
            return ThreeValuedSign(t)
        else:  # e
            return sign  # U is its own dual
    elif isinstance(sign, WkrqSign):
        return sign.dual()
    else:
        raise ValueError(f"Unknown sign type: {type(sign)}")


def parse_formula(formula_str: str) -> Formula:
    """
    Parse a formula string into a Formula object.
    
    This is a simple parser for basic propositional formulas.
    
    Args:
        formula_str: String representation of the formula
        
    Returns:
        Parsed Formula object
    """
    formula_str = formula_str.strip()
    
    # Handle negation
    if formula_str.startswith('~') or formula_str.startswith('¬'):
        inner = parse_formula(formula_str[1:].strip())
        return Negation(inner)
    
    # Handle parentheses
    if formula_str.startswith('(') and formula_str.endswith(')'):
        return parse_formula(formula_str[1:-1])
    
    # Simple atoms (letters and numbers)
    if formula_str.isalnum():
        return Atom(formula_str)
    
    # For complex formulas, find main connective by precedence (lowest to highest):
    # 1. Implication (->)
    # 2. Disjunction (|)  
    # 3. Conjunction (&)
    
    paren_depth = 0
    
    # First pass: Look for implication (lowest precedence)
    for i, char in enumerate(formula_str):
        if char == '(':
            paren_depth += 1
        elif char == ')':
            paren_depth -= 1
        elif paren_depth == 0:  # Only split at top level
            if formula_str[i:i+2] == '->' or char == '→':
                split_pos = i+2 if formula_str[i:i+2] == '->' else i+1
                left = parse_formula(formula_str[:i].strip())
                right = parse_formula(formula_str[split_pos:].strip())
                return Implication(left, right)
    
    # Second pass: Look for disjunction
    paren_depth = 0
    for i, char in enumerate(formula_str):
        if char == '(':
            paren_depth += 1
        elif char == ')':
            paren_depth -= 1
        elif paren_depth == 0:  # Only split at top level
            if char in ['|', '∨']:
                left = parse_formula(formula_str[:i].strip())
                right = parse_formula(formula_str[i+1:].strip())
                return Disjunction(left, right)
    
    # Third pass: Look for conjunction (highest precedence)
    paren_depth = 0
    for i, char in enumerate(formula_str):
        if char == '(':
            paren_depth += 1
        elif char == ')':
            paren_depth -= 1
        elif paren_depth == 0:  # Only split at top level
            if char in ['&', '∧']:
                left = parse_formula(formula_str[:i].strip())
                right = parse_formula(formula_str[i+1:].strip())
                return Conjunction(left, right)
    
    # If we can't parse it, assume it's an atom
    return Atom(formula_str)


# =============================================================================
# COMPATIBILITY FUNCTIONS FOR LITERATURE TESTS
# =============================================================================

def wk3_satisfiable(formula: Formula) -> bool:
    """
    Test satisfiability using WK3 (weak Kleene) semantics.
    
    Args:
        formula: Formula to test
        
    Returns:
        True if satisfiable in WK3, False otherwise
    """
    from wk3_tableau import WK3Tableau
    tableau = WK3Tableau([formula])  # WK3Tableau expects a list
    return tableau.build()

def wk3_models(formula: Formula) -> List[Any]:
    """
    Get WK3 models for a formula.
    
    Args:
        formula: Formula to get models for
        
    Returns:
        List of WK3 models
    """
    from wk3_tableau import WK3Tableau
    from wk3_model import WK3Model
    tableau = WK3Tableau([formula])  # WK3Tableau expects a list
    if tableau.build():
        models = []
        for branch in tableau.branches:
            if not branch.is_closed:
                model = WK3Model()
                # Extract assignments from branch (WK3Branch uses assignments, not signed_formulas)
                for assignment in branch.assignments:
                    # Each assignment has atom_name and value attributes
                    model.assignment[assignment.atom_name] = assignment.value
                models.append(model)
        return models
    return []

def classical_signed_tableau(signed_formula):
    """
    Create a classical signed tableau for compatibility.
    
    Args:
        signed_formula: Signed formula or list of signed formulas to build tableau for
        
    Returns:
        Tableau-like object with build() method
    """
    class CompatTableau:
        def __init__(self, sf):
            if isinstance(sf, list):
                self.signed_formulas = sf
            else:
                self.signed_formulas = [sf]
            self.branches = []
            self.engine = None
            self.rule_applications = 0
            
        def build(self):
            from tableau_engine import TableauEngine
            self.engine = TableauEngine("classical")
            result = self.engine.build_tableau(self.signed_formulas)
            self.branches = self.engine.branches
            stats = self.engine.get_statistics()
            self.rule_applications = stats.rule_applications
            self.last_result = result
            return result
            
        def extract_all_models(self):
            if self.engine is None:
                return []
            return self.engine.get_models()
            
        def get_statistics(self):
            if self.engine is None:
                return {}
            return {
                "sign_system": "classical",
                "initial_formulas": len(self.signed_formulas),
                "satisfiable": getattr(self, 'last_result', None),
                "rule_applications": self.rule_applications,
                "total_branches": len(self.branches)
            }
    
    return CompatTableau(signed_formula)

def three_valued_signed_tableau(signed_formula):
    """
    Create a three-valued signed tableau for compatibility.
    
    Args:
        signed_formula: Signed formula or list of signed formulas to build tableau for
        
    Returns:
        Tableau-like object with build() method
    """
    class CompatTableau:
        def __init__(self, sf):
            if isinstance(sf, list):
                self.signed_formulas = sf
            else:
                self.signed_formulas = [sf]
            self.branches = []
            self.engine = None
            self.rule_applications = 0
            
        def build(self):
            from tableau_engine import TableauEngine
            self.engine = TableauEngine("three_valued")
            result = self.engine.build_tableau(self.signed_formulas)
            self.branches = self.engine.branches
            stats = self.engine.get_statistics()
            self.rule_applications = stats.rule_applications
            self.last_result = result
            return result
            
        def extract_all_models(self):
            if self.engine is None:
                return []
            return self.engine.get_models()
            
        def get_statistics(self):
            if self.engine is None:
                return {}
            return {
                "sign_system": "three_valued",
                "initial_formulas": len(self.signed_formulas),
                "satisfiable": getattr(self, 'last_result', None),
                "rule_applications": self.rule_applications,
                "total_branches": len(self.branches)
            }
    
    return CompatTableau(signed_formula)

def wkrq_signed_tableau(signed_formula: SignedFormula):
    """
    Create a wKrQ signed tableau for compatibility.
    
    Args:
        signed_formula: Signed formula to build tableau for
        
    Returns:
        Tableau-like object with build() method
    """
    class CompatTableau:
        def __init__(self, sf):
            self.signed_formula = sf
            self.branches = []
            self.engine = None
            
        def build(self):
            from tableau_engine import TableauEngine
            self.engine = TableauEngine("wkrq")  
            result = self.engine.build_tableau([self.signed_formula])
            self.branches = self.engine.branches
            return result
            
        def extract_all_models(self):
            if self.engine is None:
                return []
            return self.engine.get_models()
    
    return CompatTableau(signed_formula)

# Legacy alias
ferguson_signed_tableau = wkrq_signed_tableau


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Truth values
    'TruthValue', 't', 'f', 'e',
    
    # Terms
    'Term', 'Constant', 'Variable', 'FunctionApplication',
    
    # Formulas
    'Formula', 'Atom', 'Predicate', 'Negation', 'Conjunction', 'Disjunction', 'Implication',
    
    # Signs
    'Sign', 'ClassicalSign', 'ThreeValuedSign', 'WkrqSign',
    
    # Signed formulas
    'SignedFormula',
    
    # Convenience functions
    'T', 'F', 'T3', 'F3', 'U', 'TF', 'FF', 'M', 'N',
    
    # Registry
    'SignRegistry',
    
    # Utility functions
    'create_signed_formula', 'dual_sign', 'parse_formula',
    
    # Compatibility functions
    'wk3_satisfiable', 'wk3_models',
    'classical_signed_tableau', 'three_valued_signed_tableau', 'wkrq_signed_tableau', 'ferguson_signed_tableau'
]