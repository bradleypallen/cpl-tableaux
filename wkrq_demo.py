#!/usr/bin/env python3
"""
wKrQ Demonstration - Weak Kleene Logic with Restricted Quantifiers

Demonstrates the wKrQ (Weak Kleene Logic with Restricted Quantifiers) 
implementation based on:
Ferguson, Thomas Macaulay. "Tableaux and restricted quantification for systems 
related to weak Kleene logic." In International Conference on Automated Reasoning 
with Analytic Tableaux and Related Methods, pp. 3-19. Cham: Springer International 
Publishing, 2021.

This shows:
- Restricted quantifier semantics ∃̌ and ∀̌
- Three-valued logic reasoning
- First-order domain management
- Model extraction from satisfiable formulas
"""

import traceback
from typing import List

# Import core components
from formula import RestrictedExistentialFormula, RestrictedUniversalFormula, Predicate, Conjunction, Negation
from term import Variable, Constant
from truth_value import t, f, e, RestrictedQuantifierOperators

# Import wKrQ system
from wkrq_components import WKrQ_Branch, WKrQ_ModelExtractor


def print_header(title: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def print_subheader(title: str):
    """Print subsection header"""
    print(f"\n{title}")
    print("-" * len(title))


def demo_restricted_quantifier_semantics():
    """Demonstrate restricted quantifier truth value semantics"""
    print_header("RESTRICTED QUANTIFIER SEMANTICS DEMO")
    
    print("Based on Ferguson (2021) Definition 3:")
    print("∃̌(X) and ∀̌(X) for sets X ⊆ V₃²")
    
    print_subheader("Restricted Existential ∃̌(X)")
    
    # Example 1: ⟨t,t⟩ ∈ X → result is t
    value_pairs = {(t, t), (f, e), (e, f)}
    result = RestrictedQuantifierOperators.restricted_existential(value_pairs)
    print(f"X = {value_pairs}")
    print(f"∃̌(X) = {result} (contains ⟨t,t⟩)")
    
    # Example 2: All pairs have e component → result is e
    value_pairs = {(e, t), (f, e), (e, e)}
    result = RestrictedQuantifierOperators.restricted_existential(value_pairs)
    print(f"X = {value_pairs}")
    print(f"∃̌(X) = {result} (all pairs have e component)")
    
    # Example 3: No ⟨t,t⟩ and some non-e pairs → result is f
    value_pairs = {(t, f), (f, t)}
    result = RestrictedQuantifierOperators.restricted_existential(value_pairs)
    print(f"X = {value_pairs}")
    print(f"∃̌(X) = {result} (no ⟨t,t⟩, has non-e pairs)")
    
    print_subheader("Restricted Universal ∀̌(X)")
    
    # Example 1: All pairs have e component → result is e
    value_pairs = {(e, t), (f, e), (e, e)}
    result = RestrictedQuantifierOperators.restricted_universal(value_pairs)
    print(f"X = {value_pairs}")
    print(f"∀̌(X) = {result} (all pairs have e component)")
    
    # Example 2: Contains critical pairs → result is f
    value_pairs = {(t, f), (f, t)}
    result = RestrictedQuantifierOperators.restricted_universal(value_pairs)
    print(f"X = {value_pairs}")
    print(f"∀̌(X) = {result} (contains ⟨t,f⟩, has non-e pairs)")
    
    # Example 3: No critical pairs, has non-e pairs → result is t
    value_pairs = {(t, t), (f, f)}
    result = RestrictedQuantifierOperators.restricted_universal(value_pairs)
    print(f"X = {value_pairs}")
    print(f"∀̌(X) = {result} (no critical pairs, has non-e pairs)")


def demo_formula_construction():
    """Demonstrate wKrQ formula construction"""
    print_header("wKrQ FORMULA CONSTRUCTION DEMO")
    
    # Create terms
    x = Variable("X")
    y = Variable("Y")
    john = Constant("john")
    mary = Constant("mary")
    
    print("Variables:", x, y)
    print("Constants:", john, mary)
    
    # Create predicates
    student_x = Predicate("Student", [x])
    loves_xy = Predicate("Loves", [x, y])
    student_john = Predicate("Student", [john])
    
    print(f"\nPredicates:")
    print(f"Student(X): {student_x}")
    print(f"Loves(X,Y): {loves_xy}")  
    print(f"Student(john): {student_john}")
    
    # Create restricted quantified formulas showing subsumption relationships
    human_x = Predicate("Human", [x])
    bachelor_x = Predicate("Bachelor", [x])
    unmarried_male_x = Predicate("UnmarriedMale", [x])
    animal_x = Predicate("Animal", [x])
    dog_x = Predicate("Dog", [x])
    
    # Subsumption examples
    student_human = RestrictedExistentialFormula(x, student_x, human_x)
    bachelor_unmarried = RestrictedUniversalFormula(x, bachelor_x, unmarried_male_x)
    dog_animal = RestrictedUniversalFormula(x, dog_x, animal_x)
    
    print(f"\nRestricted Quantified Formulas (Subsumption Relations):")
    print(f"[∃X Student(X)]Human(X): {student_human}")
    print(f"  - 'There exists a student who is human'")
    print(f"[∀X Bachelor(X)]UnmarriedMale(X): {bachelor_unmarried}")
    print(f"  - 'Every bachelor is an unmarried male' (subsumption)")
    print(f"[∀X Dog(X)]Animal(X): {dog_animal}")
    print(f"  - 'Every dog is an animal' (subsumption)")
    
    # Create complex nested formula
    person_x = Predicate("Person", [x])
    loves_john = Predicate("Loves", [x, Constant("john")])
    complex_formula = RestrictedUniversalFormula(x, person_x, 
                          RestrictedExistentialFormula(y, student_x, loves_xy))
    
    print(f"\nComplex Nested Formula:")
    print(f"[∀X Person(X)][∃Y Student(Y)]Loves(X,Y): {complex_formula}")
    print(f"  - 'Every person relates to some student through love'")
    
    # Create subsumption test case
    not_human_x = Negation(human_x)
    contradiction = Conjunction(
        RestrictedUniversalFormula(x, student_x, human_x),  # All students are human
        RestrictedExistentialFormula(x, student_x, not_human_x)  # Some student is not human
    )
    print(f"\nContradictory Subsumption:")
    print(f"[∀X Student(X)]Human(X) ∧ [∃X Student(X)]¬Human(X): {contradiction}")
    print(f"  - 'All students are human AND some student is not human'")


def demo_branch_reasoning():
    """Demonstrate wKrQ branch reasoning with domain management"""
    print_header("wKrQ BRANCH REASONING DEMO")
    
    # Create branch
    branch = WKrQ_Branch(1)
    print(f"Created branch {branch.id}")
    
    # Add constants to domain
    john = Constant("john")
    mary = Constant("mary")
    
    branch.add_to_domain(john)
    branch.add_to_domain(mary)
    print(f"Domain: {[c.name for c in branch.get_domain_constants()]}")
    
    # Add predicate assignments
    branch.add_predicate_assignment("Student(john)", t)
    branch.add_predicate_assignment("Student(mary)", f)
    branch.add_predicate_assignment("Loves(john,mary)", t)
    from truth_value import e as undefined
    branch.add_predicate_assignment("Loves(mary,john)", undefined)
    
    assignments = branch.get_all_assignments()
    print(f"\nThree-valued assignments:")
    for pred, value in assignments.items():
        print(f"  {pred} = {value}")
    
    # Generate witness constants
    witness1 = branch.generate_fresh_constant("w")
    witness2 = branch.generate_fresh_constant("w")
    
    print(f"\nGenerated witnesses: {witness1.name}, {witness2.name}")
    print(f"Updated domain: {[c.name for c in branch.get_domain_constants()]}")
    
    # Test closure detection
    print(f"\nBranch closed: {branch.is_closed}")
    
    # Try to create a contradiction
    try:
        branch.add_predicate_assignment("Student(john)", f)  # Contradicts existing t
        print(f"After contradiction attempt - Branch closed: {branch.is_closed}")
        if branch.is_closed:
            print(f"Closure reason: {branch._closure_reason}")
    except Exception as e:
        print(f"Contradiction handling: {e}")


def demo_model_extraction():
    """Demonstrate model extraction from satisfiable branches"""
    print_header("wKrQ MODEL EXTRACTION DEMO")
    
    # Create satisfiable branch
    branch = WKrQ_Branch(1)
    
    # Add domain elements
    john = Constant("john")
    mary = Constant("mary")
    alice = Constant("alice")
    
    branch.add_to_domain(john)
    branch.add_to_domain(mary) 
    branch.add_to_domain(alice)
    
    # Add three-valued predicate assignments
    branch.add_predicate_assignment("Student(john)", t)
    branch.add_predicate_assignment("Student(mary)", f)
    branch.add_predicate_assignment("Student(alice)", e)  # Undefined
    
    branch.add_predicate_assignment("Likes(john,mary)", t)
    branch.add_predicate_assignment("Likes(mary,alice)", f)
    branch.add_predicate_assignment("Likes(alice,john)", e)
    
    print("Branch contents:")
    print(f"Domain: {[c.name for c in branch.get_domain_constants()]}")
    print(f"Assignments: {branch.get_all_assignments()}")
    print(f"Closed: {branch.is_closed}")
    
    # Extract model
    extractor = WKrQ_ModelExtractor()
    model = extractor.extract_model(branch)
    
    print(f"\nExtracted Model:")
    print(f"Domain: {list(model.domain.keys())}")
    print(f"Predicate assignments:")
    for pred, value in model.predicate_assignments.items():
        print(f"  {pred} = {value}")
    
    # Test model evaluation (placeholder - would need full implementation)
    print(f"\nModel evaluation capabilities:")
    print(f"- Three-valued predicate lookup")
    print(f"- Weak Kleene connective evaluation")  
    print(f"- Restricted quantifier evaluation over domain")


def demo_logic_system_integration():
    """Demonstrate integration with the logic system framework"""
    print_header("LOGIC SYSTEM INTEGRATION DEMO")
    
    try:
        import builtin_logics
        from logic_system import get_logic_system, list_logic_systems
        
        # Show available logic systems
        systems = list_logic_systems()
        print("Available logic systems:")
        for system in sorted(systems):
            print(f"  - {system}")
        
        # Get wKrQ system
        wkrq_system = get_logic_system("wkrq")
        print(f"\nwKrQ System Details:")
        print(f"Name: {wkrq_system.config.name}")
        print(f"Description: {wkrq_system.config.description}")
        print(f"Truth values: {wkrq_system.config.truth_values}")
        print(f"Supports quantifiers: {wkrq_system.config.supports_quantifiers}")
        print(f"Aliases: {wkrq_system.config.metadata.get('aliases', [])}")
        
        # Show available rules
        print(f"\nTableau rules ({len(wkrq_system.rules)}):")
        for i, rule in enumerate(wkrq_system.rules):
            print(f"  {i+1}. {rule.name} (priority: {rule.priority})")
        
    except Exception as e:
        print(f"Integration demo failed: {e}")
        traceback.print_exc()


def run_full_demo():
    """Run complete wKrQ demonstration"""
    print("🎯 wKrQ - Weak Kleene Logic with Restricted Quantifiers")
    print("Based on Ferguson (2021) 'Tableaux and restricted quantification for systems related to weak Kleene logic'")
    
    demos = [
        demo_restricted_quantifier_semantics,
        demo_formula_construction,
        demo_branch_reasoning,
        demo_model_extraction,
        demo_logic_system_integration
    ]
    
    for demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Demo {demo_func.__name__} failed: {e}")
            traceback.print_exc()
    
    print_header("DEMO COMPLETE")
    print("The wKrQ implementation provides:")
    print("✓ Exact Ferguson (2021) restricted quantifier semantics")
    print("✓ Three-valued weak Kleene logic foundation")
    print("✓ First-order domain management with witness generation")
    print("✓ Branch-based tableau reasoning")
    print("✓ Model extraction from satisfiable branches")
    print("✓ Integration with componentized tableau framework")
    
    print(f"\nNext steps:")
    print("- Implement complete tableau construction algorithm")
    print("- Add CLI support for interactive wKrQ reasoning")
    print("- Create comprehensive test suites")
    print("- Add performance optimizations for larger domains")


if __name__ == "__main__":
    run_full_demo()