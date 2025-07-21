#!/usr/bin/env python3
"""
Test Suite for First-Order Predicate Logic Extensions

Tests the new Term hierarchy and Predicate classes for ground atomic formulas.
"""

import pytest
from term import Term, Constant, Variable, FunctionApplication, parse_term
from formula import Formula, Predicate, Atom, Negation, Conjunction


class TestTerm:
    """Test the Term hierarchy"""
    
    def test_constant_creation(self):
        """Test creating constants with valid names"""
        c1 = Constant("john")
        assert c1.name == "john"
        assert c1.is_ground()
        assert c1.get_variables() == set()
        
        c2 = Constant("c1")
        assert c2.name == "c1"
        
        c3 = Constant("mary_jane")
        assert c3.name == "mary_jane"
    
    def test_constant_naming_validation(self):
        """Test constant naming convention validation"""
        # Valid names
        Constant("john")
        Constant("c1") 
        Constant("a")
        Constant("object_1")
        
        # Invalid names
        with pytest.raises(ValueError):
            Constant("John")  # Starts with uppercase
        with pytest.raises(ValueError):
            Constant("")  # Empty
        with pytest.raises(ValueError):
            Constant("john-doe")  # Invalid character
    
    def test_variable_creation(self):
        """Test creating variables with valid names"""
        v1 = Variable("X")
        assert v1.name == "X"
        assert not v1.is_ground()
        assert v1.get_variables() == {"X"}
        
        v2 = Variable("Person")
        assert v2.name == "Person"
    
    def test_variable_naming_validation(self):
        """Test variable naming convention validation"""
        # Valid names
        Variable("X")
        Variable("Y")
        Variable("Person")
        Variable("Object_1")
        
        # Invalid names
        with pytest.raises(ValueError):
            Variable("x")  # Starts with lowercase
        with pytest.raises(ValueError):
            Variable("")  # Empty
        with pytest.raises(ValueError):
            Variable("X-Y")  # Invalid character
    
    def test_function_application(self):
        """Test function applications"""
        f0 = FunctionApplication("func", [])
        assert f0.arity == 0
        assert f0.is_ground()
        assert str(f0) == "func"
        
        f1 = FunctionApplication("succ", [Constant("c1")])
        assert f1.arity == 1
        assert f1.is_ground()
        assert str(f1) == "succ(c1)"
        
        f2 = FunctionApplication("plus", [Constant("a"), Constant("b")])
        assert f2.arity == 2
        assert f2.is_ground()
        assert str(f2) == "plus(a, b)"
    
    def test_function_with_variables(self):
        """Test function applications with variables"""
        f = FunctionApplication("f", [Variable("X"), Constant("c")])
        assert not f.is_ground()
        assert f.get_variables() == {"X"}
    
    def test_term_parsing(self):
        """Test parsing terms from strings"""
        # Constants (ground mode)
        c = parse_term("john")
        assert isinstance(c, Constant)
        assert c.name == "john"
        
        # Variables should raise error in ground mode
        with pytest.raises(ValueError, match="Variables not supported"):
            parse_term("X")


