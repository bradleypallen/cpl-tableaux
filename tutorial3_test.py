#!/usr/bin/env python3
"""Tutorial 3: Three-Valued Logic Exploration"""

from tableau_core import *

def explore_three_valued_truth_tables():
    """Demonstrate three-valued logic truth tables."""
    
    print("=== THREE-VALUED LOGIC TRUTH TABLES ===\n")
    
    # Truth values: t (true), f (false), e (undefined)
    print("Truth values:")
    print("  t = true")
    print("  f = false")
    print("  e = undefined/error")
    print()
    
    # Negation truth table
    print("Negation (¬):")
    print("  ¬t = f")
    print("  ¬f = t") 
    print("  ¬e = e  ← Undefined stays undefined")
    print()
    
    # Conjunction truth table
    print("Conjunction (∧):")
    print("     | t | f | e")
    print("  ---|---|---|---")
    print("   t | t | f | e")
    print("   f | f | f | f  ← False 'absorbs'")
    print("   e | e | f | e")
    print()
    
    # Disjunction truth table
    print("Disjunction (∨):")
    print("     | t | f | e")
    print("  ---|---|---|---")
    print("   t | t | t | t  ← True 'absorbs'")
    print("   f | t | f | e")
    print("   e | t | e | e")
    print()

def compare_classical_vs_wk3():
    """Compare classical and WK3 logic on key examples."""
    
    p = Atom("p")
    
    print("=== CLASSICAL vs WK3 COMPARISON ===\n")
    
    test_cases = [
        ("p ∧ ¬p", Conjunction(p, Negation(p)), "Classical contradiction"),
        ("p ∨ ¬p", Disjunction(p, Negation(p)), "Law of excluded middle"),
        ("p → p", Implication(p, p), "Self-implication"),
    ]
    
    for description, formula, name in test_cases:
        print(f"{name}: {description}")
        
        # Classical logic
        classical_engine = classical_signed_tableau(T(formula))
        classical_sat = classical_engine.build()
        
        # Three-valued logic using tableau approach
        t3_tableau = three_valued_signed_tableau(T3(formula))
        u_tableau = three_valued_signed_tableau(U(formula))
        wk3_sat = t3_tableau.build() or u_tableau.build()
        
        print(f"  Classical: {'Satisfiable' if classical_sat else 'Unsatisfiable'}")
        print(f"  WK3: {'Satisfiable' if wk3_sat else 'Unsatisfiable'}")
        
        if wk3_sat and not classical_sat:
            print("  *** WK3 allows satisfaction through undefined values ***")
        
        print()

if __name__ == "__main__":
    explore_three_valued_truth_tables()
    compare_classical_vs_wk3()