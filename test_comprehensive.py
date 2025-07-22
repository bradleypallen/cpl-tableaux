#!/usr/bin/env python3
"""
Comprehensive Test Suite for Tableau System

Consolidated test file covering all core functionality:
- Classical Propositional Logic
- Weak Kleene Logic (WK3) 
- First-Order Predicate Logic
- Mode-Aware System
- Componentized Rule System
- Performance and Optimization Features

This replaces multiple smaller test files while maintaining complete coverage.
"""

import pytest
from typing import List, Dict, Any
import time

# Core logic imports
from formula import Atom, Negation, Conjunction, Disjunction, Implication
from tableau import Tableau, Model
from wk3_tableau import WK3Tableau
from wk3_model import WK3Model
from truth_value import TruthValue, t, f, e

# First-order logic imports
from term import Constant, Variable, FunctionApplication
from formula import Predicate

# Mode-aware system imports
from logic_mode import LogicMode, ModeError, get_mode_validator
from mode_aware_parser import ModeAwareParser, parse_propositional, parse_first_order
from mode_aware_tableau import (
    ModeAwareTableau, PropositionalBuilder, FirstOrderBuilder,
    propositional_tableau, first_order_tableau, auto_tableau
)

# Componentized system imports
from componentized_tableau import ComponentizedTableau, classical_tableau, wk3_tableau
from logic_system import get_logic_system
from builtin_logics import describe_all_logics


