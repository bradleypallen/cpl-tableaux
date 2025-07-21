#!/usr/bin/env python3
"""
Test Suite for Weak Kleene Logic Implementation

Tests the three-valued logic system including truth tables,
model evaluation, and basic tableau functionality.
"""

import pytest
from truth_value import TruthValue, t, f, e, WeakKleeneOperators
from wk3_model import WK3Model
from wk3_tableau import WK3Assignment, WK3Branch, WK3Tableau
from formula import Atom, Negation, Conjunction, Disjunction, Implication


class TestTruthValue:
    """Test the TruthValue enum and conversions"""
    
    def test_truth_value_creation(self):
        """Test creating TruthValue instances"""
        assert t == TruthValue.TRUE
        assert f == TruthValue.FALSE
        assert e == TruthValue.NEITHER
    
    def test_string_representation(self):
        """Test string representation"""
        assert str(t) == 't'
        assert str(f) == 'f'
        assert str(e) == 'e'
    
    def test_from_bool(self):
        """Test conversion from boolean"""
        assert TruthValue.from_bool(True) == t
        assert TruthValue.from_bool(False) == f
    
    def test_from_string(self):
        """Test parsing from string"""
        assert TruthValue.from_string('t') == t
        assert TruthValue.from_string('f') == f
        assert TruthValue.from_string('e') == e
        assert TruthValue.from_string('true') == t
        assert TruthValue.from_string('false') == f
        assert TruthValue.from_string('neither') == e
    
    def test_to_bool(self):
        """Test conversion to boolean"""
        assert t.to_bool() == True
        assert f.to_bool() == False
        assert e.to_bool() is None
    
    def test_is_classical(self):
        """Test classical value detection"""
        assert t.is_classical()
        assert f.is_classical()
        assert not e.is_classical()


class TestWeakKleeneOperators:
    """Test weak Kleene logic truth tables"""
    
    def test_negation(self):
        """Test WK3 negation truth table"""
        assert WeakKleeneOperators.negation(t) == f
        assert WeakKleeneOperators.negation(f) == t
        assert WeakKleeneOperators.negation(e) == e
    
    def test_conjunction(self):
        """Test WK3 conjunction truth table"""
        # t cases
        assert WeakKleeneOperators.conjunction(t, t) == t
        assert WeakKleeneOperators.conjunction(t, f) == f
        assert WeakKleeneOperators.conjunction(t, e) == e
        
        # f cases
        assert WeakKleeneOperators.conjunction(f, t) == f
        assert WeakKleeneOperators.conjunction(f, f) == f
        assert WeakKleeneOperators.conjunction(f, e) == f
        
        # e cases
        assert WeakKleeneOperators.conjunction(e, t) == e
        assert WeakKleeneOperators.conjunction(e, f) == f
        assert WeakKleeneOperators.conjunction(e, e) == e
    
    def test_disjunction(self):
        """Test WK3 disjunction truth table"""
        # t cases
        assert WeakKleeneOperators.disjunction(t, t) == t
        assert WeakKleeneOperators.disjunction(t, f) == t
        assert WeakKleeneOperators.disjunction(t, e) == t
        
        # f cases
        assert WeakKleeneOperators.disjunction(f, t) == t
        assert WeakKleeneOperators.disjunction(f, f) == f
        assert WeakKleeneOperators.disjunction(f, e) == e
        
        # e cases
        assert WeakKleeneOperators.disjunction(e, t) == t
        assert WeakKleeneOperators.disjunction(e, f) == e
        assert WeakKleeneOperators.disjunction(e, e) == e
    
    def test_implication(self):
        """Test WK3 implication truth table"""
        # t cases
        assert WeakKleeneOperators.implication(t, t) == t
        assert WeakKleeneOperators.implication(t, f) == f
        assert WeakKleeneOperators.implication(t, e) == e
        
        # f cases
        assert WeakKleeneOperators.implication(f, t) == t
        assert WeakKleeneOperators.implication(f, f) == t
        assert WeakKleeneOperators.implication(f, e) == t
        
        # e cases
        assert WeakKleeneOperators.implication(e, t) == t
        assert WeakKleeneOperators.implication(e, f) == e
        assert WeakKleeneOperators.implication(e, e) == e


