#!/usr/bin/env python3
"""
Ferguson wKrQ Signing System Tests

Tests the implementation of Ferguson's four-valued signing system (T, F, M, N)
for weak Kleene logic with restricted quantifiers, based on:

Ferguson, Thomas Macaulay. "Tableaux and restricted quantification for systems 
related to weak Kleene logic." In International Conference on Automated Reasoning 
with Analytic Tableaux and Related Methods, pp. 3-19. Cham: Springer International 
Publishing, 2021.
"""

import pytest
from formula import Atom, Negation, Conjunction, Disjunction, Implication, RestrictedExistentialFormula, RestrictedUniversalFormula, Predicate
from term import Variable, Constant
from signed_formula import WkrqSign, SignedFormula, TF, FF, M, N
from signed_tableau import wkrq_signed_tableau
from truth_value import t, f, e


class TestWkrqSign:
    """Test Ferguson's wKrQ sign system"""
    
    def test_wkrq_sign_creation(self):
        """Test creating Ferguson signs"""
        t_sign = WkrqSign("T")
        f_sign = WkrqSign("F")
        m_sign = WkrqSign("M")
        n_sign = WkrqSign("N")
        
        assert str(t_sign) == "T"
        assert str(f_sign) == "F"
        assert str(m_sign) == "M"
        assert str(n_sign) == "N"
    
    def test_wkrq_sign_equality(self):
        """Test Ferguson sign equality"""
        t1 = WkrqSign("T")
        t2 = WkrqSign("T")
        f1 = WkrqSign("F")
        
        assert t1 == t2
        assert t1 != f1
        assert hash(t1) == hash(t2)
        assert hash(t1) != hash(f1)
    
    def test_wkrq_sign_contradiction(self):
        """Test Ferguson sign contradiction rules"""
        t_sign = WkrqSign("T")
        f_sign = WkrqSign("F")
        m_sign = WkrqSign("M")
        n_sign = WkrqSign("N")
        
        # T and F are contradictory
        assert t_sign.is_contradictory_with(f_sign)
        assert f_sign.is_contradictory_with(t_sign)
        
        # M and N do not create contradictions by themselves
        assert not m_sign.is_contradictory_with(n_sign)
        assert not n_sign.is_contradictory_with(m_sign)
        
        # T/F don't contradict M/N (epistemic uncertainty)
        assert not t_sign.is_contradictory_with(m_sign)
        assert not t_sign.is_contradictory_with(n_sign)
        assert not f_sign.is_contradictory_with(m_sign)
        assert not f_sign.is_contradictory_with(n_sign)
    
    def test_wkrq_sign_truth_values(self):
        """Test mapping Ferguson signs to truth values"""
        t_sign = WkrqSign("T")
        f_sign = WkrqSign("F")
        m_sign = WkrqSign("M")
        n_sign = WkrqSign("N")
        
        assert t_sign.get_truth_value() == t
        assert f_sign.get_truth_value() == f
        assert m_sign.get_truth_value() == e  # Uncertain
        assert n_sign.get_truth_value() == e  # Uncertain
    
    def test_wkrq_sign_properties(self):
        """Test Ferguson sign property methods"""
        t_sign = WkrqSign("T")
        f_sign = WkrqSign("F")
        m_sign = WkrqSign("M")
        n_sign = WkrqSign("N")
        
        # Definite signs
        assert t_sign.is_definite()
        assert f_sign.is_definite()
        assert not m_sign.is_definite()
        assert not n_sign.is_definite()
        
        # Epistemic signs
        assert not t_sign.is_epistemic()
        assert not f_sign.is_epistemic()
        assert m_sign.is_epistemic()
        assert n_sign.is_epistemic()
    
    def test_wkrq_sign_duals(self):
        """Test Ferguson sign duality for negation"""
        t_sign = WkrqSign("T")
        f_sign = WkrqSign("F")
        m_sign = WkrqSign("M")
        n_sign = WkrqSign("N")
        
        assert t_sign.dual() == f_sign
        assert f_sign.dual() == t_sign
        assert m_sign.dual() == n_sign
        assert n_sign.dual() == m_sign
    
    def test_invalid_ferguson_sign(self):
        """Test invalid Ferguson sign creation"""
        with pytest.raises(ValueError):
            WkrqSign("X")  # Invalid designation


