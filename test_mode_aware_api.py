#!/usr/bin/env python3
"""
Test Suite for Mode-Aware Programmatic API

Tests the programmatic interface that enforces mode separation
and prevents mixing of propositional and first-order syntax.
"""

import pytest
from logic_mode import LogicMode, ModeError
from mode_aware_tableau import (
    ModeAwareTableau, PropositionalBuilder, FirstOrderBuilder,
    propositional_tableau, first_order_tableau, auto_tableau
)
from formula import Atom, Predicate, Conjunction
from term import Constant


class TestModeAwareTableau:
    """Test the ModeAwareTableau class"""
    
    def test_propositional_tableau_creation(self):
        """Test creating propositional tableau"""
        p = Atom("p")
        tableau = propositional_tableau(p)
        
        assert tableau.logic_mode == LogicMode.PROPOSITIONAL
        assert tableau.truth_system == "classical"
        
        result = tableau.build()
        assert result == True  # p is satisfiable
    
    def test_first_order_tableau_creation(self):
        """Test creating first-order tableau"""
        pred = Predicate("Student", [Constant("john")])
        tableau = first_order_tableau(pred)
        
        assert tableau.logic_mode == LogicMode.FIRST_ORDER
        assert tableau.truth_system == "classical"
        
        result = tableau.build()
        assert result == True  # Student(john) is satisfiable
    
    def test_auto_detection_propositional(self):
        """Test automatic mode detection for propositional formulas"""
        p = Atom("p")
        tableau = auto_tableau(p)
        
        assert tableau.logic_mode == LogicMode.PROPOSITIONAL
    
    def test_auto_detection_first_order(self):
        """Test automatic mode detection for FOL formulas"""
        pred = Predicate("Student", [Constant("john")])
        tableau = auto_tableau(pred)
        
        assert tableau.logic_mode == LogicMode.FIRST_ORDER
    
    def test_mixed_mode_prevention(self):
        """Test that mixed modes are prevented"""
        # Create mixed formula using old API
        atom = Atom("p")
        pred = Predicate("Student", [Constant("john")])
        mixed = Conjunction(atom, pred)
        
        # Should be rejected regardless of mode
        with pytest.raises(ModeError, match="Formula inconsistent"):
            propositional_tableau(mixed)
        
        with pytest.raises(ModeError, match="Formula inconsistent"):
            first_order_tableau(mixed)
        
        # Auto-detection should also reject it
        with pytest.raises(ModeError, match="Formula inconsistent"):
            auto_tableau(mixed)
    
    def test_wk3_mode_support(self):
        """Test weak Kleene logic support with modes"""
        p = Atom("p")
        tableau = propositional_tableau(p, truth_system="wk3")
        
        assert tableau.truth_system == "wk3"
        result = tableau.build()
        assert result == True


class TestPropositionalBuilder:
    """Test the PropositionalBuilder class"""
    
    def test_valid_atom_creation(self):
        """Test creating valid propositional atoms"""
        p = PropositionalBuilder.atom("p")
        assert isinstance(p, Atom)
        assert p.name == "p"
        
        atom1 = PropositionalBuilder.atom("atom1")
        assert atom1.name == "atom1"
    
    def test_invalid_atom_rejection(self):
        """Test rejection of invalid atom names"""
        # Uppercase atoms not allowed in propositional mode
        with pytest.raises(ModeError, match="Invalid propositional atom"):
            PropositionalBuilder.atom("P")
        
        with pytest.raises(ModeError, match="Invalid propositional atom"):
            PropositionalBuilder.atom("ATOM")
    
    def test_formula_construction(self):
        """Test building complex propositional formulas"""
        p = PropositionalBuilder.atom("p")
        q = PropositionalBuilder.atom("q")
        
        # Test conjunction
        conj = PropositionalBuilder.conjunction(p, q)
        assert str(conj) == "(p ∧ q)"
        
        # Test disjunction
        disj = PropositionalBuilder.disjunction(p, q)
        assert str(disj) == "(p ∨ q)"
        
        # Test implication
        impl = PropositionalBuilder.implication(p, q)
        assert str(impl) == "(p → q)"
        
        # Test negation
        neg = PropositionalBuilder.negation(p)
        assert str(neg) == "¬p"
    
    def test_predicate_mixing_prevention(self):
        """Test that predicates cannot be mixed in propositional formulas"""
        p = PropositionalBuilder.atom("p")
        # Create predicate manually (bypassing FOL builder)
        pred = Predicate("Student", [Constant("john")])
        
        # Should reject mixing
        with pytest.raises(ModeError, match="Cannot mix predicate"):
            PropositionalBuilder.conjunction(p, pred)
        
        with pytest.raises(ModeError, match="Cannot mix predicate"):
            PropositionalBuilder.disjunction(p, pred)
        
        with pytest.raises(ModeError, match="Cannot mix predicate"):
            PropositionalBuilder.implication(p, pred)
        
        with pytest.raises(ModeError, match="Cannot mix predicate"):
            PropositionalBuilder.negation(pred)


