# Tableau System Tutorials

**Version**: 3.0 (Consolidated Architecture)  
**Last Updated**: July 2025  
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

## Tutorial 6: Performance Optimization

**Goal**: Learn to optimize tableau performance for complex formulas and large-scale reasoning.

### Step 1: Understanding Performance Characteristics

```python
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
```

### Step 2: Optimization Strategies

```python
def optimize_formula_representation():
    """Learn techniques for optimizing formula representation"""
    
    print("=== FORMULA OPTIMIZATION STRATEGIES ===\n")
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    # Strategy 1: Convert to CNF for some cases
    print("Strategy 1: CNF Conversion Benefits")
    
    # Original formula
    original = Disjunction(
        Conjunction(p, q),
        Conjunction(Negation(p), r)
    )
    
    # CNF equivalent: (p ∨ ¬p ∨ r) ∧ (p ∨ r) ∧ (q ∨ ¬p ∨ r) ∧ (q ∨ r)
    # For demonstration, we'll test the original
    print(f"Original formula: {original}")
    time1, stats1 = measure_performance(original, "Original form")
    
    # Strategy 2: Factoring common subformulas
    print("\nStrategy 2: Factor Common Subformulas")
    
    # Instead of: (p ∧ q ∧ r) ∨ (p ∧ q ∧ s)
    # Use: p ∧ q ∧ (r ∨ s)
    s = Atom("s")
    
    unfactored = Disjunction(
        Conjunction(Conjunction(p, q), r),
        Conjunction(Conjunction(p, q), s)
    )
    
    factored = Conjunction(
        Conjunction(p, q),
        Disjunction(r, s)
    )
    
    print(f"Unfactored: {unfactored}")
    time2, stats2 = measure_performance(unfactored, "Unfactored")
    
    print(f"Factored: {factored}")
    time3, stats3 = measure_performance(factored, "Factored")
    
    improvement = ((time2 - time3) / time2) * 100 if time2 > 0 else 0
    print(f"\nFactoring improvement: {improvement:.1f}% faster")

def demonstrate_early_termination():
    """Show how early termination can improve performance"""
    
    print("\n=== EARLY TERMINATION STRATEGIES ===\n")
    
    p = Atom("p")
    q = Atom("q")
    
    # Create a formula that becomes unsatisfiable quickly
    contradiction = Conjunction(
        Conjunction(p, Negation(p)),  # This will close branches early
        Disjunction(q, Negation(q))   # This won't need to be processed
    )
    
    print("Early termination on contradiction:")
    measure_performance(contradiction, "Early contradiction detection")
    
    # Compare with a formula that requires full expansion
    tautology = Disjunction(
        Conjunction(p, q),
        Conjunction(Negation(p), Negation(q))
    )
    
    print("\nFull expansion required:")
    measure_performance(tautology, "Requires full expansion")

if __name__ == "__main__":
    optimize_formula_representation()
    demonstrate_early_termination()
```

### Step 3: Memory and Scaling Optimization

