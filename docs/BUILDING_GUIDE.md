# Building with the Tableau System: Developer's Guide

**Version**: 2.0 (Plugin Architecture)  
**Last Updated**: January 2025  
**License**: MIT  

## Table of Contents

1. [Introduction](#introduction)
2. [Understanding the Plugin Architecture](#understanding-the-plugin-architecture)
3. [Building New Logic Systems](#building-new-logic-systems)
4. [Extending Existing Logic Systems](#extending-existing-logic-systems)
5. [Performance Optimization](#performance-optimization)
6. [Testing Your Extensions](#testing-your-extensions)
7. [Common Patterns and Best Practices](#common-patterns-and-best-practices)
8. [Troubleshooting](#troubleshooting)

## Introduction

This guide teaches you how to extend the tableau system's plugin architecture to build new logic systems. The current architecture supports classical, weak Kleene, wKrQ, and FDE logic through a unified framework that makes adding new logics straightforward.

### Who This Guide Is For

- **Researchers** implementing new logical systems
- **Developers** extending the existing implementation
- **Students** learning how tableau systems work
- **Contributors** adding features to the project

### Prerequisites

- Python 3.10+ programming experience
- Basic understanding of propositional logic
- Familiarity with tableau methods
- Understanding of the concepts in [TUTORIAL.md](TUTORIAL.md)

### Philosophy: Unified Logic Definitions

The key insight of this architecture is that **a logic system is defined by its syntax and tableau rules together**. Each logic system is completely self-contained in a single file, containing:

1. **Connective definitions** (syntax and precedence)
2. **Truth value systems** (semantics)
3. **Sign systems** (tableau signs)
4. **Tableau rules** (complete proof theory)

This makes logic systems natural to define, understand, and modify.

## Understanding the Plugin Architecture

### Core Components

The system is built around several key abstractions:

```python
# Core framework (src/tableaux/core/)
from tableaux.core.formula import ConnectiveSpec
from tableaux.core.semantics import TruthValueSystem, TruthValue
from tableaux.core.signs import SignSystem, Sign
from tableaux.core.rules import TableauRule, RuleType, RulePattern

# Plugin system (src/tableaux/logics/)
from tableaux.logics.logic_system import LogicSystem, LogicRegistry
```

### Logic System Lifecycle

1. **Definition**: Create a class extending `LogicSystem`
2. **Registration**: Register with `LogicRegistry`
3. **Discovery**: Automatic CLI and API integration
4. **Usage**: Available via `--logic=name` and `LogicSystem.name()`

### Example: Complete Logic System

```python
# src/tableaux/logics/my_logic.py
from .logic_system import LogicSystem
from ..core.formula import ConnectiveSpec
from ..core.semantics import TruthValueSystem, TruthValue
from ..core.signs import SignSystem, Sign
from ..core.rules import TableauRule, RuleType, RulePattern

class MyLogic(LogicSystem):
    """Complete definition of my custom logic system."""
    
    def initialize(self):
        """Initialize the logic system with syntax, semantics, and rules."""
        # 1. Define connectives
        self._define_connectives()
        
        # 2. Set truth value system
        self.set_truth_system(MyTruthValueSystem())
        
        # 3. Set sign system
        self.set_sign_system(MySignSystem())
        
        # 4. Define tableau rules
        self._define_tableau_rules()
    
    def _define_connectives(self):
        """Define the syntax of logical connectives."""
        self.add_connective(ConnectiveSpec("&", 2, 3, "left", "infix"))
        self.add_connective(ConnectiveSpec("|", 2, 2, "left", "infix"))
        self.add_connective(ConnectiveSpec("~", 1, 4, "none", "prefix"))
        self.add_connective(ConnectiveSpec("->", 2, 1, "right", "infix"))
    
    def _define_tableau_rules(self):
        """Define the complete tableau proof system."""
        # T-Conjunction rule
        self.add_rule(TableauRule(
            name="T-Conjunction",
            rule_type=RuleType.ALPHA,
            premises=[RulePattern("T", "A & B")],
            conclusions=[["T:A", "T:B"]],
            priority=1
        ))
        # ... more rules
```

## Building New Logic Systems

### Step 1: Create the Logic Class

Create a new file in `src/tableaux/logics/` for your logic system:

```python
# src/tableaux/logics/lukasiewicz.py
from .logic_system import LogicSystem
from ..core.formula import ConnectiveSpec
from ..core.semantics import TruthValueSystem, TruthValue
from ..core.signs import SignSystem, Sign
from ..core.rules import TableauRule, RuleType, RulePattern
from typing import Set, Optional, Callable

class LukasiewiczLogic(LogicSystem):
    """Łukasiewicz three-valued logic system."""
    
    def initialize(self):
        """Initialize Łukasiewicz logic."""
        self._define_connectives()
        self.set_truth_system(LukasiewiczTruthSystem())
        self.set_sign_system(LukasiewiczSignSystem())
        self._define_tableau_rules()
    
    def _define_connectives(self):
        """Define connectives with precedence."""
        # Standard connectives
        self.add_connective(ConnectiveSpec("&", 2, 3, "left", "infix"))
        self.add_connective(ConnectiveSpec("|", 2, 2, "left", "infix"))
        self.add_connective(ConnectiveSpec("~", 1, 4, "none", "prefix"))
        self.add_connective(ConnectiveSpec("->", 2, 1, "right", "infix"))
```

### Step 2: Define Truth Value System

```python
class LukasiewiczTruthValue(TruthValue):
    """Truth values for Łukasiewicz logic."""
    
    def __init__(self, name: str, value: float):
        self.name = name
        self.value = value  # 0.0, 0.5, 1.0
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        return isinstance(other, LukasiewiczTruthValue) and self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)

class LukasiewiczTruthSystem(TruthValueSystem):
    """Łukasiewicz three-valued truth system."""
    
    def __init__(self):
        self.false = LukasiewiczTruthValue("F", 0.0)
        self.half = LukasiewiczTruthValue("H", 0.5)
        self.true = LukasiewiczTruthValue("T", 1.0)
    
    def truth_values(self) -> Set[TruthValue]:
        """All truth values in this system."""
        return {self.false, self.half, self.true}
    
    def designated_values(self) -> Set[TruthValue]:
        """Values that count as 'true' - only 1.0 is designated."""
        return {self.true}
    
    def evaluate_negation(self, value: TruthValue) -> TruthValue:
        """Łukasiewicz negation: ~x = 1 - x"""
        if value == self.true:
            return self.false
        elif value == self.false:
            return self.true
        else:  # half
            return self.half
    
    def evaluate_conjunction(self, left: TruthValue, right: TruthValue) -> TruthValue:
        """Łukasiewicz conjunction: x ∧ y = min(x, y)"""
        min_val = min(left.value, right.value)
        if min_val == 0.0:
            return self.false
        elif min_val == 0.5:
            return self.half
        else:
            return self.true
    
    def evaluate_disjunction(self, left: TruthValue, right: TruthValue) -> TruthValue:
        """Łukasiewicz disjunction: x ∨ y = max(x, y)"""
        max_val = max(left.value, right.value)
        if max_val == 1.0:
            return self.true
        elif max_val == 0.5:
            return self.half
        else:
            return self.false
    
    def evaluate_implication(self, left: TruthValue, right: TruthValue) -> TruthValue:
        """Łukasiewicz implication: x → y = min(1, 1 - x + y)"""
        result_val = min(1.0, 1.0 - left.value + right.value)
        if result_val == 1.0:
            return self.true
        elif result_val == 0.5:
            return self.half
        else:
            return self.false
    
    def name(self) -> str:
        return "Lukasiewicz"
    
    def get_operation(self, connective: str) -> Optional[Callable]:
        """Get semantic operation for connective."""
        operations = {
            "&": self.evaluate_conjunction,
            "|": self.evaluate_disjunction,
            "~": self.evaluate_negation,
            "->": self.evaluate_implication,
        }
        return operations.get(connective)
```

### Step 3: Define Sign System

```python
class LukasiewiczSign(Sign):
    """Signs for Łukasiewicz tableau system."""
    
    def __init__(self, symbol: str):
        if symbol not in ["T", "F", "H"]:
            raise ValueError(f"Invalid Łukasiewicz sign: {symbol}")
        self.symbol = symbol
    
    def __str__(self) -> str:
        return self.symbol
    
    def __eq__(self, other) -> bool:
        return isinstance(other, LukasiewiczSign) and self.symbol == other.symbol
    
    def __hash__(self) -> int:
        return hash(("lukasiewicz", self.symbol))
    
    def get_symbol(self) -> str:
        return self.symbol
    
    def is_contradictory_with(self, other: Sign) -> bool:
        """Define contradiction rules for Łukasiewicz logic."""
        if not isinstance(other, LukasiewiczSign):
            return False
        # T and F contradict, H doesn't contradict with anything
        return (self.symbol == "T" and other.symbol == "F") or \
               (self.symbol == "F" and other.symbol == "T")

class LukasiewiczSignSystem(SignSystem):
    """Sign system for Łukasiewicz logic."""
    
    def __init__(self):
        self.t_sign = LukasiewiczSign("T")
        self.f_sign = LukasiewiczSign("F")
        self.h_sign = LukasiewiczSign("H")
    
    def signs(self) -> Set[Sign]:
        """All signs in this system."""
        return {self.t_sign, self.f_sign, self.h_sign}
    
    def default_sign(self) -> Sign:
        """Default sign for satisfiability testing."""
        return self.t_sign
    
    def name(self) -> str:
        return "Lukasiewicz"
```

### Step 4: Define Tableau Rules

```python
def _define_tableau_rules(self):
    """Define complete tableau rules for Łukasiewicz logic."""
    
    # T-Conjunction rules
    self.add_rule(TableauRule(
        name="T-Conjunction",
        rule_type=RuleType.ALPHA,
        premises=[RulePattern("T", "A & B")],
        conclusions=[["T:A", "T:B"]],
        priority=1
    ))
    
    # F-Conjunction rules
    self.add_rule(TableauRule(
        name="F-Conjunction",
        rule_type=RuleType.BETA,
        premises=[RulePattern("F", "A & B")],
        conclusions=[["F:A"], ["F:B"]],
        priority=2
    ))
    
    # H-Conjunction rules (Łukasiewicz-specific)
    self.add_rule(TableauRule(
        name="H-Conjunction",
        rule_type=RuleType.BETA,
        premises=[RulePattern("H", "A & B")],
        conclusions=[["H:A", "T:B"], ["T:A", "H:B"], ["H:A", "H:B"]],
        priority=2
    ))
    
    # T-Disjunction rules
    self.add_rule(TableauRule(
        name="T-Disjunction",
        rule_type=RuleType.BETA,
        premises=[RulePattern("T", "A | B")],
        conclusions=[["T:A"], ["T:B"]],
        priority=2
    ))
    
    # F-Disjunction rules
    self.add_rule(TableauRule(
        name="F-Disjunction",
        rule_type=RuleType.ALPHA,
        premises=[RulePattern("F", "A | B")],
        conclusions=[["F:A", "F:B"]],
        priority=1
    ))
    
    # H-Disjunction rules
    self.add_rule(TableauRule(
        name="H-Disjunction",
        rule_type=RuleType.BETA,
        premises=[RulePattern("H", "A | B")],
        conclusions=[["H:A", "F:B"], ["F:A", "H:B"], ["H:A", "H:B"]],
        priority=2
    ))
    
    # Negation rules
    self.add_rule(TableauRule(
        name="T-Negation",
        rule_type=RuleType.ALPHA,
        premises=[RulePattern("T", "~ A")],
        conclusions=[["F:A"]],
        priority=1
    ))
    
    self.add_rule(TableauRule(
        name="F-Negation",
        rule_type=RuleType.ALPHA,
        premises=[RulePattern("F", "~ A")],
        conclusions=[["T:A"]],
        priority=1
    ))
    
    self.add_rule(TableauRule(
        name="H-Negation",
        rule_type=RuleType.ALPHA,
        premises=[RulePattern("H", "~ A")],
        conclusions=[["H:A"]],
        priority=1
    ))
    
    # Implication rules (Łukasiewicz-specific semantics)
    self.add_rule(TableauRule(
        name="T-Implication",
        rule_type=RuleType.BETA,
        premises=[RulePattern("T", "A -> B")],
        conclusions=[["F:A"], ["T:B"]],
        priority=2
    ))
    
    # ... more implication rules for F and H signs
```

### Step 5: Registration and Integration

```python
# At the end of lukasiewicz.py

# Register the logic system
from .logic_system import LogicRegistry
LogicRegistry.register(LukasiewiczLogic("lukasiewicz"))

# Add to API (optional convenience method)
def add_lukasiewicz_to_api():
    """Add Łukasiewicz logic to the LogicSystem API."""
    from ..api import LogicSystem as APILogicSystem
    
    @classmethod
    def lukasiewicz(cls):
        """Create a Łukasiewicz logic system."""
        logic = LogicRegistry.get("lukasiewicz")
        return cls(logic)
    
    APILogicSystem.lukasiewicz = lukasiewicz

# Convenience function
def lukasiewicz():
    """Quick access to Łukasiewicz logic."""
    from ..api import LogicSystem
    add_lukasiewicz_to_api()
    return LogicSystem.lukasiewicz()
```

### Step 6: Usage

Your logic system is now available:

```python
# Programmatic usage
from tableaux.logics.lukasiewicz import add_lukasiewicz_to_api
add_lukasiewicz_to_api()

lukasiewicz = LogicSystem.lukasiewicz()
p, q = lukasiewicz.atoms('p', 'q')
formula = p.implies(q)
result = lukasiewicz.solve(formula)
```

```bash
# CLI usage (automatic)
tableaux --logic=lukasiewicz "p -> q"
tableaux --logic=lukasiewicz --sign=H "p | ~p"
```

## Extending Existing Logic Systems

### Adding New Connectives

To add a new connective to an existing logic system:

```python
# In the logic system's _define_connectives method
self.add_connective(ConnectiveSpec("⊕", 2, 2, "left", "infix"))  # XOR

# Add semantic operation
def evaluate_xor(self, left: TruthValue, right: TruthValue) -> TruthValue:
    """Exclusive or: true if exactly one operand is true."""
    if (left == self.true) != (right == self.true):
        return self.true
    else:
        return self.false

# Update get_operation method
def get_operation(self, connective: str) -> Optional[Callable]:
    operations = {
        # ... existing operations
        "⊕": self.evaluate_xor,
    }
    return operations.get(connective)

# Add tableau rules
def _add_xor_rules(self):
    # T-XOR rule (branching)
    self.add_rule(TableauRule(
        name="T-XOR",
        rule_type=RuleType.BETA,
        premises=[RulePattern("T", "A ⊕ B")],
        conclusions=[["T:A", "F:B"], ["F:A", "T:B"]],
        priority=2
    ))
    
    # F-XOR rule (branching)
    self.add_rule(TableauRule(
        name="F-XOR",
        rule_type=RuleType.BETA,
        premises=[RulePattern("F", "A ⊕ B")],
        conclusions=[["T:A", "T:B"], ["F:A", "F:B"]],
        priority=2
    ))
```

### Adding New Signs

For multi-valued logic extensions:

```python
# Add new sign to sign system
class ExtendedSign(Sign):
    def __init__(self, symbol: str):
        if symbol not in ["T", "F", "U", "X"]:  # Added X
            raise ValueError(f"Invalid sign: {symbol}")
        self.symbol = symbol
    
    # ... implement required methods

# Update sign system
class ExtendedSignSystem(SignSystem):
    def __init__(self):
        self.t_sign = ExtendedSign("T")
        self.f_sign = ExtendedSign("F")
        self.u_sign = ExtendedSign("U")
        self.x_sign = ExtendedSign("X")  # New sign
    
    def signs(self) -> Set[Sign]:
        return {self.t_sign, self.f_sign, self.u_sign, self.x_sign}

# Add corresponding tableau rules for the new sign
```

## Performance Optimization

### Rule Priority Optimization

```python
# Use priority to optimize tableau construction
self.add_rule(TableauRule(
    name="High-Priority-Rule",
    rule_type=RuleType.ALPHA,  # Non-branching rules have higher priority
    premises=[RulePattern("T", "A & B")],
    conclusions=[["T:A", "T:B"]],
    priority=1  # Higher priority = applied first
))

self.add_rule(TableauRule(
    name="Lower-Priority-Rule",
    rule_type=RuleType.BETA,  # Branching rules have lower priority
    premises=[RulePattern("T", "A | B")],
    conclusions=[["T:A"], ["T:B"]],
    priority=2  # Lower priority = applied later
))
```

### Truth Value System Optimization

```python
# Cache expensive operations
class OptimizedTruthSystem(TruthValueSystem):
    def __init__(self):
        super().__init__()
        self._operation_cache = {}
    
    def evaluate_complex_operation(self, left, right):
        # Use caching for expensive operations
        key = (left, right, "complex_op")
        if key not in self._operation_cache:
            result = self._compute_complex_operation(left, right)
            self._operation_cache[key] = result
        return self._operation_cache[key]
```

### Memory Optimization

```python
# Use __slots__ for memory efficiency in frequently created objects
class OptimizedTruthValue(TruthValue):
    __slots__ = ['name', 'value']
    
    def __init__(self, name: str, value: float):
        self.name = name
        self.value = value

# Share common objects
class OptimizedTruthSystem(TruthValueSystem):
    def __init__(self):
        # Create singletons
        self._true = OptimizedTruthValue("T", 1.0)
        self._false = OptimizedTruthValue("F", 0.0)
    
    @property
    def true(self):
        return self._true  # Always return same object
```

## Testing Your Extensions

### Unit Tests

Create comprehensive tests for your logic system:

```python
# tests/test_lukasiewicz.py
import pytest
from tableaux.logics.lukasiewicz import LukasiewiczLogic, add_lukasiewicz_to_api
from tableaux import LogicSystem

class TestLukasiewiczLogic:
    
    def setup_method(self):
        """Set up test environment."""
        add_lukasiewicz_to_api()
        self.lukasiewicz = LogicSystem.lukasiewicz()
        self.p, self.q = self.lukasiewicz.atoms('p', 'q')
    
    def test_three_valued_behavior(self):
        """Test that atoms can take three values."""
        p = self.lukasiewicz.atom('p')
        
        # Test all three signs
        for sign in ['T', 'F', 'H']:
            result = self.lukasiewicz.solve(p, sign)
            assert result.satisfiable, f"Atom should be satisfiable with sign {sign}"
    
    def test_lukasiewicz_implication(self):
        """Test Łukasiewicz implication semantics."""
        # p -> p should be tautology
        formula = self.p.implies(self.p)
        result = self.lukasiewicz.solve(formula, 'F')
        assert not result.satisfiable, "p -> p should not be falsifiable"
        
        # Test specific Łukasiewicz behavior
        formula = self.p.implies(self.q)
        result = self.lukasiewicz.solve(formula)
        assert result.satisfiable
        assert len(result.models) > 0
    
    def test_comparison_with_classical(self):
        """Compare with classical logic behavior."""
        classical = LogicSystem.classical()
        p_classical, q_classical = classical.atoms('p', 'q')
        
        # Test formula that behaves differently
        formula = "p | ~p"
        
        classical_result = classical.solve(classical.parse(formula), 'F')
        lukasiewicz_result = self.lukasiewicz.solve(
            self.lukasiewicz.parse(formula), 'F'
        )
        
        # Should behave differently for excluded middle
        assert classical_result.satisfiable != lukasiewicz_result.satisfiable
    
    def test_tableau_rules(self):
        """Test that tableau rules work correctly."""
        # Test conjunction rule
        formula = self.p & self.q
        result = self.lukasiewicz.solve(formula)
        assert result.satisfiable
        
        # Verify model has both p and q true
        if result.models:
            model = result.models[0]
            model_str = str(model)
            # Implementation-specific model format checking
            assert 'p' in model_str and 'q' in model_str
    
    def test_cli_integration(self):
        """Test CLI integration works."""
        # This would be an integration test
        import subprocess
        result = subprocess.run(
            ['python', '-m', 'tableaux.extensible_cli', 
             '--logic=lukasiewicz', '--list-logics'],
            capture_output=True, text=True
        )
        assert 'lukasiewicz' in result.stdout
```

### Integration Tests

```python
# tests/test_integration.py
def test_all_logic_systems():
    """Test that all logic systems work consistently."""
    systems = [
        ("classical", LogicSystem.classical()),
        ("weak_kleene", LogicSystem.weak_kleene()),
        ("wkrq", LogicSystem.wkrq()),
        ("lukasiewicz", LogicSystem.lukasiewicz()),  # Your new system
    ]
    
    for name, system in systems:
        # Test basic functionality
        p = system.atom('p')
        result = system.solve(p)
        assert result.satisfiable, f"{name} should support basic atoms"
        
        # Test parser integration
        parsed = system.parse("p & q")
        result = system.solve(parsed)
        assert result.satisfiable, f"{name} should support conjunction"
```

### Performance Tests

```python
def test_performance():
    """Test performance of new logic system."""
    import time
    
    lukasiewicz = LogicSystem.lukasiewicz()
    atoms = lukasiewicz.atoms(*[f'p{i}' for i in range(10)])
    
    # Build complex formula
    formula = atoms[0]
    for atom in atoms[1:]:
        formula = formula | atom
    
    start_time = time.time()
    result = lukasiewicz.solve(formula)
    end_time = time.time()
    
    assert result.satisfiable
    assert end_time - start_time < 1.0, "Should complete within 1 second"
```

## Common Patterns and Best Practices

### Logic System Patterns

1. **Always use self-contained definitions**: Everything about your logic in one file
2. **Follow naming conventions**: `MyLogic` class, `my_logic` registry name
3. **Implement all required methods**: Don't leave abstract methods unimplemented
4. **Use meaningful rule names**: "T-Conjunction", "F-Disjunction-Lukasiewicz"

### Truth Value System Patterns

```python
# Good: Clear value representation
class MyTruthValue(TruthValue):
    def __init__(self, name: str, numeric_value: float):
        self.name = name
        self.value = numeric_value
    
    def __str__(self):
        return self.name  # Human-readable
    
    def __repr__(self):
        return f"MyTruthValue({self.name})"  # Debug-friendly

# Good: Efficient operations
class MyTruthSystem(TruthValueSystem):
    def evaluate_conjunction(self, left, right):
        # Use numeric values for efficiency
        result_value = min(left.value, right.value)
        return self._value_to_truth_value(result_value)
```

### Rule Definition Patterns

```python
# Good: Clear rule structure
def _add_conjunction_rules(self):
    """Add all conjunction rules for this logic."""
    
    # Group related rules together
    # T-Conjunction (non-branching)
    self.add_rule(TableauRule(
        name="T-Conjunction",
        rule_type=RuleType.ALPHA,
        premises=[RulePattern("T", "A & B")],
        conclusions=[["T:A", "T:B"]],
        priority=1
    ))
    
    # F-Conjunction (branching)
    self.add_rule(TableauRule(
        name="F-Conjunction",
        rule_type=RuleType.BETA,
        premises=[RulePattern("F", "A & B")],
        conclusions=[["F:A"], ["F:B"]],
        priority=2
    ))

# Good: Systematic rule coverage
def _define_tableau_rules(self):
    """Define complete rule system."""
    self._add_conjunction_rules()
    self._add_disjunction_rules()
    self._add_negation_rules()
    self._add_implication_rules()
    # Add any logic-specific rules
    self._add_special_rules()
```

### Error Handling Patterns

```python
# Good: Comprehensive validation
class MyLogic(LogicSystem):
    def initialize(self):
        try:
            self._define_connectives()
            self.set_truth_system(MyTruthSystem())
            self.set_sign_system(MySignSystem())
            self._define_tableau_rules()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize {self.__class__.__name__}: {e}")
    
    def _validate_configuration(self):
        """Validate that the logic system is properly configured."""
        if not self.connectives:
            raise ValueError("No connectives defined")
        if not self.truth_system:
            raise ValueError("No truth system defined")
        if not self.sign_system:
            raise ValueError("No sign system defined")
        if not self.rules:
            raise ValueError("No tableau rules defined")
```

## Troubleshooting

### Common Issues

**1. Logic System Not Recognized**
```python
# Problem: Logic not registered
LogicRegistry.register(MyLogic("my_logic"))  # Must call this

# Problem: Wrong name used
tableaux --logic=mylogic "p"  # Should be --logic=my_logic
```

**2. Rule Pattern Matching Failures**
```python
# Problem: Incorrect pattern syntax
RulePattern("T", "A & B")     # Correct
RulePattern("T", "A and B")   # Wrong - use & not 'and'
```

**3. Truth Value System Errors**
```python
# Problem: Missing required methods
class IncompleteTruthSystem(TruthValueSystem):
    # Must implement ALL abstract methods
    def truth_values(self): return {...}
    def designated_values(self): return {...}
    def evaluate_negation(self, value): return ...
    # etc.
```

**4. Sign System Issues**
```python
# Problem: Inconsistent sign definitions
def is_contradictory_with(self, other):
    # Must be symmetric: if A contradicts B, then B contradicts A
    return (self.symbol == "T" and other.symbol == "F") or \
           (self.symbol == "F" and other.symbol == "T")
```

### Debugging Techniques

**1. Test Step by Step**
```python
# Test each component individually
truth_system = MyTruthSystem()
assert len(truth_system.truth_values()) > 0

sign_system = MySignSystem()
assert len(sign_system.signs()) > 0

logic = MyLogic("test")
logic.initialize()
assert len(logic.rules) > 0
```

**2. Use Debug Output**
```bash
# CLI debugging
tableaux --logic=my_logic --debug "p & q"

# Look for rule application issues
```

**3. Compare with Working Logic**
```python
# Compare behavior with known-good logic
classical = LogicSystem.classical()
my_logic = LogicSystem.my_logic()

test_formula = "p -> p"
classical_result = classical.solve(classical.parse(test_formula))
my_result = my_logic.solve(my_logic.parse(test_formula))

# Both should find this satisfiable
assert classical_result.satisfiable == my_result.satisfiable
```

### Performance Issues

**1. Too Many Rules**
- Ensure rules have appropriate priorities
- Use ALPHA rules for non-branching operations
- Use BETA rules for branching operations

**2. Expensive Truth Value Operations**
- Cache expensive computations
- Use numeric representations when possible
- Avoid creating new objects in hot paths

**3. Memory Usage**
- Use `__slots__` in frequently created objects
- Share common truth value objects
- Profile memory usage with complex formulas

### Getting Help

1. **Check existing logic systems** in `src/tableaux/logics/` for patterns
2. **Run the test suite** to ensure you haven't broken existing functionality
3. **Use the debug CLI** to trace tableau construction
4. **Read the architecture documentation** for deeper understanding

## Conclusion

The plugin architecture makes extending the tableau system natural and maintainable. By following the patterns established in existing logic systems and adhering to the principle of unified logic definitions, you can add new logical systems that integrate seamlessly with the existing framework.

Key takeaways:
- **Self-contained definitions** make logic systems easy to understand and modify
- **Consistent patterns** across all components ensure reliable behavior
- **Comprehensive testing** validates correctness and performance
- **Plugin registration** enables automatic CLI and API integration

The system's design reflects the philosophical insight that logic systems should be treated as unified wholes, making it a natural platform for exploring automated reasoning across diverse logical frameworks.