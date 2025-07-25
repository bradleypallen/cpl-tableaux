# API Reference: Unified Tableau System

**Version**: 4.0 (Unified Implementation)  
**Last Updated**: July 2025  
**License**: MIT  

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core API Functions](#core-api-functions)
3. [OptimizedTableauEngine Class](#optimizedtableauengine-class)
4. [Data Structures](#data-structures)
5. [Logic Systems](#logic-systems)
6. [Visualization Features](#visualization-features)
7. [Extension Framework](#extension-framework)
8. [Complete Examples](#complete-examples)

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/bradleypallen/tableaux.git
cd tableaux

# Verify installation
python -m pytest --tb=no -q
```

### Basic Usage

```python
from tableau_core import (
    # Formula construction
    Atom, Conjunction, Disjunction, Negation, Implication,
    # Signs
    T, F, T3, F3, U, TF, FF, M, N,
    # Truth values
    t, f, e,
    # Tableau functions
    classical_signed_tableau, three_valued_signed_tableau, T3, U
)

# Create formulas
p = Atom("p")
q = Atom("q")
formula = Implication(p, Disjunction(p, q))

# Classical logic with visualization
tableau = classical_signed_tableau(T(formula), track_steps=True)
satisfiable = tableau.build()
print(f"Satisfiable: {satisfiable}")

# Show step-by-step construction
tableau.print_construction_steps()

# Extract models if satisfiable
if satisfiable:
    models = tableau.extract_all_models()
    print(f"Found {len(models)} models")

# Three-valued logic (weak Kleene)
# weak Kleene satisfiability using tableau approach
t3_tableau = three_valued_signed_tableau(T3(formula))
u_tableau = three_valued_signed_tableau(U(formula))
wk3_result = t3_tableau.build() or u_tableau.build()
print(f"weak Kleene satisfiable: {wk3_result}")
```

## Core API Functions

### Classical Logic Functions

#### `classical_signed_tableau(formulas, track_steps=False)`

Create a classical logic tableau engine with optional step tracking.

**Parameters:**
- `formulas`: `SignedFormula` or `List[SignedFormula]` - Initial signed formulas
- `track_steps`: `bool` - Enable step-by-step visualization (default: False)

**Returns:**
- `OptimizedTableauEngine` - Configured tableau engine

**Example:**
```python
from tableau_core import T, F, classical_signed_tableau, Atom

# Single formula with visualization
tableau = classical_signed_tableau(T(Atom("p")), track_steps=True)

# Multiple formulas
tableau = classical_signed_tableau([T(Atom("p")), F(Atom("q"))])

# Build and show results
result = tableau.build()
if tableau.track_construction:
    tableau.print_construction_steps()
```

#### `three_valued_signed_tableau(formulas, track_steps=False)`

Create a three-valued logic tableau engine.

**Parameters:**
- `formulas`: `SignedFormula` or `List[SignedFormula]` - Initial signed formulas
- `track_steps`: `bool` - Enable step-by-step visualization

**Returns:**
- `OptimizedTableauEngine` - Engine configured for three-valued logic

**Example:**
```python
from tableau_core import T3, F3, U, three_valued_signed_tableau

p = Atom("p")
tableau = three_valued_signed_tableau([T3(p), U(p)], track_steps=True)
result = tableau.build()
```

### Three-Valued Logic Functions

#### weak Kleene Satisfiability Check (Tableau Approach)

Check weak Kleene satisfiability using the tableau method.

**Approach:**
A formula is weak Kleene-satisfiable if it can be either **true** (T3) or **undefined** (U).

**Algorithm:**
1. Create tableau for `T3(formula)` (can the formula be true?)
2. Create tableau for `U(formula)` (can the formula be undefined?)
3. Formula is satisfiable if either tableau succeeds

**Example:**
```python
from tableau_core import three_valued_signed_tableau, T3, U, Conjunction, Negation, Atom

p = Atom("p")
contradiction = Conjunction(p, Negation(p))

# Classical: unsatisfiable
tableau = classical_signed_tableau(T(contradiction))
classical_result = tableau.build()
print(f"Classical: {classical_result}")  # False

# weak Kleene: satisfiable using tableau approach
t3_tableau = three_valued_signed_tableau(T3(contradiction))
u_tableau = three_valued_signed_tableau(U(contradiction))
wk3_result = t3_tableau.build() or u_tableau.build()
print(f"weak Kleene: {wk3_result}")  # True
```

#### weak Kleene Model Extraction (Tableau Approach)

Extract all weak Kleene models for a formula using the tableau method.

**Approach:**
1. Check if formula can be true (T3) - extract models from successful tableau
2. Check if formula can be undefined (U) - extract models from successful tableau  
3. Combine models from both tableaux

**Returns:**
- Models from tableaux show **minimal satisfying assignments**

**Example:**
```python
from tableau_core import three_valued_signed_tableau, T3, U, Disjunction, Atom

p = Atom("p")
q = Atom("q") 
formula = Disjunction(p, q)

# Get models from both T3 and U tableaux
t3_tableau = three_valued_signed_tableau(T3(formula))
u_tableau = three_valued_signed_tableau(U(formula))

models = []
if t3_tableau.build():
    models.extend(t3_tableau.extract_all_models())
if u_tableau.build():
    models.extend(u_tableau.extract_all_models())
for i, model in enumerate(models):
    print(f"Model {i+1}:")
    print(f"  p: {model.get_assignment('p')}")
    print(f"  q: {model.get_assignment('q')}")
    print(f"  Satisfies formula: {model.satisfies(formula)}")
```

### wKrQ Epistemic Logic

#### `wkrq_signed_tableau(formulas, track_steps=False)`

Create wKrQ tableau.

**Parameters:**
- `formulas`: `SignedFormula` or `List[SignedFormula]` - Initial signed formulas
- `track_steps`: `bool` - Enable step-by-step visualization

**Returns:**
- `OptimizedTableauEngine` - Engine configured for wKrQ logic

**Example:**
```python
from tableau_core import M, N, TF, FF, wkrq_signed_tableau

p = Atom("p")
q = Atom("q")

# Epistemic uncertainty: "p may be true" and "p need not be true"
formulas = [M(p), N(p)]
tableau = wkrq_signed_tableau(formulas, track_steps=True)
result = tableau.build()  # True - epistemic uncertainty is consistent
```

#### `ferguson_signed_tableau(formulas, track_steps=False)`

Alternative name for wKrQ tableau (same functionality).

### Signed Formula Constructors

#### Classical Signs: `T(formula)`, `F(formula)`

Create signed formulas for classical logic.

**Parameters:**
- `formula`: `Formula` - The formula to sign

**Returns:**
- `SignedFormula` - Signed formula with classical sign

**Example:**
```python
from tableau_core import T, F, Atom, Conjunction

p = Atom("p")
q = Atom("q")

# T:(p ∧ q) - "p ∧ q is true"
t_conj = T(Conjunction(p, q))

# F:(p ∧ q) - "p ∧ q is false"  
f_conj = F(Conjunction(p, q))
```

#### Three-Valued Signs: `T3(formula)`, `F3(formula)`, `U(formula)`

Create signed formulas for three-valued logic.

**Example:**
```python
from tableau_core import T3, F3, U

p = Atom("p")

t3_p = T3(p)  # "p is true"
f3_p = F3(p)  # "p is false"
u_p = U(p)    # "p is undefined"
```

#### wKrQ Signs: `TF(formula)`, `FF(formula)`, `M(formula)`, `N(formula)`

Create signed formulas for wKrQ.

**Signs:**
- `TF`: Definitely true (classical T)
- `FF`: Definitely false (classical F)
- `M`: May be true (epistemic possibility)
- `N`: Need not be true (epistemic possibility of falsehood)

**Example:**
```python
from tableau_core import TF, FF, M, N

p = Atom("p")

tf_p = TF(p)  # "p is definitely true"
ff_p = FF(p)  # "p is definitely false"
m_p = M(p)    # "p may be true"
n_p = N(p)    # "p need not be true"
```

## OptimizedTableauEngine Class

The `OptimizedTableauEngine` class provides industrial-grade tableau construction with visualization.

### Key Features

- **α/β Rule Prioritization**: Apply linear rules before branching (Smullyan, 1968)
- **O(1) Closure Detection**: Hash-based formula tracking
- **Subsumption Elimination**: Remove redundant branches
- **Step-by-Step Visualization**: Track construction with tree structure

### Constructor

The engine is typically created through convenience functions, but can be instantiated directly:

```python
from tableau_core import OptimizedTableauEngine

engine = OptimizedTableauEngine("classical")  # or "wk3", "wkrq"
```

### Core Methods

#### `build() -> bool`

Construct the tableau and determine satisfiability.

**Returns:**
- `bool` - True if satisfiable, False if unsatisfiable

**Side Effects:**
- Updates `self.branches` with final tableau
- Records construction steps if tracking enabled
- Updates performance statistics

#### `is_satisfiable() -> bool`

Check satisfiability (must call `build()` first).

**Returns:**
- `bool` - True if satisfiable

#### `extract_all_models() -> List[Model]`

Extract all satisfying models from open branches.

**Returns:**
- `List[Model]` - List of models (ClassicalModel, weakKleeneModel, or WkrqModel)

**Example:**
```python
tableau = classical_signed_tableau(T(Atom("p")))
if tableau.build():
    models = tableau.extract_all_models()
    for model in models:
        print(f"Model: {model.assignment}")
```

### Visualization Methods

#### `enable_step_tracking()`

Enable construction step recording for visualization.

**Note:** Must be called before `build_tableau()`.

#### `print_construction_steps(title="Step-by-Step Tableau Construction")`

Print step-by-step construction with tree visualization.

**Parameters:**
- `title`: `str` - Title for the output

**Output Format:**
```
Step 1: Initialize tableau with given formulas
Initial formulas:
  • T:p ∨ q

Step 2: Apply T-Disjunction (β) to T:p ∨ q (creates 2 branches)
Rule applied: T-Disjunction (β)
New formulas added:
  • T:p
  • T:q
Tableau tree structure:
├── Branch 1 ○
│   ├─ T:p ∨ q
│   └─ T:p
└── Branch 2 ○
    ├─ T:p ∨ q
    └─ T:q
```

#### `get_step_by_step_construction() -> List[dict]`

Get raw construction steps for programmatic access.

**Returns:**
- `List[dict]` - Step information with tree snapshots

## Data Structures

### Formula Classes

#### `Atom(name)`

Atomic proposition.

**Parameters:**
- `name`: `str` - Atom name

**Example:**
```python
p = Atom("p")
q = Atom("q")
```

#### `Negation(operand)`

Negation formula.

**Parameters:**
- `operand`: `Formula` - Formula to negate

#### `Conjunction(left, right)`

Conjunction (AND) formula.

**Parameters:**
- `left`: `Formula` - Left conjunct
- `right`: `Formula` - Right conjunct

#### `Disjunction(left, right)`

Disjunction (OR) formula.

#### `Implication(antecedent, consequent)`

Implication formula.

**Parameters:**
- `antecedent`: `Formula` - Antecedent (if part)
- `consequent`: `Formula` - Consequent (then part)

### First-Order Logic Classes

#### `Predicate(name, terms)`

Predicate with terms.

**Parameters:**
- `name`: `str` - Predicate name
- `terms`: `List[Term]` - List of terms

**Example:**
```python
from tableau_core import Predicate, Constant, Variable

x = Variable("x")
a = Constant("a")
Student_a = Predicate("Student", [a])
Human_x = Predicate("Human", [x])
```

#### `Constant(name)`

Constant term.

#### `Variable(name)`

Variable term.

### Truth Values

#### `TruthValue` Enumeration

Three-valued truth system:

```python
from tableau_core import TruthValue, t, f, e

# Values
t = TruthValue.TRUE      # True
f = TruthValue.FALSE     # False  
e = TruthValue.UNDEFINED # Undefined/error
```

#### `weakKleeneOperators`

Operators for weak Kleene semantics:

```python
from tableau_core import weakKleeneOperators

# Any operation with 'e' returns 'e'
result = weakKleeneOperators.conjunction(t, e)  # Returns e
result = weakKleeneOperators.disjunction(f, e)  # Returns e
result = weakKleeneOperators.negation(e)        # Returns e
```

### Model Classes

#### `ClassicalModel`

Two-valued model for classical logic.

**Methods:**
- `get_assignment(atom_name: str) -> bool`
- `satisfies(formula: Formula) -> bool`

#### `weakKleeneModel`

Three-valued model for weak Kleene logic.

**Methods:**
- `get_assignment(atom_name: str) -> TruthValue`
- `satisfies(formula: Formula) -> TruthValue`

#### `WkrqModel`

Model for wKrQ.

**Methods:**
- `get_assignment(formula: Formula) -> Optional[Sign]`

## Logic Systems

### Classical Propositional Logic

**Signs:** T (true), F (false)  
**Contradiction:** T:φ and F:φ contradict

**Rules:**
- T-Conjunction (α): T:(A∧B) → T:A, T:B
- F-Conjunction (β): F:(A∧B) → F:A | F:B
- T-Disjunction (β): T:(A∨B) → T:A | T:B
- F-Disjunction (α): F:(A∨B) → F:A, F:B
- T-Implication (β): T:(A→B) → F:A | T:B
- F-Implication (α): F:(A→B) → T:A, F:B
- T-Negation (α): T:¬A → F:A
- F-Negation (α): F:¬A → T:A

### Weak Kleene Logic (WK3)

**Signs:** T (true), F (false), U (undefined)  
**Contradiction:** Only T:φ and F:φ contradict

**Truth Tables:**
```
¬t = f    ¬f = t    ¬e = e

t ∧ t = t    t ∧ f = e    t ∧ e = e
f ∧ t = e    f ∧ f = f    f ∧ e = e
e ∧ t = e    e ∧ f = e    e ∧ e = e
```

### wKrQ Epistemic Logic

**Signs:** T/F (definite), M/N (epistemic)  
**Contradiction:** Only T:φ and F:φ contradict

**Interpretation:**
- T:φ - "φ is definitely true"
- F:φ - "φ is definitely false"
- M:φ - "φ may be true" (epistemic possibility)
- N:φ - "φ need not be true" (epistemic possibility of falsehood)

## Visualization Features

### Step-by-Step Construction

Enable detailed construction tracking:

```python
tableau = classical_signed_tableau(formulas, track_steps=True)
result = tableau.build()
tableau.print_construction_steps("My Tableau Construction")
```

### Tree Structure Display

The visualization shows:
- Branch hierarchy with parent-child relationships
- Open (○) and closed (✗) branch status
- Specific rules applied at each step
- Formulas added by each rule application

Example output:
```
Step 2: Apply F-Conjunction (β) to F:p ∧ q (creates 2 branches)
Rule applied: F-Conjunction (β)
Tableau tree structure:
└── Branch 0 (parent node)
    ├── Branch 1 ○
    │   ├─ F:p ∧ q
    │   └─ F:p
    └── Branch 2 ○
        ├─ F:p ∧ q
        └─ F:q
```

## Extension Framework

### Adding New Logic Systems

Extend the unified implementation by modifying `tableau_core.py`:

**Step 1: Define Sign System**
```python
class TemporalSign(Sign):
    def __init__(self, designation: str, time: int):
        self.designation = designation  # "T" or "F"
        self.time = time               # Time point
    
    def is_contradictory_with(self, other: 'Sign') -> bool:
        return (isinstance(other, TemporalSign) and
                self.designation != other.designation and
                self.time == other.time)
```

**Step 2: Add Rules to Engine**
```python
# In OptimizedTableauEngine._initialize_tableau_rules()
elif self.sign_system == "temporal":
    rules['T_next'] = [TableauRule(
        rule_type="alpha",
        premises=["T:X(A)"],
        conclusions=[["T:A@t+1"]],  # Next time point
        priority=1,
        name="Temporal-Next (α)"
    )]
```

**Step 3: Create Helper Function**
```python
def temporal_signed_tableau(formulas, track_steps=False):
    engine = OptimizedTableauEngine("temporal")
    if track_steps:
        engine.enable_step_tracking()
    engine.build_tableau(formulas)
    return engine
```

## Complete Examples

### Example 1: Classical Logic with Visualization

```python
from tableau_core import Atom, Conjunction, classical_signed_tableau, T, F

# Test a complex formula
p = Atom("p")
q = Atom("q")
r = Atom("r")

# (p ∧ q) → r
formula = Implication(Conjunction(p, q), r)

# Create tableau with step tracking
tableau = classical_signed_tableau([T(formula), T(p), T(q), F(r)], track_steps=True)

# Build and analyze
result = tableau.build()
print(f"Satisfiable: {result}")

# Show construction steps
tableau.print_construction_steps("Testing (p ∧ q) → r with p, q true and r false")

# This should be unsatisfiable (contradiction)
```

### Example 2: Three-Valued Logic Comparison

```python
from tableau_core import Atom, Conjunction, Negation, wk3_satisfiable, wk3_models

p = Atom("p")

# Classical contradiction: p ∧ ¬p
contradiction = Conjunction(p, Negation(p))

# Classical logic
classical_tableau = classical_signed_tableau(T(contradiction))
classical_result = classical_tableau.build()
print(f"Classical satisfiable: {classical_result}")  # False

# WK3 logic
wk3_result = wk3_satisfiable(contradiction)
print(f"weak Kleene satisfiable: {wk3_result}")  # True

# Find WK3 models
models = wk3_models(contradiction)
print(f"WK3 models: {len(models)}")
for model in models:
    p_val = model.get_assignment("p")
    result = model.satisfies(contradiction)
    print(f"  p={p_val}, formula evaluates to {result}")
```

### Example 3: Ferguson's Epistemic Logic

```python
from tableau_core import Atom, M, N, TF, FF, ferguson_signed_tableau

p = Atom("p")
q = Atom("q")

# Test epistemic uncertainty
print("Example: Epistemic uncertainty without contradiction")
formulas = [M(p), N(p)]  # "p may be true" and "p need not be true"
tableau = ferguson_signed_tableau(formulas, track_steps=True)
result = tableau.build()
print(f"M:p ∧ N:p satisfiable: {result}")  # True

# Test classical contradiction
print("\nExample: Classical contradiction")
formulas = [TF(p), FF(p)]  # "p is definitely true" and "p is definitely false"
tableau = ferguson_signed_tableau(formulas, track_steps=True)
result = tableau.build()
print(f"T:p ∧ F:p satisfiable: {result}")  # False

tableau.print_construction_steps("Ferguson Epistemic Logic Example")
```

### Example 4: First-Order Logic

```python
from tableau_core import Predicate, Constant, Implication, classical_signed_tableau, T

# First-order predicate logic
tweety = Constant("tweety")
Human = lambda x: Predicate("Human", [x])
Mortal = lambda x: Predicate("Mortal", [x])

# Human(tweety) → Mortal(tweety)
formula = Implication(Human(tweety), Mortal(tweety))

# Test satisfiability
tableau = classical_signed_tableau(T(formula), track_steps=True)
result = tableau.build()
print(f"Human(tweety) → Mortal(tweety) satisfiable: {result}")

# Show construction
tableau.print_construction_steps("First-Order Logic Example")
```

### Example 5: Performance Analysis

```python
from tableau_core import Atom, Conjunction, Disjunction, classical_signed_tableau, T
import time

# Create complex formula for performance testing
atoms = [Atom(f"p{i}") for i in range(10)]

# Create CNF formula: (p0 ∨ p1) ∧ (p2 ∨ p3) ∧ ... ∧ (p8 ∨ p9)
clauses = []
for i in range(0, len(atoms), 2):
    if i + 1 < len(atoms):
        clauses.append(Disjunction(atoms[i], atoms[i+1]))

# Conjoin all clauses
formula = clauses[0]
for clause in clauses[1:]:
    formula = Conjunction(formula, clause)

# Test with timing
start_time = time.time()
tableau = classical_signed_tableau(T(formula))
result = tableau.build()
end_time = time.time()

print(f"Complex formula satisfiable: {result}")
print(f"Construction time: {end_time - start_time:.4f} seconds")
print(f"Total branches: {len(tableau.branches)}")

# Extract models
if result:
    models = tableau.extract_all_models()
    print(f"Number of models: {len(models)}")
```