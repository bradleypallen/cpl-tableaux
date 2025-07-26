# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository is a **research platform for semantic tableau systems supporting non-classical logics**, implemented in Python with a focus on **theoretical correctness and computational efficiency**. The project brings together the best practices from both industrial automated reasoning systems and academic research in non-classical logic semantics.

**Primary Research Goal**: To support rigorous investigation of tableau-based proof methods for non-classical logics, including but not limited to many-valued logics, modal logics, temporal logics, and paraconsistent logics. The implementation prioritizes semantic accuracy, algorithmic efficiency, and extensibility to enable systematic comparison and analysis of different logical systems.

**Core Philosophy**: Combine the **theoretical rigor** expected in automated reasoning research with the **software engineering excellence** found in production theorem proving systems. Every logical system implementation must be demonstrably sound and complete (where applicable), while maintaining industrial-grade performance characteristics and code quality.

**License**: MIT License - This project is open source and freely available for use, modification, and distribution under the MIT License.

## Modern Plugin Architecture

The system has been redesigned with a **modular plugin architecture** that separates core tableau functionality from logic-specific implementations, enabling easy extension with new logic systems.

### Core Framework Components

#### Core Framework (`src/tableaux/core/`)
- `formula.py` - Abstract formula representation with extensible connective system
- `semantics.py` - Truth value systems and semantic operations  
- `signs.py` - Sign systems for different logic systems (T/F, T/F/U, T/F/M/N, etc.)
- `tableau_engine.py` - Optimized tableau construction engine with industrial-grade performance
- `rule_engine.py` - Rule application and tableau construction logic
- `rules.py` - Declarative rule specification DSL for tableau rules
- `syntax.py` - Syntactic operations and formula manipulation

#### Logic System Plugins (`src/tableaux/logics/`)
- `logic_system.py` - Plugin architecture and registry system
- `classical.py` - Complete classical propositional logic definition (syntax + tableau rules)
- `weak_kleene.py` - Complete three-valued weak Kleene logic definition (syntax + tableau rules)
- `wkrq.py` - Complete four-valued wKrQ epistemic logic definition (syntax + tableau rules)
- `fde.py` - Complete First-Degree Entailment logic definition (syntax + tableau rules)

#### Modern API (`src/tableaux/`)
- `api.py` - Clean, modern Python API with natural syntax
- `parser.py` - Extensible formula parser supporting all logic systems
- `extensible_cli.py` - Command-line interface with `--logic` parameter

### Core Framework Features

- **Theoretical Soundness**: All tableau rules implement correct logical semantics
- **Complete Termination**: No arbitrary limits that compromise logical completeness
- **Industrial Performance**: O(1) closure detection, α/β rule prioritization, subsumption elimination
- **Multi-Logic Support**: Unified engine supports any number of logic systems
- **Enhanced Visualization**: Step-by-step construction with rule names and tree structure

### Supported Logic Systems

The framework currently includes these logic systems as plugins:

- **Classical Logic** (`classical`): Two-valued semantics (T/F signs)
- **Weak Kleene Logic** (`weak_kleene`): Three-valued semantics (T/F/U signs)
- **wKrQ Epistemic Logic** (`wkrq`): Four-valued Ferguson system (T/F/M/N signs)
- **First-Degree Entailment** (`fde`): Four-valued paraconsistent/paracomplete logic (T/F/B/N signs)

## Development Commands

This is a research-grade Python project with modular plugin architecture and comprehensive testing.

### Main Usage Patterns

```bash
# Modern extensible CLI (classical logic is default)
tableaux "p | ~p"                    # Classical logic
tableaux --logic=weak_kleene "p & ~p"    # Three-valued logic
tableaux --logic=fde "p & ~p"            # Paraconsistent logic
tableaux --logic=wkrq --sign=M "p"       # Epistemic logic with M sign
tableaux --list-logics                   # Show all available systems

# Interactive mode with logic switching
tableaux                             # Interactive mode
# Commands: logic fde, test p & ~p, models p | q, help, quit

# Advanced features
tableaux --models --stats --debug "complex_formula"
tableaux --format=json --logic=fde "p & ~p"
```

