#!/usr/bin/env python3
"""
Weak Kleene Logic Demonstration

Shows the differences between classical logic and weak Kleene logic
with practical examples.
"""

from truth_value import TruthValue, t, f, e, WeakKleeneOperators
from wk3_model import WK3Model
from wk3_tableau import WK3Tableau
from formula import Atom, Negation, Conjunction, Disjunction, Implication


def demonstrate_truth_tables():
    """Show WK3 truth tables vs classical logic"""
    print("=" * 60)
    print("WEAK KLEENE LOGIC vs CLASSICAL LOGIC")
    print("=" * 60)
    
    print("\n1. NEGATION")
    print("Classical: ¬t=f, ¬f=t")
    print("WK3:       ¬t=f, ¬f=t, ¬e=e")
    print("Key difference: ¬e = e (undefined stays undefined)")
    
    print("\n2. CONJUNCTION (showing e cases)")
    print("WK3 cases where classical logic doesn't apply:")
    print(f"  t ∧ e = {WeakKleeneOperators.conjunction(t, e)}")
    print(f"  f ∧ e = {WeakKleeneOperators.conjunction(f, e)}")
    print(f"  e ∧ e = {WeakKleeneOperators.conjunction(e, e)}")
    
    print("\n3. DISJUNCTION (showing e cases)")
    print("WK3 cases where classical logic doesn't apply:")
    print(f"  t ∨ e = {WeakKleeneOperators.disjunction(t, e)}")
    print(f"  f ∨ e = {WeakKleeneOperators.disjunction(f, e)}")
    print(f"  e ∨ e = {WeakKleeneOperators.disjunction(e, e)}")
    
    print("\n4. IMPLICATION (showing e cases)")
    print("WK3 cases where classical logic doesn't apply:")
    print(f"  t → e = {WeakKleeneOperators.implication(t, e)}")
    print(f"  e → t = {WeakKleeneOperators.implication(e, t)}")
    print(f"  e → f = {WeakKleeneOperators.implication(e, f)}")
    print(f"  e → e = {WeakKleeneOperators.implication(e, e)}")


def demonstrate_formulas():
    """Show how formulas behave differently in WK3"""
    print("\n" + "=" * 60)
    print("FORMULA EVALUATION EXAMPLES")
    print("=" * 60)
    
    # Create atoms
    p = Atom('p')
    q = Atom('q')
    
    # Create formulas
    excluded_middle = Disjunction(p, Negation(p))  # p ∨ ¬p
    contradiction = Conjunction(p, Negation(p))   # p ∧ ¬p
    implication = Implication(p, q)               # p → q
    
    print("\n1. LAW OF EXCLUDED MIDDLE: p ∨ ¬p")
    print("Classical: Always true (tautology)")
    print("WK3: Depends on the value of p")
    
    model_t = WK3Model({'p': t})
    model_f = WK3Model({'p': f})
    model_e = WK3Model({'p': e})
    
    print(f"  When p=t: p ∨ ¬p = {model_t.satisfies(excluded_middle)}")
    print(f"  When p=f: p ∨ ¬p = {model_f.satisfies(excluded_middle)}")
    print(f"  When p=e: p ∨ ¬p = {model_e.satisfies(excluded_middle)} ← Not a tautology!")
    
    print("\n2. CONTRADICTION: p ∧ ¬p")
    print("Classical: Always false")
    print("WK3: Depends on the value of p")
    
    print(f"  When p=t: p ∧ ¬p = {model_t.satisfies(contradiction)}")
    print(f"  When p=f: p ∧ ¬p = {model_f.satisfies(contradiction)}")
    print(f"  When p=e: p ∧ ¬p = {model_e.satisfies(contradiction)} ← Not always false!")
    
    print("\n3. IMPLICATION: p → q")
    print("Shows how undefined values propagate")
    
    models = [
        WK3Model({'p': t, 'q': t}),
        WK3Model({'p': t, 'q': f}),
        WK3Model({'p': t, 'q': e}),
        WK3Model({'p': e, 'q': t}),
        WK3Model({'p': e, 'q': f}),
        WK3Model({'p': e, 'q': e}),
    ]
    
    for model in models:
        p_val = model.get_value('p')
        q_val = model.get_value('q')
        result = model.satisfies(implication)
        print(f"  When p={p_val}, q={q_val}: p → q = {result}")


