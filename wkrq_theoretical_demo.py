#!/usr/bin/env python3
"""
wKrQ Theoretical Insights Demonstration

Demonstrates key theoretical insights about epistemic reasoning in the 
weak Kleene logic with restricted quantifiers (wKrQ), based on:

Ferguson, Thomas Macaulay. "Tableaux and restricted quantification for systems 
related to weak Kleene logic." In International Conference on Automated Reasoning 
with Analytic Tableaux and Related Methods, pp. 3-19. Cham: Springer International 
Publishing, 2021.
"""

from formula import Atom, Negation, Conjunction, Disjunction, Implication, RestrictedExistentialFormula, RestrictedUniversalFormula, Predicate
from term import Variable, Constant
from signed_formula import TF, FF, M, N
from signed_tableau import wkrq_signed_tableau


def get_rule_name(signed_formula, sign_system="wkrq"):
    """Get the tableau rule name that would apply to this signed formula"""
    from signed_tableau_rules import SignedRuleRegistry
    
    registry = SignedRuleRegistry()
    rule = registry.get_best_rule(signed_formula, sign_system)
    if rule:
        rule_type = rule.rule_type
        # Convert enum to readable string
        rule_name = str(rule_type).split('.')[-1]  # Get just the name part
        return rule_name
    else:
        return "ATOMIC"


def print_step_by_step_tableau(tableau, title="Step-by-Step Tableau Construction"):
    """Print tableau construction step by step, showing tree evolution"""
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
    step_by_step_construction(tableau)
    
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
            if assignments:
                print(f"  Model: {{{', '.join(assignments)}}}")


def step_by_step_construction(tableau):
    """Reconstruct and display the tableau construction process step by step"""
    from signed_tableau_rules import SignedRuleRegistry
    
    registry = SignedRuleRegistry()
    
    # Start with initial state
    current_tree = TableauTreeState(tableau.initial_signed_formulas)
    step = 1
    
    # Track which formulas have been processed globally
    all_processed = set()
    
    # Simulate the tableau building process
    while True:
        expansion_found = False
        
        # Find next formula to expand across all open branches
        next_expansion = None
        target_branch_idx = None
        
        for branch_idx, branch_formulas in enumerate(current_tree.branches):
            if current_tree.branch_closed[branch_idx]:
                continue
                
            # Find expandable formulas in this branch
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


class TableauTreeState:
    """Helper class to track tableau tree state during step-by-step construction"""
    
    def __init__(self, initial_formulas):
        self.branches = [list(initial_formulas)]  # List of branches, each branch is list of formulas
        self.branch_closed = [False]  # Track which branches are closed
        self.step_history = []  # Track what happened at each step
        
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
            # Don't remove expanded formula - keep it visible in the tree
            
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


def print_tableau_tree(tableau, title="Tableau Construction"):
    """Print tableau using the new step-by-step approach"""
    print_step_by_step_tableau(tableau, title)


def print_single_branch_tree(branch, initial_formulas):
    """Print a single branch tableau tree"""
    # Track what we've shown
    shown_formulas = set(initial_formulas)
    
    # Show rule applications in order
    step = 1
    for processed_sf in branch.processed_signed_formulas:
        if processed_sf in shown_formulas:
            rule_name = get_rule_name(processed_sf)
            print(f"\nStep {step}: Apply {rule_name} to {processed_sf}")
            
            # Show what this rule produces
            new_formulas = []
            for sf in branch.signed_formulas:
                if sf not in shown_formulas and sf != processed_sf:
                    new_formulas.append(sf)
            
            if new_formulas:
                for nf in new_formulas:
                    print(f"  ├─ {nf}")
                    shown_formulas.add(nf)
            
            step += 1
    
    # Show final branch status
    if branch.is_closed:
        print(f"\n✗ Branch closes")
    else:
        print(f"\n✓ Branch remains open")


