# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository is a **research platform for semantic tableau systems supporting non-classical logics**, implemented in Python with a focus on **theoretical correctness and computational efficiency**. The project brings together the best practices from both industrial automated reasoning systems and academic research in non-classical logic semantics.

**Primary Research Goal**: To support rigorous investigation of tableau-based proof methods for non-classical logics, including but not limited to many-valued logics, modal logics, temporal logics, and paraconsistent logics. The implementation prioritizes semantic accuracy, algorithmic efficiency, and extensibility to enable systematic comparison and analysis of different logical systems.

**Core Philosophy**: Combine the **theoretical rigor** expected in automated reasoning research with the **software engineering excellence** found in production theorem proving systems. Every logical system implementation must be demonstrably sound and complete (where applicable), while maintaining industrial-grade performance characteristics and code quality.

**License**: MIT License - This project is open source and freely available for use, modification, and distribution under the MIT License.

## Project Structure

### Research-Grade Logic Systems
- `tableau.py` - Classical propositional logic (reference implementation)
- `wk3_tableau.py` - Weak Kleene Logic (WK3) with three-valued semantics
- `formula.py` - Formula AST with support for propositional and first-order constructs
- `truth_value.py` - Multi-valued truth systems (classical, WK3, extensible)
- `wk3_model.py` - Three-valued model evaluation and semantics

### Componentized Architecture (Version 2.0)
- `componentized_tableau.py` - Unified tableau engine for multiple logic systems
- `tableau_rules.py` - Abstract rule system with pluggable tableau rules
- `logic_system.py` - Logic system registry and component management
- `classical_rules.py` / `wk3_rules.py` - Logic-specific tableau rule implementations
- `classical_components.py` / `wk3_components.py` - Logic-specific branch management and model extraction
- `builtin_logics.py` - Standard logic system definitions and registry

### Mode-Aware Extensions
- `mode_aware_tableau.py` - Logic mode separation (propositional vs first-order)
- `mode_aware_parser.py` - Mode-specific formula parsing and validation
- `logic_mode.py` - Mode detection and enforcement
- `term.py` - First-order terms (constants, variables, function applications)

### Interface and Demonstration Tools
- `cli.py` - Command-line interface with multi-logic support
- `wk3_demo.py` - Weak Kleene logic demonstration and examples
- `demo_componentized.py` - Componentized system capabilities demonstration

### Research Documentation and Testing
- `test_comprehensive.py` - Unified test suite (42 tests) covering all functionality
- `test_tableau.py` - Classical logic test suite (50+ tests)
- `test_wk3.py` - WK3 logic test suite (25+ tests)
- `test_componentized_rules.py` - Component system validation (18 tests)
- `test_performance.py` - Performance benchmarks and optimization validation
- `ARCHITECTURE.md` - Comprehensive architectural documentation for code review
- `README.md` - Complete usage documentation for all interfaces
- `OPTIMIZATIONS.md` - Performance analysis and optimization strategies
- `TECHNICAL_ANALYSIS.md` - Implementation quality assessment
- `WEAK_KLEENE_PLAN.md` - WK3 research implementation plan

## Development Commands

This is a research-grade Python project with multiple logic systems, componentized architecture, and comprehensive testing. Key commands:

```bash
# Research demonstrations and examples
python tableau.py              # Classical logic reference implementation
python wk3_demo.py             # Weak Kleene logic research demonstration
python demo_componentized.py   # Componentized architecture capabilities

# Interactive research interface (supports multiple logics)
python cli.py                  # Interactive mode with logic switching
python cli.py "p | ~p"         # Classical logic command-line
python cli.py --wk3 "p | ~p"   # WK3 logic command-line

# Comprehensive testing framework (100+ tests total)
python -m pytest test_comprehensive.py -v    # Unified test suite (42 tests)
python -m pytest -v                          # All tests across all systems

# Logic-specific test suites
python -m pytest test_tableau.py -v          # Classical logic validation (50+ tests)
python -m pytest test_wk3.py -v             # WK3 logic validation (25+ tests)
python -m pytest test_componentized_rules.py -v  # Architecture validation (18 tests)

# Performance and optimization analysis
python -m pytest test_performance.py -v      # Performance benchmarks
python -m pytest test_medium_optimizations.py -v  # Optimization validation

# Research-specific testing
python -c "from test_comprehensive import run_classical_tests; run_classical_tests()"
python -c "from test_comprehensive import run_wk3_tests; run_wk3_tests()"
python -c "from test_comprehensive import run_componentized_tests; run_componentized_tests()"
```

