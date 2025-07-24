#!/usr/bin/env python3
"""
Comprehensive Test Suite for Semantic Tableau Implementation

Tests 30+ logical formulas across different categories:
- Tautologies (always true)
- Contradictions (always false) 
- Satisfiable formulas (sometimes true)
- Classical logical patterns
"""

import pytest
from tableau_core import Atom, Negation, Conjunction, Disjunction, Implication, T, classical_signed_tableau


class TestTableau:
    """Test suite for semantic tableau with comprehensive logical formulas"""
    
    def setup_method(self):
        """Set up common atoms for tests"""
        self.p = Atom("p")
        self.q = Atom("q")
        self.r = Atom("r")
        self.s = Atom("s")
    
    def is_satisfiable(self, formula):
        """Helper to test if a formula is satisfiable"""
        tableau = classical_signed_tableau(T(formula))
        return tableau.build()
    
    def is_unsatisfiable(self, formula):
        """Helper to test if a formula is unsatisfiable"""
        return not self.is_satisfiable(formula)
    
    def is_formula_set_satisfiable(self, formulas):
        """Helper to test if a set of formulas is satisfiable"""
        if not formulas:
            return True  # Empty set is satisfiable
        if len(formulas) == 1:
            return self.is_satisfiable(formulas[0])
        # Combine multiple formulas with conjunction
        combined = formulas[0]
        for formula in formulas[1:]:
            combined = Conjunction(combined, formula)
        return self.is_satisfiable(combined)
    
    def is_tautology(self, formula):
        """Helper to test if a formula is a tautology (¬formula is unsatisfiable)"""
        neg_formula = Negation(formula)
        return self.is_unsatisfiable(neg_formula)

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
    
    def test_contradiction_03_modus_ponens(self):
        """(p → q) ∧ p ∧ ¬q"""
        impl = Implication(self.p, self.q)
        formula = Conjunction(Conjunction(impl, self.p), Negation(self.q))
        assert self.is_unsatisfiable(formula), "Modus ponens contradiction should be unsatisfiable"
    
    def test_contradiction_04_transitivity_chain(self):
        """a ∧ ¬c ∧ (a → b) ∧ (b → c)"""
        a, b, c = Atom("a"), Atom("b"), Atom("c")
        formula = Conjunction(
            Conjunction(
                Conjunction(a, Negation(c)),
                Implication(a, b)
            ),
            Implication(b, c)
        )
        assert self.is_unsatisfiable(formula), "Transitivity chain contradiction should be unsatisfiable"
    
    def test_contradiction_05_disjunction_both_false(self):
        """(p ∨ q) ∧ ¬p ∧ ¬q"""
        disj = Disjunction(self.p, self.q)
        formula = Conjunction(Conjunction(disj, Negation(self.p)), Negation(self.q))
        assert self.is_unsatisfiable(formula), "Disjunction with both disjuncts false should be unsatisfiable"

    # ===== TAUTOLOGIES (should be SATISFIABLE, negation UNSATISFIABLE) =====
    
    def test_tautology_01_excluded_middle(self):
        """p ∨ ¬p"""
        formula = Disjunction(self.p, Negation(self.p))
        assert self.is_tautology(formula), "Law of excluded middle should be a tautology"
    
    def test_tautology_02_material_implication(self):
        """(p → q) ↔ (¬p ∨ q)"""
        left = Implication(self.p, self.q)
        right = Disjunction(Negation(self.p), self.q)
        # Test both directions as separate implications
        formula1 = Implication(left, right)
        formula2 = Implication(right, left)
        assert self.is_tautology(formula1), "Material implication equivalence (→) should be tautology"
        assert self.is_tautology(formula2), "Material implication equivalence (←) should be tautology"
    
    def test_tautology_03_transitivity(self):
        """((p → q) ∧ (q → r)) → (p → r)"""
        impl1 = Implication(self.p, self.q)
        impl2 = Implication(self.q, self.r)
        premise = Conjunction(impl1, impl2)
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
    
    def test_satisfiable_05_mixed_connectives(self):
        """(p ∧ q) ∨ (r → s)"""
        left = Conjunction(self.p, self.q)
        right = Implication(self.r, self.s)
        formula = Disjunction(left, right)
        assert self.is_satisfiable(formula), "Mixed connectives should be satisfiable"
    
    def test_satisfiable_06_complex_nesting(self):
        """((p → q) → r) → s"""
        inner = Implication(self.p, self.q)
        middle = Implication(inner, self.r)
        formula = Implication(middle, self.s)
        assert self.is_satisfiable(formula), "Complex nesting should be satisfiable"

    # ===== SPECIFIC LOGICAL PATTERNS =====
    
    def test_pattern_01_disjunctive_syllogism_valid(self):
        """((p ∨ q) ∧ ¬p) → q"""
        premise1 = Disjunction(self.p, self.q)
        premise2 = Negation(self.p)
        premises = Conjunction(premise1, premise2)
        formula = Implication(premises, self.q)
        assert self.is_tautology(formula), "Disjunctive syllogism should be a tautology"
    
    def test_pattern_02_modus_tollens_valid(self):
        """((p → q) ∧ ¬q) → ¬p"""
        premise1 = Implication(self.p, self.q)
        premise2 = Negation(self.q)
        premises = Conjunction(premise1, premise2)
        conclusion = Negation(self.p)
        formula = Implication(premises, conclusion)
        assert self.is_tautology(formula), "Modus tollens should be a tautology"
    
    def test_pattern_03_hypothetical_syllogism(self):
        """((p → q) ∧ (q → r)) → (p → r)"""
        # Same as transitivity test but worth having explicitly
        premise1 = Implication(self.p, self.q)
        premise2 = Implication(self.q, self.r)
        premises = Conjunction(premise1, premise2)
        conclusion = Implication(self.p, self.r)
        formula = Implication(premises, conclusion)
        assert self.is_tautology(formula), "Hypothetical syllogism should be a tautology"
    
    def test_pattern_04_constructive_dilemma(self):
        """((p → q) ∧ (r → s) ∧ (p ∨ r)) → (q ∨ s)"""
        impl1 = Implication(self.p, self.q)
        impl2 = Implication(self.r, self.s)
        disj1 = Disjunction(self.p, self.r)
        premises = Conjunction(Conjunction(impl1, impl2), disj1)
        conclusion = Disjunction(self.q, self.s)
        formula = Implication(premises, conclusion)
        assert self.is_tautology(formula), "Constructive dilemma should be a tautology"

    # ===== EQUIVALENCE TESTS =====
    
    def test_equivalence_01_commutative_and(self):
        """(p ∧ q) and (q ∧ p) should have same satisfiability"""
        formula1 = Conjunction(self.p, self.q)
        formula2 = Conjunction(self.q, self.p)
        result1 = self.is_satisfiable(formula1)
        result2 = self.is_satisfiable(formula2)
        assert result1 == result2, "Conjunction should be commutative"
    
    def test_equivalence_02_commutative_or(self):
        """(p ∨ q) and (q ∨ p) should have same satisfiability"""
        formula1 = Disjunction(self.p, self.q)
        formula2 = Disjunction(self.q, self.p)
        result1 = self.is_satisfiable(formula1)
        result2 = self.is_satisfiable(formula2)
        assert result1 == result2, "Disjunction should be commutative"
    
    def test_equivalence_03_associative_and(self):
        """((p ∧ q) ∧ r) and (p ∧ (q ∧ r)) should have same satisfiability"""
        formula1 = Conjunction(Conjunction(self.p, self.q), self.r)
        formula2 = Conjunction(self.p, Conjunction(self.q, self.r))
        result1 = self.is_satisfiable(formula1)
        result2 = self.is_satisfiable(formula2)
        assert result1 == result2, "Conjunction should be associative"

    # ===== EDGE CASES AND COMPLEX FORMULAS =====
    
    def test_edge_case_01_nested_negations(self):
        """¬¬¬p"""
        formula = Negation(Negation(Negation(self.p)))
        # Should be equivalent to ¬p, so satisfiable but not tautology
        assert self.is_satisfiable(formula), "Triple negation should be satisfiable"
        assert not self.is_tautology(formula), "Triple negation should not be tautology"
    
    def test_edge_case_02_deep_implication_chain(self):
        """p → (q → (r → s))"""
        inner = Implication(self.r, self.s)
        middle = Implication(self.q, inner)
        formula = Implication(self.p, middle)
        assert self.is_satisfiable(formula), "Deep implication chain should be satisfiable"
    
    def test_edge_case_03_large_disjunction(self):
        """p ∨ q ∨ r ∨ s"""
        disj1 = Disjunction(self.p, self.q)
        disj2 = Disjunction(self.r, self.s)
        formula = Disjunction(disj1, disj2)
        assert self.is_satisfiable(formula), "Large disjunction should be satisfiable"
    
    def test_edge_case_04_large_conjunction(self):
        """p ∧ q ∧ r ∧ s"""
        conj1 = Conjunction(self.p, self.q)
        conj2 = Conjunction(self.r, self.s)
        formula = Conjunction(conj1, conj2)
        assert self.is_satisfiable(formula), "Large conjunction should be satisfiable"

    # ===== FAMOUS LOGICAL FORMULAS =====
    
    def test_famous_01_pierce_law(self):
        """((p → q) → p) → p"""
        inner = Implication(self.p, self.q)
        middle = Implication(inner, self.p)
        formula = Implication(middle, self.p)
        assert self.is_tautology(formula), "Peirce's law should be a tautology"
    
    def test_famous_02_weak_peirce_law(self):
        """((p → p) → p) → p"""
        inner = Implication(self.p, self.p)
        middle = Implication(inner, self.p)
        formula = Implication(middle, self.p)
        assert self.is_tautology(formula), "Weak Peirce law should be a tautology"

    # ===== MULTIPLE FORMULA TESTS =====
    
    def test_multiple_01_simple_consistent_set(self):
        """[p, q] should be satisfiable"""
        formulas = [self.p, self.q]
        result = self.is_formula_set_satisfiable(formulas)
        assert result, "Consistent formula set should be satisfiable"
    
    def test_multiple_02_simple_inconsistent_set(self):
        """[p, ¬p] should be unsatisfiable"""
        formulas = [self.p, Negation(self.p)]
        result = self.is_formula_set_satisfiable(formulas)
        assert not result, "Inconsistent formula set should be unsatisfiable"
    
    def test_multiple_03_modus_ponens_set(self):
        """[p → q, p, ¬q] should be unsatisfiable"""
        impl = Implication(self.p, self.q)
        formulas = [impl, self.p, Negation(self.q)]
        result = self.is_formula_set_satisfiable(formulas)
        assert not result, "Modus ponens contradiction set should be unsatisfiable"
    
    def test_multiple_04_satisfiable_complex_set(self):
        """[p ∨ q, r → s, ¬p] should be satisfiable"""
        disj = Disjunction(self.p, self.q)
        impl = Implication(self.r, self.s)
        neg_p = Negation(self.p)
        formulas = [disj, impl, neg_p]
        result = self.is_formula_set_satisfiable(formulas)
        assert result, "Complex satisfiable set should be satisfiable"
    
    def test_multiple_05_transitivity_chain_inconsistent(self):
        """[a, ¬c, a → b, b → c] should be unsatisfiable"""
        a, b, c = Atom("a"), Atom("b"), Atom("c")
        formulas = [
            a,
            Negation(c),
            Implication(a, b),
            Implication(b, c)
        ]
        result = self.is_formula_set_satisfiable(formulas)
        assert not result, "Transitivity chain contradiction should be unsatisfiable"
    
    def test_multiple_06_disjunctive_syllogism_valid_set(self):
        """[p ∨ q, ¬p, ¬q] should be unsatisfiable"""
        disj = Disjunction(self.p, self.q)
        formulas = [disj, Negation(self.p), Negation(self.q)]
        result = self.is_formula_set_satisfiable(formulas)
        assert not result, "Disjunctive syllogism contradiction should be unsatisfiable"
    
    def test_multiple_07_large_consistent_set(self):
        """[p, q, r, s, p → q, q → r, r → s] should be satisfiable"""
        impl1 = Implication(self.p, self.q)
        impl2 = Implication(self.q, self.r)
        impl3 = Implication(self.r, self.s)
        formulas = [self.p, self.q, self.r, self.s, impl1, impl2, impl3]
        result = self.is_formula_set_satisfiable(formulas)
        assert result, "Large consistent set should be satisfiable"
    
    def test_multiple_08_mixed_operators_set(self):
        """[p ∧ q, (p ∧ q) → r, ¬r] should be unsatisfiable"""
        conj = Conjunction(self.p, self.q)
        impl = Implication(conj, self.r)
        formulas = [conj, impl, Negation(self.r)]
        result = self.is_formula_set_satisfiable(formulas)
        assert not result, "Mixed operators contradiction should be unsatisfiable"
    
    def test_multiple_09_empty_list(self):
        """Empty formula list should be satisfiable (trivially)"""
        result = self.is_formula_set_satisfiable([])
        assert result, "Empty formula set should be satisfiable"
    
    def test_multiple_10_single_formula_list(self):
        """Single formula in list should work same as direct formula"""
        # Test with list containing one formula
        result1 = self.is_formula_set_satisfiable([self.p])
        
        # Test with formula directly
        result2 = self.is_satisfiable(self.p)
        
        assert result1 == result2, "Single formula in list should behave same as direct formula"