def print_branching_tree(tableau):
    """Print a branching tableau tree"""
    print("│")
    
    # Find the branching point
    branching_formula = None
    for branch in tableau.branches:
        for processed_sf in branch.processed_signed_formulas:
            rule_name = get_rule_name(processed_sf)
            if "DISJUNCTION" in rule_name or "T∨" in rule_name or "M∨" in rule_name or "F∧" in rule_name or "N∧" in rule_name:
                branching_formula = processed_sf
                break
        if branching_formula:
            break
    
    if branching_formula:
        rule_name = get_rule_name(branching_formula)
        print(f"Apply {rule_name} to {branching_formula}")
        print("│")
    
    # Show branches
    for i, branch in enumerate(tableau.branches):
        prefix = "├─" if i < len(tableau.branches) - 1 else "└─"
        print(f"{prefix} Branch {i+1}:")
        
        # Show branch-specific formulas (excluding common ones)
        branch_specific = []
        for sf in branch.signed_formulas:
            if sf not in tableau.initial_signed_formulas and (not branching_formula or sf != branching_formula):
                branch_specific.append(sf)
        
        for sf in branch_specific[:3]:  # Show first few
            indent = "│   " if i < len(tableau.branches) - 1 else "    "
            print(f"{indent}  {sf}")
        
        # Show status
        indent = "│   " if i < len(tableau.branches) - 1 else "    "
        status = "CLOSED" if branch.is_closed else "OPEN"
        print(f"{indent}  [{status}]")


def print_detailed_tableau_analysis(tableau, title="Detailed Tableau Analysis"):
    """Print comprehensive tableau analysis with rule details"""
    print(f"\n{title}:")
    print("-" * (len(title) + 1))
    
    # Statistics
    stats = tableau.get_statistics()
    print(f"Branches: {stats['total_branches']} total, {stats['open_branches']} open, {stats['closed_branches']} closed")
    print(f"Rule applications: {stats['rule_applications']}")
    
    # Show each branch with details
    for i, branch in enumerate(tableau.branches):
        print(f"\nBranch {i+1}:")
        
        # Initial vs derived formulas
        initial_in_branch = [sf for sf in tableau.initial_signed_formulas if sf in branch.signed_formulas]
        derived_formulas = [sf for sf in branch.signed_formulas if sf not in tableau.initial_signed_formulas]
        
        print(f"  Initial: {[str(sf) for sf in initial_in_branch]}")
        if derived_formulas:
            print(f"  Derived: {[str(sf) for sf in derived_formulas]}")
        
        # Show rule applications for this branch
        if branch.processed_signed_formulas:
            print(f"  Rules applied:")
            for processed_sf in branch.processed_signed_formulas:
                rule_name = get_rule_name(processed_sf)
                print(f"    {rule_name} → {processed_sf}")
        
        # Status
        if branch.is_closed:
            sf1, sf2 = branch.closure_reason if branch.closure_reason else (None, None)
            print(f"  Status: CLOSED ({sf1} contradicts {sf2})")
        else:
            print(f"  Status: OPEN")


def print_tableau_details(tableau, title="Tableau Details"):
    """Print tableau using the new step-by-step approach"""
    print_step_by_step_tableau(tableau, title)


def insight_1_epistemic_uncertainty_without_contradiction():
    """
    Theoretical Insight 1: Epistemic Uncertainty Without Contradiction
    
    In the wKrQ system, epistemic signs M (may be true) and N (need not be true)
    represent uncertainty rather than classical truth values. Unlike classical T/F pairs,
    M and N do not create contradictions when applied to the same formula.
    """
    print("=" * 70)
    print("INSIGHT 1: Epistemic Uncertainty Without Contradiction")
    print("=" * 70)
    
    p = Atom("p")
    
    # Classical contradiction: T:p ∧ F:p
    print("Classical Case: T:p ∧ F:p")
    classical_tableau = wkrq_signed_tableau([TF(p), FF(p)])
    classical_result = classical_tableau.build()
    print(f"Result: {'SATISFIABLE' if classical_result else 'UNSATISFIABLE'}")
    print("Explanation: Classical signs T and F represent definite truth values")
    print("that contradict each other, closing all tableau branches.")
    print_tableau_details(classical_tableau, "Classical Tableau")
    
    # Epistemic uncertainty: M:p ∧ N:p
    print("\nEpistemic Case: M:p ∧ N:p")
    epistemic_tableau = wkrq_signed_tableau([M(p), N(p)])
    epistemic_result = epistemic_tableau.build()
    print(f"Result: {'SATISFIABLE' if epistemic_result else 'UNSATISFIABLE'}")
    print("Explanation: M:p ('p may be true') and N:p ('p need not be true')")
    print("both express epistemic uncertainty about p's truth value without")
    print("creating a logical contradiction. They can coexist.")
    print_tableau_details(epistemic_tableau, "Epistemic Tableau")


