#!/usr/bin/env python3
"""Tutorial 7: Extending with New Logic Systems"""

from tableau_core import *
from unified_model import UnifiedModel
from typing import Dict, Union, List
from abc import ABC, abstractmethod

# Four-valued logic implementation from Tutorial 7
class FourValuedTruthValue:
    """Four-valued truth system: TRUE, FALSE, BOTH, NEITHER"""
    
    def __init__(self, value: str):
        if value not in {'TRUE', 'FALSE', 'BOTH', 'NEITHER'}:
            raise ValueError(f"Invalid four-valued truth value: {value}")
        self.value = value
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f"FourValuedTruthValue('{self.value}')"
    
    def __eq__(self, other):
        return isinstance(other, FourValuedTruthValue) and self.value == other.value
    
    def __hash__(self):
        return hash(self.value)

# Four-valued truth constants
TRUE = FourValuedTruthValue('TRUE')
FALSE = FourValuedTruthValue('FALSE')
BOTH = FourValuedTruthValue('BOTH')
NEITHER = FourValuedTruthValue('NEITHER')

class FourValuedModel(UnifiedModel):
    """Model for four-valued logic system"""
    
    def __init__(self, assignments: Dict[str, Union[str, FourValuedTruthValue]]):
        self._assignments = {}
        for atom, value in assignments.items():
            if isinstance(value, FourValuedTruthValue):
                self._assignments[atom] = value
            elif isinstance(value, str) and value in {'TRUE', 'FALSE', 'BOTH', 'NEITHER'}:
                self._assignments[atom] = FourValuedTruthValue(value)
            else:
                raise ValueError(f"Invalid four-valued truth value for {atom}: {value}")
    
    def satisfies(self, formula: Formula) -> FourValuedTruthValue:
        """Evaluate formula under four-valued semantics"""
        return self._evaluate_four_valued(formula)
    
    def is_satisfying(self, formula: Formula) -> bool:
        """Check if model satisfies formula (TRUE or BOTH)"""
        result = self._evaluate_four_valued(formula)
        return result.value in {'TRUE', 'BOTH'}
    
    def get_assignment(self, atom_name: str) -> FourValuedTruthValue:
        """Get four-valued assignment for atom"""
        return self._assignments.get(atom_name, NEITHER)
    
    @property
    def assignments(self) -> Dict[str, FourValuedTruthValue]:
        """Get all assignments"""
        return self._assignments.copy()
    
    def _evaluate_four_valued(self, formula: Formula) -> FourValuedTruthValue:
        """Evaluate formula using four-valued semantics"""
        if isinstance(formula, Atom):
            return self._assignments.get(formula.name, NEITHER)
        elif isinstance(formula, Negation):
            operand_value = self._evaluate_four_valued(formula.operand)
            # Negation: TRUE->FALSE, FALSE->TRUE, BOTH->BOTH, NEITHER->NEITHER
            negation_map = {
                'TRUE': FALSE,
                'FALSE': TRUE,
                'BOTH': BOTH,
                'NEITHER': NEITHER
            }
            return negation_map[operand_value.value]
        elif isinstance(formula, Conjunction):
            left_value = self._evaluate_four_valued(formula.left)
            right_value = self._evaluate_four_valued(formula.right)
            # Simplified conjunction - can be extended with full truth table
            if left_value == TRUE and right_value == TRUE:
                return TRUE
            elif left_value == FALSE or right_value == FALSE:
                return FALSE
            elif left_value == BOTH or right_value == BOTH:
                return BOTH
            else:
                return NEITHER
        elif isinstance(formula, Disjunction):
            left_value = self._evaluate_four_valued(formula.left)
            right_value = self._evaluate_four_valued(formula.right)
            # Simplified disjunction
            if left_value == TRUE or right_value == TRUE:
                return TRUE
            elif left_value == FALSE and right_value == FALSE:
                return FALSE
            elif left_value == BOTH or right_value == BOTH:
                return BOTH
            else:
                return NEITHER
        else:
            return NEITHER  # Default for unknown formulas
    
    def __str__(self) -> str:
        if not self._assignments:
            return "{}"
        
        sorted_items = sorted(self._assignments.items())
        assignment_strs = [f"{atom}={value}" for atom, value in sorted_items]
        return "{" + ", ".join(assignment_strs) + "}"
    
    def __repr__(self) -> str:
        return f"FourValuedModel({self._assignments})"

