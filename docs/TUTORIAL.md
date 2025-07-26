# Tableau System Tutorial

This tutorial provides a complete guide to using the tableau system for automated reasoning across multiple logic systems, and shows you how to build your own logic system plugin.

**Target Audience:** Researchers and practitioners working with automated reasoning and non-classical logics  
**Prerequisites:** Basic familiarity with propositional logic and tableau methods

## Table of Contents

1. [Getting Started](#getting-started)
2. [Command Line Interface](#command-line-interface)  
3. [Python API](#python-api)
4. [Working with Different Logic Systems](#working-with-different-logic-systems)
5. [Building Your Own Logic System](#building-your-own-logic-system)
6. [Advanced Usage](#advanced-usage)

## Getting Started

The tableau system supports multiple logic systems through a unified interface. Install and verify:

```bash
pip install tableaux
tableaux --help
```

### Quick Test

```bash
# Test a classical tautology
tableaux "p | ~p"

# Test with different logic systems
tableaux --logic=weak_kleene "p | ~p" 
tableaux --logic=wkrq "p & ~p"
```

## Command Line Interface

The CLI provides immediate access to all logic systems with a consistent interface.

### Basic Usage

**Test satisfiability:**
```bash
tableaux "p -> q"                    # Classical logic (default)
tableaux --logic=weak_kleene "p | ~p"  # Three-valued logic
tableaux --logic=wkrq "p & ~p"         # Four-valued logic
```

**Show all models:**
```bash
tableaux --models "p -> q"
tableaux --logic=weak_kleene --models "p | ~p"
```

**Test with specific signs:**
```bash
tableaux --sign=F "p | ~p"              # Can excluded middle be false?
tableaux --logic=weak_kleene --sign=U "p"  # Can p be undefined?
tableaux --logic=wkrq --sign=M "p"         # Can p be both true and false?
```

### Available Logic Systems

```bash
tableaux --list-logics
```

Shows:
- **classical**: Two-valued classical logic (T, F)
- **weak_kleene**: Three-valued weak Kleene logic (T, F, U)  
- **wkrq**: Four-valued wKrQ epistemic logic (T, F, M, N)

### Interactive Mode

```bash
tableaux
```

Starts an interactive session:
```
tableau[classical]> p -> q
tableau[classical]> models
tableau[classical]> logic weak_kleene
tableau[weak_kleene]> p | ~p
tableau[weak_kleene]> sign U
tableau[weak_kleene]> test p
tableau[weak_kleene]> help
tableau[weak_kleene]> quit
```

### Advanced CLI Features

**Debug mode:**
```bash
tableaux --debug "complex_formula"      # Show tableau construction steps
```

**JSON output:**
```bash
tableaux --format=json "p & q"         # Machine-readable output
```

**Statistics:**
```bash
tableaux --stats "complex_formula"     # Show performance metrics
```

## Python API

The Python API provides full programmatic access with natural syntax.

### Basic Usage

```python
from tableaux import LogicSystem

# Create a logic system
classical = LogicSystem.classical()

# Create atomic formulas
p, q, r = classical.atoms('p', 'q', 'r')

# Build complex formulas
conjunction = p & q
disjunction = p | q  
negation = ~p
implication = p.implies(q)    # Use .implies() method for implication
complex_formula = (p & q).implies(~r | q)

# Test satisfiability
result = classical.solve(complex_formula)
print(f"Satisfiable: {result.satisfiable}")
print(f"Models: {result.models}")
```

### Working with Results

```python
formula = p.implies(q)
result = classical.solve(formula)

# Basic properties
print(f"Satisfiable: {result.satisfiable}")
print(f"Number of models: {len(result.models)}")

# Access models
if result.models:
    print("All models:")
    for i, model in enumerate(result.models, 1):
        print(f"  Model {i}: {model}")
```

### Testing Validity and Entailment

```python
# Test argument validity
premises = [classical.parse("p -> q"), p]  # Use parser for string formulas
conclusion = q

is_valid = classical.entails(premises, conclusion)
print(f"Modus ponens is valid: {is_valid}")

# Test with counterexamples
if not is_valid:
    # Create formula: premises true, conclusion false
    combined = premises[0] & premises[1] & (~conclusion)
    counter_result = classical.solve(combined)
    if counter_result.satisfiable:
        print(f"Counterexample: {counter_result.models[0]}")
```

### Parsing String Formulas

```python
# Mix programmatic and parsed formulas
programmatic = p & q
parsed = classical.parse("r -> s")
combined = programmatic | parsed

result = classical.solve(combined)
print(f"Combined formula: {result.satisfiable}")
```

**Important:** Use different syntax for different contexts:
- **Python API**: Use `.implies()` method: `p.implies(q)`
- **String parsing**: Use `->` operator: `"p -> q"`
- **Command line**: Use `->` operator: `tableaux "p -> q"`

## Working with Different Logic Systems

Each logic system uses the same API but with different semantic behavior.

### Classical Logic

```python
classical = LogicSystem.classical()
p = classical.atom('p')

# Classical contradiction is unsatisfiable
contradiction = p & ~p
result = classical.solve(contradiction)
print(f"p & ~p satisfiable: {result.satisfiable}")  # False

# Classical excluded middle is a tautology
excluded_middle = p | ~p
result = classical.solve(excluded_middle, 'F')  # Can it be false?
print(f"p | ~p can be false: {result.satisfiable}")  # False
```

### Weak Kleene Logic (Three-Valued)

```python
weak_kleene = LogicSystem.weak_kleene()
p = weak_kleene.atom('p')

# Excluded middle can fail (be undefined)
excluded_middle = p | ~p
result = weak_kleene.solve(excluded_middle, 'U')  # Test for undefined
print(f"p | ~p can be undefined: {result.satisfiable}")  # True

# Show all three possible values for p
for sign in ['T', 'F', 'U']:
    result = weak_kleene.solve(p, sign)
    print(f"p can be {sign}: {result.satisfiable}")
```

### wKrQ Logic (Four-Valued)

```python
wkrq = LogicSystem.wkrq()
p = wkrq.atom('p')

# Test all four values
signs = ['T', 'F', 'M', 'N']  # True, False, Both, Neither
for sign in signs:
    result = wkrq.solve(p, sign)
    print(f"p can be {sign}: {result.satisfiable}")

# Contradiction can be satisfiable (paraconsistent)
contradiction = p & ~p
result = wkrq.solve(contradiction, 'M')  # Test for "both"
print(f"p & ~p can be both true and false: {result.satisfiable}")  # True
```

### FDE Logic (Paraconsistent)

```python
# FDE requires registration
from tableaux.logics.fde import add_fde_to_api
add_fde_to_api()

fde = LogicSystem.fde()
p, q = fde.atoms('p', 'q')

# FDE has no implication - only &, |, ~
formula = (p & ~q) | (~p & q)  # XOR pattern
result = fde.solve(formula)
print(f"XOR pattern: {len(result.models)} models")

# Contradictions are satisfiable (paraconsistent)
contradiction = p & ~p
result = fde.solve(contradiction, 'B')  # "Both" true and false
print(f"p & ~p can be both: {result.satisfiable}")  # True

# Test explosion principle
premises = [p & ~p]
conclusion = q
explodes = fde.entails(premises, conclusion)
print(f"Does contradiction entail q? {explodes}")  # False (no explosion)
```

### Comparing Logic Systems

```python
# Test the same formula across different systems
formula_str = "p & ~p"

systems = [
    ("Classical", LogicSystem.classical()),
    ("Weak Kleene", LogicSystem.weak_kleene()),
    ("wKrQ", LogicSystem.wkrq()),
    ("FDE", LogicSystem.fde())  # Assumes FDE is registered
]

for name, system in systems:
    formula = system.parse(formula_str)
    result = system.solve(formula)
    print(f"{name:12}: {len(result.models)} models")
```

## Building Your Own Logic System

The unified architecture makes it natural to define new logic systems. Each logic is completely self-contained in one file.

### Step 1: Define the Logic Class

Create `my_logic.py`:

```python
from tableaux.logics.logic_system import LogicSystem
from tableaux.core.formula import ConnectiveSpec
from tableaux.core.semantics import TruthValueSystem, TruthValue
from tableaux.core.signs import SignSystem, Sign
from tableaux.core.rules import TableauRule, RuleType, RulePattern
from typing import Set, Optional, Callable

class MyLogic(LogicSystem):
    """Complete definition of my custom logic system."""
    
    def initialize(self):
        """Initialize the logic system."""
        # 1. Define syntax (connectives and precedence)
        self._define_syntax()
        
        # 2. Define semantics (truth values)
        self._define_semantics()
        
        # 3. Define tableau rules
        self._define_tableau_rules()
    
    def _define_syntax(self):
        """Define the connectives and their properties."""
        # Standard connectives with precedence levels
        self.add_connective(ConnectiveSpec("&", 2, 3, "left", "infix"))   # conjunction
        self.add_connective(ConnectiveSpec("|", 2, 2, "left", "infix"))   # disjunction  
        self.add_connective(ConnectiveSpec("~", 1, 4, "none", "prefix"))  # negation
        self.add_connective(ConnectiveSpec("->", 2, 1, "right", "infix"))  # implication
        
        # Custom connectives (example: strong disjunction)
        self.add_connective(ConnectiveSpec("⊕", 2, 2, "left", "infix"))   # XOR
    
    def _define_semantics(self):
        """Define truth values and semantic operations."""
        self.set_truth_system(MyTruthSystem())
        self.set_sign_system(MySignSystem())
    
    def _define_tableau_rules(self):
        """Define all tableau rules for this logic."""
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
        
        # Add more rules for |, ~, ->, ⊕...
```

### Step 2: Define Truth Value System

```python
class MyTruthValue(TruthValue):
    """Custom truth values."""
    
    def __init__(self, name: str):
        self.name = name
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        return isinstance(other, MyTruthValue) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(self.name)


class MyTruthSystem(TruthValueSystem):
    """Custom truth value system."""
    
    def __init__(self):
        # Define your truth values
        self.true = MyTruthValue("T")
        self.false = MyTruthValue("F")
        self.unknown = MyTruthValue("U")
        # Add more as needed...
    
    def truth_values(self) -> Set[TruthValue]:
        """Return all truth values."""
        return {self.true, self.false, self.unknown}
    
    def designated_values(self) -> Set[TruthValue]:
        """Values that count as 'true'."""
        return {self.true}
    
    def evaluate_negation(self, value: TruthValue) -> TruthValue:
        """Define negation operation."""
        if value == self.true:
            return self.false
        elif value == self.false:
            return self.true
        elif value == self.unknown:
            return self.unknown
        else:
            raise ValueError(f"Unknown truth value: {value}")
    
    def evaluate_conjunction(self, left: TruthValue, right: TruthValue) -> TruthValue:
        """Define conjunction operation."""
        # Implement your conjunction logic
        if left == self.true and right == self.true:
            return self.true
        elif left == self.false or right == self.false:
            return self.false
        else:
            return self.unknown
    
    def evaluate_disjunction(self, left: TruthValue, right: TruthValue) -> TruthValue:
        """Define disjunction operation."""
        # Implement your disjunction logic
        if left == self.true or right == self.true:
            return self.true
        elif left == self.false and right == self.false:
            return self.false
        else:
            return self.unknown
    
    def name(self) -> str:
        return "MyLogic"
```

### Step 3: Define Sign System

```python
class MySign(Sign):
    """Custom signs for tableau system."""
    
    def __init__(self, symbol: str):
        if symbol not in ["T", "F", "U"]:  # Your valid signs
            raise ValueError(f"Invalid sign: {symbol}")
        self.symbol = symbol
    
    def __str__(self) -> str:
        return self.symbol
    
    def __eq__(self, other) -> bool:
        return isinstance(other, MySign) and self.symbol == other.symbol
    
    def __hash__(self) -> int:
        return hash(("my_logic", self.symbol))
    
    def get_symbol(self) -> str:
        return self.symbol


class MySignSystem(SignSystem):
    """Sign system for tableau construction."""
    
    def __init__(self):
        self.t_sign = MySign("T")
        self.f_sign = MySign("F") 
        self.u_sign = MySign("U")
    
    def signs(self) -> Set[Sign]:
        """Return all signs."""
        return {self.t_sign, self.f_sign, self.u_sign}
    
    def default_sign(self) -> Sign:
        """Default sign for testing satisfiability."""
        return self.t_sign
    
    def name(self) -> str:
        return "MyLogic"
```

### Step 4: Register and Use

```python
# Register your logic system
from tableaux.logics.logic_system import LogicRegistry
from tableaux.api import LogicSystem as APILogicSystem

# Register the logic
LogicRegistry.register(MyLogic("my_logic"))

# Add to API (optional - for LogicSystem.my_logic() syntax)
@classmethod
def my_logic(cls):
    """Create a my_logic system."""
    logic = LogicRegistry.get("my_logic")
    return cls(logic)

APILogicSystem.my_logic = my_logic

# Use your logic
my_system = LogicSystem.my_logic()
p, q = my_system.atoms('p', 'q')
formula = p & (q | ~p)
result = my_system.solve(formula)
print(f"My logic result: {result.satisfiable}")
```

### Step 5: Command Line Integration

Your logic is automatically available via CLI:

```bash
tableaux --logic=my_logic "p & q"
tableaux --logic=my_logic --models "p | ~p"
tableaux --logic=my_logic --sign=U "p"
```

### Complete Example: Łukasiewicz Three-Valued Logic

Here's a complete working example:

```python
# lukasiewicz.py
from tableaux.logics.logic_system import LogicSystem
from tableaux.core.formula import ConnectiveSpec
from tableaux.core.semantics import TruthValueSystem, TruthValue
from tableaux.core.signs import SignSystem, Sign
from tableaux.core.rules import TableauRule, RuleType, RulePattern
from typing import Set

class LukasiewiczTruthValue(TruthValue):
    def __init__(self, name: str, value: float):
        self.name = name
        self.value = value  # 0, 0.5, 1
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        return isinstance(other, LukasiewiczTruthValue) and self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)

class LukasiewiczTruthSystem(TruthValueSystem):
    def __init__(self):
        self.false = LukasiewiczTruthValue("F", 0.0)
        self.half = LukasiewiczTruthValue("H", 0.5)
        self.true = LukasiewiczTruthValue("T", 1.0)
    
    def truth_values(self) -> Set[TruthValue]:
        return {self.false, self.half, self.true}
    
    def designated_values(self) -> Set[TruthValue]:
        return {self.true}  # Only 1 is designated
    
    def evaluate_negation(self, value: TruthValue) -> TruthValue:
        """~x = 1 - x"""
        if value == self.true:
            return self.false
        elif value == self.false:
            return self.true
        else:  # half
            return self.half
    
    def evaluate_conjunction(self, left: TruthValue, right: TruthValue) -> TruthValue:
        """x ∧ y = min(x, y)"""
        min_val = min(left.value, right.value)
        if min_val == 0.0:
            return self.false
        elif min_val == 0.5:
            return self.half
        else:
            return self.true
    
    def evaluate_disjunction(self, left: TruthValue, right: TruthValue) -> TruthValue:
        """x ∨ y = max(x, y)"""
        max_val = max(left.value, right.value)
        if max_val == 1.0:
            return self.true
        elif max_val == 0.5:
            return self.half
        else:
            return self.false
    
    def evaluate_implication(self, left: TruthValue, right: TruthValue) -> TruthValue:
        """x → y = min(1, 1 - x + y)"""
        result_val = min(1.0, 1.0 - left.value + right.value)
        if result_val == 1.0:
            return self.true
        elif result_val == 0.5:
            return self.half
        else:
            return self.false
    
    def name(self) -> str:
        return "Lukasiewicz"

class LukasiewiczLogic(LogicSystem):
    def initialize(self):
        # Define connectives
        self.add_connective(ConnectiveSpec("&", 2, 3, "left", "infix"))
        self.add_connective(ConnectiveSpec("|", 2, 2, "left", "infix"))
        self.add_connective(ConnectiveSpec("~", 1, 4, "none", "prefix"))
        self.add_connective(ConnectiveSpec("->", 2, 1, "right", "infix"))
        
        # Set semantics
        self.set_truth_system(LukasiewiczTruthSystem())
        self.set_sign_system(LukasiewiczSignSystem())
        
        # Add tableau rules (simplified)
        self._add_tableau_rules()
    
    def _add_tableau_rules(self):
        # Add rules for T, F, H signs with Łukasiewicz semantics
        # (Implementation would follow the pattern above)
        pass

# Register and use
LogicRegistry.register(LukasiewiczLogic("lukasiewicz"))
```

### Complete Extension Example: FDE Logic

The system includes a complete implementation of FDE (First-Degree Entailment) logic as a real-world example of the extension framework:

```python
# Import and register FDE logic
from tableaux.logics.fde import add_fde_to_api
add_fde_to_api()

# Use FDE logic
fde = LogicSystem.fde()
p, q = fde.atoms('p', 'q')

# Test paraconsistent behavior (contradictions are satisfiable)
contradiction = p & ~p
result = fde.solve(contradiction, 'B')  # B = "both true and false"
print(f"Contradiction satisfiable: {result.satisfiable}")  # True

# Test explosion failure (contradictions don't entail everything)
explosion_test = fde.entails([p & ~p], q)
print(f"Does contradiction entail q? {explosion_test}")  # False
```

**FDE demonstrates:**
- Four-valued logic (T, F, B, N)
- Paraconsistent reasoning (allows contradictions)
- Complete plugin architecture usage
- Proper API integration with registration

See `src/tableaux/logics/fde.py` and `tests/test_fde_extension.py` for the complete implementation.

## Advanced Usage

### Performance Optimization

The system includes several optimizations:

```python
# Enable step tracking for analysis
result = classical.solve(formula, track_steps=True)
print(f"Steps taken: {len(result.steps)}")

# For large formulas, the system automatically:
# - Prioritizes α-rules (non-branching) over β-rules (branching)
# - Uses O(1) closure detection
# - Eliminates subsumed branches
# - Terminates early when satisfiability is determined
```

### Custom Formula Patterns

```python
# Test specific formula patterns
def test_dnf_patterns(logic_system):
    """Test disjunctive normal form patterns."""
    p, q, r = logic_system.atoms('p', 'q', 'r')
    
    # Generate DNF formulas
    dnf_formulas = [
        (p & q) | (~p & r),
        (p & q & r) | (~p & ~q) | (p & ~r),
        # ... more patterns
    ]
    
    for formula in dnf_formulas:
        result = logic_system.solve(formula)
        print(f"{formula}: {len(result.models)} models")

# Test across all systems
for name, system in [("Classical", LogicSystem.classical()),
                     ("Weak Kleene", LogicSystem.weak_kleene())]:
    print(f"\n{name} Logic:")
    test_dnf_patterns(system)
```

### Integration with External Tools

```python
# Export models for external analysis
def export_models(result, filename):
    """Export models to JSON for external tools."""
    import json
    
    models_data = []
    for model in result.models:
        model_dict = {}
        for assignment in str(model).split(', '):
            if ': ' in assignment:
                var, val = assignment.split(': ')
                model_dict[var] = val
        models_data.append(model_dict)
    
    with open(filename, 'w') as f:
        json.dump(models_data, f, indent=2)

# Use with your formulas
formula = p.implies(q) & (~q)
result = classical.solve(formula)
export_models(result, 'models.json')
```

## Conclusion

The tableau system provides a unified framework for automated reasoning across multiple logic systems. Key takeaways:

1. **Unified Interface**: Same API and CLI work across all logic systems
2. **Extensible Design**: Easy to add new logic systems by defining syntax and tableau rules
3. **Self-Contained Logic Definitions**: Each logic system is completely defined in one file
4. **Industrial Performance**: Optimized tableau construction with proper termination
5. **Research Friendly**: Clean abstractions make it easy to experiment with new logics

The system handles all the complex tableau construction while letting you focus on the logical definitions. Whether you're using existing logic systems or building new ones, the unified architecture provides a solid foundation for automated reasoning research.

For more information, see:
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Architecture Guide](ARCHITECTURE.md) - System design details  
- [CLI Guide](CLI_GUIDE.md) - Comprehensive CLI reference

Happy reasoning!