class TestWkrqSignedFormulas:
    """Test Ferguson signed formula creation and operations"""
    
    def setup_method(self):
        """Set up test atoms"""
        self.p = Atom("p")
        self.q = Atom("q")
    
    def test_wkrq_signed_formula_creation(self):
        """Test creating Ferguson signed formulas"""
        tf_p = TF(self.p)
        ff_p = FF(self.p)
        m_p = M(self.p)
        n_p = N(self.p)
        
        assert str(tf_p) == "T:p"
        assert str(ff_p) == "F:p"
        assert str(m_p) == "M:p"
        assert str(n_p) == "N:p"
        
        assert isinstance(tf_p.sign, WkrqSign)
        assert tf_p.sign.designation == "T"
        assert m_p.sign.designation == "M"
    
    def test_wkrq_signed_formula_contradictions(self):
        """Test contradictions in Ferguson signed formulas"""
        tf_p = TF(self.p)
        ff_p = FF(self.p)
        m_p = M(self.p)
        n_p = N(self.p)
        
        # T:p and F:p contradict
        assert tf_p.is_contradictory_with(ff_p)
        assert ff_p.is_contradictory_with(tf_p)
        
        # M:p and N:p do not contradict
        assert not m_p.is_contradictory_with(n_p)
        assert not n_p.is_contradictory_with(m_p)
        
        # T:p and M:p do not contradict (epistemic uncertainty)
        assert not tf_p.is_contradictory_with(m_p)
        assert not tf_p.is_contradictory_with(n_p)
    
    def test_wkrq_signed_formula_properties(self):
        """Test Ferguson signed formula properties"""
        tf_p = TF(self.p)
        m_conj = M(Conjunction(self.p, self.q))
        
        assert tf_p.is_atomic()
        assert tf_p.is_literal()
        assert not m_conj.is_atomic()
        assert not m_conj.is_literal()


class TestWkrqTableau:
    """Test Ferguson wKrQ tableau construction"""
    
    def setup_method(self):
        """Set up test formulas"""
        self.p = Atom("p")
        self.q = Atom("q")
        self.x = Variable("X")
        self.john = Constant("john")
        self.student_x = Predicate("Student", [self.x])
        self.human_x = Predicate("Human", [self.x])
    
    def test_wkrq_tableau_creation(self):
        """Test creating Ferguson tableaux"""
        tf_p = TF(self.p)
        tableau = wkrq_signed_tableau(tf_p)
        
        assert tableau.sign_system == "ferguson"
        assert len(tableau.initial_signed_formulas) == 1
        assert tableau.initial_signed_formulas[0] == tf_p
    
    def test_wkrq_tableau_simple_satisfiable(self):
        """Test simple satisfiable formula in Ferguson tableau"""
        tf_p = TF(self.p)
        tableau = wkrq_signed_tableau(tf_p)
        result = tableau.build()
        
        assert result == True, "T:p should be satisfiable in Ferguson system"
        
        # Should have open branches
        open_branches = [b for b in tableau.branches if not b.is_closed]
        assert len(open_branches) > 0, "Should have open branches"
    
    def test_wkrq_tableau_epistemic_satisfiable(self):
        """Test epistemic signs are satisfiable in Ferguson tableau"""
        m_p = M(self.p)
        tableau = wkrq_signed_tableau(m_p)
        result = tableau.build()
        
        assert result == True, "M:p should be satisfiable in Ferguson system"
        
        n_p = N(self.p)
        tableau2 = wkrq_signed_tableau(n_p)
        result2 = tableau2.build()
        
        assert result2 == True, "N:p should be satisfiable in Ferguson system"
    
    def test_wkrq_tableau_classical_contradiction(self):
        """Test classical contradiction in Ferguson tableau"""
        tf_p = TF(self.p)
        ff_p = FF(self.p)
        tableau = wkrq_signed_tableau([tf_p, ff_p])
        result = tableau.build()
        
        assert result == False, "T:p ∧ F:p should be unsatisfiable"
        
        # All branches should be closed
        closed_branches = [b for b in tableau.branches if b.is_closed]
        assert len(closed_branches) == len(tableau.branches), "All branches should be closed"
    
    def test_wkrq_tableau_epistemic_no_contradiction(self):
        """Test that epistemic signs don't create contradictions"""
        m_p = M(self.p)
        n_p = N(self.p)
        tableau = wkrq_signed_tableau([m_p, n_p])
        result = tableau.build()
        
        assert result == True, "M:p ∧ N:p should be satisfiable (no contradiction)"
        
        # Should have open branches (no contradiction)
        open_branches = [b for b in tableau.branches if not b.is_closed]
        assert len(open_branches) > 0, "Should have open branches (no contradiction)"
    
    def test_wkrq_tableau_complex_formula(self):
        """Test Ferguson tableau with complex formulas"""
        # M:(p ∧ q) - "p and q may both be true"
        complex_formula = Conjunction(self.p, self.q)
        m_complex = M(complex_formula)
        
        tableau = wkrq_signed_tableau(m_complex)
        result = tableau.build()
        
        assert result == True, "Complex epistemic formulas should be satisfiable"
    
    def test_wkrq_tableau_restricted_quantifiers(self):
        """Test Ferguson tableau with restricted quantifiers"""
        # [∃X Student(X)]Human(X) - "There exists a student who is human"
        exists_student_human = RestrictedExistentialFormula(self.x, self.student_x, self.human_x)
        
        # M:[∃X Student(X)]Human(X) - "It may be true that there exists a student who is human"
        m_exists = M(exists_student_human)
        
        tableau = wkrq_signed_tableau(m_exists)
        result = tableau.build()
        
        # Should be satisfiable (epistemic uncertainty about quantified statement)
        assert result == True, "Epistemic restricted quantifier should be satisfiable"
    
    def test_wkrq_negation_rules(self):
        """Test Ferguson negation rules with sign duality"""
        # T:¬p should lead to F:p
        neg_p = Negation(self.p)
        tf_neg_p = TF(neg_p)
        
        tableau = wkrq_signed_tableau(tf_neg_p)
        result = tableau.build()
        
        assert result == True, "T:¬p should be satisfiable"
        
        # Check that tableau expansion works (implementation dependent)
        # The key is that it should be satisfiable
    
    def test_wkrq_disjunction_epistemic(self):
        """Test epistemic disjunction in Ferguson system"""
        # M:(p ∨ q) - "p or q may be true"
        disj = Disjunction(self.p, self.q)
        m_disj = M(disj)
        
        tableau = wkrq_signed_tableau(m_disj)
        result = tableau.build()
        
        assert result == True, "Epistemic disjunction should be satisfiable"