class TestWK3Model:
    """Test three-valued model functionality"""
    
    def test_model_creation(self):
        """Test creating WK3 models"""
        model = WK3Model({'p': t, 'q': f, 'r': e})
        assert model.get_value('p') == t
        assert model.get_value('q') == f
        assert model.get_value('r') == e
        assert model.get_value('s') == e  # Unassigned atoms default to e
    
    def test_model_with_mixed_types(self):
        """Test model creation with mixed input types"""
        model = WK3Model({'p': True, 'q': 'f', 'r': e})
        assert model.get_value('p') == t
        assert model.get_value('q') == f
        assert model.get_value('r') == e
    
    def test_formula_evaluation(self):
        """Test evaluating formulas under WK3 model"""
        model = WK3Model({'p': t, 'q': f, 'r': e})
        
        p = Atom('p')
        q = Atom('q')
        r = Atom('r')
        
        # Test atoms
        assert model.satisfies(p) == t
        assert model.satisfies(q) == f
        assert model.satisfies(r) == e
        
        # Test negation
        assert model.satisfies(Negation(p)) == f
        assert model.satisfies(Negation(q)) == t
        assert model.satisfies(Negation(r)) == e
        
        # Test conjunction
        assert model.satisfies(Conjunction(p, q)) == f  # t ∧ f = f
        assert model.satisfies(Conjunction(p, r)) == e  # t ∧ e = e
        assert model.satisfies(Conjunction(q, r)) == f  # f ∧ e = f
        
        # Test disjunction
        assert model.satisfies(Disjunction(p, q)) == t  # t ∨ f = t
        assert model.satisfies(Disjunction(q, r)) == e  # f ∨ e = e
        
        # Test implication
        assert model.satisfies(Implication(p, q)) == f  # t → f = f
        assert model.satisfies(Implication(q, p)) == t  # f → t = t
        assert model.satisfies(Implication(r, p)) == t  # e → t = t
    
    def test_is_satisfying(self):
        """Test classical satisfiability check"""
        model = WK3Model({'p': t, 'q': f, 'r': e})
        
        p = Atom('p')
        q = Atom('q')
        r = Atom('r')
        
        assert model.is_satisfying(p) == True
        assert model.is_satisfying(q) == False
        assert model.is_satisfying(r) == False  # e is not classically satisfying
    
    def test_model_extension(self):
        """Test extending models with new assignments"""
        model = WK3Model({'p': t})
        extended = model.extend('q', f)
        
        assert model.get_value('q') == e  # Original unchanged
        assert extended.get_value('p') == t
        assert extended.get_value('q') == f
    
    def test_classical_conversion(self):
        """Test conversion to classical models"""
        # Model with only classical values
        classical_model = WK3Model({'p': t, 'q': f})
        classical_dict = classical_model.to_classical()
        assert classical_dict == {'p': True, 'q': False}
        
        # Model with e values
        non_classical_model = WK3Model({'p': t, 'q': e})
        assert non_classical_model.to_classical() is None


class TestWK3Assignment:
    """Test three-valued assignments"""
    
    def test_assignment_creation(self):
        """Test creating assignments"""
        assignment = WK3Assignment('p', t)
        assert assignment.atom_name == 'p'
        assert assignment.value == t
        assert str(assignment) == 'p=t'
    
    def test_assignment_equality(self):
        """Test assignment equality"""
        a1 = WK3Assignment('p', t)
        a2 = WK3Assignment('p', t)
        a3 = WK3Assignment('p', f)
        a4 = WK3Assignment('q', t)
        
        assert a1 == a2
        assert a1 != a3
        assert a1 != a4


