#!/usr/bin/env python3
"""
Tableau Rule System

Defines the abstract interfaces and data structures for a componentized
tableau rule system that supports multiple logic variants.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Optional, Union, Dict, Any, Protocol
from dataclasses import dataclass

from formula import Formula


class RuleType(Enum):
    """Classification of tableau expansion rules"""
    # α-rules (non-branching, add formulas to same branch)
    DOUBLE_NEGATION = auto()    # ¬¬A → A
    CONJUNCTION = auto()        # A ∧ B → A, B
    NEG_DISJUNCTION = auto()    # ¬(A ∨ B) → ¬A, ¬B
    NEG_IMPLICATION = auto()    # ¬(A → B) → A, ¬B
    
    # β-rules (branching, split into multiple branches)
    DISJUNCTION = auto()        # A ∨ B → A | B
    NEG_CONJUNCTION = auto()    # ¬(A ∧ B) → ¬A | ¬B
    IMPLICATION = auto()        # A → B → ¬A | B
    
    # Extension points for future logics
    UNIVERSAL_QUANTIFIER = auto()     # ∀x φ(x)
    EXISTENTIAL_QUANTIFIER = auto()   # ∃x φ(x)
    MODAL_NECESSITY = auto()          # □A
    MODAL_POSSIBILITY = auto()        # ◊A
    TEMPORAL_NEXT = auto()            # ○A
    TEMPORAL_ALWAYS = auto()          # □A (temporal)
    TEMPORAL_EVENTUALLY = auto()      # ◊A (temporal)


@dataclass
class RuleApplication:
    """Result of applying a tableau rule"""
    # New formulas to add to branches
    formulas_for_branches: List[List[Formula]]
    # Number of branches this creates (1 for α-rules, >1 for β-rules)
    branch_count: int
    # Optional metadata for logic-specific information
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_branching(self) -> bool:
        """Return True if this application causes branching"""
        return self.branch_count > 1


class BranchInterface(Protocol):
    """Protocol defining the interface that branch implementations must provide"""
    
    @property
    def id(self) -> int:
        """Unique identifier for this branch"""
        ...
    
    @property
    def is_closed(self) -> bool:
        """Whether this branch is closed (contradictory)"""
        ...
    
    @property
    def formulas(self) -> List[Formula]:
        """All formulas currently in this branch"""
        ...
    
    def add_formula(self, formula: Formula) -> None:
        """Add a formula to this branch"""
        ...
    
    def copy(self) -> 'BranchInterface':
        """Create a deep copy of this branch"""
        ...


@dataclass
class RuleContext:
    """Context information provided to rules during application"""
    tableau: Any  # The tableau instance (avoid circular import)
    branch: BranchInterface
    parent_node: Optional[Any] = None  # TableauNode if tree tracking enabled
    depth: int = 0
    applied_rules: List[str] = None  # Track rule application history
    
    def __post_init__(self):
        if self.applied_rules is None:
            self.applied_rules = []


class TableauRule(ABC):
    """Abstract base class for all tableau expansion rules"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this rule"""
        pass
    
    @property
    @abstractmethod
    def rule_type(self) -> RuleType:
        """The type/classification of this rule"""
        pass
    
    @abstractmethod
    def applies_to(self, formula: Formula) -> bool:
        """Check if this rule can be applied to the given formula"""
        pass
    
    @abstractmethod
    def apply(self, formula: Formula, context: RuleContext) -> RuleApplication:
        """Apply this rule to the formula in the given context"""
        pass
    
    @property
    def is_alpha_rule(self) -> bool:
        """Return True if this is an α-rule (non-branching)"""
        return self.rule_type in {
            RuleType.DOUBLE_NEGATION,
            RuleType.CONJUNCTION,
            RuleType.NEG_DISJUNCTION,
            RuleType.NEG_IMPLICATION
        }
    
    @property
    def is_beta_rule(self) -> bool:
        """Return True if this is a β-rule (branching)"""
        return self.rule_type in {
            RuleType.DISJUNCTION,
            RuleType.NEG_CONJUNCTION,
            RuleType.IMPLICATION
        }
    
    @property
    def priority(self) -> int:
        """Priority for rule application (lower = higher priority)"""
        # α-rules get higher priority than β-rules for efficiency
        if self.is_alpha_rule:
            return 1
        elif self.is_beta_rule:
            return 2
        else:
            # Extension rules get lowest priority by default
            return 3


class ClosureDetector(ABC):
    """Abstract interface for detecting branch closure (contradictions)"""
    
    @abstractmethod
    def is_closed(self, branch: BranchInterface) -> bool:
        """Check if the branch contains a contradiction"""
        pass
    
    @abstractmethod
    def get_closure_reason(self, branch: BranchInterface) -> Optional[str]:
        """Get human-readable explanation of why branch is closed"""
        pass


class ModelExtractor(ABC):
    """Abstract interface for extracting models from open branches"""
    
    @abstractmethod
    def extract_model(self, branch: BranchInterface) -> Any:
        """Extract a satisfying model from an open branch"""
        pass
    
    @abstractmethod
    def extract_all_models(self, branches: List[BranchInterface]) -> List[Any]:
        """Extract all satisfying models from a list of open branches"""
        pass


class BranchFactory(ABC):
    """Abstract factory for creating logic-specific branch implementations"""
    
    @abstractmethod
    def create_branch(self, branch_id: int, formulas: List[Formula] = None) -> BranchInterface:
        """Create a new branch with optional initial formulas"""
        pass
    
    @abstractmethod
    def copy_branch(self, source_branch: BranchInterface, new_id: int) -> BranchInterface:
        """Create a copy of an existing branch with a new ID"""
        pass


class LiteralRecognizer(ABC):
    """Abstract interface for recognizing when formulas are literals"""
    
    @abstractmethod
    def is_literal(self, formula: Formula) -> bool:
        """Check if a formula is a literal (cannot be expanded further)"""
        pass
    
    @abstractmethod
    def get_literal_value(self, formula: Formula, branch: BranchInterface) -> Any:
        """Get the truth value assignment for a literal in the branch context"""
        pass


class SubsumptionDetector(ABC):
    """Abstract interface for detecting branch subsumption"""
    
    @abstractmethod
    def is_subsumed(self, branch: BranchInterface, other_branches: List[BranchInterface]) -> bool:
        """Check if a branch is subsumed by any other branch"""
        pass
    
    @abstractmethod
    def remove_subsumed_branches(self, branches: List[BranchInterface]) -> List[BranchInterface]:
        """Remove all subsumed branches from a list"""
        pass


# Export the main interfaces
__all__ = [
    'RuleType',
    'RuleApplication', 
    'BranchInterface',
    'RuleContext',
    'TableauRule',
    'ClosureDetector',
    'ModelExtractor', 
    'BranchFactory',
    'LiteralRecognizer',
    'SubsumptionDetector'
]