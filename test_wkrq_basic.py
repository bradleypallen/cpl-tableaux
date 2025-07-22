#!/usr/bin/env python3
"""
Basic wKrQ Implementation Test

Tests the fundamental functionality of the wKrQ (Weak Kleene Logic with
Restricted Quantifiers) implementation to verify core components work.
"""

import sys
import traceback
from typing import Set, Tuple

# Import truth value system and operators
from truth_value import TruthValue, t, f, e, RestrictedQuantifierOperators

# Import formula classes
from formula import RestrictedExistentialQuantifier, RestrictedUniversalQuantifier, Predicate
from term import Variable, Constant

# Import wKrQ components
from wkrq_components import WKrQ_Branch, WKrQ_ModelExtractor


def test_restricted_quantifier_operators():
    """Test the restricted quantifier truth value operators"""
    print("Testing RestrictedQuantifierOperators...")
    
    # Test restricted existential quantifier
    # Case 1: ⟨t,t⟩ ∈ X → result should be t
    value_pairs = {(t, t), (f, e), (e, f)}
    result = RestrictedQuantifierOperators.restricted_existential(value_pairs)
    assert result == t, f"Expected t, got {result}"
    print("✓ Restricted existential with ⟨t,t⟩: t")
    
    # Case 2: All pairs have e component → result should be e  
    value_pairs = {(e, t), (f, e), (e, e)}
    result = RestrictedQuantifierOperators.restricted_existential(value_pairs)
    assert result == e, f"Expected e, got {result}"
    print("✓ Restricted existential with all e components: e")
    
    # Case 3: No ⟨t,t⟩ and some non-e pairs → result should be f
    value_pairs = {(t, f), (f, t), (e, e)}
    result = RestrictedQuantifierOperators.restricted_existential(value_pairs)
    assert result == f, f"Expected f, got {result}"
    print("✓ Restricted existential without ⟨t,t⟩: f")
    
    # Test restricted universal quantifier
    # Case 1: All pairs have e component → result should be e
    value_pairs = {(e, t), (f, e), (e, e)}
    result = RestrictedQuantifierOperators.restricted_universal(value_pairs)
    assert result == e, f"Expected e, got {result}"
    print("✓ Restricted universal with all e components: e")
    
    # Case 2: Contains ⟨t,f⟩ or ⟨t,e⟩ and non-e pair → result should be f  
    value_pairs = {(t, f), (f, t)}
    result = RestrictedQuantifierOperators.restricted_universal(value_pairs)
    assert result == f, f"Expected f, got {result}"
    print("✓ Restricted universal with critical pairs: f")
    
    # Case 3: No critical pairs and has non-e pair → result should be t
    value_pairs = {(t, t), (f, f)}
    result = RestrictedQuantifierOperators.restricted_universal(value_pairs)
    assert result == t, f"Expected t, got {result}"
    print("✓ Restricted universal without critical pairs: t")


def test_formula_classes():
    """Test the restricted quantifier formula classes"""
    print("\nTesting formula classes...")
    
    # Create test terms
    x = Variable("X")
    john = Constant("john")
    
    # Create predicates
    student_x = Predicate("Student", [x])
    student_john = Predicate("Student", [john])
    
    # Create restricted quantifiers
    exists_student = RestrictedExistentialQuantifier(x, student_x)
    all_student = RestrictedUniversalQuantifier(x, student_x)
    
    # Test string representations
    assert str(exists_student) == "∃̌X(Student(X))", f"Got: {str(exists_student)}"
    assert str(all_student) == "∀̌X(Student(X))", f"Got: {str(all_student)}"
    print("✓ Formula string representations correct")
    
    # Test properties
    assert not exists_student.is_atomic()
    assert not exists_student.is_literal()
    assert not exists_student.is_ground()
    print("✓ Formula properties correct")
    
    # Test variable extraction (bound variable should be excluded)
    free_vars = exists_student.get_variables()
    assert len(free_vars) == 0, f"Expected no free variables, got {free_vars}"
    print("✓ Free variable extraction correct")


