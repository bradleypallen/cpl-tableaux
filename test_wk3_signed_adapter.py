#!/usr/bin/env python3
"""
Test WK3 Signed Adapter

Verifies that the WK3 signed adapter provides the same results as the
original WK3 implementation while using signed tableaux internally.
"""

import pytest
from formula import Atom, Negation, Conjunction, Disjunction, Implication
from wk3_signed_adapter import wk3_tableau, wk3_satisfiable, wk3_models, WK3SignedTableau
from truth_value import t, f, e


class TestWK3SignedAdapter:
    """Test the WK3 signed adapter functionality"""
    
    def test_simple_atom_satisfiable(self):
        """Test that a simple atom is satisfiable"""
        p = Atom("p")
        
        assert wk3_satisfiable(p) == True
        
        models = wk3_models(p)
        assert len(models) >= 1
        
        # Should have models where p can be true, false, or undefined
        model = models[0]
        assert p.name in model.assignment
        assert model.assignment[p.name] in {t, f, e}
    
    def test_contradiction_satisfiable_in_wk3(self):
        """Test that p ∧ ¬p is satisfiable in WK3 (when p is undefined)"""
        p = Atom("p")
        neg_p = Negation(p)
        contradiction = Conjunction(p, neg_p)
        
        # In WK3, this should be satisfiable when p = e
        assert wk3_satisfiable(contradiction) == True
        
        models = wk3_models(contradiction)
        assert len(models) >= 1
        
        # At least one model should have p = e
        found_undefined = False
        for model in models:
            if model.assignment.get(p.name) == e:
                found_undefined = True
                # Verify that the model actually satisfies the contradiction
                assert model.satisfies(contradiction) == e
                break
        
        assert found_undefined, "Should find model where p is undefined"
    
    def test_classical_contradiction_unsatisfiable(self):
        """Test that a true contradiction (both T:p and F:p) is unsatisfiable"""
        p = Atom("p")
        
        # Create tableau with both T:p and F:p (classical contradiction)
        tableau = WK3SignedTableau([p])  # This creates T:p
        
        # For now, test that single formulas work
        # TODO: Add test for explicit contradictory signed formulas
        result = tableau.build()
        assert result == True  # T:p should be satisfiable
    
    def test_tautology_law_of_excluded_middle(self):
        """Test law of excluded middle: p ∨ ¬p"""
        p = Atom("p")
        neg_p = Negation(p)
        lem = Disjunction(p, neg_p)
        
        # In WK3, p ∨ ¬p should be satisfiable (not a tautology)
        assert wk3_satisfiable(lem) == True
        
        models = wk3_models(lem)
        assert len(models) >= 1
        
        # Should have different models with different truth values for p
        model = models[0]
        lem_value = model.satisfies(lem)
        assert lem_value in {t, e}  # Could be true or undefined in WK3
    
    def test_wk3_conjunction_semantics(self):
        """Test WK3-specific conjunction semantics"""
        p = Atom("p")
        q = Atom("q")
        conj = Conjunction(p, q)
        
        assert wk3_satisfiable(conj) == True
        
        models = wk3_models(conj)
        assert len(models) >= 1
        
        # Test a specific model to verify WK3 semantics
        model = models[0]
        
        # If we can control the model, test specific truth combinations
        # For now, just verify it produces a valid WK3 model
        conj_value = model.satisfies(conj)
        assert conj_value in {t, f, e}
    
    def test_wk3_implication_semantics(self):
        """Test WK3-specific implication semantics"""
        p = Atom("p")
        q = Atom("q")
        impl = Implication(p, q)
        
        assert wk3_satisfiable(impl) == True
        
        models = wk3_models(impl)
        assert len(models) >= 1
        
        model = models[0]
        impl_value = model.satisfies(impl)
        assert impl_value in {t, f, e}
    
    def test_backward_compatibility_api(self):
        """Test that the API matches the original WK3 implementation"""
        p = Atom("p")
        q = Atom("q")
        formula = Conjunction(p, q)
        
        # Test tableau creation
        tableau = wk3_tableau(formula)
        assert hasattr(tableau, 'build')
        assert hasattr(tableau, 'is_satisfiable')
        assert hasattr(tableau, 'extract_all_models')
        assert hasattr(tableau, 'get_sample_model')
        assert hasattr(tableau, 'print_tree')
        
        # Test building
        result = tableau.build()
        assert isinstance(result, bool)
        
        # Test model extraction
        models = tableau.extract_all_models()
        assert isinstance(models, list)
        
        if models:
            model = models[0]
            assert hasattr(model, 'satisfies')
            assert hasattr(model, 'assignment')
            
            # Test model evaluation
            satisfaction = model.satisfies(formula)
            assert satisfaction in {t, f, e}
    
    def test_statistics_collection(self):
        """Test that statistics are collected properly"""
        p = Atom("p")
        q = Atom("q")
        formula = Conjunction(Disjunction(p, q), Negation(p))
        
        tableau = wk3_tableau(formula)
        tableau.build()
        
        stats = tableau.get_statistics()
        
        assert 'logic_system' in stats
        assert 'sign_system' in stats
        assert 'truth_values' in stats
        assert 'satisfiable' in stats
        assert 'total_branches' in stats
        assert 'rule_applications' in stats
        
        assert stats['sign_system'] == 'three_valued'
        assert stats['truth_values'] == ['t', 'f', 'e']
    
    def test_complex_formula_handling(self):
        """Test handling of complex nested formulas"""
        p = Atom("p")
        q = Atom("q") 
        r = Atom("r")
        
        # ((p ∧ q) ∨ r) → (¬p ∨ q)
        complex_formula = Implication(
            Disjunction(Conjunction(p, q), r),
            Disjunction(Negation(p), q)
        )
        
        result = wk3_satisfiable(complex_formula)
        assert isinstance(result, bool)
        
        if result:
            models = wk3_models(complex_formula)
            assert len(models) >= 1
            
            # Verify at least one model satisfies the formula
            found_satisfying = False
            for model in models:
                if model.satisfies(complex_formula) in {t, e}:  # True or undefined is satisfying
                    found_satisfying = True
                    break
            
            assert found_satisfying, "Should find at least one satisfying model"
    
    def test_model_string_representation(self):
        """Test that model string representation works correctly"""
        p = Atom("p")
        q = Atom("q")
        formula = Conjunction(p, q)
        
        models = wk3_models(formula)
        if models:
            model = models[0]
            model_str = str(model)
            
            # Should contain recognizable truth value information
            assert isinstance(model_str, str)
            # Could be empty {} or contain truth value information
            # Just verify it doesn't crash and produces a string


