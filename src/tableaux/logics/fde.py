#!/usr/bin/env python3
"""
First-Degree Entailment (FDE) Logic Plugin

FDE is a four-valued logic system introduced by Nuel Belnap and developed by
Anderson and Belnap. It uses four truth values:
- T (true only)
- F (false only) 
- B (both true and false)
- N (neither true nor false)

This logic is paraconsistent (allows contradictions without explosion) and
paracomplete (some formulas are neither true nor false).

Key characteristics:
- Four truth values: T, F, B, N
- Conjunction and disjunction are De Morgan duals
- Negation swaps T↔F and B↔N
- No implication in basic FDE (though extensions exist)
- Used in databases, computer science, and philosophical logic
"""

from typing import Set, Iterator, Optional, Callable
from ..core.formula import ConnectiveSpec
from ..core.semantics import TruthValueSystem, TruthValue
from ..core.signs import SignSystem, Sign
from ..core.rules import RuleType, TableauRule, RulePattern
from .logic_system import LogicSystem


class FDETruthValue(TruthValue):
    """Truth values for FDE logic."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"FDETruthValue({self.name})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, FDETruthValue) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)


class FDETruthValueSystem(TruthValueSystem):
    """Four-valued truth system for FDE logic."""
    
    def __init__(self):
        self.t = FDETruthValue("T", "true only")
        self.f = FDETruthValue("F", "false only") 
        self.b = FDETruthValue("B", "both true and false")
        self.n = FDETruthValue("N", "neither true nor false")
    
    def truth_values(self) -> Set[TruthValue]:
        """Return all four truth values."""
        return {self.t, self.f, self.b, self.n}
    
    def designated_values(self) -> Set[TruthValue]:
        """Values that count as 'true' - T and B have some truth."""
        return {self.t, self.b}
    
    def anti_designated_values(self) -> Set[TruthValue]:
        """Values that count as 'false' - F and B have some falsity."""
        return {self.f, self.b}
    
    def evaluate_negation(self, value: TruthValue) -> TruthValue:
        """FDE negation: ~T=F, ~F=T, ~B=B, ~N=N"""
        if value == self.t:
            return self.f
        elif value == self.f:
            return self.t
        elif value == self.b:
            return self.b  # Both true and false stays both
        elif value == self.n:
            return self.n  # Neither stays neither
        else:
            raise ValueError(f"Unknown truth value: {value}")
    
    def evaluate_conjunction(self, left: TruthValue, right: TruthValue) -> TruthValue:
        """FDE conjunction: T∧F=F, T∧B=B, N∧anything=N, etc."""
        # If either is N (neither), result is N
        if left == self.n or right == self.n:
            return self.n
        
        # If either is F (false only), result depends on the other
        if left == self.f:
            if right == self.f:
                return self.f
            elif right == self.t:
                return self.f
            elif right == self.b:
                return self.f  # F∧B = F (false wins in conjunction)
        
        if right == self.f:
            if left == self.t:
                return self.f
            elif left == self.b:
                return self.f
        
        # T∧T = T
        if left == self.t and right == self.t:
            return self.t
        
        # B∧T = B, T∧B = B, B∧B = B
        if (left == self.b and right == self.t) or (left == self.t and right == self.b) or (left == self.b and right == self.b):
            return self.b
        
        raise ValueError(f"Unexpected conjunction: {left} ∧ {right}")
    
    def evaluate_disjunction(self, left: TruthValue, right: TruthValue) -> TruthValue:
        """FDE disjunction: dual of conjunction via De Morgan's laws."""
        # If either is N (neither), result is N
        if left == self.n or right == self.n:
            return self.n
        
        # If either is T (true only), result depends on the other
        if left == self.t:
            if right == self.t:
                return self.t
            elif right == self.f:
                return self.t
            elif right == self.b:
                return self.t  # T∨B = T (true wins in disjunction)
        
        if right == self.t:
            if left == self.f:
                return self.t
            elif left == self.b:
                return self.t
        
        # F∨F = F
        if left == self.f and right == self.f:
            return self.f
        
        # B∨F = B, F∨B = B, B∨B = B
        if (left == self.b and right == self.f) or (left == self.f and right == self.b) or (left == self.b and right == self.b):
            return self.b
        
        raise ValueError(f"Unexpected disjunction: {left} ∨ {right}")
    
    def name(self) -> str:
        return "FDE"
    
    def get_operation(self, connective: str) -> Optional[Callable]:
        """Get the semantic operation for a connective."""
        operations = {
            "&": self.evaluate_conjunction,
            "|": self.evaluate_disjunction,
            "~": self.evaluate_negation,
        }
        return operations.get(connective)