# Modal logic extension from Tutorial 7
class ModalFormula(Formula):
    """Base class for modal formulas"""
    pass

class Box(ModalFormula):
    """Necessity operator (□φ)"""
    
    def __init__(self, operand: Formula):
        self.operand = operand
    
    def is_atomic(self) -> bool:
        """Modal operators are not atomic"""
        return False
    
    def is_literal(self) -> bool:
        """Modal operators are not literals"""
        return False
    
    def __str__(self):
        return f"□{self.operand}"
    
    def __repr__(self):
        return f"Box({self.operand!r})"
    
    def __eq__(self, other):
        return isinstance(other, Box) and self.operand == other.operand
    
    def __hash__(self):
        return hash(('Box', self.operand))

class Diamond(ModalFormula):
    """Possibility operator (◇φ)"""
    
    def __init__(self, operand: Formula):
        self.operand = operand
    
    def is_atomic(self) -> bool:
        """Modal operators are not atomic"""
        return False
    
    def is_literal(self) -> bool:
        """Modal operators are not literals"""
        return False
    
    def __str__(self):
        return f"◇{self.operand}"
    
    def __repr__(self):
        return f"Diamond({self.operand!r})"
    
    def __eq__(self, other):
        return isinstance(other, Diamond) and self.operand == other.operand
    
    def __hash__(self):
        return hash(('Diamond', self.operand))

class ModalModel(UnifiedModel):
    """Simplified modal model with possible worlds"""
    
    def __init__(self, worlds: Dict[str, Dict[str, bool]], accessibility: Dict[str, List[str]], current_world: str = "w0"):
        self.worlds = worlds  # world -> {atom -> bool}
        self.accessibility = accessibility  # world -> [accessible_worlds]
        self.current_world = current_world
    
    def satisfies(self, formula: Formula) -> bool:
        """Evaluate formula in current world"""
        return self._evaluate_modal(formula, self.current_world)
    
    def is_satisfying(self, formula: Formula) -> bool:
        """Check if model satisfies formula in current world"""
        return self.satisfies(formula)
    
    def get_assignment(self, atom_name: str) -> bool:
        """Get assignment for atom in current world"""
        return self.worlds.get(self.current_world, {}).get(atom_name, False)
    
    @property
    def assignments(self) -> Dict[str, bool]:
        """Get assignments in current world"""
        return self.worlds.get(self.current_world, {}).copy()
    
    def _evaluate_modal(self, formula: Formula, world: str) -> bool:
        """Evaluate formula in specific world"""
        if isinstance(formula, Atom):
            return self.worlds.get(world, {}).get(formula.name, False)
        elif isinstance(formula, Negation):
            return not self._evaluate_modal(formula.operand, world)
        elif isinstance(formula, Conjunction):
            return (self._evaluate_modal(formula.left, world) and 
                   self._evaluate_modal(formula.right, world))
        elif isinstance(formula, Disjunction):
            return (self._evaluate_modal(formula.left, world) or 
                   self._evaluate_modal(formula.right, world))
        elif isinstance(formula, Box):
            # □φ is true iff φ is true in all accessible worlds
            accessible_worlds = self.accessibility.get(world, [])
            return all(self._evaluate_modal(formula.operand, w) for w in accessible_worlds)
        elif isinstance(formula, Diamond):
            # ◇φ is true iff φ is true in some accessible world
            accessible_worlds = self.accessibility.get(world, [])
            return any(self._evaluate_modal(formula.operand, w) for w in accessible_worlds)
        else:
            return False
    
    def __str__(self) -> str:
        return f"ModalModel(current={self.current_world}, worlds={len(self.worlds)})"
    
    def __repr__(self) -> str:
        return f"ModalModel(worlds={self.worlds}, accessibility={self.accessibility}, current='{self.current_world}')"