def test_wkrq_branch():
    """Test the wKrQ branch implementation"""
    print("\nTesting WKrQ_Branch...")
    
    # Create branch
    branch = WKrQ_Branch(1)
    
    # Test basic properties
    assert branch.id == 1
    assert not branch.is_closed
    assert len(branch.formulas) == 0
    print("✓ Branch creation and basic properties")
    
    # Test domain management
    c1 = Constant("c1")
    c2 = Constant("c2")
    
    branch.add_to_domain(c1)
    branch.add_to_domain(c2)
    
    domain = branch.get_domain_constants()
    assert len(domain) == 2
    assert c1 in domain and c2 in domain
    print("✓ Domain management")
    
    # Test fresh constant generation
    fresh = branch.generate_fresh_constant("test")
    assert fresh.name.startswith("test_")
    assert fresh in branch.get_domain_constants()
    print("✓ Fresh constant generation")
    
    # Test predicate assignments
    branch.add_predicate_assignment("Student(john)", t)
    branch.add_predicate_assignment("Loves(john,mary)", f)
    
    assignments = branch.get_all_assignments()
    assert assignments["Student(john)"] == t
    assert assignments["Loves(john,mary)"] == f
    print("✓ Predicate assignments")
    
    # Test branch copying
    branch_copy = branch.copy()
    assert branch_copy.id == branch.id
    assert len(branch_copy.get_domain_constants()) == len(branch.get_domain_constants())
    assert branch_copy.get_all_assignments() == branch.get_all_assignments()
    print("✓ Branch copying")


def test_wkrq_model_extractor():
    """Test the wKrQ model extractor"""
    print("\nTesting WKrQ_ModelExtractor...")
    
    # Create branch with some content
    branch = WKrQ_Branch(1)
    branch.add_to_domain(Constant("john"))
    branch.add_to_domain(Constant("mary"))
    branch.add_predicate_assignment("Student(john)", t)
    branch.add_predicate_assignment("Student(mary)", f)
    
    # Extract model
    extractor = WKrQ_ModelExtractor()
    model = extractor.extract_model(branch)
    
    # Test model properties
    assert len(model.domain) == 2
    assert "john" in model.domain and "mary" in model.domain
    assert model.predicate_assignments["Student(john)"] == t
    assert model.predicate_assignments["Student(mary)"] == f
    print("✓ Model extraction")


def test_logic_system_registration():
    """Test that wKrQ logic system is properly registered"""
    print("\nTesting logic system registration...")
    
    try:
        # Import builtin_logics to trigger registration
        import builtin_logics
        from logic_system import get_logic_system, list_logic_systems
        
        # Check if wKrQ is registered
        logic_names = list_logic_systems()
        assert "wkrq" in logic_names, f"wkrq not found in {logic_names}"
        print("✓ wKrQ logic system registered")
        
        # Try to get the system
        wkrq_system = get_logic_system("wkrq")
        assert wkrq_system is not None, "Failed to retrieve wKrQ system"
        assert wkrq_system.config.supports_quantifiers == True
        assert wkrq_system.config.truth_values == 3
        print("✓ wKrQ logic system properties correct")
        
    except ImportError as e:
        print(f"⚠ Logic system registration test skipped: {e}")


def run_all_tests():
    """Run all basic wKrQ tests"""
    print("=" * 60)
    print("wKrQ Basic Implementation Test")
    print("=" * 60)
    
    tests = [
        test_restricted_quantifier_operators,
        test_formula_classes,
        test_wkrq_branch,
        test_wkrq_model_extractor,
        test_logic_system_registration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_func.__name__} FAILED:")
            print(f"Error: {e}")
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All basic wKrQ tests passed!")
        return True
    else:
        print("❌ Some tests failed - check implementation")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)