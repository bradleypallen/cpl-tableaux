# Semantic Tableau System

A Python implementation of semantic tableau methods for automated theorem proving, supporting multiple logic systems including classical propositional logic and three-valued Weak Kleene logic (WK3).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## System Architecture

The system uses a unified architecture with a single core module:

### Core Module
- `tableau_core.py` - Complete implementation containing:
  - Formula representation (atoms, connectives, predicates, quantifiers)
  - Truth value systems (classical, three-valued WK3)
  - Sign systems (classical T/F, three-valued T/F/U, epistemic wKrQ T/F/M/N)
  - Optimized tableau engine with step-by-step visualization
  - Tableau rules for multiple logic systems
  - Model extraction and satisfiability checking
  - Mode-aware system for propositional and first-order logic

### Supporting Modules
- `unified_model.py` - Unified model representation for all logic systems
- `cli.py` - Command-line interface supporting multiple logic systems

### Demonstration Programs
- `wkrq_countermodel_demo.py` - Ferguson's wKrQ epistemic logic demonstrations
- `wkrq_theoretical_demo.py` - Theoretical insights for weak Kleene logic
- `verify_kleene_tables.py` - Verification of weak Kleene truth tables

## Installation

This is a pure Python implementation with no external dependencies for core functionality:

```bash
# Clone the repository
git clone <repository-url>
cd tableaux

# Run tests to verify installation
python -m pytest
```

## Usage

### Command Line Interface

```bash
# Classical logic
python cli.py "p | ~p"                    # Tautology check
python cli.py "p & ~p"                    # Contradiction check

# Weak Kleene logic (WK3)
python cli.py --wk3 "p | ~p"              # WK3 satisfiability check
python cli.py --wk3 "p & ~p"              # WK3 satisfiability check

# Interactive mode
python cli.py                             # Interactive tableau system
```

### Python API

```python
from tableau_core import (
    # Formula construction
    Atom, Conjunction, Disjunction, Negation, Implication,
    Predicate, Constant, Variable,
    # Signs for different logics
    T, F, T3, F3, U, TF, FF, M, N,
    # Truth values
    t, f, e,
    # Tableau functions
    classical_signed_tableau, three_valued_signed_tableau,
    wkrq_signed_tableau, ferguson_signed_tableau,
    wk3_satisfiable, wk3_models
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

# Three-Valued Logic (WK3)
formula = Disjunction(p, Negation(p))  # p ∨ ¬p

# Check WK3 satisfiability
is_wk3_satisfiable = wk3_satisfiable(formula)
print(f"WK3 satisfiable: {is_wk3_satisfiable}")

# Get all WK3 models
wk3_model_list = wk3_models(formula)
for model in wk3_model_list:
    print(f"Model: p={model.get_assignment('p')}")

# Ferguson's wKrQ Epistemic Logic
r = Atom("r")
epistemic_formula = Conjunction(p, q)

# Check with epistemic signs
tableau = ferguson_signed_tableau([M(epistemic_formula), N(r)])
result = tableau.build()
print(f"Epistemic satisfiability: {result}")

# First-Order Logic
x = Variable("x")
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

### Weak Kleene Logic (WK3)

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
python -m pytest                              # All tests

# Run specific test suites
python -m pytest test_comprehensive.py -v    # Unified test suite (42 tests)
python -m pytest test_literature_examples.py -v  # Literature-based tests (26 tests)

# Run tutorial tests
python -m pytest tutorial*_test.py -v        # Tutorial validation tests

# Quick verification
python -m pytest --tb=no -q                   # Brief output
```

### Core Test Suites

- **test_comprehensive.py** (42 tests) - Complete validation of unified implementation
- **test_literature_examples.py** (26 tests) - Examples from Priest, Fitting, Smullyan, Ferguson
- **tutorial*_test.py** - Tutorial code validation

### Demonstrations

