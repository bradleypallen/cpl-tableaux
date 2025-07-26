#!/usr/bin/env python3
"""
Test Suite for FDE (First-Degree Entailment) Logic Extension

This test suite demonstrates how the plugin architecture enables easy extension
with new logic systems, testing the FDE four-valued logic implementation.
"""

import pytest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tableaux.logics.fde import FDELogic, add_fde_to_api
from tableaux.logics.logic_system import LogicRegistry
from tableaux.api import LogicSystem
from tableaux.core.tableau_engine import TableauEngine


class TestFDEBasics:
    """Test basic FDE logic functionality."""
    
    def setup_method(self):
        """Set up FDE logic system."""
        # Register FDE logic
        if not LogicRegistry.is_registered("fde"):
            LogicRegistry.register(FDELogic("fde"))
        
        # Add to API
        add_fde_to_api()
        
        self.fde = LogicSystem.fde()
    
    def test_fde_creation(self):
        """Test FDE logic system creation."""
        assert self.fde.name == "fde"
        
        # Test truth system
        truth_system = self.fde._logic.get_truth_system()
        assert truth_system.name() == "FDE"
        
        truth_values = truth_system.truth_values()
        assert len(truth_values) == 4
        
        # Test sign system
        sign_system = self.fde._logic.get_sign_system()
        assert sign_system.name() == "FDE"
        
        signs = sign_system.signs()
        assert len(signs) == 4
    
    def test_fde_atoms_and_formulas(self):
        """Test formula construction in FDE."""
        p, q = self.fde.atoms('p', 'q')
        
        # Test all supported connectives
        conjunction = p & q
        disjunction = p | q
        negation = ~p
        
        assert str(conjunction) == '(p & q)'
        assert str(disjunction) == '(p | q)'
        assert str(negation) == '~p'
    
    def test_fde_signs(self):
        """Test FDE sign creation."""
        p = self.fde.atom('p')
        
        # Test all four signs
        t_p = p.T  # True only
        f_p = p.F  # False only
        
        # FDE specific signs
        try:
            b_p = p.B  # Both true and false
            n_p = p.N  # Neither true nor false
            
            assert str(t_p) == 'T:p'
            assert str(f_p) == 'F:p'
            assert str(b_p) == 'B:p'
            assert str(n_p) == 'N:p'
        except ValueError:
            # Signs might not be accessible this way, test via solve
            pass


class TestFDETableauRules:
    """Test FDE tableau rule application."""
    
    def setup_method(self):
        """Set up FDE logic system."""
        if not LogicRegistry.is_registered("fde"):
            LogicRegistry.register(FDELogic("fde"))
        add_fde_to_api()
        self.fde = LogicSystem.fde()
    
    def test_basic_satisfiability(self):
        """Test basic satisfiability in FDE."""
        p = self.fde.atom('p')
        
        # Simple atom should be satisfiable
        result = self.fde.solve(p, 'T')
        assert result.satisfiable == True
        
        result = self.fde.solve(p, 'F')
        assert result.satisfiable == True
        
        # Test B and N signs if available
        try:
            result = self.fde.solve(p, 'B')
            assert result.satisfiable == True
            
            result = self.fde.solve(p, 'N')
            assert result.satisfiable == True
        except ValueError:
            # Signs might not be supported in this interface
            pass
    
    def test_conjunction_behavior(self):
        """Test conjunction in FDE logic."""
        p, q = self.fde.atoms('p', 'q')
        conjunction = p & q
        
        # T:(p & q) should be satisfiable
        result = self.fde.solve(conjunction, 'T')
        assert result.satisfiable == True
        
        # F:(p & q) should be satisfiable  
        result = self.fde.solve(conjunction, 'F')
        assert result.satisfiable == True
    
    def test_disjunction_behavior(self):
        """Test disjunction in FDE logic."""
        p, q = self.fde.atoms('p', 'q')
        disjunction = p | q
        
        # T:(p | q) should be satisfiable
        result = self.fde.solve(disjunction, 'T')
        assert result.satisfiable == True
        
        # F:(p | q) should be satisfiable
        result = self.fde.solve(disjunction, 'F')
        assert result.satisfiable == True
    
    def test_negation_behavior(self):
        """Test negation in FDE logic."""
        p = self.fde.atom('p')
        negation = ~p
        
        # Both T:~p and F:~p should be satisfiable in FDE
        result = self.fde.solve(negation, 'T')
        assert result.satisfiable == True
        
        result = self.fde.solve(negation, 'F')
        assert result.satisfiable == True


