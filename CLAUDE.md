# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository is a **research platform for semantic tableau systems supporting non-classical logics**, implemented in Python with a focus on **theoretical correctness and computational efficiency**. The project brings together the best practices from both industrial automated reasoning systems and academic research in non-classical logic semantics.

**Primary Research Goal**: To support rigorous investigation of tableau-based proof methods for non-classical logics, including but not limited to many-valued logics, modal logics, temporal logics, and paraconsistent logics. The implementation prioritizes semantic accuracy, algorithmic efficiency, and extensibility to enable systematic comparison and analysis of different logical systems.

**Core Philosophy**: Combine the **theoretical rigor** expected in automated reasoning research with the **software engineering excellence** found in production theorem proving systems. Every logical system implementation must be demonstrably sound and complete (where applicable), while maintaining industrial-grade performance characteristics and code quality.

**License**: MIT License - This project is open source and freely available for use, modification, and distribution under the MIT License.

## Current Unified Architecture

The system has been consolidated into a **unified tableau framework** with a single core implementation supporting multiple logic systems:

### Core Implementation (Unified System)
- `tableau_core.py` - **Complete unified implementation** containing:
  - Formula representation (atoms, connectives, predicates, quantifiers)
  - Truth value systems (classical, three-valued WK3, four-valued wKrQ)
  - Sign systems (classical T/F, three-valued T3/F3/U, epistemic wKrQ T/F/M/N)
  - Optimized tableau engine with step-by-step visualization
  - Tableau rules for multiple logic systems
  - Model extraction and satisfiability checking
  - Mode-aware system for propositional and first-order logic
  - Formula parsing with proper operator precedence

### Supporting Modules
- `unified_model.py` - Unified model representation for all logic systems
- `cli.py` - Command-line interface supporting multiple logic systems

### Demonstration Programs
- `tableau_demo.py` - Comprehensive demonstration of tableau capabilities
- `wkrq_countermodel_demo.py` - Ferguson's wKrQ epistemic logic demonstrations  
- `wkrq_theoretical_demo.py` - Theoretical insights for weak Kleene logic
- `verify_kleene_tables.py` - Verification of weak Kleene truth tables

### Testing Framework (Consolidated)
- `test_comprehensive.py` - **Main unified test suite (35 tests)** covering all functionality
- `test_literature_examples.py` - Academic validation tests (26 tests) from Priest, Fitting, Smullyan, Ferguson
- `test_performance.py` - Performance benchmarks and optimization validation
- `test_setup.py` - Test utilities and setup functions

### Tutorial System
- `tutorial1_test.py` through `tutorial7_test.py` - Interactive tutorial examples
- Various specialized demo files for research-specific features

## Development Commands

This is a research-grade Python project with unified architecture and comprehensive testing. Key commands:

```bash
# Main demonstration
python tableau_demo.py            # Comprehensive tableau system demonstration

# Interactive research interface (supports multiple logics)
tableaux                     # Interactive mode with logic switching
tableaux "p | ~p"            # Classical logic command-line
tableaux --wk3 "p | ~p"      # WK3 logic command-line

# Comprehensive testing framework (69 tests total)
python -m pytest -v                           # All tests across all systems
python -m pytest test_comprehensive.py -v     # Unified test suite (35 tests)
python -m pytest test_literature_examples.py -v  # Literature validation (26 tests)

# Performance and optimization analysis
python -m pytest test_performance.py -v       # Performance benchmarks

# Research demonstrations
python wkrq_countermodel_demo.py    # Ferguson's wKrQ epistemic logic
python wkrq_theoretical_demo.py     # Theoretical insights demonstration
python verify_kleene_tables.py      # Weak Kleene truth table verification

# Tutorial examples
python tutorial1_test.py            # Basic tableau construction
python tutorial2_test.py            # Signed formula notation
# ... (tutorials 3-7 for advanced topics)
```

