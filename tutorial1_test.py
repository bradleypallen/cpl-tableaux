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
    
    tableau = classical_signed_tableau(T(p))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        print(f"Model: {models[0].assignments}")
    print()
    
    # Example 2: Conjunction - satisfiable if both parts can be true
    print("Example 2: Conjunction")
    conjunction = Conjunction(p, q)
    print(f"Formula: {conjunction}")
    
    tableau = classical_signed_tableau(T(conjunction))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        print(f"Model: {models[0].assignments}")
    print()
    
    # Example 3: Contradiction - never satisfiable
    print("Example 3: Contradiction")
    contradiction = Conjunction(p, Negation(p))
    print(f"Formula: {contradiction}")
    
    tableau = classical_signed_tableau(T(contradiction))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be False
    print()
    
    # Example 4: Tautology - always satisfiable
    print("Example 4: Tautology")
    tautology = Disjunction(p, Negation(p))
    print(f"Formula: {tautology}")
    
    tableau = classical_signed_tableau(T(tautology))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be True
    if result:
        models = tableau.extract_all_models()
        print(f"Number of models: {len(models)}")
    print()

def test_implication_examples():
    """Explore implication satisfiability."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("=== IMPLICATION EXAMPLES ===\n")
    
    # Example 1: Simple implication
    print("Example 1: p → q")
    implication = Implication(p, q)
    
    tableau = classical_signed_tableau(T(implication))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        print(f"Found {len(models)} models:")
        for i, model in enumerate(models):
            print(f"  Model {i+1}: {model.assignments}")
    print()
    
    # Example 2: Modus ponens test
    print("Example 2: Modus ponens - p, p → q, ¬q")
    formulas = [T(p), T(implication), T(Negation(q))]
    
    tableau = classical_signed_tableau(formulas)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be False (contradiction)
    print()

if __name__ == "__main__":
    test_satisfiability_examples()
    test_implication_examples()