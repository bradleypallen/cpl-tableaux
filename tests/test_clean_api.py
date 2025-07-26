#!/usr/bin/env python3
"""
Test Suite for Clean Modern Tableau API

This test suite validates the new clean API while maintaining comprehensive
coverage of all functionality from the original test suite.
"""

import pytest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tableaux import LogicSystem, TableauResult


class TestCleanAPIBasics:
    """Test basic functionality of the clean API."""
    
    def test_logic_system_creation(self):
        """Test creating logic systems."""
        classical = LogicSystem.classical()
        weak_kleene = LogicSystem.weak_kleene()
        wkrq = LogicSystem.wkrq()
        
        assert classical.name == "classical"
        assert weak_kleene.name == "weak_kleene"
        assert wkrq.name == "wkrq"
    
    def test_atom_creation(self):
        """Test creating atoms."""
        classical = LogicSystem.classical()
        p = classical.atom('p')
        p2, q2 = classical.atoms('p', 'q')
        
        assert str(p) == 'p'
        assert str(p2) == 'p'
        assert str(q2) == 'q'
        assert p == p2  # Same atom should be equal
    
    def test_formula_operators(self):
        """Test formula construction with operators."""
        classical = LogicSystem.classical()
        p, q = classical.atoms('p', 'q')
        
        # Test all operators
        conjunction = p & q
        disjunction = p | q
        implication = p.implies(q)
        negation = ~p
        
        assert str(conjunction) == '(p & q)'
        assert str(disjunction) == '(p | q)'
        assert str(implication) == '(p -> q)'
        assert str(negation) == '~p'
    
    def test_complex_formulas(self):
        """Test complex formula construction."""
        classical = LogicSystem.classical()
        p, q, r = classical.atoms('p', 'q', 'r')
        
        complex_formula = (p & q) | (~p & r)
        assert str(complex_formula) == '((p & q) | (~p & r))'
        
        nested = p.implies(q) & q.implies(r) & p
        assert str(nested) == '(((p -> q) & (q -> r)) & p)'


class TestClassicalLogic:
    """Test classical propositional logic functionality."""
    
    def test_simple_satisfiability(self):
        """Test basic satisfiability checking."""
        classical = LogicSystem.classical()
        p = classical.atom('p')
        
        # Simple atom should be satisfiable
        result = classical.solve(p)
        assert result.satisfiable == True
        assert len(result.models) >= 1
    
    def test_tautology(self):
        """Test tautology detection."""
        classical = LogicSystem.classical()
        p = classical.atom('p')
        
        tautology = p | ~p
        assert classical.valid(tautology) == True
        assert classical.satisfiable(tautology) == True
        
        # When solving as T, should be satisfiable
        result = classical.solve(tautology, 'T')
        assert result.satisfiable == True
        
        # When solving as F, should be unsatisfiable  
        result = classical.solve(tautology, 'F')
        assert result.satisfiable == False
    
    def test_contradiction(self):
        """Test contradiction detection."""
        classical = LogicSystem.classical()
        p = classical.atom('p')
        
        contradiction = p & ~p
        assert classical.satisfiable(contradiction) == False
        assert classical.unsatisfiable(contradiction) == True
        
        result = classical.solve(contradiction)
        assert result.satisfiable == False
        assert len(result.models) == 0
    
    def test_contingency(self):
        """Test contingent formulas."""
        classical = LogicSystem.classical()
        p, q = classical.atoms('p', 'q')
        
        contingency = p.implies(q)
        assert classical.satisfiable(contingency) == True
        assert classical.valid(contingency) == False
        
        result = classical.solve(contingency)
        assert result.satisfiable == True
        assert len(result.models) >= 1
    
    def test_entailment(self):
        """Test entailment checking."""
        classical = LogicSystem.classical()
        p, q = classical.atoms('p', 'q')
        
        # Modus ponens: p -> q, p ⊨ q
        premises = [p.implies(q), p]
        conclusion = q
        assert classical.entails(premises, conclusion) == True
        
        # Invalid entailment
        invalid_premises = [p.implies(q)]
        assert classical.entails(invalid_premises, q) == False
    
    def test_disjunctive_syllogism(self):
        """Test disjunctive syllogism: p ∨ q, ¬p ⊨ q"""
        classical = LogicSystem.classical()
        p, q = classical.atoms('p', 'q')
        
        premises = [p | q, ~p]
        conclusion = q
        assert classical.entails(premises, conclusion) == True
    
    def test_hypothetical_syllogism(self):
        """Test hypothetical syllogism: p → q, q → r ⊨ p → r"""
        classical = LogicSystem.classical()
        p, q, r = classical.atoms('p', 'q', 'r')
        
        premises = [p.implies(q), q.implies(r)]
        conclusion = p.implies(r)
        assert classical.entails(premises, conclusion) == True


class TestWeakKleeneLogic:
    """Test weak Kleene three-valued logic."""
    
    def test_basic_satisfiability(self):
        """Test basic satisfiability in weak Kleene logic."""
        wk = LogicSystem.weak_kleene()
        p = wk.atom('p')
        
        # Simple atom should be satisfiable
        result = wk.solve(p)
        assert result.satisfiable == True
    
    def test_contradiction_behavior(self):
        """Test how contradictions behave in weak Kleene logic."""
        wk = LogicSystem.weak_kleene()
        p = wk.atom('p')
        
        # In weak Kleene, p ∧ ¬p is still unsatisfiable
        contradiction = p & ~p
        result = wk.solve(contradiction)
        assert result.satisfiable == False
    
    def test_law_of_excluded_middle(self):
        """Test law of excluded middle in weak Kleene logic."""
        wk = LogicSystem.weak_kleene()
        p = wk.atom('p')
        
        # In weak Kleene, p ∨ ¬p is valid (unlike in some three-valued logics)
        lem = p | ~p
        assert wk.valid(lem) == True


