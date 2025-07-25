# Semantic Tableau System

A Python implementation of semantic tableau methods for automated theorem proving, supporting multiple logic systems including classical propositional logic and three-valued weak Kleene logic.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## System Architecture

The system uses a unified architecture with a single core module:

### Core Modules
- `src/tableaux/tableau_core.py` - Complete implementation containing:
  - Formula representation (atoms, connectives, predicates, quantifiers)
  - Truth value systems (classical, three-valued weak Kleene)
  - Sign systems (classical T/F, three-valued T/F/U, epistemic wKrQ T/F/M/N)
  - Optimized tableau engine with step-by-step visualization
  - Tableau rules for multiple logic systems
  - Model extraction and satisfiability checking
  - Mode-aware system for propositional and first-order logic
- `src/tableaux/unified_model.py` - Unified model representation for all logic systems
- `src/tableaux/cli.py` - Command-line interface supporting multiple logic systems

### Examples and Demonstrations
- `examples/wkrq_countermodel_demo.py` - wKrQ demonstrations
- `examples/wkrq_theoretical_demo.py` - Theoretical insights for weak Kleene logic
- `examples/verify_kleene_tables.py` - Verification of weak Kleene truth tables
- `examples/tutorials/` - Interactive tutorial examples

## Installation

### From PyPI (Recommended)

```bash
pip install tableaux
```

### From Source

```bash
# Clone the repository
git clone https://github.com/bradleypallen/tableaux.git
cd tableaux

# Install in development mode
pip install -e .

# Run tests to verify installation
python -m pytest tests/
```

## Usage

### Command Line Interface

After installation, use the `tableaux` command:

```bash
# Classical logic
tableaux "p | ~p"                         # Tautology check
tableaux "p & ~p"                         # Contradiction check

# weak Kleene logic
tableaux --wk3 "p | ~p"                   # weak Kleene satisfiability check
tableaux --wk3 "p & ~p"                   # weak Kleene satisfiability check

# Interactive mode
tableaux                                  # Interactive tableau system
```

**Development Mode**: If running from source without installation:
```bash
python -m tableaux.cli "formula"          # Alternative command
```

### Python API

```python
from tableaux import (
    # Formula construction
    Atom, Conjunction, Disjunction, Negation, Implication,
    Predicate, Constant, Variable,
    # Signs for different logics
    T, F, T3, F3, U, TF, FF, M, N,
    # Truth values
    t, f, e,
    # Tableau functions
    classical_signed_tableau, three_valued_signed_tableau,
    wkrq_signed_tableau, ferguson_signed_tableau
)

# Classical Logic using Signed Tableaux
p = Atom("p")
q = Atom("q")
formula = Implication(p, q)

# Check satisfiability with step tracking
tableau = classical_signed_tableau(T(formula), track_steps=True)
satisfiable = tableau.build()
print(f"Satisfiable: {satisfiable}")

# Show step-by-step construction
if hasattr(tableau, 'print_construction_steps'):
    tableau.print_construction_steps()

if satisfiable:
    models = tableau.extract_all_models()
    print(f"Found {len(models)} models")

# Three-Valued Logic (weak Kleene)
formula = Disjunction(p, Negation(p))  # p ∨ ¬p

# Check weak Kleene satisfiability (formula is satisfiable if it can be true OR undefined)
t3_tableau = three_valued_signed_tableau(T3(formula))
u_tableau = three_valued_signed_tableau(U(formula))
t3_satisfiable = t3_tableau.build()
u_satisfiable = u_tableau.build()
is_wk3_satisfiable = t3_satisfiable or u_satisfiable
print(f"weak Kleene satisfiable: {is_wk3_satisfiable}")

# Get all weak Kleene models
wk3_models = []
if t3_satisfiable:
    wk3_models.extend(t3_tableau.extract_all_models())
if u_satisfiable:
    wk3_models.extend(u_tableau.extract_all_models())

for model in wk3_models:
    print(f"Model: {model}")

# wKrQ Epistemic Logic
r = Atom("r")
epistemic_formula = Conjunction(p, q)

# Check with epistemic signs
tableau = ferguson_signed_tableau([M(epistemic_formula), N(r)])
result = tableau.build()
print(f"Epistemic satisfiability: {result}")

# First-Order Logic
X = Variable("X")
a = Constant("a")
Student = lambda term: Predicate("Student", [term])
Human = lambda term: Predicate("Human", [term])

# Check predicate satisfiability
pred_formula = Implication(Student(a), Human(a))
tableau = classical_signed_tableau(T(pred_formula))
result = tableau.build()
print(f"Predicate satisfiable: {result}")
```

