# Propositional Logic Tableaux

Semantic tableau systems for both Classical Propositional Logic (CPL) and Weak Kleene Logic (WK3) with optimizations and full CLI support.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Files

### Core Logic Systems
- `tableau.py` - Classical propositional logic tableau implementation
- `wk3_tableau.py` - Weak Kleene logic (WK3) tableau implementation  
- `formula.py` - Formula representation classes and logical operators
- `truth_value.py` - Three-valued truth system for WK3
- `wk3_model.py` - Three-valued model evaluation for WK3

### Componentized Rule System (New Architecture)
- `componentized_tableau.py` - Unified tableau engine for any logic system
- `tableau_rules.py` - Abstract rule system interfaces and protocols
- `logic_system.py` - Logic system registry and component management
- `classical_rules.py` - Concrete classical logic tableau rules
- `classical_components.py` - Classical logic components (branches, closure detection, etc.)
- `wk3_rules.py` - Concrete WK3 tableau rules with three-valued semantics
- `wk3_components.py` - WK3 components with three-valued branch management
- `builtin_logics.py` - Standard logic system definitions and registry

### Interface and Tools
- `cli.py` - Command-line interface supporting both CPL and WK3 modes
- `wk3_demo.py` - Comprehensive WK3 demonstration and examples
- `demo_componentized.py` - Demonstration of componentized rule system

### Testing and Documentation
- `test_comprehensive.py` - Comprehensive test suite (42 tests covering all functionality)
- `test_tableau.py` - Classical logic test suite (50+ tests)
- `test_wk3.py` - WK3 test suite (25+ tests)
- `test_performance.py` - Performance benchmarks and optimization tests
- `test_medium_optimizations.py` - Optimization feature tests
- `test_componentized_rules.py` - Component system tests (18 tests)
- `OPTIMIZATIONS.md` - Documentation of performance improvements
- `TECHNICAL_ANALYSIS.md` - Analysis and assessment of implementation quality
- `WEAK_KLEENE_PLAN.md` - WK3 implementation plan and design notes

## Installation

This is a pure Python implementation with no external dependencies for core functionality:

```bash
# Clone the repository
git clone <repository-url>
cd tableaux

# Optional: Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Optional: Install testing dependencies
pip install pytest
```

## Usage

### Basic Usage

**Legacy Direct Usage:**
```bash
python tableau.py          # Classical logic demonstration  
python wk3_demo.py         # Weak Kleene logic demonstration
```

**Componentized System:**
```bash
python demo_componentized.py  # Unified system demonstration
```

**Interactive CLI (supports both logics):**
```bash
python cli.py              # Interactive mode with mode switching
python cli.py "formula"    # Direct command-line usage  
python cli.py --wk3 "formula"  # WK3 mode from command line
```

### Command-Line Interface

The CLI provides both interactive and command-line modes for testing formulas in either Classical Propositional Logic or Weak Kleene Logic (WK3).

#### Interactive Mode

Start the interactive interface:

```bash
python cli.py
```

Example interactive session:
```
============================================================
SEMANTIC TABLEAU SYSTEM
============================================================
Enter propositional logic formulas to test satisfiability.

Syntax:
  Atoms: p, q, r, x, y, etc.
  Negation: ~p or ¬p
  Conjunction: p & q or p ∧ q
  Disjunction: p | q or p ∨ q
  Implication: p -> q or p → q
  Parentheses: (p & q) -> r

Commands:
  help     - Show this help
  history  - Show formula history
  examples - Show example formulas
  multi    - Enter multiple formulas mode
  quit     - Exit
============================================================

Tableau> p | ~p
Parsed formula: (p ∨ ¬p)
Testing satisfiability...
----------------------------------------

RESULT: SATISFIABLE

Show full tableau tree? (y/n): y

======================================================================
SEMANTIC TABLEAU TREE
======================================================================
Testing satisfiability of: (p ∨ ¬p)

└── 1: (p ∨ ¬p)
    ├── 2: p [Branch 2✓] [by Disjunction (A∨B → A | B)]
    └── 3: ¬p [Branch 3✓] [by Disjunction (A∨B → A | B)]

======================================================================
Total branches: 2
Open branches: 2 [2, 3]
Closed branches: 0 
✓ SATISFIABLE - Formula has satisfying interpretation(s)
======================================================================

Tableau> mode
Current mode: Classical

Available modes:
  1. Classical Propositional Logic
  2. Weak Kleene Logic (WK3)

Select mode (1 or 2): 2
Switched to Weak Kleene Logic (WK3) mode.
Note: In WK3, atoms can have values t (true), f (false), or e (undefined).

Tableau> p & ~p
Parsed formula: (p ∧ ¬p)
Testing satisfiability...
----------------------------------------

RESULT: SATISFIABLE

Tableau> history
Formula History:
--------------------
 1. (p ∨ ¬p)
 2. (p ∧ ¬p)

Tableau> quit
Goodbye!
```

