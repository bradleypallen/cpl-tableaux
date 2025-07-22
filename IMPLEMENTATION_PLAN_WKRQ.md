# Implementation Plan: wKrQ - Weak Kleene Logic with Restricted Quantifiers

Based on Ferguson, Thomas Macaulay. "Tableaux and restricted quantification for systems related to weak Kleene logic." In International Conference on Automated Reasoning with Analytic Tableaux and Related Methods, pp. 3-19. Cham: Springer International Publishing, 2021.

## Overview

This document outlines the implementation plan for extending our tableau system to support **wKrQ (Weak Kleene Logic with Restricted Quantifiers)** with **restricted quantifiers** (∃̌ and ∀̌).

## Formal Foundation

### Restricted Kleene Quantifiers (Definition 3)

For a nonempty set X ⊆ V₃²:

**Existential ∃̌(X):**
```
∃̌(X) = {
    t  if ⟨t,t⟩ ∈ X
    e  if for all ⟨u,v⟩ ∈ X, either u = e or v = e  
    f  if ⟨t,t⟩ ∉ X and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e
}
```

**Universal ∀̌(X):**
```
∀̌(X) = {
    t  if ⟨t,f⟩, ⟨t,e⟩ ∉ X and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e
    e  if for all ⟨u,v⟩ ∈ X, either u = e or v = e
    f  if {⟨t,f⟩, ⟨t,e⟩} ∩ X ≠ ∅ and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e  
}
```

### Predicate Weak Kleene Interpretation (Definition 4)

A predicate weak Kleene interpretation I is a pair (C^I, R^I) where:
- C^I is a domain of individuals  
- R^I is a collection of functions where I assigns:
  - every constant c an individual c^I ∈ C^I
  - every n-ary predicate R a function R^I: (C^I)ⁿ → V₃

### Quantified Formula Evaluation (Definition 5)

For atomic formulas:
- I(R(c₀, ..., cₙ₋₁)) = R^I(c₀^I, ..., cₙ₋₁^I)

For quantified formulas:
- I([∃̌xφ(x)]ψ(x)) = ∃̌({⟨I(φ(c)), I(ψ(c))⟩ | c ∈ C})
- I([∀̌xφ(x)]ψ(x)) = ∀̌({⟨I(φ(c)), I(ψ(c))⟩ | c ∈ C})

## Implementation Architecture

### 1. Core Components

#### 1.1 Formula Extensions
```python
# New formula types for quantified formulas
class RestrictedExistentialQuantifier(Formula):
    def __init__(self, variable: Variable, body: Formula):
        self.variable = variable
        self.body = body
        self.quantifier_type = "restricted_existential"

class RestrictedUniversalQuantifier(Formula):
    def __init__(self, variable: Variable, body: Formula):
        self.variable = variable  
        self.body = body
        self.quantifier_type = "restricted_universal"
```

#### 1.2 Truth Value System Extensions
```python
class RestrictedQuantifierOperators:
    @staticmethod
    def restricted_existential(value_pairs: Set[Tuple[TruthValue, TruthValue]]) -> TruthValue:
        """Implement ∃̌(X) from Definition 3"""
        if not value_pairs:
            raise ValueError("Empty set not allowed for restricted quantifiers")
        
        # Check if ⟨t,t⟩ ∈ X
        if (t, t) in value_pairs:
            return t
            
        # Check if for all ⟨u,v⟩ ∈ X, either u = e or v = e
        if all(u == e or v == e for u, v in value_pairs):
            return e
            
        # Otherwise: ⟨t,t⟩ ∉ X and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e
        return f

    @staticmethod
    def restricted_universal(value_pairs: Set[Tuple[TruthValue, TruthValue]]) -> TruthValue:
        """Implement ∀̌(X) from Definition 3"""
        if not value_pairs:
            raise ValueError("Empty set not allowed for restricted quantifiers")
            
        # Check if for all ⟨u,v⟩ ∈ X, either u = e or v = e
        if all(u == e or v == e for u, v in value_pairs):
            return e
            
        # Check if {⟨t,f⟩, ⟨t,e⟩} ∩ X ≠ ∅ and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e
        has_critical_pairs = (t, f) in value_pairs or (t, e) in value_pairs
        has_non_undefined_pair = any(u != e and v != e for u, v in value_pairs)
        
        if has_critical_pairs and has_non_undefined_pair:
            return f
            
        # Otherwise: ⟨t,f⟩, ⟨t,e⟩ ∉ X and for some ⟨u,v⟩ ∈ X, u ≠ e and v ≠ e  
        if has_non_undefined_pair:
            return t
            
        return e  # Fallback case
```

