# Classical Propositional Logic Tableaux

A sophisticated implementation of semantic tableaux for classical propositional logic in Python with production-quality optimizations.

## Files

- `tableau.py` - Main tableau implementation with optimized expansion rules
- `formula.py` - Formula representation classes and logical operators
- `cli.py` - Command-line interface for interactive use
- `test_tableau.py` - Comprehensive test suite (40+ tests)
- `test_performance.py` - Performance benchmarks and optimization tests
- `test_medium_optimizations.py` - Advanced optimization feature tests
- `OPTIMIZATIONS.md` - Detailed documentation of performance improvements
- `TECHNICAL_ANALYSIS.md` - Expert analysis and assessment of implementation quality

## Installation

This is a pure Python implementation with no external dependencies for core functionality:

```bash
# Clone the repository
git clone <repository-url>
cd cpl-tableaux

# Optional: Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Optional: Install testing dependencies
pip install pytest
```

## Usage

### Basic Usage

Run the tableau system with built-in examples:

```bash
python tableau.py
```

This will test transitivity formulas and display tableau trees.

### Command-Line Interface

For interactive formula testing:

```bash
python cli.py
```

### Programmatic Usage

```python
from tableau import Tableau
from formula import Atom, Implication, Conjunction

# Create formulas
a, b, c = Atom("a"), Atom("b"), Atom("c")
formula = Implication(Conjunction(a, b), c)

# Test satisfiability
tableau = Tableau(formula)
is_satisfiable = tableau.build()
tableau.print_tree()

# Extract models
models = tableau.extract_all_models()
for model in models:
    print(f"Model: {model}")
```

### Testing

Run the comprehensive test suite:

```bash
# All tests
python -m pytest -v

# Specific test categories
python -m pytest test_tableau.py -v         # Core functionality
python -m pytest test_performance.py -v     # Performance tests
python -m pytest test_medium_optimizations.py -v  # Optimization tests
```

## Tableau Rules Implemented

- **Double Negation**: `¬¬A` → `A`
- **Conjunction**: `A ∧ B` → `A`, `B` (same branch)
- **Negated Conjunction**: `¬(A ∧ B)` → `¬A | ¬B` (branching)
- **Disjunction**: `A ∨ B` → `A | B` (branching)
- **Negated Disjunction**: `¬(A ∨ B)` → `¬A`, `¬B` (same branch)
- **Implication**: `A → B` → `¬A ∨ B` (branching)
- **Negated Implication**: `¬(A → B)` → `A`, `¬B` (same branch)

## Formula Syntax

Create formulas using Python classes:

```python
from formula import Atom, Negation, Conjunction, Disjunction, Implication

# Atoms
p, q, r = Atom("p"), Atom("q"), Atom("r")

# Logical operators
negation = Negation(p)                    # ¬p
conjunction = Conjunction(p, q)           # p ∧ q
disjunction = Disjunction(p, q)          # p ∨ q
implication = Implication(p, q)          # p → q

# Complex formulas
formula = Implication(
    Conjunction(p, q),  # (p ∧ q) → r
    r
)
```

## Performance Features

This implementation includes state-of-the-art tableau optimizations:

1. **Proper Termination**: No arbitrary iteration limits
2. **Formula Prioritization**: α-formulas expanded before β-formulas to minimize branching
3. **Subsumption Elimination**: Removes redundant branches automatically
4. **O(1) Closure Detection**: Fast contradiction detection using literal indexing
5. **Early Satisfiability Detection**: Terminates as soon as satisfying branch found
6. **Incremental Branch Representation**: Memory-efficient formula inheritance

## Output

The system provides detailed output including:

- **Tableau Trees**: Visual representation of the proof search
- **Branch Information**: Open/closed status with closure reasons
- **Satisfiability Results**: Clear satisfiable/unsatisfiable determination
- **Model Extraction**: Satisfying truth assignments for satisfiable formulas
- **Performance Metrics**: Timing and branch count statistics

## Examples

### Testing Tautologies

```python
# Test if a formula is a tautology
from formula import Atom, Disjunction, Negation
from tableau import Tableau

p = Atom("p")
tautology = Disjunction(p, Negation(p))  # p ∨ ¬p

# Test if negation is unsatisfiable (proving tautology)
tableau = Tableau(Negation(tautology))
is_tautology = not tableau.build()
print(f"Is tautology: {is_tautology}")
```

### Testing Logical Arguments

```python
# Test modus ponens: (p → q) ∧ p → q
from formula import Atom, Implication, Conjunction

p, q = Atom("p"), Atom("q")
premise1 = Implication(p, q)  # p → q
premise2 = p                  # p
conclusion = q                # q

# Test if premises imply conclusion
premises = Conjunction(premise1, premise2)
argument = Implication(premises, conclusion)

tableau = Tableau(Negation(argument))  # Test if argument is valid
is_valid = not tableau.build()
print(f"Argument is valid: {is_valid}")
```