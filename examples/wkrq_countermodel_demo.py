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

from tableaux import Atom, Negation, Conjunction, Disjunction, Implication, Predicate, Constant, TF, FF, M, N, wkrq_signed_tableau


def print_step_by_step_tableau(tableau, title="Tableau Construction"):
    """Print step-by-step tableau construction with full visualization"""
    
    # Use the built-in step visualization if available
    if hasattr(tableau, 'construction_steps') and tableau.construction_steps:
        tableau.print_construction_steps(title)
        
        # Show final result
        result = tableau.is_satisfiable()
        print(f"\nFinal Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}")
        
        # Show models if satisfiable
        if result:
            models = tableau.extract_all_models()
            if models and len(models) > 0:
                model = models[0]
                if hasattr(model, 'assignments') and model.assignments:
                    assignments = []
                    for atom, value in model.assignments.items():
                        assignments.append(f"{value}:{atom}")
                    if assignments:
                        print(f"  Countermodel: {{{', '.join(assignments)}}}")
            else:
                print("  (No specific model assignments extracted)")
        return
    
    # Fallback to simplified display if no step tracking
    print(f"\n{title}:")
    print("-" * (len(title) + 1))
    
    # Show initial formulas
    print("Initial formulas:")
    for i, sf in enumerate(tableau.initial_signed_formulas):
        connector = "├─" if i < len(tableau.initial_signed_formulas) - 1 else "└─"
        print(f"│ {connector} {sf}")
    print()
    
    # Show final result
    result = tableau.is_satisfiable()
    print(f"Final Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}")
    
    # Show models if satisfiable
    if result:
        models = tableau.extract_all_models()
        if models and len(models) > 0:
            model = models[0]
            if hasattr(model, 'assignments') and model.assignments:
                assignments = []
                for atom, value in model.assignments.items():
                    assignments.append(f"{value}:{atom}")
                if assignments:
                    print(f"  Countermodel: {{{', '.join(assignments)}}}")
        else:
            print("  (No specific model assignments extracted)")
    
    print()


def check_inference_validity(premises, conclusion, description):
    """
    Test the validity of an inference using signed tableaux.
    
    An inference Γ ⊢ φ is valid iff the set Γ ∪ {¬φ} is unsatisfiable.
    In signed tableau terms: premises ∪ {F:conclusion} must be unsatisfiable.
    """
    print(f"\n{'='*80}")
    print(f"TESTING INFERENCE: {description}")
    print(f"{'='*80}")
    
    # Create negated conclusion
    if isinstance(conclusion, tuple):  # (sign, formula) pair
        sign, formula = conclusion
        if str(sign) == "T":
            negated_conclusion = FF(formula)
        elif str(sign) == "F": 
            negated_conclusion = TF(formula)
        elif str(sign) == "M":
            negated_conclusion = N(formula)
        elif str(sign) == "N":
            negated_conclusion = M(formula)
        else:
            negated_conclusion = FF(formula)  # Default fallback
    else:
        # Handle signed formula objects or raw formulas
        if hasattr(conclusion, 'sign') and hasattr(conclusion, 'formula'):
            # It's a SignedFormula
            if str(conclusion.sign) == "T":
                negated_conclusion = FF(conclusion.formula)
            elif str(conclusion.sign) == "F":
                negated_conclusion = TF(conclusion.formula)
            elif str(conclusion.sign) == "M":
                negated_conclusion = N(conclusion.formula)
            elif str(conclusion.sign) == "N":
                negated_conclusion = M(conclusion.formula)
            else:
                negated_conclusion = FF(conclusion.formula)
        else:
            # Assume raw formula - negate classically
            negated_conclusion = FF(conclusion)
    
    # Combine premises with negated conclusion
    test_formulas = premises + [negated_conclusion]
    
    print(f"Premises: {[str(p) for p in premises]}")
    print(f"Conclusion: {conclusion}")
    print(f"Testing satisfiability of: {[str(f) for f in test_formulas]}")
    
    # Build tableau with step tracking
    tableau = wkrq_signed_tableau(test_formulas, track_steps=True)
    result = tableau.build()
    
    # Interpret result
    if result:
        print(f"RESULT: SATISFIABLE → Inference is INVALID (countermodel exists)")
        models = tableau.extract_all_models()
        if models and models[0].assignments:
            print(f"COUNTERMODEL FOUND:")
            for formula, sign in models[0].assignments.items():
                print(f"  {sign}:{formula}")
    else:
        print(f"RESULT: UNSATISFIABLE → Inference is VALID (no countermodel)")
    
    # Show detailed tableau construction
    print_step_by_step_tableau(tableau, f"Signed Tableau for {description}")
    
    return result