class FDESign(Sign):
    """Signs for FDE tableau system."""
    
    def __init__(self, symbol: str):
        if symbol not in ["T", "F", "B", "N"]:
            raise ValueError(f"Invalid FDE sign: {symbol}")
        self.symbol = symbol
    
    def __str__(self) -> str:
        return self.symbol
    
    def __eq__(self, other) -> bool:
        return isinstance(other, FDESign) and self.symbol == other.symbol
    
    def __hash__(self) -> int:
        return hash(("fde", self.symbol))
    
    def is_contradictory_with(self, other: Sign) -> bool:
        """Check if this sign contradicts another sign."""
        if not isinstance(other, FDESign):
            return False
        # In FDE tableau, T and F contradict when not combined with B
        return (self.symbol == "T" and other.symbol == "F") or \
               (self.symbol == "F" and other.symbol == "T")
    
    def get_symbol(self) -> str:
        """Get the symbol representing this sign.""" 
        return self.symbol


class FDESignSystem(SignSystem):
    """Sign system for FDE logic with four signs."""
    
    def __init__(self):
        self.t_sign = FDESign("T")  # True only
        self.f_sign = FDESign("F")  # False only  
        self.b_sign = FDESign("B")  # Both true and false
        self.n_sign = FDESign("N")  # Neither true nor false
    
    def signs(self) -> Set[Sign]:
        """Return all four signs."""
        return {self.t_sign, self.f_sign, self.b_sign, self.n_sign}
    
    def truth_conditions(self, sign: Sign) -> Set[TruthValue]:
        """Return truth values that satisfy this sign."""
        if sign == self.t_sign:
            return {FDETruthValue("T"), FDETruthValue("B")}  # T-signed formulas are true when T or B
        elif sign == self.f_sign:
            return {FDETruthValue("F"), FDETruthValue("B")}  # F-signed formulas are true when F or B
        elif sign == self.b_sign:
            return {FDETruthValue("B")}  # B-signed formulas are true only when B
        elif sign == self.n_sign:
            return {FDETruthValue("N")}  # N-signed formulas are true only when N
        else:
            return set()
    
    def find_contradictions(self, signed_formulas) -> list:
        """Find contradictory pairs of formulas."""
        # In FDE, there are no contradictions at the level of T and F signs
        # because both can be satisfied by the B (both) truth value
        # Only certain complex combinations would be contradictory
        
        # For now, implement no contradictions to maintain paraconsistency
        # A more sophisticated implementation would check for specific patterns
        # that are contradictory in FDE (like having all four signs for one formula)
        
        contradictions = []
        
        # Group formulas by their base formula  
        formula_signs = {}
        for sf in signed_formulas:
            base = str(sf.formula)
            if base not in formula_signs:
                formula_signs[base] = []
            formula_signs[base].append(sf)
        
        # Check for very specific contradictions in FDE
        for base, sfs in formula_signs.items():
            signs = {str(sf.sign) for sf in sfs}
            
            # In FDE, having all four signs T, F, B, N for one formula is contradictory
            if len(signs) == 4 and signs == {"T", "F", "B", "N"}:
                # This would be over-determined - contradictory in FDE
                t_formula = next(sf for sf in sfs if str(sf.sign) == "T")
                f_formula = next(sf for sf in sfs if str(sf.sign) == "F")
                contradictions.append((t_formula, f_formula))
        
        return contradictions
    
    def complementary_signs(self, sign: Sign) -> Set[Sign]:
        """Return signs that contradict this sign."""
        # In FDE tableau, T and F are complementary when not combined with B
        if str(sign) == "T":
            return {self.f_sign}
        elif str(sign) == "F":
            return {self.t_sign}
        else:
            return set()  # B and N don't have simple complements
    
    def sign_for_truth_value(self, value: TruthValue) -> Sign:
        """Return the sign corresponding to a truth value."""
        if isinstance(value, FDETruthValue):
            if value.name == "T":
                return self.t_sign
            elif value.name == "F":
                return self.f_sign
            elif value.name == "B":
                return self.b_sign
            elif value.name == "N":
                return self.n_sign
        raise ValueError(f"No FDE sign for truth value: {value}")
    
    def name(self) -> str:
        return "FDE"


