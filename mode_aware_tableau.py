#!/usr/bin/env python3
"""
Mode-Aware Tableau Systems

Provides mode-aware tableau construction that enforces logical consistency
and prevents mixing of propositional and first-order syntax.
"""

from typing import Union, List, Optional
from logic_mode import LogicMode, ModeError, get_mode_validator
from formula import Formula, Atom, Predicate
from tableau import Tableau, Model
from wk3_tableau import WK3Tableau
from wk3_model import WK3Model


class ModeAwareTableau:
    """Tableau system that enforces mode consistency"""
    
    def __init__(self, formula: Formula, 
                 logic_mode: Optional[LogicMode] = None,
                 truth_system: str = "classical"):
        """
        Create a mode-aware tableau.
        
        Args:
            formula: The formula to analyze
            logic_mode: Explicit mode, or None for auto-detection
            truth_system: "classical" or "wk3"
        """
        # Auto-detect mode if not specified
        if logic_mode is None:
            logic_mode = self._detect_formula_mode(formula)
        
        self.logic_mode = logic_mode
        self.truth_system = truth_system
        self.validator = get_mode_validator(logic_mode)
        
        # Validate formula consistency with mode
        self._validate_formula_mode_consistency(formula)
        
        # Create appropriate underlying tableau
        if truth_system == "wk3":
            self._tableau = WK3Tableau(formula)
        else:
            self._tableau = Tableau(formula)
    
    def _detect_formula_mode(self, formula: Formula) -> LogicMode:
        """Auto-detect the logic mode from formula structure"""
        if self._contains_predicates(formula):
            return LogicMode.FIRST_ORDER
        else:
            return LogicMode.PROPOSITIONAL
    
    def _contains_predicates(self, formula: Formula) -> bool:
        """Check if formula contains any proper Predicate instances (not Atoms)"""
        from formula import Negation, Conjunction, Disjunction, Implication
        
        if isinstance(formula, Predicate) and not isinstance(formula, Atom):
            return True
        elif isinstance(formula, Atom):
            return False
        elif isinstance(formula, Negation):
            return self._contains_predicates(formula.operand)
        elif isinstance(formula, (Conjunction, Disjunction)):
            return (self._contains_predicates(formula.left) or 
                   self._contains_predicates(formula.right))
        elif isinstance(formula, Implication):
            return (self._contains_predicates(formula.antecedent) or 
                   self._contains_predicates(formula.consequent))
        else:
            return False
    
    def _validate_formula_mode_consistency(self, formula: Formula):
        """Validate that formula is consistent with the chosen mode"""
        issues = self._check_formula_consistency(formula)
        
        if issues:
            mode_name = self.logic_mode.name.lower().replace('_', ' ')
            error_msg = f"Formula inconsistent with {mode_name} mode:\n" + "\n".join(issues)
            suggestions = self.validator.get_syntax_description()
            raise ModeError(error_msg, self.logic_mode, suggestions)
    
    def _check_formula_consistency(self, formula: Formula) -> List[str]:
        """Check formula for mode consistency issues"""
        from formula import Negation, Conjunction, Disjunction, Implication
        
        issues = []
        
        if isinstance(formula, Atom):
            if self.logic_mode == LogicMode.PROPOSITIONAL:
                if not self.validator.validate_atom_name(formula.name):
                    issues.append(f"Invalid propositional atom: '{formula.name}' "
                                f"(use lowercase: '{formula.name.lower()}')")
            else:  # FOL mode
                issues.append(f"Propositional atom '{formula.name}' not allowed in FOL mode "
                            f"(use 0-ary predicate: '{formula.name.capitalize()}' instead)")
        
        elif isinstance(formula, Predicate):
            if self.logic_mode == LogicMode.PROPOSITIONAL:
                issues.append(f"Predicate '{formula.predicate_name}' not allowed in propositional mode "
                            f"(use atom: '{formula.predicate_name.lower()}' instead)")
            else:  # FOL mode
                if not self.validator.validate_predicate_name(formula.predicate_name):
                    issues.append(f"Invalid predicate name: '{formula.predicate_name}' "
                                f"(use uppercase: '{formula.predicate_name.capitalize()}')")
                
                # Check argument consistency
                for i, arg in enumerate(formula.args):
                    if hasattr(arg, 'name'):
                        if not self.validator.validate_constant_name(arg.name):
                            issues.append(f"Invalid constant in {formula.predicate_name}: '{arg.name}' "
                                        f"(use lowercase: '{arg.name.lower()}')")
        
        elif isinstance(formula, Negation):
            issues.extend(self._check_formula_consistency(formula.operand))
        
        elif isinstance(formula, (Conjunction, Disjunction)):
            issues.extend(self._check_formula_consistency(formula.left))
            issues.extend(self._check_formula_consistency(formula.right))
        
        elif isinstance(formula, Implication):
            issues.extend(self._check_formula_consistency(formula.antecedent))
            issues.extend(self._check_formula_consistency(formula.consequent))
        
        return issues
    
    def build(self) -> bool:
        """Build the tableau and return satisfiability"""
        return self._tableau.build()
    
    def build_with_models(self):
        """Build tableau and extract models"""
        return self._tableau.build_with_models()
    
    def extract_all_models(self):
        """Extract all satisfying models"""
        return self._tableau.extract_all_models()
    
    def get_sample_model(self):
        """Get one satisfying model"""
        return self._tableau.get_sample_model()
    
    def print_tree(self):
        """Print the tableau tree"""
        return self._tableau.print_tree()
    
    @property
    def branches(self):
        """Access to underlying branches"""
        return self._tableau.branches


# Convenience functions for different modes

