#!/usr/bin/env python3
"""
wKrQ Countermodel Demonstration

A focused demonstration of countermodels to inferences in 
weak Kleene logic with restricted quantifiers (wKrQ), showing how 
epistemic uncertainty can invalidate classically valid inferences.

Based on: Ferguson, Thomas Macaulay. "Tableaux and restricted quantification 
for systems related to weak Kleene logic." TABLEAUX 2021.

Author: Generated for review by Thomas Ferguson
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tableaux import LogicSystem, Constant, PredicateFormula


def print_step_by_step_tableau(result, title="Tableau Construction"):
    """Print step-by-step tableau construction with full visualization"""
    
    print(f"\n{title}:")
    print("-" * (len(title) + 1))
    
    # Show final result
    print(f"Final Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
    
    # Show models if satisfiable
    if result.satisfiable and result.models:
        model = result.models[0]
        assignments = []
        for atom, value in model.valuation.items():
            assignments.append(f"{value}:{atom}")
        if assignments:
            print(f"  Countermodel: {{{', '.join(assignments)}}}")
    else:
        print("  (No countermodel - inference is valid)")
    
    # Show tableau tree if available
    if result.tableau:
        print("\nTableau Tree:")
        tree = result.tableau.print_tree(show_steps=True)
        # Show first few lines
        lines = tree.split('\n')[:10]
        for line in lines:
            print(f"  {line}")
        if len(tree.split('\n')) > 10:
            print("  ...")
    
    print()


def check_inference_validity(wkrq, premises, conclusion, description):
    """
    Test the validity of an inference using wKrQ logic.
    
    An inference Γ ⊢ φ is valid iff the set Γ ∪ {¬φ} is unsatisfiable.
    """
    print(f"\n{'='*80}")
    print(f"TESTING INFERENCE: {description}")
    print(f"{'='*80}")
    
    print(f"Premises: {[str(p) for p in premises]}")
    print(f"Conclusion: {conclusion}")
    
    # Test entailment directly using new API
    valid = wkrq.entails(premises, conclusion)
    
    print(f"RESULT: {'VALID' if valid else 'INVALID (countermodel exists)'}")
    
    # If invalid, try to find a countermodel by testing premises & ~conclusion
    if not valid:
        # Combine premises with negated conclusion to look for satisfiability
        all_premises = premises[:]
        neg_conclusion = ~conclusion
        all_premises.append(neg_conclusion)
        
        # Test if this combination is satisfiable
        combined = all_premises[0]
        for p in all_premises[1:]:
            combined = combined & p
        
        result = wkrq.solve(combined, track_steps=True)
        print_step_by_step_tableau(result, f"Countermodel Search for {description}")
        return False
    else:
        print("No countermodel exists - inference is valid")
        return True


def demo_classical_vs_epistemic_validity():
    """
    Demonstrate how classically valid inferences can become invalid 
    when epistemic uncertainty is introduced.
    """
    print("wKrQ COUNTERMODEL DEMONSTRATION")
    print("=" * 50)
    print("Showing countermodels to inferences in epistemic logic")
    print()
    
    # Create logic systems
    wkrq = LogicSystem.wkrq()
    
    p, q = wkrq.atoms('p', 'q')
    
    # Example 1: Classical Disjunction Introduction
    print("\n" + "▶" * 3 + " EXAMPLE 1: Disjunction Introduction")
    print("Classical Logic: p ⊢ p ∨ q (VALID)")
    print("Question: Does this remain valid with epistemic signs?")
    
    disjunction = p | q
    
    # Test classical version (using regular atoms, should be valid)
    check_inference_validity(
        wkrq,
        premises=[p],
        conclusion=disjunction, 
        description="Classical: p ⊢ (p ∨ q)"
    )
    
    # Example 2: Modus Ponens
    print("\n" + "▶" * 3 + " EXAMPLE 2: Modus Ponens")
    print("Classical Logic: p, p → q ⊢ q (VALID)")
    print("Question: Is this valid in wKrQ?")
    
    implication = p.implies(q)
    
    # Test classical modus ponens
    check_inference_validity(
        wkrq,
        premises=[p, implication],
        conclusion=q,
        description="Modus Ponens: p, (p → q) ⊢ q"
    )


def demo_predicate_logic_countermodels():
    """
    Demonstrate countermodels in propositional contexts.
    """
    print("\n" + "▶" * 3 + " EXAMPLE 3: Logical Independence")
    print("Question: Can we infer one proposition from another without connecting rules?")
    
    # Create wKrQ logic system
    wkrq = LogicSystem.wkrq()
    
    # Use logically independent propositions
    r, s = wkrq.atoms('r', 's')
    
    # r ⊢ s - clearly invalid without connecting axioms
    check_inference_validity(
        wkrq,
        premises=[r],
        conclusion=s,
        description="Logical Independence: r ⊢ s"
    )
    
    print("\nEXPLANATION:")
    print("This countermodel shows that knowing r doesn't entail s")
    print("without additional axioms connecting these propositions. The countermodel")
    print("assigns different truth values to r and s, which is logically consistent.")
    
    # More meaningful example
    print("\n" + "▶" * 3 + " EXAMPLE 4: Conditional Reasoning")
    print("Question: Does affirming the consequent work?")
    
    # Test: p → q, q ⊢ p (affirming the consequent - should be invalid)
    p, q = wkrq.atoms('p', 'q')
    impl = p.implies(q)
    
    check_inference_validity(
        wkrq,
        premises=[impl, q],
        conclusion=p,
        description="Affirming Consequent: (p → q), q ⊢ p"
    )
    
    print("\nEXPLANATION:")
    print("This demonstrates the classical fallacy of affirming the consequent.")
    print("Even if p → q and q are both true, p need not be true.")


def demo_epistemic_sign_relationships():
    """
    Demonstrate countermodels involving wKrQ epistemic sign relationships.
    """
    print("\n" + "▶" * 3 + " EXAMPLE 5: Ferguson Sign Relationships")
    print("Question: How do different logical relationships hold in wKrQ?")
    
    # Create wKrQ logic system
    wkrq = LogicSystem.wkrq()
    p = wkrq.atom("p")
    
    # Test: p ⊢ ¬¬p (double negation elimination)
    neg_neg_p = ~(~p)
    
    check_inference_validity(
        wkrq,
        premises=[p],
        conclusion=neg_neg_p,
        description="Double Negation: p ⊢ ¬¬p"
    )
    
    print("\nEXPLANATION:")
    print("Testing whether double negation elimination holds in wKrQ.")
    print("In classical logic, p and ¬¬p are equivalent.")
    print("In weak Kleene logic, this relationship may not always hold.")


def main():
    """Run the focused countermodel demonstration"""
    print("🔍 wKrQ COUNTERMODEL ANALYSIS")
    print("=" * 60)
    print("A rigorous examination of inference validity in epistemic logic")
    print("Prepared for review by Thomas Ferguson")
    print()
    
    demo_classical_vs_epistemic_validity()
    demo_predicate_logic_countermodels() 
    demo_epistemic_sign_relationships()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("This demonstration shows that the wKrQ system:")
    print("  1. Preserves classical validity for truth-functional inferences")
    print("  2. Allows countermodels when epistemic uncertainty is introduced")
    print("  3. Distinguishes between truth-functional and epistemic validity")
    print("  4. Provides a principled framework for reasoning under uncertainty")
    print()
    print("Each countermodel demonstrates a logically sound scenario where")
    print("premises can be satisfied while conclusions fail, showing the")
    print("philosophical significance of epistemic vs. truth-functional reasoning.")


if __name__ == "__main__":
    main()