#!/usr/bin/env python3
"""Tutorial 2: Understanding Signed Tableaux"""

from tableau_core import *

def explore_signed_formulas():
    """Understand signed formula notation."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("=== SIGNED FORMULA NOTATION ===\n")
    
    # Basic signed formulas
    t_p = T(p)  # "p is true"
    f_p = F(p)  # "p is false"
    
    print(f"T:p = {t_p} (p is true)")
    print(f"F:p = {f_p} (p is false)")
    print()
    
    # Signed complex formulas
    conjunction = Conjunction(p, q)
    t_conj = T(conjunction)  # "(p ∧ q) is true"
    f_conj = F(conjunction)  # "(p ∧ q) is false"
    
    print(f"T:(p ∧ q) = {t_conj}")
    print(f"F:(p ∧ q) = {f_conj}")
    print()
    
    # Test what these mean
    print("Testing T:(p ∧ q) - requires both p and q to be true:")
    engine = classical_signed_tableau(t_conj)
    result = engine.build()
    if result:
        models = engine.extract_all_models()
        print(f"  Model: {models[0]}")
    
    print("\nTesting F:(p ∧ q) - requires at least one of p, q to be false:")
    engine = classical_signed_tableau(f_conj)
    result = engine.build()
    if result:
        models = engine.extract_all_models()
        print(f"  Found {len(models)} models:")
        for model in models:
            print(f"    {model}")

if __name__ == "__main__":
    explore_signed_formulas()