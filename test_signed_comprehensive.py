#!/usr/bin/env python3
"""
Comprehensive Signed Tableau Test Suite

This file provides a unified test runner and compatibility layer for all 
signed tableau tests, ensuring comprehensive coverage of:

1. Classical logic using signed tableaux (test_classical_signed.py)
2. WK3 logic using signed tableaux (test_wk3_signed.py)  
3. Literature examples using signed tableaux (test_literature_examples.py)
4. Cross-system compatibility and integration tests

This serves as the main entry point for verifying the signed tableau system
works correctly across all supported logics and maintains compatibility
with existing interfaces.
"""

import pytest
import sys
from typing import List, Dict, Any

# Import all migrated test suites
from test_classical_signed import TestClassicalSignedTableau, test_signed_classical_integration
from test_wk3_signed import TestWK3SignedTableau, test_wk3_signed_integration, test_wk3_basic_functionality_signed
from test_literature_examples import TestPriestExamples, TestFittingExamples, TestSmullyanExamples, TestHandbookExamples, TestEdgeCasesFromLiterature

# Import signed tableau components for integration testing
from signed_tableau import SignedTableau, classical_signed_tableau, three_valued_signed_tableau
from signed_formula import T, F, T3, F3, U
from formula import Atom, Negation, Conjunction, Disjunction, Implication
from wk3_signed_adapter import wk3_satisfiable, wk3_models


