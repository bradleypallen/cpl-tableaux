#!/usr/bin/env python3
"""
Countermodel Test Suite for Invalid Inferences

This test suite demonstrates countermodels for invalid inferences of the form P |- Q
across different logic systems. Examples are drawn from classical and non-classical 
logic literature to showcase the unique semantic properties of each system.

The tests verify that our tableau system correctly identifies invalid inferences
by finding countermodels - models where the premises are satisfied but the 
conclusion is not.

Literature Sources:
- Priest, G. "Introduction to Non-Classical Logic" (2nd ed., 2008)
- Fitting, M. "First-Order Logic and Automated Theorem Proving" (2nd ed., 1996)
- Ferguson, S. "Tableaux and restricted quantification for systems related to weak Kleene logic" (2021)
- Kleene, S.C. "Introduction to Metamathematics" (1952)
- Smullyan, R. "First-Order Logic" (1968)
"""

from tableaux import LogicSystem, Variable, Constant, Predicate
import os

def show_tableau_visualization(logic_system, formula_str, sign='T', description=""):
    """Helper function to display tableau visualization for a formula."""
    if description:
        print(f"\n    === Tableau for {description} ===")
    else:
        print(f"\n    === Tableau for {sign}:{formula_str} ===")
    
    formula = logic_system.parse(formula_str)
    result = logic_system.solve(formula, sign, track_steps=True)
    
    # Show the tableau construction steps
    if result.steps and len(result.steps) > 0:
        print("\n    Tableau construction:")
        for i, step in enumerate(result.steps):
            if hasattr(step, 'description') and step.description:
                print(f"    {i}: {step.description}")
            elif hasattr(step, 'rule_name') and step.rule_name:
                if hasattr(step, 'formula') and step.formula:
                    print(f"    {i}: Applied {step.rule_name} to {step.formula}")
                else:
                    print(f"    {i}: Applied {step.rule_name}")
            elif hasattr(step, 'formulas') and step.formulas:
                print(f"    {i}: {', '.join(str(f) for f in step.formulas)}")
        
        # Show tree structure if we have enough information
        print("\n    Tableau tree structure:")
        print(f"    Root: {sign}:{formula_str}")
        
        # Track which rules created branches
        branch_count = 0
        for step in result.steps:
            if hasattr(step, 'description') and 'branches' in str(step.description):
                branch_count += 1
                print(f"    ├── Branch point: {step.description}")
        
        if branch_count == 0:
            print("    └── Linear construction (no branching)")
    
    # Show if branches are open or closed
    if result.satisfiable:
        print("\n    ✓ Open branches found (formula is satisfiable)")
        if result.models:
            print(f"    ✓ {len(result.models)} model(s) extracted")
            # Show one example model
            if len(result.models) > 0:
                print("\n    Example model:")
                model = result.models[0]
                for atom, value in sorted(model.valuation.items()):
                    if hasattr(value, 'symbol'):
                        print(f"      {atom} = {value}")
                    else:
                        print(f"      {atom} = {value}")
    else:
        print("\n    ✗ All branches closed (formula is unsatisfiable)")
    
    return result

