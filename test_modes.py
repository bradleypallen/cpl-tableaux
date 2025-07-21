#!/usr/bin/env python3
"""
Test Suite for Mode-Aware Logic System

Tests the separation between propositional and first-order logic modes
with proper validation and error handling.
"""

import pytest
from logic_mode import LogicMode, ModeError, get_mode_validator, detect_mode_from_syntax
from mode_aware_parser import ModeAwareParser, parse_propositional, parse_first_order
from formula import Atom, Predicate, Conjunction, Negation
from term import Constant


class TestLogicMode:
    """Test LogicMode enum and utilities"""
    
    def test_logic_mode_creation(self):
        """Test creating LogicMode instances"""
        assert LogicMode.PROPOSITIONAL.name == "PROPOSITIONAL"
        assert LogicMode.FIRST_ORDER.name == "FIRST_ORDER"
    
    def test_logic_mode_string_conversion(self):
        """Test string representation"""
        assert str(LogicMode.PROPOSITIONAL) == "propositional"
        assert str(LogicMode.FIRST_ORDER) == "first-order"
    
    def test_logic_mode_from_string(self):
        """Test parsing from string"""
        assert LogicMode.from_string("prop") == LogicMode.PROPOSITIONAL
        assert LogicMode.from_string("propositional") == LogicMode.PROPOSITIONAL
        assert LogicMode.from_string("cpl") == LogicMode.PROPOSITIONAL
        
        assert LogicMode.from_string("fol") == LogicMode.FIRST_ORDER
        assert LogicMode.from_string("first-order") == LogicMode.FIRST_ORDER
        assert LogicMode.from_string("predicate") == LogicMode.FIRST_ORDER
        
        with pytest.raises(ValueError):
            LogicMode.from_string("invalid")
    
    def test_mode_detection(self):
        """Test automatic mode detection from syntax"""
        # Propositional formulas
        assert detect_mode_from_syntax("p & q") == LogicMode.PROPOSITIONAL
        assert detect_mode_from_syntax("p -> q") == LogicMode.PROPOSITIONAL
        
        # FOL formulas (contain predicate applications)
        assert detect_mode_from_syntax("Student(john)") == LogicMode.FIRST_ORDER
        assert detect_mode_from_syntax("Loves(a, b)") == LogicMode.FIRST_ORDER


class TestModeValidator:
    """Test mode validation rules"""
    
    def test_propositional_validation(self):
        """Test propositional mode validation"""
        validator = get_mode_validator(LogicMode.PROPOSITIONAL)
        
        # Valid propositional atoms
        assert validator.validate_atom_name("p")
        assert validator.validate_atom_name("q")
        assert validator.validate_atom_name("atom1")
        assert validator.validate_atom_name("myatom")
        
        # Invalid in propositional mode
        assert not validator.validate_atom_name("P")  # uppercase
        assert not validator.validate_atom_name("ATOM")  # uppercase
        
        # Predicates not allowed in propositional mode
        assert not validator.validate_predicate_name("Student")
        assert not validator.validate_predicate_name("P")
    
    def test_first_order_validation(self):
        """Test first-order mode validation"""
        validator = get_mode_validator(LogicMode.FIRST_ORDER)
        
        # Valid predicate names
        assert validator.validate_predicate_name("P")
        assert validator.validate_predicate_name("Student")
        assert validator.validate_predicate_name("LOVES")
        
        # Invalid predicate names  
        assert not validator.validate_predicate_name("p")  # lowercase
        assert not validator.validate_predicate_name("student")  # lowercase
        
        # Valid constant names
        assert validator.validate_constant_name("john")
        assert validator.validate_constant_name("c1")
        assert validator.validate_constant_name("mary")
        
        # Invalid constant names
        assert not validator.validate_constant_name("John")  # uppercase
        assert not validator.validate_constant_name("JOHN")  # uppercase
        
        # Atoms not allowed in FOL mode
        assert not validator.validate_atom_name("p")
        assert not validator.validate_atom_name("atom")