class TestWkrqIntegration:
    """Integration tests for Ferguson system with existing components"""
    
    def test_wkrq_sign_registry(self):
        """Test Ferguson sign system registration"""
        from signed_formula import SignRegistry
        
        # Should be registered as "ferguson"
        ferguson_signs = SignRegistry.get_signs("ferguson")
        assert len(ferguson_signs) == 4, "Should have 4 Ferguson signs"
        
        sign_strs = [str(sign) for sign in ferguson_signs]
        assert "T" in sign_strs
        assert "F" in sign_strs
        assert "M" in sign_strs
        assert "N" in sign_strs
    
    def test_wkrq_vs_classical_behavior(self):
        """Test differences between Ferguson and classical signing"""
        p = Atom("p")
        
        # Classical: T:p and F:p contradict
        from signed_formula import T, F
        classical_t = T(p)
        classical_f = F(p)
        assert classical_t.is_contradictory_with(classical_f)
        
        # Ferguson: T:p and F:p also contradict (same behavior)
        ferguson_t = TF(p)
        ferguson_f = FF(p)
        assert ferguson_t.is_contradictory_with(ferguson_f)
        
        # Ferguson: M:p and N:p do NOT contradict (different from classical)
        ferguson_m = M(p)
        ferguson_n = N(p)
        assert not ferguson_m.is_contradictory_with(ferguson_n)
    
    def test_wkrq_truth_value_mapping(self):
        """Test mapping Ferguson signs to truth values"""
        p = Atom("p")
        
        tf_p = TF(p)
        ff_p = FF(p)
        m_p = M(p)
        n_p = N(p)
        
        assert tf_p.sign.get_truth_value() == t
        assert ff_p.sign.get_truth_value() == f
        assert m_p.sign.get_truth_value() == e  # Epistemic uncertainty
        assert n_p.sign.get_truth_value() == e  # Epistemic uncertainty


def test_wkrq_comprehensive():
    """Comprehensive test of Ferguson system functionality"""
    print("Testing Ferguson wKrQ signing system...")
    
    # Test basic sign functionality
    p = Atom("p")
    tf_p = TF(p)
    m_p = M(p)
    
    assert str(tf_p.sign) == "T"
    assert str(m_p.sign) == "M"
    assert tf_p.sign.is_definite()
    assert m_p.sign.is_epistemic()
    
    # Test tableau construction
    tableau = wkrq_signed_tableau(m_p)
    result = tableau.build()
    assert result == True, "M:p should be satisfiable"
    
    print("✅ Ferguson wKrQ signing system works correctly!")


if __name__ == "__main__":
    test_wkrq_comprehensive()
    pytest.main([__file__, "-v"])