```python
def analyze_memory_usage():
    """Analyze memory usage patterns"""
    
    print("=== MEMORY USAGE ANALYSIS ===\n")
    
    import psutil
    import os
    
    def get_memory_usage():
        """Get current memory usage in MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    initial_memory = get_memory_usage()
    print(f"Initial memory usage: {initial_memory:.1f} MB")
    
    # Test with increasing formula complexity
    formulas = []
    
    # Build progressively larger formulas
    current_formula = p
    for i in range(3):
        # Create more complex formula
        current_formula = Conjunction(
            Disjunction(current_formula, q),
            Disjunction(Negation(current_formula), r)
        )
        formulas.append((f"Level {i+1}", current_formula))
    
    for description, formula in formulas:
        memory_before = get_memory_usage()
        
        tableau = classical_signed_tableau(T(formula))
        result = tableau.build()
        
        if result:
            models = tableau.extract_all_models()
            model_count = len(models)
        else:
            model_count = 0
        
        memory_after = get_memory_usage()
        memory_used = memory_after - memory_before
        
        print(f"{description}:")
        print(f"  Memory used: {memory_used:.1f} MB")
        print(f"  Models: {model_count}")
        print(f"  Result: {'SAT' if result else 'UNSAT'}")

def demonstrate_batch_optimization():
    """Show optimization techniques for processing multiple formulas"""
    
    print("\n=== BATCH PROCESSING OPTIMIZATION ===\n")
    
    # Create a batch of related formulas
    formulas = []
    atoms = [Atom(f"p{i}") for i in range(4)]
    
    # Generate various combinations
    for i in range(len(atoms)):
        for j in range(i+1, len(atoms)):
            # Create implications between pairs
            formula = Implication(atoms[i], atoms[j])
            formulas.append(formula)
    
    print(f"Processing batch of {len(formulas)} formulas...")
    
    # Method 1: Process each individually
    start_time = time.time()
    individual_results = []
    
    for formula in formulas:
        tableau = classical_signed_tableau(T(formula))
        result = tableau.build()
        individual_results.append(result)
    
    individual_time = time.time() - start_time
    
    print(f"Individual processing: {individual_time:.4f} seconds")
    print(f"Average per formula: {individual_time/len(formulas):.6f} seconds")
    print(f"Results: {sum(individual_results)} satisfiable out of {len(formulas)}")

if __name__ == "__main__":
    try:
        analyze_memory_usage()
    except ImportError:
        print("psutil not available - skipping memory analysis")
    
    demonstrate_batch_optimization()
```

### Exercise 6

1. Implement a tableau performance profiler that identifies bottlenecks
2. Create a formula complexity estimator that predicts construction time
3. Build an adaptive timeout system that adjusts based on formula characteristics

## Tutorial 7: Extending with New Logic Systems

**Goal**: Learn to extend the tableau system with new non-classical logics beyond WK3.

### Step 1: Understanding the Extension Architecture