## Research Architecture

The system implements a **componentized tableau framework** designed specifically for non-classical logic research, with three architectural layers supporting rigorous investigation:

### 1. Legacy Research Implementations (Version 1.0)
- **Classical Logic Reference**: Optimized implementation demonstrating standard tableau methods
- **Weak Kleene Logic (WK3)**: Complete three-valued logic system with proper semantics
- **Theoretical Validation**: Each system includes comprehensive correctness verification

### 2. Componentized Research Framework (Version 2.0)
- **Plugin Architecture**: Abstract rule system enabling rapid logic system prototyping
- **Logic System Registry**: Centralized management of multiple logic variants
- **Component Abstractions**: Pluggable branch management, closure detection, model extraction
- **Extension Framework**: Clean interfaces for implementing new non-classical logics

### 3. Mode-Aware Logic Separation
- **Propositional Mode**: Pure propositional logic with atom-level reasoning
- **First-Order Mode**: Ground predicate support with term structures (extensible to full FOL)
- **Mixed Mode Prevention**: Rigorous separation ensuring semantic correctness

### Research-Grade Implementation Features
- **Theoretical Soundness**: All tableau rules implement correct logical semantics
- **Complete Termination**: No arbitrary limits that compromise logical completeness  
- **Industrial Performance**: O(1) closure detection, α/β rule prioritization, subsumption elimination
- **Extensibility**: Multiple clean extension points for new logic systems
- **Validation Framework**: Comprehensive testing ensuring correctness of logical implementations

### Supported Logic Systems (Current Research)
- **Classical Propositional Logic**: Two-valued semantics with complete tableau rules
- **Weak Kleene Logic (WK3)**: Three-valued semantics with undefined value propagation
- **First-Order Logic**: Ground atomic formulas with predicate and term structures
- **Extension Points**: Modal, temporal, many-valued, and paraconsistent logics

## Research Quality Standards

This implementation maintains **research-grade quality standards** (9.0/10) combining theoretical rigor with industrial software engineering practices:

### **Research Excellence Standards**
- **Theoretical Soundness**: All tableau rules correctly implement formal logical semantics with mathematical precision
- **Semantic Accuracy**: Three-valued WK3 semantics implement exact Weak Kleene truth conditions
- **Completeness Preservation**: No arbitrary limits that compromise logical completeness or decidability
- **Extension Correctness**: Component framework validated to preserve soundness across logic system extensions
- **Performance Optimization**: Industrial-grade optimizations (α/β prioritization, O(1) closure, subsumption elimination)

### **Research Infrastructure Quality**
- **Comprehensive Testing**: 100+ tests across all logic systems with systematic edge case coverage
- **Architecture Documentation**: Complete technical documentation suitable for peer review
- **Component Validation**: Each logical component includes correctness verification
- **Benchmarking Framework**: Performance analysis ensuring scalability for research applications
- **Extension Validation**: Plugin architecture verified with multiple logic system implementations

### **Current Research Capabilities**
- **Logic System Comparison**: Framework enables systematic comparison of reasoning performance
- **Semantic Investigation**: Support for investigating truth value propagation in non-classical systems  
- **Optimization Analysis**: Platform for studying tableau optimization effectiveness across logics
- **Extensibility Research**: Clean framework for prototyping new tableau-based reasoning systems

### **Research Development Guidelines**
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
   - Implement systematic test cases covering all logical patterns
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