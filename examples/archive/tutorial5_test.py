#!/usr/bin/env python3
"""Tutorial 5: Model Extraction and Analysis"""

from tableaux import Atom, Conjunction, Disjunction, Implication, Negation
from tableaux import T, F, T3, U, classical_signed_tableau, three_valued_signed_tableau

def analyze_classical_models():
    """Extract and analyze classical logic models."""
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    print("=== CLASSICAL MODEL ANALYSIS ===\n")
    
    # Example: CNF formula with multiple models
    # (p ∨ q) ∧ (¬p ∨ r)
    clause1 = Disjunction(p, q)
    clause2 = Disjunction(Negation(p), r)
    formula = Conjunction(clause1, clause2)
    
    print(f"Formula: {formula}")
    print("This is satisfiable when:")
    print("  Case 1: p=False, q=True, r=any")
    print("  Case 2: p=True, q=any, r=True")
    print()
    
    tableau = classical_signed_tableau(T(formula))
    result = tableau.build()
    
    if result:
        models = tableau.extract_all_models()
        print(f"Found {len(models)} models:")
        
        for i, model in enumerate(models):
            print(f"\nModel {i+1}: {model.assignments}")
            
            # Verify model satisfies formula
            satisfies = model.satisfies(formula)
            print(f"  Satisfies formula: {satisfies}")
        print()
    
    # Analyze each clause
    print("Clause analysis:")
    for i, model in enumerate(models):
        print(f"Model {i+1}:")
        
        # Check clause1: p ∨ q
        clause1_result = model.satisfies(clause1)
        print(f"  (p ∨ q): {clause1_result}")
        
        # Check clause2: ¬p ∨ r  
        clause2_result = model.satisfies(clause2)
        print(f"  (¬p ∨ r): {clause2_result}")
        print()

def analyze_wk3_models():
    """Analyze three-valued models."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("=== WK3 MODEL ANALYSIS ===\n")
    
    # Formula that has different behavior in WK3
    # p → q (implication)
    formula = Implication(p, q)
    
    print(f"Formula: {formula}")
    print("In WK3, this can be satisfied in various ways including")
    print("when p or q (or both) are undefined.\n")
    
    # Get WK3 models using tableau approach
    t3_tableau = three_valued_signed_tableau(T3(formula))
    u_tableau = three_valued_signed_tableau(U(formula))
    t3_satisfiable = t3_tableau.build()
    u_satisfiable = u_tableau.build()
    
    models = []
    if t3_satisfiable:
        models.extend(t3_tableau.extract_all_models())
    if u_satisfiable:
        models.extend(u_tableau.extract_all_models())
    
    print(f"Found {len(models)} WK3 models:")
    
    for i, model in enumerate(models):
        print(f"Model {i+1}: {model}")
    print()
    
    # Show which assignments DON'T satisfy
    print("Non-satisfying assignments (formula evaluates to 'f'):")
    from tableaux import t, f, e
    all_assignments = [
        (t, t), (t, f), (t, e),
        (f, t), (f, f), (f, e),
        (e, t), (e, f), (e, e)
    ]
    
    from tableaux import WK3Model
    from tableaux import weakKleeneOperators
    
    for p_val, q_val in all_assignments:
        model = WK3Model({"p": p_val, "q": q_val})
        result = model.satisfies(formula)
        
        if result == f:
            print(f"  p={p_val}, q={q_val} → {result}")

def model_comparison():
    """Compare models across logic systems."""
    
    p = Atom("p")
    
    print("\n=== MODEL COMPARISON ACROSS LOGICS ===\n")
    
    # Test excluded middle: p ∨ ¬p
    formula = Disjunction(p, Negation(p))
    
    print(f"Formula: {formula}")
    print()
    
    # Classical models
    classical_tableau = classical_signed_tableau(T(formula))
    classical_result = classical_tableau.build()
    
    if classical_result:
        classical_models = classical_tableau.extract_all_models()
        print(f"Classical models ({len(classical_models)}):")
        for model in classical_models:
            print(f"  {model}")
    print()
    
    # WK3 models using tableau approach
    t3_tableau = three_valued_signed_tableau(T3(formula))
    u_tableau = three_valued_signed_tableau(U(formula))
    t3_satisfiable = t3_tableau.build()
    u_satisfiable = u_tableau.build()
    
    wk3_model_list = []
    if t3_satisfiable:
        wk3_model_list.extend(t3_tableau.extract_all_models())
    if u_satisfiable:
        wk3_model_list.extend(u_tableau.extract_all_models())
    
    print(f"WK3 models ({len(wk3_model_list)}):")
    for model in wk3_model_list:
        print(f"  {model}")
    print()
    
    print("Key difference: WK3 has an additional model where p=e (undefined)")
    print("and the formula still evaluates to e (which is considered satisfying).")

if __name__ == "__main__":
    analyze_classical_models()
    analyze_wk3_models()
    model_comparison()