def test_four_valued_logic():
    """Test the four-valued logic implementation"""
    
    print("=== FOUR-VALUED LOGIC TEST ===\n")
    
    # Create test model
    model = FourValuedModel({
        'p': 'TRUE',
        'q': 'FALSE',
        'r': 'BOTH'
    })
    
    # Test atoms
    p = Atom('p')
    q = Atom('q')
    r = Atom('r')
    
    print("Model assignments:")
    for atom, value in model.assignments.items():
        print(f"  {atom} = {value}")
    print()
    
    # Test formulas
    test_cases = [
        ("p", p),
        ("q", q), 
        ("r", r),
        ("¬p", Negation(p)),
        ("¬q", Negation(q)),
        ("¬r", Negation(r)),
        ("p ∧ q", Conjunction(p, q)),
        ("p ∨ q", Disjunction(p, q)),
        ("r ∧ p", Conjunction(r, p))
    ]
    
    print("Formula evaluations:")
    for description, formula in test_cases:
        result = model.satisfies(formula)
        satisfying = model.is_satisfying(formula)
        print(f"  {description:<8} = {result} (satisfying: {satisfying})")
    
    print(f"\nModel: {model}")

def test_modal_logic():
    """Test the modal logic implementation"""
    
    print("\n=== MODAL LOGIC TEST ===\n")
    
    # Create modal model with two worlds
    worlds = {
        'w0': {'p': True, 'q': False},
        'w1': {'p': False, 'q': True}
    }
    accessibility = {
        'w0': ['w1'],  # w0 can access w1
        'w1': []       # w1 has no accessible worlds
    }
    
    model = ModalModel(worlds, accessibility, 'w0')
    
    print(f"Modal model: {model}")
    print("World assignments:")
    for world, assignments in worlds.items():
        assignment_strs = [f"{atom}={value}" for atom, value in assignments.items()]
        print(f"  {world}: {{{', '.join(assignment_strs)}}}")
    print(f"Accessibility: {accessibility}")
    print()
    
    # Test modal formulas
    p = Atom('p')
    q = Atom('q')
    
    test_cases = [
        ("p", p),
        ("q", q),
        ("□p", Box(p)),
        ("□q", Box(q)),
        ("◇p", Diamond(p)),
        ("◇q", Diamond(q)),
        ("□(p ∨ q)", Box(Disjunction(p, q))),
        ("◇(p ∧ q)", Diamond(Conjunction(p, q)))
    ]
    
    print("Modal formula evaluations (in w0):")
    for description, formula in test_cases:
        try:
            result = model.satisfies(formula)
            print(f"  {description:<12} = {result}")
        except Exception as e:
            print(f"  {description:<12} = ERROR: {e}")

def test_logic_comparison():
    """Compare different logic systems"""
    
    print("\n=== LOGIC SYSTEM COMPARISON ===\n")
    
    # Test formula: p ∨ ¬p (should behave differently in different logics)
    p = Atom('p')
    formula = Disjunction(p, Negation(p))
    
    print(f"Formula: {formula}")
    print("Evaluation in different logic systems:")
    
    # Classical logic - always true
    try:
        classical_tableau = classical_signed_tableau(T(formula))
        classical_result = classical_tableau.build()
        print(f"  Classical:    {'SAT' if classical_result else 'UNSAT'}")
    except Exception as e:
        print(f"  Classical:    ERROR: {e}")
    
    # WK3 logic - use tableau approach
    try:
        t3_tableau = three_valued_signed_tableau(T3(formula))
        u_tableau = three_valued_signed_tableau(U(formula))
        wk3_result = t3_tableau.build() or u_tableau.build()
        print(f"  WK3:          {'SAT' if wk3_result else 'UNSAT'}")
    except Exception as e:
        print(f"  WK3:          ERROR: {e}")
    
    # Four-valued logic - test with different models
    four_valued_models = [
        FourValuedModel({'p': 'TRUE'}),
        FourValuedModel({'p': 'FALSE'}),
        FourValuedModel({'p': 'BOTH'}),
        FourValuedModel({'p': 'NEITHER'})
    ]
    
    print("  Four-valued:")
    for i, model in enumerate(four_valued_models):
        p_value = model.get_assignment('p')
        result = model.satisfies(formula)
        satisfying = model.is_satisfying(formula)
        print(f"    p={p_value}: {result} (satisfying: {satisfying})")

if __name__ == "__main__":
    test_four_valued_logic()
    test_modal_logic()
    test_logic_comparison()