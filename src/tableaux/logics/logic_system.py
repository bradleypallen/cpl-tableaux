#!/usr/bin/env python3
"""
Logic system abstraction and registry for extensible tableau framework.

This module provides the base LogicSystem class and registry that allows
users to define and register new logic systems as plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional, Type, Callable
from dataclasses import dataclass, field

from ..core.formula import Formula, ConnectiveSpec
from ..core.semantics import TruthValueSystem
from ..core.signs import SignSystem, SignedFormula
from ..core.rules import RuleSet, TableauRule


class LogicSystem(ABC):
    """Abstract base class for logic systems."""
    
    def __init__(self, name: str):
        self.name = name
        self.connectives: Dict[str, ConnectiveSpec] = {}
        self.truth_system: Optional[TruthValueSystem] = None
        self.sign_system: Optional[SignSystem] = None
        self.rule_set = RuleSet()
        self._initialized = False
    
    @abstractmethod
    def initialize(self):
        """Initialize the logic system (called once during registration)."""
        pass
    
    def ensure_initialized(self):
        """Ensure the logic system has been initialized."""
        if not self._initialized:
            self.initialize()
            self._initialized = True
    
    def add_connective(self, spec: ConnectiveSpec):
        """Add a connective to this logic system."""
        self.connectives[spec.symbol] = spec
    
    def set_truth_system(self, truth_system: TruthValueSystem):
        """Set the truth value system for this logic."""
        self.truth_system = truth_system
    
    def set_sign_system(self, sign_system: SignSystem):
        """Set the sign system for this logic."""
        self.sign_system = sign_system
    
    def add_rule(self, rule: TableauRule):
        """Add a tableau rule to this logic system."""
        self.rule_set.add_rule(rule)
    
    def add_rules(self, rules: List[TableauRule]):
        """Add multiple tableau rules to this logic system."""
        for rule in rules:
            self.add_rule(rule)
    
    def get_connective(self, symbol: str) -> Optional[ConnectiveSpec]:
        """Get connective specification by symbol."""
        self.ensure_initialized()
        return self.connectives.get(symbol)
    
    def get_truth_system(self) -> TruthValueSystem:
        """Get the truth value system."""
        self.ensure_initialized()
        if not self.truth_system:
            raise ValueError(f"Logic system {self.name} has no truth system configured")
        return self.truth_system
    
    def get_sign_system(self) -> SignSystem:
        """Get the sign system."""
        self.ensure_initialized()
        if not self.sign_system:
            raise ValueError(f"Logic system {self.name} has no sign system configured")
        return self.sign_system
    
    def get_rule_set(self) -> RuleSet:
        """Get the rule set."""
        self.ensure_initialized()
        return self.rule_set


class LogicRegistry:
    """Registry for logic systems."""
    
    _systems: Dict[str, LogicSystem] = {}
    _aliases: Dict[str, str] = {}
    
    @classmethod
    def register(cls, system: LogicSystem, aliases: List[str] = None):
        """Register a logic system with optional aliases."""
        if system.name in cls._systems:
            raise ValueError(f"Logic system '{system.name}' already registered")
        
        cls._systems[system.name] = system
        
        # Register aliases
        if aliases:
            for alias in aliases:
                if alias in cls._aliases:
                    raise ValueError(f"Alias '{alias}' already in use")
                cls._aliases[alias] = system.name
    
    @classmethod
    def get(cls, name: str) -> LogicSystem:
        """Get a logic system by name or alias."""
        # Check if it's an alias
        if name in cls._aliases:
            name = cls._aliases[name]
        
        if name not in cls._systems:
            raise ValueError(f"Unknown logic system: {name}")
        
        system = cls._systems[name]
        system.ensure_initialized()
        return system
    
    @classmethod
    def list_systems(cls) -> List[str]:
        """List all registered logic systems."""
        return list(cls._systems.keys())
    
    @classmethod
    def list_aliases(cls) -> Dict[str, str]:
        """List all aliases and their targets."""
        return cls._aliases.copy()
    
    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a logic system is registered."""
        return name in cls._systems or name in cls._aliases
    
    @classmethod
    def unregister(cls, name: str):
        """Unregister a logic system (mainly for testing)."""
        if name in cls._systems:
            del cls._systems[name]
        
        # Remove any aliases pointing to this system
        aliases_to_remove = [alias for alias, target in cls._aliases.items() if target == name]
        for alias in aliases_to_remove:
            del cls._aliases[alias]