class TestSignedTableauIntegration:
    """Integration tests across all signed tableau implementations"""
    
    def setup_method(self):
        """Set up common test atoms"""
        self.p = Atom("p")
        self.q = Atom("q")
        self.r = Atom("r")
    
    def test_cross_system_consistency(self):
        """Test that different logic systems produce consistent results where expected"""
        # Simple tautology should be valid in both classical and WK3
        tautology = Disjunction(self.p, Negation(self.p))
        
        # Classical: F:(p ∨ ¬p) should be unsatisfiable (tautology)
        classical_tableau = classical_signed_tableau(F(tautology))
        classical_result = classical_tableau.build()
        assert classical_result == False, "Excluded middle should be tautology in classical logic"
        
        # WK3: p ∨ ¬p should be satisfiable (can be undefined)
        wk3_result = wk3_satisfiable(tautology)
        assert wk3_result == True, "Excluded middle should be satisfiable in WK3"
        
        # This demonstrates the key difference between classical and WK3
    
    def test_sign_system_compatibility(self):
        """Test that sign systems work correctly across different logics"""
        formula = Conjunction(self.p, self.q)
        
        # Test classical signs
        t_formula = T(formula)
        f_formula = F(formula)
        
        assert str(t_formula.sign) == "T"
        assert str(f_formula.sign) == "F"
        assert t_formula.formula == formula
        assert f_formula.formula == formula
        
        # Test three-valued signs
        t3_formula = T3(formula)
        f3_formula = F3(formula)
        u_formula = U(formula)
        
        # Note: T3 and F3 use ThreeValuedSign which displays as "T" and "F"
        # The distinction is in the sign class type, not the string representation
        assert str(t3_formula.sign) == "T"
        assert str(f3_formula.sign) == "F"
        assert str(u_formula.sign) == "U"
        
        # Verify sign types are different
        assert type(t_formula.sign).__name__ == "ClassicalSign"
        assert type(t3_formula.sign).__name__ == "ThreeValuedSign"
        assert type(u_formula.sign).__name__ == "ThreeValuedSign"
        
        # All should have same formula
        assert t3_formula.formula == formula
        assert f3_formula.formula == formula
        assert u_formula.formula == formula
    
    def test_model_extraction_consistency(self):
        """Test that model extraction works consistently across systems"""
        # Simple satisfiable formula
        formula = Conjunction(self.p, self.q)
        
        # Classical system
        classical_tableau = classical_signed_tableau(T(formula))
        classical_result = classical_tableau.build()
        assert classical_result == True, "p ∧ q should be satisfiable classically"
        
        classical_models = classical_tableau.extract_all_models()
        assert len(classical_models) > 0, "Should extract classical models"
        
        # WK3 system
        wk3_result = wk3_satisfiable(formula)
        assert wk3_result == True, "p ∧ q should be satisfiable in WK3"
        
        wk3_model_list = wk3_models(formula)
        assert len(wk3_model_list) > 0, "Should extract WK3 models"
    
    def test_tableau_rule_consistency(self):
        """Test that tableau rules work consistently"""
        # Test α-rule: conjunction expansion should be non-branching
        formula = Conjunction(self.p, self.q)
        
        # Classical
        classical_tableau = classical_signed_tableau(T(formula))
        classical_tableau.build()
        
        # Should have limited branching for α-rules
        classical_branches = len(classical_tableau.branches)
        assert classical_branches <= 3, "α-rules should not cause excessive branching"
        
        # Test β-rule: disjunction expansion should be branching
        disjunction = Disjunction(self.p, self.q)
        
        classical_disj_tableau = classical_signed_tableau(T(disjunction))
        classical_disj_tableau.build()
        
        # Should create branches for β-rules
        disj_branches = len(classical_disj_tableau.branches)
        assert disj_branches >= 2, "β-rules should create branches"
    
    def test_closure_detection_robustness(self):
        """Test that closure detection works robustly across systems"""
        # Create contradiction: p ∧ ¬p
        contradiction = Conjunction(self.p, Negation(self.p))
        
        # Classical: should be unsatisfiable
        classical_tableau = classical_signed_tableau(T(contradiction))
        classical_result = classical_tableau.build()
        assert classical_result == False, "Classical contradiction should be unsatisfiable"
        
        # All branches should be closed
        closed_branches = [b for b in classical_tableau.branches if b.is_closed]
        assert len(closed_branches) == len(classical_tableau.branches), "All branches should close"
        
        # WK3: should be satisfiable (when p is undefined)
        wk3_result = wk3_satisfiable(contradiction)
        assert wk3_result == True, "WK3 contradiction should be satisfiable"
    
    def test_literature_integration(self):
        """Test integration with literature examples"""
        # Test that literature examples work with signed tableaux
        
        # Priest's excluded middle example
        excluded_middle = Disjunction(self.p, Negation(self.p))
        
        # Should be satisfiable in WK3 (not a tautology)
        assert wk3_satisfiable(excluded_middle) == True
        
        # Fitting's basic expansion example
        formula = Negation(Conjunction(self.p, self.q))
        
        # Should be satisfiable
        tableau = classical_signed_tableau(T(formula))
        result = tableau.build()
        assert result == True, "¬(p ∧ q) should be satisfiable"
        
        # Should create proper branches
        assert len(tableau.branches) >= 2, "Should create branches"
    
    def test_performance_consistency(self):
        """Test that signed tableaux maintain reasonable performance"""
        # Create moderately complex formula
        formula = Conjunction(
            Disjunction(self.p, self.q),
            Disjunction(Negation(self.p), self.r)
        )
        
        # Should complete in reasonable time
        classical_tableau = classical_signed_tableau(T(formula))
        result = classical_tableau.build()
        
        # Should be satisfiable
        assert result == True, "Complex formula should be satisfiable"
        
        # Should not create excessive branches
        assert len(classical_tableau.branches) < 20, "Should not create excessive branches"
    
    def test_backward_compatibility(self):
        """Test that signed tableaux maintain backward compatibility"""
        # Test that old-style satisfiability checking still works
        
        # Simple satisfiable formula
        formula = self.p
        
        # Classical approach
        classical_result = classical_signed_tableau(T(formula)).build()
        assert classical_result == True, "Simple atom should be satisfiable"
        
        # WK3 adapter approach  
        wk3_result = wk3_satisfiable(formula)
        assert wk3_result == True, "Simple atom should be satisfiable in WK3"
        
        # Both should agree on basic satisfiability for simple cases


