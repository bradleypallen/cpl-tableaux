# Building with the Tableau System: Developer's Guide

**Version**: 4.0 (Unified Architecture)  
**Last Updated**: July 2025  
**License**: MIT  

## Table of Contents

1. [Introduction](#introduction)
2. [Understanding the Current Architecture](#understanding-the-current-architecture)
3. [Extending the System](#extending-the-system)
4. [Building New Logic Systems](#building-new-logic-systems)
5. [Performance Optimization](#performance-optimization)
6. [Testing Your Extensions](#testing-your-extensions)
7. [Common Patterns and Best Practices](#common-patterns-and-best-practices)
8. [Troubleshooting](#troubleshooting)

## Introduction

This guide teaches you how to extend and build upon the unified tableau system implemented in `tableau_core.py`. The system currently supports classical propositional logic, three-valued Weak Kleene logic (WK3), and Ferguson's four-valued epistemic logic (wKrQ).

### Who This Guide Is For

- **Researchers** implementing new logical systems
- **Developers** extending the existing implementation
- **Students** learning how tableau systems work
- **Contributors** adding features to the project

### Prerequisites

- Understanding of the existing codebase (see ARCHITECTURE.md)
- Python programming experience
- Basic knowledge of logic and tableau methods
- Familiarity with the current API (see API_REFERENCE.md)

## Understanding the Current Architecture

The entire tableau system is implemented in a single unified module: `tableau_core.py`. This consolidated approach provides:

### Core Components

1. **Formula Representation**
```python
from tableau_core import Atom, Negation, Conjunction, Disjunction, Implication

# Build formulas
p = Atom("p")
q = Atom("q")
formula = Implication(p, q)  # p → q
```

2. **Sign Systems**
```python
from tableau_core import T, F, T3, F3, U, TF, FF, M, N

# Classical signs
signed_true = T(formula)   # T:p → q
signed_false = F(formula)  # F:p → q

# Three-valued signs
t3_signed = T3(formula)    # T₃:p → q
u_signed = U(formula)      # U:p → q

# Epistemic signs
may_be_true = M(formula)   # M:p → q
need_not_true = N(formula) # N:p → q
```

3. **Tableau Functions**
```python
from tableau_core import (
    classical_signed_tableau,
    three_valued_signed_tableau,
    wkrq_signed_tableau,
    ferguson_signed_tableau
)

# Create and build tableaux
tableau = classical_signed_tableau(T(formula))
is_satisfiable = tableau.build()
models = tableau.extract_all_models()
```

## Extending the System

### Adding New Operators

To add a new logical operator, extend the `Formula` base class:

```python
# In tableau_core.py, add your new operator
class Biconditional(Formula):
    """Biconditional operator (if and only if)."""
    
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
        self._cached_hash = None
        self._cached_str = None
        
    def __str__(self) -> str:
        if self._cached_str is None:
            self._cached_str = f"({self.left} ↔ {self.right})"
        return self._cached_str
        
    def __eq__(self, other) -> bool:
        return (isinstance(other, Biconditional) and 
                self.left == other.left and 
                self.right == other.right)
                
    def __hash__(self) -> int:
        if self._cached_hash is None:
            self._cached_hash = hash(("BICONDITIONAL", hash(self.left), hash(self.right)))
        return self._cached_hash
        
    def is_atomic(self) -> bool:
        return False
```

Then add tableau rules for the new operator in the `OptimizedTableauEngine._initialize_tableau_rules()` method:

```python
# Add to the classical rules section
if self.sign_system == "classical":
    # Existing rules...
    
    # Add biconditional rules
    rules['T_biconditional'] = TableauRule(
        rule_type="beta",
        premises=[SignedFormula(T, Biconditional)],
        conclusions=[
            [SignedFormula(T, "left"), SignedFormula(T, "right")],
            [SignedFormula(F, "left"), SignedFormula(F, "right")]
        ],
        priority=3,
        name="T-Biconditional (β)"
    )
    
    rules['F_biconditional'] = TableauRule(
        rule_type="beta", 
        premises=[SignedFormula(F, Biconditional)],
        conclusions=[
            [SignedFormula(T, "left"), SignedFormula(F, "right")],
            [SignedFormula(F, "left"), SignedFormula(T, "right")]
        ],
        priority=3,
        name="F-Biconditional (β)"
    )
```

### Adding New Truth Values

To support a logic with different truth values, extend the `TruthValue` enum:

```python
# Add to the TruthValue enum
class TruthValue(Enum):
    TRUE = "t"
    FALSE = "f"
    ERROR = "e"
    # Add new truth value
    BOTH = "b"  # For paraconsistent logic
    
# Create a constant for easy access
b = TruthValue.BOTH
```

## Building New Logic Systems

### Example: Four-Valued Logic (FDE)

Here's how to add Belnap's four-valued logic (First Degree Entailment):

1. **Define the Sign System**
```python
class FDESign(Sign):
    """Four-valued FDE signs: T, F, B (both), N (neither)."""
    
    def __init__(self, designation: str):
        if designation not in ["T", "F", "B", "N"]:
            raise ValueError(f"Invalid FDE sign: {designation}")
        self.designation = designation
        
    def __str__(self) -> str:
        return f"{self.designation}"
        
    def is_contradictory_with(self, other: 'Sign') -> bool:
        # In FDE, no signs are contradictory!
        return False

# Convenience constructors
def TB(formula): return SignedFormula(FDESign("T"), formula)
def FB(formula): return SignedFormula(FDESign("F"), formula)
def B(formula): return SignedFormula(FDESign("B"), formula)
def N(formula): return SignedFormula(FDESign("N"), formula)
```

2. **Add Tableau Rules**
```python
def fde_signed_tableau(signed_formula, track_steps=False):
    """Create an FDE tableau."""
    return OptimizedTableauEngine(
        initial_formulas=[signed_formula],
        sign_system="fde",
        track_steps=track_steps
    )

# In _initialize_tableau_rules(), add:
elif self.sign_system == "fde":
    rules = {}
    
    # FDE conjunction rules
    rules['T_conjunction'] = TableauRule(
        rule_type="alpha",
        premises=[SignedFormula(FDESign("T"), Conjunction)],
        conclusions=[[
            SignedFormula(FDESign("T"), "left"),
            SignedFormula(FDESign("T"), "right")
        ]],
        priority=1,
        name="T-Conjunction (α)"
    )
    
    # ... add all other FDE rules
```

3. **Add Model Extraction**
```python
class FDEModel(UnifiedModel):
    """Model for four-valued FDE logic."""
    
    def __init__(self, assignments: Dict[str, str]):
        # assignments map atoms to "T", "F", "B", or "N"
        self._assignments = assignments
        
    def satisfies(self, formula: Formula) -> str:
        """Evaluate formula in FDE semantics."""
        # Implement FDE truth tables
        pass
```

## Performance Optimization

### 1. Rule Prioritization

The system already implements α/β prioritization. Maintain this pattern:

```python
# α-rules (non-branching) get priority 1
# β-rules (branching) get priority 2-3
# Complex rules get higher priority numbers

rules['double_negation'] = TableauRule(
    rule_type="alpha",
    premises=[SignedFormula(T, Negation(Negation))],
    conclusions=[[SignedFormula(T, "subformula.subformula")]],
    priority=0,  # Highest priority - simplifies immediately
    name="Double Negation (α)"
)
```

### 2. Formula Caching

The system uses extensive caching. Follow this pattern in new formula types:

```python
class NewOperator(Formula):
    def __init__(self, ...):
        # Your initialization
        self._cached_hash = None
        self._cached_str = None
        
    def __str__(self) -> str:
        if self._cached_str is None:
            self._cached_str = self._compute_string()
        return self._cached_str
```

### 3. Early Termination

The system checks for closure after each rule application. Ensure your rules maintain this property.

## Testing Your Extensions

### 1. Add Unit Tests

Add tests to `test_comprehensive.py`:

```python
def test_biconditional_operator():
    """Test the new biconditional operator."""
    p = Atom("p")
    q = Atom("q")
    
    # Test T:(p ↔ q) with p true, q true
    bicon = Biconditional(p, q)
    tableau = classical_signed_tableau(T(bicon))
    assert tableau.build()
    
    models = tableau.extract_all_models()
    # Should have models where p,q have same truth value
    assert len(models) == 2
```

### 2. Add Literature Examples

Add validation against known results to `test_literature_examples.py`:

```python
def test_fde_paradoxes():
    """Test that FDE handles paradoxes without explosion."""
    p = Atom("p")
    
    # Liar paradox: p ↔ ¬p
    liar = Biconditional(p, Negation(p))
    
    # In classical logic, this is unsatisfiable
    classical_tableau = classical_signed_tableau(T(liar))
    assert not classical_tableau.build()
    
    # In FDE, this should be satisfiable (p = B or p = N)
    fde_tableau = fde_signed_tableau(TB(liar))
    assert fde_tableau.build()
```

### 3. Performance Testing

Add benchmarks to `test_performance.py`:

```python
def test_new_operator_performance():
    """Benchmark the new operator."""
    import time
    
    # Generate a complex formula
    atoms = [Atom(f"p{i}") for i in range(10)]
    formula = create_complex_formula_with_new_operator(atoms)
    
    start = time.time()
    tableau = classical_signed_tableau(T(formula))
    tableau.build()
    end = time.time()
    
    assert end - start < 0.1  # Should be fast
```

## Common Patterns and Best Practices

### 1. Sign Compatibility

When adding new sign systems, ensure they interact properly with the `is_contradictory_with` method:

```python
def is_contradictory_with(self, other: 'Sign') -> bool:
    if not isinstance(other, MyNewSign):
        return False
    # Define your contradiction rules
    return self.value == "T" and other.value == "F"
```

### 2. Formula Decomposition

Follow the pattern of accessing subformulas through attributes:

```python
# In tableau rules, reference subformulas like:
conclusions=[[
    SignedFormula(T, "left"),    # Accesses formula.left
    SignedFormula(F, "right.subformula")  # Accesses formula.right.subformula
]]
```

### 3. Model Extraction

Ensure your model extraction handles all cases:

```python
def _extract_my_logic_model(self, branch):
    """Extract model from an open branch."""
    assignments = {}
    
    # Collect all assignments from signed formulas
    for sf in branch.signed_formulas:
        if isinstance(sf.formula, Atom):
            # Handle your sign system's semantics
            pass
            
    # Handle unassigned atoms according to your logic's semantics
    all_atoms = branch.collect_atoms()
    for atom in all_atoms:
        if atom.name not in assignments:
            # Your logic's default value
            assignments[atom.name] = "default"
            
    return MyLogicModel(assignments)
```

## Troubleshooting

### Common Issues

1. **Infinite Loops**
   - Ensure your rules don't regenerate the same formulas
   - Check that complex formulas eventually decompose to atoms
   - Verify termination conditions

2. **Missing Models**
   - Check that model extraction covers all truth value combinations
   - Ensure your `is_contradictory_with` is correct
   - Verify that branches aren't closing prematurely

3. **Performance Problems**
   - Profile your rules to find bottlenecks
   - Ensure proper formula caching
   - Check rule priorities

### Debugging Techniques

1. **Enable Step Tracking**
```python
tableau = classical_signed_tableau(T(formula), track_steps=True)
tableau.build()
tableau.print_construction_steps()
```

2. **Print Branch States**
```python
for i, branch in enumerate(tableau.branches):
    print(f"Branch {i}: {len(branch.signed_formulas)} formulas")
    print(f"  Closed: {branch.is_closed}")
    if branch.is_closed:
        print(f"  Reason: {branch.closure_reason}")
```

3. **Trace Rule Applications**
```python
# Add logging to your rules
print(f"Applying {rule.name} to {signed_formula}")
```

## Example: Complete Implementation of XOR Operator

Here's a complete example of adding an XOR (exclusive or) operator:

```python
# 1. Add to tableau_core.py - Formula class
class ExclusiveOr(Formula):
    """Exclusive OR operator (XOR)."""
    
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
        self._cached_hash = None
        self._cached_str = None
        
    def __str__(self) -> str:
        if self._cached_str is None:
            self._cached_str = f"({self.left} ⊕ {self.right})"
        return self._cached_str
        
    def __eq__(self, other) -> bool:
        return (isinstance(other, ExclusiveOr) and 
                self.left == other.left and 
                self.right == other.right)
                
    def __hash__(self) -> int:
        if self._cached_hash is None:
            self._cached_hash = hash(("XOR", hash(self.left), hash(self.right)))
        return self._cached_hash
        
    def is_atomic(self) -> bool:
        return False

# 2. Add to _initialize_tableau_rules() in OptimizedTableauEngine
# Under classical rules section:
rules['T_xor'] = TableauRule(
    rule_type="beta",
    premises=[SignedFormula(T, ExclusiveOr)],
    conclusions=[
        [SignedFormula(T, "left"), SignedFormula(F, "right")],
        [SignedFormula(F, "left"), SignedFormula(T, "right")]
    ],
    priority=2,
    name="T-XOR (β)"
)

rules['F_xor'] = TableauRule(
    rule_type="beta",
    premises=[SignedFormula(F, ExclusiveOr)],
    conclusions=[
        [SignedFormula(T, "left"), SignedFormula(T, "right")],
        [SignedFormula(F, "left"), SignedFormula(F, "right")]
    ],
    priority=2,
    name="F-XOR (β)"
)

# 3. Add tests
def test_xor_operator():
    """Test exclusive OR operator."""
    p = Atom("p")
    q = Atom("q")
    
    # p ⊕ q should be satisfied by (p=T,q=F) or (p=F,q=T)
    xor_formula = ExclusiveOr(p, q)
    tableau = classical_signed_tableau(T(xor_formula))
    assert tableau.build()
    
    models = tableau.extract_all_models()
    assert len(models) == 2
    
    # Check the models
    model_assignments = [
        {k: v.value for k, v in model._assignments.items()}
        for model in models
    ]
    
    assert {"p": "t", "q": "f"} in model_assignments
    assert {"p": "f", "q": "t"} in model_assignments

# 4. Usage example
from tableau_core import Atom, ExclusiveOr, T, classical_signed_tableau

p = Atom("p")
q = Atom("q")
formula = ExclusiveOr(p, q)  # p ⊕ q

tableau = classical_signed_tableau(T(formula))
if tableau.build():
    print("Formula is satisfiable")
    for model in tableau.extract_all_models():
        print(f"Model: {model}")
```

## Conclusion

The unified tableau system in `tableau_core.py` provides a solid foundation for implementing new logical systems. By following the patterns established in the codebase and the guidelines in this document, you can extend the system with new operators, truth values, and even entirely new logics while maintaining performance and correctness.

Remember to:
- Follow the established patterns for formulas, signs, and rules
- Add comprehensive tests for your extensions
- Document your implementation choices
- Maintain the performance optimizations already in place

For more details on the existing implementation, see:
- **ARCHITECTURE.md** - System architecture details
- **API_REFERENCE.md** - Complete API documentation
- **TUTORIALS.md** - Usage examples and patterns