# Changelog

All notable changes to the tableaux project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-25

### Added
- Initial release of the semantic tableau system
- Support for classical propositional logic with optimized tableau algorithm
- Support for three-valued Weak Kleene logic (WK3) with gap semantics
- Support for wKrQ four-valued epistemic logic
- Unified tableau engine with step-by-step visualization
- Command-line interface with multiple output formats
- Comprehensive test suite with 69 tests
- Tutorial system with 7 interactive examples
- Complete documentation suite including tutorials, API reference, and architecture guide

### Features
- Formula parsing with proper operator precedence
- Model extraction and satisfiability checking
- Performance optimizations: O(1) closure detection, α/β rule prioritization
- Multiple logic system support in single unified engine
- Step-by-step tableau construction visualization
- Support for first-order logic with predicates and quantifiers

### Project Structure
- Modern Python packaging structure ready for PyPI distribution
- CLI entry point allowing `tableaux` command after installation
- Minimum Python version: 3.10
- Zero runtime dependencies