```python
#!/usr/bin/env python3
"""Tutorial 7: Extending with New Logic Systems"""

from tableau_core import *
from unified_model import UnifiedModel
from typing import Dict, List, Union
import copy

class FourValuedTruthValue:
    """Four-valued truth system: TRUE, FALSE, BOTH, NEITHER"""
    
    def __init__(self, value: str):
        if value not in {'TRUE', 'FALSE', 'BOTH', 'NEITHER'}:
            raise ValueError(f"Invalid four-valued truth value: {value}")
        self.value = value
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f"FourValuedTruthValue('{self.value}')"
    
    def __eq__(self, other):
        return isinstance(other, FourValuedTruthValue) and self.value == other.value
    
    def __hash__(self):
        return hash(self.value)

# Four-valued truth constants
TRUE = FourValuedTruthValue('TRUE')
FALSE = FourValuedTruthValue('FALSE')
BOTH = FourValuedTruthValue('BOTH')
NEITHER = FourValuedTruthValue('NEITHER')

class FourValuedOperators:
    """Truth table operations for four-valued logic"""
    
    @staticmethod
    def negation(a: FourValuedTruthValue) -> FourValuedTruthValue:
        """Four-valued negation"""
        negation_table = {
            'TRUE': FALSE,   # ¬TRUE = FALSE
            'FALSE': TRUE,   # ¬FALSE = TRUE
            'BOTH': BOTH,    # ¬BOTH = BOTH (both true and false)
            'NEITHER': NEITHER  # ¬NEITHER = NEITHER (neither true nor false)
        }
        return negation_table[a.value]
    
    @staticmethod
    def conjunction(a: FourValuedTruthValue, b: FourValuedTruthValue) -> FourValuedTruthValue:
        """Four-valued conjunction"""
        # Truth table for A ∧ B
        table = {
            ('TRUE', 'TRUE'): TRUE,  ('TRUE', 'FALSE'): FALSE,  ('TRUE', 'BOTH'): BOTH,  ('TRUE', 'NEITHER'): NEITHER,
            ('FALSE', 'TRUE'): FALSE,  ('FALSE', 'FALSE'): FALSE,  ('FALSE', 'BOTH'): FALSE,  ('FALSE', 'NEITHER'): FALSE,
            ('BOTH', 'TRUE'): BOTH,  ('BOTH', 'FALSE'): FALSE,  ('BOTH', 'BOTH'): BOTH,  ('BOTH', 'NEITHER'): FALSE,
            ('NEITHER', 'TRUE'): NEITHER,  ('NEITHER', 'FALSE'): FALSE,  ('NEITHER', 'BOTH'): FALSE,  ('NEITHER', 'NEITHER'): NEITHER,
        }
        return table[(a.value, b.value)]
    
    @staticmethod
    def disjunction(a: FourValuedTruthValue, b: FourValuedTruthValue) -> FourValuedTruthValue:
        """Four-valued disjunction"""
        # Truth table for A ∨ B
        table = {
            ('TRUE', 'TRUE'): TRUE,  ('TRUE', 'FALSE'): TRUE,  ('TRUE', 'BOTH'): TRUE,  ('TRUE', 'NEITHER'): TRUE,
            ('FALSE', 'TRUE'): TRUE,  ('FALSE', 'FALSE'): FALSE,  ('FALSE', 'BOTH'): BOTH,  ('FALSE', 'NEITHER'): NEITHER,
            ('BOTH', 'TRUE'): TRUE,  ('BOTH', 'FALSE'): BOTH,  ('BOTH', 'BOTH'): BOTH,  ('BOTH', 'NEITHER'): BOTH,
            ('NEITHER', 'TRUE'): TRUE,  ('NEITHER', 'FALSE'): NEITHER,  ('NEITHER', 'BOTH'): BOTH,  ('NEITHER', 'NEITHER'): NEITHER,
        }
        return table[(a.value, b.value)]

def demonstrate_four_valued_logic():
    """Demonstrate four-valued logic truth tables"""
    
    print("=== FOUR-VALUED LOGIC DEMONSTRATION ===\n")
    
    values = [TRUE, FALSE, BOTH, NEITHER]
    value_names = ['TRUE', 'FALSE', 'BOTH', 'NEITHER']
    
    print("Truth values:")
    print("  TRUE = true only")
    print("  FALSE = false only") 
    print("  BOTH = both true and false")
    print("  NEITHER = neither true nor false")
    print()
    
    # Negation table
    print("Negation (¬):")
    for val, name in zip(values, value_names):
        neg_val = FourValuedOperators.negation(val)
        print(f"  ¬{name} = {neg_val}")
    print()
    
    # Conjunction table
    print("Conjunction (∧):")
    print("         | TRUE  | FALSE | BOTH  | NEITHER")
    print("  ---|---|---|---|---")
    for a, a_name in zip(values, value_names):
        row = f"   {a_name} |"
        for b in values:
            result = FourValuedOperators.conjunction(a, b)
            row += f" {result} |"
        print(row)
    print()
    
    # Disjunction table  
    print("Disjunction (∨):")
    print("     | T | F | B | N")
    print("  ---|---|---|---|---")
    for a, a_name in zip(values, value_names):
        row = f"   {a_name} |"
        for b in values:
            result = FourValuedOperators.disjunction(a, b)
            row += f" {result} |"
        print(row)

if __name__ == "__main__":
    demonstrate_four_valued_logic()
```

### Step 2: Implementing a Custom Model System