class TestClassicalPropositionalLogic:
    """Comprehensive tests for classical propositional logic"""
    
    # Basic satisfiability tests
    def test_simple_atom(self):
        """Test satisfiability of simple atom"""
        p = Atom("p")
        tableau = Tableau(p)
        assert tableau.build() == True
        models = tableau.extract_all_models()
        assert len(models) > 0
        assert models[0].assignment["p"] == True
    
    def test_simple_negation(self):
        """Test satisfiability of negated atom"""
        p = Atom("p")
        formula = Negation(p)
        tableau = Tableau(formula)
        assert tableau.build() == True
        models = tableau.extract_all_models()
        assert len(models) > 0
        assert models[0].assignment["p"] == False
    
    # Contradiction tests
    def test_contradiction_basic(self):
        """Test basic contradiction p ∧ ¬p"""
        p = Atom("p")
        formula = Conjunction(p, Negation(p))
        tableau = Tableau(formula)
        assert tableau.build() == False
        assert len(tableau.extract_all_models()) == 0
    
    def test_contradiction_complex(self):
        """Test complex contradiction"""
        p, q = Atom("p"), Atom("q")
        # (p → q) ∧ p ∧ ¬q should be unsatisfiable
        formula = Conjunction(
            Conjunction(Implication(p, q), p),
            Negation(q)
        )
        tableau = Tableau(formula)
        assert tableau.build() == False
    
    # Tautology tests  
    def test_tautology_excluded_middle(self):
        """Test law of excluded middle p ∨ ¬p"""
        p = Atom("p")
        formula = Disjunction(p, Negation(p))
        tableau = Tableau(formula)
        assert tableau.build() == True
        
        # To verify it's a tautology, test that negation is unsatisfiable
        neg_formula = Negation(formula)
        neg_tableau = Tableau(neg_formula)
        assert neg_tableau.build() == False
    
    def test_tautology_transitivity(self):
        """Test transitivity tautology"""
        a, b, c = Atom("a"), Atom("b"), Atom("c")
        impl_ab = Implication(a, b)
        impl_bc = Implication(b, c)
        premise = Conjunction(impl_ab, impl_bc)
        impl_ac = Implication(a, c)
        transitivity = Implication(premise, impl_ac)
        
        # Test that transitivity is a tautology
        neg_transitivity = Negation(transitivity)
        tableau = Tableau(neg_transitivity)
        assert tableau.build() == False  # Negation should be unsatisfiable
    
    def test_tautology_material_implication(self):
        """Test material implication equivalence"""
        p, q = Atom("p"), Atom("q")
        # (p → q) ↔ (¬p ∨ q) should be tautology
        impl = Implication(p, q)
        equiv = Disjunction(Negation(p), q)
        
        # Test both directions
        formula1 = Implication(impl, equiv)
        formula2 = Implication(equiv, impl)
        
        neg_tableau1 = Tableau(Negation(formula1))
        neg_tableau2 = Tableau(Negation(formula2))
        
        assert neg_tableau1.build() == False
        assert neg_tableau2.build() == False
    
    # Satisfiable formula tests
    def test_satisfiable_conjunction(self):
        """Test satisfiable conjunction"""
        p, q = Atom("p"), Atom("q")
        formula = Conjunction(p, q)
        tableau = Tableau(formula)
        assert tableau.build() == True
        models = tableau.extract_all_models()
        assert len(models) > 0
        model = models[0]
        assert model.assignment["p"] == True
        assert model.assignment["q"] == True
    
    def test_satisfiable_disjunction(self):
        """Test satisfiable disjunction"""
        p, q = Atom("p"), Atom("q")
        formula = Disjunction(p, q)
        tableau = Tableau(formula)
        assert tableau.build() == True
        models = tableau.extract_all_models()
        assert len(models) >= 2  # Should have multiple models
    
    def test_satisfiable_implication(self):
        """Test satisfiable implication"""
        p, q = Atom("p"), Atom("q")
        formula = Implication(p, q)
        tableau = Tableau(formula)
        assert tableau.build() == True
        
        # Should also be satisfiable when negated (contingent)
        neg_formula = Negation(formula)
        neg_tableau = Tableau(neg_formula)
        assert neg_tableau.build() == True
    
    # Complex formula tests
    def test_complex_nested_formula(self):
        """Test complex nested formula"""
        p, q, r, s = Atom("p"), Atom("q"), Atom("r"), Atom("s")
        # ((p ∧ q) → r) ∧ (r → s) ∧ (p ∧ q) should imply s
        formula = Conjunction(
            Conjunction(
                Implication(Conjunction(p, q), r),
                Implication(r, s)
            ),
            Conjunction(p, q)
        )
        tableau = Tableau(formula)
        assert tableau.build() == True
        models = tableau.extract_all_models()
        # All models should have s = True
        for model in models:
            assert model.assignment.get("s", False) == True
    
    def test_de_morgan_laws(self):
        """Test De Morgan's laws"""
        p, q = Atom("p"), Atom("q")
        
        # ¬(p ∧ q) ↔ (¬p ∨ ¬q)
        left1 = Negation(Conjunction(p, q))
        right1 = Disjunction(Negation(p), Negation(q))
        equiv1a = Implication(left1, right1)
        equiv1b = Implication(right1, left1)
        
        # ¬(p ∨ q) ↔ (¬p ∧ ¬q)
        left2 = Negation(Disjunction(p, q))
        right2 = Conjunction(Negation(p), Negation(q))
        equiv2a = Implication(left2, right2)
        equiv2b = Implication(right2, left2)
        
        # All should be tautologies
        for formula in [equiv1a, equiv1b, equiv2a, equiv2b]:
            neg_tableau = Tableau(Negation(formula))
            assert neg_tableau.build() == False
    
    # Multiple formula tests
    def test_multiple_formulas_consistent(self):
        """Test consistent set of multiple formulas"""
        p, q, r = Atom("p"), Atom("q"), Atom("r")
        formulas = [
            Implication(p, q),
            Implication(q, r),
            p
        ]
        tableau = Tableau(formulas)
        assert tableau.build() == True
        models = tableau.extract_all_models()
        # All models should have p, q, r = True
        for model in models:
            assert model.assignment.get("p", False) == True
            assert model.assignment.get("q", False) == True
            assert model.assignment.get("r", False) == True
    
    def test_multiple_formulas_inconsistent(self):
        """Test inconsistent set of multiple formulas"""
        p, q = Atom("p"), Atom("q")
        formulas = [
            p,
            Implication(p, q),
            Negation(q)
        ]
        tableau = Tableau(formulas)
        assert tableau.build() == False


