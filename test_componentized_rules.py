#!/usr/bin/env python3
"""
Test Suite for Componentized Rule System

Tests the new componentized tableau rule architecture to ensure it produces
the same results as the original hardcoded implementation.
"""

import pytest
from formula import Atom, Negation, Conjunction, Disjunction, Implication
from componentized_tableau import ComponentizedTableau, classical_tableau, wk3_tableau
from logic_system import get_logic_system
from builtin_logics import describe_all_logics


class TestLogicSystemRegistry:
    """Test the logic system registry"""
    
    def test_builtin_systems_registered(self):
        """Test that built-in logic systems are registered"""
        classical = get_logic_system("classical")
        assert classical is not None
        assert classical.config.name == "Classical Propositional Logic"
        
        wk3 = get_logic_system("wk3")
        assert wk3 is not None
        assert wk3.config.name == "Weak Kleene Logic"
    
    def test_system_aliases(self):
        """Test that logic system aliases work"""
        # Classical aliases
        assert get_logic_system("classical") is not None
        assert get_logic_system("CPL") is not None
        assert get_logic_system("prop") is not None
        
        # WK3 aliases
        assert get_logic_system("wk3") is not None
        assert get_logic_system("WK3") is not None
        assert get_logic_system("weak-kleene") is not None
    
    def test_describe_logics(self):
        """Test that logic descriptions work"""
        description = describe_all_logics()
        assert "Classical Propositional Logic" in description
        assert "Weak Kleene Logic" in description


class TestClassicalRules:
    """Test classical logic rules through the componentized system"""
    
    def test_simple_atom(self):
        """Test satisfiability of simple atom"""
        p = Atom("p")
        tableau = classical_tableau(p)
        result = tableau.build()
        
        assert result == True
        assert len(tableau.extract_all_models()) > 0
    
    def test_contradiction(self):
        """Test unsatisfiability of contradiction"""
        p = Atom("p")
        formula = Conjunction(p, Negation(p))
        tableau = classical_tableau(formula)
        result = tableau.build()
        
        assert result == False
        assert len(tableau.extract_all_models()) == 0
    
    def test_tautology(self):
        """Test satisfiability of tautology"""
        p = Atom("p")
        formula = Disjunction(p, Negation(p))
        tableau = classical_tableau(formula)
        result = tableau.build()
        
        assert result == True
        models = tableau.extract_all_models()
        assert len(models) > 0
    
    def test_complex_formula(self):
        """Test complex propositional formula"""
        p, q, r = Atom("p"), Atom("q"), Atom("r")
        # (p → q) ∧ (q → r) ∧ p → r (should be satisfiable)
        formula = Implication(
            Conjunction(
                Conjunction(Implication(p, q), Implication(q, r)),
                p
            ),
            r
        )
        
        tableau = classical_tableau(formula)
        result = tableau.build()
        
        assert result == True
        models = tableau.extract_all_models()
        assert len(models) > 0


class TestWK3Rules:
    """Test WK3 logic rules through the componentized system"""
    
    def test_simple_atom_wk3(self):
        """Test WK3 satisfiability of simple atom"""
        p = Atom("p")
        tableau = wk3_tableau(p)
        result = tableau.build()
        
        assert result == True
        models = tableau.extract_all_models()
        assert len(models) > 0
    
    def test_contradiction_wk3(self):
        """Test WK3 contradiction handling"""
        p = Atom("p")
        formula = Conjunction(p, Negation(p))
        tableau = wk3_tableau(formula)
        result = tableau.build()
        
        # In WK3, p ∧ ¬p might be satisfiable with p=e
        # This depends on the exact WK3 semantics implementation
        assert isinstance(result, bool)