### 2. Tableau Rules Implementation

Based on Definition 9 from Ferguson (2021):

#### 2.1 Restricted Existential Quantifier Rule
```python
class RestrictedExistentialRule(TableauRule):
    priority = 2  # α-rule priority
    rule_type = RuleType.RESTRICTED_EXISTENTIAL
    description = "Restricted Existential Quantifier (∃̌xφ(x))"
    
    def applies_to(self, formula: Formula) -> bool:
        return isinstance(formula, RestrictedExistentialQuantifier)
    
    def apply(self, formula: RestrictedExistentialQuantifier, context: RuleContext) -> RuleApplication:
        # Generate fresh constant
        fresh_constant = self._generate_fresh_constant(context)
        
        # Substitute variable with fresh constant in body
        instantiated_body = formula.body.substitute(formula.variable, fresh_constant)
        
        # Add to same branch (α-rule behavior)
        return RuleApplication(
            formulas_for_branches=[[instantiated_body]],
            branch_count=1,
            metadata={
                'quantifier_type': 'restricted_existential',
                'variable': formula.variable.name,
                'fresh_constant': fresh_constant.name,
                'witness_generation': True
            }
        )
```

#### 2.2 Restricted Universal Quantifier Rule  
```python
class RestrictedUniversalRule(TableauRule):
    priority = 3  # β-rule priority (creates branching)
    rule_type = RuleType.RESTRICTED_UNIVERSAL  
    description = "Restricted Universal Quantifier (∀̌xφ(x))"
    
    def applies_to(self, formula: Formula) -> bool:
        return isinstance(formula, RestrictedUniversalQuantifier)
    
    def apply(self, formula: RestrictedUniversalQuantifier, context: RuleContext) -> RuleApplication:
        # Get all constants in current domain
        domain_constants = self._get_domain_constants(context)
        
        if not domain_constants:
            # No constants yet - generate fresh constant
            fresh_constant = self._generate_fresh_constant(context)
            domain_constants = [fresh_constant]
        
        # Create instantiations for all domain constants
        instantiated_formulas = []
        for constant in domain_constants:
            instantiated = formula.body.substitute(formula.variable, constant)
            instantiated_formulas.append(instantiated)
        
        # Universal quantifier creates single branch with all instantiations
        return RuleApplication(
            formulas_for_branches=[instantiated_formulas],
            branch_count=1,
            metadata={
                'quantifier_type': 'restricted_universal',
                'variable': formula.variable.name,
                'domain_constants': [c.name for c in domain_constants],
                'instantiation_count': len(domain_constants)
            }
        )
```

### 3. Domain Management