## Unified Architecture Details

The system implements a **single unified tableau engine** with the following key characteristics:

### Core Engine Features
- **Theoretical Soundness**: All tableau rules implement correct logical semantics
- **Complete Termination**: No arbitrary limits that compromise logical completeness  
- **Industrial Performance**: O(1) closure detection, α/β rule prioritization, subsumption elimination
- **Multi-Logic Support**: Classical, WK3, wKrQ epistemic logic in single engine
- **Enhanced Visualization**: Step-by-step construction with rule names and tree structure

### Supported Logic Systems
- **Classical Propositional Logic**: Two-valued semantics (T/F signs)
- **Weak Kleene Logic (WK3)**: Three-valued semantics (T3/F3/U signs)  
- **wKrQ Epistemic Logic**: Four-valued Ferguson system (T/F/M/N signs)
- **First-Order Logic**: Ground atomic formulas with predicate and term structures

### Key API Functions (tableau_core.py)
```python
# Core tableau functions - use these exclusively
classical_signed_tableau(signed_formula, track_steps=False)
three_valued_signed_tableau(signed_formula, track_steps=False) 
wkrq_signed_tableau(signed_formulas, track_steps=False)
ferguson_signed_tableau(signed_formulas, track_steps=False)

# Formula construction
Atom(name), Negation(formula), Conjunction(left, right)
Disjunction(left, right), Implication(left, right)
Predicate(name, terms), Constant(name), Variable(name)

# Sign systems
T(formula), F(formula)        # Classical signs
T3(formula), F3(formula), U(formula)  # Three-valued signs
TF(formula), FF(formula), M(formula), N(formula)  # wKrQ signs

# Truth values
t, f, e  # true, false, undefined/error
```

## Research Quality Standards

This implementation maintains **research-grade quality standards** (9.0/10) combining theoretical rigor with industrial software engineering practices:

### Research Excellence Standards
- **Theoretical Soundness**: All tableau rules correctly implement formal logical semantics with mathematical precision
- **Semantic Accuracy**: Three-valued WK3 semantics implement exact Weak Kleene truth conditions
- **Completeness Preservation**: No arbitrary limits that compromise logical completeness or decidability
- **Performance Optimization**: Industrial-grade optimizations (α/β prioritization, O(1) closure, subsumption elimination)

### Research Infrastructure Quality
- **Comprehensive Testing**: 69 tests across all logic systems with systematic edge case coverage
- **Architecture Documentation**: Complete technical documentation suitable for peer review
- **Benchmarking Framework**: Performance analysis ensuring scalability for research applications
- **Literature Validation**: Academic examples from major tableau references

### Current Research Capabilities
- **Logic System Comparison**: Framework enables systematic comparison of reasoning performance
- **Semantic Investigation**: Support for investigating truth value propagation in non-classical systems  
- **Optimization Analysis**: Platform for studying tableau optimization effectiveness across logics
- **Extensibility Research**: Clean framework for prototyping new tableau-based reasoning systems

## Important: Eliminated Patterns (DO NOT USE)

The following patterns were **eliminated during consolidation** and must **NOT** be referenced:

### Eliminated Convenience Functions
```python
# DELETED - Do not use these functions:
wk3_satisfiable(formula)     # Use tableau approach instead
wk3_models(formula)          # Use tableau.extract_all_models() instead
```

### Eliminated Test Files
```python
# DELETED - These test files no longer exist:
test_tableau.py              # Consolidated into test_comprehensive.py
test_wk3.py                  # Consolidated into test_comprehensive.py  
test_signed_tableau.py       # Consolidated into test_comprehensive.py
# ... (16 total test files were consolidated)
```

### Eliminated Architecture Files
```python
# DELETED - These files never existed or were removed:
tableau.py, wk3_tableau.py, formula.py, truth_value.py
componentized_tableau.py, tableau_rules.py, logic_system.py
mode_aware_tableau.py, mode_aware_parser.py, logic_mode.py
# All functionality moved to tableau_core.py
```