```bash
# Ferguson's wKrQ epistemic logic demonstrations
python wkrq_countermodel_demo.py

# Theoretical insights demonstration
python wkrq_theoretical_demo.py

# Verify weak Kleene truth tables
python verify_kleene_tables.py

# Interactive CLI with multiple logic support
python cli.py
```

## Performance Characteristics

The implementation includes standard tableau optimizations:

### Algorithmic Optimizations
- **O(1) closure detection** using literal indexing
- **Rule prioritization** (α-rules before β-rules) 
- **Early termination** for satisfiability checking
- **Subsumption elimination** for branch pruning

### Performance Metrics
- Complete test suite (227 tests) executes in under 0.2 seconds
- Efficient memory usage with shallow copying for branch management
- Cached rule lookup for O(1) rule selection

### Complexity Analysis
- **Time Complexity**: O(n log n) best case, O(2ⁿ) worst case (inherent to tableau method)
- **Space Complexity**: O(b × f) where b = branches, f = formulas per branch
- **Closure Detection**: O(1) with hash-based formula tracking
- **Rule Selection**: O(log n) with priority-based ordering

## Architecture Documentation

For detailed technical documentation, see:

- **ARCHITECTURE.md** - Complete system architecture and implementation details
- **OPTIMIZATIONS.md** - Performance optimization strategies and analysis
- **TECHNICAL_ANALYSIS.md** - Implementation quality assessment
- **WEAK_KLEENE_PLAN.md** - WK3 implementation design and semantics

## Extension Framework

The unified system supports extension with new logic systems:

### Adding New Logic Systems

1. **Define Sign System**: Create sign classes extending the `Sign` base class
2. **Implement Rules**: Add rules to the `OptimizedTableauEngine._initialize_tableau_rules()` method
3. **Create Helper Functions**: Add convenience functions for the new logic

Example modal logic extension:
```python
# In tableau_core.py
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

1. **Define Formula Class**: Extend the `Formula` base class in `tableau_core.py`
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

- **Multi-Logic Support**: Classical, WK3, wKrQ epistemic logic in one system
- **Enhanced Visualization**: Shows specific rules applied and tableau tree structure
- **Optimized Performance**: α/β rule prioritization, subsumption elimination
- **Comprehensive Testing**: Literature-based examples validate correctness
- **Mode Awareness**: Separate handling of propositional and first-order logic

## Further Reading

For comprehensive documentation and detailed guides, see:

### Core Documentation
- **[TUTORIALS.md](TUTORIALS.md)** - Step-by-step tutorials covering basic to advanced usage
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation with examples for all functions and classes
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture, design patterns, and implementation details
- **[CLI_GUIDE.md](CLI_GUIDE.md)** - Comprehensive command-line interface usage guide with examples

### Implementation Guides
- **[BUILDING_GUIDE.md](BUILDING_GUIDE.md)** - Step-by-step guide for extending the system with new logic systems
- **[OPTIMIZATIONS.md](OPTIMIZATIONS.md)** - Performance optimization strategies and analysis
- **[TECHNICAL_ANALYSIS.md](TECHNICAL_ANALYSIS.md)** - Implementation quality assessment and code review

### Logic System Specific
- **[WEAK_KLEENE_PLAN.md](WEAK_KLEENE_PLAN.md)** - WK3 implementation design, semantics, and theoretical background
- **[IMPLEMENTATION_PLAN_WKRQ.md](IMPLEMENTATION_PLAN_WKRQ.md)** - Ferguson's wKrQ epistemic logic implementation plan
- **[INTERFACE_CHANGES_WKRQ.md](INTERFACE_CHANGES_WKRQ.md)** - Interface evolution for epistemic logic support

### Development
- **[CLAUDE.md](CLAUDE.md)** - Project instructions and development guidelines for AI assistants

The system demonstrates how semantic tableau methods can be implemented with clean architecture, optimized performance, and support for multiple logical systems suitable for both research and educational applications.