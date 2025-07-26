#!/usr/bin/env python3
"""
Clean Modern API for Tableau Framework

This module provides the main user-facing API with modern Python patterns:
- Factory methods for logic systems
- Natural operator overloading for formulas  
- Clean result objects
- Type safety throughout
"""

from typing import List, Set, Optional, Union, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .core.formula import Formula, PropositionalAtom, CompoundFormula, ConnectiveSpec
from .core.semantics import Model, TruthValue
from .core.signs import SignedFormula, Sign
from .core.tableau_engine import TableauEngine, Tableau
from .logics.logic_system import LogicRegistry
from .logics.classical import ClassicalLogic
from .logics.weak_kleene import WeakKleeneLogic  
from .logics.wkrq import WkrqLogic


@dataclass
class TableauResult:
    """Clean result object for tableau solving."""
    satisfiable: bool
    models: List[Model]
    tableau: Optional[Tableau] = None
    steps: List[Any] = None
    
    @property
    def is_satisfiable(self) -> bool:
        """Check if the formula is satisfiable."""
        return self.satisfiable
    
    @property
    def is_unsatisfiable(self) -> bool:
        """Check if the formula is unsatisfiable."""
        return not self.satisfiable
    
    @property
    def model_count(self) -> int:
        """Get the number of models found."""
        return len(self.models)


class LogicFormula:
    """Enhanced formula with logic-system-specific operators and methods."""
    
    def __init__(self, base_formula: Formula, logic_system: 'LogicSystem'):
        self._base_formula = base_formula
        self._logic_system = logic_system
    
    def __str__(self) -> str:
        return str(self._base_formula)
    
    def __eq__(self, other) -> bool:
        if isinstance(other, LogicFormula):
            return self._base_formula == other._base_formula
        return self._base_formula == other
    
    def __hash__(self) -> int:
        return hash(self._base_formula)
    
    # Delegate to base formula
    def is_atomic(self) -> bool:
        return self._base_formula.is_atomic()
    
    def get_atoms(self) -> Set[str]:
        return self._base_formula.get_atoms()
    
    def get_subformulas(self) -> List[Formula]:
        return self._base_formula.get_subformulas()
    
    def get_main_connective(self) -> Optional[str]:
        return self._base_formula.get_main_connective()
    
    # Operator overloading for natural formula construction
    def __and__(self, other: 'LogicFormula') -> 'LogicFormula':
        """Conjunction: p & q"""
        spec = self._logic_system.get_connective_spec('&') or ConnectiveSpec("&", 2, 3)
        result = CompoundFormula(spec, self._base_formula, other._base_formula)
        return LogicFormula(result, self._logic_system)
    
    def __or__(self, other: 'LogicFormula') -> 'LogicFormula':
        """Disjunction: p | q"""
        spec = self._logic_system.get_connective_spec('|') or ConnectiveSpec("|", 2, 2)
        result = CompoundFormula(spec, self._base_formula, other._base_formula)
        return LogicFormula(result, self._logic_system)
    
    
    def implies(self, other: 'LogicFormula') -> 'LogicFormula':
        """Implication: p.implies(q) creates p -> q"""
        spec = self._logic_system.get_connective_spec('->') or ConnectiveSpec("->", 2, 1, "right")
        result = CompoundFormula(spec, self._base_formula, other._base_formula)
        return LogicFormula(result, self._logic_system)
    
    def __invert__(self) -> 'LogicFormula':
        """Negation: ~p"""
        spec = self._logic_system.get_connective_spec('~') or ConnectiveSpec("~", 1, 4, format_style="prefix")
        result = CompoundFormula(spec, self._base_formula)
        return LogicFormula(result, self._logic_system)
    
    # Sign methods for natural tableau construction
    @property
    def T(self) -> SignedFormula:
        """Create a true-signed formula."""
        return self._logic_system.create_signed_formula('T', self._base_formula)
    
    @property
    def F(self) -> SignedFormula:
        """Create a false-signed formula."""
        return self._logic_system.create_signed_formula('F', self._base_formula)
    
    @property
    def U(self) -> SignedFormula:
        """Create an undefined-signed formula (three-valued logic)."""
        return self._logic_system.create_signed_formula('U', self._base_formula)
    
    @property
    def B(self) -> SignedFormula:
        """Create a both-signed formula (FDE logic)."""
        return self._logic_system.create_signed_formula('B', self._base_formula)
    
    @property
    def M(self) -> SignedFormula:
        """Create an M-signed formula (wKrQ logic)."""
        return self._logic_system.create_signed_formula('M', self._base_formula)
    
    @property
    def N(self) -> SignedFormula:
        """Create an N-signed formula (wKrQ logic)."""
        return self._logic_system.create_signed_formula('N', self._base_formula)