## Correct Usage Patterns

### WK3 Satisfiability Checking
```python 
# CORRECT: Use tableau approach
from tableau_core import three_valued_signed_tableau, T3, U, Atom

formula = Atom("p")
# WK3 formula is satisfiable if it can be true OR undefined
t3_tableau = three_valued_signed_tableau(T3(formula))
u_tableau = three_valued_signed_tableau(U(formula))
is_satisfiable = t3_tableau.build() or u_tableau.build()

# Get models
models = []
if t3_tableau.build():
    models.extend(t3_tableau.extract_all_models())
if u_tableau.build():
    models.extend(u_tableau.extract_all_models())
```

### Classical Logic Testing
```python
# CORRECT: Use unified tableau engine
from tableau_core import classical_signed_tableau, T, Atom, Implication

p, q = Atom("p"), Atom("q")
formula = Implication(p, q)
tableau = classical_signed_tableau(T(formula))
is_satisfiable = tableau.build()
models = tableau.extract_all_models() if is_satisfiable else []
```

### Testing Approach
```python
# CORRECT: Use consolidated test files
python -m pytest test_comprehensive.py -v      # Main test suite
python -m pytest test_literature_examples.py -v  # Academic validation

# INCORRECT: These files don't exist
python -m pytest test_tableau.py -v            # DELETED
python -m pytest test_wk3.py -v                # DELETED
```

## Research Development Guidelines

When extending this research platform:

1. **Preserve Theoretical Correctness**: All extensions must maintain formal semantic accuracy
   - Implement complete truth tables for non-classical operators
   - Verify soundness and completeness properties where applicable
   - Include mathematical documentation of semantic choices

2. **Maintain Performance Standards**: Research extensions should preserve industrial-grade performance
   - Preserve O(1) critical operations (closure detection, rule lookup)
   - Implement proper α/β rule prioritization for new logic systems
   - Add performance benchmarks for new logic system implementations

3. **Add Comprehensive Validation**: New logic systems require complete test coverage
   - Add tests to test_comprehensive.py or test_literature_examples.py
   - Include edge cases specific to non-classical semantics
   - Add comparative tests against reference implementations where available

4. **Document Research Decisions**: All semantic and implementation choices must be documented
   - Explain departures from standard semantics with mathematical justification
   - Document performance trade-offs and optimization strategies
   - Include references to relevant literature and formal specifications

5. **Support Research Reproducibility**: Enable other researchers to validate and extend work
   - Include complete working examples for each logic system
   - Provide clear extension points for new research directions
   - Maintain backward compatibility to preserve existing research results

## Coding Principles and Best Practices

### Fundamental Principles
- **Do not, under any circumstances, add a workaround to a demo when there is an underlying bug; fix the bug so that the demo works correctly.**
- **Don't eliminate items for the imports because they are not working. Fix the underlying problem.**
- **Always use the unified tableau approach - never reference eliminated convenience functions**
- **Use consolidated test files - never reference deleted test files**

### Documentation and Communication Guidelines
- In comments and documentation, do not use language that is promotional or self-congratulatory. Keep to fact-based statements that are appropriate for academic exposition.
- Always reference the current unified architecture, not eliminated multi-file systems
- Update any references to outdated file structures or eliminated functions

### Important Reminders
- The system uses **ONE** core file: `tableau_core.py` - everything else is supporting
- All tableau operations use `tableau.build()` and `tableau.extract_all_models()`
- Test count is **69 tests total** (35 comprehensive + 26 literature + 8 others)
- **NO** convenience functions exist - use tableau functions directly
- **NO** separate tableau files exist - everything is unified in tableau_core.py

This unified architecture provides a clean, efficient, and theoretically sound foundation for automated reasoning research while maintaining industrial-grade performance characteristics.