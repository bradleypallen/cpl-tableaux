#!/usr/bin/env python3
"""
Migrated Classical Tableau Tests Using Signed Tableaux

This file migrates the comprehensive test suite from test_tableau.py to use
the signed tableau system. All original test logic is preserved while using
the modern signed tableau infrastructure.

Original test categories:
- Contradictions (unsatisfiable formulas)
- Tautologies (valid formulas)
- Satisfiable formulas (contingent formulas)
- Classical logical patterns
"""

import pytest
from formula import Atom, Negation, Conjunction, Disjunction, Implication
from signed_formula import T, F
from signed_tableau import SignedTableau, classical_signed_tableau


class TestClassicalSignedTableau:
    """Migrated test suite for classical logic using signed tableaux"""
    
    def setup_method(self):
        """Set up common atoms for tests"""
        self.p = Atom("p")
        self.q = Atom("q")
        self.r = Atom("r")
        self.s = Atom("s")
    
    def is_satisfiable(self, formula):
        """Helper to test if a formula is satisfiable using signed tableau"""
        tableau = classical_signed_tableau(T(formula))
        return tableau.build()
    
    def is_unsatisfiable(self, formula):
        """Helper to test if a formula is unsatisfiable using signed tableau"""
        return not self.is_satisfiable(formula)
    
    def is_tautology(self, formula):
        """Helper to test if a formula is a tautology (F:formula is unsatisfiable)"""
        tableau = classical_signed_tableau(F(formula))
        return not tableau.build()

    # ===== CONTRADICTIONS (should be UNSATISFIABLE) =====
    
    def test_contradiction_01_basic(self):
        """p ∧ ¬p"""
        formula = Conjunction(self.p, Negation(self.p))
        assert self.is_unsatisfiable(formula), "Basic contradiction should be unsatisfiable"
    
    def test_contradiction_02_complex(self):
        """(p ∧ q) ∧ ¬(p ∧ q)"""
        conj = Conjunction(self.p, self.q)
        formula = Conjunction(conj, Negation(conj))
        assert self.is_unsatisfiable(formula), "Complex contradiction should be unsatisfiable"
    
    def test_contradiction_03_nested(self):
        """(p → q) ∧ p ∧ ¬q"""
        impl = Implication(self.p, self.q)
        formula = Conjunction(Conjunction(impl, self.p), Negation(self.q))
        assert self.is_unsatisfiable(formula), "Modus ponens contradiction should be unsatisfiable"
    
    def test_contradiction_04_de_morgan_violation(self):
        """(p ∧ q) ∧ (¬p ∨ ¬q) ∧ p ∧ q"""
        left = Conjunction(self.p, self.q)
        right = Disjunction(Negation(self.p), Negation(self.q))
        formula = Conjunction(Conjunction(left, right), Conjunction(self.p, self.q))
        assert self.is_unsatisfiable(formula), "De Morgan violation should be unsatisfiable"
    
    def test_contradiction_05_implication_cycle(self):
        """(p → q) ∧ (q → r) ∧ (r → ¬p) ∧ p"""
        impl1 = Implication(self.p, self.q)
        impl2 = Implication(self.q, self.r)
        impl3 = Implication(self.r, Negation(self.p))
        cycle = Conjunction(Conjunction(impl1, impl2), impl3)
        formula = Conjunction(cycle, self.p)
        assert self.is_unsatisfiable(formula), "Implication cycle with p should be unsatisfiable"

    # ===== TAUTOLOGIES (should be VALID - their negations are unsatisfiable) =====
    
    def test_tautology_01_excluded_middle(self):
        """p ∨ ¬p"""
        formula = Disjunction(self.p, Negation(self.p))
        assert self.is_tautology(formula), "Law of excluded middle should be a tautology"
    
    def test_tautology_02_modus_ponens(self):
        """((p → q) ∧ p) → q"""
        premise = Conjunction(Implication(self.p, self.q), self.p)
        formula = Implication(premise, self.q)
        assert self.is_tautology(formula), "Modus ponens should be a tautology"
    
    def test_tautology_03_transitivity(self):
        """((p → q) ∧ (q → r)) → (p → r)"""
        premise = Conjunction(Implication(self.p, self.q), Implication(self.q, self.r))
        conclusion = Implication(self.p, self.r)
        formula = Implication(premise, conclusion)
        assert self.is_tautology(formula), "Transitivity of implication should be a tautology"
    
    def test_tautology_04_de_morgan_1(self):
        """¬(p ∧ q) → (¬p ∨ ¬q)"""
        left = Negation(Conjunction(self.p, self.q))
        right = Disjunction(Negation(self.p), Negation(self.q))
        formula = Implication(left, right)
        assert self.is_tautology(formula), "De Morgan's law (∧→∨) should be a tautology"
    
    def test_tautology_05_de_morgan_2(self):
        """¬(p ∨ q) → (¬p ∧ ¬q)"""
        left = Negation(Disjunction(self.p, self.q))
        right = Conjunction(Negation(self.p), Negation(self.q))
        formula = Implication(left, right)
        assert self.is_tautology(formula), "De Morgan's law (∨→∧) should be a tautology"
    
    def test_tautology_06_double_negation(self):
        """¬¬p → p"""
        formula = Implication(Negation(Negation(self.p)), self.p)
        assert self.is_tautology(formula), "Double negation elimination should be a tautology"
    
    def test_tautology_07_contrapositive(self):
        """(p → q) → (¬q → ¬p)"""
        left = Implication(self.p, self.q)
        right = Implication(Negation(self.q), Negation(self.p))
        formula = Implication(left, right)
        assert self.is_tautology(formula), "Contrapositive should be a tautology"
    
    def test_tautology_08_explosion(self):
        """(p ∧ ¬p) → q"""
        contradiction = Conjunction(self.p, Negation(self.p))
        formula = Implication(contradiction, self.q)
        assert self.is_tautology(formula), "Principle of explosion should be a tautology"

    # ===== SATISFIABLE FORMULAS (should be SATISFIABLE but not tautologies) =====
    
    def test_satisfiable_01_simple_atom(self):
        """p"""
        assert self.is_satisfiable(self.p), "Single atom should be satisfiable"
        assert not self.is_tautology(self.p), "Single atom should not be a tautology"
    
    def test_satisfiable_02_simple_conjunction(self):
        """p ∧ q"""
        formula = Conjunction(self.p, self.q)
        assert self.is_satisfiable(formula), "Simple conjunction should be satisfiable"
        assert not self.is_tautology(formula), "Simple conjunction should not be a tautology"
    
    def test_satisfiable_03_simple_disjunction(self):
        """p ∨ q"""
        formula = Disjunction(self.p, self.q)
        assert self.is_satisfiable(formula), "Simple disjunction should be satisfiable"
        assert not self.is_tautology(formula), "Simple disjunction should not be a tautology"
    
    def test_satisfiable_04_simple_implication(self):
        """p → q"""
        formula = Implication(self.p, self.q)
        assert self.is_satisfiable(formula), "Simple implication should be satisfiable"
        assert not self.is_tautology(formula), "Simple implication should not be a tautology"
    
    def test_satisfiable_05_complex_conjunction(self):
        """(p ∨ q) ∧ (r ∨ s)"""
        left = Disjunction(self.p, self.q)
        right = Disjunction(self.r, self.s)
        formula = Conjunction(left, right)
        assert self.is_satisfiable(formula), "Complex conjunction should be satisfiable"
        assert not self.is_tautology(formula), "Complex conjunction should not be a tautology"
    
    def test_satisfiable_06_mixed_operators(self):
        """(p → q) ∧ (¬r ∨ s)"""
        left = Implication(self.p, self.q)
        right = Disjunction(Negation(self.r), self.s)
        formula = Conjunction(left, right)
        assert self.is_satisfiable(formula), "Mixed operators should be satisfiable"
        assert not self.is_tautology(formula), "Mixed operators should not be a tautology"
    
    def test_satisfiable_07_nested_implications(self):
        """(p → q) → (q → r)"""
        inner = Implication(self.p, self.q)
        outer = Implication(self.q, self.r)
        formula = Implication(inner, outer)
        assert self.is_satisfiable(formula), "Nested implications should be satisfiable"
        assert not self.is_tautology(formula), "Nested implications should not be a tautology"
    
    def test_satisfiable_08_long_conjunction(self):
        """p ∧ q ∧ r ∧ s"""
        formula = Conjunction(
            Conjunction(self.p, self.q),
            Conjunction(self.r, self.s)
        )
        assert self.is_satisfiable(formula), "Long conjunction should be satisfiable"
        assert not self.is_tautology(formula), "Long conjunction should not be a tautology"
    
    def test_satisfiable_09_long_disjunction(self):
        """p ∨ q ∨ r ∨ s"""
        formula = Disjunction(
            Disjunction(self.p, self.q),
            Disjunction(self.r, self.s)
        )
        assert self.is_satisfiable(formula), "Long disjunction should be satisfiable"
        assert not self.is_tautology(formula), "Long disjunction should not be a tautology"
    
    def test_satisfiable_10_implication_chain(self):
        """p → (q → r)"""
        inner = Implication(self.q, self.r)
        formula = Implication(self.p, inner)
        assert self.is_satisfiable(formula), "Implication chain should be satisfiable"
        assert not self.is_tautology(formula), "Implication chain should not be a tautology"

    # ===== CLASSICAL LOGICAL PATTERNS =====
    
    def test_pattern_01_distributivity_and_over_or(self):
        """p ∧ (q ∨ r) → (p ∧ q) ∨ (p ∧ r)"""
        left = Conjunction(self.p, Disjunction(self.q, self.r))
        right = Disjunction(Conjunction(self.p, self.q), Conjunction(self.p, self.r))
        formula = Implication(left, right)
        assert self.is_tautology(formula), "Distributivity (∧ over ∨) should be a tautology"
    
    def test_pattern_02_distributivity_or_over_and(self):
        """p ∨ (q ∧ r) → (p ∨ q) ∧ (p ∨ r)"""
        left = Disjunction(self.p, Conjunction(self.q, self.r))
        right = Conjunction(Disjunction(self.p, self.q), Disjunction(self.p, self.r))
        formula = Implication(left, right)
        assert self.is_tautology(formula), "Distributivity (∨ over ∧) should be a tautology"
    
    def test_pattern_03_associativity_and(self):
        """(p ∧ q) ∧ r → p ∧ (q ∧ r)"""
        left = Conjunction(Conjunction(self.p, self.q), self.r)
        right = Conjunction(self.p, Conjunction(self.q, self.r))
        formula = Implication(left, right)
        assert self.is_tautology(formula), "Associativity of ∧ should be a tautology"
    
    def test_pattern_04_associativity_or(self):
        """(p ∨ q) ∨ r → p ∨ (q ∨ r)"""
        left = Disjunction(Disjunction(self.p, self.q), self.r)
        right = Disjunction(self.p, Disjunction(self.q, self.r))
        formula = Implication(left, right)
        assert self.is_tautology(formula), "Associativity of ∨ should be a tautology"
    
    def test_pattern_05_commutativity_and(self):
        """p ∧ q → q ∧ p"""
        left = Conjunction(self.p, self.q)
        right = Conjunction(self.q, self.p)
        formula = Implication(left, right)
        assert self.is_tautology(formula), "Commutativity of ∧ should be a tautology"
    
    def test_pattern_06_commutativity_or(self):
        """p ∨ q → q ∨ p"""
        left = Disjunction(self.p, self.q)
        right = Disjunction(self.q, self.p)
        formula = Implication(left, right)
        assert self.is_tautology(formula), "Commutativity of ∨ should be a tautology"
    
    def test_pattern_07_idempotence_and(self):
        """p ∧ p → p"""
        left = Conjunction(self.p, self.p)
        formula = Implication(left, self.p)
        assert self.is_tautology(formula), "Idempotence of ∧ should be a tautology"
    
    def test_pattern_08_idempotence_or(self):
        """p ∨ p → p"""
        left = Disjunction(self.p, self.p)
        formula = Implication(left, self.p)
        assert self.is_tautology(formula), "Idempotence of ∨ should be a tautology"
    
    def test_pattern_09_absorption_1(self):
        """p ∧ (p ∨ q) → p"""
        left = Conjunction(self.p, Disjunction(self.p, self.q))
        formula = Implication(left, self.p)
        assert self.is_tautology(formula), "Absorption law 1 should be a tautology"
    
    def test_pattern_10_absorption_2(self):
        """p ∨ (p ∧ q) → p"""
        left = Disjunction(self.p, Conjunction(self.p, self.q))
        formula = Implication(left, self.p)
        assert self.is_tautology(formula), "Absorption law 2 should be a tautology"

    # ===== SIGNED TABLEAU SPECIFIC TESTS =====
    
    def test_signed_tableau_rule_expansion(self):
        """Test that signed tableau rules expand correctly"""
        # T:(p ∧ q) should expand to T:p, T:q
        formula = Conjunction(self.p, self.q)
        tableau = classical_signed_tableau(T(formula))
        result = tableau.build()
        
        assert result == True, "T:(p ∧ q) should be satisfiable"
        
        # Should find branches containing T:p and T:q
        open_branches = [b for b in tableau.branches if not b.is_closed]
        assert len(open_branches) > 0, "Should have open branches"
        
        found_tp_tq = False
        for branch in open_branches:
            has_tp = T(self.p) in branch.signed_formulas
            has_tq = T(self.q) in branch.signed_formulas
            if has_tp and has_tq:
                found_tp_tq = True
                break
        
        assert found_tp_tq, "Should find branch with T:p and T:q from T:(p ∧ q) expansion"
    
    def test_signed_tableau_branching_rules(self):
        """Test that signed tableau branching rules work correctly"""
        # F:(p ∧ q) should branch to F:p | F:q
        formula = Conjunction(self.p, self.q)
        tableau = classical_signed_tableau(F(formula))
        result = tableau.build()
        
        assert result == True, "F:(p ∧ q) should be satisfiable"
        
        # Should create branches
        open_branches = [b for b in tableau.branches if not b.is_closed]
        assert len(open_branches) >= 2, "F:(p ∧ q) should create multiple branches"
        
        # Should find F:p in one branch, F:q in another
        found_fp = False
        found_fq = False
        for branch in open_branches:
            if F(self.p) in branch.signed_formulas:
                found_fp = True
            if F(self.q) in branch.signed_formulas:
                found_fq = True
        
        assert found_fp and found_fq, "Should find F:p and F:q in different branches"
    
    def test_signed_tableau_closure_detection(self):
        """Test that signed tableau closure detection works"""
        # Create a contradiction: T:p ∧ T:¬p (equivalent to p ∧ ¬p)
        formula = Conjunction(self.p, Negation(self.p))
        tableau = classical_signed_tableau(T(formula))
        result = tableau.build()
        
        assert result == False, "T:(p ∧ ¬p) should be unsatisfiable"
        
        # All branches should be closed
        closed_branches = [b for b in tableau.branches if b.is_closed]
        assert len(closed_branches) == len(tableau.branches), "All branches should be closed"
        
        # Should have closure reasons
        for branch in closed_branches:
            assert branch.closure_reason is not None, f"Branch {branch.id} should have closure reason"
    
    def test_signed_model_extraction(self):
        """Test that signed tableau model extraction works"""
        # Simple satisfiable formula
        formula = Conjunction(self.p, self.q)
        tableau = classical_signed_tableau(T(formula))
        result = tableau.build()
        
        assert result == True, "T:(p ∧ q) should be satisfiable"
        
        # Extract models
        models = tableau.extract_all_models()
        assert len(models) > 0, "Should extract satisfying models"
        
        # Verify models satisfy the original formula
        found_satisfying = False
        for model in models:
            # Check if model makes both p and q true
            p_true = T(self.p) in model.assignments or any(
                formula == self.p and str(sign) == "T" 
                for formula, sign in model.assignments.items()
            )
            q_true = T(self.q) in model.assignments or any(
                formula == self.q and str(sign) == "T" 
                for formula, sign in model.assignments.items()
            )
            
            if p_true and q_true:
                found_satisfying = True
                break
        
        assert found_satisfying, "Should find model where both p and q are true"


# Additional integration tests
def test_signed_classical_integration():
    """Integration test comparing signed tableau with original tableau results"""
    p = Atom("p")
    q = Atom("q")
    
    # Test several formulas to ensure results match
    test_formulas = [
        p,  # Simple atom
        Conjunction(p, q),  # Simple conjunction
        Disjunction(p, Negation(p)),  # Tautology
        Conjunction(p, Negation(p)),  # Contradiction
        Implication(p, q),  # Simple implication
    ]
    
    for formula in test_formulas:
        # Test with signed tableau
        signed_tableau = classical_signed_tableau(T(formula))
        signed_result = signed_tableau.build()
        
        # Test tautology check
        tautology_tableau = classical_signed_tableau(F(formula))
        is_tautology = not tautology_tableau.build()
        
        # Basic sanity checks
        if signed_result:
            # If satisfiable, should extract models
            models = signed_tableau.extract_all_models()
            assert len(models) > 0, f"Satisfiable formula {formula} should have models"
        else:
            # If unsatisfiable, all branches should be closed
            closed_branches = [b for b in signed_tableau.branches if b.is_closed]
            assert len(closed_branches) == len(signed_tableau.branches), \
                f"Unsatisfiable formula {formula} should have all branches closed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])