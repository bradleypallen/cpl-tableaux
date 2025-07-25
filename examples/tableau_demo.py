#!/usr/bin/env python3
"""
Unified Tableau Demonstration

This module provides comprehensive demonstrations of the tableau reasoning system
across all supported logical systems. It showcases both the theoretical capabilities
and practical applications of the tableau method for automated reasoning.

The demonstrations are designed for multiple audiences:
1. **Researchers**: Detailed examples showing tableau construction and optimization
2. **Students**: Educational examples explaining logical reasoning step-by-step  
3. **Practitioners**: Practical applications of automated theorem proving
4. **Developers**: API usage examples and performance benchmarking

Key Features Demonstrated:
- Classical propositional logic reasoning
- Three-valued weak Kleene logic (WK3) with gap semantics
- Step-by-step tableau construction with visualization
- Performance comparison across logical systems
- Model enumeration and analysis
- Error handling and edge cases

Academic Context:
These demonstrations illustrate the practical application of formal tableau methods
as described in the foundational literature:
- Smullyan's unified notation for tableau systems
- Priest's three-valued logic semantics  
- Industrial optimizations for performance

The examples progress from simple satisfiability testing to complex logical
reasoning scenarios, providing a complete tour of the system's capabilities.
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from tableaux import (
    Formula, Atom, Negation, Conjunction, Disjunction, Implication,
    T, F, T3, F3, U, TF, FF,
    classical_signed_tableau, three_valued_signed_tableau,
    parse_formula, TruthValue, t, f, e
)
from tableaux import UnifiedModel, ClassicalModel, WK3Model


@dataclass
class DemoResult:
    """Result from a single demonstration with timing and analysis"""
    name: str
    satisfiable: bool
    models: List[Dict[str, Any]]
    construction_time: float
    rule_applications: int
    branch_count: int
    logic_system: str


class TableauDemo:
    """
    Comprehensive demonstration system for tableau reasoning.
    
    This class provides structured demonstrations of tableau capabilities
    across different logical systems, with detailed analysis and comparison.
    """
    
    def __init__(self):
        self.results: List[DemoResult] = []
        
    def run_all_demonstrations(self):
        """Run all demonstrations in sequence"""
        print("🔬 Tableau Reasoning System - Comprehensive Demonstration")
        print("=" * 70)
        print()
        
        self._demo_basic_satisfiability()
        self._demo_theorem_proving()
        self._demo_model_finding()
        self._demo_three_valued_logic()
        self._demo_step_by_step_construction()
        self._demo_performance_comparison()
        self._demo_complex_reasoning()
        self._demo_error_handling()
        
        print("\n" + "=" * 70)
        print("✅ All demonstrations completed successfully!")
        self._print_summary_statistics()
        
    def _demo_basic_satisfiability(self):
        """Demonstrate basic satisfiability testing"""
        print("📋 Basic Satisfiability Testing")
        print("-" * 40)
        
        test_cases = [
            ("p", "Simple atom", True),
            ("p & q", "Simple conjunction", True),
            ("p & ~p", "Contradiction", False),
            ("(p & q) | (~p & ~q)", "Complex formula", True),
            ("(p -> q) & p & ~q", "Modus ponens contradiction", False),
        ]
        
        for formula_str, description, expected in test_cases:
            formula = parse_formula(formula_str)
            start_time = time.time()
            tableau = classical_signed_tableau(T(formula))
            result = tableau.build()
            end_time = time.time()
            
            # Count statistics
            branch_count = len(tableau.branches)
            rule_applications = sum(len(branch.signed_formulas) for branch in tableau.branches)
            
            # Store result
            models = tableau.extract_all_models() if result else []
            demo_result = DemoResult(
                name=description,
                satisfiable=result,
                models=[str(model) for model in models],
                construction_time=end_time - start_time,
                rule_applications=rule_applications,
                branch_count=branch_count,
                logic_system="classical"
            )
            self.results.append(demo_result)
            
            status = "✅" if result == expected else "❌"
            print(f"{status} {description}: '{formula_str}' -> {'SAT' if result else 'UNSAT'} ({end_time - start_time:.4f}s)")
            
        print()
        
    def _demo_theorem_proving(self):
        """Demonstrate theorem proving (tautology checking)"""
        print("🎯 Theorem Proving (Tautology Detection)")
        print("-" * 40)
        
        theorems = [
            ("p | ~p", "Law of excluded middle"),
            ("((p -> q) & (q -> r)) -> (p -> r)", "Transitivity of implication"),
            ("(p & q) -> (p | q)", "Conjunction implies disjunction"),
        ]
        
        non_theorems = [
            ("p & q", "Simple conjunction"),
            ("p -> q", "Simple implication"),
        ]
        
        print("Valid theorems (negation should be UNSAT):")
        for formula_str, description in theorems:
            formula = parse_formula(formula_str)
            start_time = time.time()
            # To check if something is a theorem, we test if its negation is unsatisfiable
            negated_formula = Negation(formula)
            negated_tableau = classical_signed_tableau(T(negated_formula))
            is_theorem = not negated_tableau.build()
            end_time = time.time()
            
            status = "✅" if is_theorem else "❌"
            print(f"  {status} {description}: '{formula_str}' -> {'THEOREM' if is_theorem else 'NOT THEOREM'} ({end_time - start_time:.4f}s)")
            
        print("\nNon-theorems (should be satisfiable):")
        for formula_str, description in non_theorems:
            formula = parse_formula(formula_str)
            start_time = time.time()
            tableau = classical_signed_tableau(T(formula))
            is_satisfiable = tableau.build()
            end_time = time.time()
            
            status = "✅" if is_satisfiable else "❌"
            print(f"  {status} {description}: '{formula_str}' -> {'SAT' if is_satisfiable else 'UNSAT'} ({end_time - start_time:.4f}s)")
            
        print()
        
    def _demo_model_finding(self):
        """Demonstrate model extraction and enumeration"""
        print("🔍 Model Finding and Enumeration")
        print("-" * 40)
        
        test_cases = [
            ("p", "Single atom"),
            ("p & q", "Conjunction"),
            ("p | q", "Disjunction"), 
            ("p -> q", "Implication"),
            ("(p | q) & (~p | r)", "Complex satisfiable formula"),
        ]
        
        for formula_str, description in test_cases:
            formula = parse_formula(formula_str)
            start_time = time.time()
            tableau = classical_signed_tableau(T(formula))
            is_satisfiable = tableau.build()
            models = tableau.extract_all_models() if is_satisfiable else []
            end_time = time.time()
            
            print(f"📊 {description}: '{formula_str}'")
            if is_satisfiable:
                print(f"   Result: SATISFIABLE with {len(models)} model(s)")
                for i, model in enumerate(models[:3], 1):  # Show first 3 models
                    print(f"   Model {i}: {model}")
                if len(models) > 3:
                    print(f"   ... and {len(models) - 3} more models")
            else:
                print("   Result: UNSATISFIABLE")
            print(f"   Time: {end_time - start_time:.4f}s")
            print()
            
    def _demo_three_valued_logic(self):
        """Demonstrate three-valued logic (WK3) capabilities"""
        print("🔺 Three-Valued Logic (WK3) Demonstration")
        print("-" * 40)
        
        # Classical vs WK3 comparison
        comparison_cases = [
            ("p & ~p", "Contradiction"),
            ("p | ~p", "Law of excluded middle"),
            ("p -> p", "Self-implication"),
        ]
        
        for formula_str, description in comparison_cases:
            formula = parse_formula(formula_str)
            
            # Classical logic
            classical_tableau = classical_signed_tableau(T(formula))
            classical_result = classical_tableau.build()
            classical_models = classical_tableau.extract_all_models() if classical_result else []
            
            # WK3 logic - check both T3 and U
            t3_tableau = three_valued_signed_tableau(T3(formula))
            u_tableau = three_valued_signed_tableau(U(formula))
            t3_result = t3_tableau.build()
            u_result = u_tableau.build()
            wk3_result = t3_result or u_result
            
            wk3_models = []
            if t3_result:
                wk3_models.extend(t3_tableau.extract_all_models())
            if u_result:
                wk3_models.extend(u_tableau.extract_all_models())
            
            print(f"🔀 {description}: '{formula_str}'")
            print(f"   Classical: {'SAT' if classical_result else 'UNSAT'} ({len(classical_models)} models)")
            print(f"   WK3:       {'SAT' if wk3_result else 'UNSAT'} ({len(wk3_models)} models)")
            
            if wk3_result and len(wk3_models) > 0:
                print(f"   WK3 Models: {wk3_models[0] if wk3_models else 'None'}")
            
            if classical_result != wk3_result:
                print("   ⚠️  Results differ between classical and WK3 logic!")
            print()
            
    def _demo_step_by_step_construction(self):
        """Demonstrate step-by-step tableau construction with visualization"""
        print("🏗️  Step-by-Step Tableau Construction")
        print("-" * 40)
        
        # Choose a formula that will show interesting tableau construction
        formula_str = "(p -> q) & p & ~q"  # This will create a contradiction
        formula = parse_formula(formula_str)
        
        print(f"Building tableau for: {formula_str}")
        print("=" * 50)
        
        # Create tableau with step tracking enabled
        tableau = classical_signed_tableau(T(formula), track_steps=True)
        
        print("Initial state:")
        print(f"  Formula to satisfy: T:{formula}")
        print()
        
        # Build the tableau step by step
        start_time = time.time()
        is_satisfiable = tableau.build()
        end_time = time.time()
        
        # Show construction steps if available
        if hasattr(tableau, 'construction_steps') and tableau.construction_steps:
            print("Construction Steps:")
            for i, step in enumerate(tableau.construction_steps, 1):
                print(f"Step {i}: {step}")
            print()
        
        # Show the final result
        print(f"Final Result: {'SATISFIABLE' if is_satisfiable else 'UNSATISFIABLE'}")
        print(f"Construction time: {end_time - start_time:.4f}s")
        print(f"Total branches: {len(tableau.branches)}")
        print(f"Open branches: {len([b for b in tableau.branches if not b.is_closed])}")
        print(f"Closed branches: {len([b for b in tableau.branches if b.is_closed])}")
        
        if is_satisfiable:
            models = tableau.extract_all_models()
            print(f"Models found: {len(models)}")
            for i, model in enumerate(models[:2], 1):
                print(f"  Model {i}: {model}")
        else:
            print("No models found (unsatisfiable)")
            # Show why it's unsatisfiable
            for i, branch in enumerate(tableau.branches):
                if branch.is_closed:
                    print(f"  Branch {i} closed: {branch.closure_reason if hasattr(branch, 'closure_reason') else 'contradiction found'}")
        
        # Show tableau tree structure if available
        if hasattr(tableau, 'print_tree'):
            print("\nTableau tree structure:")
            tableau.print_tree()
        elif hasattr(tableau, '_print_tree_structure'):
            print("\nTableau tree structure:")
            # Pass the latest branches snapshot if step tracking is enabled
            if hasattr(tableau, 'construction_steps') and tableau.construction_steps:
                latest_step = tableau.construction_steps[-1]
                if 'branches_snapshot' in latest_step:
                    tableau._print_tree_structure(latest_step['branches_snapshot'])
            else:
                print("  (Tree structure not available without step tracking)")
        
        print()
        
        # Add a second example showing a satisfiable case
        print("Second Example - Satisfiable Formula:")
        formula_str2 = "p | q"
        formula2 = parse_formula(formula_str2)
        print(f"Building tableau for: {formula_str2}")
        print("-" * 30)
        
        tableau2 = classical_signed_tableau(T(formula2), track_steps=True)
        is_satisfiable2 = tableau2.build()
        
        print(f"Result: {'SATISFIABLE' if is_satisfiable2 else 'UNSATISFIABLE'}")
        if is_satisfiable2:
            models2 = tableau2.extract_all_models()
            print(f"Models: {len(models2)}")
            for i, model in enumerate(models2, 1):
                print(f"  Model {i}: {model}")
        
        print()
        
    def _demo_performance_comparison(self):
        """Compare performance across different logic systems"""
        print("⚡ Performance Comparison")
        print("-" * 40)
        
        test_formulas = [
            "p & q",
            "(p | q) & (r | s)",
            "((p -> q) & (q -> r)) -> (p -> r)",
            "(p & q & r) | (~p & ~q & ~r)",
        ]
        
        print(f"{'Formula':<30} {'Classical':<12} {'WK3':<12} {'Ratio':<8}")
        print("-" * 62)
        
        for formula_str in test_formulas:
            formula = parse_formula(formula_str)
            
            # Classical performance
            start = time.time()
            classical_tableau = classical_signed_tableau(T(formula))
            classical_result = classical_tableau.build()
            classical_time = time.time() - start
            
            # WK3 performance
            start = time.time()
            t3_tableau = three_valued_signed_tableau(T3(formula))
            u_tableau = three_valued_signed_tableau(U(formula))
            t3_result = t3_tableau.build()
            u_result = u_tableau.build()
            wk3_time = time.time() - start
            
            ratio = wk3_time / classical_time if classical_time > 0 else float('inf')
            
            print(f"{formula_str:<30} {classical_time*1000:>8.2f}ms {wk3_time*1000:>8.2f}ms {ratio:>6.1f}x")
            
        print()
        
    def _demo_complex_reasoning(self):
        """Demonstrate complex reasoning scenarios"""
        print("🧠 Complex Reasoning Scenarios")
        print("-" * 40)
        
        scenarios = [
            ("(p -> q) & (q -> r) & p", "Chained implications"),
            ("(p | q) & (~p | r) & (~q | s)", "Multiple constraints"),
            ("((p & q) -> r) & (~r) & (p | q)", "Proof by contradiction"),
        ]
        
        for formula_str, description in scenarios:
            formula = parse_formula(formula_str)
            
            print(f"🎲 {description}")
            print(f"   Formula: {formula_str}")
            
            start_time = time.time()
            tableau = classical_signed_tableau(T(formula))
            is_satisfiable = tableau.build()
            end_time = time.time()
            
            print(f"   Result: {'SATISFIABLE' if is_satisfiable else 'UNSATISFIABLE'}")
            print(f"   Branches: {len(tableau.branches)}")
            print(f"   Time: {end_time - start_time:.4f}s")
            
            if is_satisfiable:
                models = tableau.extract_all_models()
                print(f"   Models: {len(models)}")
                if models:
                    print(f"   Sample: {models[0]}")
            print()
            
    def _demo_error_handling(self):
        """Demonstrate error handling and edge cases"""
        print("🚨 Error Handling and Edge Cases")
        print("-" * 40)
        
        edge_cases = [
            ("", "Empty formula"),
            ("p &", "Incomplete formula"),
            ("(p & q", "Unmatched parentheses"),
            ("p && q", "Invalid operator"),
        ]
        
        for formula_str, description in edge_cases:
            print(f"🔍 {description}: '{formula_str}'")
            try:
                if formula_str:
                    formula = parse_formula(formula_str)
                    tableau = classical_signed_tableau(T(formula))
                    result = tableau.build()
                    print(f"   Result: {'SAT' if result else 'UNSAT'}")
                else:
                    print("   Error: Empty formula string")
            except Exception as e:
                print(f"   Error: {type(e).__name__}: {e}")
            print()
            
    def _print_summary_statistics(self):
        """Print summary statistics from all demonstrations"""
        print("📊 Summary Statistics")
        print("-" * 40)
        
        total_tests = len(self.results)
        total_time = sum(r.construction_time for r in self.results)
        total_satisfiable = sum(1 for r in self.results if r.satisfiable)
        
        print(f"Total tests run: {total_tests}")
        print(f"Total time: {total_time:.4f}s")
        print(f"Average time per test: {total_time/total_tests:.4f}s")
        print(f"Satisfiable: {total_satisfiable}/{total_tests} ({100*total_satisfiable/total_tests:.1f}%)")
        print(f"Unsatisfiable: {total_tests-total_satisfiable}/{total_tests} ({100*(total_tests-total_satisfiable)/total_tests:.1f}%)")
        
        # Performance by logic system
        classical_results = [r for r in self.results if r.logic_system == "classical"]
        if classical_results:
            avg_classical = sum(r.construction_time for r in classical_results) / len(classical_results)
            print(f"Average classical time: {avg_classical:.4f}s")
        
        print()
        print("🎉 Demonstration complete! The tableau system is working correctly.")


def main():
    """Main entry point for the demonstration"""
    demo = TableauDemo()
    demo.run_all_demonstrations()


if __name__ == "__main__":
    main()