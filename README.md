# Semantic Tableau System

A research-grade Python implementation of semantic tableau methods for automated theorem proving, supporting multiple logic systems through a unified plugin architecture.

## Features

- **Multiple Logic Systems**: Classical, weak Kleene, and wKrQ logic with consistent API
- **Plugin Architecture**: Easy extension with custom logic systems
- **Unified Interface**: Same API and CLI work across all logic systems  
- **Industrial Performance**: Optimized tableau construction with proper termination
- **Research Quality**: Theoretical soundness with practical usability

## Quick Start

```bash
# Install
pip install tableaux

# Test classical logic
tableaux "p | ~p"

# Test three-valued logic  
tableaux --logic=weak_kleene "p | ~p"

# Test four-valued epistemic logic
tableaux --logic=wkrq "p | ~p"

# Interactive mode
tableaux
```

## Supported Logic Systems

- **Classical**: Two-valued propositional logic (T, F)
- **Weak Kleene**: Three-valued logic with undefined values (T, F, U)  
- **wKrQ**: Four-valued epistemic logic with restricted quantification (T, F, M, N)

### Extension Example

- **FDE**: Four-valued paraconsistent logic (T, F, B, N) - demonstrates plugin architecture

## Python API

```python
from tableaux import LogicSystem

# Create logic system
classical = LogicSystem.classical()

# Build formulas
p, q = classical.atoms('p', 'q')
formula = p.implies(q) & p & ~q

# Test satisfiability
result = classical.solve(formula)
print(f"Satisfiable: {result.satisfiable}")
print(f"Models: {result.models}")

# Test entailment
premises = [classical.parse("p -> q"), p]
conclusion = q
valid = classical.entails(premises, conclusion)
print(f"Modus ponens valid: {valid}")
```

## Tutorial

**📖 [Complete Tutorial](docs/TUTORIAL.md)** - Comprehensive guide covering:

- Command line interface usage
- Python API with examples
- Working with different logic systems
- Building your own logic system plugin
- Advanced usage patterns

## Installation

### From PyPI (Recommended)

```bash
pip install tableaux
```

### From Source

```bash
git clone https://github.com/bradleypallen/tableaux.git
cd tableaux
pip install -e .

# Verify installation
python -m pytest tests/
```

## Architecture

The system uses a clean modular design:

```
src/tableaux/
├── core/              # Framework infrastructure
├── logics/            # Complete logic system definitions
│   ├── classical.py   # Classical logic (syntax + rules)
│   ├── weak_kleene.py # Weak Kleene (syntax + rules)
│   └── wkrq.py        # wKrQ logic (syntax + rules)
├── api.py             # Modern Python API
├── parser.py          # Extensible parser
└── extensible_cli.py  # Command-line interface
```

Each logic system is completely self-contained, defining both syntax and tableau rules in one place.

## Key Design Principles

- **Unified Logic Definitions**: Each logic system contains both syntax and tableau rules
- **Plugin Architecture**: Easy extension with new logic systems
- **Research Quality**: Theoretical correctness with practical performance
- **Clean API**: Natural Python syntax with consistent patterns
- **Industrial Performance**: Optimized tableau construction algorithms

## Documentation

- **[Tutorial](docs/TUTORIAL.md)** - Complete guide with examples
- **[API Reference](docs/API_REFERENCE.md)** - Detailed API documentation
- **[CLI Guide](docs/CLI_GUIDE.md)** - Command-line interface reference
- **[Architecture](docs/ARCHITECTURE.md)** - System design details

## Testing

```bash
# Run all tests
python -m pytest tests/

# Specific test suites
python -m pytest tests/test_clean_api.py -v          # Modern API tests
python -m pytest tests/test_fde_extension.py -v      # FDE extension example
python -m pytest tests/test_literature_examples.py -v # Literature examples  
python -m pytest tests/test_countermodels.py -v      # Countermodel examples
```

## Performance

The system includes standard tableau optimizations:

- **O(1) closure detection** using hash-based formula tracking
- **α/β rule prioritization** (non-branching before branching rules)
- **Early termination** on satisfiability determination
- **Subsumption elimination** for branch pruning

## Contributing

When extending the system:

1. **Maintain logical correctness** - All implementations must be semantically sound
2. **Follow plugin architecture** - New logics should be self-contained
3. **Add comprehensive tests** - Include systematic test coverage
4. **Document semantic choices** - Explain logical and implementation decisions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Further Reading

The system demonstrates how semantic tableau methods can be implemented with clean architecture, optimized performance, and support for multiple logical systems suitable for both research and educational applications.

For comprehensive guides and examples, start with the **[Tutorial](docs/TUTORIAL.md)**.