#### 3.1 wKrQ Branch Implementation
```python
class WKrQ_Branch(BranchInterface):
    def __init__(self, branch_id: int, formulas: List[Formula] = None):
        super().__init__()
        self._id = branch_id
        self._formulas = list(formulas) if formulas else []
        self._is_closed = False
        self._closure_reason: Optional[str] = None
        
        # Three-valued assignments for atomic formulas
        self._assignments: Dict[str, TruthValue] = {}
        
        # Domain management for quantifiers
        self._domain: Set[Constant] = set()
        self._fresh_constant_counter = 0
        
        # Quantifier tracking
        self._applied_universals: Set[str] = set()  # Track applied ∀̌ formulas
        self._generated_witnesses: Dict[str, List[Constant]] = {}  # ∃̌ witnesses
        
    def add_to_domain(self, constant: Constant) -> None:
        """Add constant to the domain of quantification"""
        self._domain.add(constant)
        
        # Re-apply any universal quantifiers with new constant
        self._trigger_universal_reapplication()
    
    def generate_fresh_constant(self, base_name: str = "c") -> Constant:
        """Generate a fresh constant for witness generation"""
        fresh_name = f"{base_name}_{self._fresh_constant_counter}"
        self._fresh_constant_counter += 1
        fresh_constant = Constant(fresh_name)
        self.add_to_domain(fresh_constant)
        return fresh_constant
    
    def get_domain_constants(self) -> List[Constant]:
        """Get all constants in the current domain"""
        return list(self._domain)
    
    def add_predicate_assignment(self, predicate: str, args: List[Constant], value: TruthValue) -> None:
        """Add three-valued assignment for predicate with arguments"""
        predicate_key = f"{predicate}({','.join(c.name for c in args)})"
        
        existing = self._assignments.get(predicate_key)
        if existing is not None and existing != value:
            # Check for three-valued contradiction
            if existing in [t, f] and value in [t, f] and existing != value:
                self.close_branch(f"Three-valued contradiction: {predicate_key}={existing} and {predicate_key}={value}")
        else:
            self._assignments[predicate_key] = value
```

### 4. Model Extraction for wKrQ

```python
class WKrQ_ModelExtractor(ModelExtractor):
    def extract_model(self, branch: BranchInterface) -> 'WKrQ_Model':
        """Extract three-valued first-order model from open branch"""
        if not isinstance(branch, WKrQ_Branch):
            raise TypeError("Expected WKrQ_Branch")
            
        if branch.is_closed:
            raise ModelExtractionError("Cannot extract model from closed branch")
        
        # Create domain from branch's domain constants
        domain = {c.name: c for c in branch.get_domain_constants()}
        
        # Extract predicate assignments
        predicate_assignments = {}
        for key, value in branch._assignments.items():
            predicate_assignments[key] = value
        
        # Create complete model with default values for unassigned predicates
        return WKrQ_Model(domain, predicate_assignments)

class WKrQ_Model:
    def __init__(self, domain: Dict[str, Constant], predicate_assignments: Dict[str, TruthValue]):
        self.domain = domain
        self.predicate_assignments = predicate_assignments
    
    def evaluate(self, formula: Formula) -> TruthValue:
        """Evaluate formula under this three-valued first-order model"""
        if isinstance(formula, Predicate):
            key = f"{formula.predicate_name}({','.join(arg.name for arg in formula.args)})"
            return self.predicate_assignments.get(key, e)  # Default to undefined
            
        elif isinstance(formula, RestrictedExistentialQuantifier):
            # Evaluate ∃̌xφ(x) using restricted quantifier semantics
            value_pairs = set()
            for constant in self.domain.values():
                instantiated = formula.body.substitute(formula.variable, constant)
                # For ∃̌, we need pairs ⟨φ(c), φ(c)⟩ (simplified case)
                value = self.evaluate(instantiated)
                value_pairs.add((value, value))
            
            return RestrictedQuantifierOperators.restricted_existential(value_pairs)
            
        elif isinstance(formula, RestrictedUniversalQuantifier):
            # Evaluate ∀̌xφ(x) using restricted quantifier semantics  
            value_pairs = set()
            for constant in self.domain.values():
                instantiated = formula.body.substitute(formula.variable, constant)
                # For ∀̌, we need pairs ⟨φ(c), ¬φ(c)⟩ 
                value = self.evaluate(instantiated)
                neg_value = WeakKleeneOperators.negation(value)
                value_pairs.add((value, neg_value))
            
            return RestrictedQuantifierOperators.restricted_universal(value_pairs)
            
        # Handle propositional connectives using existing WK3 operators
        elif isinstance(formula, Negation):
            return WeakKleeneOperators.negation(self.evaluate(formula.operand))
        elif isinstance(formula, Conjunction):
            return WeakKleeneOperators.conjunction(
                self.evaluate(formula.left), self.evaluate(formula.right))
        elif isinstance(formula, Disjunction):
            return WeakKleeneOperators.disjunction(
                self.evaluate(formula.left), self.evaluate(formula.right))
        elif isinstance(formula, Implication):
            return WeakKleeneOperators.implication(
                self.evaluate(formula.left), self.evaluate(formula.right))
        else:
            raise ValueError(f"Unknown formula type: {type(formula)}")
```