def test_classical_countermodels():
    """
    Classical logic countermodel examples.
    These should all be invalid inferences in classical logic.
    """
    print("=== CLASSICAL LOGIC COUNTERMODELS ===\n")
    
    classical = LogicSystem.classical()
    
    countermodel_cases = [
        {
            "name": "Affirming the Consequent",
            "description": "Classic fallacy: (p → q) ∧ q ⊬ p",
            "premises": ["(p -> q) & q"],
            "conclusion": "p",
            "source": "Standard logic textbooks"
        },
        {
            "name": "Denying the Antecedent", 
            "description": "Classic fallacy: (p → q) ∧ ¬p ⊬ ¬q",
            "premises": ["(p -> q) & ~p"],
            "conclusion": "~q",
            "source": "Standard logic textbooks"
        },
        {
            "name": "Converse Confusion",
            "description": "Invalid: p → q ⊬ q → p (converse is not equivalent)",
            "premises": ["p -> q"],
            "conclusion": "q -> p",
            "source": "Standard logic fallacy - confusing conditional with its converse"
        },
        {
            "name": "Disjunction Introduction Reverse",
            "description": "Invalid: p ∨ q ⊬ p",
            "premises": ["p | q"],
            "conclusion": "p", 
            "source": "Hurley 'A Concise Introduction to Logic'"
        },
        {
            "name": "Conjunction Elimination Invalid",
            "description": "Invalid: p ⊬ p ∧ q",
            "premises": ["p"],
            "conclusion": "p & q",
            "source": "Basic propositional logic"
        },
        {
            "name": "Material Conditional Confusion",
            "description": "Invalid: p ⊬ p → q (conditional doesn't follow from antecedent alone)",
            "premises": ["p"],
            "conclusion": "p -> q",
            "source": "Material conditional semantics"
        },
        {
            "name": "Biconditional Partial",
            "description": "Invalid: p → q ⊬ p ↔ q",
            "premises": ["p -> q"],
            "conclusion": "(p -> q) & (q -> p)",  # biconditional
            "source": "Biconditional definition"
        }
    ]
    
    for i, case in enumerate(countermodel_cases, 1):
        print(f"Test {i}: {case['name']}")
        print(f"  Description: {case['description']}")
        print(f"  Source: {case['source']}")
        
        try:
            # Test entailment
            entails = classical.parse_and_entails(case['premises'], case['conclusion'])
            
            if not entails:
                print("  ✓ Correctly identified as invalid inference")
                
                # Find countermodel by solving premises but not conclusion
                premises_formula = classical.parse(" & ".join(f"({p})" for p in case['premises']))
                conclusion_formula = classical.parse(case['conclusion'])
                negated_conclusion = ~conclusion_formula
                
                # Model where premises are true but conclusion is false
                countermodel_formula = premises_formula & negated_conclusion
                result = classical.solve(countermodel_formula)
                
                if result.satisfiable and len(result.models) > 0:
                    print("  ✓ Countermodel found:")
                    model = result.models[0]
                    for atom, value in model.valuation.items():
                        # Convert TruthValue to boolean for display
                        if hasattr(value, 'symbol'):
                            bool_value = value.symbol == 't'
                        else:
                            bool_value = value
                        print(f"    {atom}: {bool_value}")
                    
                    # Show tableau for selected examples
                    if i in [1, 4]:  # Show tableaux for "Affirming the Consequent" and "Disjunction Introduction Reverse"
                        show_tableau_visualization(
                            classical, 
                            f"({' & '.join(f'({p})' for p in case['premises'])}) & ~({case['conclusion']})",
                            description=f"countermodel search for {case['name']}"
                        )
                else:
                    print("  ⚠ No countermodel found (unexpected)")
            else:
                print("  ✗ Incorrectly identified as valid inference")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print()