@dataclass
class LogicExtension:
    """Helper class for building logic system extensions."""
    name: str
    base_system: Optional[str] = None
    connectives: List[ConnectiveSpec] = field(default_factory=list)
    truth_system: Optional[TruthValueSystem] = None
    sign_system: Optional[SignSystem] = None
    rules: List[TableauRule] = field(default_factory=list)
    
    def build(self) -> LogicSystem:
        """Build a concrete logic system from this extension."""
        if self.base_system:
            # Extend existing system
            base = LogicRegistry.get(self.base_system)
            system = ExtendedLogicSystem(self.name, base)
        else:
            # Create new system
            system = ConcreteLogicSystem(self.name)
        
        # Add components
        for spec in self.connectives:
            system.add_connective(spec)
        
        if self.truth_system:
            system.set_truth_system(self.truth_system)
        
        if self.sign_system:
            system.set_sign_system(self.sign_system)
        
        system.add_rules(self.rules)
        
        return system


class ConcreteLogicSystem(LogicSystem):
    """A concrete logic system implementation."""
    
    def __init__(self, name: str):
        super().__init__(name)
    
    def initialize(self):
        """Default initialization - subclasses can override."""
        pass


class ExtendedLogicSystem(LogicSystem):
    """A logic system that extends another system."""
    
    def __init__(self, name: str, base_system: LogicSystem):
        super().__init__(name)
        self.base_system = base_system
    
    def initialize(self):
        """Initialize by copying from base system."""
        self.base_system.ensure_initialized()
        
        # Copy connectives
        self.connectives.update(self.base_system.connectives)
        
        # Copy systems if not overridden
        if not self.truth_system:
            self.truth_system = self.base_system.truth_system
        
        if not self.sign_system:
            self.sign_system = self.base_system.sign_system
        
        # Copy rules
        for rule in self.base_system.rule_set.rules:
            self.rule_set.add_rule(rule)


def create_logic_system(name: str, 
                       connectives: List[ConnectiveSpec] = None,
                       truth_system: TruthValueSystem = None,
                       sign_system: SignSystem = None,
                       rules: List[TableauRule] = None,
                       base_system: str = None) -> LogicSystem:
    """
    Convenience function for creating logic systems.
    
    Args:
        name: Name of the logic system
        connectives: List of connective specifications
        truth_system: Truth value system
        sign_system: Sign system  
        rules: List of tableau rules
        base_system: Name of base system to extend
    
    Returns:
        Configured LogicSystem instance
    """
    extension = LogicExtension(
        name=name,
        base_system=base_system,
        connectives=connectives or [],
        truth_system=truth_system,
        sign_system=sign_system,
        rules=rules or []
    )
    
    return extension.build()


# Decorators for easy logic system definition
def logic_system(name: str, aliases: List[str] = None):
    """Decorator for defining and registering logic systems."""
    def decorator(cls):
        # Create instance and register
        system = cls(name)
        LogicRegistry.register(system, aliases)
        return cls
    return decorator


def extends_logic(base_name: str):
    """Decorator for logic systems that extend another system."""
    def decorator(cls):
        original_init = cls.__init__
        
        def new_init(self, name: str):
            base = LogicRegistry.get(base_name)
            ExtendedLogicSystem.__init__(self, name, base)
            # Call original init if it exists
            if hasattr(cls, '_original_init'):
                cls._original_init(self, name)
        
        cls._original_init = original_init
        cls.__init__ = new_init
        return cls
    return decorator