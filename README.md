# Semantic Tableau System

A Python implementation of semantic tableau methods for automated theorem proving, supporting multiple logic systems including classical propositional logic and three-valued Weak Kleene logic (WK3).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## System Architecture

The system uses a consolidated architecture with three core modules:

### Core Modules
- `tableau_core.py` - Data structures, formulas, truth values, and signed formula system
- `tableau_engine.py` - Tableau construction algorithm with optimized branch management
- `tableau_rules.py` - Rule system supporting multiple logic implementations

### Legacy Implementations (Maintained)
- `tableau.py` - Classical propositional logic tableau implementation
- `wk3_tableau.py` - Weak Kleene logic (WK3) tableau implementation  
- `formula.py` - Formula representation classes and logical operators
- `truth_value.py` - Three-valued truth system for WK3
- `wk3_model.py` - Three-valued model evaluation

### Interface and Tools
- `cli.py` - Command-line interface supporting multiple logic systems
- `wk3_demo.py` - WK3 demonstration and examples
- `demo_componentized.py` - System capabilities demonstration

### Mode-Aware Extensions
- `mode_aware_tableau.py` - Logic mode separation (propositional vs first-order)
- `mode_aware_parser.py` - Mode-specific formula parsing and validation
- `logic_mode.py` - Mode detection and enforcement
- `term.py` - First-order terms (constants, variables, function applications)

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

### Python API - Consolidated System

```python
from tableau_core import Atom, Conjunction, Disjunction, Negation, Implication
from tableau_core import T, F, U, classical_signed_tableau, wk3_satisfiable, wk3_models

# Classical Logic using Signed Tableaux
p = Atom("p")
q = Atom("q")
formula = Implication(p, q)

# Check satisfiability
engine = classical_signed_tableau(T(formula))  # T:(p→q) - "p→q is true"
satisfiable = engine.build()
print(f"Satisfiable: {satisfiable}")

if satisfiable:
    models = engine.extract_all_models()
    print(f"Found {len(models)} models")

# Three-Valued Logic (WK3)
formula = Disjunction(p, Negation(p))  # p ∨ ¬p

# Check WK3 satisfiability
is_wk3_satisfiable = wk3_satisfiable(formula)
print(f"WK3 satisfiable: {is_wk3_satisfiable}")

# Get all WK3 models
wk3_model_list = wk3_models(formula)
print(f"WK3 models: {len(wk3_model_list)}")
```

### Python API - Legacy Implementations

```python
# Classical Logic (Original Implementation)
from tableau import Tableau
from formula import Atom, Conjunction, Disjunction, Negation, Implication

p = Atom("p")
q = Atom("q")
formula = Implication(p, q)

tableau = Tableau([formula])
is_satisfiable = tableau.build()
print(f"Satisfiable: {is_satisfiable}")

# Weak Kleene Logic (Original Implementation)
from wk3_tableau import WK3Tableau
from wk3_model import WK3Model

wk3_tableau = WK3Tableau([formula])
wk3_satisfiable = wk3_tableau.build()
print(f"WK3 satisfiable: {wk3_satisfiable}")

if wk3_satisfiable:
    models = wk3_tableau.extract_all_models()
    print(f"WK3 models: {len(models)}")
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
python -m pytest                              # All 227 tests

# Run specific test suites
python -m pytest test_tableau.py -v           # Classical logic (50 tests)
python -m pytest test_wk3.py -v              # WK3 logic (25 tests)
python -m pytest test_signed_tableau.py -v    # Signed tableaux (18 tests)
python -m pytest test_consolidated_tableau.py -v  # Consolidated system (68 tests)
python -m pytest test_performance.py -v       # Performance tests (4 tests)

# Quick verification
python -m pytest --tb=no -q                   # Brief output
```

### Core Test Suites

- **test_tableau.py** (50 tests) - Classical logic validation with literature examples
- **test_wk3.py** (25 tests) - WK3 logic semantics and model evaluation
- **test_performance.py** (4 tests) - Performance benchmarks and optimization validation
- **test_signed_tableau.py** (18 tests) - Signed tableau system validation
- **test_consolidated_tableau.py** (68 tests) - Consolidated architecture validation
- **test_predicate.py** (21 tests) - First-order logic term and predicate support
- **test_modes.py** (14 tests) - Logic mode management and validation
- **test_mode_aware_api.py** (18 tests) - Mode-aware parsing and API

### Demonstrations

```bash
# Classical logic reference implementation
python tableau.py

# WK3 logic demonstration
python wk3_demo.py

# Consolidated system capabilities
python demo_componentized.py

# Interactive CLI
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
- **Closure Detection**: O(1) with pre-computed indices

## Architecture Documentation

For detailed technical documentation, see:

- **ARCHITECTURE.md** - Complete system architecture and implementation details
- **OPTIMIZATIONS.md** - Performance optimization strategies and analysis
- **TECHNICAL_ANALYSIS.md** - Implementation quality assessment
- **WEAK_KLEENE_PLAN.md** - WK3 implementation design and semantics

## Extension Framework

The system supports extension with new logic systems:

### Adding New Logic Systems

1. **Define Sign System**: Create sign classes for the new logic
2. **Implement Rules**: Create tableau rules following the `SignedTableauRule` interface
3. **Register System**: Add rules to the `SignedRuleRegistry`

Example modal logic extension:
```python
class ModalSign:
    def __init__(self, modality: str, polarity: str):
        self.modality = modality  # □ or ◇
        self.polarity = polarity  # T or F

class ModalNecessityRule(AlphaRule):
    """□T:A → T:A"""
    priority = 1
    
    def applies_to(self, signed_formula: SignedFormula) -> bool:
        return (isinstance(signed_formula.sign, ModalSign) and
                signed_formula.sign.modality == "□")
```

### Adding New Formula Types

1. **Define Formula Class**: Extend the `Formula` base class
2. **Implement Methods**: Provide `__str__`, `__eq__`, and `__hash__` methods
3. **Create Rules**: Implement corresponding tableau rules

## Contributing

When extending the system:

1. **Maintain Logical Correctness**: All extensions must implement proper logical semantics
2. **Preserve Performance**: Maintain O(1) operations for critical paths
3. **Add Comprehensive Tests**: Include systematic test coverage for new functionality
4. **Document Semantic Choices**: Explain logical and implementation decisions

## Implementation Notes

### Design Principles

1. **Consolidation**: Single unified system instead of multiple separate implementations
2. **Direct Implementation**: Algorithms implemented directly rather than through abstraction layers
3. **Signed Tableau Foundation**: Universal signed tableau notation (T:φ, F:φ, U:φ)
4. **Performance Optimization**: Critical operations optimized for O(1) complexity
5. **Logical Correctness**: Each operator implemented according to standard semantics

### Code Quality

- Full type hints throughout the codebase
- Comprehensive error handling and validation
- Extensive documentation with examples
- 227 tests with 100% pass rate
- Consistent coding patterns and naming conventions

The system demonstrates how semantic tableau methods can be implemented with clean architecture, optimized performance, and support for multiple logical systems suitable for both research and educational applications.