def insight_2_epistemic_reasoning_about_tautologies():
    """
    Theoretical Insight 2: Epistemic Reasoning About Tautologies
    
    the system allows expressing epistemic uncertainty even about logical
    tautologies. While p ∨ ¬p is truth-functionally valid, we can still be
    epistemically uncertain about it using M:(p ∨ ¬p).
    """
    print("\n" + "=" * 70)
    print("INSIGHT 2: Epistemic Reasoning About Tautologies")  
    print("=" * 70)
    
    p = Atom("p")
    excluded_middle = Disjunction(p, Negation(p))
    
    # Classical negation of tautology: F:(p ∨ ¬p)
    print("Classical Case: F:(p ∨ ¬p)")
    classical_tableau = wkrq_signed_tableau(FF(excluded_middle))
    classical_result = classical_tableau.build()
    print(f"Result: {'SATISFIABLE' if classical_result else 'UNSATISFIABLE'}")
    print("Explanation: The negation of a tautology is unsatisfiable in")
    print("classical logic - there's no model where p ∨ ¬p is false.")
    print_tableau_details(classical_tableau, "Classical F:(p ∨ ¬p) Tableau")
    
    # Epistemic uncertainty about tautology: M:(p ∨ ¬p)
    print("\nEpistemic Case: M:(p ∨ ¬p)")
    epistemic_tableau = wkrq_signed_tableau(M(excluded_middle))
    epistemic_result = epistemic_tableau.build()
    print(f"Result: {'SATISFIABLE' if epistemic_result else 'UNSATISFIABLE'}")
    print("Explanation: M:(p ∨ ¬p) expresses epistemic uncertainty about")
    print("whether the excluded middle holds, even though it's truth-functionally")
    print("valid. This separates epistemic and truth-functional dimensions.")
    print_tableau_details(epistemic_tableau, "Epistemic M:(p ∨ ¬p) Tableau")


def insight_3_sign_duality_in_negation():
    """
    Theoretical Insight 3: Sign Duality in Negation Rules
    
    the signs exhibit duality relationships: T↔F (classical) and M↔N (epistemic).
    This duality is crucial for proper handling of negation in tableau rules.
    """
    print("\n" + "=" * 70)
    print("INSIGHT 3: Sign Duality in Negation Rules")
    print("=" * 70)
    
    p = Atom("p")
    neg_p = Negation(p)
    
    # Show sign dualities
    from signed_formula import WkrqSign
    signs = [WkrqSign("T"), WkrqSign("F"), WkrqSign("M"), WkrqSign("N")]
    
    print("Sign Duality Relationships:")
    for sign in signs:
        print(f"  {sign} ↔ {sign.dual()}")
    print()
    
    # Demonstrate in negation: M:¬p
    print("Example: M:¬p ('¬p may be true')")
    m_neg_p_tableau = wkrq_signed_tableau(M(neg_p))
    m_neg_p_result = m_neg_p_tableau.build()
    print(f"Result: {'SATISFIABLE' if m_neg_p_result else 'UNSATISFIABLE'}")
    print("Explanation: According to duality, M:¬p should lead to N:p in")
    print("tableau expansion, meaning 'if ¬p may be true, then p need not be true'.")
    print_tableau_details(m_neg_p_tableau, "M:¬p Tableau (shows duality)")
    
    # Dual case: N:¬p
    print("\nDual Example: N:¬p ('¬p need not be true')")
    n_neg_p_tableau = wkrq_signed_tableau(N(neg_p))
    n_neg_p_result = n_neg_p_tableau.build()
    print(f"Result: {'SATISFIABLE' if n_neg_p_result else 'UNSATISFIABLE'}")
    print("Explanation: By duality, N:¬p should lead to M:p, meaning")
    print("'if ¬p need not be true, then p may be true'.")
    print_tableau_details(n_neg_p_tableau, "N:¬p Tableau (shows duality)")


