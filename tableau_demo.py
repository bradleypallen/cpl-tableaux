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
- Ferguson's wKrQ system with epistemic uncertainty
- Performance comparison across logical systems
- Model enumeration and analysis
- Error handling and edge cases

Academic Context:
These demonstrations illustrate the practical application of formal tableau methods
as described in the foundational literature:
- Smullyan's unified notation for tableau systems
- Priest's three-valued logic semantics  
- Ferguson's restricted quantification methods
- Industrial optimizations for performance

The examples progress from simple satisfiability testing to complex logical
reasoning scenarios, providing a complete tour of the system's capabilities.
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from tableau_core import (
    Formula, Atom, Negation, Conjunction, Disjunction, Implication,
    SignedFormula, ClassicalSign, ThreeValuedSign, WkrqSign,
    create_signed_formula, parse_formula, TruthValue, t, f, e
)
from tableau_engine import TableauEngine, TableauStatistics
from inference_api import (
    TableauInference, InferenceResult, LogicSystem,
    is_satisfiable, is_theorem, find_models, analyze_formula
)


@dataclass
class DemoResult:
    """Result from a single demonstration with timing and analysis"""
    name: str
    satisfiable: bool
    models: List[Dict[str, Any]]
    construction_time: float
    rule_applications: int
    branch_count: int
    logic_system: LogicSystem


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
        self._demo_wkrq_epistemic_logic()
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
            start_time = time.time()
            result = is_satisfiable(formula_str)
            end_time = time.time()
            
            status = "✅" if result == expected else "❌"
            print(f"{status} {description}: '{formula_str}' -> {result} ({end_time - start_time:.4f}s)")
            
        print()
        
    def _demo_theorem_proving(self):
        """Demonstrate theorem proving (tautology checking)"""
        print("🎯 Theorem Proving (Tautology Detection)")
        print("-" * 40)
        
        theorems = [
            ("p | ~p", "Law of excluded middle"),
            ("(p -> q) <-> (~q -> ~p)", "Contraposition equivalence"),
            ("((p -> q) & (q -> r)) -> (p -> r)", "Transitivity of implication"),
            ("(p & q) -> (p | q)", "Conjunction implies disjunction"),
        ]
        
        non_theorems = [
            ("p & q", "Simple conjunction"),
            ("p -> q", "Simple implication"),
        ]
        
        print("Valid theorems:")
        for formula_str, description in theorems:
            start_time = time.time()
            result = is_theorem(formula_str)
            end_time = time.time()
            
            status = "✅" if result else "❌"
            print(f"  {status} {description}: '{formula_str}' -> {result} ({end_time - start_time:.4f}s)")
            
        print("\nNon-theorems (should be False):")
        for formula_str, description in non_theorems:
            start_time = time.time()
            result = is_theorem(formula_str)
            end_time = time.time()
            
            status = "✅" if not result else "❌"
            print(f"  {status} {description}: '{formula_str}' -> {result} ({end_time - start_time:.4f}s)")
            
        print()
        
    def _demo_model_finding(self):
        """Demonstrate model enumeration"""
        print("🔍 Model Finding and Enumeration")
        print("-" * 40)
        
        formulas = [
            ("p", "Single atom"),
            ("p | q", "Disjunction"),
            ("p -> q", "Implication"),
            ("(p & q) | (~p & ~q)", "Exclusive cases"),
        ]
        
        for formula_str, description in formulas:
            models = find_models(formula_str)
            print(f"{description}: '{formula_str}'")
            print(f"  Found {len(models)} model(s):")
            
            for i, model in enumerate(models, 1):
                assignments = [f"{atom}={value}" for atom, value in sorted(model.items())]
                print(f"    Model {i}: {{{', '.join(assignments)}}}")
                
            print()
            
    def _demo_three_valued_logic(self):
        """Demonstrate three-valued weak Kleene logic"""
        print("🔬 Three-Valued Weak Kleene Logic (WK3)")
        print("-" * 40)
        
        # Create three-valued inference engine
        wk3_inference = TableauInference(LogicSystem.THREE_VALUED)
        
        test_cases = [
            ("p | ~p", "Law of excluded middle in WK3"),
            ("p & ~p", "Law of non-contradiction in WK3"),
            ("(p -> q) -> ((~p -> q) -> q)", "Complex three-valued reasoning"),
        ]
        
        for formula_str, description in test_cases:
            print(f"{description}: '{formula_str}'")
            
            # Test satisfiability
            satisfiable = wk3_inference.is_satisfiable(formula_str)
            print(f"  Satisfiable: {satisfiable}")
            
            # Find models
            models = wk3_inference.get_models(formula_str)
            print(f"  Models ({len(models)}):")
            for i, model in enumerate(models, 1):
                assignments = [f"{atom}={value}" for atom, value in sorted(model.items())]
                print(f"    Model {i}: {{{', '.join(assignments)}}}")
                
            print()
            
    def _demo_wkrq_epistemic_logic(self):
        """Demonstrate Ferguson's wKrQ epistemic logic system"""
        print("🧠 Ferguson's wKrQ Epistemic Logic")
        print("-" * 40)
        
        # Note: This demonstrates the conceptual framework
        # Full wKrQ implementation would require additional parser support
        print("wKrQ System Features:")
        print("  • T: Definitely true")
        print("  • F: Definitely false") 
        print("  • M: May be true (epistemic possibility)")
        print("  • N: Need not be true (epistemic necessity negation)")
        print()
        
        print("Example wKrQ reasoning patterns:")
        print("  T:p ∧ F:p → Contradiction (classical contradiction)")
        print("  M:p ∧ N:p → Satisfiable (epistemic uncertainty)")
        print("  T:(p ∧ q) → T:p, T:q (definite conjunction)")
        print("  M:(p ∨ q) → M:p ∨ M:q (epistemic disjunction)")
        print()
        
        # Demonstrate with classical formulas that would have wKrQ interpretations
        classical_inference = TableauInference(LogicSystem.CLASSICAL)
        
        wkrq_examples = [
            ("p", "Atomic proposition (could be M:p or N:p in wKrQ)"),
            ("p & q", "Conjunction (definite vs epistemic uncertainty)"),
            ("p | q", "Disjunction (epistemic possibility)"),
        ]
        
        for formula_str, description in wkrq_examples:
            result = classical_inference.analyze_inference(formula_str)
            print(f"{description}: '{formula_str}'")
            print(f"  Classical result: {result.get_model_summary()}")
            print(f"  wKrQ interpretation: Would support epistemic signing")
            print()
            
    def _demo_performance_comparison(self):
        """Compare performance across logic systems"""
        print("⚡ Performance Comparison Across Logic Systems")
        print("-" * 40)
        
        test_formula = "(p & q) | (r & s) | (t & u)"
        
        systems = [
            (LogicSystem.CLASSICAL, "Classical Logic"),
            (LogicSystem.THREE_VALUED, "Three-Valued Logic"),
        ]
        
        print(f"Test formula: '{test_formula}'")
        print()
        
        results = {}
        for system, name in systems:
            inference = TableauInference(system)
            
            start_time = time.time()
            result = inference.analyze_inference(test_formula)
            end_time = time.time()
            
            results[system] = result
            
            print(f"{name}:")
            print(f"  Construction time: {end_time - start_time:.4f}s")
            print(f"  Rule applications: {result.statistics.rule_applications}")
            print(f"  Branches created: {result.total_branches}")
            print(f"  Models found: {len(result.models)}")
            print()
            
        # Performance analysis
        if len(results) > 1:
            classical_time = results[LogicSystem.CLASSICAL].construction_time or 0
            wk3_time = results[LogicSystem.THREE_VALUED].construction_time or 0
            
            if classical_time > 0 and wk3_time > 0:
                ratio = wk3_time / classical_time
                print(f"Performance ratio (WK3/Classical): {ratio:.2f}x")
                print()
                
    def _demo_complex_reasoning(self):
        """Demonstrate complex logical reasoning scenarios"""
        print("🎭 Complex Logical Reasoning")
        print("-" * 40)
        
        complex_cases = [
            {
                'premises': ["p -> q", "q -> r", "p"],
                'conclusion': "r",
                'description': "Chain of implications"
            },
            {
                'premises': ["p | q", "~p", "q -> r"],
                'conclusion': "r", 
                'description': "Disjunctive syllogism with implication"
            },
            {
                'premises': ["(p & q) -> r", "~r", "p"],
                'conclusion': "~q",
                'description': "Modus tollens with conjunction"
            }
        ]
        
        for case in complex_cases:
            print(f"{case['description']}:")
            print(f"  Premises: {', '.join(case['premises'])}")
            print(f"  Conclusion: {case['conclusion']}")
            
            # Test if premises + negated conclusion is unsatisfiable
            # (which means the conclusion follows from the premises)
            test_formulas = case['premises'] + [f"~({case['conclusion']})"]
            
            inference = TableauInference()
            satisfiable = inference.is_satisfiable(test_formulas)
            valid = not satisfiable  # Valid if premises + ~conclusion is unsatisfiable
            
            status = "✅ Valid" if valid else "❌ Invalid"
            print(f"  Result: {status}")
            
            if valid:
                print(f"  Conclusion follows logically from premises")
            else:
                print(f"  Conclusion does not follow from premises")
                models = inference.get_models(test_formulas)
                if models:
                    print(f"  Counterexample: {models[0]}")
                    
            print()
            
    def _demo_error_handling(self):
        """Demonstrate error handling and edge cases"""
        print("⚠️  Error Handling and Edge Cases")
        print("-" * 40)
        
        error_cases = [
            ("", "Empty formula"),
            ("p &", "Incomplete conjunction"),
            ("((p)", "Unmatched parentheses"),
            ("p q", "Missing operator"),
        ]
        
        for formula_str, description in error_cases:
            print(f"{description}: '{formula_str}'")
            try:
                result = is_satisfiable(formula_str)
                print(f"  Unexpected success: {result}")
            except Exception as e:
                print(f"  Expected error: {type(e).__name__}")
                print(f"  Message: {str(e)[:50]}...")
            print()
            
        # Edge cases that should work
        edge_cases = [
            ("T", "Boolean constant (if supported)"),
            ("p", "Single atom"),
            ("~p", "Simple negation"),
        ]
        
        print("Edge cases (should work):")
        for formula_str, description in edge_cases:
            try:
                result = is_satisfiable(formula_str)
                print(f"  ✅ {description}: '{formula_str}' -> {result}")
            except Exception as e:
                print(f"  ❌ {description}: '{formula_str}' -> Error: {e}")
                
        print()
        
    def _print_summary_statistics(self):
        """Print overall demonstration statistics"""
        if not self.results:
            return
            
        print("📊 Demonstration Summary")
        print("-" * 40)
        
        total_time = sum(r.construction_time for r in self.results)
        total_rules = sum(r.rule_applications for r in self.results)
        total_branches = sum(r.branch_count for r in self.results)
        
        print(f"Total demonstrations: {len(self.results)}")
        print(f"Total construction time: {total_time:.4f}s")
        print(f"Total rule applications: {total_rules}")
        print(f"Total branches created: {total_branches}")
        print()
        
        # System breakdown
        system_stats = {}
        for result in self.results:
            system = result.logic_system
            if system not in system_stats:
                system_stats[system] = {'count': 0, 'time': 0, 'rules': 0}
                
            system_stats[system]['count'] += 1
            system_stats[system]['time'] += result.construction_time
            system_stats[system]['rules'] += result.rule_applications
            
        if system_stats:
            print("By logic system:")
            for system, stats in system_stats.items():
                avg_time = stats['time'] / stats['count'] if stats['count'] > 0 else 0
                print(f"  {system}: {stats['count']} demos, "
                      f"avg {avg_time:.4f}s, {stats['rules']} rules")


