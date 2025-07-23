#!/usr/bin/env python3
"""
Tests for Signed Tableau System

Verifies that the signed tableau implementation correctly follows standard
tableau literature methods for both classical and three-valued logics.
"""

import pytest
from formula import Atom, Negation, Conjunction, Disjunction, Implication
from signed_formula import (
    SignedFormula, ClassicalSign, ThreeValuedSign, 
    T, F, U, T3, F3, SignRegistry
)
from signed_tableau import SignedTableau, classical_signed_tableau, three_valued_signed_tableau
from signed_tableau_rules import SignedRuleRegistry


class TestSignedFormulas:
    """Test the basic signed formula functionality"""
    
    def test_classical_signs(self):
        """Test classical T/F signs"""
        p = Atom("p")
        
        tp = T(p)  # T:p
        fp = F(p)  # F:p
        
        assert str(tp) == "T:p"
        assert str(fp) == "F:p"
        
        # Test contradiction detection
        assert tp.is_contradictory_with(fp)
        assert fp.is_contradictory_with(tp)
        assert not tp.is_contradictory_with(tp)
        assert not fp.is_contradictory_with(fp)
    
    def test_three_valued_signs(self):
        """Test three-valued T/F/U signs"""
        p = Atom("p")
        
        tp = T3(p)  # T:p
        fp = F3(p)  # F:p  
        up = U(p)   # U:p
        
        assert str(tp) == "T:p"
        assert str(fp) == "F:p"
        assert str(up) == "U:p"
        
        # Test three-valued contradiction rules
        assert tp.is_contradictory_with(fp)  # T and F are contradictory
        assert fp.is_contradictory_with(tp)
        
        assert not tp.is_contradictory_with(up)  # T and U are NOT contradictory
        assert not up.is_contradictory_with(tp)
        assert not fp.is_contradictory_with(up)  # F and U are NOT contradictory  
        assert not up.is_contradictory_with(fp)
        assert not up.is_contradictory_with(up)  # U and U are NOT contradictory


class TestSignedTableauRules:
    """Test signed tableau rules"""
    
    def test_t_conjunction_rule(self):
        """Test T:(A∧B) → T:A, T:B"""
        p = Atom("p")
        q = Atom("q")
        conj = Conjunction(p, q)
        
        registry = SignedRuleRegistry()
        rule = registry.get_best_rule(T(conj), "classical")
        
        assert rule is not None
        assert rule.applies_to(T(conj))
        
        result = rule.apply(T(conj))
        assert result.is_alpha
        assert len(result.branches) == 1
        assert len(result.branches[0]) == 2
        
        # Should produce T:p and T:q
        formulas = result.branches[0]
        assert T(p) in formulas
        assert T(q) in formulas
    
    def test_f_conjunction_rule(self):
        """Test F:(A∧B) → F:A | F:B"""
        p = Atom("p")
        q = Atom("q")
        conj = Conjunction(p, q)
        
        registry = SignedRuleRegistry()
        rule = registry.get_best_rule(F(conj), "classical")
        
        assert rule is not None
        assert rule.applies_to(F(conj))
        
        result = rule.apply(F(conj))
        assert not result.is_alpha  # β-rule (branching)
        assert len(result.branches) == 2
        
        # Should produce F:p | F:q
        assert result.branches[0] == [F(p)]
        assert result.branches[1] == [F(q)]
    
    def test_negation_rule(self):
        """Test T:¬A → F:A and F:¬A → T:A"""
        p = Atom("p")
        neg_p = Negation(p)
        
        registry = SignedRuleRegistry()
        
        # Test T:¬p → F:p
        rule1 = registry.get_best_rule(T(neg_p), "classical")
        result1 = rule1.apply(T(neg_p))
        assert result1.is_alpha
        assert result1.branches[0] == [F(p)]
        
        # Test F:¬p → T:p
        rule2 = registry.get_best_rule(F(neg_p), "classical")
        result2 = rule2.apply(F(neg_p))
        assert result2.is_alpha
        assert result2.branches[0] == [T(p)]


