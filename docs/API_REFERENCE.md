# API Reference: Tableau System

**Version**: 2.0 (Plugin Architecture)  
**Last Updated**: January 2025  
**License**: MIT  

## Table of Contents

1. [Quick Start](#quick-start)
2. [LogicSystem Class](#logicsystem-class)
3. [LogicFormula Class](#logicformula-class)
4. [TableauResult Class](#tableauresult-class)
5. [Logic System Factories](#logic-system-factories)
6. [Parser Integration](#parser-integration)
7. [Model and Result Objects](#model-and-result-objects)
8. [Extension Framework](#extension-framework)
9. [Complete Examples](#complete-examples)

## Quick Start

### Installation

```bash
pip install tableaux
```

### Basic Usage

```python
from tableaux import LogicSystem

# Create a logic system
classical = LogicSystem.classical()

# Create formulas
p, q = classical.atoms('p', 'q')
formula = p.implies(q) & p & ~q

# Test satisfiability
result = classical.solve(formula)
print(f"Satisfiable: {result.satisfiable}")
```

## LogicSystem Class

The main interface for all logic systems. Each logic system provides the same API but with different semantic behavior.

### Factory Methods

```python
# Create logic systems
classical = LogicSystem.classical()
weak_kleene = LogicSystem.weak_kleene()
wkrq = LogicSystem.wkrq()
```

### Core Methods

#### `atom(name: str) -> LogicFormula`

Create an atomic formula.

```python
classical = LogicSystem.classical()
p = classical.atom('p')
```

#### `atoms(*names: str) -> Tuple[LogicFormula, ...]`

Create multiple atomic formulas.

```python
p, q, r = classical.atoms('p', 'q', 'r')
```

#### `parse(formula_string: str) -> LogicFormula`

Parse a formula from string representation.

```python
formula = classical.parse("p -> q")
complex_formula = classical.parse("(p & q) | (~r -> s)")
```

**String Syntax:**
- Atoms: `p`, `q`, `r`, etc.
- Negation: `~p`
- Conjunction: `p & q`
- Disjunction: `p | q`
- Implication: `p -> q`
- Parentheses: `(p & q) | r`

#### `solve(formula: LogicFormula, sign: str = None) -> TableauResult`

Test satisfiability of a formula.

```python
# Test satisfiability (default: can formula be true?)
result = classical.solve(formula)

# Test with specific sign
result = classical.solve(formula, 'F')  # Can formula be false?

# For three-valued systems
result = weak_kleene.solve(formula, 'U')  # Can formula be undefined?

# For four-valued systems
result = wkrq.solve(formula, 'M')  # Can formula be both true and false?
```

#### `entails(premises: List[LogicFormula], conclusion: LogicFormula) -> bool`

Test logical entailment.

```python
premises = [classical.parse("p -> q"), p]
conclusion = q
is_valid = classical.entails(premises, conclusion)  # True (modus ponens)
```

## LogicFormula Class

Represents formulas within a specific logic system. Created by `LogicSystem` methods.

### Operators

```python
p, q = classical.atoms('p', 'q')

# Logical operators
conjunction = p & q
disjunction = p | q
negation = ~p
implication = p.implies(q)  # Use .implies() method

# Complex formulas
complex_formula = (p & q).implies(~r | q)
```

### Methods

#### `implies(other: LogicFormula) -> LogicFormula`

Create implication formula.

```python
implication = p.implies(q)  # p -> q
```

**Important:** Use `.implies()` method for programmatic formula construction. The `->` syntax is only for string parsing.

### Properties

```python
formula = p & q
print(f"Formula: {formula}")
print(f"String representation: {str(formula)}")
```

## TableauResult Class

Result object returned by `solve()` method.

### Properties

#### `satisfiable: bool`

Whether the formula is satisfiable.

```python
result = classical.solve(p & ~p)
print(result.satisfiable)  # False
```

#### `models: List[Model]`

List of all satisfying models.

```python
result = classical.solve(p | q)
for model in result.models:
    print(model)
```

#### `is_satisfiable: bool` and `is_unsatisfiable: bool`

Convenience properties.

```python
if result.is_satisfiable:
    print("Formula is satisfiable")
    
if result.is_unsatisfiable:
    print("Formula is a contradiction")
```

#### `model_count: int`

Number of models found.

```python
print(f"Found {result.model_count} models")
```

## Logic System Factories

### Classical Logic

Two-valued logic with T (true) and F (false).

```python
classical = LogicSystem.classical()
p = classical.atom('p')

# Classical contradiction is unsatisfiable
result = classical.solve(p & ~p)
print(result.satisfiable)  # False

# Classical excluded middle is a tautology
result = classical.solve(p | ~p, 'F')  # Can it be false?
print(result.satisfiable)  # False (no, it cannot be false)
```

### Weak Kleene Logic

Three-valued logic with T (true), F (false), and U (undefined).

```python
weak_kleene = LogicSystem.weak_kleene()
p = weak_kleene.atom('p')

# Test all three values
for sign in ['T', 'F', 'U']:
    result = weak_kleene.solve(p, sign)
    print(f"p can be {sign}: {result.satisfiable}")

# Excluded middle can fail
result = weak_kleene.solve(p | ~p, 'U')
print(f"p | ~p can be undefined: {result.satisfiable}")  # True
```

### wKrQ Logic

Four-valued logic with T (true only), F (false only), M (both), N (neither).

```python
wkrq = LogicSystem.wkrq()
p = wkrq.atom('p')

# Test all four values
for sign in ['T', 'F', 'M', 'N']:
    result = wkrq.solve(p, sign)
    print(f"p can be {sign}: {result.satisfiable}")

# Contradiction can be satisfiable (paraconsistent)
result = wkrq.solve(p & ~p, 'M')
print(f"p & ~p can be both: {result.satisfiable}")  # True
```


## Parser Integration

The parser handles string formulas with standard syntax:

```python
# Simple formulas
p_and_q = classical.parse("p & q")
p_or_not_q = classical.parse("p | ~q")
implication = classical.parse("p -> q")

# Complex formulas with parentheses
complex_formula = classical.parse("((p & q) -> r) | (~p & s)")

# Operator precedence (highest to lowest): ~, &, |, ->
formula1 = classical.parse("~p & q | r -> s")
formula2 = classical.parse("((~p) & q) | r) -> s")  # Same as above

# Mix with programmatic construction
parsed = classical.parse("p -> q")
programmatic = r & s
combined = parsed | programmatic
```

## Model and Result Objects

### Model Objects

Models represent truth value assignments:

```python
result = classical.solve(p & q)
if result.satisfiable:
    for model in result.models:
        print(f"Model: {model}")
        # Output: Model: {p: True, q: True}
```

### Analyzing Results

```python
formula = p.implies(q)
result = classical.solve(formula)

print(f"Satisfiable: {result.satisfiable}")
print(f"Number of models: {len(result.models)}")

if result.models:
    print("All models:")
    for i, model in enumerate(result.models, 1):
        print(f"  Model {i}: {model}")
```

### Working with Different Logic Systems

```python
# Same formula across different systems
formula_str = "p & ~p"

systems = [
    ("Classical", LogicSystem.classical()),
    ("Weak Kleene", LogicSystem.weak_kleene()),
    ("wKrQ", LogicSystem.wkrq()),
]

for name, system in systems:
    formula = system.parse(formula_str)
    result = system.solve(formula)
    print(f"{name:12}: {len(result.models)} models")
```

## Extension Framework

### Creating Custom Logic Systems

To create a new logic system, extend the `LogicSystem` base class:

```python
from tableaux.logics.logic_system import LogicSystem
from tableaux.core.formula import ConnectiveSpec
from tableaux.core.semantics import TruthValueSystem
from tableaux.core.signs import SignSystem
from tableaux.core.rules import TableauRule, RuleType, RulePattern

class MyLogic(LogicSystem):
    def initialize(self):
        # Define connectives
        self.add_connective(ConnectiveSpec("&", 2, 3, "left", "infix"))
        self.add_connective(ConnectiveSpec("|", 2, 2, "left", "infix"))
        self.add_connective(ConnectiveSpec("~", 1, 4, "none", "prefix"))
        self.add_connective(ConnectiveSpec("->", 2, 1, "right", "infix"))
        
        # Set semantic systems
        self.set_truth_system(MyTruthSystem())
        self.set_sign_system(MySignSystem())
        
        # Add tableau rules
        self._add_tableau_rules()
    
    def _add_tableau_rules(self):
        # Define your tableau rules
        self.add_rule(TableauRule(
            name="T-Conjunction",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "A & B")],
            conclusions=[["T:A", "T:B"]]
        ))
        # ... more rules
```

### Registration

```python
from tableaux.logics.logic_system import LogicRegistry

# Register your logic
LogicRegistry.register(MyLogic("my_logic"))

# Use immediately
system = LogicSystem(LogicRegistry.get("my_logic"))
```

## Complete Examples

### Example 1: Testing Classical Argument Forms

```python
from tableaux import LogicSystem

classical = LogicSystem.classical()
p, q, r = classical.atoms('p', 'q', 'r')

# Test classic valid arguments
valid_tests = [
    ("Modus Ponens", [classical.parse("p -> q"), p], q),
    ("Modus Tollens", [classical.parse("p -> q"), ~q], ~p),
    ("Hypothetical Syllogism", [classical.parse("p -> q"), classical.parse("q -> r")], classical.parse("p -> r")),
    ("Disjunctive Syllogism", [p | q, ~p], q)
]

for name, premises, conclusion in valid_tests:
    is_valid = classical.entails(premises, conclusion)
    print(f"{name:20}: {is_valid}")
```

### Example 2: Comparing Logic Systems

```python
# Test formula across different systems
formula_str = "p | ~p"  # Excluded middle

systems = [
    ("Classical", LogicSystem.classical()),
    ("Weak Kleene", LogicSystem.weak_kleene()),
    ("wKrQ", LogicSystem.wkrq())
]

for name, system in systems:
    formula = system.parse(formula_str)
    
    # Test satisfiability under different signs
    print(f"\n{name} Logic - {formula_str}:")
    
    if name == "Classical":
        signs = ['T', 'F']
    elif name == "Weak Kleene":
        signs = ['T', 'F', 'U']
    else:  # wKrQ
        signs = ['T', 'F', 'M', 'N']
    
    for sign in signs:
        result = system.solve(formula, sign)
        print(f"  Can be {sign}: {result.satisfiable}")
```

### Example 3: Model Analysis

```python
classical = LogicSystem.classical()
p, q, r = classical.atoms('p', 'q', 'r')

# Analyze a complex formula
formula = (p & q) | (r & ~p)
result = classical.solve(formula)

print(f"Formula: {formula}")
print(f"Satisfiable: {result.satisfiable}")
print(f"Number of models: {len(result.models)}")

if result.models:
    print("All satisfying models:")
    for i, model in enumerate(result.models, 1):
        print(f"  Model {i}: {model}")
    
    # Analyze patterns
    p_true_count = sum(1 for m in result.models if 'p: True' in str(m))
    total = len(result.models)
    print(f"p is true in {p_true_count}/{total} models ({p_true_count/total:.1%})")
```

### Example 4: Counterexample Generation

```python
# Test invalid argument with counterexample
premises = [classical.parse("p -> q"), q]  # Affirming consequent
conclusion = p

is_valid = classical.entails(premises, conclusion)
print(f"Affirming consequent is valid: {is_valid}")  # False

if not is_valid:
    # Find counterexample: premises true, conclusion false
    combined = premises[0] & premises[1] & (~conclusion)
    counter_result = classical.solve(combined)
    if counter_result.satisfiable:
        print(f"Counterexample: {counter_result.models[0]}")
```

### Example 5: Performance Testing

```python
import time

# Test performance on complex formulas
classical = LogicSystem.classical()
atoms = classical.atoms(*[f'p{i}' for i in range(10)])

# Build a complex formula
formula = atoms[0]
for atom in atoms[1:]:
    formula = formula | atom

start_time = time.time()
result = classical.solve(formula)
end_time = time.time()

print(f"Formula with {len(atoms)} atoms:")
print(f"Satisfiable: {result.satisfiable}")
print(f"Models: {len(result.models)}")
print(f"Time: {end_time - start_time:.4f} seconds")
```

## Error Handling

The API includes comprehensive error handling:

```python
try:
    # Invalid formula string
    formula = classical.parse("p & & q")
except Exception as e:
    print(f"Parse error: {e}")

try:
    # Invalid sign for logic system
    result = classical.solve(p, 'U')  # U not valid in classical logic
except Exception as e:
    print(f"Sign error: {e}")
```

## Type Safety

The API is designed with type safety in mind:

```python
from typing import List
from tableaux import LogicSystem, LogicFormula, TableauResult

def test_entailment(system: LogicSystem, 
                   premises: List[LogicFormula], 
                   conclusion: LogicFormula) -> bool:
    return system.entails(premises, conclusion)

# Usage with type checking
classical = LogicSystem.classical()
p, q = classical.atoms('p', 'q')
premises = [p.implies(q), p]
conclusion = q

result = test_entailment(classical, premises, conclusion)
```

This API provides a clean, consistent interface for working with multiple logic systems while maintaining the flexibility to extend with new logics and the performance characteristics needed for serious automated reasoning applications.