## Logic Systems

### Classical Propositional Logic

Standard two-valued logic with truth values true and false.

**Supported Operators:**
- Atoms: `p`, `q`, `r`, etc.
- Negation: `¬p` (NOT p)
- Conjunction: `p ∧ q` (p AND q)
- Disjunction: `p ∨ q` (p OR q)  
- Implication: `p → q` (p IMPLIES q)

**Signed Tableau Notation:**
- `T:φ` - formula φ is true
- `F:φ` - formula φ is false

### weak Kleene Logic

Three-valued logic with truth values true, false, and undefined.

**Truth Values:**
- `t` (true)
- `f` (false)
- `e` (undefined/error)

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

**Signed Tableau Notation:**
- `T:φ` - formula φ is true
- `F:φ` - formula φ is false
- `U:φ` - formula φ is undefined

### First-Order Logic Extensions

Basic support for first-order logic with ground terms.

**Supported Elements:**
- Constants: `a`, `b`, `c`
- Variables: `x`, `y`, `z`
- Predicates: `P(x)`, `Q(a,b)`, `R(x,y,z)`
- Function applications: `f(x)`, `g(a,b)`

## Development

### Running Tests

The system includes comprehensive test coverage:

```bash
# Run all tests
python -m pytest tests/                       # All tests

# Run specific test suites
python -m pytest tests/test_comprehensive.py -v    # Unified test suite (35 tests)
python -m pytest tests/test_literature_examples.py -v  # Literature-based tests (26 tests)

# Run tutorial tests
python -m pytest examples/tutorials/ -v       # Tutorial validation tests

# Quick verification
python -m pytest tests/ --tb=no -q            # Brief output
```

### Core Test Suites

- **tests/test_comprehensive.py** (35 tests) - Complete validation of unified implementation
- **tests/test_literature_examples.py** (26 tests) - Examples from Priest, Fitting, Smullyan, Ferguson
- **examples/tutorials/tutorial*_test.py** - Tutorial code validation

### Demonstrations

```bash
# wKrQ demonstrations
python examples/wkrq_countermodel_demo.py

# Theoretical insights demonstration
python examples/wkrq_theoretical_demo.py

# Verify weak Kleene truth tables
python examples/verify_kleene_tables.py

# Interactive CLI with multiple logic support
tableaux
```

## Performance Characteristics

The implementation includes standard tableau optimizations:

### Algorithmic Optimizations
- **O(1) closure detection** using literal indexing
- **Rule prioritization** (α-rules before β-rules) 
- **Early termination** for satisfiability checking
- **Subsumption elimination** for branch pruning

### Performance Metrics
- Complete test suite (69 tests) executes in under 0.2 seconds
- Efficient memory usage with shallow copying for branch management
- Cached rule lookup for O(1) rule selection

### Complexity Analysis
- **Time Complexity**: O(n log n) best case, O(2ⁿ) worst case (inherent to tableau method)
- **Space Complexity**: O(b × f) where b = branches, f = formulas per branch
- **Closure Detection**: O(1) with hash-based formula tracking
- **Rule Selection**: O(log n) with priority-based ordering

## Architecture Documentation