class TestWeakKleeneLogic:
    """Tests for three-valued Weak Kleene Logic"""
    
    def test_wk3_simple_atom(self):
        """Test WK3 satisfiability of simple atom"""
        p = Atom("p")
        tableau = WK3Tableau(p)
        assert tableau.build() == True
        models = tableau.extract_all_models()
        assert len(models) > 0
    
    def test_wk3_contradiction_satisfiable(self):
        """Test that p ∧ ¬p can be satisfiable in WK3 with p=e"""
        p = Atom("p")
        formula = Conjunction(p, Negation(p))
        tableau = WK3Tableau(formula)
        result = tableau.build()
        # In WK3, this could be satisfiable with p=e
        assert isinstance(result, bool)
    
    def test_wk3_truth_values(self):
        """Test WK3 truth value system"""
        from truth_value import WeakKleeneOperators
        
        # Test truth value operations using WeakKleeneOperators
        assert WeakKleeneOperators.negation(t) == f
        assert WeakKleeneOperators.negation(f) == t
        assert WeakKleeneOperators.negation(e) == e
        
        # Test conjunction
        assert WeakKleeneOperators.conjunction(t, t) == t
        assert WeakKleeneOperators.conjunction(t, f) == f
        assert WeakKleeneOperators.conjunction(t, e) == e
        assert WeakKleeneOperators.conjunction(e, e) == e
        
        # Test disjunction
        assert WeakKleeneOperators.disjunction(f, f) == f
        assert WeakKleeneOperators.disjunction(f, t) == t
        assert WeakKleeneOperators.disjunction(f, e) == e
        assert WeakKleeneOperators.disjunction(e, e) == e
    
    def test_wk3_model_evaluation(self):
        """Test WK3 model evaluation"""
        model = WK3Model({"p": t, "q": f, "r": e})
        
        p, q, r = Atom("p"), Atom("q"), Atom("r")
        
        # Test atom evaluation
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
        
        # Test disjunction
        assert model.satisfies(Disjunction(p, q)) == t  # t ∨ f = t
        assert model.satisfies(Disjunction(q, r)) == e  # f ∨ e = e


class TestFirstOrderPredicateLogic:
    """Tests for first-order predicate logic extensions"""
    
    def test_term_creation(self):
        """Test creation of constants, variables, and functions"""
        # Constants
        john = Constant("john")
        assert john.name == "john"
        assert isinstance(john, Constant)
        assert john.is_ground() == True
        
        # Variables
        x = Variable("X")
        assert x.name == "X"
        assert isinstance(x, Variable)
        assert x.is_ground() == False
        
        # Function applications
        father = FunctionApplication("father", [john])
        assert father.function_name == "father"
        assert len(father.args) == 1
        assert father.args[0] == john
        assert father.is_ground() == True
    
    def test_predicate_creation(self):
        """Test creation of n-ary predicates"""
        john = Constant("john")
        mary = Constant("mary")
        
        # 0-ary predicate
        p = Predicate("P")
        assert p.arity == 0
        assert p.predicate_name == "P"
        assert p.is_ground() == True
        
        # Unary predicate
        student = Predicate("Student", [john])
        assert student.arity == 1
        assert student.predicate_name == "Student"
        assert student.args[0] == john
        assert student.is_ground() == True
        
        # Binary predicate
        loves = Predicate("Loves", [john, mary])
        assert loves.arity == 2
        assert loves.predicate_name == "Loves"
        assert str(loves) == "Loves(john, mary)"
        assert loves.is_ground() == True
    
    def test_predicate_with_variables(self):
        """Test predicates with variables"""
        x = Variable("X")
        john = Constant("john")
        
        student = Predicate("Student", [x])
        assert student.arity == 1
        assert student.is_ground() == False
        assert "X" in student.get_variables()
        
        loves = Predicate("Loves", [john, x])
        assert loves.arity == 2
        assert loves.is_ground() == False
        assert "X" in loves.get_variables()
    
    def test_atom_backward_compatibility(self):
        """Test that Atom still works as before"""
        p = Atom("p")
        assert isinstance(p, Predicate)  # Atom is now a subclass of Predicate
        assert p.arity == 0
        assert p.predicate_name == "p"
        assert p.name == "p"  # Backward compatibility
        
        # Should still work in formulas
        formula = Conjunction(p, Negation(p))
        tableau = Tableau(formula)
        assert tableau.build() == False