### Programmatic API

```python
# Modern clean API
from tableaux import LogicSystem

# Create logic systems
classical = LogicSystem.classical()
fde = LogicSystem.fde()
weak_kleene = LogicSystem.weak_kleene()

# Natural formula construction
p, q = classical.atoms('p', 'q')
formula = p.implies(q) & p & ~q

# Solve with rich results
result = classical.solve(formula, track_steps=True)
print(f"Satisfiable: {result.satisfiable}")
print(f"Models: {result.models}")

# Parser integration
formula = fde.parse("(p & ~p) | q")
result = fde.solve(formula)

# Entailment checking
premises = [classical.parse("p -> q"), p]
conclusion = q
assert classical.entails(premises, conclusion)  # Modus ponens
```

### Testing Framework

```bash
# Comprehensive test suite (36 tests total)
python -m pytest tests/test_clean_api.py -v      # Modern API tests (23 tests)
python -m pytest tests/test_fde_extension.py -v  # Extension example (13 tests)

# Run all tests
python -m pytest -v                             # All tests across all systems
```

## Plugin Architecture Details

### Defining New Logic Systems for Philosophical Logicians

The unified architecture makes it natural to define new logic systems. Each logic is completely self-contained in one file with both syntax and tableau rules:

**Complete Logic Definition** (`src/tableaux/logics/my_logic.py`):
```python
from .logic_system import LogicSystem
from ..core.formula import ConnectiveSpec
from ..core.semantics import TruthValueSystem  
from ..core.signs import SignSystem
from ..core.rules import TableauRule, RuleType, RulePattern

class MyLogic(LogicSystem):
    """Complete definition of my logic system."""
    
    def initialize(self):
        # 1. Define the syntax (connectives and precedence)
        self.add_connective(ConnectiveSpec("&", 2, 3, "left", "infix"))   # conjunction
        self.add_connective(ConnectiveSpec("|", 2, 2, "left", "infix"))   # disjunction  
        self.add_connective(ConnectiveSpec("~", 1, 4, "none", "prefix"))  # negation
        self.add_connective(ConnectiveSpec("->", 2, 1, "right", "infix")) # implication
        
        # 2. Define the semantics (truth values and operations)
        self.set_truth_system(MyTruthSystem())
        self.set_sign_system(MySignSystem())
        
        # 3. Define the tableau rules (complete proof theory)
        self._add_tableau_rules()
    
    def _add_tableau_rules(self):
        """Define all tableau rules for this logic."""
        
        # T-Conjunction (non-branching)
        self.add_rule(TableauRule(
            name="T-Conjunction",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "A & B")],
            conclusions=[["T:A", "T:B"]]
        ))
        
        # F-Conjunction (branching)  
        self.add_rule(TableauRule(
            name="F-Conjunction",
            rule_type=RuleType.BETA,
            premises=[RulePattern("F", "A & B")],
            conclusions=[["F:A"], ["F:B"]]
        ))
        
        # ... more rules ...
```

**Key Advantages for Philosophical Logicians**:
- **Conceptual Unity**: Syntax and rules defined together in one place
- **Self-Contained**: Everything about your logic is in one file
- **Natural Workflow**: Define connectives, then define how they behave in tableaux
- **Immediate Availability**: Once defined, your logic works with CLI, API, and parser
- **Research Friendly**: Easy to modify and experiment with rule variations

**Register and Use**:
```python
# Register once
LogicRegistry.register(MyLogic("my_logic"))

# Use everywhere
logic_system = LogicSystem.my_logic()  # Programmatic
```

```bash
tableaux --logic=my_logic "formula"   # Command line
```

### Extension Example: FDE Logic

The FDE (First-Degree Entailment) logic serves as a complete example of extending the system:

- **File**: `src/tableaux/logics/fde.py`
- **Features**: Four-valued paraconsistent/paracomplete logic
- **Signs**: T (true only), F (false only), B (both), N (neither)
- **Properties**: Contradictions satisfiable, LEM not valid
- **Integration**: Full CLI, API, and parser support