#### Command-Line Mode

Test formulas directly from the command line:

```bash
# Single formula (Classical Logic)
python cli.py "p -> q"
python cli.py "(p & q) -> (p | q)"
python cli.py "~(p & q) -> (~p | ~q)"

# Multiple formulas (comma-separated)
python cli.py "p -> q, q -> r, p, ~r"

# Weak Kleene Logic (WK3) mode
python cli.py --wk3 "p | ~p"     # Not a tautology in WK3!
python cli.py --wk3 "p & ~p"     # Not unsatisfiable in WK3!
```

Example output:
```bash
$ python cli.py "p & ~p"
Tableau System - Single Formula Mode
========================================

Parsed formula: (p ∧ ¬p)
Testing satisfiability...
----------------------------------------

RESULT: UNSATISFIABLE

======================================================================
SEMANTIC TABLEAU TREE
======================================================================
Testing satisfiability of: (p ∧ ¬p)

└── 1: (p ∧ ¬p)
    ├── 2: p [Branch 1✗] [by Conjunction (A∧B → A, B)]
    └── 3: ¬p [Branch 1✗] [by Conjunction (A∧B → A, B)]

======================================================================
Total branches: 1
Open branches: 0 
Closed branches: 1 [1]
✗ UNSATISFIABLE - All branches close
======================================================================
```

#### Syntax Reference

The CLI accepts formulas using either symbolic or ASCII notation:

| Logic Operator | Symbolic | ASCII | Example |
|---------------|----------|-------|---------|
| Negation | ¬ | ~ | `~p` or `¬p` |
| Conjunction | ∧ | & | `p & q` or `p ∧ q` |
| Disjunction | ∨ | \| | `p \| q` or `p ∨ q` |
| Implication | → | -> | `p -> q` or `p → q` |
| Parentheses | ( ) | ( ) | `(p & q) -> r` |

### Programmatic Usage

The system provides three programmatic interfaces:

1. **Legacy Interface** - Direct access to specific tableau implementations
2. **Componentized Interface** - Unified interface with pluggable logic systems
3. **Mode-Aware Interface** - Mode separation between propositional and first-order logic

#### 1. Legacy Interface (Original)

**Classical Logic:**
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

**Weak Kleene Logic (WK3):**
```python
from wk3_tableau import WK3Tableau
from wk3_model import WK3Model
from truth_value import TruthValue, t, f, e
from formula import Atom, Negation, Conjunction, Disjunction

# Create formulas
p, q = Atom("p"), Atom("q")
excluded_middle = Disjunction(p, Negation(p))  # p ∨ ¬p
contradiction = Conjunction(p, Negation(p))    # p ∧ ¬p

# Test satisfiability in WK3
wk3_tableau = WK3Tableau(excluded_middle)
is_satisfiable = wk3_tableau.build()
wk3_tableau.print_tree()

# Extract three-valued models
wk3_models = wk3_tableau.extract_all_models()
for model in wk3_models:
    p_val = model.get_value('p')
    formula_val = model.satisfies(excluded_middle)
    print(f"Model: p={p_val} → formula={formula_val}")

# Create specific three-valued models
model_t = WK3Model({'p': t, 'q': f})
model_e = WK3Model({'p': e, 'q': e})  # Both atoms undefined

# Evaluate formulas under different models
print(f"p ∧ ¬p with p=t: {model_t.satisfies(contradiction)}")  # f
print(f"p ∧ ¬p with p=e: {model_e.satisfies(contradiction)}")  # e

# Work with truth values directly
from truth_value import WeakKleeneOperators
result = WeakKleeneOperators.conjunction(t, e)  # t ∧ e = e
print(f"t ∧ e = {result}")
```

#### 2. Componentized Interface (New Architecture)

The componentized system provides a unified interface supporting multiple logic systems with pluggable rule sets.

