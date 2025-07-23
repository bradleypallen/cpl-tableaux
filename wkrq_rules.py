#!/usr/bin/env python3
"""
wKrQ Tableau Rules - Weak Kleene Logic with Restricted Quantifiers

Implements tableau rules for restricted quantifiers ∃̌ and ∀̌ based on:
Ferguson, Thomas Macaulay. "Tableaux and restricted quantification for systems 
related to weak Kleene logic." In International Conference on Automated Reasoning 
with Analytic Tableaux and Related Methods, pp. 3-19. Cham: Springer International 
Publishing, 2021.
"""

from typing import Set, List, Optional, Dict, Any
from tableau_rules import TableauRule, RuleType, RuleContext, RuleApplication, BranchInterface
from formula import Formula, RestrictedExistentialFormula, RestrictedUniversalFormula
from term import Variable, Constant, Term


class RestrictedExistentialRule(TableauRule):
    """
    Tableau rule for restricted existential quantifier ∃̌xφ(x).
    
    Based on Ferguson (2021) Definition 9: The rule generates a fresh constant
    and instantiates the quantifier body with that constant.
    """
    
    @property
    def name(self) -> str:
        return "Restricted Existential Quantifier"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.EXISTENTIAL_QUANTIFIER  # Maps to existing type
    
    @property
    def priority(self) -> int:
        return 2  # α-rule priority (non-branching)
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if this rule applies to restricted existential formulas"""
        return isinstance(formula, RestrictedExistentialFormula)
    
    def apply(self, formula: RestrictedExistentialFormula, context: RuleContext) -> RuleApplication:
        """
        Apply restricted existential rule for [∃X φ(X)]ψ(X):
        This creates a branch with instantiations for all constants in the domain,
        then evaluates using the restricted existential truth function ∃̌
        
        The evaluation is: ∃̌({⟨φ(c), ψ(c)⟩ | c ∈ domain})
        """
        # Get all constants in current domain
        domain_constants = self._get_domain_constants(context.branch)
        
        if not domain_constants:
            # No constants yet - generate fresh constant for witness
            fresh_constant = self._generate_fresh_constant(context)
            domain_constants = [fresh_constant]
            
            # Add to domain if branch supports it
            if hasattr(context.branch, 'add_to_domain'):
                context.branch.add_to_domain(fresh_constant)
        
        # For tableau construction, we need to create the appropriate branches
        # The restricted existential creates instantiations where we need
        # to track the truth value pairs ⟨φ(c), ψ(c)⟩
        
        instantiated_formulas = []
        for constant in domain_constants:
            substitution = {formula.variable.name: constant}
            
            # Create φ(c) and ψ(c) 
            phi_c = self._substitute_in_formula(formula.antecedent, substitution)
            psi_c = self._substitute_in_formula(formula.consequent, substitution)
            
            # For now, add both to the branch - the evaluation logic
            # will be handled by the model extractor using the ∃̌ truth function
            instantiated_formulas.extend([phi_c, psi_c])
        
        # Return single branch with all instantiations
        # The restricted quantifier evaluation happens during model extraction
        return RuleApplication(
            formulas_for_branches=[instantiated_formulas],
            branch_count=1,
            metadata={
                'rule_name': 'restricted_existential',
                'quantifier_type': 'restricted_existential',
                'variable': formula.variable.name,
                'domain_constants': [c.name for c in domain_constants],
                'antecedent': str(formula.antecedent),
                'consequent': str(formula.consequent)
            }
        )
    
    def _generate_fresh_constant(self, context: RuleContext) -> Constant:
        """Generate a fresh constant for witness generation"""
        # Try to use branch's fresh constant generator if available
        if hasattr(context.branch, 'generate_fresh_constant'):
            return context.branch.generate_fresh_constant('c')
        
        # Fallback: generate based on existing constants in branch
        existing_constants = self._get_existing_constants(context.branch)
        counter = len(existing_constants)
        
        while True:
            candidate_name = f"c_{counter}"
            if candidate_name not in existing_constants:
                return Constant(candidate_name)
            counter += 1
    
    def _get_existing_constants(self, branch: BranchInterface) -> Set[str]:
        """Extract all constant names from formulas in the branch"""
        constants = set()
        
        for formula in branch.formulas:
            constants.update(self._extract_constants_from_formula(formula))
        
        return constants
    
    def _get_domain_constants(self, branch: BranchInterface) -> List[Constant]:
        """Get all constants that should be in the quantification domain"""
        # Try to use branch's domain if available
        if hasattr(branch, 'get_domain_constants'):
            return branch.get_domain_constants()
        
        # Fallback: extract constants from all formulas in branch
        constant_names = set()
        for formula in branch.formulas:
            constant_names.update(self._extract_constants_from_formula(formula))
        
        return [Constant(name) for name in sorted(constant_names)]
    
    def _extract_constants_from_formula(self, formula: Formula) -> Set[str]:
        """Recursively extract constant names from a formula"""
        from formula import Predicate, Negation, Conjunction, Disjunction, Implication
        
        constants = set()
        
        if isinstance(formula, Predicate):
            for arg in formula.args:
                if isinstance(arg, Constant):
                    constants.add(arg.name)
        elif isinstance(formula, Negation):
            constants.update(self._extract_constants_from_formula(formula.operand))
        elif isinstance(formula, (Conjunction, Disjunction, Implication)):
            constants.update(self._extract_constants_from_formula(formula.left))
            constants.update(self._extract_constants_from_formula(formula.right))
        elif isinstance(formula, (RestrictedExistentialFormula, RestrictedUniversalFormula)):
            constants.update(self._extract_constants_from_formula(formula.antecedent))
            constants.update(self._extract_constants_from_formula(formula.consequent))
        
        return constants
    
    def _substitute_in_formula(self, formula: Formula, substitution: Dict[str, Term]) -> Formula:
        """Apply substitution to a formula"""
        if hasattr(formula, 'substitute'):
            # Use formula's built-in substitution if available
            if len(substitution) == 1:
                var_name, term = next(iter(substitution.items()))
                var = Variable(var_name)
                return formula.substitute(var, term)
        
        # Fallback: recursive substitution
        return self._substitute_recursive(formula, substitution)
    
    def _substitute_recursive(self, formula: Formula, substitution: Dict[str, Term]) -> Formula:
        """Recursive substitution implementation"""
        from formula import Predicate, Negation, Conjunction, Disjunction, Implication
        
        if isinstance(formula, Predicate):
            new_args = []
            for arg in formula.args:
                if isinstance(arg, Variable) and arg.name in substitution:
                    new_args.append(substitution[arg.name])
                else:
                    new_args.append(arg)
            return Predicate(formula.predicate_name, new_args)
        
        elif isinstance(formula, Negation):
            new_operand = self._substitute_recursive(formula.operand, substitution)
            return Negation(new_operand)
        
        elif isinstance(formula, Conjunction):
            new_left = self._substitute_recursive(formula.left, substitution)
            new_right = self._substitute_recursive(formula.right, substitution)
            return Conjunction(new_left, new_right)
        
        elif isinstance(formula, Disjunction):
            new_left = self._substitute_recursive(formula.left, substitution)
            new_right = self._substitute_recursive(formula.right, substitution)
            return Disjunction(new_left, new_right)
        
        elif isinstance(formula, Implication):
            new_ante = self._substitute_recursive(formula.antecedent, substitution)
            new_cons = self._substitute_recursive(formula.consequent, substitution)
            return Implication(new_ante, new_cons)
        
        elif isinstance(formula, RestrictedExistentialFormula):
            new_ante = self._substitute_recursive(formula.antecedent, substitution)
            new_cons = self._substitute_recursive(formula.consequent, substitution)
            return RestrictedExistentialFormula(formula.variable, new_ante, new_cons)
        
        elif isinstance(formula, RestrictedUniversalFormula):
            new_ante = self._substitute_recursive(formula.antecedent, substitution)
            new_cons = self._substitute_recursive(formula.consequent, substitution)
            return RestrictedUniversalFormula(formula.variable, new_ante, new_cons)
        
        else:
            # Return formula unchanged if no substitution needed
            return formula


class RestrictedUniversalRule(TableauRule):
    """
    Tableau rule for restricted universal quantifier ∀̌xφ(x).
    
    Based on Ferguson (2021) Definition 9: The rule instantiates the quantifier
    with all constants in the current domain.
    """
    
    @property
    def name(self) -> str:
        return "Restricted Universal Quantifier"
    
    @property
    def rule_type(self) -> RuleType:
        return RuleType.UNIVERSAL_QUANTIFIER  # Maps to existing type
    
    @property
    def priority(self) -> int:
        return 3  # Lower priority to apply after existentials create domain elements
    
    def applies_to(self, formula: Formula) -> bool:
        """Check if this rule applies to restricted universal formulas"""
        return isinstance(formula, RestrictedUniversalFormula)
    
    def apply(self, formula: RestrictedUniversalFormula, context: RuleContext) -> RuleApplication:
        """
        Apply restricted universal rule for [∀X φ(X)]ψ(X):
        This creates instantiations for all constants in the domain,
        then evaluates using the restricted universal truth function ∀̌
        
        The evaluation is: ∀̌({⟨φ(c), ψ(c)⟩ | c ∈ domain})
        """
        # Get all constants in current domain
        domain_constants = self._get_domain_constants(context.branch)
        
        if not domain_constants:
            # No constants yet - generate fresh constant to avoid empty domain
            fresh_constant = self._generate_fresh_constant(context)
            domain_constants = [fresh_constant]
            
            # Add to domain if branch supports it
            if hasattr(context.branch, 'add_to_domain'):
                context.branch.add_to_domain(fresh_constant)
        
        # Create instantiations for the antecedent and consequent pairs
        instantiated_formulas = []
        for constant in domain_constants:
            substitution = {formula.variable.name: constant}
            
            # Create φ(c) and ψ(c) 
            phi_c = self._substitute_in_formula(formula.antecedent, substitution)
            psi_c = self._substitute_in_formula(formula.consequent, substitution)
            
            # For now, add both to the branch - the evaluation logic
            # will be handled by the model extractor using the ∀̌ truth function
            instantiated_formulas.extend([phi_c, psi_c])
        
        # Universal quantifier creates single branch with all instantiations
        # The restricted quantifier evaluation happens during model extraction
        return RuleApplication(
            formulas_for_branches=[instantiated_formulas],
            branch_count=1,
            metadata={
                'rule_name': 'restricted_universal',
                'quantifier_type': 'restricted_universal',
                'variable': formula.variable.name,
                'domain_constants': [c.name for c in domain_constants],
                'antecedent': str(formula.antecedent),
                'consequent': str(formula.consequent)
            }
        )
    
    def _get_domain_constants(self, branch: BranchInterface) -> List[Constant]:
        """Get all constants that should be in the quantification domain"""
        # Try to use branch's domain if available
        if hasattr(branch, 'get_domain_constants'):
            return branch.get_domain_constants()
        
        # Fallback: extract constants from all formulas in branch
        constant_names = set()
        for formula in branch.formulas:
            constant_names.update(self._extract_constants_from_formula(formula))
        
        return [Constant(name) for name in sorted(constant_names)]
    
    def _generate_fresh_constant(self, context: RuleContext) -> Constant:
        """Generate a fresh constant (reuse from existential rule)"""
        existing_constants = set()
        for formula in context.branch.formulas:
            existing_constants.update(self._extract_constants_from_formula(formula))
        
        counter = 0
        while True:
            candidate_name = f"c_{counter}"
            if candidate_name not in existing_constants:
                return Constant(candidate_name)
            counter += 1
    
    def _extract_constants_from_formula(self, formula: Formula) -> Set[str]:
        """Extract constants (reuse from existential rule)"""
        return RestrictedExistentialRule()._extract_constants_from_formula(formula)
    
    def _substitute_in_formula(self, formula: Formula, substitution: Dict[str, Term]) -> Formula:
        """Apply substitution (reuse from existential rule)"""
        return RestrictedExistentialRule()._substitute_in_formula(formula, substitution)


# Export the rules
__all__ = [
    'RestrictedExistentialRule',
    'RestrictedUniversalRule'
]