def propositional_tableau(formula: Formula, truth_system: str = "classical") -> ModeAwareTableau:
    """Create a propositional logic tableau"""
    return ModeAwareTableau(formula, LogicMode.PROPOSITIONAL, truth_system)


def first_order_tableau(formula: Formula, truth_system: str = "classical") -> ModeAwareTableau:
    """Create a first-order logic tableau"""
    return ModeAwareTableau(formula, LogicMode.FIRST_ORDER, truth_system)


def auto_tableau(formula: Formula, truth_system: str = "classical") -> ModeAwareTableau:
    """Create a tableau with automatic mode detection"""
    return ModeAwareTableau(formula, None, truth_system)


# Mode-aware formula builders

class PropositionalBuilder:
    """Builder for propositional formulas with validation"""
    
    @staticmethod
    def atom(name: str) -> Atom:
        """Create a validated propositional atom"""
        validator = get_mode_validator(LogicMode.PROPOSITIONAL)
        if not validator.validate_atom_name(name):
            suggestions = validator.get_error_suggestions(name, "atom")
            raise ModeError(f"Invalid propositional atom: '{name}'", 
                          LogicMode.PROPOSITIONAL, suggestions)
        return Atom(name)
    
    @staticmethod
    def conjunction(left: Formula, right: Formula) -> Formula:
        """Create conjunction with mode validation"""
        from formula import Conjunction
        # Validate both operands are propositional (not predicates with arity > 0)
        for operand in [left, right]:
            if isinstance(operand, Predicate) and not isinstance(operand, Atom):
                raise ModeError(f"Cannot mix predicate {operand} in propositional formula",
                              LogicMode.PROPOSITIONAL)
        return Conjunction(left, right)
    
    @staticmethod
    def disjunction(left: Formula, right: Formula) -> Formula:
        """Create disjunction with mode validation"""
        from formula import Disjunction
        for operand in [left, right]:
            if isinstance(operand, Predicate) and not isinstance(operand, Atom):
                raise ModeError(f"Cannot mix predicate {operand} in propositional formula",
                              LogicMode.PROPOSITIONAL)
        return Disjunction(left, right)
    
    @staticmethod
    def implication(antecedent: Formula, consequent: Formula) -> Formula:
        """Create implication with mode validation"""
        from formula import Implication
        for operand in [antecedent, consequent]:
            if isinstance(operand, Predicate) and not isinstance(operand, Atom):
                raise ModeError(f"Cannot mix predicate {operand} in propositional formula",
                              LogicMode.PROPOSITIONAL)
        return Implication(antecedent, consequent)
    
    @staticmethod
    def negation(operand: Formula) -> Formula:
        """Create negation with mode validation"""
        from formula import Negation
        if isinstance(operand, Predicate) and not isinstance(operand, Atom):
            raise ModeError(f"Cannot mix predicate {operand} in propositional formula",
                          LogicMode.PROPOSITIONAL)
        return Negation(operand)


class FirstOrderBuilder:
    """Builder for first-order formulas with validation"""
    
    @staticmethod
    def predicate(name: str, *args) -> Predicate:
        """Create a validated predicate"""
        from term import Constant
        validator = get_mode_validator(LogicMode.FIRST_ORDER)
        
        if not validator.validate_predicate_name(name):
            suggestions = validator.get_error_suggestions(name, "predicate")
            raise ModeError(f"Invalid predicate name: '{name}'",
                          LogicMode.FIRST_ORDER, suggestions)
        
        # Validate and convert arguments to Constants
        term_args = []
        for arg in args:
            if isinstance(arg, str):
                if not validator.validate_constant_name(arg):
                    suggestions = validator.get_error_suggestions(arg, "constant")
                    raise ModeError(f"Invalid constant: '{arg}'",
                                  LogicMode.FIRST_ORDER, suggestions)
                term_args.append(Constant(arg))
            else:
                # Assume it's already a Term
                term_args.append(arg)
        
        return Predicate(name, term_args)
    
    @staticmethod
    def conjunction(left: Formula, right: Formula) -> Formula:
        """Create conjunction with mode validation"""
        from formula import Conjunction
        for operand in [left, right]:
            if isinstance(operand, Atom):
                raise ModeError(f"Cannot mix propositional atom {operand} in FOL formula",
                              LogicMode.FIRST_ORDER)
        return Conjunction(left, right)
    
    @staticmethod
    def disjunction(left: Formula, right: Formula) -> Formula:
        """Create disjunction with mode validation"""  
        from formula import Disjunction
        for operand in [left, right]:
            if isinstance(operand, Atom):
                raise ModeError(f"Cannot mix propositional atom {operand} in FOL formula",
                              LogicMode.FIRST_ORDER)
        return Disjunction(left, right)
    
    @staticmethod
    def implication(antecedent: Formula, consequent: Formula) -> Formula:
        """Create implication with mode validation"""
        from formula import Implication
        for operand in [antecedent, consequent]:
            if isinstance(operand, Atom):
                raise ModeError(f"Cannot mix propositional atom {operand} in FOL formula",
                              LogicMode.FIRST_ORDER)
        return Implication(antecedent, consequent)
    
    @staticmethod
    def negation(operand: Formula) -> Formula:
        """Create negation with mode validation"""
        from formula import Negation
        if isinstance(operand, Atom):
            raise ModeError(f"Cannot mix propositional atom {operand} in FOL formula",
                          LogicMode.FIRST_ORDER)
        return Negation(operand)


# Export commonly used items
__all__ = [
    'ModeAwareTableau', 'PropositionalBuilder', 'FirstOrderBuilder',
    'propositional_tableau', 'first_order_tableau', 'auto_tableau'
]