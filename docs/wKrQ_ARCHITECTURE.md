# wKrQ Architecture: Three-Valued Weak Kleene Logic System

**Version**: 2.0  
**Last Updated**: July 2025  
**License**: MIT  

## Table of Contents

1. [Overview](#overview)
2. [Theoretical Foundation](#theoretical-foundation)
3. [System Architecture](#system-architecture)
4. [Core Components](#core-components)
5. [Tableau Engine](#tableau-engine)
6. [Semantic System](#semantic-system)
7. [Performance Optimizations](#performance-optimizations)
8. [Extension Points](#extension-points)
9. [Testing Architecture](#testing-architecture)
10. [Future Directions](#future-directions)

## Overview

The wKrQ (weak Kleene logic with restricted quantification) system is a research-grade implementation of three-valued logic with industrial performance characteristics. It combines theoretical rigor with practical efficiency, making it suitable for both academic research and real-world automated reasoning applications.

### Design Principles

1. **Theoretical Correctness**: All tableau rules implement exact semantic conditions for weak Kleene logic
2. **Industrial Performance**: Sub-millisecond response times with optimized data structures and algorithms
3. **Extensibility**: Clean separation between core engine and logic-specific components
4. **Research Quality**: Comprehensive testing and validation against literature results
5. **Usability**: Both programmatic API and command-line interfaces for different use cases

### Key Innovations

- **Weak Kleene Semantics**: Correct implementation where any undefined input produces undefined output
- **Four-Sign Tableau System**: T, F, M, N signs enable proof construction in three-valued logic
- **Restricted Quantification**: Domain-limited quantifiers for practical first-order reasoning
- **Industrial Optimizations**: O(1) contradiction detection, alpha/beta rule prioritization, intelligent branch selection
- **Comprehensive Testing**: 79 tests covering correctness, performance, and literature validation

## Theoretical Foundation

### Three-Valued Logic

wKrQ implements **weak Kleene** three-valued logic with truth values:

- **t (true)**: Classical truth value
- **f (false)**: Classical falsity value  
- **e (undefined)**: Neither true nor false

#### Weak Kleene Truth Tables

The defining characteristic of weak Kleene logic is that **any operation involving undefined produces undefined**:

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

This differs from **strong Kleene** logic where, for example, `t ∨ e = t`. In weak Kleene, `t ∨ e = e`.

### Tableau Signs

The tableau system uses four signs to construct proofs:

- **T**: Formula must have truth value **t**
- **F**: Formula must have truth value **f**
- **M**: Formula can have truth value **t or f** (multiple possibilities)
- **N**: Formula must have truth value **e** (neither/undefined)

#### Sign Truth Conditions

```python
T.truth_conditions() = {t}        # Must be true
F.truth_conditions() = {f}        # Must be false
M.truth_conditions() = {t, f}     # Can be true or false
N.truth_conditions() = {e}        # Must be undefined
```

### Restricted Quantification

wKrq supports restricted quantifiers that limit the domain of quantification:

- **[∃X P(X)]Q(X)**: "There exists an X such that P(X) and Q(X)"
- **[∀X P(X)]Q(X)**: "For all X, if P(X) then Q(X)"

This provides more natural first-order reasoning than unrestricted quantification.

## System Architecture

### High-Level Structure

```
wKrQ System
├── Core Logic Engine
│   ├── Formula Representation
│   ├── Semantic System  
│   ├── Sign System
│   └── Tableau Engine
├── Interfaces
│   ├── Python API
│   ├── Command Line Interface
│   └── Interactive Mode
├── Performance Layer
│   ├── Optimization Engine
│   ├── Caching System
│   └── Performance Monitoring
└── Testing Framework
    ├── Correctness Tests
    ├── Performance Tests
    └── Literature Validation
```

### Module Organization

```
src/wkrq/
├── __init__.py           # Public API exports
├── api.py               # High-level convenience API  
├── cli.py              # Command-line interface
├── formula.py          # Formula representation classes
├── semantics.py        # Three-valued semantic system
├── signs.py           # Tableau sign system
├── tableau.py         # Core tableau construction engine
└── parser.py          # Formula parsing from strings
```

### Data Flow

```
Input Formula (String or Python objects)
    ↓
Formula Parser/Constructor
    ↓
Signed Formula (Formula + Sign)
    ↓
Tableau Engine
    ↓
Rule Application + Optimization
    ↓
Result (Satisfiability + Models + Statistics)
```

## Core Components

### Formula Hierarchy

```python
Formula (Abstract Base)
├── PropositionalAtom           # p, q, r
├── CompoundFormula            # p & q, p | q, ~p, p -> q
├── PredicateFormula           # P(x), R(x,y)
├── RestrictedExistentialFormula    # [∃X P(X)]Q(X)
└── RestrictedUniversalFormula      # [∀X P(X)]Q(X)

Term (Abstract Base)
├── Variable                   # X, Y, Z
└── Constant                   # a, b, c
```

#### Formula Operations

All formulas support:
- **Structural operations**: `get_atoms()`, `complexity()`, `is_atomic()`
- **Operator overloading**: `p & q`, `p | q`, `~p`, `p.implies(q)`
- **Substitution**: `substitute()`, `substitute_term()`
- **Equality and hashing**: For use in sets and dictionaries

### Semantic System

```python
class WeakKleeneSemantics:
    """Three-valued weak Kleene semantic system."""
    
    truth_values = {TRUE, FALSE, UNDEFINED}
    designated_values = {TRUE}
    
    def conjunction(self, a: TruthValue, b: TruthValue) -> TruthValue
    def disjunction(self, a: TruthValue, b: TruthValue) -> TruthValue
    def negation(self, a: TruthValue) -> TruthValue
    def implication(self, a: TruthValue, b: TruthValue) -> TruthValue
```

The semantic system implements truth tables as lookup dictionaries for O(1) evaluation.

### Sign System

```python
class Sign:
    """Base class for tableau signs."""
    
    def truth_conditions(self) -> Set[TruthValue]
    def is_contradictory_with(self, other: 'Sign') -> bool
    def is_satisfiable_with(self, truth_value: TruthValue) -> bool

# Sign instances
T = TrueSign()      # Must be true
F = FalseSign()     # Must be false  
M = MultipleSign()  # Can be true or false
N = NeitherSign()   # Must be undefined
```

## Tableau Engine

### Core Algorithm

The tableau engine implements a systematic proof search with industrial-grade optimizations:

```python
class Tableau:
    """Industrial-grade optimized tableau for wKrQ logic."""
    
    def __init__(self, initial_formulas: List[SignedFormula])
    def construct(self) -> TableauResult
    def apply_rule(self, node: TableauNode, branch: Branch, rule: RuleInfo)
    def is_complete(self) -> bool
```

### Rule Types

#### Alpha Rules (Non-branching, High Priority)
- **T-Conjunction**: `T: p ∧ q → T: p, T: q`
- **F-Disjunction**: `F: p ∨ q → F: p, F: q`
- **T-Negation**: `T: ~p → F: p`
- **F-Negation**: `F: ~p → T: p`
- **F-Implication**: `F: p → q → T: p, F: q`

#### Beta Rules (Branching, Lower Priority)
- **F-Conjunction**: `F: p ∧ q → {F: p} | {F: q}`
- **T-Disjunction**: `T: p ∨ q → {T: p} | {T: q}`  
- **T-Implication**: `T: p → q → {F: p} | {T: q}`

#### First-Order Rules
- **T-RestrictedExists**: `T: [∃X P(X)]Q(X) → T: P(c), T: Q(c)` (for fresh constant c)
- **F-RestrictedExists**: `F: [∃X P(X)]Q(X) → {F: P(c)} | {F: Q(c)}`
- **T-RestrictedForall**: `T: [∀X P(X)]Q(X) → {F: P(c)} | {T: Q(c)}`  
- **F-RestrictedForall**: `F: [∀X P(X)]Q(X) → T: P(c), F: Q(c)`

### Data Structures

#### Optimized Branch Representation

```python
@dataclass
class Branch:
    """A branch with industrial-grade optimizations."""
    
    # Core data
    nodes: List[TableauNode]
    formulas: Set[SignedFormula]
    is_closed: bool
    
    # O(1) lookup optimization
    formula_index: Dict[Sign, Dict[Formula, Set[int]]]
    
    # Constraint propagation
    unit_literals: Set[SignedFormula]
    implications: List[Tuple[SignedFormula, SignedFormula]]
    
    # Performance metrics
    complexity_score: int
    branching_factor: int
```

#### Node Structure

```python
@dataclass
class TableauNode:
    """A node in the tableau tree."""
    
    id: int
    formula: SignedFormula
    parent: Optional['TableauNode']
    children: List['TableauNode']
    rule_applied: Optional[str]
    is_closed: bool
    depth: int
```

## Performance Optimizations

### O(1) Contradiction Detection

Uses hash-based indexing for immediate contradiction detection:

```python
def _check_contradiction(self, new_formula: SignedFormula) -> bool:
    """Check if new formula contradicts existing formulas."""
    if new_formula.sign == T:
        return len(self.formula_index[F][new_formula.formula]) > 0
    elif new_formula.sign == F:
        return len(self.formula_index[T][new_formula.formula]) > 0
    return False
```

### Alpha/Beta Rule Prioritization

Non-branching rules (alpha) are always processed before branching rules (beta):

```python
class RuleInfo:
    def __lt__(self, other):
        # Alpha rules always come first
        if self.rule_type == RuleType.ALPHA and other.rule_type != RuleType.ALPHA:
            return True
        # Then by explicit priority
        if self.priority != other.priority:
            return self.priority < other.priority
        # Finally by complexity cost
        return self.complexity_cost < other.complexity_cost
```

### Intelligent Branch Selection

Branches are selected using the "least complex first" strategy:

```python
def _select_optimal_branch(self) -> Optional[Branch]:
    if self.branch_selection_strategy == "least_complex":
        return min(self.open_branches, key=lambda b: b.complexity_score)
```

### Early Termination

For satisfiability testing, the tableau stops at the first satisfying model:

```python
if self.early_termination and len(self.open_branches) > 0:
    for branch in self.open_branches:
        if all(node.formula.formula.is_atomic() for node in branch.nodes):
            break  # Found satisfying assignment
```

### Subsumption Elimination

Redundant formulas are identified and eliminated:

```python
def _is_subsumed(self, signed_formula: SignedFormula) -> bool:
    """Check if formula is subsumed by existing formulas."""
    return signed_formula in self.subsumed_formulas or signed_formula in self.formulas
```

### Performance Metrics

The system tracks detailed performance statistics:

```python
@dataclass
class TableauResult:
    satisfiable: bool
    models: List[Model]
    closed_branches: int
    open_branches: int
    total_nodes: int
    tableau: Optional[Tableau]
```

## Extension Points

### Adding New Connectives

To add a new logical connective:

1. **Extend Formula Classes**:
```python
class BiconditionalFormula(CompoundFormula):
    def __init__(self, left: Formula, right: Formula):
        super().__init__("<->", [left, right])
```

2. **Define Semantic Operations**:
```python
def biconditional(self, a: TruthValue, b: TruthValue) -> TruthValue:
    """Weak Kleene biconditional."""
    if a == UNDEFINED or b == UNDEFINED:
        return UNDEFINED
    return TRUE if a == b else FALSE
```

3. **Add Tableau Rules**:
```python
# T-Biconditional: T: p <-> q → {T: p, T: q} | {F: p, F: q}
if connective == "<->" and sign == T:
    conclusions = [
        [SignedFormula(T, left), SignedFormula(T, right)],
        [SignedFormula(F, left), SignedFormula(F, right)]
    ]
    return RuleInfo("T-Biconditional", RuleType.BETA, 15, 4, conclusions)
```

### Adding New Logic Systems

The architecture supports extending to other many-valued logics:

1. **Create New Semantic System**:
```python
class StrongKleeneSemantics(ThreeValuedSemantics):
    def disjunction(self, a: TruthValue, b: TruthValue) -> TruthValue:
        # Strong Kleene: t ∨ e = t (unlike weak Kleene)
        if a == TRUE or b == TRUE:
            return TRUE
        if a == UNDEFINED or b == UNDEFINED:
            return UNDEFINED
        return FALSE
```

2. **Modify Tableau Rules**: Adjust rules to match new semantics
3. **Update Tests**: Add test cases for new logic system

### Performance Extensions

The optimization framework supports adding new strategies:

```python
# Custom branch selection strategy
def _select_highest_priority_branch(self) -> Optional[Branch]:
    """Select branch with highest priority formulas."""
    return max(self.open_branches, key=lambda b: self._calculate_priority(b))

# Custom subsumption detection
def _advanced_subsumption(self, general: Formula, specific: Formula) -> bool:
    """Advanced subsumption checking."""
    # Implement domain-specific subsumption logic
    pass
```

## Testing Architecture

### Test Categories

1. **Unit Tests**: Individual component functionality
2. **Integration Tests**: Component interaction
3. **Correctness Tests**: Semantic and proof-theoretic correctness  
4. **Performance Tests**: Speed and memory benchmarks
5. **Literature Tests**: Validation against published results
6. **Regression Tests**: Prevent performance degradation

### Test Structure

```
tests/wkrq/
├── test_wkrq_basic.py           # Core functionality (25 tests)
├── test_first_order.py          # First-order features (12 tests)
├── test_literature_cases.py     # Literature validation (34 tests)
└── test_performance_regression.py  # Performance benchmarks (8 tests)
```

### Continuous Validation

All tests run automatically to ensure:
- **Semantic Correctness**: Truth tables match weak Kleene specifications
- **Tableau Soundness**: All tableau rules are semantically valid
- **Performance Benchmarks**: No regression below acceptable thresholds
- **Literature Compliance**: Results match published examples

## Future Directions

### Theoretical Extensions

1. **Additional Many-Valued Logics**: Strong Kleene, Łukasiewicz, Belnap four-valued logic
2. **Modal Extensions**: Necessity and possibility operators  
3. **Temporal Logic**: Linear and branching time operators
4. **Epistemic Logic**: Knowledge and belief operators

### Performance Improvements

1. **Parallel Tableau Construction**: Multi-threaded branch processing
2. **Advanced Caching**: Memoization of subformula results
3. **Incremental Solving**: Reuse previous results for modified formulas
4. **GPU Acceleration**: Parallel rule application on graphics hardware

### Interface Enhancements

1. **Web Interface**: Browser-based formula testing and visualization
2. **IDE Integration**: Plugins for popular development environments
3. **Visualization Tools**: Interactive tableau tree display
4. **Batch Processing**: High-throughput formula validation

### Research Applications

1. **Automated Theorem Proving**: Integration with larger proof systems
2. **AI Reasoning**: Uncertainty handling in knowledge representation
3. **Database Systems**: Three-valued logic for incomplete information
4. **Philosophical Logic**: Tool for philosophical argument analysis

---

This architecture provides a solid foundation for three-valued logic research while maintaining industrial-grade performance and extensibility. The clean separation of concerns allows for both theoretical exploration and practical application development.