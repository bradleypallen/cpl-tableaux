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

from formula import Atom, Negation, Conjunction, Disjunction, Implication, Predicate
from term import Constant
from signed_formula import TF, FF, M, N
from signed_tableau import wkrq_signed_tableau


def print_step_by_step_tableau(tableau, title="Tableau Construction"):
    """Print tableau construction step by step, showing tree evolution"""
    from signed_tableau_rules import SignedRuleRegistry
    
    print(f"\n{title}:")
    print("-" * (len(title) + 1))
    
    # Start with initial state
    print("Step 0: Initial formulas")
    print("│")
    for i, sf in enumerate(tableau.initial_signed_formulas):
        connector = "├─" if i < len(tableau.initial_signed_formulas) - 1 else "└─"
        print(f"{connector} {sf}")
    print()
    
    # Build tableau step by step by reconstructing the process
    registry = SignedRuleRegistry()
    current_tree = TableauTreeState(tableau.initial_signed_formulas)
    step = 1
    all_processed = set()
    
    # Simulate the tableau building process
    while True:
        expansion_found = False
        next_expansion = None
        target_branch_idx = None
        
        for branch_idx, branch_formulas in enumerate(current_tree.branches):
            if current_tree.branch_closed[branch_idx]:
                continue
                
            for sf in branch_formulas:
                if sf in all_processed:
                    continue
                    
                rules = registry.find_applicable_rules(sf, "wkrq")
                if rules:
                    next_expansion = sf
                    target_branch_idx = branch_idx
                    expansion_found = True
                    break
            
            if expansion_found:
                break
        
        if not expansion_found:
            break
            
        # Apply the rule and show the step
        rule = registry.get_best_rule(next_expansion, "wkrq")
        result = rule.apply(next_expansion)
        
        print(f"Step {step}: Apply {rule.rule_type.name} to {next_expansion}")
        
        # Show tree before expansion
        print("Before:")
        current_tree.print_tree("│ ")
        
        # Apply the expansion
        current_tree.apply_expansion(target_branch_idx, next_expansion, result)
        all_processed.add(next_expansion)
        
        # Show tree after expansion
        print("After:")
        current_tree.print_tree("│ ")
        print()
        
        step += 1
    
    # Show final result
    print(f"Final Result: {'SATISFIABLE' if tableau.is_satisfiable() else 'UNSATISFIABLE'}")
    
    # Show closure information
    closed_branches = [(i, b) for i, b in enumerate(tableau.branches) if b.is_closed]
    if closed_branches:
        print("\nClosure Details:")
        for i, branch in closed_branches:
            if branch.closure_reason:
                sf1, sf2 = branch.closure_reason
                print(f"  Branch {i+1}: {sf1} ⊥ {sf2}")
    
    # Show models if satisfiable
    if tableau.is_satisfiable():
        models = tableau.extract_all_models()
        if models and models[0].assignments:
            assignments = []
            for formula, sign in models[0].assignments.items():
                if hasattr(formula, 'name'):  # Atomic formula
                    assignments.append(f"{sign}:{formula}")
                elif hasattr(formula, 'predicate_name'):  # Predicate
                    assignments.append(f"{sign}:{formula}")
            if assignments:
                print(f"  Countermodel: {{{', '.join(assignments)}}}")


class TableauTreeState:
    """Helper class to track tableau tree state during step-by-step construction"""
    
    def __init__(self, initial_formulas):
        self.branches = [list(initial_formulas)]
        self.branch_closed = [False]
        
    def apply_expansion(self, branch_idx, expanded_formula, rule_result):
        """Apply a rule expansion to the tree"""
        if rule_result.is_alpha:
            # α-rule: add formulas to same branch
            if rule_result.branches:
                for new_formula in rule_result.branches[0]:
                    self.branches[branch_idx].append(new_formula)
            self._check_branch_closure(branch_idx)
        else:
            # β-rule: create new branches
            original_branch = self.branches[branch_idx][:]
            
            # Replace the original branch with new branches
            self.branches.pop(branch_idx)
            self.branch_closed.pop(branch_idx)
            
            for i, branch_formulas in enumerate(rule_result.branches):
                new_branch = original_branch[:]
                new_branch.extend(branch_formulas)
                self.branches.insert(branch_idx + i, new_branch)
                self.branch_closed.insert(branch_idx + i, False)
                self._check_branch_closure(branch_idx + i)
                
    def _check_branch_closure(self, branch_idx):
        """Check if a branch should be closed due to contradictions"""
        branch = self.branches[branch_idx]
        
        # Build formula->signs mapping
        formula_signs = {}
        for sf in branch:
            formula = sf.formula
            if formula not in formula_signs:
                formula_signs[formula] = []
            formula_signs[formula].append(sf.sign)
        
        # Check for contradictions
        for formula, signs in formula_signs.items():
            for i, sign1 in enumerate(signs):
                for j, sign2 in enumerate(signs[i+1:], i+1):
                    if sign1.is_contradictory_with(sign2):
                        self.branch_closed[branch_idx] = True
                        return
                        
    def print_tree(self, prefix=""):
        """Print current tree state"""
        if len(self.branches) == 1:
            # Single branch
            branch = self.branches[0]
            status = "CLOSED" if self.branch_closed[0] else "OPEN"
            print(f"{prefix}Branch [status: {status}]:")
            for i, sf in enumerate(branch):
                connector = "├─" if i < len(branch) - 1 else "└─"
                print(f"{prefix}  {connector} {sf}")
        else:
            # Multiple branches
            print(f"{prefix}Branches:")
            for i, branch in enumerate(self.branches):
                status = "CLOSED" if self.branch_closed[i] else "OPEN"
                connector = "├─" if i < len(self.branches) - 1 else "└─"
                print(f"{prefix}  {connector} Branch {i+1} [status: {status}]:")
                
                for j, sf in enumerate(branch):
                    branch_prefix = "│   " if i < len(self.branches) - 1 else "    "
                    sf_connector = "├─" if j < len(branch) - 1 else "└─"
                    print(f"{prefix}  {branch_prefix}  {sf_connector} {sf}")


def test_inference_validity(premises, conclusion, description):
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
    
    # Build tableau
    tableau = wkrq_signed_tableau(test_formulas)
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
    test_inference_validity(
        premises=[TF(p)],
        conclusion=TF(disjunction), 
        description="Classical: T:p ⊢ T:(p ∨ q)"
    )
    
    # Test epistemic version 1: M:p ⊢ T:(p ∨ q)
    test_inference_validity(
        premises=[M(p)],
        conclusion=TF(disjunction),
        description="Epistemic: M:p ⊢ T:(p ∨ q)"
    )
    
    # Test epistemic version 2: T:p ⊢ M:(p ∨ q) 
    test_inference_validity(
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
    test_inference_validity(
        premises=[TF(p), TF(implication)],
        conclusion=TF(q),
        description="Classical Modus Ponens: T:p, T:(p → q) ⊢ T:q"
    )
    
    # Test epistemic modus ponens failure
    test_inference_validity(
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
    
    test_inference_validity(
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
    
    test_inference_validity(
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
    
    test_inference_validity(
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