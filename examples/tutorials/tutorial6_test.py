#!/usr/bin/env python3
"""Tutorial 6: First-Order Logic"""

from tableaux import Predicate, Constant, Variable, Implication, Negation
from tableaux import T, F, classical_signed_tableau

def first_order_basics():
    """Basic first-order logic concepts."""
    
    print("=== FIRST-ORDER LOGIC BASICS ===\n")
    
    # Create terms
    tweety = Constant("tweety")
    X = Variable("X")
    
    # Create predicates
    Bird = lambda term: Predicate("Bird", [term])
    Flies = lambda term: Predicate("Flies", [term])
    
    print("Terms:")
    print(f"  Constant: {tweety}")
    print(f"  Variable: {X}")
    print()
    
    print("Predicates:")
    print(f"  Bird(tweety): {Bird(tweety)}")
    print(f"  Flies(tweety): {Flies(tweety)}")
    print()
    
    # Test simple predicate satisfiability
    print("Testing: T:Bird(tweety)")
    tableau = classical_signed_tableau(T(Bird(tweety)))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        print(f"Model: {models[0].assignments}")
    print()

def predicate_logic_reasoning():
    """More complex predicate logic reasoning."""
    
    print("=== PREDICATE LOGIC REASONING ===\n")
    
    # Domain: animals
    tweety = Constant("tweety")
    polly = Constant("polly")
    
    # Predicates
    Bird = lambda x: Predicate("Bird", [x])
    Flies = lambda x: Predicate("Flies", [x])
    Penguin = lambda x: Predicate("Penguin", [x])
    
    print("Domain setup:")
    print("  Constants: tweety, polly")
    print("  Predicates: Bird(x), Flies(x), Penguin(x)")
    print()
    
    # Example 1: Simple implication
    print("Example 1: Bird(tweety) → Flies(tweety)")
    rule1 = Implication(Bird(tweety), Flies(tweety))
    
    tableau = classical_signed_tableau(T(rule1))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        print(f"Found {len(models)} models")
        for model in models:
            print(f"  {model.assignments}")
    print()
    
    # Example 2: Multiple individuals
    print("Example 2: Bird(tweety) ∧ ¬Flies(polly)")
    formulas = [T(Bird(tweety)), T(Negation(Flies(polly)))]
    
    tableau = classical_signed_tableau(formulas)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        for model in models:
            print(f"  {model.assignments}")
    print()

def test_logical_validity():
    """Test logical validity using unsatisfiability."""
    
    print("=== TESTING LOGICAL VALIDITY ===\n")
    
    tweety = Constant("tweety")
    Human = lambda x: Predicate("Human", [x])
    Mortal = lambda x: Predicate("Mortal", [x])
    
    print("Testing validity of: Human(tweety) → Mortal(tweety)")
    print("Method: Try to satisfy the negation")
    print("If negation is unsatisfiable, original is valid\n")
    
    # Create the implication
    implication = Implication(Human(tweety), Mortal(tweety))
    
    # Test satisfiability of negation
    # ¬(Human(tweety) → Mortal(tweety)) ≡ Human(tweety) ∧ ¬Mortal(tweety)
    negation_formulas = [T(Human(tweety)), T(Negation(Mortal(tweety)))]
    
    tableau = classical_signed_tableau(negation_formulas)
    result = tableau.build()
    
    print(f"Negation satisfiable: {result}")
    
    if result:
        print("Original implication is NOT valid (contingent)")
        models = tableau.extract_all_models()
        print("Countermodel where implication fails:")
        for model in models:
            print(f"  {model.assignments}")
    else:
        print("Original implication is VALID (tautology)")
    print()
    
    print("This shows the implication is contingent - it depends on")
    print("the specific interpretation of Human and Mortal predicates.")

if __name__ == "__main__":
    first_order_basics()
    predicate_logic_reasoning()
    test_logical_validity()