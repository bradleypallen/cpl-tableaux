#!/usr/bin/env python3
"""Tutorial 1: Basic Satisfiability Testing"""

from tableau_core import Atom, Conjunction, Disjunction, Negation, Implication
from tableau_core import T, F, classical_signed_tableau

def test_satisfiability_examples():
    """Explore basic satisfiability concepts."""
    
    # Create some atoms
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    print("=== SATISFIABILITY EXAMPLES ===\n")
    
    # Example 1: Simple atom - always satisfiable
    print("Example 1: Simple atom")
    print(f"Formula: {p}")
    
    engine = classical_signed_tableau(T(p))
    result = engine.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = engine.extract_all_models()
        print(f"Model: {models[0]}")
    print()
    
    # Example 2: Conjunction - satisfiable if both parts can be true
    print("Example 2: Conjunction")
    conjunction = Conjunction(p, q)
    print(f"Formula: {conjunction}")
    
    engine = classical_signed_tableau(T(conjunction))
    result = engine.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = engine.extract_all_models()
        print(f"Model: {models[0]}")
    print()
    
    # Example 3: Contradiction - never satisfiable
    print("Example 3: Contradiction")
    contradiction = Conjunction(p, Negation(p))
    print(f"Formula: {contradiction}")
    
    engine = classical_signed_tableau(T(contradiction))
    result = engine.build()
    
    print(f"Satisfiable: {result}")
    if not result:
        print("No models exist (unsatisfiable)")
    print()
    
    # Example 4: Disjunction - satisfiable if at least one part can be true
    print("Example 4: Disjunction")
    disjunction = Disjunction(p, q)
    print(f"Formula: {disjunction}")
    
    engine = classical_signed_tableau(T(disjunction))
    result = engine.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = engine.extract_all_models()
        print(f"Found {len(models)} models:")
        for i, model in enumerate(models):
            print(f"  Model {i+1}: {model}")
    print()

if __name__ == "__main__":
    test_satisfiability_examples()