def run_interactive_demo():
    """Run an interactive demonstration where users can input formulas"""
    print("🎮 Interactive Tableau Demo")
    print("-" * 30)
    print("Enter logical formulas to test. Use:")
    print("  & (and), | (or), -> (implies), ~ (not)")
    print("  Examples: 'p & q', 'p -> (q | r)', '~(p & ~p)'")
    print("  Type 'quit' to exit, 'help' for more examples")
    print()
    
    inference = TableauInference()
    
    while True:
        try:
            formula_str = input("Formula: ").strip()
            
            if formula_str.lower() in ['quit', 'exit', 'q']:
                break
            elif formula_str.lower() == 'help':
                print_help_examples()
                continue
            elif not formula_str:
                continue
                
            # Analyze the formula
            result = inference.analyze_inference(formula_str)
            
            print(f"Result: {result.get_model_summary()}")
            print(f"Construction: {result.statistics.rule_applications} rules, "
                  f"{result.total_branches} branches")
            
            if result.construction_time:
                print(f"Time: {result.construction_time:.4f}s")
                
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print()


def print_help_examples():
    """Print helpful examples for interactive demo"""
    examples = [
        ("p", "Simple atom"),
        ("p & q", "Conjunction (and)"),
        ("p | q", "Disjunction (or)"),
        ("p -> q", "Implication"), 
        ("~p", "Negation (not)"),
        ("p | ~p", "Tautology (always true)"),
        ("p & ~p", "Contradiction (always false)"),
        ("(p & q) -> (p | q)", "Complex tautology"),
        ("(p -> q) & p & ~q", "Complex contradiction"),
    ]
    
    print("\nExample formulas:")
    for formula, description in examples:
        print(f"  {formula:<15} - {description}")
    print()


