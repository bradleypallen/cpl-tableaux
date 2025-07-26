# Architecture Documentation: Tableau System

**Version**: 2.0 (Plugin Architecture)  
**Last Updated**: January 2025  
**License**: MIT  

## Table of Contents

1. [Overview](#overview)
2. [Design Philosophy](#design-philosophy)
3. [System Architecture](#system-architecture)
4. [Core Framework](#core-framework)
5. [Plugin System](#plugin-system)
6. [Data Flow](#data-flow)
7. [Performance Architecture](#performance-architecture)
8. [Extension Points](#extension-points)
9. [Implementation Assessment](#implementation-assessment)

## Overview

This document describes the architecture of a plugin-based tableau system for automated theorem proving. The system implements semantic tableau methods through a unified framework that supports multiple logic systems via a plugin architecture.

### Supported Logic Systems

- **Classical Logic**: Two-valued propositional logic (T, F)
- **Weak Kleene Logic**: Three-valued logic with undefined values (T, F, U)
- **wKrQ Logic**: Four-valued epistemic logic (T, F, M, N)
- **FDE Logic**: Four-valued paraconsistent logic (T, F, B, N)
- **Extensible**: Easy addition of new logic systems

### Key Architectural Principles

1. **Plugin Architecture**: All logic systems are plugins with no hardcoded logic
2. **Unified Engine**: Single tableau engine supports all logic systems
3. **Self-Contained Logic Definitions**: Each logic contains both syntax and tableau rules
4. **Clean API**: Modern Python interface with natural formula construction
5. **Research Quality**: Theoretical correctness with industrial performance

## Design Philosophy

### Philosophical Logician Perspective

The architecture is designed from the perspective of philosophical logicians who think of logic systems as unified wholes. When defining Łukasiewicz logic, you don't separate syntax from proof theory - you define a complete logical system.

**Core Insight**: A logic system **is** defined by its syntax and tableau rules together. The architecture reflects this conceptual unity.

### Software Engineering Excellence

While maintaining theoretical rigor, the system incorporates industrial-grade software engineering:

- **Modular Design**: Clean separation of concerns
- **Performance Optimization**: O(1) operations for critical paths
- **Type Safety**: Strong typing throughout the system
- **Comprehensive Testing**: Systematic validation of correctness
- **Extensibility**: Clean extension points for new logic systems

## System Architecture

### High-Level Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                        TABLEAU SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│  User Interface Layer                                           │
│  • Modern Python API (LogicSystem, LogicFormula, etc.)         │
│  • Extensible CLI with --logic parameter                       │
│  • Parser Integration with -> syntax                           │
├─────────────────────────────────────────────────────────────────┤
│  Logic Plugin Layer                                             │
│  • Classical Logic Plugin (syntax + rules)                     │
│  • Weak Kleene Logic Plugin (syntax + rules)                   │
│  • wKrQ Logic Plugin (syntax + rules)                          │
│  • FDE Logic Plugin (syntax + rules)                           │
│  • Plugin Registry and Discovery System                        │
├─────────────────────────────────────────────────────────────────┤
│  Core Framework Layer                                           │
│  • Tableau Engine (optimized construction)                     │
│  • Rule DSL (declarative rule specification)                   │
│  • Formula System (extensible connectives)                     │
│  • Semantic Systems (truth values and operations)              │
│  • Sign Systems (tableau signs)                                │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
src/tableaux/
├── core/                    # Core framework infrastructure
│   ├── formula.py          # Extensible formula representation
│   ├── semantics.py        # Truth value systems
│   ├── signs.py            # Sign systems for tableau construction
│   ├── tableau_engine.py   # Optimized tableau construction engine
│   ├── rule_engine.py      # Rule application and tableau logic
│   ├── rules.py            # Declarative rule specification DSL
│   └── syntax.py           # Syntactic operations
├── logics/                  # Self-contained logic system plugins
│   ├── logic_system.py     # Plugin architecture and registry
│   ├── classical.py        # Classical logic (complete definition)
│   ├── weak_kleene.py      # Weak Kleene logic (complete definition)
│   ├── wkrq.py             # wKrQ logic (complete definition)
│   └── fde.py              # FDE logic (complete definition)
├── api.py                   # Modern Python API
├── parser.py                # Extensible formula parser
└── extensible_cli.py        # Plugin-aware command-line interface
```

## Core Framework

### Formula System (`core/formula.py`)

Provides extensible formula representation supporting any connective system:

```python
class ConnectiveSpec:
    """Specification for a logical connective."""
    def __init__(self, symbol: str, arity: int, precedence: int, 
                 associativity: str, notation: str):
        self.symbol = symbol          # "&", "|", "->", etc.
        self.arity = arity           # Number of arguments
        self.precedence = precedence # For parsing (higher = binds tighter)
        self.associativity = associativity  # "left", "right", "none"
        self.notation = notation     # "infix", "prefix", "postfix"
```

**Key Features**:
- Supports arbitrary connectives with custom precedence
- Abstract syntax tree representation
- Efficient equality and hashing for tableau operations
- Extensible for first-order constructs (predicates, quantifiers)

### Semantic Systems (`core/semantics.py`)

Defines truth value systems and semantic operations:

```python
class TruthValueSystem(ABC):
    """Abstract base for truth value systems."""
    
    @abstractmethod
    def truth_values(self) -> Set[TruthValue]:
        """All truth values in this system."""
        pass
    
    @abstractmethod
    def designated_values(self) -> Set[TruthValue]:
        """Truth values that count as 'true'."""
        pass
    
    @abstractmethod
    def evaluate_negation(self, value: TruthValue) -> TruthValue:
        """Semantic operation for negation."""
        pass
```

**Implementations**:
- `ClassicalTruthValueSystem`: Two-valued (T, F)
- `WeakKleeneTruthValueSystem`: Three-valued (T, F, U)
- `FourValuedTruthSystem`: Four-valued base for wKrQ and FDE
- Extensible for new multi-valued systems

### Sign Systems (`core/signs.py`)

Defines tableau signs for different logic systems:

```python
class Sign(ABC):
    """Abstract base for tableau signs."""
    
    @abstractmethod
    def get_symbol(self) -> str:
        """String representation of this sign."""
        pass
    
    @abstractmethod
    def is_contradictory_with(self, other: 'Sign') -> bool:
        """Whether this sign contradicts another."""
        pass
```

**Key Features**:
- Logic-specific sign systems (T/F, T/F/U, T/F/M/N, etc.)
- Contradiction detection for tableau closure
- Extensible for modal, temporal, and other specialized signs

### Tableau Engine (`core/tableau_engine.py`)

Optimized tableau construction engine with industrial-grade performance:

```python
class TableauEngine:
    """Core tableau construction engine."""
    
    def construct_tableau(self, initial_formulas: List[SignedFormula], 
                         logic_system: LogicSystem) -> Tableau:
        """Construct tableau with optimizations."""
        # α/β rule prioritization
        # O(1) closure detection
        # Subsumption elimination
        # Early termination
```

**Optimizations**:
- **O(1) Closure Detection**: Hash-based formula tracking
- **α/β Rule Prioritization**: Non-branching rules before branching
- **Subsumption Elimination**: Remove redundant branches
- **Early Termination**: Stop on satisfiability determination

### Rule System (`core/rules.py`)

Declarative DSL for specifying tableau rules:

```python
class TableauRule:
    """Declarative tableau rule specification."""
    
    def __init__(self, name: str, rule_type: RuleType,
                 premises: List[RulePattern], 
                 conclusions: List[List[str]]):
        self.name = name              # "T-Conjunction", "F-Disjunction"
        self.rule_type = rule_type    # ALPHA (non-branching) or BETA (branching)
        self.premises = premises      # What formulas this rule applies to
        self.conclusions = conclusions # What formulas are added
```

**Features**:
- Pattern matching for rule application
- Type system (α-rules vs β-rules) for optimization
- Priority system for rule ordering
- Logic-agnostic rule specification

## Plugin System

### Logic System Architecture

Each logic system is completely self-contained, defining both syntax and tableau rules:

```python
class LogicSystem(ABC):
    """Base class for all logic systems."""
    
    @abstractmethod 
    def initialize(self):
        """Initialize the logic system."""
        # 1. Define connectives and syntax
        self.add_connective(ConnectiveSpec(...))
        
        # 2. Set semantic systems
        self.set_truth_system(MyTruthSystem())
        self.set_sign_system(MySignSystem())
        
        # 3. Add tableau rules
        self._add_tableau_rules()
```

### Plugin Registration

```python
class LogicRegistry:
    """Central registry for logic systems."""
    
    @classmethod
    def register(cls, logic_system: LogicSystem):
        """Register a new logic system."""
        cls._systems[logic_system.name] = logic_system
    
    @classmethod 
    def get(cls, name: str) -> LogicSystem:
        """Retrieve a registered logic system."""
        return cls._systems.get(name)
    
    @classmethod
    def list_systems(cls) -> List[str]:
        """List all available logic systems."""
        return list(cls._systems.keys())
```

### Example: Classical Logic Plugin

```python
class ClassicalLogic(LogicSystem):
    """Complete classical logic definition."""
    
    def initialize(self):
        # Define syntax
        self.add_connective(ConnectiveSpec("&", 2, 3, "left", "infix"))
        self.add_connective(ConnectiveSpec("|", 2, 2, "left", "infix"))
        self.add_connective(ConnectiveSpec("~", 1, 4, "none", "prefix"))
        self.add_connective(ConnectiveSpec("->", 2, 1, "right", "infix"))
        
        # Set semantics
        self.set_truth_system(ClassicalTruthValueSystem())
        self.set_sign_system(ClassicalSignSystem())
        
        # Define tableau rules
        self._add_classical_rules()
    
    def _add_classical_rules(self):
        # T-Conjunction rule
        self.add_rule(TableauRule(
            name="T-Conjunction",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "A & B")],
            conclusions=[["T:A", "T:B"]]
        ))
        # ... all other classical rules
```

**Key Benefits**:
- **Conceptual Unity**: Everything about classical logic in one place
- **Self-Contained**: No external dependencies on other files
- **Maintainable**: Easy to modify or extend classical logic
- **Discoverable**: Automatic CLI and API integration

## Data Flow

### Formula Construction Flow

```
User Input → Parser → Formula AST → LogicFormula Wrapper → Operations
     ↓
"p -> q" → parse() → CompoundFormula(->,[Atom(p),Atom(q)]) → LogicFormula → solve()
```

### Tableau Construction Flow

```
LogicFormula → SignedFormula → TableauEngine → Rule Application → Result
     ↓              ↓              ↓               ↓            ↓
  p.implies(q)  → T:(p->q)  → Engine Init → Apply Rules → Models/UNSAT
```

### Plugin Discovery Flow

```
CLI/API Request → LogicRegistry → Plugin Instance → Method Dispatch
     ↓               ↓               ↓                ↓
--logic=fde → LogicRegistry.get("fde") → FDELogic() → solve()
```

## Performance Architecture

### Critical Path Optimizations

1. **O(1) Closure Detection**:
   ```python
   class ClosureDetector:
       def __init__(self):
           self.formula_index = {}  # Hash-based lookup
       
       def is_closed(self, branch) -> bool:
           # O(1) contradiction check using hash index
   ```

2. **α/β Rule Prioritization**:
   ```python
   def get_applicable_rules(self, branch) -> List[TableauRule]:
       alpha_rules = [r for r in rules if r.rule_type == RuleType.ALPHA]
       beta_rules = [r for r in rules if r.rule_type == RuleType.BETA]
       return alpha_rules + beta_rules  # α-rules first
   ```

3. **Subsumption Elimination**:
   - Remove branches that are supersets of other branches
   - Early termination when satisfiability is determined

### Memory Architecture

- **Shallow Copying**: Branches share formula objects via references
- **Hash Consing**: Common subformulas are shared
- **Lazy Evaluation**: Models computed only when needed

### Complexity Analysis

- **Time Complexity**: O(n log n) best case, O(2ⁿ) worst case (inherent to tableau method)
- **Space Complexity**: O(b × f) where b = branches, f = formulas per branch
- **Closure Detection**: O(1) with hash-based formula tracking
- **Rule Selection**: O(log n) with priority-based ordering

## Extension Points

### Adding New Logic Systems

1. **Create Logic Class**:
   ```python
   class MyLogic(LogicSystem):
       def initialize(self):
           # Define complete logic system
   ```

2. **Register System**:
   ```python
   LogicRegistry.register(MyLogic("my_logic"))
   ```

3. **Immediate Availability**:
   - CLI: `tableaux --logic=my_logic "formula"`
   - API: `LogicSystem(LogicRegistry.get("my_logic"))`

### Adding New Connectives

```python
# In logic system initialization
self.add_connective(ConnectiveSpec("⊕", 2, 2, "left", "infix"))  # XOR

# Add corresponding semantic operation
def evaluate_xor(self, left: TruthValue, right: TruthValue) -> TruthValue:
    # Define XOR semantics

# Add tableau rules
self.add_rule(TableauRule(
    name="T-XOR",
    rule_type=RuleType.BETA,
    premises=[RulePattern("T", "A ⊕ B")],
    conclusions=[["T:A", "F:B"], ["F:A", "T:B"]]
))
```

### Adding New Truth Value Systems

```python
class LukasiewiczTruthSystem(TruthValueSystem):
    def __init__(self):
        self.true = LukasiewiczTruthValue("T", 1.0)
        self.half = LukasiewiczTruthValue("H", 0.5)
        self.false = LukasiewiczTruthValue("F", 0.0)
    
    def evaluate_conjunction(self, left, right):
        # min(left.value, right.value)
        return self._value_to_truth_value(min(left.value, right.value))
```

## Implementation Assessment

### Strengths

1. **Architectural Clarity**: Clean separation between core framework and logic plugins
2. **Conceptual Unity**: Logic systems are self-contained and natural to define
3. **Performance**: Industrial-grade optimizations with proper complexity analysis
4. **Extensibility**: Easy to add new logic systems without modifying core code
5. **Consistency**: Same API works across all logic systems
6. **Research Quality**: Maintains theoretical soundness with practical usability

### Design Decisions

1. **Plugin Architecture vs Monolithic**: Chose plugins for extensibility and maintainability
2. **Unified Rules in Logic Files**: Eliminated separate rules directory for conceptual unity
3. **Modern API**: Clean Python interface over complex procedural API
4. **Hash-Based Optimization**: O(1) operations for critical tableau construction paths
5. **Declarative Rules**: DSL for rule specification rather than procedural code

### Trade-offs

1. **Memory vs Speed**: Uses more memory for hash indexing to achieve O(1) operations
2. **Abstraction vs Performance**: Clean abstractions maintained while preserving performance
3. **Flexibility vs Complexity**: Plugin system adds some complexity but enables extensibility
4. **Type Safety vs Dynamism**: Strong typing throughout while maintaining plugin flexibility

### Validation

The architecture has been validated through:

- **Comprehensive Testing**: 36+ tests across all logic systems
- **Literature Compliance**: Examples from Priest, Fitting, Smullyan validate correctness
- **Performance Benchmarks**: Sub-second execution for complex formulas
- **Extension Testing**: FDE logic demonstrates clean extensibility
- **API Usability**: Natural formula construction and result handling

## Future Directions

### Planned Extensions

1. **Modal Logic Support**: Temporal and epistemic modal systems
2. **First-Order Logic**: Full predicate logic with quantifiers
3. **Proof Extraction**: Generate natural deduction proofs from tableaux
4. **Parallel Construction**: Multi-threaded tableau construction
5. **Interactive Debugging**: Step-through tableau construction

### Research Applications

The architecture supports research in:

- **Non-Classical Logic Investigation**: Easy prototyping of new systems
- **Tableau Method Optimization**: Platform for testing new algorithms
- **Logic System Comparison**: Systematic analysis across multiple systems
- **Educational Applications**: Clean visualization of tableau construction

## Conclusion

The plugin architecture successfully combines:

- **Theoretical Rigor**: Correct implementation of multiple logic systems
- **Software Engineering Excellence**: Clean, maintainable, performant code
- **Research Utility**: Easy extension and systematic comparison
- **Educational Value**: Clear visualization and natural API

The system demonstrates that semantic tableau methods can be implemented with both theoretical correctness and industrial-grade engineering, providing a solid foundation for automated reasoning research and education.

The key insight - treating logic systems as unified wholes rather than fragmented components - leads to a more natural and maintainable architecture that better serves both researchers and practitioners in automated reasoning.