### 5. Logic System Registration

```python
def create_wkrq_logic_system() -> LogicSystem:
    """Create wKrQ (Weak Kleene Logic with Restricted Quantifiers) system"""
    
    config = LogicSystemConfig(
        name="wKrQ (Weak Kleene Logic with Restricted Quantifiers)",
        truth_values=3,
        description="Three-valued first-order logic with restricted Kleene quantifiers ∃̌ and ∀̌",
        supports_quantifiers=True,
        aliases=["wkrq", "wkrq-restricted"]
    )
    
    # Combine propositional WK3 rules with quantifier rules
    rules = [
        # Propositional rules (inherited from WK3)
        DoubleNegationRule(),
        ConjunctionRule(), 
        DisjunctionRule(),
        ImplicationRule(),
        NegatedConjunctionRule(),
        NegatedDisjunctionRule(),
        NegatedImplicationRule(),
        
        # New quantifier rules
        RestrictedExistentialRule(),
        RestrictedUniversalRule(),
        
        # Atom assignment rules for three-valued predicates
        PredicateAssignmentTrueRule(),
        PredicateAssignmentFalseRule(),
        PredicateAssignmentUndefinedRule()
    ]
    
    components = {
        'branch_factory': WKrQ_BranchFactory(),
        'closure_detector': WKrQ_ClosureDetector(),
        'model_extractor': WKrQ_ModelExtractor(),
        'literal_recognizer': WKrQ_LiteralRecognizer(), 
        'subsumption_detector': WKrQ_SubsumptionDetector()
    }
    
    return LogicSystem(config, rules, **components)

# Register the new logic system
register_logic_system("wkrq", create_wkrq_logic_system)
```

### 6. Usage Examples

```python
# Create terms and predicates
john = Constant("john")
mary = Constant("mary")
x = Variable("x")

# Create predicates
student = lambda term: Predicate("Student", [term])
loves = lambda t1, t2: Predicate("Loves", [t1, t2])

# Create quantified formulas with restricted quantifiers
exists_student = RestrictedExistentialQuantifier(x, student(x))  # ∃̌x Student(x)
all_love_john = RestrictedUniversalQuantifier(x, loves(x, john))  # ∀̌x Loves(x, john)

# Test satisfiability using wKrQ tableau
formula = Conjunction(exists_student, all_love_john)
tableau = ComponentizedTableau(formula, "wkrq")
is_satisfiable = tableau.build()

print(f"Formula satisfiable: {is_satisfiable}")
if is_satisfiable:
    models = tableau.extract_all_models()
    for model in models:
        print(f"Model domain: {list(model.domain.keys())}")
        print(f"Predicate assignments: {model.predicate_assignments}")
```

## Testing Strategy

