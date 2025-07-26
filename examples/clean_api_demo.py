#!/usr/bin/env python3
"""
Demonstration of the Clean Modern Tableau API

This example shows how much simpler and more natural the new API is
compared to the old backward-compatibility layer.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tableaux import LogicSystem

def main():
    print("=== Clean Modern Tableau API Demo ===\n")
    
    # Create logic systems with simple factory methods
    print("1. Creating Logic Systems")
    classical = LogicSystem.classical()
    weak_kleene = LogicSystem.weak_kleene()
    wkrq = LogicSystem.wkrq()
    print(f"   ✓ Classical: {classical.name}")
    print(f"   ✓ Weak Kleene: {weak_kleene.name}")
    print(f"   ✓ wKrQ: {wkrq.name}")
    
    # Natural formula construction with operator overloading
    print("\n2. Natural Formula Construction")
    p, q, r = classical.atoms('p', 'q', 'r')
    print(f"   Atoms: p={p}, q={q}, r={r}")
    
    # Use natural Python operators
    conjunction = p & q
    disjunction = p | q  
    implication = p.implies(q)
    negation = ~p
    complex_formula = p.implies(q) & (p & ~q)
    
    print(f"   Conjunction: {conjunction}")
    print(f"   Disjunction: {disjunction}")
    print(f"   Implication: {implication}")
    print(f"   Negation: {negation}")
    print(f"   Complex: {complex_formula}")
    
    # Direct solving with clean result objects
    print("\n3. Direct Solving")
    
    # Test a tautology
    tautology = p | ~p
    result = classical.solve(tautology)
    print(f"   Tautology {tautology}:")
    print(f"     Satisfiable: {result.satisfiable}")
    print(f"     Models: {result.model_count}")
    
    # Test a contradiction
    contradiction = p & ~p
    result = classical.solve(contradiction)
    print(f"   Contradiction {contradiction}:")
    print(f"     Satisfiable: {result.satisfiable}")
    print(f"     Models: {result.model_count}")
    
    # Test a contingency
    contingency = p.implies(q)
    result = classical.solve(contingency)
    print(f"   Contingency {contingency}:")
    print(f"     Satisfiable: {result.satisfiable}")
    print(f"     Models: {result.model_count}")
    
    # Convenience methods
    print("\n4. Convenience Methods")
    print(f"   {tautology} is valid: {classical.valid(tautology)}")
    print(f"   {contradiction} is unsatisfiable: {classical.unsatisfiable(contradiction)}")
    print(f"   {contingency} is satisfiable: {classical.satisfiable(contingency)}")
    
    # Entailment checking
    premises = [p.implies(q), p]
    conclusion = q
    entails = classical.entails(premises, conclusion)
    print(f"   {premises} entails {conclusion}: {entails}")
    
    # Multi-logic comparison
    print("\n5. Multi-Logic Comparison")
    wk_p, wk_q = weak_kleene.atoms('p', 'q')
    wkrq_p, wkrq_q = wkrq.atoms('p', 'q')
    
    # Test law of excluded middle in different logics
    lem_classical = p | ~p
    lem_wk = wk_p | ~wk_p  
    lem_wkrq = wkrq_p | ~wkrq_p
    
    print(f"   Law of Excluded Middle:")
    print(f"     Classical: valid={classical.valid(lem_classical)}")
    print(f"     Weak Kleene: valid={weak_kleene.valid(lem_wk)}")
    print(f"     wKrQ: valid={wkrq.valid(lem_wkrq)}")
    
    # Step tracking for debugging
    print("\n6. Step Tracking")
    result = classical.solve(complex_formula, track_steps=True)
    print(f"   Formula: {complex_formula}")
    print(f"   Steps tracked: {len(result.steps) if result.steps else 0}")
    print(f"   Satisfiable: {result.satisfiable}")
    
    if result.tableau:
        print("\n   Tableau construction:")
        tree = result.tableau.print_tree(show_steps=True)
        # Show just first few lines
        lines = tree.split('\n')[:15]
        for line in lines:
            print(f"   {line}")
        if len(tree.split('\n')) > 15:
            print("   ...")
    
    print("\n=== Demo Complete ===")
    print("The new API is much cleaner and more intuitive!")


if __name__ == "__main__":
    main()