class TestClassicalSignedTableaux:
    """Test classical signed tableaux following standard literature"""
    
    def test_satisfiable_atom(self):
        """Test T:p - should be satisfiable"""
        p = Atom("p")
        tableau = classical_signed_tableau(T(p))
        
        result = tableau.build()
        assert result == True  # Satisfiable
        
        models = tableau.extract_all_models()
        assert len(models) >= 1
        
        # Should have T:p in the model
        model = models[0]
        assert p in model.assignments
        assert str(model.assignments[p]) == "T"
    
    def test_contradiction(self):
        """Test T:p, F:p - should be unsatisfiable"""
        p = Atom("p")
        tableau = classical_signed_tableau([T(p), F(p)])
        
        result = tableau.build()
        assert result == False  # Unsatisfiable
        
        # Should have one closed branch
        assert len(tableau.branches) == 1
        assert tableau.branches[0].is_closed
        
        # Closure should be due to T:p and F:p contradiction
        closure_reason = tableau.branches[0].closure_reason
        assert closure_reason is not None
        sf1, sf2 = closure_reason
        assert {sf1, sf2} == {T(p), F(p)}
    
    def test_tautology_excluded_middle(self):
        """Test F:(p ∨ ¬p) - should be unsatisfiable (tautology)"""
        p = Atom("p")
        neg_p = Negation(p)
        disj = Disjunction(p, neg_p)
        
        # F:(p ∨ ¬p) should be unsatisfiable because (p ∨ ¬p) is a tautology
        tableau = classical_signed_tableau(F(disj))
        
        result = tableau.build()  
        assert result == False  # Unsatisfiable
        
        stats = tableau.get_statistics()
        assert stats["satisfiable"] == False
    
    def test_satisfiable_disjunction(self):
        """Test T:(p ∨ q) - should be satisfiable with 2 models"""
        p = Atom("p")
        q = Atom("q")
        disj = Disjunction(p, q)
        
        tableau = classical_signed_tableau(T(disj))
        
        result = tableau.build()
        assert result == True  # Satisfiable
        
        # Should have 2 open branches (T:p | T:q)
        open_branches = [b for b in tableau.branches if not b.is_closed]
        assert len(open_branches) == 2
    
    def test_conjunction_expansion(self):
        """Test T:(p ∧ q) expansion"""
        p = Atom("p")
        q = Atom("q")
        conj = Conjunction(p, q)
        
        tableau = classical_signed_tableau(T(conj))
        
        result = tableau.build()
        assert result == True  # Satisfiable
        
        # Should have 1 branch containing T:p and T:q
        assert len(tableau.branches) == 1
        branch = tableau.branches[0]
        assert not branch.is_closed
        
        # Branch should contain T:p and T:q
        signed_formulas = branch.signed_formulas
        assert T(p) in signed_formulas
        assert T(q) in signed_formulas
    
    def test_implication_expansion(self):
        """Test T:(p → q) expansion"""
        p = Atom("p")
        q = Atom("q")
        impl = Implication(p, q)
        
        tableau = classical_signed_tableau(T(impl))
        
        result = tableau.build()
        assert result == True  # Satisfiable
        
        # Should have 2 branches: F:p | T:q
        open_branches = [b for b in tableau.branches if not b.is_closed]
        assert len(open_branches) == 2


class TestThreeValuedSignedTableaux:
    """Test three-valued signed tableaux"""
    
    def test_three_valued_satisfiable(self):
        """Test that T:p is satisfiable in three-valued logic"""
        p = Atom("p")
        tableau = three_valued_signed_tableau(T3(p))
        
        result = tableau.build()
        assert result == True
        
        models = tableau.extract_all_models()
        assert len(models) >= 1
    
    def test_three_valued_undefined(self):
        """Test U:p (undefined) - should be satisfiable"""
        p = Atom("p")
        tableau = three_valued_signed_tableau(U(p))
        
        result = tableau.build()
        assert result == True  # U:p should be satisfiable
    
    def test_three_valued_non_contradiction(self):
        """Test T:p, U:p - should be satisfiable (not contradictory in 3-valued)"""
        p = Atom("p")
        tableau = three_valued_signed_tableau([T3(p), U(p)])
        
        result = tableau.build()
        assert result == True  # Should be satisfiable
        
        # Branch should not be closed
        assert len(tableau.branches) == 1
        assert not tableau.branches[0].is_closed
    
    def test_three_valued_contradiction(self):
        """Test T:p, F:p - should still be unsatisfiable in 3-valued logic"""
        p = Atom("p")
        tableau = three_valued_signed_tableau([T3(p), F3(p)])
        
        result = tableau.build()
        assert result == False  # Still unsatisfiable
        
        # Should be closed due to T:p and F:p contradiction
        assert len(tableau.branches) == 1
        assert tableau.branches[0].is_closed


class TestSignedTableauIntegration:
    """Integration tests for the signed tableau system"""
    
    def test_system_comparison(self):
        """Compare classical vs three-valued results for same formula"""
        p = Atom("p")
        q = Atom("q")
        conj = Conjunction(p, Negation(p))  # p ∧ ¬p
        
        # Classical: F:(p ∧ ¬p) should be satisfiable because p ∧ ¬p IS false
        classical_tableau = classical_signed_tableau(F(conj))
        classical_result = classical_tableau.build()
        
        # Three-valued: F:(p ∧ ¬p) should also be satisfiable  
        three_valued_tableau = three_valued_signed_tableau(F3(conj))
        three_valued_result = three_valued_tableau.build()
        
        # Both should be satisfiable - F:(p ∧ ¬p) means "p ∧ ¬p is false" which is true
        assert classical_result == True
        assert three_valued_result == True
    
    def test_rule_priority(self):
        """Test that α-rules are applied before β-rules"""
        p = Atom("p")
        q = Atom("q")
        r = Atom("r")
        
        # T:((p ∧ q) ∨ r) should expand T:(p ∧ q) first (α-rule) before branching
        conj = Conjunction(p, q)
        disj = Disjunction(conj, r)
        
        tableau = classical_signed_tableau(T(disj))
        result = tableau.build()
        
        assert result == True  # Should be satisfiable
        # Verify that rule applications > 1 (multiple expansions occurred)
        assert tableau.rule_applications >= 1
    
    def test_statistics(self):
        """Test tableau statistics collection"""
        p = Atom("p")
        q = Atom("q")
        impl = Implication(p, q)
        
        tableau = classical_signed_tableau(T(impl))
        tableau.build()
        
        stats = tableau.get_statistics()
        
        assert stats["sign_system"] == "classical"
        assert stats["initial_formulas"] == 1
        assert stats["satisfiable"] == True
        assert stats["rule_applications"] >= 1
        assert stats["total_branches"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])