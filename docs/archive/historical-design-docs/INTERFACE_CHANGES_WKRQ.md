# Interface Changes Summary: wKrQ Implementation

## Overview
This document summarizes all interface and documentation changes needed to support First-Order Weak Kleene Logic with Restricted Quantifiers (wKrQ).

## 1. Programmatic Interface Changes

### 1.1 New Core Classes
**File: formula.py**
```python
class RestrictedExistentialQuantifier(Formula)  # ∃̌xφ(x)
class RestrictedUniversalQuantifier(Formula)    # ∀̌xφ(x)
```

**File: truth_value.py**  
```python
class RestrictedQuantifierOperators             # Truth value computations
```

**File: wkrq_tableau.py** (new)
```python
class WKrQ_Tableau                          # Legacy interface
```

### 1.2 Componentized Interface Extensions
**New convenience functions:**
```python
def wkrq_tableau(formula) -> ComponentizedTableau
```

**New logic system registration:**
```python
register_logic_system("wkrq", create_wkrq_logic_system)
```

### 1.3 Mode-Aware Interface Extensions  
**File: logic_mode.py**
```python
class LogicMode(Enum):
    WKRQ = "wkrq"  # New mode
```

**File: mode_aware_tableau.py**
```python
class WKrQ_Builder                          # Programmatic formula builder
def wkrq_tableau(formula) -> ComponentizedTableau
```

## 2. CLI Interface Changes

### 2.1 New Command-Line Options
```bash
tableaux --wkrq "formula"            # New wKrQ mode
tableaux --wkrq --interactive        # Interactive wKrQ mode
```

### 2.2 Parser Extensions
**File: cli.py - FormulaParser class**
- Add quantifier keyword recognition: `exists_r`, `forall_r`, `∃̌`, `∀̌`
- Add predicate syntax parsing: `P(x,y)`, `Student(john)`
- Add variable/constant distinction in quantifier contexts

### 2.3 Interactive Mode Extensions
**New help sections:**
- wKrQ syntax guide
- Quantifier usage examples
- Three-valued model interpretation

**Mode switching:**
```
Tableau> mode
Current mode: Classical
Available modes:
  1. Classical Propositional Logic  
  2. Weak Kleene Logic (WK3)
  3. First-Order Weak Kleene Logic (wKrQ)    # New option
```

## 3. Documentation Changes

### 3.1 README.md Major Updates
**New sections:**
- **4. First-Order Weak Kleene Logic (wKrQ) Interface** (complete section)
- **Quantifier syntax table** in Command-Line Interface section  
- **wKrQ examples** in Programmatic Usage section
- **Interface comparison table** updated with wKrQ column

**Updated sections:**
- Basic Usage examples
- Testing section with wKrQ test commands
- Formula syntax with quantifier patterns

### 3.2 ARCHITECTURE.md Extensions
**New sections:**
- **4. First-Order Weak Kleene Logic (wKrQ)** under Implemented Logic Systems
- **Restricted Quantifier Rules** with formal specifications
- **Domain Management Architecture** for first-order reasoning
- **wKrQ Components** detailed architecture

**Updated sections:**
- Supported Logic Systems summary
- Extension Examples with wKrQ patterns
- Performance characteristics with quantifier complexity analysis

### 3.3 CLAUDE.md Updates
**Updated sections:**
- Repository Overview with wKrQ research focus
- Supported Logic Systems with wKrQ details
- Development Commands with wKrQ examples  
- Research Development Guidelines for quantifier extensions

### 3.4 New Documentation Files
```
WKrQ_TUTORIAL.md              # Complete tutorial with examples
QUANTIFIER_SEMANTICS.md          # Mathematical foundations
WKrQ_EXAMPLES.md              # Extended example library
RESEARCH_VALIDATION.md           # Validation against Ferguson (2024)
```

## 4. Test Suite Extensions

### 4.1 New Test Files
```python
test_wkrq.py                      # Complete wKrQ test suite (25+ tests)
test_wkrq_quantifiers.py          # Quantifier operator unit tests
test_wkrq_cli.py                  # CLI integration tests
```

### 4.2 Updated Test Files
```python
test_comprehensive.py             # Add TestFirstOrderWeakKleeneLogic class
test_componentized_rules.py       # Add wKrQ rule validation tests
```

### 4.3 Test Categories
- **Unit Tests**: Restricted quantifier truth value operators
- **Integration Tests**: wKrQ tableau construction and satisfiability
- **CLI Tests**: Command-line parsing and interactive mode
- **Model Tests**: Three-valued first-order model extraction
- **Performance Tests**: Quantifier expansion performance analysis

## 5. Parser System Changes

### 5.1 Formula Parser Extensions
**File: cli.py - FormulaParser**
- `_parse_quantifier()` method for quantified formula parsing
- Enhanced `_tokenize()` for quantifier keywords and predicate syntax
- Variable/constant recognition in quantifier contexts

### 5.2 Mode-Aware Parser
**File: mode_aware_parser.py**
- WKrQ mode configuration
- Quantifier-aware syntax validation
- Predicate vs propositional atom disambiguation

## 6. Implementation Priority

### Phase 1: Core Extensions (High Priority)
- [ ] Add RestrictedExistentialQuantifier and RestrictedUniversalQuantifier classes
- [ ] Implement RestrictedQuantifierOperators with exact Ferguson semantics
- [ ] Create basic wKrQ tableau rule implementations
- [ ] Add --wkrq CLI option with basic parsing

### Phase 2: Interface Integration (Medium Priority)  
- [ ] Complete componentized system integration
- [ ] Add mode-aware parser support
- [ ] Implement WKrQ_Builder programmatic interface
- [ ] Create interactive mode extensions

### Phase 3: Documentation and Testing (Medium Priority)
- [ ] Update README.md with complete wKrQ documentation
- [ ] Extend ARCHITECTURE.md with wKrQ details
- [ ] Create comprehensive test suites
- [ ] Add tutorial and example documentation

### Phase 4: Advanced Features (Low Priority)
- [ ] Performance optimization for quantifier expansion
- [ ] Advanced model extraction features
- [ ] Research validation documentation
- [ ] Integration with external verification tools

## 7. Backward Compatibility

**All changes maintain 100% backward compatibility:**
- Existing Classical and WK3 logic interfaces unchanged
- All current programmatic APIs preserved
- CLI maintains existing command-line options
- Documentation preserves existing examples and usage patterns

**Migration strategy:**
- wKrQ added as optional extension
- Users can gradually adopt new features
- Legacy code continues to work without modifications
- Clear upgrade path for users wanting wKrQ capabilities

## 8. Quality Assurance

**Interface consistency:**
- wKrQ follows same patterns as Classical/WK3 interfaces
- Error handling and validation consistent across modes
- Documentation style and depth consistent with existing docs

**Testing strategy:**
- All new interfaces covered by automated tests
- CLI integration tested across all supported platforms
- Documentation examples verified as working code

**Performance requirements:**
- wKrQ maintains same performance standards as WK3
- Quantifier expansion optimized for practical reasoning tasks
- Memory usage efficient for domains up to moderate size (100+ constants)

This comprehensive interface analysis ensures that wKrQ integration will be seamless, well-documented, and maintain the high quality standards of the existing system.