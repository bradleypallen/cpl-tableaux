#!/usr/bin/env python3
"""Tutorial 6: Performance Optimization"""

from tableau_core import *
import time
import sys

def measure_performance(formula, description=""):
    """Measure tableau construction performance"""
    print(f"\n=== PERFORMANCE TEST: {description} ===")
    print(f"Formula: {formula}")
    
    # Measure construction time
    start_time = time.time()
    tableau = classical_signed_tableau(T(formula))
    build_result = tableau.build()
    end_time = time.time()
    
    construction_time = end_time - start_time
    
    # Get statistics
    stats = tableau.get_statistics()
    
    print(f"Result: {'SAT' if build_result else 'UNSAT'}")
    print(f"Construction time: {construction_time:.4f} seconds")
    print(f"Rule applications: {stats.get('rule_applications', 0)}")
    print(f"Total branches: {stats.get('total_branches', 0)}")
    
    # Measure model extraction time if satisfiable
    if build_result:
        start_time = time.time()
        models = tableau.extract_all_models()
        end_time = time.time()
        
        extraction_time = end_time - start_time
        print(f"Model extraction time: {extraction_time:.4f} seconds")
        print(f"Models found: {len(models)}")
    
    return construction_time, stats

def demonstrate_performance_characteristics():
    """Show how formula structure affects performance"""
    
    p = Atom("p")
    q = Atom("q") 
    r = Atom("r")
    s = Atom("s")
    
    # Simple formula - fast
    simple = Conjunction(p, q)
    measure_performance(simple, "Simple conjunction")
    
    # Medium complexity - moderate performance
    medium = Conjunction(
        Disjunction(p, q),
        Disjunction(Negation(p), r)
    )
    measure_performance(medium, "Medium complexity")
    
    # High branching factor - slower
    high_branching = Conjunction(
        Disjunction(Disjunction(p, q), Disjunction(r, s)),
        Conjunction(
            Disjunction(Negation(p), Negation(q)),
            Disjunction(Negation(r), Negation(s))
        )
    )
    measure_performance(high_branching, "High branching factor")
    
    # Deep nesting - can be expensive
    deep_nesting = p
    for i in range(5):
        deep_nesting = Implication(deep_nesting, Conjunction(p, q))
    measure_performance(deep_nesting, "Deep nesting")

if __name__ == "__main__":
    demonstrate_performance_characteristics()