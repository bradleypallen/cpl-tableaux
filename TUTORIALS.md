# Tableau System Tutorials

**Version**: 4.0 (Unified Implementation)  
**Last Updated**: December 2024  
**License**: MIT  

## Table of Contents

1. [Getting Started](#getting-started)
2. [Tutorial 1: Basic Satisfiability Testing](#tutorial-1-basic-satisfiability-testing)
3. [Tutorial 2: Understanding Signed Tableaux with Visualization](#tutorial-2-understanding-signed-tableaux-with-visualization)
4. [Tutorial 3: Three-Valued Logic Exploration](#tutorial-3-three-valued-logic-exploration)
5. [Tutorial 4: Ferguson's Epistemic Logic](#tutorial-4-fergusons-epistemic-logic)
6. [Tutorial 5: Model Extraction and Analysis](#tutorial-5-model-extraction-and-analysis)
7. [Tutorial 6: First-Order Logic](#tutorial-6-first-order-logic)
8. [Tutorial 7: Performance Analysis and Optimization](#tutorial-7-performance-analysis-and-optimization)
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
# Should show tests passing
```

### Verify Your Setup

```python
# test_setup.py
from tableau_core import Atom, classical_signed_tableau, T

# Create a simple formula
p = Atom("p")
tableau = classical_signed_tableau(T(p))
result = tableau.build()

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
    
    tableau = classical_signed_tableau(T(p))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        print(f"Model: {models[0].assignment}")
    print()
    
    # Example 2: Conjunction - satisfiable if both parts can be true
    print("Example 2: Conjunction")
    conjunction = Conjunction(p, q)
    print(f"Formula: {conjunction}")
    
    tableau = classical_signed_tableau(T(conjunction))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        print(f"Model: {models[0].assignment}")
    print()
    
    # Example 3: Contradiction - never satisfiable
    print("Example 3: Contradiction")
    contradiction = Conjunction(p, Negation(p))
    print(f"Formula: {contradiction}")
    
    tableau = classical_signed_tableau(T(contradiction))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be False
    print()
    
    # Example 4: Tautology - always satisfiable
    print("Example 4: Tautology")
    tautology = Disjunction(p, Negation(p))
    print(f"Formula: {tautology}")
    
    tableau = classical_signed_tableau(T(tautology))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be True
    if result:
        models = tableau.extract_all_models()
        print(f"Number of models: {len(models)}")
    print()

def test_implication_examples():
    """Explore implication satisfiability."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("=== IMPLICATION EXAMPLES ===\n")
    
    # Example 1: Simple implication
    print("Example 1: p → q")
    implication = Implication(p, q)
    
    tableau = classical_signed_tableau(T(implication))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        print(f"Found {len(models)} models:")
        for i, model in enumerate(models):
            print(f"  Model {i+1}: {model.assignment}")
    print()
    
    # Example 2: Modus ponens test
    print("Example 2: Modus ponens - p, p → q, ¬q")
    formulas = [T(p), T(implication), T(Negation(q))]
    
    tableau = classical_signed_tableau(formulas)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be False (contradiction)
    print()

if __name__ == "__main__":
    test_satisfiability_examples()
    test_implication_examples()
```

### Step 2: Running Your First Examples

Save the code above as `tutorial1_test.py` and run:

```bash
python tutorial1_test.py
```

**Expected Output:**
```
=== SATISFIABILITY EXAMPLES ===

Example 1: Simple atom
Formula: p
Satisfiable: True
Model: {'p': True}

Example 2: Conjunction
Formula: p ∧ q
Satisfiable: True
Model: {'p': True, 'q': True}

Example 3: Contradiction
Formula: p ∧ ¬p
Satisfiable: False

Example 4: Tautology
Formula: p ∨ ¬p
Satisfiable: True
Number of models: 2
```

## Tutorial 2: Understanding Signed Tableaux with Visualization

**Goal**: Learn how tableau construction works with step-by-step visualization.

### Step 1: Basic Tableau Visualization

The unified implementation includes powerful visualization features:

```python
#!/usr/bin/env python3
"""Tutorial 2: Signed Tableaux with Visualization"""

from tableau_core import Atom, Conjunction, Disjunction, Implication, Negation
from tableau_core import T, F, classical_signed_tableau

def visualize_simple_tableau():
    """Show tableau construction step-by-step."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("=== TABLEAU VISUALIZATION EXAMPLE ===\n")
    
    # Create a formula that will require branching
    # F:(p ∨ q) means "p ∨ q is false"
    formula = Disjunction(p, q)
    
    print(f"Testing: F:({formula})")
    print("This means: 'p ∨ q must be false'")
    print("For this to be true, both p and q must be false.\n")
    
    # Create tableau with step tracking enabled
    tableau = classical_signed_tableau(F(formula), track_steps=True)
    result = tableau.build()
    
    print(f"Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}\n")
    
    # Show the step-by-step construction
    tableau.print_construction_steps("F:(p ∨ q) Tableau Construction")

def visualize_branching_tableau():
    """Show a more complex example with multiple branches."""
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    print("\n=== COMPLEX BRANCHING EXAMPLE ===\n")
    
    # T:(p ∨ q) ∧ T:(r ∨ ¬p)
    # This will create multiple branches
    formula1 = Disjunction(p, q)
    formula2 = Disjunction(r, Negation(p))
    
    formulas = [T(formula1), T(formula2)]
    
    print("Testing multiple formulas:")
    for i, f in enumerate(formulas):
        print(f"  {i+1}. {f}")
    print()
    
    tableau = classical_signed_tableau(formulas, track_steps=True)
    result = tableau.build()
    
    print(f"Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}\n")
    
    # Show detailed construction
    tableau.print_construction_steps("Complex Tableau Construction")
    
    # Show final models
    if result:
        models = tableau.extract_all_models()
        print(f"\nFound {len(models)} satisfying models:")
        for i, model in enumerate(models):
            print(f"Model {i+1}: {model.assignment}")

def visualize_contradiction():
    """Show how contradictions are detected."""
    
    p = Atom("p")
    
    print("\n=== CONTRADICTION DETECTION ===\n")
    
    # Create a clear contradiction: T:p and F:p
    formulas = [T(p), F(p)]
    
    print("Testing contradiction: T:p ∧ F:p")
    print("This says 'p is true AND p is false' - impossible!\n")
    
    tableau = classical_signed_tableau(formulas, track_steps=True)
    result = tableau.build()
    
    print(f"Result: {'SATISFIABLE' if result else 'UNSATISFIABLE'}\n")
    
    tableau.print_construction_steps("Contradiction Detection")

if __name__ == "__main__":
    visualize_simple_tableau()
    visualize_branching_tableau()
    visualize_contradiction()
```

### Step 2: Understanding the Output

When you run this tutorial, you'll see output like:

```
Step 1: Initialize tableau with given formulas
Initial formulas:
  • F:p ∨ q
Tableau tree structure:
└── Branch 0 ○
    └─ F:p ∨ q

Step 2: Apply F-Disjunction (α) to F:p ∨ q
Rule applied: F-Disjunction (α)
New formulas added:
  • F:p
  • F:q
Tableau tree structure:
└── Branch 0 ○
    ├─ F:p ∨ q
    ├─ F:p
    └─ F:q
Current state: 1 open, 0 closed
```

**Key Points:**
- **α-rules** (like F-Disjunction) extend the current branch
- **β-rules** (like T-Disjunction) create multiple branches
- **○** indicates open branches, **✗** indicates closed branches
- Tree structure shows parent-child relationships

## Tutorial 3: Three-Valued Logic Exploration

**Goal**: Understand how three-valued logic differs from classical logic.

### Step 1: Introduction to Weak Kleene Logic

```python
#!/usr/bin/env python3
"""Tutorial 3: Three-Valued Logic (WK3)"""

from tableau_core import Atom, Conjunction, Disjunction, Negation
from tableau_core import T, F, classical_signed_tableau, wk3_satisfiable, wk3_models
from tableau_core import TruthValue, t, f, e

def compare_classical_vs_wk3():
    """Compare classical and WK3 logic on key examples."""
    
    p = Atom("p")
    
    print("=== CLASSICAL vs WK3 COMPARISON ===\n")
    
    # Example 1: Contradiction in classical logic
    print("Example 1: p ∧ ¬p (Classical contradiction)")
    contradiction = Conjunction(p, Negation(p))
    
    # Classical logic
    classical_tableau = classical_signed_tableau(T(contradiction))
    classical_result = classical_tableau.build()
    
    # WK3 logic
    wk3_result = wk3_satisfiable(contradiction)
    
    print(f"Classical satisfiable: {classical_result}")  # False
    print(f"WK3 satisfiable: {wk3_result}")  # True
    
    if wk3_result:
        models = wk3_models(contradiction)
        print(f"WK3 models: {len(models)}")
        for model in models:
            p_val = model.get_assignment("p")
            result = model.satisfies(contradiction) 
            print(f"  p={p_val}, formula evaluates to {result}")
    print()
    
    # Example 2: Excluded middle
    print("Example 2: p ∨ ¬p (Excluded middle)")
    excluded_middle = Disjunction(p, Negation(p))
    
    classical_tableau = classical_signed_tableau(T(excluded_middle))
    classical_result = classical_tableau.build()
    
    wk3_result = wk3_satisfiable(excluded_middle)
    
    print(f"Classical satisfiable: {classical_result}")  # True
    print(f"WK3 satisfiable: {wk3_result}")  # True
    
    if wk3_result:
        models = wk3_models(excluded_middle)
        print(f"WK3 models: {len(models)}")
        for model in models:
            p_val = model.get_assignment("p")
            result = model.satisfies(excluded_middle)
            print(f"  p={p_val}, formula evaluates to {result}")
    print()

def explore_wk3_truth_tables():
    """Demonstrate WK3 truth tables."""
    
    from tableau_core import WeakKleeneOperators
    
    print("=== WK3 TRUTH TABLES ===\n")
    
    print("Negation (¬):")
    print("  ¬t = f")
    print("  ¬f = t") 
    print("  ¬e = e  (undefined remains undefined)")
    print()
    
    print("Conjunction (∧) - any operation with 'e' returns 'e':")
    values = [t, f, e]
    for a in values:
        for b in values:
            result = WeakKleeneOperators.conjunction(a, b)
            print(f"  {a} ∧ {b} = {result}")
    print()
    
    print("Key insight: In Weak Kleene logic, undefined values 'contaminate'")
    print("all operations - any operation involving 'e' returns 'e'.")
    print("This is different from Strong Kleene logic.")

def test_wk3_formulas():
    """Test various formulas in WK3."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("\n=== WK3 FORMULA TESTING ===\n")
    
    formulas = [
        ("p → p", Implication(p, p)),
        ("p ∨ ¬p", Disjunction(p, Negation(p))),
        ("(p ∧ q) → p", Implication(Conjunction(p, q), p)),
        ("p → (p ∨ q)", Implication(p, Disjunction(p, q)))
    ]
    
    for name, formula in formulas:
        print(f"Testing: {name}")
        
        # Classical
        classical_tableau = classical_signed_tableau(T(formula))
        classical_result = classical_tableau.build()
        
        # WK3
        wk3_result = wk3_satisfiable(formula)
        wk3_model_count = len(wk3_models(formula)) if wk3_result else 0
        
        print(f"  Classical: {'✓' if classical_result else '✗'}")
        print(f"  WK3: {'✓' if wk3_result else '✗'} ({wk3_model_count} models)")
        print()

if __name__ == "__main__":
    compare_classical_vs_wk3()
    explore_wk3_truth_tables()
    test_wk3_formulas()
```

## Tutorial 4: Ferguson's Epistemic Logic

**Goal**: Explore epistemic reasoning with Ferguson's wKrQ system.

### Step 1: Understanding Epistemic Signs

```python
#!/usr/bin/env python3
"""Tutorial 4: Ferguson's wKrQ Epistemic Logic"""

from tableau_core import Atom, Conjunction, Disjunction, Implication, Negation
from tableau_core import TF, FF, M, N, wkrq_signed_tableau, ferguson_signed_tableau

def epistemic_basics():
    """Understand the four epistemic signs."""
    
    p = Atom("p")
    
    print("=== FERGUSON'S wKrQ SIGNS ===\n")
    
    print("T: Definitely true (classical true)")
    print("F: Definitely false (classical false)")
    print("M: May be true (epistemic possibility)")
    print("N: Need not be true (epistemic possibility of falsehood)")
    print()
    
    print("Key insight: M and N represent epistemic uncertainty")
    print("and can coexist without contradiction!\n")
    
    # Test epistemic uncertainty
    print("Example 1: Epistemic uncertainty - M:p ∧ N:p")
    formulas = [M(p), N(p)]
    
    tableau = ferguson_signed_tableau(formulas, track_steps=True)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be True
    print("Explanation: Both express uncertainty about p's truth value\n")
    
    # Show construction
    tableau.print_construction_steps("Epistemic Uncertainty Example")

def epistemic_vs_classical():
    """Compare epistemic and classical contradictions."""
    
    p = Atom("p")
    
    print("\n=== EPISTEMIC vs CLASSICAL CONTRADICTIONS ===\n")
    
    # Classical contradiction: T:p ∧ F:p
    print("Classical contradiction: T:p ∧ F:p")
    formulas = [TF(p), FF(p)]
    
    tableau = ferguson_signed_tableau(formulas, track_steps=True)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be False
    print("Explanation: Definite truth and falsehood contradict\n")
    
    # Mixed epistemic-classical
    print("Mixed case: T:p ∧ M:p")
    formulas = [TF(p), M(p)]
    
    tableau = ferguson_signed_tableau(formulas)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")  # Should be True
    print("Explanation: Definite truth is consistent with possibility\n")

def epistemic_reasoning_examples():
    """Explore complex epistemic reasoning."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("=== COMPLEX EPISTEMIC REASONING ===\n")
    
    # Example 1: Epistemic disjunction
    print("Example 1: M:(p ∨ q) - 'p or q may be true'")
    disjunction = Disjunction(p, q)
    
    tableau = ferguson_signed_tableau(M(disjunction), track_steps=True)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    print("Shows epistemic uncertainty about disjunction\n")
    
    # Example 2: Mixed definite and epistemic
    print("Example 2: T:p ∧ M:q ∧ N:q")
    print("'p is definitely true, q may be true, q need not be true'")
    
    formulas = [TF(p), M(q), N(q)]
    tableau = ferguson_signed_tableau(formulas)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    print("Definite knowledge coexists with epistemic uncertainty\n")

if __name__ == "__main__":
    epistemic_basics()
    epistemic_vs_classical()
    epistemic_reasoning_examples()
```

## Tutorial 5: Model Extraction and Analysis

**Goal**: Learn to extract and analyze satisfying models.

```python
#!/usr/bin/env python3
"""Tutorial 5: Model Extraction and Analysis"""

from tableau_core import Atom, Conjunction, Disjunction, Implication, Negation
from tableau_core import T, F, classical_signed_tableau, wk3_models

def analyze_classical_models():
    """Extract and analyze classical logic models."""
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    print("=== CLASSICAL MODEL ANALYSIS ===\n")
    
    # Example: CNF formula with multiple models
    # (p ∨ q) ∧ (¬p ∨ r)
    clause1 = Disjunction(p, q)
    clause2 = Disjunction(Negation(p), r)
    formula = Conjunction(clause1, clause2)
    
    print(f"Formula: {formula}")
    print("This is satisfiable when:")
    print("  Case 1: p=False, q=True, r=any")
    print("  Case 2: p=True, q=any, r=True")
    print()
    
    tableau = classical_signed_tableau(T(formula))
    result = tableau.build()
    
    if result:
        models = tableau.extract_all_models()
        print(f"Found {len(models)} models:")
        
        for i, model in enumerate(models):
            print(f"Model {i+1}: {model.assignment}")
            
            # Verify model satisfies formula
            satisfies = model.satisfies(formula)
            print(f"  Satisfies formula: {satisfies}")
        print()
    
    # Analyze each clause
    print("Clause analysis:")
    for i, model in enumerate(models):
        print(f"Model {i+1}:")
        
        # Check clause1: p ∨ q
        clause1_result = model.satisfies(clause1)
        print(f"  (p ∨ q): {clause1_result}")
        
        # Check clause2: ¬p ∨ r  
        clause2_result = model.satisfies(clause2)
        print(f"  (¬p ∨ r): {clause2_result}")
        print()

def analyze_wk3_models():
    """Analyze three-valued models."""
    
    p = Atom("p")
    q = Atom("q")
    
    print("=== WK3 MODEL ANALYSIS ===\n")
    
    # Formula that has different behavior in WK3
    # p → q (implication)
    formula = Implication(p, q)
    
    print(f"Formula: {formula}")
    print("In WK3, this can be satisfied in various ways including")
    print("when p or q (or both) are undefined.\n")
    
    models = wk3_models(formula)
    print(f"Found {len(models)} WK3 models:")
    
    for i, model in enumerate(models):
        p_val = model.get_assignment("p")
        q_val = model.get_assignment("q")
        result = model.satisfies(formula)
        
        print(f"Model {i+1}: p={p_val}, q={q_val} → formula={result}")
    print()
    
    # Show which assignments DON'T satisfy
    print("Non-satisfying assignments (formula evaluates to 'f'):")
    from tableau_core import t, f, e
    all_assignments = [
        (t, t), (t, f), (t, e),
        (f, t), (f, f), (f, e),
        (e, t), (e, f), (e, e)
    ]
    
    from tableau_core import WK3Model, WeakKleeneOperators
    
    for p_val, q_val in all_assignments:
        model = WK3Model({"p": p_val, "q": q_val})
        result = model.satisfies(formula)
        
        if result == f:
            print(f"  p={p_val}, q={q_val} → {result}")

def model_comparison():
    """Compare models across logic systems."""
    
    p = Atom("p")
    
    print("\n=== MODEL COMPARISON ACROSS LOGICS ===\n")
    
    # Test excluded middle: p ∨ ¬p
    formula = Disjunction(p, Negation(p))
    
    print(f"Formula: {formula}")
    print()
    
    # Classical models
    classical_tableau = classical_signed_tableau(T(formula))
    classical_result = classical_tableau.build()
    
    if classical_result:
        classical_models = classical_tableau.extract_all_models()
        print(f"Classical models ({len(classical_models)}):")
        for model in classical_models:
            print(f"  {model.assignment}")
    print()
    
    # WK3 models
    wk3_model_list = wk3_models(formula)
    print(f"WK3 models ({len(wk3_model_list)}):")
    for model in wk3_model_list:
        p_val = model.get_assignment("p")
        result = model.satisfies(formula)
        print(f"  p={p_val} → formula={result}")
    print()
    
    print("Key difference: WK3 has an additional model where p=e (undefined)")
    print("and the formula still evaluates to e (which is considered satisfying).")

if __name__ == "__main__":
    analyze_classical_models()
    analyze_wk3_models()
    model_comparison()
```

## Tutorial 6: First-Order Logic

**Goal**: Work with predicates, constants, and variables.

```python
#!/usr/bin/env python3
"""Tutorial 6: First-Order Logic"""

from tableau_core import Predicate, Constant, Variable, Implication
from tableau_core import T, F, classical_signed_tableau

def first_order_basics():
    """Basic first-order logic concepts."""
    
    print("=== FIRST-ORDER LOGIC BASICS ===\n")
    
    # Create terms
    tweety = Constant("tweety")
    x = Variable("x")
    
    # Create predicates
    Bird = lambda term: Predicate("Bird", [term])
    Flies = lambda term: Predicate("Flies", [term])
    
    print("Terms:")
    print(f"  Constant: {tweety}")
    print(f"  Variable: {x}")
    print()
    
    print("Predicates:")
    print(f"  Bird(tweety): {Bird(tweety)}")
    print(f"  Flies(tweety): {Flies(tweety)}")
    print()
    
    # Test simple predicate satisfiability
    print("Testing: T:Bird(tweety)")
    tableau = classical_signed_tableau(T(Bird(tweety)))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        print(f"Model: {models[0].assignment}")
    print()

def predicate_logic_reasoning():
    """More complex predicate logic reasoning."""
    
    print("=== PREDICATE LOGIC REASONING ===\n")
    
    # Domain: animals
    tweety = Constant("tweety")
    polly = Constant("polly")
    
    # Predicates
    Bird = lambda x: Predicate("Bird", [x])
    Flies = lambda x: Predicate("Flies", [x])
    Penguin = lambda x: Predicate("Penguin", [x])
    
    print("Domain setup:")
    print("  Constants: tweety, polly")
    print("  Predicates: Bird(x), Flies(x), Penguin(x)")
    print()
    
    # Example 1: Simple implication
    print("Example 1: Bird(tweety) → Flies(tweety)")
    rule1 = Implication(Bird(tweety), Flies(tweety))
    
    tableau = classical_signed_tableau(T(rule1))
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        print(f"Found {len(models)} models")
        for model in models:
            print(f"  {model.assignment}")
    print()
    
    # Example 2: Multiple individuals
    print("Example 2: Bird(tweety) ∧ ¬Flies(polly)")
    formulas = [T(Bird(tweety)), T(Negation(Flies(polly)))]
    
    tableau = classical_signed_tableau(formulas)
    result = tableau.build()
    
    print(f"Satisfiable: {result}")
    if result:
        models = tableau.extract_all_models()
        for model in models:
            print(f"  {model.assignment}")
    print()

def test_logical_validity():
    """Test logical validity using unsatisfiability."""
    
    print("=== TESTING LOGICAL VALIDITY ===\n")
    
    tweety = Constant("tweety")
    Human = lambda x: Predicate("Human", [x])
    Mortal = lambda x: Predicate("Mortal", [x])
    
    print("Testing validity of: Human(tweety) → Mortal(tweety)")
    print("Method: Try to satisfy the negation")
    print("If negation is unsatisfiable, original is valid\n")
    
    # Create the implication
    implication = Implication(Human(tweety), Mortal(tweety))
    
    # Test satisfiability of negation
    # ¬(Human(tweety) → Mortal(tweety)) ≡ Human(tweety) ∧ ¬Mortal(tweety)
    negation_formulas = [T(Human(tweety)), T(Negation(Mortal(tweety)))]
    
    tableau = classical_signed_tableau(negation_formulas)
    result = tableau.build()
    
    print(f"Negation satisfiable: {result}")
    
    if result:
        print("Original implication is NOT valid (contingent)")
        models = tableau.extract_all_models()
        print("Countermodel where implication fails:")
        for model in models:
            print(f"  {model.assignment}")
    else:
        print("Original implication is VALID (tautology)")
    print()
    
    print("This shows the implication is contingent - it depends on")
    print("the specific interpretation of Human and Mortal predicates.")

if __name__ == "__main__":
    first_order_basics()
    predicate_logic_reasoning()
    test_logical_validity()
```

## Tutorial 7: Performance Analysis and Optimization

**Goal**: Understand performance characteristics and optimization techniques.

```python
#!/usr/bin/env python3
"""Tutorial 7: Performance Analysis"""

import time
from tableau_core import Atom, Conjunction, Disjunction, classical_signed_tableau, T

def performance_comparison():
    """Compare performance across different formula sizes."""
    
    print("=== PERFORMANCE ANALYSIS ===\n")
    
    sizes = [5, 10, 15, 20]
    
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
    atoms = [Atom(f"p{i}") for i in range(8)]
    
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
```

## CLI Usage Guide

The unified system includes a powerful command-line interface:

### Basic CLI Usage

```bash
# Classical logic satisfiability
python cli.py "p | ~p"                    # Tautology
python cli.py "p & ~p"                    # Contradiction

# Three-valued logic
python cli.py --wk3 "p | ~p"              # WK3 satisfiability
python cli.py --wk3 "p & ~p"              # WK3 satisfiability

# Interactive mode
python cli.py                             # Start interactive session
```

### Interactive Mode

In interactive mode, you can:

```
> p -> q
Satisfiable: True
Models: [{'p': False, 'q': False}, {'p': False, 'q': True}, {'p': True, 'q': True}]

> :wk3 p -> q  
WK3 Satisfiable: True
WK3 Models: 7 models (including undefined assignments)

> :help
Available commands:
  :wk3 <formula>    - Test in WK3 logic
  :quit            - Exit
  <formula>        - Test in classical logic
```

## Advanced Applications

### Building a SAT Solver

```python
def simple_sat_solver(cnf_clauses):
    """Simple SAT solver using tableau method."""
    
    # Convert CNF clauses to tableau formula
    tableau_formula = None
    for clause in cnf_clauses:
        clause_formula = None
        for literal in clause:
            atom = Atom(abs(literal))
            lit_formula = atom if literal > 0 else Negation(atom)
            
            if clause_formula is None:
                clause_formula = lit_formula
            else:
                clause_formula = Disjunction(clause_formula, lit_formula)
        
        if tableau_formula is None:
            tableau_formula = clause_formula
        else:
            tableau_formula = Conjunction(tableau_formula, clause_formula)
    
    # Use tableau to solve
    tableau = classical_signed_tableau(T(tableau_formula))
    result = tableau.build()
    
    if result:
        models = tableau.extract_all_models()
        return models[0].assignment  # Return first satisfying assignment
    else:
        return None  # UNSAT

# Example usage
cnf = [[1, 2], [-1, 3], [-2, -3]]  # (p1 ∨ p2) ∧ (¬p1 ∨ p3) ∧ (¬p2 ∨ ¬p3)
solution = simple_sat_solver(cnf)
print(f"SAT solution: {solution}")
```

### Educational Logic Tutor

```python
def logic_tutor():
    """Interactive logic learning system."""
    
    print("Welcome to the Logic Tutor!")
    print("Enter formulas to learn about satisfiability")
    print("Type 'help' for commands, 'quit' to exit\n")
    
    while True:
        user_input = input("Formula> ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'help':
            print("Commands:")
            print("  help - Show this help")
            print("  quit - Exit tutor")
            print("  <formula> - Test formula satisfiability")
            print("Examples: 'p & q', 'p -> q', '~(p & ~p)'")
            continue
        
        try:
            # Parse and test formula (simplified parser)
            tableau = classical_signed_tableau(T(parse_formula(user_input)))
            result = tableau.build()
            
            print(f"Satisfiable: {result}")
            
            if result:
                models = tableau.extract_all_models()
                print(f"Models ({len(models)}):")
                for model in models:
                    print(f"  {model.assignment}")
            else:
                print("This formula is unsatisfiable (contradiction)")
            print()
            
        except Exception as e:
            print(f"Error: {e}")
            print("Please check formula syntax\n")

# Run the tutor
if __name__ == "__main__":
    logic_tutor()
```

## Conclusion

These tutorials demonstrate the power and flexibility of the unified tableau system. Key takeaways:

1. **Unified Architecture**: Single module handles all logic systems
2. **Rich Visualization**: Step-by-step construction with tree structure
3. **Multiple Logics**: Classical, WK3, and Ferguson's epistemic logic
4. **Industrial Performance**: Optimized algorithms with O(1) closure detection
5. **Educational Value**: Clear visualizations aid understanding
6. **Extensibility**: Framework supports adding new logic systems

The system provides both theoretical rigor and practical utility, making it suitable for research, education, and practical applications in automated reasoning.