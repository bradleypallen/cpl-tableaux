#!/usr/bin/env python3
"""Tutorial 2: Signed Tableaux with Visualization"""

from tableau_core import Atom, Conjunction, Disjunction, Implication, Negation
from tableau_core import T, F, classical_signed_tableau

def visualize_simple_tableau():
    """Show tableau construction step-by-step."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("=== TABLEAU VISUALIZATION EXAMPLE ===\n")
    
    # Create a formula that will require branching
    # F:(p ∨ q) means "p ∨ q is false"
    formula = Disjunction(p, q)
    
    print(f"Testing: F:({formula})")
    print("This means: 'p ∨ q must be false'")
    print("For this to be true, both p and q must be false.\n")
    
    # Create tableau with step tracking enabled
    tableau = classical_signed_tableau(F(formula), track_steps=True)
    result = tableau.build()
    
    print(f"Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}\n")
    
    # Show the step-by-step construction
    tableau.print_construction_steps("F:(p ∨ q) Tableau Construction")

def visualize_branching_tableau():
    """Show a more complex example with multiple branches."""
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    print("\n=== COMPLEX BRANCHING EXAMPLE ===\n")
    
    # T:(p ∨ q) ∧ T:(r ∨ ¬p)
    # This will create multiple branches
    formula1 = Disjunction(p, q)
    formula2 = Disjunction(r, Negation(p))
    
    formulas = [T(formula1), T(formula2)]
    
    print("Testing multiple formulas:")
    for i, f in enumerate(formulas):
        print(f"  {i+1}. {f}")
    print()
    
    tableau = classical_signed_tableau(formulas, track_steps=True)
    result = tableau.build()
    
    print(f"Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}\n")
    
    # Show detailed construction
    tableau.print_construction_steps("Complex Tableau Construction")
    
    # Show final models
    if result:
        models = tableau.extract_all_models()
        print(f"\nFound {len(models)} satisfying models:")
        for i, model in enumerate(models):
            print(f"Model {i+1}: {model.assignments}")

def visualize_contradiction():
    """Show how contradictions are detected."""
    
    p = Atom("p")
    
    print("\n=== CONTRADICTION DETECTION ===\n")
    
    # Create a clear contradiction: T:p and F:p
    formulas = [T(p), F(p)]
    
    print("Testing contradiction: T:p ∧ F:p")
    print("This says 'p is true AND p is false' - impossible!\n")
    
    tableau = classical_signed_tableau(formulas, track_steps=True)
    result = tableau.build()
    
    print(f"Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}\n")
    
    tableau.print_construction_steps("Contradiction Detection")

if __name__ == "__main__":
    visualize_simple_tableau()
    visualize_branching_tableau()
    visualize_contradiction()