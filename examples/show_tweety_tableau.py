#!/usr/bin/env python3
"""
Show the tableau construction for the Tweety syllogism in wKrQ logic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tableaux import LogicSystem, Variable, Constant, Predicate, RestrictedUniversalFormula

def show_tableau_tree(node, prefix="", is_last=True, depth=0):
    """Recursively display the tableau tree structure."""
    if depth > 10:  # Prevent infinite recursion
        print(f"{prefix}... (max depth reached)")
        return
        
    # Print current node
    connector = "└── " if is_last else "├── "
    status = "CLOSED" if node.is_closed else "OPEN"
    print(f"{prefix}{connector}Branch [{status}]")
    
    # Print formulas in this node
    for formula in node.signed_formulas:
        formula_prefix = prefix + ("    " if is_last else "│   ")
        print(f"{formula_prefix}├─ {formula}")
    
    # Print children
    if hasattr(node, 'children') and node.children:
        for i, child in enumerate(node.children):
            child_prefix = prefix + ("    " if is_last else "│   ")
            is_last_child = (i == len(node.children) - 1)
            show_tableau_tree(child, child_prefix, is_last_child, depth + 1)

def show_tweety_tableau():
    """Show the complete tableau construction for the Tweety syllogism."""
    
    print("=== TWEETY SYLLOGISM TABLEAU CONSTRUCTION ===\n")
    
    # Create wKrQ logic system
    wkrq = LogicSystem.wkrq()
    
    # Create the logical structures
    x = Variable("X")
    tweety = Constant("tweety")
    
    bird_x = Predicate("Bird", [x])
    bird_tweety = Predicate("Bird", [tweety])
    flies_x = Predicate("Flies", [x])
    flies_tweety = Predicate("Flies", [tweety])
    
    # The classic syllogism
    print("THE SYLLOGISM:")
    print("  Premise 1: [∀X Bird(X)]Flies(X)  ('All birds can fly')")
    print("  Premise 2: Bird(tweety)           ('Tweety is a bird')")
    print("  ∴ Conclusion: Flies(tweety)       ('Tweety can fly')")
    print("\n" + "="*60)
    
    # Create the formulas
    all_birds_fly = RestrictedUniversalFormula(x, bird_x, flies_x)
    tweety_is_bird = bird_tweety
    
    # Test the complete syllogism: premises → conclusion
    premise1 = wkrq.create_logic_formula(all_birds_fly)
    premise2 = wkrq.create_logic_formula(tweety_is_bird)
    conclusion = wkrq.create_logic_formula(flies_tweety)
    
    # To test entailment, we test if premises ∧ ¬conclusion is unsatisfiable
    print("\nTESTING ENTAILMENT: premises ∧ ¬conclusion should be UNSATISFIABLE")
    print("If unsatisfiable, then the entailment is valid.")
    print("\nFormula being tested:")
    premises_and_negated_conclusion = premise1 & premise2 & (~conclusion)
    print(f"T:({premise1} ∧ {premise2} ∧ ¬{conclusion})")
    print("\n" + "-"*60)
    
    # Build the tableau
    print("\nTABLEAU CONSTRUCTION:")
    result = wkrq.solve(premises_and_negated_conclusion, track_steps=True)
    
    print(f"\nFinal Result: {'UNSATISFIABLE' if not result.satisfiable else 'SATISFIABLE'}")
    if not result.satisfiable:
        print("✓ Since premises ∧ ¬conclusion is UNSATISFIABLE, the entailment is VALID!")
        print("✓ The Tweety syllogism is logically sound!")
    else:
        print("✗ The entailment is not valid (counterexample exists)")
    
    # Show the tableau construction steps
    if hasattr(result, 'steps') and result.steps:
        print(f"\nTABLEAU CONSTRUCTION STEPS ({len(result.steps)} steps):")
        for i, step in enumerate(result.steps):
            print(f"  Step {i+1}: {step.description}")
            if step.rule_name:
                print(f"           Rule: {step.rule_name}")
            if step.new_formulas:
                print(f"           Added: {step.new_formulas}")
    
    # Show the actual tableau tree structure
    if hasattr(result, 'tableau') and result.tableau and hasattr(result.tableau, 'root'):
        print(f"\nTABLEAU TREE STRUCTURE:")
        show_tableau_tree(result.tableau.root)
    
    # Show models (if any)
    print(f"\nMODELS FOUND: {len(result.models)}")
    if result.models:
        for i, model in enumerate(result.models):
            print(f"  Model {i+1}: {model}")
    else:
        print("  No models (formula is unsatisfiable)")
    
    # Show what first-order rules are available
    print(f"\nFIRST-ORDER TABLEAU RULES AVAILABLE:")
    fo_rules = [rule for rule in wkrq._logic.rule_set.rules if "Restricted" in rule.name]
    for rule in fo_rules:
        print(f"  • {rule.name}")
        print(f"    Type: {rule.rule_type.value}")
        print(f"    Premises: {[str(p) for p in rule.premises]}")
        print(f"    Conclusions: {rule.conclusions}")
        print()
    
    print("="*60)
    if not result.satisfiable:
        print("SUCCESS: The tableau proves Tweety can fly given the premises!")
    else:
        print("The tableau construction is working, but may need rule refinement.")

if __name__ == "__main__":
    show_tweety_tableau()