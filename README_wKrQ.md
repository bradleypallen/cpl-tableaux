# wKrQ: Three-Valued Weak Kleene Logic with Restricted Quantification

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-79%20passing-green.svg)](#testing)

A research-grade implementation of three-valued weak Kleene logic with restricted quantification, featuring industrial-grade performance optimizations and comprehensive tableau-based automated reasoning.

## Quick Start

### Installation

```bash
git clone https://github.com/username/tableaux.git
cd tableaux
pip install -e .
```

### Basic Usage

```bash
# Test a simple formula
python -m wkrq "p & q"

# Test with three-valued semantics
python -m wkrq --sign=N "p | ~p"

# Interactive mode
python -m wkrq
```

### Python API

```python
from wkrq import Formula, solve, T, F, M, N

# Create formulas
p, q = Formula.atoms("p", "q")
formula = p & (q | ~p)

# Test satisfiability
result = solve(formula, T)
print(f"Satisfiable: {result.satisfiable}")
print(f"Models: {result.models}")
```

## What is wKrQ?

**wKrQ** (weak Kleene logic with restricted quantification) is a three-valued logic system designed for reasoning under uncertainty and vagueness. Unlike classical binary logic, wKrQ includes a third truth value (undefined) to handle incomplete information naturally.

### Key Features

- **Three-Valued Semantics**: True (t), False (f), Undefined (e)
- **Weak Kleene Logic**: Any operation with undefined input produces undefined output
- **Four Tableau Signs**: T, F, M, N for systematic proof construction
- **Restricted Quantification**: Domain-limited first-order reasoning
- **Industrial Performance**: Sub-millisecond response times with optimized algorithms
- **Research Quality**: Comprehensive testing and literature validation

### Why Weak Kleene?

Weak Kleene logic is particularly useful for:

- **Philosophical Logic**: Handling vague predicates and borderline cases
- **AI Reasoning**: Managing incomplete knowledge and uncertainty
- **Database Systems**: Three-valued logic for null/unknown values
- **Formal Methods**: Reasoning about partial specifications

## Logic System Overview

### Truth Values

| Symbol | Meaning | Description |
|--------|---------|-------------|
| **t** | True | Classical truth |
| **f** | False | Classical falsity |
| **e** | Undefined | Neither true nor false |

### Tableau Signs

| Sign | Meaning | Truth Conditions |
|------|---------|------------------|
| **T** | Must be true | Formula has truth value t |
| **F** | Must be false | Formula has truth value f |
| **M** | Multiple | Formula can be t or f |
| **N** | Neither | Formula has truth value e |

### Truth Tables (Weak Kleene)

```
Conjunction (∧):     Disjunction (∨):     Negation (~):
  ∧ | t | f | e        ∨ | t | f | e        ~ | t | f | e
  --|---|---|---       --|---|---|---       --|---|---|---
  t | t | f | e        t | t | t | e          | f | t | e
  f | f | f | e        f | t | f | e
  e | e | e | e        e | e | e | e

Implication (→):
  → | t | f | e
  --|---|---|---
  t | t | f | e
  f | t | t | e
  e | e | e | e
```

**Key Property**: In weak Kleene logic, any operation involving undefined (e) produces undefined (e).

## Examples

### Basic Propositional Logic

```python
from wkrq import Formula, solve, valid, T, F, M, N

# Create atoms
p, q, r = Formula.atoms("p", "q", "r")

# Test classical tautology
tautology = p | ~p
print(f"p | ~p is valid: {valid(tautology)}")

# Test with different signs
result_t = solve(tautology, T)  # Must be true
result_n = solve(tautology, N)  # Can be undefined
print(f"Can be undefined: {result_n.satisfiable}")
```

### Three-Valued Reasoning

```python
# Test undefined value propagation
borderline = Formula.atom("BorderlineCase")
definite = Formula.atom("DefiniteCase")

# In weak Kleene: undefined ∧ true = undefined
conjunction = borderline & definite
result = solve(conjunction, N)  # Test if can be undefined
print(f"Conjunction can be undefined: {result.satisfiable}")

# Show models
if result.models:
    for model in result.models:
        print(f"Model: {model}")
```

### First-Order Logic with Restricted Quantification

```python
from wkrq import Formula

# Set up first-order reasoning
x = Formula.variable("X")
human_x = Formula.predicate("Human", [x])
mortal_x = Formula.predicate("Mortal", [x])
alice = Formula.constant("alice")

# Restricted universal: "All humans are mortal"
all_humans_mortal = Formula.restricted_forall(x, human_x, mortal_x)

# Individual fact: "Alice is human"
alice_human = Formula.predicate("Human", [alice])

# Combined reasoning
premises = all_humans_mortal & alice_human
result = solve(premises, T)

print(f"Premises satisfiable: {result.satisfiable}")
print(f"Number of models: {len(result.models)}")
```

### Philosophical Application: Sorites Paradox

```python
# Model the sorites paradox with three-valued logic
heap_1000 = Formula.atom("Heap1000")  # Clearly a heap
heap_999 = Formula.atom("Heap999")    # Borderline case
heap_1 = Formula.atom("Heap1")        # Clearly not a heap

# Sorites principle
sorites_step = heap_1000.implies(heap_999)

# The paradox setup
paradox = heap_1000 & sorites_step & ~heap_1

# Test satisfiability
result = solve(paradox, T)
print(f"Paradox is satisfiable: {result.satisfiable}")

# Can the borderline case be undefined?
borderline_undefined = solve(heap_999, N)
print(f"999 grains can be undefined: {borderline_undefined.satisfiable}")
```

## Performance

wKrQ achieves industrial-grade performance through sophisticated optimizations:

### Benchmarks

- **Simple formulas**: < 1ms response time
- **Complex formulas**: Linear scaling with formula size
- **First-order reasoning**: Efficient restricted quantifier handling
- **Memory usage**: Controlled branch and node growth

### Optimizations

1. **O(1) Contradiction Detection**: Hash-based formula indexing
2. **Alpha/Beta Prioritization**: Non-branching rules processed first
3. **Intelligent Branch Selection**: Least complex branches chosen first
4. **Early Termination**: Stops at first satisfying model for satisfiability
5. **Subsumption Elimination**: Removes redundant formulas

### Performance Example

```python
import time
from wkrq import Formula, solve, T

# Create complex formula
atoms = [Formula.atom(f"p{i}") for i in range(20)]
formula = atoms[0]
for atom in atoms[1:]:
    formula = formula & atom

# Benchmark
start = time.time()
result = solve(formula, T)
end = time.time()

print(f"Formula with 20 atoms: {(end-start)*1000:.2f}ms")
print(f"Tableau nodes: {result.total_nodes}")
print(f"Satisfiable: {result.satisfiable}")
```

## Command Line Interface

### Basic Commands

```bash
# Test formula satisfiability
python -m wkrq "p & q"

# Specify tableau sign
python -m wkrq --sign=T "p | ~p"  # Must be true
python -m wkrq --sign=F "p & ~p"  # Must be false
python -m wkrq --sign=M "p"       # Can be true or false
python -m wkrq --sign=N "p"       # Must be undefined

# Show all models
python -m wkrq --models "p | q"

# Verbose output with tableau construction
python -m wkrq --verbose --tableau "p -> q"

# JSON output for programmatic use
python -m wkrq --format=json "p & (q | r)"
```

### Interactive Mode

```bash
python -m wkrq
```

```
wKrQ Interactive Mode - Three-Valued Weak Kleene Logic
Type 'help' for commands, 'quit' to exit.

wKrQ> test p & q
Testing formula: p & q
Result: SATISFIABLE
Models: [{p=t, q=t}]

wKrQ> sign N
Current sign: N (neither/undefined)

wKrQ> test p | ~p
Testing formula: p | ~p with sign N
Result: SATISFIABLE (can be undefined in weak Kleene)
Models: [{p=e}]

wKrQ> help
Available commands:
  test FORMULA     - Test formula satisfiability
  models FORMULA   - Show all models
  tableau FORMULA  - Show tableau construction
  sign SIGN       - Set tableau sign (T, F, M, N)
  valid FORMULA   - Test validity
  help            - Show this help
  quit            - Exit

wKrQ> quit
```

### First-Order Syntax

```bash
# Predicates
python -m wkrq "P(a) & Q(b)"

# Restricted quantifiers
python -m wkrq "[∃X Student(X)]Human(X)"
python -m wkrq "[∀X Human(X)]Mortal(X)"

# Complex first-order reasoning
python -m wkrq "[∃X Student(X)]Human(X) & [∀X Human(X)]Mortal(X) & Student(alice)"
```

## Testing

The system includes comprehensive testing with 79 tests covering:

- **Correctness**: Semantic and proof-theoretic validity
- **Performance**: Speed and memory benchmarks  
- **Literature**: Validation against published results
- **Regression**: Prevention of performance degradation

```bash
# Run all tests
python -m pytest tests/wkrq/ -v

# Run specific test categories
python -m pytest tests/wkrq/test_wkrq_basic.py -v          # Basic functionality
python -m pytest tests/wkrq/test_first_order.py -v         # First-order logic
python -m pytest tests/wkrq/test_literature_cases.py -v    # Literature validation
python -m pytest tests/wkrq/test_performance_regression.py -v  # Performance
```

## Documentation

### Complete Documentation

- **[CLI Guide](docs/wKrQ_CLI_GUIDE.md)**: Comprehensive command-line usage
- **[API Reference](docs/wKrQ_API_REFERENCE.md)**: Complete Python API documentation
- **[Architecture](docs/wKrQ_ARCHITECTURE.md)**: System design and implementation details

### Examples

- **[Philosophical Examples](examples/philosophical_examples.py)**: Vagueness, sorites paradox, epistemic reasoning
- **[Performance Showcase](examples/performance_showcase.py)**: Optimization demonstrations and benchmarks

### Quick References

- **Truth Values**: t (true), f (false), e (undefined)
- **Signs**: T (must be true), F (must be false), M (multiple), N (neither)
- **Connectives**: `&` (and), `|` (or), `~` (not), `->` (implies)
- **Quantifiers**: `[∃X P(X)]Q(X)` (restricted exists), `[∀X P(X)]Q(X)` (restricted forall)

## Research Applications

wKrQ is designed for:

### Theoretical Research
- **Many-valued logic studies**: Weak vs strong Kleene comparison
- **Philosophical logic**: Vagueness, sorites paradox, epistemic reasoning
- **Proof theory**: Tableau method optimization and completeness

### Practical Applications  
- **AI reasoning**: Uncertainty and incomplete knowledge handling
- **Database systems**: Three-valued logic for null values
- **Formal verification**: Partial specification reasoning
- **Expert systems**: Knowledge representation with uncertainty

## Architecture

### Core Components

```
wKrQ System
├── Formula System          # Propositional and first-order formulas
├── Semantic Engine        # Three-valued weak Kleene operations
├── Sign System           # Four tableau signs (T, F, M, N)
├── Tableau Engine        # Optimized proof search
├── Parser               # String to formula conversion
└── Interfaces          # CLI and Python API
```

### Key Classes

```python
# Core classes
Formula                 # Base formula class
WeakKleeneSemantics    # Three-valued semantic operations
Tableau                # Tableau construction engine
TableauResult          # Rich result objects with models and statistics

# Formula types
PropositionalAtom      # p, q, r
CompoundFormula       # p & q, p | q, ~p, p -> q
PredicateFormula      # P(x), R(x,y)
RestrictedQuantifierFormula  # [∃X P(X)]Q(X), [∀X P(X)]Q(X)
```

## Contributing

### Development Setup

```bash
git clone https://github.com/username/tableaux.git
cd tableaux
pip install -e ".[dev]"
python -m pytest tests/wkrq/ -v
```

### Code Quality

- **Type hints**: Full type annotation coverage
- **Testing**: 79 comprehensive tests with >95% coverage
- **Documentation**: Extensive inline and external documentation
- **Performance**: Benchmark tests prevent regression

### Extension Points

The system is designed for extensibility:

- **New connectives**: Add operators with semantic definitions and tableau rules  
- **New logic systems**: Implement different many-valued logics
- **Optimization strategies**: Custom branch selection and subsumption methods
- **Interface additions**: Web interfaces, IDE plugins, visualization tools

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Citation

If you use wKrQ in academic research, please cite:

```bibtex
@software{wkrq2025,
  title={wKrQ: Three-Valued Weak Kleene Logic with Restricted Quantification},
  author={[Authors]},
  year={2025},
  url={https://github.com/username/tableaux},
  note={Version 2.0}
}
```

## Support

- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory  
- **Issues**: GitHub issue tracker
- **Performance**: Include `--stats` output in performance reports

---

*wKrQ combines theoretical rigor with industrial-grade performance, making three-valued logic accessible for both research and practical applications.*