**Basic Usage:**
```python
from componentized_tableau import ComponentizedTableau, classical_tableau, wk3_tableau
from formula import Atom, Conjunction, Negation

p = Atom("p")
formula = Conjunction(p, Negation(p))  # p ∧ ¬p

# Method 1: Direct logic-specific functions
classical_result = classical_tableau(formula)
wk3_result = wk3_tableau(formula)

print(f"Classical: {classical_result.build()}")  # False (unsatisfiable)
print(f"WK3: {wk3_result.build()}")             # True (satisfiable with p=e)

# Method 2: Specify logic system by name
tableau = ComponentizedTableau(formula, "classical")
result = tableau.build()
print(f"Result: {result}")

# Method 3: Use LogicSystem objects directly
from logic_system import get_logic_system

wk3_system = get_logic_system("wk3")
tableau = ComponentizedTableau(formula, wk3_system)
result = tableau.build()
```

**Advanced Features:**
```python
from logic_system import list_logic_systems, get_logic_system
from builtin_logics import describe_all_logics

# List available logic systems
systems = list_logic_systems()
print("Available logics:", systems)  # ['classical', 'wk3']

# Get detailed descriptions
descriptions = describe_all_logics()
for name, desc in descriptions.items():
    print(f"{name}: {desc}")

# Access system components
classical = get_logic_system("classical")
print(f"Rules: {classical.list_rules()}")
print(f"Truth values: {classical.config.truth_values}")

# Get detailed statistics
tableau = ComponentizedTableau(formula, "classical")
tableau.build()
stats = tableau.get_statistics()
print(f"Logic: {stats['logic_system']}")
print(f"Rules applied: {stats['rule_applications']}")
print(f"Branches: {stats['total_branches']}")
```

**Logic System Extension:**
```python
from logic_system import register_logic_system, LogicSystemConfig
from tableau_rules import TableauRule
from classical_components import create_classical_components

# Define custom logic system (example structure)
def create_custom_logic():
    config = LogicSystemConfig(
        name="My Custom Logic",
        truth_values=2,
        description="Custom logic with special rules"
    )
    
    # Define custom rules (implement TableauRule interface)
    custom_rules = [...]  # Your custom rule implementations
    
    # Use existing components or create new ones
    components = create_classical_components()  
    
    return LogicSystem(config, custom_rules, **components)

# Register the new logic
register_logic_system("custom", create_custom_logic)

# Use your custom logic
tableau = ComponentizedTableau(formula, "custom")
result = tableau.build()
```

#### 3. Mode-Aware Interface (Logic Mode Separation)

The mode-aware system enforces separation between propositional and first-order logic modes.

**Basic Mode-Aware Usage:**
```python
from mode_aware_tableau import propositional_tableau, first_order_tableau, auto_tableau
from mode_aware_parser import ModeAwareParser
from logic_mode import LogicMode

# Propositional mode
p, q = Atom("p"), Atom("q")
prop_formula = Conjunction(p, Negation(q))
prop_tableau = propositional_tableau(prop_formula)
print(f"Propositional result: {prop_tableau.build()}")

# First-order mode (with ground atoms only)
from formula import Predicate
from term import Constant

john = Constant("john")
student = Predicate("Student", [john])  # Student(john)
fol_tableau = first_order_tableau(student)
print(f"First-order result: {fol_tableau.build()}")

# Automatic mode detection
mixed_formula = Conjunction(p, student)  # This will be rejected
try:
    auto_tableau(mixed_formula)  # Error: mixed modes not allowed
except ModeError as e:
    print(f"Mode error: {e}")
```

**Programmatic API Builders:**
```python
from mode_aware_tableau import PropositionalBuilder, FirstOrderBuilder

# Propositional builder
p = PropositionalBuilder.atom("p")
q = PropositionalBuilder.atom("q")
prop_formula = PropositionalBuilder.conjunction(p, q)
prop_tableau = propositional_tableau(prop_formula)

# First-order builder  
student = FirstOrderBuilder.predicate("Student", "john")
smart = FirstOrderBuilder.predicate("Smart", "john")
fol_formula = FirstOrderBuilder.implication(student, smart)
fol_tableau = first_order_tableau(fol_formula)
```

#### Comparing Logic Systems

**Using Legacy Interface:**
```python
from tableau import Tableau
from wk3_tableau import WK3Tableau
from formula import Atom, Conjunction, Negation

# Test the same formula in both logics
p = Atom("p")
contradiction = Conjunction(p, Negation(p))  # p ∧ ¬p

# Classical logic
classical_tableau = Tableau(contradiction)
classical_result = classical_tableau.build()

# WK3 logic  
wk3_tableau = WK3Tableau(contradiction)
wk3_result = wk3_tableau.build()

print(f"Classical: p ∧ ¬p is {'SATISFIABLE' if classical_result else 'UNSATISFIABLE'}")
print(f"WK3:       p ∧ ¬p is {'SATISFIABLE' if wk3_result else 'UNSATISFIABLE'}")

# Show WK3 models
if wk3_result:
    wk3_models = wk3_tableau.extract_all_models()
    for model in wk3_models:
        p_val = model.get_value('p')
        print(f"  WK3 Model: p={p_val}")
```