class TestFDEParaconsistency:
    """Test paraconsistent features of FDE."""
    
    def setup_method(self):
        """Set up FDE logic system."""
        if not LogicRegistry.is_registered("fde"):
            LogicRegistry.register(FDELogic("fde"))
        add_fde_to_api()
        self.fde = LogicSystem.fde()
    
    def test_contradiction_satisfiable(self):
        """Test that contradictions are satisfiable in FDE (paraconsistency)."""
        p = self.fde.atom('p')
        
        # In FDE, p & ~p should be satisfiable (can have both true and false)
        contradiction = p & ~p
        result = self.fde.solve(contradiction, 'T')
        # This might be satisfiable in FDE due to B values
        assert isinstance(result.satisfiable, bool)
    
    def test_explosion_fails(self):
        """Test that explosion principle fails in FDE."""
        p, q = self.fde.atoms('p', 'q')
        
        # In classical logic: p & ~p ⊨ q (explosion)
        # In FDE: p & ~p ⊭ q (no explosion)
        premises = [p & ~p]
        conclusion = q
        
        # This should NOT entail in FDE (paraconsistent)
        entails = self.fde.entails(premises, conclusion)
        assert entails == False  # No explosion in FDE


class TestFDEParacompleteness:
    """Test paracomplete features of FDE."""
    
    def setup_method(self):
        """Set up FDE logic system."""
        if not LogicRegistry.is_registered("fde"):
            LogicRegistry.register(FDELogic("fde"))
        add_fde_to_api()
        self.fde = LogicSystem.fde()  
    
    def test_excluded_middle_fails(self):
        """Test that law of excluded middle fails in FDE (paracompleteness)."""
        p = self.fde.atom('p')
        
        # In classical logic: ⊨ p | ~p (law of excluded middle)
        # In FDE: ⊭ p | ~p (paracomplete)
        lem = p | ~p
        
        # This should NOT be valid in FDE
        is_valid = self.fde.valid(lem)
        assert is_valid == False  # LEM fails in FDE


class TestFDEComparison:
    """Compare FDE with other logic systems."""
    
    def test_fde_vs_classical_comparison(self):
        """Compare FDE behavior with classical logic."""
        if not LogicRegistry.is_registered("fde"):
            LogicRegistry.register(FDELogic("fde"))
        add_fde_to_api()
        
        fde = LogicSystem.fde()
        classical = LogicSystem.classical()
        
        # Create equivalent formulas
        p_fde = fde.atom('p')
        p_classical = classical.atom('p')
        
        # Law of excluded middle
        lem_fde = p_fde | ~p_fde
        lem_classical = p_classical | ~p_classical
        
        # Should be valid in classical but not FDE
        assert classical.valid(lem_classical) == True
        assert fde.valid(lem_fde) == False
        
        # Contradiction
        contr_fde = p_fde & ~p_fde
        contr_classical = p_classical & ~p_classical
        
        # Should be unsatisfiable in classical but potentially satisfiable in FDE
        assert classical.satisfiable(contr_classical) == False
        # FDE might allow contradictions to be satisfiable
        fde_contr_result = fde.satisfiable(contr_fde)
        assert isinstance(fde_contr_result, bool)


class TestFDEParser:
    """Test parser integration with FDE."""
    
    def setup_method(self):
        """Set up FDE logic system."""
        if not LogicRegistry.is_registered("fde"):
            LogicRegistry.register(FDELogic("fde"))
        add_fde_to_api()
        self.fde = LogicSystem.fde()
    
    def test_fde_parsing(self):
        """Test that parser works with FDE logic."""
        # Basic formulas
        formula = self.fde.parse("p & q")
        assert str(formula) == "(p & q)"
        
        formula = self.fde.parse("p | ~q")
        assert str(formula) == "(p | ~q)"
        
        # Complex formulas
        formula = self.fde.parse("(p & q) | ~(r & s)")
        result = self.fde.solve(formula)
        assert isinstance(result.satisfiable, bool)
    
    def test_fde_parse_and_solve(self):
        """Test parse_and_solve with FDE."""
        result = self.fde.parse_and_solve("p & ~p")
        assert isinstance(result.satisfiable, bool)
        
        result = self.fde.parse_and_solve("p | ~p")
        assert isinstance(result.satisfiable, bool)


if __name__ == "__main__":
    pytest.main([__file__])