class TestModeAwareParser:
    """Test mode-aware parsing"""
    
    def test_propositional_parsing(self):
        """Test parsing propositional formulas"""
        parser = ModeAwareParser(LogicMode.PROPOSITIONAL)
        
        # Basic atoms
        formula = parser.parse("p")
        assert isinstance(formula, Atom)
        assert formula.name == "p"
        
        # Complex propositional formula
        formula = parser.parse("(p & q) -> r")
        assert str(formula) == "((p ∧ q) → r)"
        
        # With negation
        formula = parser.parse("~p | q")
        assert str(formula) == "(¬p ∨ q)"
    
    def test_first_order_parsing(self):
        """Test parsing first-order formulas"""
        parser = ModeAwareParser(LogicMode.FIRST_ORDER)
        
        # 0-ary predicate
        formula = parser.parse("P")
        assert isinstance(formula, Predicate)
        assert formula.arity == 0
        assert formula.predicate_name == "P"
        
        # Unary predicate
        formula = parser.parse("Student(john)")
        assert isinstance(formula, Predicate)
        assert formula.arity == 1
        assert formula.predicate_name == "Student"
        assert len(formula.args) == 1
        assert formula.args[0].name == "john"
        
        # Binary predicate
        formula = parser.parse("Loves(john, mary)")
        assert isinstance(formula, Predicate)
        assert formula.arity == 2
        assert str(formula) == "Loves(john, mary)"
        
        # Complex FOL formula
        formula = parser.parse("Student(john) & Loves(john, mary)")
        assert str(formula) == "(Student(john) ∧ Loves(john, mary))"
    
    def test_mode_violation_detection(self):
        """Test detection of mode violations"""
        prop_parser = ModeAwareParser(LogicMode.PROPOSITIONAL)
        fol_parser = ModeAwareParser(LogicMode.FIRST_ORDER)
        
        # FOL syntax in propositional mode
        with pytest.raises(ModeError, match="Invalid propositional atom"):
            prop_parser.parse("Student(john)")
        
        with pytest.raises(ModeError, match="Invalid propositional atom"):
            prop_parser.parse("P")  # uppercase atom
        
        # Propositional syntax in FOL mode
        with pytest.raises(ModeError, match="Invalid predicate name"):
            fol_parser.parse("p & q")
        
        with pytest.raises(ModeError, match="Invalid predicate name"):
            fol_parser.parse("atom1")  # lowercase predicate
    
    def test_helpful_error_messages(self):
        """Test that error messages provide helpful suggestions"""
        prop_parser = ModeAwareParser(LogicMode.PROPOSITIONAL)
        fol_parser = ModeAwareParser(LogicMode.FIRST_ORDER)
        
        # Wrong case in propositional mode
        try:
            prop_parser.parse("P & Q")
        except ModeError as e:
            assert "Use lowercase for atoms" in str(e)
        
        # Wrong case in FOL mode
        try:
            fol_parser.parse("student(john)")
        except ModeError as e:
            assert "Use uppercase for predicates" in str(e)
        
        # Wrong case for constants
        try:
            fol_parser.parse("Student(John)")
        except ModeError as e:
            assert "Invalid constant" in str(e)


class TestConvenienceFunctions:
    """Test convenience parsing functions"""
    
    def test_parse_propositional(self):
        """Test parse_propositional convenience function"""
        formula = parse_propositional("p & q -> r")
        assert str(formula) == "((p ∧ q) → r)"
        
        with pytest.raises(ModeError):
            parse_propositional("Student(john)")
    
    def test_parse_first_order(self):
        """Test parse_first_order convenience function"""
        formula = parse_first_order("Student(john) & Smart(john)")
        assert str(formula) == "(Student(john) ∧ Smart(john))"
        
        with pytest.raises(ModeError):
            parse_first_order("p & q")


class TestModeCoexistence:
    """Test that different modes can coexist without interference"""
    
    def test_separate_parsing(self):
        """Test that parsers don't interfere with each other"""
        # Parse same logical structure in different modes
        prop_formula = parse_propositional("p & q")
        fol_formula = parse_first_order("P & Q")  # 0-ary predicates
        
        # Should be different types
        assert isinstance(prop_formula.left, Atom)
        assert isinstance(fol_formula.left, Predicate)
        
        # But same logical structure
        assert str(prop_formula) == "(p ∧ q)"
        assert str(fol_formula) == "(P ∧ Q)"
    
    def test_mode_isolation(self):
        """Test that modes are properly isolated"""
        prop_parser = ModeAwareParser(LogicMode.PROPOSITIONAL)
        fol_parser = ModeAwareParser(LogicMode.FIRST_ORDER)
        
        # Each parser should maintain its own mode
        assert prop_parser.mode == LogicMode.PROPOSITIONAL
        assert fol_parser.mode == LogicMode.FIRST_ORDER
        
        # Mode settings should be independent
        prop_formula = prop_parser.parse("p")
        fol_formula = fol_parser.parse("P")
        
        assert isinstance(prop_formula, Atom)
        assert isinstance(fol_formula, Predicate)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])