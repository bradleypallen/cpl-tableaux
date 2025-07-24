# Tableau System Tutorials

**Version**: 3.0 (Consolidated Architecture)  
**Last Updated**: January 2025  
**License**: MIT  

## Table of Contents

1. [Getting Started](#getting-started)
2. [Tutorial 1: Basic Satisfiability Testing](#tutorial-1-basic-satisfiability-testing)
3. [Tutorial 2: Understanding Signed Tableaux](#tutorial-2-understanding-signed-tableaux)
4. [Tutorial 3: Three-Valued Logic Exploration](#tutorial-3-three-valued-logic-exploration)
5. [Tutorial 4: Building a SAT Solver](#tutorial-4-building-a-sat-solver)
6. [Tutorial 5: Model Extraction and Analysis](#tutorial-5-model-extraction-and-analysis)
7. [Tutorial 6: Performance Optimization](#tutorial-6-performance-optimization)
8. [Tutorial 7: Extending with New Logic Systems](#tutorial-7-extending-with-new-logic-systems)
9. [CLI Usage Guide](#cli-usage-guide)
10. [Advanced Applications](#advanced-applications)

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Basic understanding of propositional logic
- Familiarity with logical operators: ∧ (AND), ∨ (OR), ¬ (NOT), → (IMPLIES)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd tableaux

# Verify installation works
python -m pytest --tb=no -q
# Should show: 227 passed in <0.5s
```

### Verify Your Setup

```python
# test_setup.py
from tableau_core import Atom, classical_signed_tableau, T

# Create a simple formula
p = Atom("p")
engine = classical_signed_tableau(T(p))
result = engine.build()

print(f"Setup working: {result}")  # Should print: Setup working: True
```

## Tutorial 1: Basic Satisfiability Testing

**Goal**: Learn fundamental concepts of satisfiability and tableau construction.

### Step 1: Understanding Satisfiability

Satisfiability is the core question in logic: *Can this formula be made true?*

```python
#!/usr/bin/env python3
"""Tutorial 1: Basic Satisfiability Testing"""

from tableau_core import Atom, Conjunction, Disjunction, Negation, Implication
from tableau_core import T, F, classical_signed_tableau

def test_satisfiability_examples():
    """Explore basic satisfiability concepts."""
    
    # Create some atoms
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    print("=== SATISFIABILITY EXAMPLES ===\n")
    
    # Example 1: Simple atom - always satisfiable
    print("Example 1: Simple atom")
    print(f"Formula: {p}")
    
    engine = classical_signed_tableau(T(p))
    result = engine.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = engine.extract_all_models()
        print(f"Model: {models[0]}")
    print()
    
    # Example 2: Conjunction - satisfiable if both parts can be true
    print("Example 2: Conjunction")
    conjunction = Conjunction(p, q)
    print(f"Formula: {conjunction}")
    
    engine = classical_signed_tableau(T(conjunction))
    result = engine.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = engine.extract_all_models()
        print(f"Model: {models[0]}")
    print()
    
    # Example 3: Contradiction - never satisfiable
    print("Example 3: Contradiction")
    contradiction = Conjunction(p, Negation(p))
    print(f"Formula: {contradiction}")
    
    engine = classical_signed_tableau(T(contradiction))
    result = engine.build()
    
    print(f"Satisfiable: {result}")
    if not result:
        print("No models exist (unsatisfiable)")
    print()
    
    # Example 4: Disjunction - satisfiable if at least one part can be true
    print("Example 4: Disjunction")
    disjunction = Disjunction(p, q)
    print(f"Formula: {disjunction}")
    
    engine = classical_signed_tableau(T(disjunction))
    result = engine.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = engine.extract_all_models()
        print(f"Found {len(models)} models:")
        for i, model in enumerate(models):
            print(f"  Model {i+1}: {model}")
    print()

if __name__ == "__main__":
    test_satisfiability_examples()
```

### Step 2: Interactive Satisfiability Tester

```python
def interactive_sat_tester():
    """Interactive tool to test formula satisfiability."""
    
    print("=== INTERACTIVE SATISFIABILITY TESTER ===")
    print("Enter formulas using: p, q, r (atoms), &, |, ~, -> (operators)")
    print("Examples: 'p & q', '~p | q', 'p -> q'")
    print("Type 'quit' to exit\n")
    
    while True:
        formula_str = input("Enter formula: ").strip()
        
        if formula_str.lower() == 'quit':
            break
        
        try:
            # Simple parser (you could extend this)
            formula = parse_simple_formula(formula_str)
            
            engine = classical_signed_tableau(T(formula))
            result = engine.build()
            
            print(f"  Formula: {formula}")
            print(f"  Satisfiable: {result}")
            
            if result:
                models = engine.extract_all_models()
                print(f"  Models ({len(models)}):")
                for i, model in enumerate(models[:3]):  # Show first 3
                    print(f"    {i+1}: {model}")
                if len(models) > 3:
                    print(f"    ... and {len(models) - 3} more")
            else:
                print("  No satisfying models exist")
            print()
            
        except Exception as e:
            print(f"  Error: {e}")
            print("  Try simpler formulas like 'p & q' or '~p | q'")
            print()

def parse_simple_formula(formula_str):
    """Simple formula parser for common cases."""
    # This is a simplified parser - you could make it more robust
    formula_str = formula_str.replace(" ", "")
    
    # Handle simple cases
    if formula_str == "p":
        return Atom("p")
    elif formula_str == "q":
        return Atom("q")
    elif formula_str == "r":
        return Atom("r")
    elif formula_str == "~p":
        return Negation(Atom("p"))
    elif formula_str == "p&q":
        return Conjunction(Atom("p"), Atom("q"))
    elif formula_str == "p|q":
        return Disjunction(Atom("p"), Atom("q"))
    elif formula_str == "p->q":
        return Implication(Atom("p"), Atom("q"))
    elif formula_str == "p&~p":
        return Conjunction(Atom("p"), Negation(Atom("p")))
    elif formula_str == "p|~p":
        return Disjunction(Atom("p"), Negation(Atom("p")))
    else:
        raise ValueError(f"Cannot parse: {formula_str}")

# Run the interactive tester
# interactive_sat_tester()
```

### Exercise 1

Try these formulas and predict whether they're satisfiable:

1. `p`
2. `p & q`
3. `p | q`
4. `p & ~p`
5. `p | ~p`
6. `p -> q`
7. `(p -> q) & p & ~q`

**Answers**: 1-3: Satisfiable, 4: Unsatisfiable, 5-6: Satisfiable, 7: Unsatisfiable

## Tutorial 2: Understanding Signed Tableaux

**Goal**: Learn how signed tableaux systematically test satisfiability.

### Step 1: Signed Formula Notation

Signed tableaux use prefixes to track what we're trying to prove:

- `T:φ` means "φ is true"
- `F:φ` means "φ is false"

```python
#!/usr/bin/env python3
"""Tutorial 2: Understanding Signed Tableaux"""

from tableau_core import *

def explore_signed_formulas():
    """Understand signed formula notation."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("=== SIGNED FORMULA NOTATION ===\n")
    
    # Basic signed formulas
    t_p = T(p)  # "p is true"
    f_p = F(p)  # "p is false"
    
    print(f"T:p = {t_p} (p is true)")
    print(f"F:p = {f_p} (p is false)")
    print()
    
    # Signed complex formulas
    conjunction = Conjunction(p, q)
    t_conj = T(conjunction)  # "(p ∧ q) is true"
    f_conj = F(conjunction)  # "(p ∧ q) is false"
    
    print(f"T:(p ∧ q) = {t_conj}")
    print(f"F:(p ∧ q) = {f_conj}")
    print()
    
    # Test what these mean
    print("Testing T:(p ∧ q) - requires both p and q to be true:")
    engine = classical_signed_tableau(t_conj)
    result = engine.build()
    if result:
        models = engine.extract_all_models()
        print(f"  Model: {models[0]}")
    
    print("\nTesting F:(p ∧ q) - requires at least one of p, q to be false:")
    engine = classical_signed_tableau(f_conj)
    result = engine.build()
    if result:
        models = engine.extract_all_models()
        print(f"  Found {len(models)} models:")
        for model in models:
            print(f"    {model}")

if __name__ == "__main__":
    explore_signed_formulas()
```

### Step 2: Tableau Rules in Action

```python
def demonstrate_tableau_rules():
    """Show how tableau rules work."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("=== TABLEAU RULES DEMONSTRATION ===\n")
    
    # T-Conjunction Rule: T:(p ∧ q) → T:p, T:q
    print("Rule 1: T-Conjunction")
    print("T:(p ∧ q) breaks down to: T:p AND T:q (both must be true)")
    
    conjunction = Conjunction(p, q)
    engine = classical_signed_tableau(T(conjunction))
    result = engine.build()
    
    print(f"Result: Satisfiable = {result}")
    if result:
        # Look at what the tableau contains
        for branch in engine.branches:
            if not branch.is_closed:
                print("Open branch contains:")
                for sf in branch.signed_formulas:
                    print(f"  {sf}")
                break
    print()
    
    # F-Conjunction Rule: F:(p ∧ q) → F:p | F:q  
    print("Rule 2: F-Conjunction")
    print("F:(p ∧ q) branches to: F:p OR F:q (at least one must be false)")
    
    engine = classical_signed_tableau(F(conjunction))
    result = engine.build()
    
    print(f"Result: Satisfiable = {result}")
    if result:
        open_branches = [b for b in engine.branches if not b.is_closed]
        print(f"Created {len(open_branches)} branches:")
        for i, branch in enumerate(open_branches):
            print(f"  Branch {i+1}:")
            for sf in branch.signed_formulas:
                print(f"    {sf}")
    print()
    
    # T-Disjunction Rule: T:(p ∨ q) → T:p | T:q
    print("Rule 3: T-Disjunction")
    print("T:(p ∨ q) branches to: T:p OR T:q (at least one must be true)")
    
    disjunction = Disjunction(p, q)
    engine = classical_signed_tableau(T(disjunction))
    result = engine.build()
    
    print(f"Result: Satisfiable = {result}")
    if result:
        open_branches = [b for b in engine.branches if not b.is_closed]
        print(f"Created {len(open_branches)} branches:")
        for i, branch in enumerate(open_branches):
            print(f"  Branch {i+1}:")
            for sf in branch.signed_formulas:
                print(f"    {sf}")

if __name__ == "__main__":
    demonstrate_tableau_rules()
```

### Step 3: Branch Closure

```python
def demonstrate_branch_closure():
    """Show how contradictions close branches."""
    
    p = Atom("p")
    
    print("=== BRANCH CLOSURE DEMONSTRATION ===\n")
    
    # Case 1: Contradiction closes all branches
    print("Case 1: Testing T:(p ∧ ¬p) - should be unsatisfiable")
    contradiction = Conjunction(p, Negation(p))
    engine = classical_signed_tableau(T(contradiction))
    result = engine.build()
    
    print(f"Satisfiable: {result}")
    print("Branch analysis:")
    
    for i, branch in enumerate(engine.branches):
        print(f"  Branch {i+1}: {'CLOSED' if branch.is_closed else 'OPEN'}")
        if branch.is_closed and hasattr(branch, 'closure_reason') and branch.closure_reason:
            sf1, sf2 = branch.closure_reason
            print(f"    Closed by: {sf1} contradicts {sf2}")
        
        print(f"    Contains:")
        for sf in branch.signed_formulas:
            print(f"      {sf}")
    print()
    
    # Case 2: Some branches close, others remain open
    print("Case 2: Testing F:(p ∧ ¬p) - should be satisfiable")
    engine = classical_signed_tableau(F(contradiction))
    result = engine.build()
    
    print(f"Satisfiable: {result}")
    print("Branch analysis:")
    
    for i, branch in enumerate(engine.branches):
        print(f"  Branch {i+1}: {'CLOSED' if branch.is_closed else 'OPEN'}")
        if branch.is_closed and hasattr(branch, 'closure_reason') and branch.closure_reason:
            sf1, sf2 = branch.closure_reason
            print(f"    Closed by: {sf1} contradicts {sf2}")
        
        print(f"    Contains:")
        for sf in branch.signed_formulas:
            print(f"      {sf}")

if __name__ == "__main__":
    demonstrate_branch_closure()
```

### Exercise 2

Trace through these tableau constructions by hand:

1. `T:(p ∨ q)`
2. `F:(p → q)`
3. `T:((p → q) ∧ p ∧ ¬q)`

## Tutorial 3: Three-Valued Logic Exploration

**Goal**: Understand how three-valued logic differs from classical logic.

### Step 1: Three-Valued Truth Tables

```python
#!/usr/bin/env python3
"""Tutorial 3: Three-Valued Logic Exploration"""

from tableau_core import *

def explore_three_valued_truth_tables():
    """Demonstrate three-valued logic truth tables."""
    
    print("=== THREE-VALUED LOGIC TRUTH TABLES ===\n")
    
    # Truth values: t (true), f (false), e (undefined)
    print("Truth values:")
    print("  t = true")
    print("  f = false")
    print("  e = undefined/error")
    print()
    
    # Negation truth table
    print("Negation (¬):")
    print("  ¬t = f")
    print("  ¬f = t") 
    print("  ¬e = e  ← Undefined stays undefined")
    print()
    
    # Conjunction truth table
    print("Conjunction (∧):")
    print("     | t | f | e")
    print("  ---|---|---|---")
    print("   t | t | f | e")
    print("   f | f | f | f  ← False 'absorbs'")
    print("   e | e | f | e")
    print()
    
    # Disjunction truth table
    print("Disjunction (∨):")
    print("     | t | f | e")
    print("  ---|---|---|---")
    print("   t | t | t | t  ← True 'absorbs'")
    print("   f | t | f | e")
    print("   e | t | e | e")
    print()

def compare_classical_vs_wk3():
    """Compare classical and WK3 logic on key examples."""
    
    p = Atom("p")
    
    print("=== CLASSICAL vs WK3 COMPARISON ===\n")
    
    test_cases = [
        ("p ∧ ¬p", Conjunction(p, Negation(p)), "Classical contradiction"),
        ("p ∨ ¬p", Disjunction(p, Negation(p)), "Law of excluded middle"),
        ("p → p", Implication(p, p), "Self-implication"),
    ]
    
    for description, formula, name in test_cases:
        print(f"{name}: {description}")
        
        # Classical logic
        classical_engine = classical_signed_tableau(T(formula))
        classical_sat = classical_engine.build()
        
        # Three-valued logic
        wk3_sat = wk3_satisfiable(formula)
        
        print(f"  Classical: {'Satisfiable' if classical_sat else 'Unsatisfiable'}")
        print(f"  WK3: {'Satisfiable' if wk3_sat else 'Unsatisfiable'}")
        
        if wk3_sat and not classical_sat:
            print("  *** WK3 allows satisfaction through undefined values ***")
            models = wk3_models(formula)
            for model in models:
                if model.assignment.get('p', e) == e:
                    print(f"    Model with p=undefined: {model.assignment}")
                    result = model.satisfies(formula)
                    print(f"    Formula evaluates to: {result}")
                    break
        
        print()

if __name__ == "__main__":
    explore_three_valued_truth_tables()
    compare_classical_vs_wk3()
```

### Step 2: WK3 Model Analysis

```python
def analyze_wk3_models():
    """Detailed analysis of WK3 models."""
    
    print("=== WK3 MODEL ANALYSIS ===\n")
    
    p = Atom("p")
    q = Atom("q")
    
    # Example: p ∨ ¬p in WK3
    excluded_middle = Disjunction(p, Negation(p))
    
    print(f"Analyzing: {excluded_middle}")
    print("In classical logic, this is always true (tautology)")
    print("In WK3, let's see what happens...\n")
    
    models = wk3_models(excluded_middle)
    print(f"Found {len(models)} models:")
    
    for i, model in enumerate(models):
        print(f"\nModel {i+1}:")
        p_value = model.assignment.get('p', e)
        print(f"  p = {p_value}")
        
        # Evaluate each subformula
        not_p_value = model.satisfies(Negation(p))
        disjunction_value = model.satisfies(excluded_middle)
        
        print(f"  ¬p = {not_p_value}")
        print(f"  p ∨ ¬p = {disjunction_value}")
        
        if disjunction_value != t:
            print(f"  *** This model shows p ∨ ¬p is not always true in WK3! ***")
    
    print("\nExplanation:")
    print("When p is undefined (e), ¬p is also undefined (e).")
    print("Therefore, e ∨ e = e (undefined), not t (true).")
    print("This shows the law of excluded middle fails in WK3.")

def wk3_satisfiable_contradictions():
    """Show contradictions that are satisfiable in WK3."""
    
    print("\n=== WK3 SATISFIABLE 'CONTRADICTIONS' ===\n")
    
    p = Atom("p")
    q = Atom("q")
    
    # Formulas that are contradictions in classical logic
    classical_contradictions = [
        ("p ∧ ¬p", Conjunction(p, Negation(p))),
        ("(p → q) ∧ p ∧ ¬q", Conjunction(Conjunction(Implication(p, q), p), Negation(q))),
    ]
    
    for description, formula in classical_contradictions:
        print(f"Testing: {description}")
        
        # Classical check
        classical_sat = classical_signed_tableau(T(formula)).build()
        
        # WK3 check  
        wk3_sat = wk3_satisfiable(formula)
        
        print(f"  Classical: {'SAT' if classical_sat else 'UNSAT'}")
        print(f"  WK3: {'SAT' if wk3_sat else 'UNSAT'}")
        
        if wk3_sat and not classical_sat:
            print("  WK3 models:")
            models = wk3_models(formula)
            for model in models:
                print(f"    {model.assignment}")
                result = model.satisfies(formula)
                print(f"    Formula value: {result}")
        print()

if __name__ == "__main__":
    analyze_wk3_models()
    wk3_satisfiable_contradictions()
```

### Exercise 3

1. Create truth tables for `p → q` in both classical and WK3 logic
2. Find a formula that's unsatisfiable in classical logic but satisfiable in WK3
3. Explain why `(p ∧ q) → p` might not be a tautology in WK3

## Tutorial 4: Building a SAT Solver

**Goal**: Create a practical satisfiability solver using the tableau system.

### Step 1: Basic SAT Solver

```python
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
            satisfiable = wk3_satisfiable(formula)  
            models = wk3_models(formula) if satisfiable else []
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
```

### Step 2: Advanced SAT Solver Features

```python
class AdvancedSATSolver(TableauSATSolver):
    """Advanced SAT solver with additional features."""
    
    def __init__(self, logic_system="classical"):
        super().__init__(logic_system)
        self.problem_cache = {}
    
    def solve_with_assumptions(self, formula, assumptions):
        """
        Solve SAT problem with additional assumptions.
        
        Args:
            formula: Main formula to test
            assumptions: List of literals that must be true
        """
        # Combine formula with assumptions
        if assumptions:
            assumption_conjunction = assumptions[0]
            for assumption in assumptions[1:]:
                assumption_conjunction = Conjunction(assumption_conjunction, assumption)
            
            combined_formula = Conjunction(formula, assumption_conjunction)
        else:
            combined_formula = formula
        
        return self.solve(combined_formula)
    
    def find_minimal_unsatisfiable_core(self, formulas):
        """
        Find minimal subset of formulas that are unsatisfiable.
        
        This is useful for debugging why a formula is unsatisfiable.
        """
        print(f"Finding minimal unsatisfiable core for {len(formulas)} formulas...")
        
        # First check if all formulas together are unsatisfiable
        if len(formulas) == 1:
            combined = formulas[0]
        else:
            combined = formulas[0]
            for formula in formulas[1:]:
                combined = Conjunction(combined, formula)
        
        result = self.solve(combined)
        if result['satisfiable']:
            return []  # No unsatisfiable core
        
        # Try removing each formula to find minimal core
        minimal_core = formulas[:]
        
        for i in range(len(formulas)):
            # Try without formula i
            test_formulas = formulas[:i] + formulas[i+1:]
            
            if not test_formulas:
                continue
            
            if len(test_formulas) == 1:
                test_combined = test_formulas[0]
            else:
                test_combined = test_formulas[0]  
                for formula in test_formulas[1:]:
                    test_combined = Conjunction(test_combined, formula)
            
            test_result = self.solve(test_combined)
            
            if not test_result['satisfiable']:
                # Still unsatisfiable without formula i, so remove it
                minimal_core = test_formulas
        
        return minimal_core
    
    def solve_and_explain(self, formula):
        """Solve and provide detailed explanation."""
        
        result = self.solve(formula)
        
        print(f"Formula: {formula}")
        print(f"Result: {'SATISFIABLE' if result['satisfiable'] else 'UNSATISFIABLE'}")
        print()
        
        if result['satisfiable']:
            print("Explanation: The formula can be made true.")
            print(f"Found {result['statistics']['num_models']} satisfying model(s):")
            
            for i, model in enumerate(result['models'][:3]):  # Show first 3
                print(f"  Model {i+1}: {model}")
                
                # Verify model satisfies formula
                if hasattr(model, 'satisfies'):  # WK3 model
                    verification = model.satisfies(formula)
                    print(f"    Verification: {formula} = {verification}")
                else:  # Classical model (dict)
                    print(f"    Atom assignments: {model}")
                    
            if len(result['models']) > 3:
                print(f"    ... and {len(result['models']) - 3} more models")
        else:
            print("Explanation: No truth assignment can make this formula true.")
            print("This means the formula contains a logical contradiction.")
            
            # Try to find what makes it contradictory
            if hasattr(formula, 'left') and hasattr(formula, 'right'):
                # It's a binary operator - test parts separately
                if isinstance(formula, Conjunction):
                    left_result = self.solve(formula.left)
                    right_result = self.solve(formula.right)
                    
                    if not left_result['satisfiable']:
                        print(f"  Left part is contradictory: {formula.left}")
                    elif not right_result['satisfiable']:
                        print(f"  Right part is contradictory: {formula.right}")
                    else:
                        print(f"  Parts are individually satisfiable but incompatible together")
        
        print(f"\nPerformance:")
        print(f"  Solve time: {result['statistics']['solve_time']:.4f} seconds")
        if 'rule_applications' in result['statistics']:
            print(f"  Rule applications: {result['statistics']['rule_applications']}")
        
        return result

def demo_advanced_solver():
    """Demonstrate advanced solver features."""
    
    print("=== ADVANCED SAT SOLVER DEMO ===\n")
    
    solver = AdvancedSATSolver("classical")
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    # Example 1: Solve with assumptions
    print("Example 1: Solving with assumptions")
    formula = Implication(p, q)
    assumptions = [p]  # Assume p is true
    
    print(f"Formula: {formula}")
    print(f"Assumptions: {assumptions}")
    
    result = solver.solve_with_assumptions(formula, assumptions)
    print(f"Result: {'SAT' if result['satisfiable'] else 'UNSAT'}")
    if result['satisfiable']:
        print(f"Model: {result['models'][0]}")
    print()
    
    # Example 2: Detailed explanation
    print("Example 2: Detailed explanation")
    complex_formula = Conjunction(
        Conjunction(p, Implication(p, q)),
        Negation(q)
    )
    
    solver.solve_and_explain(complex_formula)
    print()
    
    # Example 3: Minimal unsatisfiable core
    print("Example 3: Minimal unsatisfiable core")
    contradictory_formulas = [
        p,
        Implication(p, q),
        Implication(q, r),
        Negation(r),
        Atom("s")  # This one is irrelevant
    ]
    
    core = solver.find_minimal_unsatisfiable_core(contradictory_formulas)
    print(f"Original formulas: {len(contradictory_formulas)}")
    print(f"Minimal core: {len(core)}")
    for formula in core:
        print(f"  {formula}")

if __name__ == "__main__":
    demo_advanced_solver()
```

### Exercise 4

1. Extend the SAT solver to handle CNF (Conjunctive Normal Form) input
2. Add a timeout feature for complex problems
3. Implement model enumeration with a maximum count

## Tutorial 5: Model Extraction and Analysis

**Goal**: Learn to extract and analyze satisfying models from tableaux.

### Step 1: Understanding Models

```python
#!/usr/bin/env python3
"""Tutorial 5: Model Extraction and Analysis"""

from tableau_core import *

def understand_models():
    """Learn what models represent."""
    
    print("=== UNDERSTANDING MODELS ===\n")
    
    p = Atom("p")
    q = Atom("q")
    
    # Simple formula with multiple models
    formula = Disjunction(p, q)  # p ∨ q
    
    print(f"Formula: {formula}")
    print("This formula is true when at least one of p or q is true.")
    print()
    
    engine = classical_signed_tableau(T(formula))
    satisfiable = engine.build()
    
    if satisfiable:
        models = engine.extract_all_models()
        print(f"Found {len(models)} satisfying models:")
        
        for i, model in enumerate(models):
            print(f"\nModel {i+1}: {model}")
            
            # Verify this model satisfies the formula
            # Manual verification for classical logic
            p_value = model.get('p', False)
            q_value = model.get('q', False)
            formula_value = p_value or q_value  # p ∨ q
            
            print(f"  p = {p_value}, q = {q_value}")
            print(f"  p ∨ q = {p_value} ∨ {q_value} = {formula_value}")
            print(f"  ✓ Model satisfies formula: {formula_value}")
    
    print("\nExplanation:")
    print("Each model represents a complete truth assignment to all atoms")
    print("that appear in the formula. Any assignment that makes the formula")
    print("true is a satisfying model.")

def analyze_model_spaces():
    """Analyze the space of all possible models."""
    
    print("\n=== MODEL SPACE ANALYSIS ===\n")
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    formulas_to_analyze = [
        ("p", p),
        ("p ∧ q", Conjunction(p, q)),
        ("p ∨ q", Disjunction(p, q)),
        ("p → q", Implication(p, q)),
        ("(p ∨ q) ∧ (p ∨ r)", Conjunction(Disjunction(p, q), Disjunction(p, r))),
    ]
    
    for description, formula in formulas_to_analyze:
        print(f"Formula: {description}")
        
        engine = classical_signed_tableau(T(formula))
        satisfiable = engine.build()
        
        if satisfiable:
            models = engine.extract_all_models()
            print(f"  Models: {len(models)}")
            
            # Show all models
            for i, model in enumerate(models):
                assignments = []
                for atom, value in sorted(model.items()):
                    assignments.append(f"{atom}={value}")
                print(f"    {i+1}: {{{', '.join(assignments)}}}")
            
            # Calculate what fraction of total space this represents
            atoms_in_formula = set()
            extract_atoms(formula, atoms_in_formula)
            total_possible = 2 ** len(atoms_in_formula)
            fraction = len(models) / total_possible
            
            print(f"  Covers {len(models)}/{total_possible} = {fraction:.1%} of possible assignments")
        else:
            print(f"  Models: 0 (unsatisfiable)")
        
        print()

def extract_atoms(formula, atom_set):
    """Extract all atoms from a formula."""
    if isinstance(formula, Atom):
        atom_set.add(formula.name)
    elif hasattr(formula, 'operand'):  # Unary operator
        extract_atoms(formula.operand, atom_set)
    elif hasattr(formula, 'left') and hasattr(formula, 'right'):  # Binary operator
        extract_atoms(formula.left, atom_set)
        extract_atoms(formula.right, atom_set)

if __name__ == "__main__":
    understand_models()
    analyze_model_spaces()
```

### Step 2: Model Comparison and Analysis

```python
def compare_classical_wk3_models():
    """Compare models between classical and WK3 logic."""
    
    print("=== CLASSICAL vs WK3 MODEL COMPARISON ===\n")
    
    p = Atom("p")
    q = Atom("q")
    
    test_formulas = [
        ("p ∧ ¬p", Conjunction(p, Negation(p))),
        ("p ∨ ¬p", Disjunction(p, Negation(p))), 
        ("p → p", Implication(p, p)),
        ("p ∨ q", Disjunction(p, q)),
    ]
    
    for description, formula in test_formulas:
        print(f"Formula: {description}")
        
        # Classical models
        classical_engine = classical_signed_tableau(T(formula))
        classical_sat = classical_engine.build()
        
        if classical_sat:
            classical_models = classical_engine.extract_all_models()
            print(f"  Classical models ({len(classical_models)}):")
            for i, model in enumerate(classical_models):
                print(f"    {i+1}: {model}")
        else:
            print(f"  Classical models: None (unsatisfiable)")
        
        # WK3 models
        wk3_sat = wk3_satisfiable(formula)
        if wk3_sat:
            wk3_models_list = wk3_models(formula)
            print(f"  WK3 models ({len(wk3_models_list)}):")
            for i, model in enumerate(wk3_models_list):
                print(f"    {i+1}: {model.assignment}")
                
                # Show how the formula evaluates in this model
                result = model.satisfies(formula)
                print(f"         Formula evaluates to: {result}")
        else:
            print(f"  WK3 models: None (unsatisfiable)")
        
        print()

def model_enumeration_strategies():
    """Demonstrate different model enumeration strategies."""
    
    print("=== MODEL ENUMERATION STRATEGIES ===\n")
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    # Formula with many models
    formula = Disjunction(Disjunction(p, q), r)  # p ∨ q ∨ r
    
    print(f"Formula: {formula}")
    print("This formula has many satisfying models...\n")
    
    # Strategy 1: Find all models
    print("Strategy 1: Find all models")
    engine = classical_signed_tableau(T(formula))
    satisfiable = engine.build()
    
    if satisfiable:
        all_models = engine.extract_all_models()
        print(f"  Found {len(all_models)} total models")
        
        # Group models by patterns
        print("  Models grouped by which atoms are true:")
        
        true_patterns = {}
        for model in all_models:
            true_atoms = [atom for atom, value in model.items() if value]
            pattern = tuple(sorted(true_atoms))
            
            if pattern not in true_patterns:
                true_patterns[pattern] = []
            true_patterns[pattern].append(model)
        
        for pattern, models in true_patterns.items():
            print(f"    {pattern}: {len(models)} model(s)")
    
    print()
    
    # Strategy 2: Find one model per "equivalence class"
    print("Strategy 2: Representative models")
    print("  Instead of all models, find one representative per pattern:")
    
    if satisfiable:
        representatives = []
        seen_patterns = set()
        
        for model in all_models:
            true_atoms = tuple(sorted(atom for atom, value in model.items() if value))
            
            if true_atoms not in seen_patterns:
                representatives.append(model)
                seen_patterns.add(true_atoms)
        
        print(f"  Found {len(representatives)} representative models:")
        for i, model in enumerate(representatives):
            true_atoms = [atom for atom, value in model.items() if value]
            print(f"    {i+1}: True atoms = {true_atoms}")

def model_validation():
    """Validate that extracted models actually satisfy formulas."""
    
    print("\n=== MODEL VALIDATION ===\n")
    
    p = Atom("p")
    q = Atom("q")
    
    # Test complex formula
    formula = Conjunction(
        Implication(p, q),
        Disjunction(p, Negation(q))
    )  # (p → q) ∧ (p ∨ ¬q)
    
    print(f"Formula: {formula}")
    
    engine = classical_signed_tableau(T(formula))
    satisfiable = engine.build()
    
    if satisfiable:
        models = engine.extract_all_models()
        print(f"Found {len(models)} models. Validating each:\n")
        
        for i, model in enumerate(models):
            print(f"Model {i+1}: {model}")
            
            # Extract values
            p_val = model.get('p', False)
            q_val = model.get('q', False)
            
            # Evaluate subformulas
            p_implies_q = (not p_val) or q_val  # p → q
            p_or_not_q = p_val or (not q_val)   # p ∨ ¬q
            full_formula = p_implies_q and p_or_not_q  # (p → q) ∧ (p ∨ ¬q)
            
            print(f"  p = {p_val}, q = {q_val}")
            print(f"  p → q = {p_implies_q}")
            print(f"  p ∨ ¬q = {p_or_not_q}")
            print(f"  Full formula = {full_formula}")
            
            if full_formula:
                print(f"  ✓ Model is valid")
            else:
                print(f"  ✗ Model is INVALID - this shouldn't happen!")
            print()
    else:
        print("Formula is unsatisfiable - no models to validate.")

if __name__ == "__main__":
    compare_classical_wk3_models()
    model_enumeration_strategies()
    model_validation()
```

### Exercise 5

1. Write a function to check if two formulas are logically equivalent by comparing their models
2. Create a model minimizer that finds the simplest satisfying assignment
3. Implement a model counter for formulas in CNF

## CLI Usage Guide

The tableau system includes a powerful command-line interface for interactive use.

### Basic CLI Usage

```bash
# Start interactive mode
python cli.py

# Test specific formulas
python cli.py "p | ~p"                    # Classical tautology
python cli.py "p & ~p"                    # Classical contradiction

# Use different logic systems
python cli.py --wk3 "p | ~p"              # WK3 logic
python cli.py --wk3 "p & ~p"              # WK3 satisfiable contradiction

# Show models
python cli.py --models "p | q"            # Show all satisfying models
python cli.py --wk3 --models "p | ~p"     # Show WK3 models

# Performance testing
python cli.py --stats "complex_formula"   # Show performance statistics
```

### Interactive Mode Tutorial

```bash
$ python cli.py
Welcome to the Tableau Logic System!
Type 'help' for commands, 'quit' to exit.

tableau> help
Available commands:
  test <formula>        - Test satisfiability
  models <formula>      - Show all models
  wk3 <formula>         - Use WK3 logic
  classical <formula>   - Use classical logic
  stats                 - Show performance statistics
  examples              - Show example formulas
  help                  - Show this help
  quit                  - Exit

tableau> test p & q
Formula: p ∧ q
Result: SATISFIABLE
Models: 1
  Model 1: {p=TRUE, q=TRUE}

tableau> test p & ~p
Formula: p ∧ ¬p
Result: UNSATISFIABLE
No satisfying models exist.

tableau> wk3 p & ~p
Switching to WK3 logic...
Formula: p ∧ ¬p
Result: SATISFIABLE
Models: 1
  Model 1: {p=UNDEFINED}

tableau> examples
Example formulas to try:
  Basic: p, p & q, p | q, ~p
  Tautologies: p | ~p, (p -> q) | (~p -> ~q)
  Contradictions: p & ~p, (p -> q) & p & ~q
  Complex: (p | q) & (~p | r) & (~q | r)

tableau> quit
Goodbye!
```

### Advanced CLI Features

```bash
# Batch processing
echo "p & q\np | q\np & ~p" | python cli.py --batch

# Output formats
python cli.py --format=json "p | q"       # JSON output
python cli.py --format=csv "p | q"        # CSV output for spreadsheets

# Timeout for complex formulas
python cli.py --timeout=5 "complex_formula"

# Debug mode
python cli.py --debug "p & q"             # Show tableau construction steps

# File input
python cli.py --file=formulas.txt         # Process formulas from file
```

### Creating Formula Files

Create a file `formulas.txt`:
```
# Test formulas - lines starting with # are comments
p & q
p | q
p -> q
~(p & q)
(p | q) & (~p | r)
```

Then run:
```bash
python cli.py --file=formulas.txt --models
```

This comprehensive tutorial system provides hands-on experience with tableau methods, progressing from basic concepts to advanced applications. Each tutorial builds on previous knowledge and includes practical exercises to reinforce learning.