### 7.1 Unit Tests for Restricted Quantifier Operators
```python
def test_restricted_existential_quantifier():
    # Test cases from Definition 3
    
    # Case 1: ⟨t,t⟩ ∈ X → result should be t
    value_pairs = {(t, t), (f, e), (e, f)}
    result = RestrictedQuantifierOperators.restricted_existential(value_pairs)
    assert result == t
    
    # Case 2: All pairs have e component → result should be e  
    value_pairs = {(e, t), (f, e), (e, e)}
    result = RestrictedQuantifierOperators.restricted_existential(value_pairs)
    assert result == e
    
    # Case 3: No ⟨t,t⟩ and some non-e pairs → result should be f
    value_pairs = {(t, f), (f, t), (e, e)}
    result = RestrictedQuantifierOperators.restricted_existential(value_pairs)
    assert result == f

def test_restricted_universal_quantifier():
    # Test cases from Definition 3
    
    # Case 1: All pairs have e component → result should be e
    value_pairs = {(e, t), (f, e), (e, e)}
    result = RestrictedQuantifierOperators.restricted_universal(value_pairs)
    assert result == e
    
    # Case 2: Contains ⟨t,f⟩ or ⟨t,e⟩ and non-e pair → result should be f  
    value_pairs = {(t, f), (f, t)}
    result = RestrictedQuantifierOperators.restricted_universal(value_pairs)
    assert result == f
    
    # Case 3: No critical pairs and has non-e pair → result should be t
    value_pairs = {(t, t), (f, f)}
    result = RestrictedQuantifierOperators.restricted_universal(value_pairs)
    assert result == t
```

### 7.2 Integration Tests
```python
def test_fol_wk3_tableau_satisfiability():
    """Test satisfiability checking with restricted quantifiers"""
    x = Variable("x")
    
    # Test: ∃̌x P(x) ∧ ∀̌x ¬P(x) should be unsatisfiable
    exists_p = RestrictedExistentialQuantifier(x, Predicate("P", [x]))
    all_not_p = RestrictedUniversalQuantifier(x, Negation(Predicate("P", [x])))
    contradiction = Conjunction(exists_p, all_not_p)
    
    tableau = ComponentizedTableau(contradiction, "wkrq")
    result = tableau.build()
    
    assert result == False  # Should be unsatisfiable
    
def test_wkrq_model_extraction():
    """Test model extraction for satisfiable formulas"""
    x = Variable("x")
    
    # Test: ∃̌x P(x) should be satisfiable
    exists_p = RestrictedExistentialQuantifier(x, Predicate("P", [x]))
    
    tableau = ComponentizedTableau(exists_p, "wkrq")
    result = tableau.build()
    
    assert result == True
    models = tableau.extract_all_models()
    assert len(models) > 0
    
    model = models[0]
    assert len(model.domain) >= 1  # Should have at least one witness constant
```

## Implementation Timeline

### Phase 1 (Week 1-2): Core Infrastructure
- [ ] Implement restricted quantifier truth value operators
- [ ] Create FOL formula classes for restricted quantifiers  
- [ ] Implement basic WKrQ_Branch with domain management
- [ ] Add unit tests for quantifier operators

### Phase 2 (Week 3-4): Tableau Rules
- [ ] Implement RestrictedExistentialRule and RestrictedUniversalRule
- [ ] Create WKrQ_ClosureDetector for three-valued predicate contradictions
- [ ] Implement fresh constant generation and domain tracking
- [ ] Add tableau rule unit tests

### Phase 3 (Week 5-6): Model Extraction and Integration
- [ ] Implement WKrQ_ModelExtractor and WKrQ_Model
- [ ] Create complete logic system registration
- [ ] Add integration with componentized tableau system
- [ ] Comprehensive integration testing

### Phase 4 (Week 7-8): Validation and Documentation  
- [ ] Extensive testing against paper's examples
- [ ] Performance benchmarking and optimization
- [ ] Complete documentation with examples
- [ ] Research validation against reference implementations

## Research Validation

The implementation will be validated against:
1. **Formal definitions** from Ferguson (2021)
2. **Tableau calculus rules** from Definition 9
3. **Truth preservation property** from Definition 6
4. **Comparison with strong/weak quantifier alternatives**
5. **Performance characteristics** for practical reasoning tasks

This implementation will provide a research-grade platform for investigating first-order reasoning in three-valued weak Kleene logic with proper quantifier semantics.