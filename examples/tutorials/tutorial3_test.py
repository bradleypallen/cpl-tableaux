#!/usr/bin/env python3
"""Tutorial 3: Three-Valued Logic (WK3)"""

from tableaux import Atom, Conjunction, Disjunction, Negation, Implication
from tableaux import T, F, T3, U, classical_signed_tableau, three_valued_signed_tableau
from tableaux import TruthValue, t, f, e

def compare_classical_vs_wk3():
    """Compare classical and WK3 logic on key examples."""
    
    p = Atom("p")
    
    print("=== CLASSICAL vs WK3 COMPARISON ===\n")
    
    # Example 1: Contradiction in classical logic
    print("Example 1: p ∧ ¬p (Classical contradiction)")
    contradiction = Conjunction(p, Negation(p))
    
    # Classical logic
    classical_tableau = classical_signed_tableau(T(contradiction))
    classical_result = classical_tableau.build()
    
    # WK3 logic (formula is satisfiable if it can be true OR undefined)
    t3_tableau = three_valued_signed_tableau(T3(contradiction))
    u_tableau = three_valued_signed_tableau(U(contradiction))
    t3_satisfiable = t3_tableau.build()
    u_satisfiable = u_tableau.build()
    wk3_result = t3_satisfiable or u_satisfiable
    
    print(f"Classical satisfiable: {classical_result}")  # False
    print(f"WK3 satisfiable: {wk3_result}")  # True
    
    if wk3_result:
        models = []
        if t3_satisfiable:
            models.extend(t3_tableau.extract_all_models())
        if u_satisfiable:
            models.extend(u_tableau.extract_all_models())
        print(f"WK3 models: {len(models)}")
        for model in models:
            print(f"  Model: {model}")
    print()
    
    # Example 2: Excluded middle
    print("Example 2: p ∨ ¬p (Excluded middle)")
    excluded_middle = Disjunction(p, Negation(p))
    
    classical_tableau = classical_signed_tableau(T(excluded_middle))
    classical_result = classical_tableau.build()
    
    t3_tableau = three_valued_signed_tableau(T3(excluded_middle))
    u_tableau = three_valued_signed_tableau(U(excluded_middle))
    t3_satisfiable = t3_tableau.build()
    u_satisfiable = u_tableau.build()
    wk3_result = t3_satisfiable or u_satisfiable
    
    print(f"Classical satisfiable: {classical_result}")  # True
    print(f"WK3 satisfiable: {wk3_result}")  # True
    
    if wk3_result:
        models = []
        if t3_satisfiable:
            models.extend(t3_tableau.extract_all_models())
        if u_satisfiable:
            models.extend(u_tableau.extract_all_models())
        print(f"WK3 models: {len(models)}")
        for model in models:
            print(f"  Model: {model}")
    print()

def explore_wk3_truth_tables():
    """Demonstrate WK3 truth tables."""
    
    from tableaux import WeakKleeneOperators
    
    print("=== WK3 TRUTH TABLES ===\n")
    
    print("Negation (¬):")
    print("  ¬t = f")
    print("  ¬f = t") 
    print("  ¬e = e  (undefined remains undefined)")
    print()
    
    print("Conjunction (∧) - any operation with 'e' returns 'e':")
    values = [t, f, e]
    for a in values:
        for b in values:
            result = WeakKleeneOperators.conjunction(a, b)
            print(f"  {a} ∧ {b} = {result}")
    print()
    
    print("Key insight: In Weak Kleene logic, undefined values 'contaminate'")
    print("all operations - any operation involving 'e' returns 'e'.")
    print("This is different from Strong Kleene logic.")

def test_wk3_formulas():
    """Test various formulas in WK3."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("\n=== WK3 FORMULA TESTING ===\n")
    
    formulas = [
        ("p → p", Implication(p, p)),
        ("p ∨ ¬p", Disjunction(p, Negation(p))),
        ("(p ∧ q) → p", Implication(Conjunction(p, q), p)),
        ("p → (p ∨ q)", Implication(p, Disjunction(p, q)))
    ]
    
    for name, formula in formulas:
        print(f"Testing: {name}")
        
        # Classical
        classical_tableau = classical_signed_tableau(T(formula))
        classical_result = classical_tableau.build()
        
        # WK3
        t3_tableau = three_valued_signed_tableau(T3(formula))
        u_tableau = three_valued_signed_tableau(U(formula))
        t3_satisfiable = t3_tableau.build()
        u_satisfiable = u_tableau.build()
        wk3_result = t3_satisfiable or u_satisfiable
        
        wk3_model_count = 0
        if wk3_result:
            models = []
            if t3_satisfiable:
                models.extend(t3_tableau.extract_all_models())
            if u_satisfiable:
                models.extend(u_tableau.extract_all_models())
            wk3_model_count = len(models)
        
        print(f"  Classical: {'✓' if classical_result else '✗'}")
        print(f"  WK3: {'✓' if wk3_result else '✗'} ({wk3_model_count} models)")
        print()

if __name__ == "__main__":
    compare_classical_vs_wk3()
    explore_wk3_truth_tables()
    test_wk3_formulas()