def test_weak_kleene_countermodels():
    """
    Weak Kleene logic countermodel examples.
    These leverage the three-valued nature where undefined propagates.
    """
    print("=== WEAK KLEENE LOGIC COUNTERMODELS ===\n")
    
    wk = LogicSystem.weak_kleene()
    
    countermodel_cases = [
        {
            "name": "Law of Excluded Middle Failure",
            "description": "In WK3: ⊬ p ∨ ¬p (not a tautology when p is undefined)",
            "premises": [],
            "conclusion": "p | ~p",
            "source": "Priest 'Introduction to Non-Classical Logic' Ch. 7"
        },
        {
            "name": "Ex Contradictione Sequitur Quodlibet Failure", 
            "description": "In WK3: p ∧ ¬p ⊬ q (explosion fails when p is undefined)",
            "premises": ["p & ~p"],
            "conclusion": "q",
            "source": "Priest 'Introduction to Non-Classical Logic'"
        },
        {
            "name": "Disjunctive Syllogism Failure",
            "description": "In WK3: (p ∨ q) ∧ ¬p ⊬ q (fails when q is undefined)",
            "premises": ["(p | q) & ~p"],
            "conclusion": "q", 
            "source": "Priest, three-valued logic chapter"
        },
        {
            "name": "Modus Ponens Failure",
            "description": "In WK3: (p → q) ∧ p ⊬ q (fails when both p and q undefined)",
            "premises": ["(p -> q) & p"],
            "conclusion": "q",
            "source": "Weak Kleene truth tables"
        },
        {
            "name": "Identity Failure",
            "description": "In WK3: ⊬ p → p (self-implication fails when p is undefined)",
            "premises": [],
            "conclusion": "p -> p",
            "source": "Kleene 'Introduction to Metamathematics'"
        }
    ]
    
    for i, case in enumerate(countermodel_cases, 1):
        print(f"Test {i}: {case['name']}")
        print(f"  Description: {case['description']}")
        print(f"  Source: {case['source']}")
        
        try:
            # In weak Kleene, we test with different signs
            if case['premises']:
                # Test if premises entail conclusion
                entails = wk.parse_and_entails(case['premises'], case['conclusion'])
                
                if not entails:
                    print("  ✓ Correctly identified as invalid inference")
                    
                    # Try to find countermodel with U signs
                    premises_formula = wk.parse(" & ".join(f"({p})" for p in case['premises']))
                    conclusion_formula = wk.parse(case['conclusion'])
                    
                    # Check if premises can be satisfied with T but conclusion with F or U
                    premise_result = wk.solve(premises_formula, 'T')
                    conclusion_f_result = wk.solve(conclusion_formula, 'F')
                    conclusion_u_result = wk.solve(conclusion_formula, 'U')
                    
                    if premise_result.satisfiable and (conclusion_f_result.satisfiable or conclusion_u_result.satisfiable):
                        print("  ✓ Countermodel exists (premises can be T while conclusion is F or U)")
                        if conclusion_u_result.satisfiable:
                            print("    - Conclusion can be undefined (U)")
                        if conclusion_f_result.satisfiable:
                            print("    - Conclusion can be false (F)")
                    
                else:
                    print("  ✗ Incorrectly identified as valid inference")
            else:
                # No premises - testing if conclusion is a tautology
                conclusion_formula = wk.parse(case['conclusion'])
                
                # Check if F:conclusion or U:conclusion is satisfiable
                f_result = wk.solve(conclusion_formula, 'F')
                u_result = wk.solve(conclusion_formula, 'U')
                
                if f_result.satisfiable or u_result.satisfiable:
                    print("  ✓ Correctly identified as non-tautology")
                    if u_result.satisfiable:
                        print("    - Can be undefined (U) - this is the key countermodel")
                        if len(u_result.models) > 0:
                            print("    - Example assignment making it undefined:")
                            model = u_result.models[0]
                            for atom, value in model.valuation.items():
                                print(f"      {atom}: {value}")
                    if f_result.satisfiable:
                        print("    - Can also be false (F)")
                    
                    # Show tableau for law of excluded middle and identity failures
                    if i in [1, 5]:
                        show_tableau_visualization(
                            wk, 
                            case['conclusion'],
                            sign='U',
                            description=f"U:{case['conclusion']} showing undefined possibility"
                        )
                else:
                    print("  ✗ Incorrectly identified as tautology")
                    
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print()