def insight_4_predicate_logic_epistemics():
    """
    Theoretical Insight 4: Epistemic Reasoning with Predicate Logic
    
    the wKrQ system handles predicate logic with individual constants,
    allowing epistemic uncertainty about specific facts like "Tweety flies" 
    or "Socrates is human".
    """
    print("\n" + "=" * 70)
    print("INSIGHT 4: Epistemic Reasoning with Predicate Logic")
    print("=" * 70)
    
    # Set up individual constants and predicates
    tweety = Constant("tweety")
    socrates = Constant("socrates") 
    fido = Constant("fido")
    
    # Basic predicate atoms with individual constants
    tweety_bird = Predicate("Bird", [tweety])
    tweety_flies = Predicate("Flies", [tweety])
    socrates_human = Predicate("Human", [socrates])
    socrates_mortal = Predicate("Mortal", [socrates])
    fido_dog = Predicate("Dog", [fido])
    
    # Example 1: Epistemic uncertainty about specific facts
    print("Example 1: M:Bird(tweety) ∧ N:Flies(tweety)")
    print("Reading: 'Tweety may be a bird, but it need not be true that Tweety flies'")
    
    m_tweety_bird = M(tweety_bird)
    n_tweety_flies = N(tweety_flies)
    
    predicate_tableau = wkrq_signed_tableau([m_tweety_bird, n_tweety_flies])
    predicate_result = predicate_tableau.build()
    print(f"Result: {'SATISFIABLE' if predicate_result else 'UNSATISFIABLE'}")
    print("Explanation: Epistemic signs allow uncertainty about individual facts.")
    print("We can be uncertain whether Tweety flies even if we're uncertain whether")
    print("Tweety is a bird. These represent different dimensions of uncertainty.")
    print_tableau_details(predicate_tableau, "M:Bird(tweety) ∧ N:Flies(tweety) Tableau")
    
    # Example 2: Classical vs epistemic reasoning about individuals
    print("\nExample 2: Classical vs Epistemic - T:Human(socrates) vs M:Human(socrates)")
    
    # Classical: definite knowledge
    t_socrates_human = TF(socrates_human)
    classical_predicate_tableau = wkrq_signed_tableau(t_socrates_human)
    classical_predicate_result = classical_predicate_tableau.build()
    print("Classical: T:Human(socrates)")
    print(f"Result: {'SATISFIABLE' if classical_predicate_result else 'UNSATISFIABLE'}")
    print("Explanation: Definite knowledge that Socrates is human.")
    print_tableau_details(classical_predicate_tableau, "T:Human(socrates) Tableau")
    
    # Epistemic: uncertainty
    m_socrates_human = M(socrates_human)
    epistemic_predicate_tableau = wkrq_signed_tableau(m_socrates_human)
    epistemic_predicate_result = epistemic_predicate_tableau.build()
    print("\nEpistemic: M:Human(socrates)")
    print(f"Result: {'SATISFIABLE' if epistemic_predicate_result else 'UNSATISFIABLE'}")
    print("Explanation: Epistemic uncertainty - Socrates may be human, but we're")
    print("not committing to definite knowledge about his humanity.")
    print_tableau_details(epistemic_predicate_tableau, "M:Human(socrates) Tableau")
    
    # Example 3: Complex predicate reasoning with epistemic signs
    print("\nExample 3: Complex - T:Dog(fido) ∧ M:(Dog(fido) → Mortal(fido))")
    t_fido_dog = TF(fido_dog)
    fido_mortal = Predicate("Mortal", [fido])
    dog_implies_mortal = Implication(fido_dog, fido_mortal)
    m_dog_implies_mortal = M(dog_implies_mortal)
    
    complex_predicate_tableau = wkrq_signed_tableau([t_fido_dog, m_dog_implies_mortal])
    complex_predicate_result = complex_predicate_tableau.build()
    print(f"Result: {'SATISFIABLE' if complex_predicate_result else 'UNSATISFIABLE'}")
    print("Explanation: We have definite knowledge that Fido is a dog, but")
    print("epistemic uncertainty about whether 'if Fido is a dog, then Fido is mortal'.")
    print("This shows mixing definite facts with uncertain rules about individuals.")
    print_tableau_details(complex_predicate_tableau, "T:Dog(fido) ∧ M:(Dog(fido) → Mortal(fido)) Tableau")