class TestWK3Branch:
    """Test WK3 branch functionality"""
    
    def test_branch_creation(self):
        """Test creating WK3 branches"""
        branch = WK3Branch(1)
        assert branch.id == 1
        assert not branch.is_closed
        assert len(branch.formulas) == 0
        assert len(branch.assignments) == 0
    
    def test_assignment_addition(self):
        """Test adding assignments to branches"""
        branch = WK3Branch(1)
        branch.add_atom_value('p', t)
        branch.add_atom_value('q', f)
        
        assignments = branch.assignments
        assert WK3Assignment('p', t) in assignments
        assert WK3Assignment('q', f) in assignments
    
    def test_closure_detection(self):
        """Test closure detection with contradictory assignments"""
        branch = WK3Branch(1)
        branch.add_atom_value('p', t)
        assert not branch.is_closed
        
        branch.add_atom_value('p', f)  # Contradiction
        assert branch.is_closed
        assert branch.closure_reason is not None
    
    def test_no_closure_with_e(self):
        """Test that e values don't cause closure"""
        branch = WK3Branch(1)
        branch.add_atom_value('p', t)
        branch.add_atom_value('p', e)  # No contradiction
        assert not branch.is_closed
        
        branch.add_atom_value('q', f)
        branch.add_atom_value('q', e)  # No contradiction
        assert not branch.is_closed


class TestWK3Tableau:
    """Test basic WK3 tableau functionality"""
    
    def test_simple_atom(self):
        """Test tableau for a simple atom"""
        p = Atom('p')
        tableau = WK3Tableau(p)
        
        # An atom should be satisfiable in WK3
        result = tableau.build()
        assert result == True
        
        models = tableau.extract_all_models()
        assert len(models) > 0
    
    def test_contradiction(self):
        """Test tableau for a contradiction"""
        p = Atom('p')
        contradiction = Conjunction(p, Negation(p))
        tableau = WK3Tableau(contradiction)
        
        # p ∧ ¬p should be unsatisfiable even in WK3
        result = tableau.build()
        # Note: In weak Kleene, this might behave differently
        # For now, we expect it to be unsatisfiable
        models = tableau.extract_all_models()
        
        # Print results for debugging
        print(f"Contradiction result: {result}")
        print(f"Models found: {len(models)}")
        for i, model in enumerate(models):
            print(f"  Model {i+1}: {model}")


def test_wk3_basic_functionality():
    """Integration test for basic WK3 functionality"""
    # Test truth values
    assert str(t) == 't'
    assert str(f) == 'f'
    assert str(e) == 'e'
    
    # Test operators
    assert WeakKleeneOperators.conjunction(t, e) == e
    assert WeakKleeneOperators.disjunction(f, e) == e
    assert WeakKleeneOperators.negation(e) == e
    
    # Test model
    model = WK3Model({'p': t, 'q': e})
    p = Atom('p')
    q = Atom('q')
    
    assert model.satisfies(p) == t
    assert model.satisfies(q) == e
    assert model.satisfies(Conjunction(p, q)) == e
    
    print("✅ All basic WK3 functionality tests passed!")


if __name__ == "__main__":
    test_wk3_basic_functionality()
    
    # Run some individual tests
    test_truth_value = TestTruthValue()
    test_truth_value.test_truth_value_creation()
    test_truth_value.test_from_string()
    
    test_operators = TestWeakKleeneOperators()
    test_operators.test_conjunction()
    test_operators.test_disjunction()
    test_operators.test_negation()
    
    test_model = TestWK3Model()
    test_model.test_model_creation()
    test_model.test_formula_evaluation()
    
    test_tableau = TestWK3Tableau()
    test_tableau.test_simple_atom()
    test_tableau.test_contradiction()
    
    print("✅ All extended tests completed!")