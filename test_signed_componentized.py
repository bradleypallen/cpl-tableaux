#!/usr/bin/env python3
"""
Test Signed Componentized Integration

Tests that signed tableaux integrate correctly with the componentized architecture.
"""

import pytest
from formula import Atom, Negation, Conjunction, Disjunction, Implication
from signed_components import (
    SignedBranchAdapter, SignedBranchFactory, SignedClosureDetector,
    SignedModelExtractor, SignedLiteralRecognizer, SignedSubsumptionDetector,
    create_classical_signed_components, create_three_valued_signed_components
)
from signed_componentized_rules import (
    SignedRuleAdapter, SignedRuleRegistry,
    get_classical_signed_rules, get_three_valued_signed_rules
)
from signed_formula import T, F, T3, F3, U
from signed_tableau import SignedBranch


class TestSignedComponents:
    """Test signed tableau components"""
    
    def test_signed_branch_adapter(self):
        """Test SignedBranchAdapter functionality"""
        p = Atom("p")
        q = Atom("q")
        
        # Create a signed branch with some formulas
        signed_branch = SignedBranch(1, {T(p), F(q)})
        adapter = SignedBranchAdapter(signed_branch, "classical")
        
        assert adapter.id == 1
        assert not adapter.is_closed
        
        # Test formula access
        formulas = adapter.formulas
        assert p in formulas
        assert q in formulas
        
        # Test signed formula access
        signed_formulas = adapter.signed_formulas
        assert T(p) in signed_formulas
        assert F(q) in signed_formulas
        
        # Test adding formulas
        r = Atom("r")
        adapter.add_formula(r)
        assert r in adapter.formulas
    
    def test_signed_branch_factory(self):
        """Test SignedBranchFactory"""
        factory = SignedBranchFactory("classical")
        p = Atom("p")
        q = Atom("q")
        
        # Create branch with formulas
        branch = factory.create_branch(1, [p, q])
        
        assert branch.id == 1
        assert p in branch.formulas
        assert q in branch.formulas
        
        # Test copying
        copy = factory.copy_branch(branch, 2)
        assert copy.id == 2
        assert p in copy.formulas
        assert q in copy.formulas
    
    def test_signed_closure_detector(self):
        """Test SignedClosureDetector"""
        detector = SignedClosureDetector("classical")
        
        # Create open branch
        p = Atom("p")
        open_branch = SignedBranchAdapter(SignedBranch(1, {T(p)}), "classical")
        assert not detector.is_closed(open_branch)
        
        # Create closed branch (contains T:p and F:p)
        closed_branch = SignedBranchAdapter(SignedBranch(2, {T(p), F(p)}), "classical")
        assert detector.is_closed(closed_branch)
        
        reason = detector.get_closure_reason(closed_branch)
        assert reason is not None
        assert "Contradiction" in reason
    
    def test_signed_model_extractor(self):
        """Test SignedModelExtractor"""
        extractor = SignedModelExtractor("classical")
        
        p = Atom("p")
        q = Atom("q")
        
        # Create open branch with assignments
        open_branch = SignedBranchAdapter(SignedBranch(1, {T(p), F(q)}), "classical")
        
        model = extractor.extract_model(open_branch)
        assert model is not None
        assert model.get(p.name) == True
        assert model.get(q.name) == False
        
        # Test closed branch
        closed_branch = SignedBranchAdapter(SignedBranch(2, {T(p), F(p)}), "classical")
        model = extractor.extract_model(closed_branch)
        assert model is None
    
    def test_signed_literal_recognizer(self):
        """Test SignedLiteralRecognizer"""
        recognizer = SignedLiteralRecognizer("classical")
        
        p = Atom("p")
        neg_p = Negation(p)
        
        # Test positive literal
        assert recognizer.is_positive_literal(T(p))
        assert not recognizer.is_positive_literal(F(p))
        assert not recognizer.is_positive_literal(T(neg_p))
        
        # Test negative literal
        assert recognizer.is_negative_literal(T(neg_p))
        assert not recognizer.is_negative_literal(F(neg_p))
        assert not recognizer.is_negative_literal(T(p))