```python
class FourValuedModel(UnifiedModel):
    """Model for four-valued logic system"""
    
    def __init__(self, assignments: Dict[str, Union[FourValuedTruthValue, str]]):
        """Initialize with four-valued assignments"""
        self._assignments = {}
        for atom, value in assignments.items():
            if isinstance(value, FourValuedTruthValue):
                self._assignments[atom] = value
            elif isinstance(value, str) and value in ['T', 'F', 'B', 'N']:
                self._assignments[atom] = FourValuedTruthValue(value)
            else:
                raise ValueError(f"Invalid four-valued assignment: {atom}={value}")
    
    def satisfies(self, formula) -> FourValuedTruthValue:
        """Evaluate formula under four-valued semantics"""
        return self._evaluate_four_valued(formula)
    
    def is_satisfying(self, formula) -> bool:
        """Check if formula evaluates to TRUE or BOTH"""
        result = self._evaluate_four_valued(formula)
        return result.value in {'TRUE', 'BOTH'}
    
    def get_assignment(self, atom_name: str) -> FourValuedTruthValue:
        """Get four-valued assignment for atom"""
        return self._assignments.get(atom_name, NEITHER)
    
    @property
    def assignments(self) -> Dict[str, FourValuedTruthValue]:
        """Get all assignments"""
        return self._assignments.copy()
    
    def _evaluate_four_valued(self, formula) -> FourValuedTruthValue:
        """Evaluate formula using four-valued semantics"""
        # Get core types dynamically to handle different formula hierarchies
        from unified_model import _get_core_types
        CoreFormula, CoreAtom, CoreNegation, CoreConjunction, CoreDisjunction, CoreImplication = _get_core_types()
        
        # Handle both formula hierarchies
        atom_types = (Atom,) + ((CoreAtom,) if CoreAtom else ())
        negation_types = (Negation,) + ((CoreNegation,) if CoreNegation else ())
        conjunction_types = (Conjunction,) + ((CoreConjunction,) if CoreConjunction else ())
        disjunction_types = (Disjunction,) + ((CoreDisjunction,) if CoreDisjunction else ())
        
        if isinstance(formula, atom_types):
            return self._assignments.get(formula.name, NEITHER)
        elif isinstance(formula, negation_types):
            operand_value = self._evaluate_four_valued(formula.operand)
            return FourValuedOperators.negation(operand_value)
        elif isinstance(formula, conjunction_types):
            left_value = self._evaluate_four_valued(formula.left)
            right_value = self._evaluate_four_valued(formula.right)
            return FourValuedOperators.conjunction(left_value, right_value)
        elif isinstance(formula, disjunction_types):
            left_value = self._evaluate_four_valued(formula.left)
            right_value = self._evaluate_four_valued(formula.right)
            return FourValuedOperators.disjunction(left_value, right_value)
        else:
            # Default for unknown types
            return NEITHER
    
    def __str__(self) -> str:
        if not self._assignments:
            return "{}"
        
        sorted_items = sorted(self._assignments.items())
        assignment_strs = [f"{atom}={value}" for atom, value in sorted_items]
        return "{" + ", ".join(assignment_strs) + "}"
    
    def __repr__(self) -> str:
        return f"FourValuedModel({self._assignments})"

def demonstrate_four_valued_models():
    """Demonstrate four-valued model evaluation"""
    
    print("\n=== FOUR-VALUED MODEL EVALUATION ===\n")
    
    p = Atom("p")
    q = Atom("q")
    
    # Test different assignments
    test_assignments = [
        ("Both true", {"p": "TRUE", "q": "TRUE"}),
        ("Mixed values", {"p": "BOTH", "q": "FALSE"}),
        ("Neither values", {"p": "NEITHER", "q": "NEITHER"}),
        ("Inconsistent", {"p": "BOTH", "q": "BOTH"}),
    ]
    
    formula = Conjunction(p, q)
    print(f"Testing formula: {formula}")
    print()
    
    for description, assignment in test_assignments:
        model = FourValuedModel(assignment)
        result = model.satisfies(formula)
        
        print(f"{description}: {model}")
        print(f"  Formula evaluates to: {result}")
        print(f"  Classically satisfying: {model.is_satisfying(formula)}")
        print()

if __name__ == "__main__":
    demonstrate_four_valued_models()
```