def insight_5_restricted_quantifier_epistemics():
    """
    Theoretical Insight 5: Epistemic Reasoning with Restricted Quantifiers
    
    the system extends to restricted quantifiers, allowing epistemic
    uncertainty about quantified statements like "all birds fly" or
    "there exists a student who is human".
    """
    print("\n" + "=" * 70)
    print("INSIGHT 5: Epistemic Reasoning with Restricted Quantifiers")
    print("=" * 70)
    
    # Set up quantified formulas
    x = Variable("X")
    bird_x = Predicate("Bird", [x])
    flies_x = Predicate("Flies", [x])
    student_x = Predicate("Student", [x])
    human_x = Predicate("Human", [x])
    
    # Universal quantifier with epistemic uncertainty
    all_birds_fly = RestrictedUniversalFormula(x, bird_x, flies_x)
    print("Example 1: N:[∀X Bird(X)]Flies(X)")
    print("Reading: 'It need not be true that all birds fly'")
    
    n_universal_tableau = wkrq_signed_tableau(N(all_birds_fly))
    n_universal_result = n_universal_tableau.build()
    print(f"Result: {'SATISFIABLE' if n_universal_result else 'UNSATISFIABLE'}")
    print("Explanation: N allows for epistemic possibility that the universal")
    print("claim might be false (counterexamples may exist), without asserting")
    print("that it definitely is false.")
    print_tableau_details(n_universal_tableau, "N:[∀X Bird(X)]Flies(X) Tableau")
    
    # Existential quantifier with epistemic uncertainty  
    exists_student_human = RestrictedExistentialFormula(x, student_x, human_x)
    print("\nExample 2: M:[∃X Student(X)]Human(X)")
    print("Reading: 'It may be true that there exists a student who is human'")
    
    m_existential_tableau = wkrq_signed_tableau(M(exists_student_human))
    m_existential_result = m_existential_tableau.build()
    print(f"Result: {'SATISFIABLE' if m_existential_result else 'UNSATISFIABLE'}")
    print("Explanation: M expresses epistemic possibility that the existential")
    print("claim is true, without committing to its definite truth value.")
    print_tableau_details(m_existential_tableau, "M:[∃X Student(X)]Human(X) Tableau")