**Using Componentized Interface:**
```python
from componentized_tableau import classical_tableau, wk3_tableau
from formula import Atom, Conjunction, Negation

p = Atom("p")
contradiction = Conjunction(p, Negation(p))  # p ∧ ¬p

# Compare results across logic systems
classical = classical_tableau(contradiction)
wk3 = wk3_tableau(contradiction)

classical_result = classical.build()
wk3_result = wk3.build()

print(f"Classical: {'SATISFIABLE' if classical_result else 'UNSATISFIABLE'}")
print(f"WK3:       {'SATISFIABLE' if wk3_result else 'UNSATISFIABLE'}")

# Get detailed statistics
classical_stats = classical.get_statistics()
wk3_stats = wk3.get_statistics()

print(f"Classical branches: {classical_stats['total_branches']}")
print(f"WK3 branches: {wk3_stats['total_branches']}")
```

#### Interface Comparison Table

| Feature | Legacy | Componentized | Mode-Aware |
|---------|--------|---------------|------------|
| **Classical Logic** | `Tableau(formula)` | `classical_tableau(formula)` | `propositional_tableau(formula)` |
| **WK3 Logic** | `WK3Tableau(formula)` | `wk3_tableau(formula)` | `propositional_tableau(formula)` |
| **Logic Selection** | Import specific class | String parameter or system object | Automatic mode detection |
| **Extensibility** | Add new tableau class | Register logic system | Add mode-specific rules |
| **Rule Access** | Hardcoded in class | `system.list_rules()` | Mode-specific validation |
| **Statistics** | Basic tree info | `get_statistics()` with details | Mode and logic info |
| **Mixed Modes** | Not supported | Logic-specific | Explicit prevention |

#### Key API Differences by Logic

| Feature | Classical | WK3 |
|---------|-----------|-----|
| **Truth Values** | `True`/`False` | `t`/`f`/`e` |
| **Model Creation** | `{'p': True}` | `{'p': t}` or `{'p': 'true'}` |
| **Formula Classes** | Same (`Atom`, `Negation`, etc.) | Same |
| **Model Evaluation** | `.satisfies()` returns `bool` | `.satisfies()` returns `TruthValue` |
| **Classical Check** | N/A | `.is_satisfying()` for bool result |
| **Tableau Class** | `Tableau` | `WK3Tableau` |
| **Model Class** | `Model` | `WK3Model` |

### Testing

The project includes comprehensive test coverage across all interfaces and logic systems.

#### Comprehensive Test Suite

```bash
# Run comprehensive test suite (42 tests covering all functionality)
python -m pytest test_comprehensive.py -v

# Run all tests (100+ total tests)
python -m pytest -v

# Individual test categories
python test_comprehensive.py   # Run by category with built-in functions
```

**Test Categories in Comprehensive Suite:**
- Classical Propositional Logic (14 tests) 
- Weak Kleene Logic (4 tests)
- First-Order Predicate Logic (4 tests)
- Mode-Aware System (5 tests)
- Componentized Rule System (5 tests)
- Performance & Optimizations (5 tests)
- Edge Cases & Regressions (5 tests)

#### Specialized Test Suites

```bash
# Legacy system tests
python -m pytest test_tableau.py -v         # Classical logic (50+ tests)
python -m pytest test_wk3.py -v            # Weak Kleene logic (25+ tests)

# System-specific tests
python -m pytest test_componentized_rules.py -v  # Componentized system (18 tests)
python -m pytest test_performance.py -v     # Performance tests (4 tests)
python -m pytest test_medium_optimizations.py -v  # Optimization tests (5 tests)

# Run tests by category
python -c "from test_comprehensive import run_classical_tests; run_classical_tests()"
python -c "from test_comprehensive import run_wk3_tests; run_wk3_tests()"
python -c "from test_comprehensive import run_componentized_tests; run_componentized_tests()"
```

#### System Demonstrations

```bash
# Logic system demonstrations
python tableau.py                           # Classical demonstration
python wk3_demo.py                          # WK3 demonstration
python demo_componentized.py               # Componentized system demo

# Command-line examples
python cli.py "p -> q"                      # Classical logic via CLI
python cli.py --wk3 "p & ~p"               # WK3 logic via CLI
```

## Architecture: Tableau Rules and Logic Systems