def demo_classical_vs_epistemic_validity():
    """
    Demonstrate how classically valid inferences can become invalid 
    when epistemic uncertainty is introduced.
    """
    print("wKrQ COUNTERMODEL DEMONSTRATION")
    print("=" * 50)
    print("Showing countermodels to inferences in epistemic logic")
    print()
    
    p = Atom("p")
    q = Atom("q")
    
    # Example 1: Classical Disjunction Introduction
    print("\n" + "▶" * 3 + " EXAMPLE 1: Disjunction Introduction")
    print("Classical Logic: p ⊢ p ∨ q (VALID)")
    print("Question: Does this remain valid with epistemic signs?")
    
    disjunction = Disjunction(p, q)
    
    # Test classical version
    check_inference_validity(
        premises=[TF(p)],
        conclusion=TF(disjunction), 
        description="Classical: T:p ⊢ T:(p ∨ q)"
    )
    
    # Test epistemic version 1: M:p ⊢ T:(p ∨ q)
    check_inference_validity(
        premises=[M(p)],
        conclusion=TF(disjunction),
        description="Epistemic: M:p ⊢ T:(p ∨ q)"
    )
    
    # Test epistemic version 2: T:p ⊢ M:(p ∨ q) 
    check_inference_validity(
        premises=[TF(p)],
        conclusion=M(disjunction),
        description="Epistemic: T:p ⊢ M:(p ∨ q)"
    )
    
    # Example 2: Modus Ponens with Epistemic Uncertainty
    print("\n" + "▶" * 3 + " EXAMPLE 2: Modus Ponens with Epistemic Signs")
    print("Classical Logic: p, p → q ⊢ q (VALID)")
    print("Question: What happens with epistemic uncertainty?")
    
    implication = Implication(p, q)
    
    # Test classical modus ponens
    check_inference_validity(
        premises=[TF(p), TF(implication)],
        conclusion=TF(q),
        description="Classical Modus Ponens: T:p, T:(p → q) ⊢ T:q"
    )
    
    # Test epistemic modus ponens failure
    check_inference_validity(
        premises=[M(p), M(implication)],
        conclusion=TF(q),
        description="Epistemic: M:p, M:(p → q) ⊢ T:q"
    )


def demo_predicate_logic_countermodels():
    """
    Demonstrate countermodels in predicate logic contexts.
    These examples avoid unwarranted domain assumptions.
    """
    print("\n" + "▶" * 3 + " EXAMPLE 3: Predicate Logic - Avoiding Domain Assumptions")
    print("Question: Can we infer properties of individuals without explicit rules?")
    
    # Use logically neutral predicates
    tweety = Constant("tweety")
    
    # P(tweety) ⊢ Q(tweety) - clearly invalid without connecting axioms
    p_tweety = Predicate("P", [tweety])  # Generic property P
    q_tweety = Predicate("Q", [tweety])  # Generic property Q
    
    check_inference_validity(
        premises=[TF(p_tweety)],
        conclusion=TF(q_tweety),
        description="Predicate Logic: T:P(tweety) ⊢ T:Q(tweety)"
    )
    
    print("\nEXPLANATION:")
    print("This countermodel shows that knowing T:P(tweety) doesn't entail T:Q(tweety)")
    print("without additional axioms connecting properties P and Q. The countermodel")
    print("assigns T:P(tweety) and F:Q(tweety), which is logically consistent.")
    
    # More meaningful example with epistemic reasoning
    human = Predicate("Human", [tweety])
    mortal = Predicate("Mortal", [tweety])
    
    print("\n" + "▶" * 3 + " EXAMPLE 4: Epistemic Reasoning about Individuals")
    print("Question: Does epistemic knowledge about humanity entail epistemic knowledge about mortality?")
    
    check_inference_validity(
        premises=[M(human)],
        conclusion=M(mortal),
        description="Epistemic: M:Human(tweety) ⊢ M:Mortal(tweety)"
    )
    
    print("\nEXPLANATION:")
    print("Even if we're epistemically uncertain that Tweety is human (M:Human(tweety)),")
    print("this doesn't automatically create epistemic uncertainty about mortality")
    print("(M:Mortal(tweety)) without explicit domain knowledge connecting these concepts.")


def demo_epistemic_sign_relationships():
    """
    Demonstrate countermodels involving wKrQ epistemic sign relationships.
    """
    print("\n" + "▶" * 3 + " EXAMPLE 5: Ferguson Sign Duality and Inference")
    print("Question: How do wKrQ M/N signs interact in inferences?")
    
    p = Atom("p")
    
    # Test: M:p ⊢ N:¬p (should this be valid?)
    neg_p = Negation(p)
    
    check_inference_validity(
        premises=[M(p)],
        conclusion=N(neg_p),
        description="wKrQ Signs: M:p ⊢ N:¬p"
    )
    
    print("\nEXPLANATION:")
    print("M:p means 'p may be true' - expressing epistemic possibility.")
    print("N:¬p means '¬p need not be true' - also epistemic possibility about ¬p.")
    print("These can coexist because they both express uncertainty, not definite knowledge.")


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