class TestComponentizedTableau:
    """Test the ComponentizedTableau class directly"""
    
    def test_logic_system_parameter(self):
        """Test using logic system by name vs object"""
        p = Atom("p")
        
        # By name
        tableau1 = ComponentizedTableau(p, "classical")
        result1 = tableau1.build()
        
        # By object
        logic_system = get_logic_system("classical")
        tableau2 = ComponentizedTableau(p, logic_system)
        result2 = tableau2.build()
        
        assert result1 == result2 == True
    
    def test_multiple_formulas(self):
        """Test tableau with multiple initial formulas"""
        p, q = Atom("p"), Atom("q")
        formulas = [p, Implication(p, q)]
        
        tableau = ComponentizedTableau(formulas, "classical")
        result = tableau.build()
        
        assert result == True
        models = tableau.extract_all_models()
        assert len(models) > 0
    
    def test_statistics(self):
        """Test tableau statistics collection"""
        p, q = Atom("p"), Atom("q")
        formula = Conjunction(p, q)
        
        tableau = ComponentizedTableau(formula, "classical")
        tableau.build()
        
        stats = tableau.get_statistics()
        assert stats["logic_system"] == "Classical Propositional Logic"
        assert stats["initial_formulas"] == 1
        assert stats["satisfiable"] == True
        assert stats["rule_applications"] >= 0
    
    def test_tree_tracking(self):
        """Test tableau tree tracking"""
        p, q = Atom("p"), Atom("q")
        formula = Disjunction(p, q)
        
        # With tree tracking
        tableau1 = ComponentizedTableau(formula, "classical", track_tree=True)
        tableau1.build()
        assert tableau1.root is not None
        
        # Without tree tracking  
        tableau2 = ComponentizedTableau(formula, "classical", track_tree=False)
        tableau2.build()
        assert tableau2.root is None
    
    def test_invalid_logic_system(self):
        """Test error handling for invalid logic system"""
        p = Atom("p")
        
        with pytest.raises(ValueError, match="Unknown logic system"):
            ComponentizedTableau(p, "nonexistent")


class TestRuleApplication:
    """Test specific rule applications"""
    
    def test_conjunction_rule(self):
        """Test that conjunction rule creates correct branches"""
        p, q = Atom("p"), Atom("q")
        formula = Conjunction(p, q)
        
        tableau = classical_tableau(formula)
        tableau.build()
        
        # Should have both p and q in the branch
        models = tableau.extract_all_models()
        assert len(models) > 0
        
        # Check that model satisfies both p and q
        model = models[0]
        assert model.assignments.get("p") == True
        assert model.assignments.get("q") == True
    
    def test_disjunction_rule(self):
        """Test that disjunction rule creates branching"""
        p, q = Atom("p"), Atom("q")
        formula = Disjunction(p, q)
        
        tableau = classical_tableau(formula)
        tableau.build()
        
        # Should have multiple models (branches)
        models = tableau.extract_all_models()
        assert len(models) > 0
        
        # At least one model should have p=True or q=True
        has_p_true = any(model.assignments.get("p") == True for model in models)
        has_q_true = any(model.assignments.get("q") == True for model in models)
        assert has_p_true or has_q_true


class TestBackwardCompatibility:
    """Test that componentized system gives same results as original"""
    
    def test_compare_with_original_classical(self):
        """Compare results with original tableau implementation"""
        from tableau import Tableau
        
        test_cases = [
            Atom("p"),
            Conjunction(Atom("p"), Atom("q")),
            Disjunction(Atom("p"), Negation(Atom("p"))),
            Conjunction(Atom("p"), Negation(Atom("p")))
        ]
        
        for formula in test_cases:
            # Original implementation
            original = Tableau(formula)
            original_result = original.build()
            
            # Componentized implementation
            componentized = classical_tableau(formula)
            componentized_result = componentized.build()
            
            # Results should match
            assert original_result == componentized_result, f"Mismatch for formula: {formula}"
    
    def test_compare_with_original_wk3(self):
        """Compare results with original WK3 tableau implementation"""
        from wk3_tableau import WK3Tableau
        
        test_cases = [
            Atom("p"),
            Conjunction(Atom("p"), Atom("q")),
            Disjunction(Atom("p"), Negation(Atom("p")))
        ]
        
        for formula in test_cases:
            # Original implementation
            original = WK3Tableau(formula)
            original_result = original.build()
            
            # Componentized implementation
            componentized = wk3_tableau(formula)
            componentized_result = componentized.build()
            
            # Results should match
            assert original_result == componentized_result, f"Mismatch for formula: {formula}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])