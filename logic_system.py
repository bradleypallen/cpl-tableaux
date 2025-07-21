#!/usr/bin/env python3
"""
Logic System Registry

Defines the LogicSystem class that combines rules and logic-specific components
to create complete tableau systems for different logics.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from tableau_rules import (
    TableauRule, BranchFactory, ClosureDetector, ModelExtractor,
    LiteralRecognizer, SubsumptionDetector, BranchInterface, RuleContext
)
from formula import Formula


@dataclass
class LogicSystemConfig:
    """Configuration for a logic system"""
    name: str
    description: str
    supports_quantifiers: bool = False
    supports_modality: bool = False
    truth_values: int = 2  # 2 for classical, 3 for WK3, 4 for FDE, etc.
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LogicSystem:
    """
    A complete logic system combining tableau rules with logic-specific components.
    
    This class serves as the central registry for a particular logic variant,
    containing all the components needed to build and run tableaux for that logic.
    """
    
    def __init__(self,
                 config: LogicSystemConfig,
                 rules: List[TableauRule],
                 branch_factory: BranchFactory,
                 closure_detector: ClosureDetector,
                 model_extractor: ModelExtractor,
                 literal_recognizer: LiteralRecognizer,
                 subsumption_detector: SubsumptionDetector):
        """
        Initialize a logic system with its components.
        
        Args:
            config: Configuration and metadata for this logic
            rules: List of tableau expansion rules
            branch_factory: Factory for creating branches
            closure_detector: Detector for branch contradictions
            model_extractor: Extractor for satisfying models
            literal_recognizer: Recognizer for literal formulas
            subsumption_detector: Detector for branch subsumption
        """
        self.config = config
        self.rules = list(rules)  # Make a copy to allow modification
        self.branch_factory = branch_factory
        self.closure_detector = closure_detector
        self.model_extractor = model_extractor
        self.literal_recognizer = literal_recognizer
        self.subsumption_detector = subsumption_detector
        
        # Build rule lookup maps for efficiency
        self._rule_cache = {}
        self._build_rule_cache()
    
    def _build_rule_cache(self):
        """Build caches for efficient rule lookup"""
        self._rule_cache = {}
        # Group rules by their applicability for faster lookup
        for rule in self.rules:
            # We'll populate this during runtime as formulas are encountered
            pass
    
    def find_applicable_rules(self, formula: Formula) -> List[TableauRule]:
        """Find all rules that can be applied to the given formula"""
        applicable_rules = []
        for rule in self.rules:
            if rule.applies_to(formula):
                applicable_rules.append(rule)
        
        # Sort by priority (α-rules before β-rules)
        applicable_rules.sort(key=lambda r: r.priority)
        return applicable_rules
    
    def get_best_rule(self, formula: Formula) -> Optional[TableauRule]:
        """Get the best (highest priority) rule applicable to the formula"""
        applicable_rules = self.find_applicable_rules(formula)
        return applicable_rules[0] if applicable_rules else None
    
    def apply_rule(self, rule: TableauRule, formula: Formula, context: RuleContext):
        """Apply a rule to a formula in the given context"""
        if not rule.applies_to(formula):
            raise ValueError(f"Rule {rule.name} does not apply to formula {formula}")
        
        return rule.apply(formula, context)
    
    def is_literal(self, formula: Formula) -> bool:
        """Check if a formula is a literal using the logic's recognizer"""
        return self.literal_recognizer.is_literal(formula)
    
    def is_branch_closed(self, branch: BranchInterface) -> bool:
        """Check if a branch is closed using the logic's detector"""
        return self.closure_detector.is_closed(branch)
    
    def get_closure_reason(self, branch: BranchInterface) -> Optional[str]:
        """Get explanation for why a branch is closed"""
        return self.closure_detector.get_closure_reason(branch)
    
    def extract_model(self, branch: BranchInterface) -> Any:
        """Extract a model from an open branch"""
        return self.model_extractor.extract_model(branch)
    
    def extract_all_models(self, branches: List[BranchInterface]) -> List[Any]:
        """Extract all models from a list of open branches"""
        return self.model_extractor.extract_all_models(branches)
    
    def create_branch(self, branch_id: int, formulas: List[Formula] = None) -> BranchInterface:
        """Create a new branch using the logic's factory"""
        return self.branch_factory.create_branch(branch_id, formulas)
    
    def copy_branch(self, source_branch: BranchInterface, new_id: int) -> BranchInterface:
        """Copy a branch using the logic's factory"""
        return self.branch_factory.copy_branch(source_branch, new_id)
    
    def remove_subsumed_branches(self, branches: List[BranchInterface]) -> List[BranchInterface]:
        """Remove subsumed branches using the logic's detector"""
        return self.subsumption_detector.remove_subsumed_branches(branches)
    
    def add_rule(self, rule: TableauRule) -> None:
        """Add a new rule to this logic system"""
        self.rules.append(rule)
        # Sort rules by priority to maintain efficiency
        self.rules.sort(key=lambda r: r.priority)
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule by name, return True if removed"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                return True
        return False
    
    def get_rule(self, rule_name: str) -> Optional[TableauRule]:
        """Get a rule by name"""
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None
    
    def list_rules(self) -> List[str]:
        """Get list of all rule names in this system"""
        return [rule.name for rule in self.rules]
    
    def describe(self) -> str:
        """Get a description of this logic system"""
        rule_count = len(self.rules)
        alpha_rules = len([r for r in self.rules if r.is_alpha_rule])
        beta_rules = len([r for r in self.rules if r.is_beta_rule])
        
        description = f"Logic System: {self.config.name}\n"
        description += f"Description: {self.config.description}\n"
        description += f"Truth Values: {self.config.truth_values}\n"
        description += f"Total Rules: {rule_count} ({alpha_rules} α-rules, {beta_rules} β-rules)\n"
        description += f"Supports Quantifiers: {self.config.supports_quantifiers}\n"
        description += f"Supports Modality: {self.config.supports_modality}\n"
        
        if self.rules:
            description += "\nRules:\n"
            for rule in sorted(self.rules, key=lambda r: r.priority):
                rule_type = "α" if rule.is_alpha_rule else "β" if rule.is_beta_rule else "γ"
                description += f"  {rule_type}-rule: {rule.name}\n"
        
        return description
    
    def validate_completeness(self) -> List[str]:
        """
        Validate that this logic system has all necessary rules for completeness.
        Returns a list of warnings about potentially missing rules.
        """
        warnings = []
        
        # Check for basic propositional connectives
        rule_types = {rule.rule_type for rule in self.rules}
        
        from tableau_rules import RuleType
        basic_rules = {
            RuleType.CONJUNCTION, RuleType.DISJUNCTION, RuleType.IMPLICATION,
            RuleType.NEG_CONJUNCTION, RuleType.NEG_DISJUNCTION, RuleType.NEG_IMPLICATION,
            RuleType.DOUBLE_NEGATION
        }
        
        missing_basic = basic_rules - rule_types
        if missing_basic:
            warnings.append(f"Missing basic propositional rules: {missing_basic}")
        
        # Logic-specific checks
        if self.config.supports_quantifiers:
            quantifier_rules = {RuleType.UNIVERSAL_QUANTIFIER, RuleType.EXISTENTIAL_QUANTIFIER}
            missing_quantifier = quantifier_rules - rule_types
            if missing_quantifier:
                warnings.append(f"Logic claims quantifier support but missing rules: {missing_quantifier}")
        
        if self.config.supports_modality:
            modal_rules = {RuleType.MODAL_NECESSITY, RuleType.MODAL_POSSIBILITY}
            missing_modal = modal_rules - rule_types
            if missing_modal:
                warnings.append(f"Logic claims modal support but missing rules: {missing_modal}")
        
        return warnings


# Registry for built-in logic systems
_LOGIC_REGISTRY: Dict[str, LogicSystem] = {}


def register_logic_system(name: str, logic_system: LogicSystem) -> None:
    """Register a logic system in the global registry"""
    _LOGIC_REGISTRY[name] = logic_system


def get_logic_system(name: str) -> Optional[LogicSystem]:
    """Get a logic system from the registry"""
    return _LOGIC_REGISTRY.get(name)


def list_logic_systems() -> List[str]:
    """List all registered logic systems"""
    return list(_LOGIC_REGISTRY.keys())


def unregister_logic_system(name: str) -> bool:
    """Remove a logic system from the registry"""
    if name in _LOGIC_REGISTRY:
        del _LOGIC_REGISTRY[name]
        return True
    return False


# Export the main classes and functions
__all__ = [
    'LogicSystemConfig',
    'LogicSystem',
    'register_logic_system',
    'get_logic_system', 
    'list_logic_systems',
    'unregister_logic_system'
]