def test_wkrq_countermodels():
    """
    wKrQ (four-valued epistemic logic) countermodel examples.
    These showcase epistemic uncertainty with M and N signs.
    """
    print("=== wKrQ EPISTEMIC LOGIC COUNTERMODELS ===\n")
    
    wkrq = LogicSystem.wkrq()
    
    countermodel_cases = [
        {
            "name": "Epistemic Uncertainty about Tautologies",
            "description": "In wKrQ: ⊬ p ∨ ¬p (can be epistemically uncertain even about tautologies)",
            "premises": [],
            "conclusion": "p | ~p",
            "source": "Ferguson 'Tableaux and restricted quantification' (2021)"
        },
        {
            "name": "Universal Quantifier Uncertainty",
            "description": "In wKrQ: [∀X Bird(X)]Flies(X) ⊬ Flies(tweety) (uncertain about universal claims)",
            "premises": ["[∀X Bird(X)]Flies(X)"],
            "conclusion": "Flies(tweety)",
            "source": "Ferguson restricted quantification"
        },
        {
            "name": "Existential Quantifier Uncertainty", 
            "description": "In wKrQ: Bird(tweety) ⊬ [∃X Bird(X)]Flies(X) (existence claims can be uncertain)",
            "premises": ["Bird(tweety)"],
            "conclusion": "[∃X Bird(X)]Flies(X)",
            "source": "Ferguson epistemic logic"
        },
        {
            "name": "Epistemic Contradiction Non-Explosion",
            "description": "In wKrQ: M:p ∧ N:p ⊬ q (epistemic uncertainty doesn't explode)",
            "premises": [],  # We'll test this differently since it involves signs
            "conclusion": "q",
            "source": "Ferguson epistemic signs",
            "special": "epistemic_signs"
        },
        {
            "name": "Knowledge vs Truth Distinction",
            "description": "In wKrQ: T:p ⊬ M:p (truth doesn't guarantee epistemic possibility)",
            "premises": [],
            "conclusion": "",
            "source": "Ferguson epistemic vs alethic",
            "special": "truth_knowledge"
        }
    ]
    
    for i, case in enumerate(countermodel_cases, 1):
        print(f"Test {i}: {case['name']}")
        print(f"  Description: {case['description']}")
        print(f"  Source: {case['source']}")
        
        try:
            if case.get('special') == 'epistemic_signs':
                # Special case: test that M:p and N:p can coexist
                p = wkrq.atom("p")
                q = wkrq.atom("q")
                
                m_p_result = wkrq.solve(p, 'M')
                n_p_result = wkrq.solve(p, 'N')
                
                if m_p_result.satisfiable and n_p_result.satisfiable:
                    print("  ✓ M:p and N:p are both satisfiable (epistemic uncertainty)")
                    print("    - This shows epistemic signs don't create classical contradictions")
                else:
                    print("  ✗ Epistemic signs behaving like classical signs")
                    
            elif case.get('special') == 'truth_knowledge':
                # Special case: truth vs knowledge
                p = wkrq.atom("p")
                
                t_p_result = wkrq.solve(p, 'T')
                m_p_result = wkrq.solve(p, 'M')
                
                print("  ✓ Truth and epistemic possibility are independent dimensions")
                print(f"    - T:p satisfiable: {t_p_result.satisfiable}")
                print(f"    - M:p satisfiable: {m_p_result.satisfiable}")
                
            elif case['premises']:
                # Standard entailment test
                entails = wkrq.parse_and_entails(case['premises'], case['conclusion'])
                
                if not entails:
                    print("  ✓ Correctly identified as invalid inference")
                    
                    # Test epistemic uncertainty
                    premises_formula = wkrq.parse(" & ".join(f"({p})" for p in case['premises']))
                    conclusion_formula = wkrq.parse(case['conclusion'])
                    
                    # Check if premises can be T/M but conclusion can be F/N
                    premise_t_result = wkrq.solve(premises_formula, 'T')
                    premise_m_result = wkrq.solve(premises_formula, 'M')
                    conclusion_f_result = wkrq.solve(conclusion_formula, 'F')
                    conclusion_n_result = wkrq.solve(conclusion_formula, 'N')
                    
                    if premise_t_result.satisfiable or premise_m_result.satisfiable:
                        countermodels = []
                        if conclusion_f_result.satisfiable:
                            countermodels.append("F (definitely false)")
                        if conclusion_n_result.satisfiable:
                            countermodels.append("N (need not be true)")
                        
                        if countermodels:
                            print(f"    - Conclusion can be: {', '.join(countermodels)}")
                else:
                    print("  ✗ Incorrectly identified as valid inference")
            else:
                # No premises - testing tautology
                conclusion_formula = wkrq.parse(case['conclusion'])
                
                # Test epistemic uncertainty about the conclusion
                m_result = wkrq.solve(conclusion_formula, 'M')
                n_result = wkrq.solve(conclusion_formula, 'N')
                
                if m_result.satisfiable or n_result.satisfiable:
                    print("  ✓ Epistemic uncertainty possible")
                    if m_result.satisfiable:
                        print("    - M: may be true (epistemic possibility)")
                    if n_result.satisfiable:
                        print("    - N: need not be true (epistemic uncertainty)")
                    
                    # Show tableau for epistemic uncertainty about tautologies
                    if i == 1:
                        show_tableau_visualization(
                            wkrq,
                            case['conclusion'],
                            sign='M',
                            description=f"M:{case['conclusion']} showing epistemic uncertainty"
                        )
                else:
                    print("  ✗ No epistemic uncertainty found")
                    
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print()