For detailed technical documentation, see:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Complete system architecture and implementation details
- **[OPTIMIZATIONS.md](docs/OPTIMIZATIONS.md)** - Performance optimization strategies and analysis
- **[docs/archive/historical-design-docs/TECHNICAL_ANALYSIS.md](docs/archive/historical-design-docs/TECHNICAL_ANALYSIS.md)** - Implementation quality assessment
- **[docs/archive/historical-design-docs/WEAK_KLEENE_PLAN.md](docs/archive/historical-design-docs/WEAK_KLEENE_PLAN.md)** - weak Kleene implementation design and semantics

## Extension Framework

The unified system supports extension with new logic systems:

### Adding New Logic Systems

1. **Define Sign System**: Create sign classes extending the `Sign` base class
2. **Implement Rules**: Add rules to the `OptimizedTableauEngine._initialize_tableau_rules()` method
3. **Create Helper Functions**: Add convenience functions for the new logic

Example modal logic extension:
```python
# In src/tableaux/tableau_core.py
class ModalSign(Sign):
    def __init__(self, modality: str, polarity: str):
        self.modality = modality  # □ or ◇
        self.polarity = polarity  # T or F
    
    def is_contradictory_with(self, other: 'Sign') -> bool:
        # Define modal contradiction rules
        pass

# Add to OptimizedTableauEngine._initialize_tableau_rules()
if self.sign_system == "modal":
    rules['box_T'] = [TableauRule(
        rule_type="alpha",
        premises=["□T:A"],
        conclusions=[["T:A"]],
        priority=1,
        name="Box-T (α)"
    )]
```

### Adding New Formula Types

1. **Define Formula Class**: Extend the `Formula` base class in `src/tableaux/tableau_core.py`
2. **Implement Required Methods**: `__str__`, `__eq__`, `__hash__`, `is_atomic()`, etc.
3. **Add Tableau Rules**: Update rule initialization for the new formula type

## Contributing

When extending the system:

1. **Maintain Logical Correctness**: All extensions must implement proper logical semantics
2. **Preserve Performance**: Maintain O(1) operations for critical paths
3. **Add Comprehensive Tests**: Include systematic test coverage for new functionality
4. **Document Semantic Choices**: Explain logical and implementation decisions

## Implementation Notes

### Design Principles

1. **Unified Architecture**: All logic systems in a single core module
2. **Optimized Implementation**: Industrial-grade algorithms with O(1) closure detection
3. **Signed Tableau Foundation**: Universal signed tableau notation supporting multiple sign systems
4. **Educational Visualization**: Step-by-step tableau construction with tree structure display
5. **Literature-Based**: Implementation follows standard references (Smullyan, Priest, Fitting, Ferguson)

### Key Features

- **Multi-Logic Support**: Classical, weak Kleene, wKrQ in one system
- **Enhanced Visualization**: Shows specific rules applied and tableau tree structure
- **Optimized Performance**: α/β rule prioritization, subsumption elimination
- **Comprehensive Testing**: Literature-based examples validate correctness
- **Mode Awareness**: Separate handling of propositional and first-order logic

## Further Reading

For comprehensive documentation and detailed guides, see:

### Core Documentation
- **[TUTORIALS.md](docs/TUTORIALS.md)** - Step-by-step tutorials covering basic to advanced usage
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete API documentation with examples for all functions and classes
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Detailed system architecture, design patterns, and implementation details
- **[CLI_GUIDE.md](docs/CLI_GUIDE.md)** - Comprehensive command-line interface usage guide with examples

### Implementation Guides
- **[BUILDING_GUIDE.md](docs/BUILDING_GUIDE.md)** - Step-by-step guide for extending the system with new logic systems
- **[OPTIMIZATIONS.md](docs/OPTIMIZATIONS.md)** - Performance optimization strategies and analysis

### Development
- **[CLAUDE.md](CLAUDE.md)** - Project instructions and development guidelines for AI assistants
- **[docs/archive/historical-design-docs/](docs/archive/historical-design-docs/)** - Historical design documents from before the July 2025 consolidation

The system demonstrates how semantic tableau methods can be implemented with clean architecture, optimized performance, and support for multiple logical systems suitable for both research and educational applications.