### Step 3: Modal Logic Extension

```python
# Modal logic extension from Tutorial 7
class ModalFormula(Formula):
    """Base class for modal formulas"""
    pass

class Box(ModalFormula):
    """Necessity operator (□φ)"""
    
    def __init__(self, operand: Formula):
        self.operand = operand
    
    def is_atomic(self) -> bool:
        """Modal operators are not atomic"""
        return False
    
    def is_literal(self) -> bool:
        """Modal operators are not literals"""
        return False
    
    def __str__(self):
        return f"□{self.operand}"
    
    def __repr__(self):
        return f"Box({self.operand!r})"
    
    def __eq__(self, other):
        return isinstance(other, Box) and self.operand == other.operand
    
    def __hash__(self):
        return hash(('Box', self.operand))

class Diamond(ModalFormula):
    """Possibility operator (◇φ)"""
    
    def __init__(self, operand: Formula):
        self.operand = operand
    
    def is_atomic(self) -> bool:
        """Modal operators are not atomic"""
        return False
    
    def is_literal(self) -> bool:
        """Modal operators are not literals"""
        return False
    
    def __str__(self):
        return f"◇{self.operand}"
    
    def __repr__(self):
        return f"Diamond({self.operand!r})"
    
    def __eq__(self, other):
        return isinstance(other, Diamond) and self.operand == other.operand
    
    def __hash__(self):
        return hash(('Diamond', self.operand))

class ModalModel(UnifiedModel):
    """Simplified modal model with possible worlds"""
    
    def __init__(self, worlds: Dict[str, Dict[str, bool]], accessibility: Dict[str, List[str]], current_world: str = "w0"):
        self.worlds = worlds  # world -> {atom -> bool}
        self.accessibility = accessibility  # world -> [accessible_worlds]  
        self.current_world = current_world
    
    def add_world(self, world_name: str):
        """Add a possible world"""
        self.worlds.add(world_name)
        if world_name not in self.accessibility:
            self.accessibility[world_name] = set()
        if world_name not in self.valuations:
            self.valuations[world_name] = {}
    
    def add_accessibility(self, from_world: str, to_world: str):
        """Add accessibility relation between worlds"""
        if from_world not in self.worlds:
            self.add_world(from_world)
        if to_world not in self.worlds:
            self.add_world(to_world)
        self.accessibility[from_world].add(to_world)
    
    def set_valuation(self, world: str, atom: str, value: bool):
        """Set truth value of atom in a world"""
        if world not in self.worlds:
            self.add_world(world)
        self.valuations[world][atom] = value
    
    def evaluate_at_world(self, formula, world: str) -> bool:
        """Evaluate formula at a specific world"""
        if isinstance(formula, Atom):
            return self.valuations[world].get(formula.name, False)
        elif isinstance(formula, Negation):
            return not self.evaluate_at_world(formula.operand, world)
        elif isinstance(formula, Conjunction):
            return (self.evaluate_at_world(formula.left, world) and
                   self.evaluate_at_world(formula.right, world))
        elif isinstance(formula, Disjunction):
            return (self.evaluate_at_world(formula.left, world) or
                   self.evaluate_at_world(formula.right, world))
        # Add modal operators here when formula classes support them
        else:
            return False
    
    def demonstrate_modal_evaluation(self):
        """Show modal logic evaluation"""
        print("=== MODAL LOGIC EXTENSION DEMO ===\n")
        
        # Create a simple modal model
        self.add_world("w1")
        self.add_world("w2") 
        self.add_world("w3")
        
        # Add accessibility relations
        self.add_accessibility("w1", "w2")
        self.add_accessibility("w1", "w3")
        self.add_accessibility("w2", "w3")
        
        # Set valuations
        self.set_valuation("w1", "p", True)
        self.set_valuation("w2", "p", False)
        self.set_valuation("w3", "p", True)
        
        print("Modal model:")
        print(f"Worlds: {sorted(self.worlds)}")
        for world in sorted(self.worlds):
            accessible = sorted(self.accessibility[world])
            print(f"  {world} → {accessible}")
        print()
        
        print("Valuations:")
        for world in sorted(self.worlds):
            p_val = self.valuations[world].get("p", False)
            print(f"  {world}: p = {p_val}")
        print()
        
        # Test basic formula evaluation
        p = Atom("p")
        for world in sorted(self.worlds):
            result = self.evaluate_at_world(p, world)
            print(f"p at {world}: {result}")

def demonstrate_logic_system_comparison():
    """Compare different logic systems on the same formulas"""
    
    print("\n=== LOGIC SYSTEM COMPARISON ===\n")
    
    p = Atom("p")
    test_formulas = [
        ("Simple atom", p),
        ("Contradiction", Conjunction(p, Negation(p))),
        ("Tautology", Disjunction(p, Negation(p))),
    ]
    
    for description, formula in test_formulas:
        print(f"Testing: {description} ({formula})")
        
        # Classical logic
        classical_tableau = classical_signed_tableau(T(formula))
        classical_sat = classical_tableau.build()
        
        # WK3 logic
        from wk3_tableau import WK3Tableau
        wk3_tableau = WK3Tableau(formula)
        wk3_sat = wk3_tableau.build()
        
        # Four-valued logic (simplified - just test with one assignment)
        fv_model = FourValuedModel({"p": "B"})  # Both true and false
        fv_result = fv_model.satisfies(formula)
        
        print(f"  Classical: {'SAT' if classical_sat else 'UNSAT'}")
        print(f"  WK3: {'SAT' if wk3_sat else 'UNSAT'}")
        print(f"  Four-valued (p=B): {fv_result}")
        print()

if __name__ == "__main__":
    # Demonstrate modal logic
    modal = ModalLogicExtension()
    modal.demonstrate_modal_evaluation()
    
    # Compare logic systems
    demonstrate_logic_system_comparison()
```