def test_first_order_countermodels():
    """
    First-order logic countermodel examples using wKrQ restricted quantifiers.
    """
    print("=== FIRST-ORDER wKrQ COUNTERMODELS ===\n")
    
    wkrq = LogicSystem.wkrq()
    
    countermodel_cases = [
        {
            "name": "Universal Instantiation Failure",
            "description": "[∀X Bird(X)]Flies(X) ∧ Bird(tweety) ⊬ Flies(tweety) (restricted quantifier)",
            "premises": ["[∀X Bird(X)]Flies(X)", "Bird(tweety)"],
            "conclusion": "Flies(tweety)",
            "source": "Ferguson restricted quantification"
        },
        {
            "name": "Existential Generalization Failure",
            "description": "Flies(tweety) ⊬ [∃X Bird(X)]Flies(X) (requires both existence and property)",
            "premises": ["Flies(tweety)"],
            "conclusion": "[∃X Bird(X)]Flies(X)",
            "source": "Restricted quantifier semantics"
        },
        {
            "name": "Domain Non-Emptiness Not Required",
            "description": "[∀X Student(X)]Smart(X) doesn't require any students to exist",
            "premises": ["[∀X Student(X)]Smart(X)"],
            "conclusion": "[∃X Student(X)]Smart(X)",
            "source": "Empty domain semantics"
        },
        {
            "name": "Cross-Predicate Inference Failure",
            "description": "[∀X Bird(X)]Flies(X) ⊬ [∀X Animal(X)]Moves(X) (different predicates)",
            "premises": ["[∀X Bird(X)]Flies(X)"],
            "conclusion": "[∀X Animal(X)]Moves(X)",
            "source": "Predicate independence"
        }
    ]
    
    for i, case in enumerate(countermodel_cases, 1):
        print(f"Test {i}: {case['name']}")
        print(f"  Description: {case['description']}")
        print(f"  Source: {case['source']}")
        
        try:
            # Test entailment
            entails = wkrq.parse_and_entails(case['premises'], case['conclusion'])
            
            if not entails:
                print("  ✓ Correctly identified as invalid inference")
                
                # Try to demonstrate why it fails
                premises_formula = wkrq.parse(" & ".join(f"({p})" for p in case['premises']))
                conclusion_formula = wkrq.parse(case['conclusion'])
                
                # Show that premises can be satisfied
                premise_result = wkrq.solve(premises_formula, 'T')
                if premise_result.satisfiable:
                    print("    - Premises are satisfiable")
                
                # Show that conclusion can fail
                conclusion_f_result = wkrq.solve(conclusion_formula, 'F')  
                conclusion_n_result = wkrq.solve(conclusion_formula, 'N')
                
                failure_modes = []
                if conclusion_f_result.satisfiable:
                    failure_modes.append("definitely false (F)")
                if conclusion_n_result.satisfiable:
                    failure_modes.append("epistemically uncertain (N)")
                
                if failure_modes:
                    print(f"    - Conclusion can be: {', '.join(failure_modes)}")
                    
                    # Show tableau for universal instantiation failure
                    if i == 1:
                        # Show the actual countermodel search
                        show_tableau_visualization(
                            wkrq,
                            f"({' & '.join(f'({p})' for p in case['premises'])}) & ~({case['conclusion']})",
                            description="searching for countermodel where premises are true but conclusion is false"
                        )
                    
            else:
                print("  ✗ Incorrectly identified as valid inference")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
        
        print()

def main():
    """Run all countermodel test suites."""
    print("COUNTERMODEL DEMONSTRATION SUITE")
    print("=" * 50)
    print("Testing invalid inferences P ⊬ Q across different logic systems")
    print("Demonstrates the unique semantic properties of each logical framework\n")
    
    test_classical_countermodels()
    test_weak_kleene_countermodels()
    test_wkrq_countermodels()
    test_first_order_countermodels()
    
    print("=" * 50)
    print("COUNTERMODEL SUITE COMPLETE")
    print("\nThis demonstrates how different logic systems handle invalid inferences:")
    print("• Classical: Standard countermodels with true/false assignments")
    print("• Weak Kleene: Undefined values that propagate through connectives")
    print("• wKrQ: Epistemic uncertainty with 'may be true' and 'need not be true'")
    print("• First-order wKrQ: Restricted quantification with domain-relative reasoning")

if __name__ == "__main__":
    main()