def benchmark_performance():
    """Run performance benchmarks across different formula complexities"""
    print("🏁 Performance Benchmarks")
    print("-" * 30)
    
    benchmarks = [
        ("p", "Single atom"),
        ("p & q", "Simple conjunction"),
        ("(p & q) | (r & s)", "Medium complexity"),
        ("(p & q & r) | (s & t & u) | (v & w & x)", "High complexity"),
        ("((p -> q) & (q -> r)) -> (p -> r)", "Logical reasoning"),
    ]
    
    systems = [LogicSystem.CLASSICAL, LogicSystem.THREE_VALUED]
    
    for formula_str, description in benchmarks:
        print(f"\n{description}: '{formula_str}'")
        
        for system in systems:
            inference = TableauInference(system)
            
            # Multiple runs for more accurate timing
            times = []
            for _ in range(3):
                start_time = time.time()
                result = inference.analyze_inference(formula_str)
                end_time = time.time()
                times.append(end_time - start_time)
                
            avg_time = sum(times) / len(times)
            print(f"  {system.value}: {avg_time:.4f}s avg "
                  f"({result.statistics.rule_applications} rules, "
                  f"{result.total_branches} branches)")


def main():
    """Main demonstration entry point"""
    print("Welcome to the Tableau Reasoning System!")
    print("Choose a demonstration mode:")
    print("1. Full comprehensive demo")
    print("2. Interactive formula testing")
    print("3. Performance benchmarks")
    print("4. Quick satisfiability examples")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        print()
        
        if choice == "1":
            demo = TableauDemo()
            demo.run_all_demonstrations()
        elif choice == "2":
            run_interactive_demo()
        elif choice == "3":
            benchmark_performance()
        elif choice == "4":
            quick_examples()
        else:
            print("Invalid choice. Running comprehensive demo...")
            demo = TableauDemo()
            demo.run_all_demonstrations()
            
    except KeyboardInterrupt:
        print("\nDemo interrupted. Goodbye!")
    except Exception as e:
        print(f"Demo error: {e}")


def quick_examples():
    """Run quick satisfiability examples"""
    print("⚡ Quick Satisfiability Examples")
    print("-" * 30)
    
    examples = [
        "p",
        "p & q", 
        "p | q",
        "p -> q",
        "~p",
        "p & ~p",
        "p | ~p",
        "(p & q) -> r",
        "((p -> q) & p) -> q",
    ]
    
    for formula_str in examples:
        satisfiable = is_satisfiable(formula_str)
        status = "SAT" if satisfiable else "UNSAT"
        print(f"  {formula_str:<20} -> {status}")


if __name__ == "__main__":
    main()