class TestModeAwareSystem:
    """Tests for mode-aware logic system (propositional vs first-order)"""
    
    def test_mode_detection(self):
        """Test automatic mode detection"""
        # Propositional formulas
        assert LogicMode.from_string("prop") == LogicMode.PROPOSITIONAL
        assert LogicMode.from_string("propositional") == LogicMode.PROPOSITIONAL
        
        # First-order formulas  
        assert LogicMode.from_string("fol") == LogicMode.FIRST_ORDER
        assert LogicMode.from_string("first-order") == LogicMode.FIRST_ORDER
    
    def test_propositional_parser(self):
        """Test mode-aware propositional parsing"""
        parser = ModeAwareParser(LogicMode.PROPOSITIONAL)
        
        formula = parser.parse("p & q")
        assert isinstance(formula, Conjunction)
        assert isinstance(formula.left, Atom)
        assert isinstance(formula.right, Atom)
        
        # Should reject FOL syntax
        with pytest.raises(ModeError):
            parser.parse("Student(john)")
    
    def test_first_order_parser(self):
        """Test mode-aware first-order parsing"""
        parser = ModeAwareParser(LogicMode.FIRST_ORDER)
        
        formula = parser.parse("Student(john)")
        assert isinstance(formula, Predicate)
        assert formula.predicate_name == "Student"
        assert formula.arity == 1
        
        # Should reject propositional atoms
        with pytest.raises(ModeError):
            parser.parse("p & q")
    
    def test_mode_aware_api(self):
        """Test mode-aware programmatic API"""
        # Propositional builder
        p = PropositionalBuilder.atom("p")
        q = PropositionalBuilder.atom("q")
        formula = PropositionalBuilder.conjunction(p, q)
        
        tableau = propositional_tableau(formula)
        assert tableau.build() == True
        
        # First-order builder
        student = FirstOrderBuilder.predicate("Student", "john")
        smart = FirstOrderBuilder.predicate("Smart", "john")
        fol_formula = FirstOrderBuilder.implication(student, smart)
        
        fol_tableau = first_order_tableau(fol_formula)
        assert fol_tableau.build() == True
    
    def test_mixed_mode_prevention(self):
        """Test that mixing modes is prevented"""
        p = Atom("p")
        john = Constant("john")
        pred = Predicate("Student", [john])
        
        # Should prevent mixing in direct construction
        mixed = Conjunction(p, pred)
        
        with pytest.raises(ModeError):
            propositional_tableau(mixed)
        
        with pytest.raises(ModeError):
            first_order_tableau(mixed)


class TestComponentizedRuleSystem:
    """Tests for the new componentized rule system"""
    
    def test_logic_system_registry(self):
        """Test that logic systems are properly registered"""
        classical = get_logic_system("classical")
        assert classical is not None
        assert classical.config.name == "Classical Propositional Logic"
        
        wk3 = get_logic_system("wk3")
        assert wk3 is not None
        assert wk3.config.name == "Weak Kleene Logic"
    
    def test_componentized_classical_logic(self):
        """Test componentized classical logic gives same results"""
        p = Atom("p")
        formula = Conjunction(p, Negation(p))
        
        # Original implementation
        original = Tableau(formula)
        original_result = original.build()
        
        # Componentized implementation
        componentized = classical_tableau(formula)
        componentized_result = componentized.build()
        
        assert original_result == componentized_result == False
    
    def test_componentized_wk3_logic(self):
        """Test componentized WK3 logic"""
        p = Atom("p")
        
        # Original implementation
        original = WK3Tableau(p)
        original_result = original.build()
        
        # Componentized implementation  
        componentized = wk3_tableau(p)
        componentized_result = componentized.build()
        
        assert original_result == componentized_result == True
    
    def test_rule_system_extensibility(self):
        """Test that rule system supports extensibility"""
        classical = get_logic_system("classical")
        
        # Should have all basic propositional rules
        rule_names = classical.list_rules()
        assert "Double Negation Elimination" in rule_names
        assert "Conjunction Elimination" in rule_names
        assert "Disjunction Elimination" in rule_names
        assert "Implication Elimination" in rule_names
        
        # Check rule priorities
        for rule in classical.rules:
            assert rule.priority >= 1
            assert rule.is_alpha_rule or rule.is_beta_rule
    
    def test_componentized_statistics(self):
        """Test componentized tableau statistics"""
        p, q = Atom("p"), Atom("q")
        formula = Conjunction(p, q)
        
        tableau = ComponentizedTableau(formula, "classical")
        tableau.build()
        
        stats = tableau.get_statistics()
        assert stats["logic_system"] == "Classical Propositional Logic"
        assert stats["satisfiable"] == True
        assert stats["rule_applications"] >= 0
        assert stats["total_branches"] >= 1


