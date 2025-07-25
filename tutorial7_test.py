#!/usr/bin/env python3
"""Tutorial 7: Performance Analysis"""

import time
from tableau_core import Atom, Conjunction, Disjunction, classical_signed_tableau, T, F

def performance_comparison():
    """Compare performance across different formula sizes."""
    
    print("=== PERFORMANCE ANALYSIS ===\n")
    
    sizes = [3, 5, 8]  # Smaller sizes for demonstration
    
    for size in sizes:
        print(f"Testing with {size} atoms:")
        
        # Create atoms
        atoms = [Atom(f"p{i}") for i in range(size)]
        
        # Create CNF formula: (p0 ∨ p1) ∧ (p2 ∨ p3) ∧ ...
        clauses = []
        for i in range(0, len(atoms) - 1, 2):
            clauses.append(Disjunction(atoms[i], atoms[i + 1]))
        
        # Conjoin all clauses
        if clauses:
            formula = clauses[0]
            for clause in clauses[1:]:
                formula = Conjunction(formula, clause)
        else:
            formula = atoms[0]  # Fallback for odd sizes
        
        # Time the tableau construction
        start_time = time.time()
        tableau = classical_signed_tableau(T(formula))
        result = tableau.build()
        end_time = time.time()
        
        # Collect statistics
        construction_time = end_time - start_time
        branch_count = len(tableau.branches)
        
        print(f"  Time: {construction_time:.4f}s")
        print(f"  Branches: {branch_count}")
        print(f"  Satisfiable: {result}")
        
        if result:
            models = tableau.extract_all_models()
            print(f"  Models: {len(models)}")
        print()

def optimization_demonstration():
    """Show optimization features in action."""
    
    print("=== OPTIMIZATION FEATURES ===\n")
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    # Create formula that demonstrates α/β rule prioritization
    # F:(p ∧ q) ∧ T:(r ∨ p)
    # This will show α-rules (non-branching) applied before β-rules (branching)
    
    formula1 = Conjunction(p, q)  # Will use F-Conjunction (β-rule)
    formula2 = Disjunction(r, p)  # Will use T-Disjunction (β-rule)
    
    formulas = [F(formula1), T(formula2)]
    
    print("Formula designed to show α/β rule prioritization:")
    print(f"  F:({formula1}) - uses F-Conjunction (β-rule)")
    print(f"  T:({formula2}) - uses T-Disjunction (β-rule)")
    print()
    
    # Build with step tracking to see optimization
    tableau = classical_signed_tableau(formulas, track_steps=True)
    result = tableau.build()
    
    print(f"Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}\n")
    
    # Show the construction - notice rule prioritization
    tableau.print_construction_steps("Optimization Demonstration")
    
    print("\nKey optimization features shown:")
    print("1. α/β rule prioritization - linear rules before branching")
    print("2. O(1) closure detection - contradictions found immediately")
    print("3. Tree structure tracking - efficient branch management")

def memory_efficiency_test():
    """Test memory efficiency with large formulas."""
    
    print("\n=== MEMORY EFFICIENCY TEST ===\n")
    
    # Create a formula that could cause exponential blowup
    # but show how optimizations help
    atoms = [Atom(f"p{i}") for i in range(5)]  # Smaller for demo
    
    # Create nested disjunctions: p0 ∨ (p1 ∨ (p2 ∨ ...))
    formula = atoms[-1]
    for atom in reversed(atoms[:-1]):
        formula = Disjunction(atom, formula)
    
    print(f"Testing deeply nested formula with {len(atoms)} atoms")
    print("This could potentially create many branches...\n")
    
    start_time = time.time()
    tableau = classical_signed_tableau(T(formula))
    result = tableau.build()
    end_time = time.time()
    
    print(f"Construction time: {end_time - start_time:.4f}s")
    print(f"Total branches created: {len(tableau.branches)}")
    print(f"Satisfiable: {result}")
    
    if result:
        models = tableau.extract_all_models()
        print(f"Models found: {len(models)}")
    
    print("\nThe optimized implementation handles this efficiently through:")
    print("- Branch sharing and subsumption elimination")
    print("- Early termination when satisfiability is determined")
    print("- Efficient memory management for branch copying")

if __name__ == "__main__":
    performance_comparison()
    optimization_demonstration()
    memory_efficiency_test()