def insight_6_mixed_definite_epistemic_reasoning():
    """
    Theoretical Insight 6: Mixed Definite and Epistemic Reasoning
    
    the system allows combining definite knowledge (T/F signs) with
    epistemic uncertainty (M/N signs) in the same reasoning context.
    """
    print("\n" + "=" * 70)
    print("INSIGHT 6: Mixed Definite and Epistemic Reasoning")
    print("=" * 70)
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    # Scenario: definite knowledge about p, uncertainty about q and r
    definite_p = TF(p)      # "p is definitely true"
    maybe_q = M(q)          # "q may be true"
    need_not_r = N(r)       # "r need not be true"
    
    print("Scenario: T:p ∧ M:q ∧ N:r")
    print("Reading: 'p is definitely true, q may be true, r need not be true'")
    
    mixed_tableau = wkrq_signed_tableau([definite_p, maybe_q, need_not_r])
    mixed_result = mixed_tableau.build()
    print(f"Result: {'SATISFIABLE' if mixed_result else 'UNSATISFIABLE'}")
    print("Explanation: Definite knowledge (T:p) coexists with epistemic")
    print("uncertainty (M:q, N:r). The system handles both dimensions of")
    print("reasoning simultaneously without conflict.")
    print_tableau_details(mixed_tableau, "T:p ∧ M:q ∧ N:r Tableau - Mixed Reasoning")
    
    # Complex interaction: definite implication with epistemic consequent
    impl = Implication(p, q)
    definite_impl = TF(impl)    # "p → q is definitely true"
    
    print("\nComplex Example: T:p ∧ T:(p → q) ∧ M:q")
    combined_tableau = wkrq_signed_tableau([definite_p, definite_impl, maybe_q])
    combined_result = combined_tableau.build()
    print(f"Result: {'SATISFIABLE' if combined_result else 'UNSATISFIABLE'}")
    print("Explanation: Even with definite modus ponens (T:p, T:(p → q)),")
    print("we can still express epistemic uncertainty about the conclusion (M:q).")
    print_tableau_details(combined_tableau, "T:p ∧ T:(p → q) ∧ M:q Tableau - Modus Ponens with Epistemic Conclusion")