The system implements a componentized architecture supporting multiple logic systems with pluggable rule sets.

### Rule System Architecture

**Abstract Components:**
- `TableauRule` - Abstract base class for all tableau expansion rules
- `BranchInterface` - Protocol for logic-specific branch management 
- `LogicSystem` - Container combining rules with logic-specific components
- `ComponentizedTableau` - Unified tableau engine working with any logic system

**Extension Points:**
- Register new logic systems with `register_logic_system()`
- Implement `TableauRule` interface for custom expansion rules
- Create logic-specific components (branch management, closure detection, model extraction)
- Support for future logics: FOL quantifiers, modal logic, temporal logic, etc.

### Implemented Logic Systems

#### 1. Classical Propositional Logic (CPL)

**Tableau Rules (α and β rules):**
- **Double Negation Elimination**: `¬¬A` → `A` (α-rule, priority 1)
- **Conjunction Elimination**: `A ∧ B` → `A`, `B` (α-rule, priority 2) 
- **Negated Disjunction**: `¬(A ∨ B)` → `¬A`, `¬B` (α-rule, priority 2)
- **Negated Implication**: `¬(A → B)` → `A`, `¬B` (α-rule, priority 2)
- **Disjunction Elimination**: `A ∨ B` → `A | B` (β-rule, priority 3)
- **Negated Conjunction**: `¬(A ∧ B)` → `¬A | ¬B` (β-rule, priority 3)
- **Implication Elimination**: `A → B` → `¬A | B` (β-rule, priority 3)

**Components:**
- `ClassicalBranch` - Two-valued branch with boolean literal tracking
- `ClassicalClosureDetector` - O(1) contradiction detection (`A` and `¬A`)
- `ClassicalModelExtractor` - Boolean satisfying assignments
- `ClassicalSubsumptionDetector` - Branch subsumption elimination

#### 2. Weak Kleene Logic (WK3)

**Tableau Rules (three-valued semantics):**
- All classical rules adapted for three-valued logic
- **Atom Assignment Rules**: `A=t`, `A=f`, `A=e` (specialized WK3 expansion)
- **Three-valued closure**: Contradiction only when atom is both `t` and `f`

**Truth System:**
- **Three truth values**: `t` (true), `f` (false), `e` (undefined)
- **Conjunction**: False-preserving (`t∧e=e`, `f∧e=f`)
- **Disjunction**: True-preserving (`t∨e=t`, `f∨e=e`)
- **Negation**: `¬e = e` (undefined stays undefined)
- **Implication**: Standard WK3 semantics

**Components:**
- `WK3Branch` - Three-valued branch with `TruthValue` assignments
- `WK3ClosureDetector` - Three-valued contradiction detection  
- `WK3ModelExtractor` - Three-valued satisfying models
- `WK3SubsumptionDetector` - Three-valued branch subsumption

#### 3. Mode-Aware Logic Separation

**Propositional Mode:**
- Enforces pure propositional logic (atoms only)
- Rejects first-order constructs (`Student(john)`)
- Uses classical or WK3 tableau rules

**First-Order Mode:**
- Supports ground predicates (`Student(john)`, `Loves(john, mary)`)
- Rejects propositional atoms (`p`, `q`)
- Ground-only restriction (no quantifiers yet)

**Mixed Mode Prevention:**
- Automatic mode detection and validation
- Explicit error on mode mixing attempts
- Clean separation for future extensions

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

## Weak Kleene Logic (WK3) Support

The system supports both Classical Propositional Logic and Weak Kleene Logic:

### Key Differences in WK3:
- **Three truth values**: t (true), f (false), e (undefined)
- **Law of Excluded Middle not a tautology**: `p ∨ ¬p` can be `e` when `p = e`
- **Contradictions not always unsatisfiable**: `p ∧ ¬p` can be `e` when `p = e`
- **Partial information handling**: Useful for incomplete databases and partial knowledge

### Usage:
```bash
# Command line
python cli.py --wk3 "p | ~p"

# Interactive mode - use 'mode' command to switch
python cli.py
Tableau> mode
```

## Performance Features

This implementation includes tableau optimizations:

1. **Proper Termination**: No arbitrary iteration limits
2. **Formula Prioritization**: α-formulas expanded before β-formulas to minimize branching
3. **Subsumption Elimination**: Removes redundant branches automatically
4. **O(1) Closure Detection**: Fast contradiction detection using literal indexing
5. **Early Satisfiability Detection**: Terminates as soon as satisfying branch found
6. **Incremental Branch Representation**: Memory-efficient formula inheritance

## Output

The system provides output including:

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