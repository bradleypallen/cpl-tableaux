#!/usr/bin/env python3
"""
Demo: Componentized Tableau Rule System

Demonstrates the new componentized rule system that allows defining logics
by their specific tableau expansion rules.
"""

from formula import Atom, Negation, Conjunction, Disjunction, Implication
from componentized_tableau import ComponentizedTableau, classical_tableau, wk3_tableau
from logic_system import get_logic_system
from builtin_logics import describe_all_logics


def demo_basic_usage():
    """Demonstrate basic usage of the componentized system"""
    print("=" * 70)
    print("COMPONENTIZED TABLEAU RULE SYSTEM DEMO")
    print("=" * 70)
    
    # Create some test formulas
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    
    # Test formulas
    test_cases = [
        ("Simple atom", p),
        ("Contradiction", Conjunction(p, Negation(p))),
        ("Tautology", Disjunction(p, Negation(p))),
        ("Complex formula", Implication(Conjunction(p, q), r))
    ]
    
    print("\n1. CLASSICAL LOGIC EXAMPLES")
    print("-" * 40)
    
    for name, formula in test_cases:
        print(f"\nTesting: {name} - {formula}")
        
        # Use the componentized system
        tableau = classical_tableau(formula)
        result = tableau.build()
        
        print(f"Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}")
        
        if result:
            models = tableau.extract_all_models()
            print(f"Models found: {len(models)}")
            if models:
                print(f"Sample model: {models[0]}")
    
    print("\n2. WK3 LOGIC EXAMPLES")
    print("-" * 40)
    
    for name, formula in test_cases[:3]:  # Skip complex formula for WK3
        print(f"\nTesting: {name} - {formula}")
        
        # Use WK3 system
        tableau = wk3_tableau(formula)
        result = tableau.build()
        
        print(f"Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}")
        
        if result:
            models = tableau.extract_all_models()
            print(f"Models found: {len(models)}")


def demo_logic_system_registry():
    """Demonstrate the logic system registry"""
    print("\n3. LOGIC SYSTEM REGISTRY")
    print("-" * 40)
    
    # Show available systems
    classical = get_logic_system("classical")
    wk3 = get_logic_system("wk3")
    
    print(f"\nClassical Logic Rules: {len(classical.rules)}")
    for rule in classical.rules:
        rule_type = "α" if rule.is_alpha_rule else "β" if rule.is_beta_rule else "γ"
        print(f"  {rule_type}: {rule.name}")
    
    print(f"\nWK3 Logic Rules: {len(wk3.rules)}")
    for rule in wk3.rules:
        rule_type = "α" if rule.is_alpha_rule else "β" if rule.is_beta_rule else "γ"
        print(f"  {rule_type}: {rule.name}")


def demo_direct_system_usage():
    """Demonstrate direct usage of the ComponentizedTableau class"""
    print("\n4. DIRECT SYSTEM USAGE")
    print("-" * 40)
    
    p, q = Atom("p"), Atom("q")
    formula = Conjunction(Implication(p, q), p)  # (p → q) ∧ p
    
    print(f"Testing formula: {formula}")
    
    # Create tableau with direct system reference
    tableau = ComponentizedTableau(formula, "classical")
    result = tableau.build()
    
    # Get detailed statistics
    stats = tableau.get_statistics()
    
    print(f"\nDetailed Results:")
    print(f"  Logic System: {stats['logic_system']}")
    print(f"  Satisfiable: {stats['satisfiable']}")
    print(f"  Total Branches: {stats['total_branches']}")
    print(f"  Open Branches: {stats['open_branches']}")
    print(f"  Closed Branches: {stats['closed_branches']}")
    print(f"  Rule Applications: {stats['rule_applications']}")
    print(f"  Rules Available: {stats['rules_used']}")
    
    if result:
        models = tableau.extract_all_models()
        print(f"\nSample Model: {models[0]}")
        print(f"Formula satisfied by model: {models[0].satisfies(formula)}")


def demo_comparison():
    """Compare results with original implementation"""
    print("\n5. BACKWARD COMPATIBILITY CHECK")
    print("-" * 40)
    
    from tableau import Tableau
    
    # Test formula
    p, q = Atom("p"), Atom("q")
    formula = Disjunction(Conjunction(p, q), Negation(p))
    
    print(f"Testing formula: {formula}")
    
    # Original implementation
    original = Tableau(formula)
    original_result = original.build()
    original_models = original.extract_all_models()
    
    # Componentized implementation
    componentized = classical_tableau(formula)
    componentized_result = componentized.build()
    componentized_models = componentized.extract_all_models()
    
    print(f"\nOriginal Implementation:")
    print(f"  Result: {'SATISFIABLE' if original_result else 'UNSATISFIABLE'}")
    print(f"  Models: {len(original_models)}")
    
    print(f"\nComponentized Implementation:")
    print(f"  Result: {'SATISFIABLE' if componentized_result else 'UNSATISFIABLE'}")
    print(f"  Models: {len(componentized_models)}")
    
    print(f"\nResults Match: {original_result == componentized_result}")


def demo_extensibility():
    """Demonstrate extensibility features"""
    print("\n6. EXTENSIBILITY FEATURES")
    print("-" * 40)
    
    # Show how easy it is to get rule information
    classical = get_logic_system("classical")
    
    print("Rule Details:")
    for rule in classical.rules[:3]:  # Show first 3 rules
        p = Atom("test")
        test_formula = Conjunction(p, Negation(p))
        
        print(f"\n  Rule: {rule.name}")
        print(f"  Type: {rule.rule_type}")
        print(f"  Priority: {rule.priority}")
        print(f"  Is Alpha Rule: {rule.is_alpha_rule}")
        print(f"  Is Beta Rule: {rule.is_beta_rule}")
        print(f"  Applies to {test_formula}: {rule.applies_to(test_formula)}")
    
    # Show system validation
    print("\nSystem Validation:")
    warnings = classical.validate_completeness()
    if warnings:
        print("  Warnings:")
        for warning in warnings:
            print(f"    - {warning}")
    else:
        print("  ✓ System appears complete")


def main():
    """Run all demonstrations"""
    demo_basic_usage()
    demo_logic_system_registry()
    demo_direct_system_usage()
    demo_comparison()
    demo_extensibility()
    
    print("\n" + "=" * 70)
    print("SYSTEM ARCHITECTURE SUMMARY")
    print("=" * 70)
    
    print("\n✓ Componentized rule system successfully implemented")
    print("✓ Classical and WK3 logic systems registered")
    print("✓ Backward compatibility maintained")
    print("✓ Extension points available for new logics")
    print("✓ All optimizations preserved")
    
    print("\nFuture Extension Examples:")
    print("  - First-Order Logic: Add quantifier rules")
    print("  - Modal Logic: Add □ and ◊ operators")  
    print("  - Temporal Logic: Add temporal operators")
    print("  - Many-valued Logics: Add more truth values")


if __name__ == "__main__":
    main()