class FDELogic(LogicSystem):
    """First-Degree Entailment (FDE) four-valued logic system."""
    
    def initialize(self):
        """Initialize FDE logic with connectives, semantics, and tableau rules."""
        # Add connectives (no implication in basic FDE)
        self.add_connective(ConnectiveSpec("&", 2, 3, "left", "infix"))  # conjunction
        self.add_connective(ConnectiveSpec("|", 2, 2, "left", "infix"))  # disjunction
        self.add_connective(ConnectiveSpec("~", 1, 4, "none", "prefix"))  # negation
        
        # Set semantic systems
        self.set_truth_system(FDETruthValueSystem())
        self.set_sign_system(FDESignSystem())
        
        # Add tableau rules
        self._add_fde_rules()
    
    def _add_fde_rules(self):
        """Add FDE tableau rules."""
        
        # T-Conjunction rules (T:A&B branches to T:A, T:B)
        self.add_rule(TableauRule(
            name="T-Conjunction",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "A & B")],
            conclusions=[["T:A", "T:B"]],
            priority=1
        ))
        
        # F-Conjunction rules (F:A&B branches to F:A | F:B)
        self.add_rule(TableauRule(
            name="F-Conjunction",
            rule_type=RuleType.BETA,  
            premises=[RulePattern("F", "A & B")],
            conclusions=[["F:A"], ["F:B"]],
            priority=2
        ))
        
        # B-Conjunction rules (B:A&B has complex behavior)
        self.add_rule(TableauRule(
            name="B-Conjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("B", "A & B")],
            conclusions=[["B:A", "T:B"], ["T:A", "B:B"], ["B:A", "B:B"]],
            priority=2
        ))
        
        # N-Conjunction rules (N:A&B branches)
        self.add_rule(TableauRule(
            name="N-Conjunction", 
            rule_type=RuleType.BETA,
            premises=[RulePattern("N", "A & B")],
            conclusions=[["N:A"], ["N:B"]],
            priority=2
        ))
        
        # T-Disjunction rules (T:A|B branches to T:A | T:B)
        self.add_rule(TableauRule(
            name="T-Disjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("T", "A | B")],
            conclusions=[["T:A"], ["T:B"]],
            priority=2
        ))
        
        # F-Disjunction rules (F:A|B branches to F:A, F:B)
        self.add_rule(TableauRule(
            name="F-Disjunction",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "A | B")],
            conclusions=[["F:A", "F:B"]],
            priority=1
        ))
        
        # B-Disjunction rules
        self.add_rule(TableauRule(
            name="B-Disjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("B", "A | B")],
            conclusions=[["B:A", "F:B"], ["F:A", "B:B"], ["B:A", "B:B"]],
            priority=2
        ))
        
        # N-Disjunction rules
        self.add_rule(TableauRule(
            name="N-Disjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("N", "A | B")],
            conclusions=[["N:A"], ["N:B"]],
            priority=2
        ))
        
        # Negation rules
        self.add_rule(TableauRule(
            name="T-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "~ A")],
            conclusions=[["F:A"]],
            priority=1
        ))
        
        self.add_rule(TableauRule(
            name="F-Negation", 
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("F", "~ A")],
            conclusions=[["T:A"]],
            priority=1
        ))
        
        self.add_rule(TableauRule(
            name="B-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("B", "~ A")],
            conclusions=[["B:A"]],  # ~B = B
            priority=1
        ))
        
        self.add_rule(TableauRule(
            name="N-Negation",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("N", "~ A")],
            conclusions=[["N:A"]],  # ~N = N
            priority=1
        ))


# Add FDE to the API
def add_fde_to_api():
    """Add FDE support to the LogicSystem API."""
    from ..api import LogicSystem as APILogicSystem
    from ..logics.logic_system import LogicRegistry
    
    @classmethod
    def fde(cls):
        """Create an FDE logic system."""
        if not LogicRegistry.is_registered("fde"):
            LogicRegistry.register(FDELogic("fde"))
        logic = LogicRegistry.get("fde")
        return cls(logic)
    
    # Add the method to the API class
    APILogicSystem.fde = fde


# Convenience functions
def fde() -> 'LogicSystem':
    """Quick access to FDE logic."""
    from ..api import LogicSystem
    add_fde_to_api()
    return LogicSystem.fde()