#!/usr/bin/env python3
"""Tutorial 4: Ferguson's wKrQ Epistemic Logic"""

from tableau_core import Atom, Conjunction, Disjunction, Implication, Negation
from tableau_core import TF, FF, M, N, wkrq_signed_tableau, ferguson_signed_tableau

def epistemic_basics():
    """Understand the four epistemic signs."""
    
    p = Atom("p")
    
    print("=== FERGUSON'S wKrQ SIGNS ===\n")
    
    print("T: Definitely true (classical true)")
    print("F: Definitely false (classical false)")
    print("M: May be true (epistemic possibility)")
    print("N: Need not be true (epistemic possibility of falsehood)")
    print()
    
    print("Key insight: M and N represent epistemic uncertainty")
    print("and can coexist without contradiction!\n")
    
    # Test epistemic uncertainty
    print("Example 1: Epistemic uncertainty - M:p ∧ N:p")
    formulas = [M(p), N(p)]
    
    tableau = ferguson_signed_tableau(formulas, track_steps=True)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be True
    print("Explanation: Both express uncertainty about p's truth value\n")
    
    # Show construction
    tableau.print_construction_steps("Epistemic Uncertainty Example")

def epistemic_vs_classical():
    """Compare epistemic and classical contradictions."""
    
    p = Atom("p")
    
    print("\n=== EPISTEMIC vs CLASSICAL CONTRADICTIONS ===\n")
    
    # Classical contradiction: T:p ∧ F:p
    print("Classical contradiction: T:p ∧ F:p")
    formulas = [TF(p), FF(p)]
    
    tableau = ferguson_signed_tableau(formulas, track_steps=True)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be False
    print("Explanation: Definite truth and falsehood contradict\n")
    
    # Mixed epistemic-classical
    print("Mixed case: T:p ∧ M:p")
    formulas = [TF(p), M(p)]
    
    tableau = ferguson_signed_tableau(formulas)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be True
    print("Explanation: Definite truth is consistent with possibility\n")

def epistemic_reasoning_examples():
    """Explore complex epistemic reasoning."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("=== COMPLEX EPISTEMIC REASONING ===\n")
    
    # Example 1: Epistemic disjunction
    print("Example 1: M:(p ∨ q) - 'p or q may be true'")
    disjunction = Disjunction(p, q)
    
    tableau = ferguson_signed_tableau(M(disjunction), track_steps=True)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    print("Shows epistemic uncertainty about disjunction\n")
    
    # Example 2: Mixed definite and epistemic
    print("Example 2: T:p ∧ M:q ∧ N:q")
    print("'p is definitely true, q may be true, q need not be true'")
    
    formulas = [TF(p), M(q), N(q)]
    tableau = ferguson_signed_tableau(formulas)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    print("Definite knowledge coexists with epistemic uncertainty\n")

if __name__ == "__main__":
    epistemic_basics()
    epistemic_vs_classical()
    epistemic_reasoning_examples()