def insight_7_countermodels_to_inferences():
    """
    Theoretical Insight 7: Countermodels to Inferences in Epistemic Logic
    
    the wKrQ system can provide countermodels to classically valid inferences
    when epistemic uncertainty is involved. This shows the distinction between 
    truth-functional validity and epistemic validity.
    """
    print("\n" + "=" * 70)
    print("INSIGHT 7: Countermodels to Inferences in Epistemic Logic") 
    print("=" * 70)
    
    p = Atom("p")
    q = Atom("q")
    
    # Classical inference: p ⊢ p ∨ q (always valid)
    print("Classical Inference: p ⊢ p ∨ q")
    print("To test validity: check if T:p ∧ F:(p ∨ q) is unsatisfiable")
    
    disjunction = Disjunction(p, q)
    classical_premise = TF(p)           # T:p (premise)
    classical_conclusion_neg = FF(disjunction)  # F:(p ∨ q) (negated conclusion)
    
    classical_inference_test = wkrq_signed_tableau([classical_premise, classical_conclusion_neg])
    classical_inference_result = classical_inference_test.build()
    
    print(f"Result: {'SATISFIABLE (invalid inference)' if classical_inference_result else 'UNSATISFIABLE (valid inference)'}")
    print("Explanation: In classical logic, if p is true, then p ∨ q must be true.")
    print("No countermodel exists for this inference.")
    print_tableau_details(classical_inference_test, "Classical T:p ∧ F:(p ∨ q) Tableau")
    
    # Epistemic countermodel 1: M:p does not entail T:(p ∨ q)
    print("\nEpistemic Case 1: M:p ⊬ T:(p ∨ q)")  
    print("Testing: M:p ∧ F:(p ∨ q) - can we be uncertain about p but certain that p ∨ q is false?")
    
    epistemic_premise1 = M(p)           # M:p (p may be true)
    epistemic_conclusion_neg1 = FF(disjunction)  # F:(p ∨ q) (p ∨ q is definitely false)
    
    epistemic_inference_test1 = wkrq_signed_tableau([epistemic_premise1, epistemic_conclusion_neg1])
    epistemic_inference_result1 = epistemic_inference_test1.build()
    
    print(f"Result: {'SATISFIABLE (countermodel exists)' if epistemic_inference_result1 else 'UNSATISFIABLE (no countermodel)'}")
    if epistemic_inference_result1:
        print("Countermodel found! M:p can be true while F:(p ∨ q) is true when both p and q")
        print("are epistemically uncertain but the disjunction is definitely false.")
        models = epistemic_inference_test1.extract_all_models()
        if models:
            print(f"Sample countermodel: {models[0]}")
    print_tableau_details(epistemic_inference_test1, "Epistemic M:p ∧ F:(p ∨ q) Tableau")
    
    # Epistemic countermodel 2: T:p does not entail M:(p ∨ q) 
    print("\nEpistemic Case 2: T:p ⊬ M:(p ∨ q)")
    print("Testing: T:p ∧ N:(p ∨ q) - definite p but disjunction need not be true?")
    
    epistemic_premise2 = TF(p)          # T:p (p is definitely true)  
    epistemic_conclusion_neg2 = N(disjunction)  # N:(p ∨ q) (p ∨ q need not be true)
    
    epistemic_inference_test2 = wkrq_signed_tableau([epistemic_premise2, epistemic_conclusion_neg2])
    epistemic_inference_result2 = epistemic_inference_test2.build()
    
    print(f"Result: {'SATISFIABLE (countermodel exists)' if epistemic_inference_result2 else 'UNSATISFIABLE (no countermodel)'}")
    if epistemic_inference_result2:
        print("Countermodel found! Even with definite T:p, we can have epistemic")
        print("uncertainty N:(p ∨ q) about the disjunction. This shows that truth-functional")
        print("entailment doesn't always preserve epistemic certainty.")
    print_tableau_details(epistemic_inference_test2, "Epistemic T:p ∧ N:(p ∨ q) Tableau")
    
    # More complex: Modus Ponens with epistemic uncertainty
    print("\nComplex Case: Epistemic Modus Ponens")
    print("Classical: T:p ∧ T:(p → q) ⊢ T:q (valid)")
    print("Epistemic: M:p ∧ M:(p → q) ⊬ T:q (may have countermodel)")
    
    implication = Implication(p, q)    
    epistemic_premise3a = M(p)              # M:p (p may be true)
    epistemic_premise3b = M(implication)    # M:(p → q) (implication may be true)
    epistemic_conclusion_neg3 = FF(q)       # F:q (q is definitely false)
    
    modus_ponens_test = wkrq_signed_tableau([epistemic_premise3a, epistemic_premise3b, epistemic_conclusion_neg3])
    modus_ponens_result = modus_ponens_test.build()
    
    print(f"Testing: M:p ∧ M:(p → q) ∧ F:q")
    print(f"Result: {'SATISFIABLE (countermodel exists)' if modus_ponens_result else 'UNSATISFIABLE (no countermodel)'}")
    if modus_ponens_result:
        print("Countermodel found! Epistemic uncertainty about premises can allow")
        print("definite falsity of conclusion - showing epistemic modus ponens is not valid.")
    print_tableau_details(modus_ponens_test, "Epistemic M:p ∧ M:(p → q) ∧ F:q Tableau")
    
    # Predicate logic countermodel
    print("\nPredicate Logic Countermodel: Bird(tweety) ⊬ Flies(tweety)")
    print("Testing: T:Bird(tweety) ∧ F:Flies(tweety)")
    
    tweety = Constant("tweety")
    bird_tweety = Predicate("Bird", [tweety])
    flies_tweety = Predicate("Flies", [tweety])
    
    predicate_premise = TF(bird_tweety)         # T:Bird(tweety)
    predicate_conclusion_neg = FF(flies_tweety) # F:Flies(tweety)
    
    predicate_inference_test = wkrq_signed_tableau([predicate_premise, predicate_conclusion_neg])
    predicate_inference_result = predicate_inference_test.build()
    
    print(f"Result: {'SATISFIABLE (countermodel exists)' if predicate_inference_result else 'UNSATISFIABLE (no countermodel)'}")
    if predicate_inference_result:
        print("Countermodel found! Being a bird doesn't logically entail flying.")
        print("This shows how countermodels work with individual constants and predicates.")
        models = predicate_inference_test.extract_all_models()
        if models:
            print(f"Countermodel: {models[0]}")
    print_tableau_details(predicate_inference_test, "T:Bird(tweety) ∧ F:Flies(tweety) Predicate Countermodel")