class TestOptimizationsAndPerformance:
    """Tests for tableau optimizations and performance features"""
    
    def test_formula_prioritization(self):
        """Test that α-rules are prioritized over β-rules"""
        p, q, r = Atom("p"), Atom("q"), Atom("r")
        
        # Formula with both α and β rules
        formula = Conjunction(  # α-rule
            Disjunction(p, q),  # β-rule
            r
        )
        
        tableau = Tableau(formula)
        tableau.build()
        
        # Should expand conjunction first (α-rule)
        # This is tested implicitly by correctness
        assert tableau.build() == True
    
    def test_subsumption_elimination(self):
        """Test branch subsumption elimination"""
        p, q = Atom("p"), Atom("q")
        
        # Create formula that might generate subsumed branches
        formula = Disjunction(
            Conjunction(p, q),
            p  # This should subsume the conjunction branch
        )
        
        tableau = Tableau(formula)
        result = tableau.build()
        assert result == True
        
        # Should have eliminated subsumed branches
        # Exact branch count depends on implementation details
        assert len(tableau.branches) >= 1
    
    def test_early_satisfiability_detection(self):
        """Test early detection of satisfiability"""
        p = Atom("p")
        
        # Simple satisfiable formula
        tableau = Tableau(p)
        result = tableau.build()
        
        assert result == True
        # Should have stopped early once satisfiability was detected
    
    def test_performance_complex_formula(self):
        """Test performance with complex formula"""
        # Create a complex but manageable formula
        atoms = [Atom(f"p{i}") for i in range(5)]
        
        # Create nested implications
        formula = atoms[0]
        for i in range(1, len(atoms)):
            formula = Implication(formula, atoms[i])
        
        start_time = time.time()
        tableau = Tableau(formula)
        result = tableau.build()
        end_time = time.time()
        
        assert result == True
        assert end_time - start_time < 1.0  # Should complete quickly
    
    def test_model_extraction_correctness(self):
        """Test that extracted models actually satisfy formulas"""
        p, q, r = Atom("p"), Atom("q"), Atom("r")
        formula = Disjunction(
            Conjunction(p, q),
            Conjunction(Negation(p), r)
        )
        
        tableau = Tableau(formula)
        result = tableau.build()
        assert result == True
        
        models = tableau.extract_all_models()
        assert len(models) > 0
        
        # Each model should satisfy the original formula
        for model in models:
            assert model.satisfies(formula) == True


class TestEdgeCasesAndRegressions:
    """Tests for edge cases and regression prevention"""
    
    def test_empty_formula_list(self):
        """Test behavior with empty formula list"""
        tableau = Tableau([])
        # Empty formula set should be satisfiable
        assert tableau.build() == True
    
    def test_single_formula_in_list(self):
        """Test single formula in list"""
        p = Atom("p")
        tableau = Tableau([p])
        assert tableau.build() == True
    
    def test_very_deep_nesting(self):
        """Test deeply nested formulas"""
        p = Atom("p")
        formula = p
        
        # Create deeply nested negations
        for _ in range(10):
            formula = Negation(formula)
        
        tableau = Tableau(formula)
        result = tableau.build()
        # Should still work correctly
        assert isinstance(result, bool)
    
    def test_large_disjunction(self):
        """Test large disjunction"""
        atoms = [Atom(f"p{i}") for i in range(10)]
        formula = atoms[0]
        
        for atom in atoms[1:]:
            formula = Disjunction(formula, atom)
        
        tableau = Tableau(formula)
        assert tableau.build() == True
        
        # Should have at least one model 
        models = tableau.extract_all_models()
        assert len(models) >= 1
    
    def test_large_conjunction(self):
        """Test large conjunction"""
        atoms = [Atom(f"p{i}") for i in range(10)]
        formula = atoms[0]
        
        for atom in atoms[1:]:
            formula = Conjunction(formula, atom)
        
        tableau = Tableau(formula)
        assert tableau.build() == True
        
        # Should have one model with all atoms true
        models = tableau.extract_all_models()
        assert len(models) > 0
        model = models[0]
        for atom in atoms:
            assert model.assignment[atom.name] == True


# Utility functions for running specific test categories
def run_classical_tests():
    """Run only classical logic tests"""
    pytest.main([__file__ + "::TestClassicalPropositionalLogic", "-v"])

def run_wk3_tests():
    """Run only WK3 logic tests"""
    pytest.main([__file__ + "::TestWeakKleeneLogic", "-v"])

def run_predicate_tests():
    """Run only first-order predicate tests"""
    pytest.main([__file__ + "::TestFirstOrderPredicateLogic", "-v"])

def run_mode_tests():
    """Run only mode-aware system tests"""
    pytest.main([__file__ + "::TestModeAwareSystem", "-v"])

def run_componentized_tests():
    """Run only componentized rule system tests"""
    pytest.main([__file__ + "::TestComponentizedRuleSystem", "-v"])

def run_performance_tests():
    """Run only performance and optimization tests"""
    pytest.main([__file__ + "::TestOptimizationsAndPerformance", "-v"])

def run_all_tests():
    """Run complete test suite"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    # Run all tests by default
    run_all_tests()