class TestFirstOrderBuilder:
    """Test the FirstOrderBuilder class"""
    
    def test_predicate_creation(self):
        """Test creating predicates with validation"""
        # 0-ary predicate
        p = FirstOrderBuilder.predicate("P")
        assert isinstance(p, Predicate)
        assert p.arity == 0
        assert p.predicate_name == "P"
        
        # Unary predicate
        student = FirstOrderBuilder.predicate("Student", "john")
        assert student.arity == 1
        assert student.predicate_name == "Student"
        assert len(student.args) == 1
        assert student.args[0].name == "john"
        
        # Binary predicate
        loves = FirstOrderBuilder.predicate("Loves", "john", "mary")
        assert loves.arity == 2
        assert str(loves) == "Loves(john, mary)"
    
    def test_invalid_predicate_rejection(self):
        """Test rejection of invalid predicate names"""
        # Lowercase predicates not allowed
        with pytest.raises(ModeError, match="Invalid predicate name"):
            FirstOrderBuilder.predicate("student", "john")
        
        # Invalid constants
        with pytest.raises(ModeError, match="Invalid constant"):
            FirstOrderBuilder.predicate("Student", "John")  # Uppercase constant
    
    def test_formula_construction(self):
        """Test building complex FOL formulas"""
        student = FirstOrderBuilder.predicate("Student", "john")
        smart = FirstOrderBuilder.predicate("Smart", "john")
        
        # Test conjunction
        conj = FirstOrderBuilder.conjunction(student, smart)
        assert str(conj) == "(Student(john) ∧ Smart(john))"
        
        # Test disjunction
        disj = FirstOrderBuilder.disjunction(student, smart)
        assert str(disj) == "(Student(john) ∨ Smart(john))"
        
        # Test implication
        impl = FirstOrderBuilder.implication(student, smart)
        assert str(impl) == "(Student(john) → Smart(john))"
        
        # Test negation
        neg = FirstOrderBuilder.negation(student)
        assert str(neg) == "¬Student(john)"
    
    def test_atom_mixing_prevention(self):
        """Test that atoms cannot be mixed in FOL formulas"""
        pred = FirstOrderBuilder.predicate("Student", "john")
        # Create atom manually (bypassing prop builder)
        atom = Atom("p")
        
        # Should reject mixing
        with pytest.raises(ModeError, match="Cannot mix propositional atom"):
            FirstOrderBuilder.conjunction(pred, atom)
        
        with pytest.raises(ModeError, match="Cannot mix propositional atom"):
            FirstOrderBuilder.disjunction(pred, atom)
        
        with pytest.raises(ModeError, match="Cannot mix propositional atom"):
            FirstOrderBuilder.implication(pred, atom)
        
        with pytest.raises(ModeError, match="Cannot mix propositional atom"):
            FirstOrderBuilder.negation(atom)


class TestModeAwareAPI:
    """Test the overall mode-aware API behavior"""
    
    def test_clean_propositional_workflow(self):
        """Test complete propositional workflow"""
        # Build formula
        p = PropositionalBuilder.atom("p")
        q = PropositionalBuilder.atom("q")
        formula = PropositionalBuilder.implication(p, q)
        
        # Create tableau
        tableau = propositional_tableau(formula)
        
        # Analyze
        result = tableau.build()
        assert result == True
        
        # Extract models
        models = tableau.extract_all_models()
        assert len(models) > 0
    
    def test_clean_fol_workflow(self):
        """Test complete FOL workflow"""
        # Build formula
        student = FirstOrderBuilder.predicate("Student", "john")
        smart = FirstOrderBuilder.predicate("Smart", "john")
        formula = FirstOrderBuilder.implication(student, smart)
        
        # Create tableau
        tableau = first_order_tableau(formula)
        
        # Analyze
        result = tableau.build()
        assert result == True
        
        # Extract models
        models = tableau.extract_all_models()
        assert len(models) > 0
    
    def test_backward_compatibility_prevention(self):
        """Test that old mixed APIs are prevented"""
        # Old way that used to work but shouldn't now
        with pytest.raises(ModeError):
            # Mixed atom and predicate
            mixed = Conjunction(Atom("p"), Predicate("Student", [Constant("john")]))
            auto_tableau(mixed)
    
    def test_helpful_error_messages(self):
        """Test that error messages are helpful"""
        try:
            PropositionalBuilder.atom("P")
        except ModeError as e:
            assert "Invalid propositional atom" in str(e)
            assert "Use lowercase for atoms" in str(e)
        
        try:
            FirstOrderBuilder.predicate("student", "john")
        except ModeError as e:
            assert "Invalid predicate name" in str(e)
            assert "Use uppercase for predicates" in str(e)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])