class LogicSystem:
    """Modern interface to logic systems with clean API."""
    
    def __init__(self, internal_logic):
        self._logic = internal_logic
        self._engine = TableauEngine(internal_logic)
    
    @classmethod
    def classical(cls) -> 'LogicSystem':
        """Create a classical logic system."""
        if not LogicRegistry.is_registered("classical"):
            LogicRegistry.register(ClassicalLogic("classical"))
        logic = LogicRegistry.get("classical")
        return cls(logic)
    
    @classmethod
    def weak_kleene(cls) -> 'LogicSystem':
        """Create a weak Kleene three-valued logic system."""
        if not LogicRegistry.is_registered("weak_kleene"):
            LogicRegistry.register(WeakKleeneLogic("weak_kleene"))
        logic = LogicRegistry.get("weak_kleene")
        return cls(logic)
    
    @classmethod
    def wkrq(cls) -> 'LogicSystem':
        """Create a wKrQ four-valued logic system."""
        if not LogicRegistry.is_registered("wkrq"):
            LogicRegistry.register(WkrqLogic("wkrq"))
        logic = LogicRegistry.get("wkrq")
        return cls(logic)
    
    def atom(self, name: str) -> LogicFormula:
        """Create a single propositional atom."""
        base_atom = PropositionalAtom(name)
        return LogicFormula(base_atom, self)
    
    def atoms(self, *names: str) -> List[LogicFormula]:
        """Create multiple propositional atoms."""
        return [self.atom(name) for name in names]
    
    def create_logic_formula(self, base_formula: Formula) -> LogicFormula:
        """Wrap a base Formula object in a LogicFormula for this logic system."""
        return LogicFormula(base_formula, self)
    
    def get_connective_spec(self, symbol: str) -> Optional[ConnectiveSpec]:
        """Get connective specification for this logic system."""
        return self._logic.get_connective(symbol)
    
    def create_signed_formula(self, sign_str: str, formula: Formula) -> SignedFormula:
        """Create a signed formula with appropriate sign type for this logic."""
        sign_system = self._logic.get_sign_system()
        
        # Find the appropriate sign
        for sign in sign_system.signs():
            if str(sign) == sign_str:
                return SignedFormula(sign, formula)
        
        raise ValueError(f"Sign '{sign_str}' not supported in {self._logic.name} logic")
    
    def tableau(self, *signed_formulas: SignedFormula, track_steps: bool = False) -> Tableau:
        """Create a tableau for the given signed formulas."""
        formula_list = list(signed_formulas)
        return self._engine.build_tableau(formula_list, track_steps)
    
    def solve(self, formula: LogicFormula, sign: str = 'T', track_steps: bool = False) -> TableauResult:
        """
        Solve a formula by constructing a tableau.
        
        Args:
            formula: The formula to solve
            sign: The sign to use ('T', 'F', 'U', 'M', 'N')
            track_steps: Whether to track construction steps
            
        Returns:
            TableauResult with satisfiability, models, and optional steps
        """
        signed_formula = self.create_signed_formula(sign, formula._base_formula)
        tableau = self.tableau(signed_formula, track_steps=track_steps)
        
        satisfiable = not tableau.is_closed()
        models = tableau.extract_all_models() if satisfiable else []
        steps = tableau.steps if track_steps else None
        
        return TableauResult(
            satisfiable=satisfiable,
            models=models,
            tableau=tableau,
            steps=steps
        )
    
    def satisfiable(self, formula: LogicFormula, sign: str = 'T') -> bool:
        """Check if a formula is satisfiable."""
        return self.solve(formula, sign).satisfiable
    
    def unsatisfiable(self, formula: LogicFormula, sign: str = 'T') -> bool:
        """Check if a formula is unsatisfiable."""
        return not self.satisfiable(formula, sign)
    
    def models(self, formula: LogicFormula, sign: str = 'T') -> List[Model]:
        """Get all models for a formula."""
        return self.solve(formula, sign).models
    
    def valid(self, formula: LogicFormula) -> bool:
        """Check if a formula is valid (unsatisfiable when false)."""
        return self.unsatisfiable(formula, 'F')
    
    def entails(self, premises: List[LogicFormula], conclusion: LogicFormula) -> bool:
        """Check if premises entail conclusion."""
        # Create conjunction of premises and negation of conclusion
        if not premises:
            return self.valid(conclusion)
        
        premise_conjunction = premises[0]
        for premise in premises[1:]:
            premise_conjunction = premise_conjunction & premise
        
        # Check if (premises & ~conclusion) is unsatisfiable
        combined = premise_conjunction & (~conclusion)
        return self.unsatisfiable(combined)
    
    @property
    def name(self) -> str:
        """Get the name of this logic system."""
        return self._logic.name
    
    # Parser integration methods
    def parse(self, text: str) -> LogicFormula:
        """
        Parse a formula string into a LogicFormula object.
        
        Args:
            text: Formula string like "(p -> q) & p"
            
        Returns:
            LogicFormula object that can be used with solve(), etc.
            
        Example:
            formula = classical.parse("p | ~p")
            result = classical.solve(formula)
        """
        from .parser import parse_formula
        return parse_formula(self, text)
    
    def parse_and_solve(self, text: str, sign: str = 'T', track_steps: bool = False) -> TableauResult:
        """
        Parse a formula string and solve it directly.
        
        Args:
            text: Formula string like "(p -> q) & p & ~q"
            sign: Sign to use ('T', 'F', 'U', 'M', 'N')
            track_steps: Whether to track construction steps
            
        Returns:
            TableauResult with satisfiability, models, and optional steps
            
        Example:
            result = classical.parse_and_solve("(p -> q) & p & ~q")
            print(f"Satisfiable: {result.satisfiable}")
        """
        formula = self.parse(text)
        return self.solve(formula, sign, track_steps)
    
    def parse_and_entails(self, premises_text: List[str], conclusion_text: str) -> bool:
        """
        Parse premise and conclusion strings and check entailment.
        
        Args:
            premises_text: List of premise strings like ["p -> q", "p"]
            conclusion_text: Conclusion string like "q"
            
        Returns:
            True if premises entail conclusion, False otherwise
            
        Example:
            entails = classical.parse_and_entails(["p -> q", "p"], "q")
            assert entails == True  # Modus ponens
        """
        premises = [self.parse(p) for p in premises_text]
        conclusion = self.parse(conclusion_text)
        return self.entails(premises, conclusion)


# Convenience functions for quick access
def classical() -> LogicSystem:
    """Quick access to classical logic."""
    return LogicSystem.classical()

def weak_kleene() -> LogicSystem:
    """Quick access to weak Kleene logic."""
    return LogicSystem.weak_kleene()

def wkrq() -> LogicSystem:
    """Quick access to wKrQ logic."""
    return LogicSystem.wkrq()