# ===== PARAMETRIZED TESTS FOR EFFICIENCY =====

@pytest.mark.parametrize("formula_desc,formula_func,expected", [
    # Basic contradictions
    ("p ∧ ¬p", lambda p, q, r, s: Conjunction(p, Negation(p)), False),
    ("q ∧ ¬q", lambda p, q, r, s: Conjunction(q, Negation(q)), False),
    
    # Basic tautologies  
    ("p ∨ ¬p", lambda p, q, r, s: Disjunction(p, Negation(p)), True),
    ("q ∨ ¬q", lambda p, q, r, s: Disjunction(q, Negation(q)), True),
    
    # Basic satisfiable formulas
    ("p", lambda p, q, r, s: p, True),
    ("p ∧ q", lambda p, q, r, s: Conjunction(p, q), True),
    ("p ∨ q", lambda p, q, r, s: Disjunction(p, q), True),
    ("p → q", lambda p, q, r, s: Implication(p, q), True),
])
def test_parametrized_formulas(formula_desc, formula_func, expected):
    """Parametrized test for multiple formulas"""
    p, q, r, s = Atom("p"), Atom("q"), Atom("r"), Atom("s")
    formula = formula_func(p, q, r, s)
    tableau = classical_signed_tableau(T(formula))
    result = tableau.build()
    assert result == expected, f"Formula '{formula_desc}' should be {'SATISFIABLE' if expected else 'UNSATISFIABLE'}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])