def insight_8_non_classical_contradiction_handling():
    """
    Theoretical Insight 8: Non-Classical Contradiction Handling
    
    the system provides a sophisticated approach to contradictions,
    distinguishing between classical contradictions (T:φ ∧ F:φ) which close
    branches, and epistemic uncertainty which remains satisfiable.
    """
    print("\n" + "=" * 70)
    print("INSIGHT 8: Non-Classical Contradiction Handling")
    print("=" * 70)
    
    p = Atom("p")
    contradiction = Conjunction(p, Negation(p))
    
    # Classical approach: definite contradiction
    print("Classical Contradiction: T:(p ∧ ¬p)")
    classical_contradiction_tableau = wkrq_signed_tableau(TF(contradiction))
    classical_contradiction_result = classical_contradiction_tableau.build()
    print(f"Result: {'SATISFIABLE' if classical_contradiction_result else 'UNSATISFIABLE'}")
    print("Explanation: A definite contradiction is unsatisfiable even")
    print("in the system - T:(p ∧ ¬p) cannot be true in any model.")
    print_tableau_details(classical_contradiction_tableau, "T:(p ∧ ¬p) Tableau - Shows Rule Expansion")
    
    # Epistemic approach: uncertainty about contradiction
    print("\nEpistemic Uncertainty: M:(p ∧ ¬p)")
    epistemic_contradiction_tableau = wkrq_signed_tableau(M(contradiction))
    epistemic_contradiction_result = epistemic_contradiction_tableau.build()
    print(f"Result: {'SATISFIABLE' if epistemic_contradiction_result else 'UNSATISFIABLE'}")
    print("Explanation: M:(p ∧ ¬p) expresses epistemic uncertainty about")
    print("whether the contradiction holds, which is satisfiable. This shows")
    print("the distinction between truth-functional and epistemic levels.")
    print_tableau_details(epistemic_contradiction_tableau, "M:(p ∧ ¬p) Tableau - Epistemic Expansion")
    
    # Comparison with definite and epistemic for same formula
    print("\nMixed Signs: T:p ∧ M:p")
    mixed_signs_tableau = wkrq_signed_tableau([TF(p), M(p)])
    mixed_signs_result = mixed_signs_tableau.build()
    print(f"Result: {'SATISFIABLE' if mixed_signs_result else 'UNSATISFIABLE'}")
    print("Explanation: T:p (definite truth) coexists with M:p (epistemic")
    print("possibility) without contradiction - they operate on different levels.")
    print_tableau_details(mixed_signs_tableau, "T:p ∧ M:p Tableau - Mixed Signs")


def main():
    """Run all theoretical insight demonstrations"""
    print("Ferguson wKrQ Theoretical Insights Demonstration")
    print("Based on Ferguson (2021) - Weak Kleene Logic with Restricted Quantifiers")
    
    insight_1_epistemic_uncertainty_without_contradiction()
    insight_2_epistemic_reasoning_about_tautologies()
    insight_3_sign_duality_in_negation()
    insight_4_predicate_logic_epistemics()
    insight_5_restricted_quantifier_epistemics()
    insight_6_mixed_definite_epistemic_reasoning()
    insight_7_countermodels_to_inferences()
    insight_8_non_classical_contradiction_handling()
    
    print("\n" + "=" * 70)
    print("THEORETICAL INSIGHTS SUMMARY")
    print("=" * 70)
    print("the wKrQ system demonstrates:")
    print("  1. Epistemic uncertainty (M/N) distinct from classical contradiction")
    print("  2. Epistemic reasoning about tautologies and logical principles")
    print("  3. Systematic sign duality for proper negation handling")
    print("  4. Epistemic reasoning about predicate logic with individual constants")
    print("  5. Epistemic uncertainty extended to quantified statements")
    print("  6. Integration of definite knowledge with epistemic uncertainty")
    print("  7. Countermodels to classically valid inferences using epistemic signs")
    print("  8. Sophisticated contradiction handling across epistemic levels")
    print()
    print("These insights show how the four-valued signing system")
    print("provides a principled framework for reasoning under epistemic")
    print("uncertainty in weak Kleene logic with restricted quantifiers.")


if __name__ == "__main__":
    main()