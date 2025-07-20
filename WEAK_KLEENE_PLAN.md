# Weak Kleene Logic Extension Plan

## Overview

This document outlines the plan to extend the current classical propositional logic (CPL) tableau system to support **Propositional Weak Kleene Logic (WK3)**.

## Background: Weak Kleene Logic

Weak Kleene logic is a **three-valued logic** with truth values:
- **t** (True)
- **f** (False)  
- **e** (Neither/Undefined/Gap)

### Truth Tables for Weak Kleene Logic

#### Negation (¬)
| A | ¬A |
|---|----| 
| t | f  |
| f | t  |
| e | e  |

#### Conjunction (∧)
| A | B | A∧B |
|---|---|-----|
| t | t | t   |
| t | f | f   |
| t | e | e   |
| f | t | f   |
| f | f | f   |
| f | e | f   |
| e | t | e   |
| e | f | f   |
| e | e | e   |

#### Disjunction (∨)
| A | B | A∨B |
|---|---|-----|
| t | t | t   |
| t | f | t   |
| t | e | t   |
| f | t | t   |
| f | f | f   |
| f | e | e   |
| e | t | t   |
| e | f | e   |
| e | e | e   |

#### Implication (→)
| A | B | A→B |
|---|---|-----|
| t | t | t   |
| t | f | f   |
| t | e | e   |
| f | t | t   |
| f | f | t   |
| f | e | t   |
| e | t | t   |
| e | f | e   |
| e | e | e   |

## Implementation Strategy

### Phase 1: Core Infrastructure (High Priority)

#### 1.1 Extend Truth Value System
- **Current**: Binary values (True/False)
- **Target**: Three-valued system (t/f/e)
- **Implementation**: 
  - New `TruthValue` enum class
  - Update `Model` class to handle three-valued assignments
  - Modify model extraction logic

#### 1.2 Update Formula Evaluation
- **Current**: Boolean evaluation in `Model._evaluate()`
- **Target**: Three-valued evaluation following WK3 truth tables
- **Implementation**:
  - Implement WK3 truth tables for all operators
  - Handle partial assignments (some atoms undefined)
  - Add validation for three-valued models

#### 1.3 Modify Tableau Rules
- **Current**: Classical tableau rules with binary branching
- **Target**: WK3 tableau rules with potential three-way branching
- **Key Changes**:
  - **Atoms**: Can be t, f, or e
  - **Negation**: ¬¬A ≠ A when A has value e
  - **Conjunction**: More complex branching for undefined values
  - **Disjunction**: Additional cases for e values
  - **Implication**: Expanded rule set for three-valued semantics

### Phase 2: Tableau Rule Extensions (High Priority)

#### 2.1 Three-Valued Literals
- **Positive literals**: A = t
- **Negative literals**: A = f  
- **Neither literals**: A = e (new)
- **Update closure detection**: No contradiction with e values

#### 2.2 Updated Expansion Rules

**Conjunction (A ∧ B):**
- **t branch**: A = t, B = t
- **f branches**: A = f | B = f
- **e branches**: (A = e, B ≠ f) | (A ≠ f, B = e)

**Disjunction (A ∨ B):**
- **t branches**: A = t | B = t  
- **f branch**: A = f, B = f
- **e branches**: (A = e, B ≠ t) | (A ≠ t, B = e)

**Implication (A → B):**
- **t branches**: A = f | B = t
- **f branch**: A = t, B = f
- **e branches**: Complex cases involving e values

#### 2.3 Closure Detection Updates
- **Classical**: A and ¬A in same branch
- **WK3**: A = t and A = f in same branch (A = e is consistent with both)
- **Three-way consistency**: Track t/f/e assignments per atom

### Phase 3: Testing and Validation (Medium Priority)

#### 3.1 Test Suite Extension
- **WK3-specific test cases**: Formulas that behave differently in WK3 vs CPL
- **Truth table validation**: Verify all operators follow WK3 semantics
- **Model enumeration**: Test three-valued model generation
- **Edge cases**: Formulas with all e values, mixed assignments

#### 3.2 Performance Testing
- **Branching factor**: Measure impact of three-way branching
- **Memory usage**: Track overhead of three-valued assignments  
- **Optimization validation**: Ensure optimizations work with WK3

### Phase 4: CLI and Documentation (Low Priority)

#### 4.1 CLI Extensions
- **Input syntax**: Support for three-valued models/assignments
- **Output formatting**: Display e values clearly
- **Model presentation**: Show three-valued satisfying assignments

#### 4.2 Documentation Updates
- **README**: Add WK3 section with examples
- **Technical analysis**: Compare WK3 vs CPL tableau complexity
- **Usage examples**: Demonstrate three-valued reasoning

## Technical Challenges

### 1. Increased Complexity
- **Branching factor**: Potential 3x increase in branches
- **Rule complexity**: More cases to handle in each expansion
- **Model space**: Exponentially larger model space (3^n vs 2^n)

### 2. Optimization Preservation
- **Formula prioritization**: May need adjustment for three-valued context
- **Subsumption**: More complex with three-valued assignments
- **Closure detection**: Must handle partial information correctly

### 3. Theoretical Considerations
- **Completeness**: Ensure WK3 tableau system is complete
- **Soundness**: Verify all rules preserve WK3 semantics
- **Decidability**: WK3 propositional logic is decidable, but complexity may increase

## Success Criteria

### Functional Requirements
- ✅ Correct implementation of all WK3 truth tables
- ✅ Sound and complete tableau system for WK3
- ✅ Three-valued model extraction and validation
- ✅ Backward compatibility with classical logic (when no e values)

### Performance Requirements  
- ✅ Reasonable performance on small-to-medium formulas
- ✅ Preservation of current optimizations where applicable
- ✅ Graceful handling of exponential cases

### Quality Requirements
- ✅ Comprehensive test suite covering WK3 specifics
- ✅ Clear documentation of differences from CPL
- ✅ Maintainable code structure supporting both logics

## Implementation Timeline

1. **Week 1**: Core infrastructure (TruthValue, Model updates)
2. **Week 2**: Basic tableau rules for WK3
3. **Week 3**: Advanced rules and optimization integration  
4. **Week 4**: Testing, validation, and documentation

## Research References

- Kleene, S.C. (1938). "On notation for ordinal numbers"
- Priest, G. (2008). "An Introduction to Non-Classical Logic" (Chapter on Many-Valued Logics)
- Fitting, M. (1991). "Many-valued modal logics" (Tableau methods for many-valued logics)
- Hähnle, R. (2001). "Tableaux and related methods" (Many-valued tableau systems)

---

This extension will significantly enhance the tableau system's capabilities while maintaining its production-quality standards and educational value.