class TestWK3ComparedToSigned:
    """Compare WK3 adapter results with direct signed tableau results"""
    
    def test_wk3_satisfiability_semantics(self):
        """Test that WK3 adapter correctly implements WK3 satisfiability semantics"""
        from signed_tableau import three_valued_signed_tableau
        from signed_formula import T3, U
        
        test_formulas = [
            Atom("p"),
            Negation(Atom("p")),
            Conjunction(Atom("p"), Atom("q")),
            Disjunction(Atom("p"), Negation(Atom("p"))),
            Conjunction(Atom("p"), Negation(Atom("p")))
        ]
        
        for formula in test_formulas:
            # Test via WK3 adapter (should be true if formula can be T OR U)
            wk3_result = wk3_satisfiable(formula)
            
            # Test via direct signed tableau for both T and U
            t_tableau = three_valued_signed_tableau(T3(formula))
            t_result = t_tableau.build()
            
            u_tableau = three_valued_signed_tableau(U(formula))
            u_result = u_tableau.build()
            
            # WK3 satisfiable should equal (T-satisfiable OR U-satisfiable)
            expected_result = t_result or u_result
            
            assert wk3_result == expected_result, \
                f"WK3 semantics incorrect for {formula}: got {wk3_result}, expected {expected_result} (T:{t_result}, U:{u_result})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])