### Exercise 7

1. Implement a complete many-valued logic system (e.g., Łukasiewicz three-valued logic)
2. Add modal operators (□ and ◇) to the formula hierarchy and implement tableau rules
3. Create a logic system registry that allows dynamic loading of new logic systems
4. Build a tableau rule generator that creates rules based on truth table specifications

### Advanced Integration Example

```python
def create_custom_logic_system():
    """Example of creating a complete custom logic system"""
    
    print("=== CUSTOM LOGIC SYSTEM INTEGRATION ===\n")
    
    # This would integrate with the existing tableau framework
    # For now, we demonstrate the concept
    
    class CustomLogicRegistry:
        """Registry for custom logic systems"""
        
        def __init__(self):
            self.systems = {}
        
        def register_system(self, name: str, model_class, operators):
            """Register a new logic system"""
            self.systems[name] = {
                'model_class': model_class,
                'operators': operators,
                'description': f"Custom logic system: {name}"
            }
        
        def list_systems(self):
            """List all registered systems"""
            print("Available logic systems:")
            for name, info in self.systems.items():
                print(f"  {name}: {info['description']}")
    
    # Create registry and register our four-valued system
    registry = CustomLogicRegistry()
    registry.register_system("four_valued", FourValuedModel, FourValuedOperators)
    registry.register_system("classical", ClassicalModel, None)
    
    registry.list_systems()
    
    print("\nCustom logic systems can be seamlessly integrated")
    print("with the existing tableau framework through:")
    print("1. Unified model interface")
    print("2. Pluggable truth value systems") 
    print("3. Extensible rule systems")
    print("4. Consistent API across all logics")

if __name__ == "__main__":
    create_custom_logic_system()
```

### Exercise 7

1. Implement tableau rules for your four-valued logic system
2. Create a complete modal logic extension with □ and ◇ operators
3. Build a fuzzy logic system with continuous truth values [0,1]
4. Design a temporal logic system with "next" and "until" operators

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