def demonstrate_partial_information():
    """Show how WK3 handles partial information"""
    print("\n" + "=" * 60)
    print("PARTIAL INFORMATION HANDLING")
    print("=" * 60)
    
    # Create atoms for a knowledge base
    raining = Atom('raining')
    wet_streets = Atom('wet_streets')
    umbrella_needed = Atom('umbrella_needed')
    
    # Create knowledge base formulas
    if_rain_then_wet = Implication(raining, wet_streets)
    if_wet_then_umbrella = Implication(wet_streets, umbrella_needed)
    
    print("\nKnowledge Base:")
    print("1. If it's raining, then streets are wet")
    print("2. If streets are wet, then umbrella is needed")
    print("\nScenarios:")
    
    # Scenario 1: We know it's raining
    print("\nScenario 1: We know it's raining")
    model1 = WK3Model({'raining': t})
    print(f"  raining = {model1.get_value('raining')}")
    print(f"  wet_streets = {model1.get_value('wet_streets')} (unknown)")
    print(f"  umbrella_needed = {model1.get_value('umbrella_needed')} (unknown)")
    print(f"  raining → wet_streets = {model1.satisfies(if_rain_then_wet)}")
    print(f"  wet_streets → umbrella_needed = {model1.satisfies(if_wet_then_umbrella)}")
    
    # Scenario 2: We know streets are wet, but not why
    print("\nScenario 2: We observe wet streets (cause unknown)")
    model2 = WK3Model({'wet_streets': t})
    print(f"  raining = {model2.get_value('raining')} (unknown)")
    print(f"  wet_streets = {model2.get_value('wet_streets')}")
    print(f"  umbrella_needed = {model2.get_value('umbrella_needed')} (unknown)")
    print(f"  raining → wet_streets = {model2.satisfies(if_rain_then_wet)}")
    print(f"  wet_streets → umbrella_needed = {model2.satisfies(if_wet_then_umbrella)}")
    
    # Scenario 3: Complete uncertainty
    print("\nScenario 3: Complete uncertainty")
    model3 = WK3Model({})  # No information
    print(f"  raining = {model3.get_value('raining')} (unknown)")
    print(f"  wet_streets = {model3.get_value('wet_streets')} (unknown)")
    print(f"  umbrella_needed = {model3.get_value('umbrella_needed')} (unknown)")
    print(f"  raining → wet_streets = {model3.satisfies(if_rain_then_wet)} (unknown)")
    print(f"  wet_streets → umbrella_needed = {model3.satisfies(if_wet_then_umbrella)} (unknown)")


def demonstrate_tableau_differences():
    """Show how WK3 tableaux differ from classical tableaux"""
    print("\n" + "=" * 60)
    print("TABLEAU SYSTEM COMPARISON")
    print("=" * 60)
    
    # Test a formula that behaves differently
    p = Atom('p')
    formula = Disjunction(p, Negation(p))  # p ∨ ¬p
    
    print(f"\nTesting formula: {formula}")
    print("In classical logic: This is a tautology (always true)")
    print("In WK3: This can be undefined when p is undefined")
    
    # Build WK3 tableau
    wk3_tableau = WK3Tableau(formula)
    wk3_result = wk3_tableau.build()
    wk3_models = wk3_tableau.extract_all_models()
    
    print(f"\nWK3 Tableau Result: {'SATISFIABLE' if wk3_result else 'UNSATISFIABLE'}")
    print(f"Number of WK3 models: {len(wk3_models)}")
    
    if wk3_models:
        print("WK3 Models found:")
        for i, model in enumerate(wk3_models, 1):
            p_val = model.get_value('p')
            formula_val = model.satisfies(formula)
            print(f"  Model {i}: p={p_val} → formula={formula_val}")
    
    print(f"\nKey insight: In WK3, when p=e, the formula p ∨ ¬p = e")
    print("This shows WK3 is not a tautology, unlike in classical logic!")


def main():
    """Run all demonstrations"""
    print("WEAK KLEENE LOGIC DEMONSTRATION")
    print("Showing three-valued logic with truth values: t (true), f (false), e (undefined)")
    
    demonstrate_truth_tables()
    demonstrate_formulas()
    demonstrate_partial_information()
    demonstrate_tableau_differences()
    
    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("Weak Kleene Logic provides a formal way to reason with:")
    print("• Incomplete information (e values)")
    print("• Undefined or unknown propositions") 
    print("• Partial knowledge in expert systems")
    print("• Three-valued database logic")
    print("\nUnlike classical logic, WK3 doesn't assume excluded middle")
    print("and allows for genuine uncertainty in logical reasoning.")


if __name__ == "__main__":
    main()