## Research Quality Standards

This implementation maintains **research-grade quality standards** combining theoretical rigor with industrial software engineering practices:

### Research Excellence Standards
- **Theoretical Soundness**: All tableau rules correctly implement formal logical semantics
- **Semantic Accuracy**: Each logic system implements exact semantic conditions  
- **Completeness Preservation**: No arbitrary limits that compromise logical completeness
- **Performance Optimization**: Industrial-grade optimizations while preserving correctness

### Software Engineering Excellence
- **Modular Architecture**: Clean separation between core engine and logic plugins
- **Comprehensive Testing**: 36 tests across all logic systems with systematic coverage
- **Modern API**: Natural Python syntax with type safety and rich result objects
- **Extensible CLI**: Plugin-aware interface that automatically supports new logic systems

### Current Research Capabilities
- **Logic System Comparison**: Framework enables systematic comparison of reasoning performance
- **Semantic Investigation**: Support for investigating truth value propagation in non-classical systems
- **Optimization Analysis**: Platform for studying tableau optimization effectiveness across logics
- **Extensibility Research**: Clean framework for prototyping new tableau-based reasoning systems

## Architecture Guidelines

When extending this research platform:

1. **Preserve Theoretical Correctness**: All extensions must maintain formal semantic accuracy
   - Implement complete truth tables for non-classical operators
   - Verify soundness and completeness properties where applicable
   - Include mathematical documentation of semantic choices

2. **Follow Plugin Architecture**: New logic systems should be implemented as plugins
   - Use the LogicSystem base class and registry system
   - Implement required abstract methods for truth systems, signs, and rules
   - Add comprehensive tests to verify correctness

3. **Maintain Performance Standards**: Extensions should preserve industrial-grade performance
   - Preserve O(1) critical operations (closure detection, rule lookup)
   - Implement proper α/β rule prioritization for new logic systems
   - Add performance benchmarks for new implementations

4. **Support Research Reproducibility**: Enable other researchers to validate and extend work
   - Include complete working examples for each logic system
   - Provide clear extension points for new research directions
   - Maintain backward compatibility to preserve existing research results

## Important Architecture Notes

### Current Architecture Overview

The system follows a clean modular design:

```
src/tableaux/
├── core/                    # Core tableau framework
│   ├── formula.py          # Abstract formula representation
│   ├── semantics.py        # Truth value systems
│   ├── signs.py            # Sign systems (T/F, T/F/U, etc.)
│   ├── tableau_engine.py   # Optimized tableau construction
│   ├── rule_engine.py      # Rule application logic
│   ├── rules.py            # Rule DSL framework
│   └── syntax.py           # Syntactic operations
├── logics/                  # Complete logic system definitions
│   ├── logic_system.py     # Plugin architecture
│   ├── classical.py        # Classical logic (syntax + rules)
│   ├── weak_kleene.py      # Weak Kleene logic (syntax + rules)
│   ├── wkrq.py             # wKrQ logic (syntax + rules)
│   └── fde.py              # FDE logic (syntax + rules)
├── api.py                   # Modern Python API
├── parser.py                # Extensible parser
└── extensible_cli.py        # Command-line interface
```

### Key Design Principles

- **Plugin Architecture**: All logic systems are plugins with no hardcoded logic
- **Unified Engine**: Single tableau engine supports all logic systems  
- **Clean API**: Modern Python interface with natural formula construction
- **Extensible CLI**: `--logic` parameter works with any registered system
- **Parser Integration**: String formulas use standard `->` syntax for implication
- **API Consistency**: Programmatic formulas use `.implies()` method for implication
- **Research Quality**: Theoretical correctness with industrial performance

### Test Coverage

- **Modern API Tests**: Comprehensive coverage in `test_clean_api.py`
- **Extension Example**: Complete FDE implementation in `test_fde_extension.py`  
- **Tutorial Examples**: All tutorial code examples are tested and verified

This architecture provides a clean, efficient, and theoretically sound foundation for automated reasoning research while maintaining the flexibility to support any tableau-based logic system through the plugin architecture.