#!/usr/bin/env python3
"""Tutorial 4: Building a SAT Solver"""

from tableau_core import *
import time

class TableauSATSolver:
    """SAT solver using tableau method."""
    
    def __init__(self, logic_system="classical"):
        self.logic_system = logic_system
        self.statistics = {}
    
    def solve(self, formula):
        """
        Solve satisfiability problem.
        
        Returns:
            dict: {
                'satisfiable': bool,
                'models': list,
                'statistics': dict
            }
        """
        start_time = time.time()
        
        if self.logic_system == "classical":
            engine = classical_signed_tableau(T(formula))
            satisfiable = engine.build()
            models = engine.extract_all_models() if satisfiable else []
            stats = engine.get_statistics()
        elif self.logic_system == "wk3":
            # Try WK3 tableau - pass as list to be safe
            from wk3_tableau import WK3Tableau
            wk3_tableau = WK3Tableau([formula])
            satisfiable = wk3_tableau.build()
            models = wk3_tableau.extract_all_models() if satisfiable else []
            stats = {'rule_applications': 0}  # WK3 doesn't track detailed stats
        else:
            raise ValueError(f"Unknown logic system: {self.logic_system}")
        
        end_time = time.time()
        
        result = {
            'satisfiable': satisfiable,
            'models': models,
            'statistics': {
                'solve_time': end_time - start_time,
                'num_models': len(models),
                **stats
            }
        }
        
        return result
    
    def solve_batch(self, formulas):
        """Solve multiple formulas and return summary."""
        results = []
        
        print(f"Solving {len(formulas)} formulas using {self.logic_system} logic...\n")
        
        for i, formula in enumerate(formulas):
            print(f"Problem {i+1}: {formula}")
            result = self.solve(formula)
            results.append(result)
            
            print(f"  Result: {'SAT' if result['satisfiable'] else 'UNSAT'}")
            print(f"  Models: {result['statistics']['num_models']}")
            print(f"  Time: {result['statistics']['solve_time']:.4f}s")
            
            if 'rule_applications' in result['statistics']:
                print(f"  Rule applications: {result['statistics']['rule_applications']}")
            print()
        
        return results

def demo_sat_solver():
    """Demonstrate the SAT solver on various problems."""
    
    print("=== TABLEAU SAT SOLVER DEMO ===\n")
    
    # Create test problems
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    test_problems = [
        # Easy satisfiable
        p,
        Conjunction(p, q),
        Disjunction(p, q),
        
        # Easy unsatisfiable  
        Conjunction(p, Negation(p)),
        
        # Medium complexity
        Conjunction(
            Disjunction(p, q),
            Disjunction(Negation(p), r)
        ),
        
        # Hard problem (should be unsatisfiable)
        Conjunction(
            Conjunction(Implication(p, q), p),
            Negation(q)
        ),
        
        # Tautology test
        Disjunction(p, Negation(p)),
    ]
    
    # Test with classical logic
    print("=== CLASSICAL LOGIC RESULTS ===")
    solver = TableauSATSolver("classical")
    classical_results = solver.solve_batch(test_problems)
    
    print("\n=== WK3 LOGIC RESULTS ===")
    solver = TableauSATSolver("wk3")
    wk3_results = solver.solve_batch(test_problems)
    
    # Compare results
    print("=== COMPARISON ===")
    print("Problem | Classical | WK3")
    print("--------|-----------|----")
    
    for i, formula in enumerate(test_problems):
        classical_sat = "SAT" if classical_results[i]['satisfiable'] else "UNSAT"
        wk3_sat = "SAT" if wk3_results[i]['satisfiable'] else "UNSAT"
        
        different = "***" if classical_sat != wk3_sat else ""
        print(f"{i+1:7} | {classical_sat:9} | {wk3_sat:3} {different}")

if __name__ == "__main__":
    demo_sat_solver()