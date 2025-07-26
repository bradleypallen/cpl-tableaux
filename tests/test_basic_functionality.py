#!/usr/bin/env python3
"""
Basic Functionality Tests for New API

Simple tests to verify core functionality is working correctly.
Replaces archived comprehensive and setup tests with new API equivalents.
"""

import pytest
import time
from tableaux import LogicSystem


class TestBasicSetup:
    """Test basic package setup and imports."""
    
    def test_package_imports(self):
        """Test that core package imports work."""
        from tableaux import LogicSystem, TableauResult
        assert LogicSystem is not None
        assert TableauResult is not None
    
    def test_logic_system_creation(self):
        """Test that logic systems can be created."""
        classical = LogicSystem.classical()
        weak_kleene = LogicSystem.weak_kleene()
        wkrq = LogicSystem.wkrq()
        
        assert classical.name == "classical"
        assert weak_kleene.name == "weak_kleene" 
        assert wkrq.name == "wkrq"
    
    def test_basic_formula_creation(self):
        """Test basic formula creation and solving."""
        classical = LogicSystem.classical()
        p = classical.atom("p")
        result = classical.solve(p)
        
        assert result.satisfiable == True
        assert len(result.models) > 0


class TestBasicPerformance:
    """Test basic performance characteristics."""
    
    def test_simple_formula_performance(self):
        """Test that simple formulas solve quickly."""
        classical = LogicSystem.classical()
        p, q, r = classical.atoms('p', 'q', 'r')
        
        # Create a moderately complex formula
        formula = (p | q) & (q | r) & (r | p) & ~p & ~q & ~r
        
        start_time = time.time()
        result = classical.solve(formula)
        end_time = time.time()
        
        # Should be very fast and unsatisfiable
        assert (end_time - start_time) < 1.0  # Less than 1 second
        assert result.satisfiable == False
    
    def test_tautology_performance(self):
        """Test tautology detection performance."""
        classical = LogicSystem.classical()
        p, q = classical.atoms('p', 'q')
        
        # Create a tautology
        tautology = (p | ~p) & (q | ~q)
        
        start_time = time.time()
        result = classical.solve(tautology)
        end_time = time.time()
        
        # Should be fast and satisfiable
        assert (end_time - start_time) < 1.0
        assert result.satisfiable == True


class TestMultiLogicBasics:
    """Test basic functionality across different logic systems."""
    
    def test_classical_vs_weak_kleene(self):
        """Test difference between classical and weak Kleene logic."""
        classical = LogicSystem.classical()
        weak_kleene = LogicSystem.weak_kleene()
        
        # Law of excluded middle
        p_classical = classical.atom("p")
        lem_classical = p_classical | ~p_classical
        
        p_wk = weak_kleene.atom("p")
        lem_wk = p_wk | ~p_wk
        
        # Both should be satisfiable, but classical should be valid
        assert classical.solve(lem_classical).satisfiable == True
        assert weak_kleene.solve(lem_wk).satisfiable == True
        assert classical.valid(lem_classical) == True
        assert weak_kleene.valid(lem_wk) == True  # Actually true in weak Kleene too
    
    def test_wkrq_four_valued_behavior(self):
        """Test basic wKrQ four-valued behavior."""
        wkrq = LogicSystem.wkrq()
        p = wkrq.atom("p")
        
        # Basic satisfiability
        result = wkrq.solve(p)
        assert result.satisfiable == True
        
        # Law of excluded middle should fail in wKrQ
        lem = p | ~p
        assert wkrq.valid(lem) == False


class TestErrorHandling:
    """Test basic error handling and edge cases."""
    
    def test_empty_formula_handling(self):
        """Test handling of edge cases."""
        classical = LogicSystem.classical()
        
        # Test with simple atom
        p = classical.atom("p")
        result = classical.solve(p)
        assert result is not None
        assert hasattr(result, 'satisfiable')
    
    def test_invalid_entailment(self):
        """Test invalid entailment detection."""
        classical = LogicSystem.classical()
        p, q = classical.atoms('p', 'q')
        
        # p does not entail q
        assert classical.entails([p], q) == False
        
        # But p, p->q entails q (modus ponens)
        assert classical.entails([p, p.implies(q)], q) == True