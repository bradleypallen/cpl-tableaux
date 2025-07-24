# API Reference: Consolidated Tableau System

**Version**: 3.0 (Consolidated Architecture)  
**Last Updated**: July 2025  
**License**: MIT  

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core API Functions](#core-api-functions)
3. [TableauEngine Class](#tableauengine-class)
4. [Data Structures](#data-structures)
5. [Logic Systems](#logic-systems)
6. [Extension Framework](#extension-framework)
7. [Performance and Debugging](#performance-and-debugging)
8. [Complete Examples](#complete-examples)

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd tableaux

# Verify installation
python -m pytest --tb=no -q
```

### Basic Usage

```python
from tableau_core import Atom, Conjunction, Disjunction, Negation, Implication
from tableau_core import T, F, classical_signed_tableau, wk3_satisfiable

# Create formulas
p = Atom("p")
q = Atom("q")
formula = Implication(p, Disjunction(p, q))

# Classical logic - check satisfiability
engine = classical_signed_tableau(T(formula))
satisfiable = engine.build()
print(f"Satisfiable: {satisfiable}")

# Extract models if satisfiable
if satisfiable:
    models = engine.extract_all_models()
    print(f"Models: {models}")

# Three-valued logic (WK3)
wk3_result = wk3_satisfiable(formula)
print(f"WK3 satisfiable: {wk3_result}")
```

## Core API Functions

### Classical Logic Functions

#### `classical_signed_tableau(formulas)`

Create a classical logic tableau engine.

**Parameters:**
- `formulas`: `SignedFormula` or `List[SignedFormula]` - Initial signed formulas

**Returns:**
- `TableauEngine` - Configured tableau engine

**Example:**
```python
from tableau_core import T, F, classical_signed_tableau

# Single formula
engine = classical_signed_tableau(T(Atom("p")))

# Multiple formulas
engine = classical_signed_tableau([T(Atom("p")), F(Atom("q"))])
```

#### `check_satisfiability(formulas, logic_system="classical")`

Quick satisfiability check without model extraction.

**Parameters:**
- `formulas`: `List[Formula]` - Unsigned formulas to test
- `logic_system`: `str` - Logic system ("classical", "three_valued", "wkrq")

**Returns:**
- `bool` - True if satisfiable

**Example:**
```python
from tableau_engine import check_satisfiability

formulas = [Atom("p"), Negation(Atom("p"))]
result = check_satisfiability(formulas, "classical")
print(f"Satisfiable: {result}")  # False (contradiction)
```

### Three-Valued Logic Functions

#### `wk3_satisfiable(formula)`

Check WK3 (Weak Kleene) satisfiability.

**Parameters:**
- `formula`: `Formula` - Formula to test

**Returns:**
- `bool` - True if satisfiable in WK3

**Example:**
```python
from tableau_core import wk3_satisfiable, Conjunction, Negation

p = Atom("p")
contradiction = Conjunction(p, Negation(p))

# Classical: unsatisfiable
classical_result = check_satisfiability([contradiction])
print(f"Classical: {classical_result}")  # False

# WK3: satisfiable (when p is undefined)
wk3_result = wk3_satisfiable(contradiction)
print(f"WK3: {wk3_result}")  # True
```

#### `wk3_models(formula)`

Find all WK3 models for a formula.

**Parameters:**
- `formula`: `Formula` - Formula to find models for

**Returns:**
- `List[WK3Model]` - List of satisfying models

**Example:**
```python
from tableau_core import wk3_models, Disjunction

p = Atom("p")
q = Atom("q")
formula = Disjunction(p, q)

models = wk3_models(formula)
for i, model in enumerate(models):
    print(f"Model {i+1}: {model.assignment}")
    print(f"  Satisfies formula: {model.satisfies(formula)}")
```

### Signed Formula Constructors

#### `T(formula)`, `F(formula)` - Classical Signs

Create signed formulas for classical logic.

**Parameters:**
- `formula`: `Formula` - The formula to sign

**Returns:**
- `SignedFormula` - Signed formula object

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

#### `T3(formula)`, `F3(formula)`, `U(formula)` - Three-Valued Signs

Create signed formulas for three-valued logic.

**Parameters:**
- `formula`: `Formula` - The formula to sign

**Returns:**
- `SignedFormula` - Signed formula with three-valued sign

**Example:**
```python
from tableau_core import T3, F3, U, three_valued_signed_tableau

p = Atom("p")

# Three-valued signs
t3_p = T3(p)  # "p is true"
f3_p = F3(p)  # "p is false"
u_p = U(p)    # "p is undefined"

# Use in three-valued tableau
engine = three_valued_signed_tableau([t3_p, u_p])
satisfiable = engine.build()
```

## TableauEngine Class

The `TableauEngine` class provides the main tableau construction algorithm.

### Constructor

#### `TableauEngine(sign_system="classical")`

Create a new tableau engine.

**Parameters:**
- `sign_system`: `str` - Logic system ("classical", "three_valued", "wkrq")

### Core Methods

#### `build() -> bool`

Construct the tableau and determine satisfiability.

**Returns:**
- `bool` - True if satisfiable, False if unsatisfiable

**Side Effects:**
- Updates `self.branches` with final tableau
- Updates `self.rule_applications` with statistics
- May modify internal state for optimization

**Example:**
```python
from tableau_engine import TableauEngine
from tableau_core import T, Atom, Implication

engine = TableauEngine("classical")
engine.add_initial_formulas([T(Implication(Atom("p"), Atom("q")))])
satisfiable = engine.build()

print(f"Satisfiable: {satisfiable}")
print(f"Rule applications: {engine.rule_applications}")
print(f"Total branches: {len(engine.branches)}")
```

#### `extract_all_models() -> List[Dict[str, TruthValue]]`

Extract all satisfying models from open branches.

**Returns:**
- `List[Dict[str, TruthValue]]` - List of models mapping atom names to truth values

**Preconditions:**
- `build()` must be called first
- Must be satisfiable (`build()` returned True)

**Raises:**
- `RuntimeError` - If called before `build()` or on unsatisfiable formula

**Example:**
```python
engine = classical_signed_tableau(T(Atom("p")))
if engine.build():
    models = engine.extract_all_models()
    for i, model in enumerate(models):
        print(f"Model {i+1}:")
        for atom, value in model.items():
            print(f"  {atom}: {value}")
```

#### `get_statistics() -> Dict[str, Any]`

Get performance and construction statistics.

**Returns:**
- `Dict[str, Any]` - Statistics dictionary

**Keys:**
- `satisfiable`: `bool` - Whether formula was satisfiable
- `total_branches`: `int` - Total branches created
- `rule_applications`: `int` - Number of rule applications
- `max_branch_size`: `int` - Largest branch size
- `construction_time`: `float` - Time in seconds (if available)

**Example:**
```python
engine = classical_signed_tableau(T(complex_formula))
engine.build()

stats = engine.get_statistics()
print(f"Total branches: {stats['total_branches']}")
print(f"Rule applications: {stats['rule_applications']}")
print(f"Max branch size: {stats['max_branch_size']}")
```

### Advanced Methods

#### `add_initial_formulas(formulas: List[SignedFormula])`

Add initial formulas before tableau construction.

#### `find_expandable_branch() -> Optional[TableauBranch]`

Find next branch to expand (internal method).

#### `apply_rule(rule, signed_formula, branch)`

Apply a tableau rule to a branch (internal method).

## Data Structures

### Formula Classes

#### `Atom(name: str)`

Propositional atom.

**Parameters:**
- `name`: `str` - Atom name (e.g., "p", "q", "proposition1")

**Example:**
```python
from tableau_core import Atom

p = Atom("p")
complex_atom = Atom("user_is_authenticated")
```

#### `Negation(operand: Formula)`

Logical negation.

**Parameters:**
- `operand`: `Formula` - Formula to negate

**Example:**
```python
from tableau_core import Negation, Atom

p = Atom("p")
not_p = Negation(p)  # ¬p
```

#### `Conjunction(left: Formula, right: Formula)`

Logical conjunction (AND).

**Parameters:**
- `left`: `Formula` - Left operand
- `right`: `Formula` - Right operand

**Example:**
```python
from tableau_core import Conjunction, Atom

p = Atom("p")
q = Atom("q")
p_and_q = Conjunction(p, q)  # p ∧ q
```

#### `Disjunction(left: Formula, right: Formula)`

Logical disjunction (OR).

**Example:**
```python
from tableau_core import Disjunction, Atom

p = Atom("p")
q = Atom("q")
p_or_q = Disjunction(p, q)  # p ∨ q
```

#### `Implication(left: Formula, right: Formula)`

Logical implication.

**Example:**
```python
from tableau_core import Implication, Atom

p = Atom("p")
q = Atom("q")
p_implies_q = Implication(p, q)  # p → q
```

### Truth Value System

#### `TruthValue`

Constants for truth values across logic systems.

**Constants:**
- `TruthValue.TRUE` - Boolean true
- `TruthValue.FALSE` - Boolean false
- `TruthValue.UNDEFINED` - Three-valued undefined

**Example:**
```python
from tableau_core import TruthValue

# Classical model
classical_model = {
    "p": TruthValue.TRUE,
    "q": TruthValue.FALSE
}

# Three-valued model
wk3_model = {
    "p": TruthValue.TRUE,
    "q": TruthValue.UNDEFINED,
    "r": TruthValue.FALSE
}
```

### WK3 Truth Value Constructors

#### `t`, `f`, `e` - Three-Valued Constants

Convenience constructors for WK3 truth values.

**Usage:**
```python
from tableau_core import t, f, e

# Direct truth value construction
model = {
    "p": t,  # true
    "q": f,  # false  
    "r": e   # undefined
}
```

## Logic Systems

### Classical Propositional Logic

Two-valued logic with standard semantics.

**Truth Values:** `true`, `false`

**Operators:**
- `¬p` (negation): `¬true = false`, `¬false = true`
- `p ∧ q` (conjunction): true only when both operands are true
- `p ∨ q` (disjunction): false only when both operands are false
- `p → q` (implication): false only when p is true and q is false

**API Usage:**
```python
from tableau_core import classical_signed_tableau, T, F

# Test tautology
tautology = Disjunction(Atom("p"), Negation(Atom("p")))
engine = classical_signed_tableau(F(tautology))  # Test if negation is unsatisfiable
is_tautology = not engine.build()  # Unsatisfiable negation = tautology
```

### Weak Kleene Logic (WK3)

Three-valued logic with undefined value propagation.

**Truth Values:** `t` (true), `f` (false), `e` (undefined/error)

**Truth Tables:**
```
¬t = f    ¬f = t    ¬e = e

t ∧ t = t    t ∧ f = f    t ∧ e = e
f ∧ t = f    f ∧ f = f    f ∧ e = f  
e ∧ t = e    e ∧ f = f    e ∧ e = e

t ∨ t = t    t ∨ f = t    t ∨ e = t
f ∨ t = t    f ∨ f = f    f ∨ e = e
e ∨ t = t    e ∨ f = e    e ∨ e = e
```

**Key Properties:**
- Contradictions can be satisfiable when atoms are undefined
- Law of excluded middle (`p ∨ ¬p`) is not a tautology
- Self-implication (`p → p`) is not a tautology

**API Usage:**
```python
from tableau_core import wk3_satisfiable, wk3_models

p = Atom("p")
contradiction = Conjunction(p, Negation(p))

# Check satisfiability
satisfiable = wk3_satisfiable(contradiction)  # True

# Find models
models = wk3_models(contradiction)
for model in models:
    print(f"p = {model.assignment.get('p', e)}")  # Should show e (undefined)
```

### wKrQ Logic (Ferguson System)

Four-valued epistemic logic with signs T, F, M, N.

**Signs:**
- `T` (definitely true) / `F` (definitely false) - Truth-functional
- `M` (may be true) / `N` (need not be true) - Epistemic

**Closure Conditions:**
- `T:p` and `F:p` close branches (classical contradiction)
- `M:p` and `N:p` do NOT close branches (epistemic uncertainty)

**API Usage:**
```python
from tableau_core import TF, FF, M, N, wkrq_signed_tableau

p = Atom("p")

# Classical contradiction - unsatisfiable
classical_test = wkrq_signed_tableau([TF(p), FF(p)])
print(classical_test.build())  # False

# Epistemic uncertainty - satisfiable
epistemic_test = wkrq_signed_tableau([M(p), N(p)])
print(epistemic_test.build())  # True
```

## Extension Framework

### Adding New Logic Systems

#### Step 1: Define Sign System

```python
from tableau_core import Sign

class ModalSign(Sign):
    """Modal logic signs: □T, □F, ◇T, ◇F"""
    
    def __init__(self, modality: str, polarity: str):
        if modality not in ["□", "◇"]:
            raise ValueError(f"Invalid modality: {modality}")
        if polarity not in ["T", "F"]:
            raise ValueError(f"Invalid polarity: {polarity}")
        self.modality = modality
        self.polarity = polarity
    
    def contradicts(self, other: 'ModalSign') -> bool:
        return (self.modality == other.modality and 
                self.polarity != other.polarity)
    
    def __str__(self) -> str:
        return f"{self.modality}{self.polarity}"
```

#### Step 2: Implement Tableau Rules

```python
from tableau_rules import SignedTableauRule, AlphaRule, RuleResult

class ModalNecessityRule(AlphaRule):
    """□T:A → T:A (necessity rule)"""
    priority = 1
    
    def applies_to(self, signed_formula) -> bool:
        return (isinstance(signed_formula.sign, ModalSign) and
                signed_formula.sign.modality == "□" and
                signed_formula.sign.polarity == "T")
    
    def apply(self, signed_formula) -> RuleResult:
        inner_formula = signed_formula.formula
        return RuleResult(
            is_alpha=True,
            branches=[[T(inner_formula)]]
        )
```

#### Step 3: Register System

```python
from tableau_rules import SignedRuleRegistry

def create_modal_tableau(formulas):
    """Create modal logic tableau engine."""
    engine = TableauEngine("modal")
    
    # Register modal rules
    engine.rule_registry.register_rules("modal", [
        ModalNecessityRule(),
        ModalPossibilityRule(),
        # ... other modal rules
    ])
    
    engine.add_initial_formulas(formulas)
    return engine
```

### Adding New Formula Types

#### Step 1: Define Formula Class

```python
from tableau_core import Formula

class TemporalNext(Formula):
    """Temporal logic: X φ (φ holds in next time point)"""
    
    def __init__(self, operand: Formula):
        self.operand = operand
    
    def __str__(self) -> str:
        return f"X({self.operand})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, TemporalNext) and self.operand == other.operand
    
    def __hash__(self) -> int:
        return hash(("TemporalNext", self.operand))
```

#### Step 2: Implement Rules

```python
class TemporalNextRule(AlphaRule):
    """T:X(φ) → advance time and add T:φ"""
    priority = 2
    
    def applies_to(self, signed_formula) -> bool:
        return isinstance(signed_formula.formula, TemporalNext)
    
    def apply(self, signed_formula) -> RuleResult:
        next_formula = signed_formula.formula.operand
        return RuleResult(
            is_alpha=True,
            branches=[[SignedFormula(signed_formula.sign, next_formula)]],
            metadata={"time_advance": 1}
        )
```

## Performance and Debugging

### Performance Monitoring

```python
import time
from tableau_core import classical_signed_tableau

# Measure construction time
start_time = time.time()
engine = classical_signed_tableau(T(complex_formula))
result = engine.build()
end_time = time.time()

stats = engine.get_statistics()
stats["actual_construction_time"] = end_time - start_time

print(f"Satisfiable: {result}")
print(f"Construction time: {stats['actual_construction_time']:.4f}s")
print(f"Rule applications: {stats['rule_applications']}")
print(f"Branches created: {stats['total_branches']}")
```

### Debug Output

```python
from tableau_engine import TableauEngine

# Enable debug mode
engine = TableauEngine("classical")
engine.debug = True  # If supported
engine.add_initial_formulas([T(formula)])

result = engine.build()

# Examine branch details
for i, branch in enumerate(engine.branches):
    print(f"Branch {i+1}: {'CLOSED' if branch.is_closed else 'OPEN'}")
    if branch.is_closed and branch.closure_reason:
        sf1, sf2 = branch.closure_reason
        print(f"  Closed by: {sf1} ⊥ {sf2}")
    
    print(f"  Formulas ({len(branch.signed_formulas)}):")
    for sf in branch.signed_formulas:
        print(f"    {sf}")
```

### Memory Usage Analysis

```python
import sys
from tableau_core import classical_signed_tableau

def get_object_size(obj):
    """Get approximate object size in bytes."""
    return sys.getsizeof(obj)

engine = classical_signed_tableau(T(large_formula))
engine.build()

total_memory = 0
for branch in engine.branches:
    branch_memory = get_object_size(branch.signed_formulas)
    total_memory += branch_memory

print(f"Approximate memory usage: {total_memory} bytes")
print(f"Memory per branch: {total_memory / len(engine.branches):.1f} bytes")
```

## Complete Examples

### Example 1: Propositional Satisfiability Solver

```python
#!/usr/bin/env python3
"""
Propositional SAT solver using tableau method.
"""

from tableau_core import *

def solve_sat(formula_str):
    """
    Solve SAT problem from string representation.
    
    Example formula strings:
    - "p & q"
    - "p | ~p" 
    - "(p -> q) & p & ~q"
    """
    # Parse formula (simplified parser)
    formula = parse_formula(formula_str)  # Implementation needed
    
    # Test satisfiability
    engine = classical_signed_tableau(T(formula))
    satisfiable = engine.build()
    
    if satisfiable:
        models = engine.extract_all_models()
        print(f"SATISFIABLE - Found {len(models)} model(s):")
        for i, model in enumerate(models):
            assignments = [f"{atom}={value}" for atom, value in model.items()]
            print(f"  Model {i+1}: {{{', '.join(assignments)}}}")
    else:
        print("UNSATISFIABLE")
    
    return satisfiable

# Usage
solve_sat("p & q")  # Satisfiable
solve_sat("p & ~p")  # Unsatisfiable
solve_sat("(p -> q) & (q -> r) & p & ~r")  # Unsatisfiable
```

### Example 2: Three-Valued Logic Explorer

```python
#!/usr/bin/env python3
"""
Explore differences between classical and three-valued logic.
"""

from tableau_core import *

def compare_logics(formula):
    """Compare classical vs WK3 satisfiability."""
    
    print(f"Formula: {formula}")
    print("-" * 40)
    
    # Classical logic
    classical_engine = classical_signed_tableau(T(formula))
    classical_sat = classical_engine.build()
    
    # Three-valued logic  
    wk3_sat = wk3_satisfiable(formula)
    
    print(f"Classical satisfiable: {classical_sat}")
    print(f"WK3 satisfiable: {wk3_sat}")
    
    if classical_sat != wk3_sat:
        print("*** DIFFERENCE DETECTED ***")
        
        if wk3_sat and not classical_sat:
            print("WK3 allows satisfiability through undefined values")
            models = wk3_models(formula)
            for model in models:
                undefined_atoms = [
                    atom for atom, value in model.assignment.items() 
                    if value == e
                ]
                if undefined_atoms:
                    print(f"  Undefined atoms: {undefined_atoms}")
    
    print()

# Test cases that highlight differences
p = Atom("p")
q = Atom("q")

test_cases = [
    Conjunction(p, Negation(p)),  # p ∧ ¬p - classical contradiction
    Disjunction(p, Negation(p)),  # p ∨ ¬p - excluded middle
    Implication(p, p),  # p → p - self-implication
    Implication(Conjunction(p, q), p),  # (p ∧ q) → p - simplification
]

for formula in test_cases:
    compare_logics(formula)
```

### Example 3: Automated Theorem Prover

```python
#!/usr/bin/env python3
"""
Automated theorem prover for propositional logic.
"""

from tableau_core import *

class TheoremProver:
    def __init__(self, logic_system="classical"):
        self.logic_system = logic_system
    
    def prove_tautology(self, formula):
        """
        Prove that formula is a tautology.
        Method: Show that ¬formula is unsatisfiable.
        """
        negated = Negation(formula)
        
        if self.logic_system == "classical":
            engine = classical_signed_tableau(T(negated))
            unsatisfiable = not engine.build()
        elif self.logic_system == "wk3":
            unsatisfiable = not wk3_satisfiable(negated)
        else:
            raise ValueError(f"Unknown logic system: {self.logic_system}")
        
        return unsatisfiable
    
    def prove_inference(self, premises, conclusion):
        """
        Prove that premises ⊢ conclusion.
        Method: Show that premises ∪ {¬conclusion} is unsatisfiable.
        """
        test_formulas = premises + [Negation(conclusion)]
        
        # Convert to single formula
        if len(test_formulas) == 1:
            combined = test_formulas[0]
        else:
            combined = test_formulas[0]
            for formula in test_formulas[1:]:
                combined = Conjunction(combined, formula)
        
        if self.logic_system == "classical":
            engine = classical_signed_tableau(T(combined))
            valid = not engine.build()
        elif self.logic_system == "wk3":
            valid = not wk3_satisfiable(combined)
        else:
            raise ValueError(f"Unknown logic system: {self.logic_system}")
        
        return valid
    
    def find_counterexample(self, premises, conclusion):
        """Find counterexample to inference if it exists."""
        test_formulas = premises + [Negation(conclusion)]
        
        if len(test_formulas) == 1:
            combined = test_formulas[0]
        else:
            combined = test_formulas[0]
            for formula in test_formulas[1:]:
                combined = Conjunction(combined, formula)
        
        if self.logic_system == "classical":
            engine = classical_signed_tableau(T(combined))
            if engine.build():
                return engine.extract_all_models()[0]
        elif self.logic_system == "wk3":
            if wk3_satisfiable(combined):
                return wk3_models(combined)[0]
        
        return None

# Usage examples
prover = TheoremProver("classical")

# Test tautologies
p = Atom("p")
q = Atom("q")

tautologies = [
    Disjunction(p, Negation(p)),  # p ∨ ¬p
    Implication(p, Disjunction(p, q)),  # p → (p ∨ q)
    Implication(Conjunction(p, q), p),  # (p ∧ q) → p
]

for tautology in tautologies:
    is_tautology = prover.prove_tautology(tautology)
    print(f"{tautology} is tautology: {is_tautology}")

# Test inferences
premises = [Implication(p, q), p]
conclusion = q

valid = prover.prove_inference(premises, conclusion)
print(f"Modus ponens valid: {valid}")

if not valid:
    counterexample = prover.find_counterexample(premises, conclusion)
    print(f"Counterexample: {counterexample}")
```

### Example 4: Interactive Logic Tutor

```python
#!/usr/bin/env python3
"""
Interactive tutorial system for learning tableau methods.
"""

from tableau_core import *

class LogicTutor:
    def __init__(self):
        self.current_lesson = 0
        self.lessons = [
            self.lesson_basic_formulas,
            self.lesson_satisfiability,
            self.lesson_tautologies,
            self.lesson_three_valued_logic,
            self.lesson_tableau_construction,
        ]
    
    def run(self):
        """Run interactive tutorial."""
        print("Welcome to the Tableau Logic Tutor!")
        print("=" * 40)
        
        while self.current_lesson < len(self.lessons):
            self.lessons[self.current_lesson]()
            
            if self.current_lesson < len(self.lessons) - 1:
                response = input("\nContinue to next lesson? (y/n): ")
                if response.lower() != 'y':
                    break
                    
            self.current_lesson += 1
        
        print("\nTutorial complete! You now understand tableau methods.")
    
    def lesson_basic_formulas(self):
        print("\nLESSON 1: Building Logical Formulas")
        print("-" * 35)
        
        p = Atom("p")
        q = Atom("q")
        
        print("Let's create some basic formulas:")
        print(f"  Atom p: {p}")
        print(f"  Atom q: {q}")
        print(f"  Negation ¬p: {Negation(p)}")
        print(f"  Conjunction p ∧ q: {Conjunction(p, q)}")
        print(f"  Disjunction p ∨ q: {Disjunction(p, q)}")
        print(f"  Implication p → q: {Implication(p, q)}")
        
        # Interactive exercise
        print("\nExercise: What would ¬(p ∧ q) look like?")
        user_input = input("Your answer (or 'skip'): ")
        
        correct = Negation(Conjunction(p, q))
        print(f"Correct answer: {correct}")
        
        if user_input.strip() and "skip" not in user_input.lower():
            print("Great job participating!")
    
    def lesson_satisfiability(self):
        print("\nLESSON 2: Satisfiability")
        print("-" * 25)
        
        p = Atom("p")
        
        satisfiable_formula = p
        unsatisfiable_formula = Conjunction(p, Negation(p))
        
        print("A formula is satisfiable if there's a truth assignment that makes it true.")
        print()
        print(f"Example 1: {satisfiable_formula}")
        engine1 = classical_signed_tableau(T(satisfiable_formula))
        result1 = engine1.build()
        print(f"  Satisfiable: {result1}")
        
        if result1:
            models = engine1.extract_all_models()
            print(f"  Model: {models[0]}")
        
        print()
        print(f"Example 2: {unsatisfiable_formula}")
        engine2 = classical_signed_tableau(T(unsatisfiable_formula))
        result2 = engine2.build()
        print(f"  Satisfiable: {result2}")
        
        print("\nA contradiction is never satisfiable - there's no way to make p both true and false!")
    
    def lesson_tautologies(self):
        print("\nLESSON 3: Tautologies")
        print("-" * 20)
        
        p = Atom("p")
        tautology = Disjunction(p, Negation(p))  # p ∨ ¬p
        
        print("A tautology is always true, regardless of truth assignments.")
        print(f"Example: {tautology}")
        print()
        print("To test if something is a tautology, we check if its negation is unsatisfiable:")
        
        negated_tautology = Negation(tautology)
        print(f"Testing: {negated_tautology}")
        
        engine = classical_signed_tableau(T(negated_tautology))
        result = engine.build()
        
        print(f"Satisfiable: {result}")
        print(f"Therefore, {tautology} is a tautology: {not result}")
    
    def lesson_three_valued_logic(self):
        print("\nLESSON 4: Three-Valued Logic")
        print("-" * 30)
        
        p = Atom("p")
        contradiction = Conjunction(p, Negation(p))
        
        print("In classical logic, p ∧ ¬p is always false (unsatisfiable).")
        classical_result = classical_signed_tableau(T(contradiction)).build()
        print(f"Classical satisfiability: {classical_result}")
        
        print("\nBut in three-valued logic, p can be 'undefined'!")
        print("When p is undefined, p ∧ ¬p is also undefined, which counts as satisfiable.")
        
        wk3_result = wk3_satisfiable(contradiction)
        print(f"WK3 satisfiability: {wk3_result}")
        
        if wk3_result:
            models = wk3_models(contradiction)
            print("WK3 models:")
            for model in models:
                print(f"  p = {model.assignment.get('p', e)}")
    
    def lesson_tableau_construction(self):
        print("\nLESSON 5: How Tableaux Work")
        print("-" * 30)
        
        p = Atom("p")
        q = Atom("q")
        formula = Conjunction(p, Disjunction(q, Negation(q)))
        
        print("Tableaux break down formulas systematically using rules:")
        print(f"Formula: {formula}")
        print()
        print("Signed tableau construction:")
        print(f"1. Start with T:{formula}")
        print("2. Apply T-conjunction rule: T:(p ∧ (q ∨ ¬q)) → T:p, T:(q ∨ ¬q)")
        print("3. Apply T-disjunction rule: T:(q ∨ ¬q) → T:q | T:¬q")
        print("4. This creates two branches:")
        print("   Branch 1: T:p, T:q")
        print("   Branch 2: T:p, T:¬q")
        print("5. Apply T-negation rule in Branch 2: T:¬q → F:q")
        print("6. Final branches:")
        print("   Branch 1: T:p, T:q (satisfying model: p=true, q=true)")
        print("   Branch 2: T:p, F:q (satisfying model: p=true, q=false)")
        print()
        
        # Verify with actual tableau
        engine = classical_signed_tableau(T(formula))
        result = engine.build()
        models = engine.extract_all_models() if result else []
        
        print(f"Tableau result - Satisfiable: {result}")
        print(f"Models found: {len(models)}")
        for i, model in enumerate(models):
            print(f"  Model {i+1}: {model}")

# Run the tutor
if __name__ == "__main__":
    tutor = LogicTutor()
    tutor.run()
```

This comprehensive API reference provides everything needed to understand and use the consolidated tableau system. The examples progress from basic usage to advanced applications, making it suitable for both beginners and expert users building tableau-based reasoning systems.