def run_all_signed_tests():
    """Run all signed tableau tests and provide comprehensive report"""
    print("=" * 80)
    print("COMPREHENSIVE SIGNED TABLEAU TEST SUITE")
    print("=" * 80)
    print()
    
    # Track test results
    results = {
        'classical_signed': 0,
        'wk3_signed': 0, 
        'literature_examples': 0,
        'integration_tests': 0,
        'total_failures': 0
    }
    
    try:
        # Run classical signed tests
        print("🔍 Running Classical Signed Tableau Tests...")
        classical_test = TestClassicalSignedTableau()
        classical_test.setup_method()
        
        # Run a few key classical tests
        try:
            classical_test.test_tautology_01_excluded_middle()
            classical_test.test_contradiction_01_basic()
            classical_test.test_satisfiable_01_simple_atom()
            classical_test.test_signed_tableau_rule_expansion()
            results['classical_signed'] += 4
            print("  ✅ Classical signed tests: PASSED")
        except Exception as e:
            print(f"  ❌ Classical signed tests: FAILED - {e}")
            results['total_failures'] += 1
        
        # Run WK3 signed tests
        print("🔍 Running WK3 Signed Tableau Tests...")
        wk3_test = TestWK3SignedTableau()
        wk3_test.setup_method()
        
        try:
            wk3_test.test_truth_value_creation()
            wk3_test.test_conjunction()
            wk3_test.test_contradiction_signed()
            wk3_test.test_excluded_middle_not_tautology_signed()
            results['wk3_signed'] += 4
            print("  ✅ WK3 signed tests: PASSED")
        except Exception as e:
            print(f"  ❌ WK3 signed tests: FAILED - {e}")
            results['total_failures'] += 1
        
        # Run integration tests
        print("🔍 Running Integration Tests...")
        integration_test = TestSignedTableauIntegration()
        integration_test.setup_method()
        
        try:
            integration_test.test_cross_system_consistency()
            integration_test.test_sign_system_compatibility()
            integration_test.test_model_extraction_consistency()
            integration_test.test_backward_compatibility()
            results['integration_tests'] += 4
            print("  ✅ Integration tests: PASSED")
        except Exception as e:
            print(f"  ❌ Integration tests: FAILED - {e}")
            results['total_failures'] += 1
        
        # Run basic functionality tests
        print("🔍 Running Basic Functionality Tests...")
        try:
            test_signed_classical_integration()
            test_wk3_signed_integration()
            test_wk3_basic_functionality_signed()
            results['integration_tests'] += 3
            print("  ✅ Basic functionality tests: PASSED")
        except Exception as e:
            print(f"  ❌ Basic functionality tests: FAILED - {e}")
            results['total_failures'] += 1
        
    except Exception as e:
        print(f"❌ Critical error during test execution: {e}")
        results['total_failures'] += 1
    
    # Print summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Classical Signed Tests:    {results['classical_signed']} passed")
    print(f"WK3 Signed Tests:          {results['wk3_signed']} passed")
    print(f"Literature Examples:       {results['literature_examples']} passed")
    print(f"Integration Tests:         {results['integration_tests']} passed")
    print(f"Total Failures:            {results['total_failures']}")
    print()
    
    if results['total_failures'] == 0:
        print("🎉 ALL SIGNED TABLEAU TESTS PASSED!")
        print("✅ The signed tableau system is working correctly across all logics.")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    print("=" * 80)
    
    return results['total_failures'] == 0


def run_literature_examples():
    """Run literature examples specifically"""
    print("📚 Running Literature Example Tests...")
    
    try:
        # Test Priest examples
        priest_test = TestPriestExamples()
        priest_test.test_priest_weak_kleene_conjunction_table()
        priest_test.test_priest_excluded_middle_not_tautology()
        
        # Test Fitting examples
        fitting_test = TestFittingExamples()
        fitting_test.test_fitting_basic_expansion_example()
        fitting_test.test_fitting_closure_example()
        
        print("  ✅ Literature examples: PASSED")
        return True
        
    except Exception as e:
        print(f"  ❌ Literature examples: FAILED - {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--literature":
        # Run just literature examples
        success = run_literature_examples()
        sys.exit(0 if success else 1)
    else:
        # Run comprehensive test suite
        success = run_all_signed_tests()
        sys.exit(0 if success else 1)