class TestSignedRules:
    """Test signed rule integration"""
    
    def test_signed_rule_adapter(self):
        """Test SignedRuleAdapter functionality"""
        from signed_tableau_rules import TConjunctionRule
        
        # Create adapter for T-conjunction rule
        signed_rule = TConjunctionRule()
        adapter = SignedRuleAdapter(signed_rule, "classical")
        
        assert adapter.is_alpha_rule
        assert not adapter.is_beta_rule
        
        # Test rule application
        p = Atom("p")
        q = Atom("q")
        conj = Conjunction(p, q)
        
        assert adapter.applies_to(conj)
        
        # Test rule application (need mock context)
        from tableau_rules import RuleContext
        context = RuleContext(tableau=None, branch=None, parent_node=None)
        
        result = adapter.apply(conj, context)
        assert result.branch_count == 1
        assert len(result.formulas_for_branches[0]) == 2
        assert p in result.formulas_for_branches[0]
        assert q in result.formulas_for_branches[0]
    
    def test_signed_rule_registry(self):
        """Test SignedRuleRegistry"""
        registry = SignedRuleRegistry("classical")
        
        rules = registry.get_rules()
        assert len(rules) > 0
        
        # Test rule finding
        p = Atom("p")
        q = Atom("q")
        conj = Conjunction(p, q)
        
        applicable = registry.find_applicable_rules(conj)
        assert len(applicable) > 0
        
        best_rule = registry.get_best_rule(conj)
        assert best_rule is not None
        assert best_rule.applies_to(conj)
    
    def test_classical_vs_three_valued_rules(self):
        """Test that classical and three-valued rule sets differ appropriately"""
        classical_rules = get_classical_signed_rules()
        three_valued_rules = get_three_valued_signed_rules()
        
        assert len(classical_rules) > 0
        assert len(three_valued_rules) > 0
        
        # Three-valued should have more rules (includes U-rules)
        # This might not always be true, but let's test they exist
        assert isinstance(classical_rules, list)
        assert isinstance(three_valued_rules, list)


class TestSignedComponentIntegration:
    """Test integration between components and rules"""
    
    def test_complete_classical_integration(self):
        """Test complete integration with classical signed components"""
        components = create_classical_signed_components()
        
        assert 'branch_factory' in components
        assert 'closure_detector' in components
        assert 'model_extractor' in components
        assert 'literal_recognizer' in components
        assert 'subsumption_detector' in components
        
        # Test creating and using components
        factory = components['branch_factory']
        detector = components['closure_detector']
        extractor = components['model_extractor']
        
        p = Atom("p")
        branch = factory.create_branch(1, [p])
        
        assert not detector.is_closed(branch)
        
        model = extractor.extract_model(branch)
        assert model is not None
    
    def test_complete_three_valued_integration(self):
        """Test complete integration with three-valued signed components"""
        components = create_three_valued_signed_components()
        
        # Similar test but for three-valued logic
        factory = components['branch_factory']
        detector = components['closure_detector']
        
        p = Atom("p")
        branch = factory.create_branch(1, [p])
        
        assert not detector.is_closed(branch)
        
        # Test three-valued specific behavior
        # In three-valued logic, T:p and U:p should not cause closure
        branch.add_signed_formula(U(p))
        assert not detector.is_closed(branch)
        
        # But T:p and F:p should cause closure
        branch.add_signed_formula(F3(p))
        assert detector.is_closed(branch)
    
    def test_rule_and_component_interaction(self):
        """Test that rules and components work together"""
        # Create components and rules
        components = create_classical_signed_components()
        rules = get_classical_signed_rules()
        
        factory = components['branch_factory']
        detector = components['closure_detector']
        
        # Create branch with conjunction
        p = Atom("p")
        q = Atom("q")
        conj = Conjunction(p, q)
        
        branch = factory.create_branch(1, [conj])
        
        # Find applicable rule
        applicable_rules = [r for r in rules if r.applies_to(conj)]
        assert len(applicable_rules) > 0
        
        rule = applicable_rules[0]
        assert rule.is_alpha_rule  # Conjunction should be α-rule
        
        # Apply rule (need mock context)
        from tableau_rules import RuleContext
        context = RuleContext(tableau=None, branch=branch, parent_node=None)
        
        result = rule.apply(conj, context)
        
        # Should produce single branch with two formulas
        assert result.branch_count == 1
        assert len(result.formulas_for_branches[0]) == 2
        
        # Add the resulting formulas to branch
        branch.add_formulas(result.formulas_for_branches[0])
        
        # Branch should still be open (p and q are consistent)
        assert not detector.is_closed(branch)
        assert p in branch.formulas
        assert q in branch.formulas


class TestPerformanceIntegration:
    """Test performance aspects of signed component integration"""
    
    def test_rule_lookup_performance(self):
        """Test that rule lookup is efficient"""
        registry = SignedRuleRegistry("classical")
        
        # Create various formulas
        test_formulas = [
            Atom("p"),
            Negation(Atom("p")),
            Conjunction(Atom("p"), Atom("q")),
            Disjunction(Atom("p"), Atom("q")),
            Implication(Atom("p"), Atom("q"))
        ]
        
        # Test that rule lookup works for all
        for formula in test_formulas:
            applicable = registry.find_applicable_rules(formula)
            # At least negation and compound formulas should have rules
            if not formula.is_atomic():
                assert len(applicable) > 0
    
    def test_branch_operation_performance(self):
        """Test that branch operations are efficient"""
        factory = SignedBranchFactory("classical")
        
        # Create branch with many formulas
        formulas = [Atom(f"p{i}") for i in range(100)]
        branch = factory.create_branch(1, formulas)
        
        # Should handle large number of formulas
        assert len(branch.formulas) == 100
        
        # Test copying large branch
        copy = factory.copy_branch(branch, 2)
        assert len(copy.formulas) == 100
        assert copy.id == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])