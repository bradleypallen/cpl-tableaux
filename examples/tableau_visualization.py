#!/usr/bin/env python3
"""
wKrQ Tableau Visualization Examples

Demonstrates the tableau tree visualization capabilities.
"""

from wkrq import parse, solve, test_inference, parse_inference, T


def simple_formulas():
    """Show tableaux for simple formulas."""
    print("=== Simple Formula Tableaux ===")
    
    formulas = [
        "p",           # Satisfiable atom
        "p & ~p",      # Contradiction
        "p | ~p",      # Tautology  
        "p & q",       # Conjunction
        "p | q",       # Disjunction
    ]
    
    for formula_str in formulas:
        print(f"\nFormula: {formula_str}")
        formula = parse(formula_str)
        result = solve(formula, T)
        
        # Build a simple tableau representation
        if result.tableau:
            print("Tableau:")
            _print_simple_tableau(result.tableau)
        
        print(f"Result: {'Satisfiable' if result.satisfiable else 'Unsatisfiable'}")
        if result.models:
            print(f"Models: {result.models}")


def _print_simple_tableau(tableau):
    """Print a simple tableau representation."""
    if not tableau.nodes:
        return
    
    def print_node(node, prefix="", is_last=True):
        # Current node
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{node.id}. {node.formula}")
        
        # Children
        if node.children:
            extension = "    " if is_last else "│   "
            for i, child in enumerate(node.children):
                child_is_last = (i == len(node.children) - 1)
                print_node(child, prefix + extension, child_is_last)
        elif any(branch.is_closed for branch in tableau.branches 
                if node in branch.nodes):
            # Show closure
            extension = "    " if is_last else "│   "
            print(f"{prefix}{extension}└── ✗ CLOSED")
    
    print_node(tableau.nodes[0])


def complex_formulas():
    """Show tableaux for more complex formulas."""
    print("\n=== Complex Formula Tableaux ===")
    
    complex_formulas = [
        "(p & q) | r",
        "p -> (q -> r)",
        "~(p & q)",
        "(p | q) & (~p | r)",
    ]
    
    for formula_str in complex_formulas:
        print(f"\nFormula: {formula_str}")
        formula = parse(formula_str)
        result = solve(formula, T)
        
        print(f"Satisfiable: {result.satisfiable}")
        print(f"Open branches: {result.open_branches}")
        print(f"Closed branches: {result.closed_branches}")
        print(f"Total nodes: {result.total_nodes}")


def inference_tableaux():
    """Show tableaux for inference testing."""
    print("\n=== Inference Tableaux ===")
    
    inferences = [
        "p, p -> q |- q",      # Valid (modus ponens)
        "p |- q",              # Invalid
        "p | q, ~p |- q",      # Valid (disjunctive syllogism)
    ]
    
    for inf_str in inferences:
        print(f"\nInference: {inf_str}")
        inference = parse_inference(inf_str)
        result = test_inference(inference)
        
        print(f"Valid: {result.valid}")
        if not result.valid and result.countermodels:
            print(f"Countermodel: {result.countermodels[0]}")
        
        # Show what formula is actually being tested
        test_formula = inference.to_formula()
        print(f"Testing satisfiability of: {test_formula}")
        print(f"Tableau result: {'Unsatisfiable' if not result.tableau_result.satisfiable else 'Satisfiable'}")


def different_signs():
    """Show how different signs affect tableau construction."""
    print("\n=== Different Signs ===")
    
    formula_str = "p | ~p"
    formula = parse(formula_str)
    
    signs = [T]  # Focus on T for now, others work similarly
    
    for sign in signs:
        print(f"\nSign {sign}: {formula}")
        result = solve(formula, sign)
        print(f"Satisfiable: {result.satisfiable}")
        print(f"Branches: {result.open_branches} open, {result.closed_branches} closed")
        if result.models:
            print(f"Sample models: {result.models[:2]}")  # Show first 2 models


def tableau_statistics():
    """Show tableau construction statistics."""
    print("\n=== Tableau Statistics ===")
    
    test_cases = [
        ("Simple atom", "p"),
        ("Contradiction", "p & ~p"), 
        ("Tautology", "p | ~p"),
        ("Complex formula", "(p & q) | (r & s)"),
        ("Deep nesting", "p -> (q -> (r -> s))"),
    ]
    
    for name, formula_str in test_cases:
        formula = parse(formula_str)
        result = solve(formula, T)
        
        print(f"\n{name}: {formula_str}")
        print(f"  Satisfiable: {result.satisfiable}")
        print(f"  Total nodes: {result.total_nodes}")
        print(f"  Open branches: {result.open_branches}")
        print(f"  Closed branches: {result.closed_branches}")
        print(f"  Models found: {len(result.models)}")


def main():
    """Run all visualization examples."""
    print("wKrQ Tableau Visualization Examples")
    print("=" * 50)
    
    simple_formulas()
    complex_formulas()
    inference_tableaux()
    different_signs()
    tableau_statistics()
    
    print("\n" + "=" * 50)
    print("Visualization examples completed!")
    print("\nTry these CLI commands for interactive visualization:")
    print("  wkrq --tree 'p & ~p'")
    print("  wkrq --tree --show-rules 'p | (q & r)'")
    print("  wkrq --tree --format=unicode 'p -> q'")
    print("  wkrq --tree --format=json 'p & q' | jq")


if __name__ == "__main__":
    main()