class TestPredicate:
    """Test the Predicate class"""
    
    def test_zero_ary_predicate(self):
        """Test 0-ary predicates (propositional atoms)"""
        p = Predicate("P", [])
        assert p.arity == 0
        assert str(p) == "P"
        assert p.is_atomic()
        assert p.is_literal()
        assert p.is_ground()
        assert p.get_variables() == set()
    
    def test_unary_predicate(self):
        """Test unary predicates"""
        pred = Predicate("Student", [Constant("john")])
        assert pred.arity == 1
        assert str(pred) == "Student(john)"
        assert pred.is_atomic()
        assert pred.is_literal()
        assert pred.is_ground()
        assert pred.get_variables() == set()
    
    def test_binary_predicate(self):
        """Test binary predicates"""
        pred = Predicate("Loves", [Constant("john"), Constant("mary")])
        assert pred.arity == 2
        assert str(pred) == "Loves(john, mary)"
        assert pred.is_atomic()
        assert pred.is_literal()
        assert pred.is_ground()
        assert pred.get_variables() == set()
    
    def test_ternary_predicate(self):
        """Test ternary predicates"""
        pred = Predicate("Between", [Constant("a"), Constant("b"), Constant("c")])
        assert pred.arity == 3
        assert str(pred) == "Between(a, b, c)"
        assert pred.is_atomic()
        assert pred.is_literal()
        assert pred.is_ground()
    
    def test_high_arity_predicate(self):
        """Test predicates with high arity"""
        args = [Constant(f"c{i}") for i in range(5)]
        pred = Predicate("R", args)
        assert pred.arity == 5
        assert str(pred) == "R(c0, c1, c2, c3, c4)"
        assert pred.is_ground()
    
    def test_predicate_with_variables(self):
        """Test predicates with variables (for future use)"""
        pred = Predicate("Loves", [Variable("X"), Constant("mary")])
        assert pred.arity == 2
        assert not pred.is_ground()
        assert pred.get_variables() == {"X"}
    
    def test_predicate_equality(self):
        """Test predicate equality"""
        p1 = Predicate("Loves", [Constant("john"), Constant("mary")])
        p2 = Predicate("Loves", [Constant("john"), Constant("mary")])
        p3 = Predicate("Loves", [Constant("mary"), Constant("john")])
        
        assert p1 == p2
        assert p1 != p3
    
    def test_predicate_hashing(self):
        """Test predicate hashing for use in sets"""
        p1 = Predicate("Student", [Constant("john")])
        p2 = Predicate("Student", [Constant("john")])
        p3 = Predicate("Student", [Constant("mary")])
        
        pred_set = {p1, p2, p3}
        assert len(pred_set) == 2  # p1 and p2 are the same


class TestAtomBackwardCompatibility:
    """Test that Atom class maintains backward compatibility"""
    
    def test_atom_creation(self):
        """Test creating atoms"""
        atom = Atom("p")
        assert atom.name == "p"
        assert atom.arity == 0
        assert str(atom) == "p"
        assert atom.is_atomic()
        assert atom.is_literal()
        assert atom.is_ground()
    
    def test_atom_predicate_equivalence(self):
        """Test that atoms and 0-ary predicates are compatible"""
        atom = Atom("p")
        pred = Predicate("p", [])
        
        # They should be equivalent in some sense
        assert atom.arity == pred.arity
        assert atom.is_atomic() == pred.is_atomic()
    
    def test_existing_functionality_preserved(self):
        """Test that existing Atom functionality still works"""
        p = Atom("p")
        q = Atom("q")
        
        # Test in formulas
        conj = Conjunction(p, Negation(q))
        assert str(conj) == "(p ∧ ¬q)"
        
        # Test equality
        p2 = Atom("p")
        assert p == p2
        assert p != q
        
        # Test hashing
        atom_set = {p, p2, q}
        assert len(atom_set) == 2


class TestFormulaExtensions:
    """Test that formula extensions work properly"""
    
    def test_negated_predicate(self):
        """Test negation of predicates"""
        pred = Predicate("Student", [Constant("john")])
        neg_pred = Negation(pred)
        
        assert str(neg_pred) == "¬Student(john)"
        assert neg_pred.is_literal()
        assert neg_pred.is_ground()
        assert neg_pred.get_variables() == set()
    
    def test_complex_formula_with_predicates(self):
        """Test complex formulas with predicates"""
        student_john = Predicate("Student", [Constant("john")])
        smart_john = Predicate("Smart", [Constant("john")])
        
        formula = Conjunction(student_john, smart_john)
        assert str(formula) == "(Student(john) ∧ Smart(john))"
        assert formula.is_ground()
        assert formula.get_variables() == set()
    
    def test_mixed_predicate_atom_formula(self):
        """Test formulas mixing old atoms and new predicates"""
        atom = Atom("p")
        pred = Predicate("Student", [Constant("john")])
        
        formula = Conjunction(atom, pred)
        assert str(formula) == "(p ∧ Student(john))"
        assert formula.is_ground()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])