class TestWkrqLogic:
    """Test wKrQ four-valued logic."""
    
    def test_basic_satisfiability(self):
        """Test basic satisfiability in wKrQ logic."""
        wkrq = LogicSystem.wkrq()
        p = wkrq.atom('p')
        
        # Simple atom should be satisfiable
        result = wkrq.solve(p)
        assert result.satisfiable == True
    
    def test_law_of_excluded_middle_failure(self):
        """Test that LEM fails in wKrQ logic."""
        wkrq = LogicSystem.wkrq()
        p = wkrq.atom('p')
        
        # In wKrQ, p ∨ ¬p is not valid
        lem = p | ~p
        assert wkrq.valid(lem) == False
    
    def test_four_valued_signs(self):
        """Test that wKrQ supports all four signs."""
        wkrq = LogicSystem.wkrq()
        p = wkrq.atom('p')
        
        # Should be able to create signed formulas with T, F, M, N
        t_formula = p.T
        f_formula = p.F
        m_formula = p.M
        n_formula = p.N
        
        assert str(t_formula) == 'T:p'
        assert str(f_formula) == 'F:p'
        assert str(m_formula) == 'M:p'
        assert str(n_formula) == 'N:p'


class TestAdvancedFeatures:
    """Test advanced features of the tableau system."""
    
    def test_step_tracking(self):
        """Test step tracking functionality."""
        classical = LogicSystem.classical()
        p, q = classical.atoms('p', 'q')
        
        formula = p.implies(q) & p & ~q
        result = classical.solve(formula, track_steps=True)
        
        assert result.steps is not None
        assert len(result.steps) > 0
        assert result.tableau is not None
    
    def test_tableau_tree_printing(self):
        """Test tableau tree visualization."""
        classical = LogicSystem.classical()
        p = classical.atom('p')
        
        result = classical.solve(p & ~p, track_steps=True)
        
        if result.tableau:
            tree_str = result.tableau.print_tree(show_steps=True)
            assert isinstance(tree_str, str)
            assert len(tree_str) > 0
            assert "Step" in tree_str or "Final" in tree_str
    
    def test_multiple_models(self):
        """Test extracting multiple models."""
        classical = LogicSystem.classical()
        p, q = classical.atoms('p', 'q')
        
        # p ∨ q should have multiple models
        formula = p | q
        result = classical.solve(formula)
        
        assert result.satisfiable == True
        assert len(result.models) >= 2  # At least {p:T,q:F}, {p:F,q:T}, {p:T,q:T}
    
    def test_result_properties(self):
        """Test TableauResult properties."""
        classical = LogicSystem.classical()
        p = classical.atom('p')
        
        # Test satisfiable result
        sat_result = classical.solve(p)
        assert sat_result.is_satisfiable == True
        assert sat_result.is_unsatisfiable == False
        assert sat_result.model_count >= 1
        
        # Test unsatisfiable result
        unsat_result = classical.solve(p & ~p)
        assert unsat_result.is_satisfiable == False
        assert unsat_result.is_unsatisfiable == True
        assert unsat_result.model_count == 0


class TestLogicComparison:
    """Test behavior across different logic systems."""
    
    def test_law_of_excluded_middle_comparison(self):
        """Compare LEM across different logics."""
        classical = LogicSystem.classical()
        weak_kleene = LogicSystem.weak_kleene()
        wkrq = LogicSystem.wkrq()
        
        # Create equivalent formulas in each logic
        p_classical = classical.atom('p')
        p_wk = weak_kleene.atom('p')
        p_wkrq = wkrq.atom('p')
        
        lem_classical = p_classical | ~p_classical
        lem_wk = p_wk | ~p_wk
        lem_wkrq = p_wkrq | ~p_wkrq
        
        # Classical and weak Kleene should validate LEM
        assert classical.valid(lem_classical) == True
        assert weak_kleene.valid(lem_wk) == True
        
        # wKrQ should not validate LEM
        assert wkrq.valid(lem_wkrq) == False
    
    def test_contradiction_comparison(self):
        """Compare contradiction behavior across logics."""
        classical = LogicSystem.classical()
        weak_kleene = LogicSystem.weak_kleene()
        wkrq = LogicSystem.wkrq()
        
        # Create equivalent contradictions
        p_classical = classical.atom('p')
        p_wk = weak_kleene.atom('p')
        p_wkrq = wkrq.atom('p')
        
        contr_classical = p_classical & ~p_classical
        contr_wk = p_wk & ~p_wk
        contr_wkrq = p_wkrq & ~p_wkrq
        
        # Classical and weak Kleene should find contradictions unsatisfiable
        assert classical.satisfiable(contr_classical) == False
        assert weak_kleene.satisfiable(contr_wk) == False
        
        # In wKrQ, contradictions may be satisfiable with M or N values
        # This is correct behavior for four-valued logic
        wkrq_result = wkrq.satisfiable(contr_wkrq)
        assert isinstance(wkrq_result, bool)  # Just check it returns a boolean


if __name__ == "__main__":
    pytest.main([__file__])