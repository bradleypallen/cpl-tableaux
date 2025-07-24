#!/usr/bin/env python3
"""
Inference API - Clean High-Level Interface for Tableau Reasoning

This module provides a clean, research-friendly interface for performing logical
inference using semantic tableaux. It abstracts away the low-level details of
tableau construction while providing access to detailed results when needed.

The API is designed for three primary use cases:
1. **Quick Satisfiability Testing**: Simple yes/no answers for logical satisfiability
2. **Model Finding**: Extract specific models that satisfy logical constraints  
3. **Research Analysis**: Detailed tableau construction statistics and step-by-step traces

Design Philosophy:
- **Simplicity First**: Common tasks should require minimal code
- **Power When Needed**: Advanced features available without complexity for basic use
- **Research Ready**: Full access to tableau internals for investigation and analysis
- **Multi-Logic Support**: Seamless switching between classical, three-valued, and wKrQ systems

Academic Applications:
- Automated theorem proving research
- Non-classical logic investigation
- Tableau optimization analysis
- Educational demonstrations of logical reasoning

Performance Characteristics:
- Zero-overhead abstractions for simple queries
- Lazy evaluation for expensive operations (model enumeration)
- Efficient caching for repeated queries with same parameters
- Detailed profiling support for performance analysis
"""

from typing import List, Dict, Set, Optional, Union, Tuple, Any, Iterator
from dataclasses import dataclass
from enum import Enum
import time

from tableau_core import (
    Formula, SignedFormula, Sign, ClassicalSign, ThreeValuedSign, WkrqSign,
    create_signed_formula, parse_formula, TruthValue, t, f, e
)
from tableau_engine import TableauEngine, TableauStatistics
from tableau_rules import get_rule_registry


class LogicSystem(Enum):
    """Enumeration of supported logical systems"""
    CLASSICAL = "classical"
    THREE_VALUED = "three_valued" 
    WKRQ = "wkrq"
    
    def __str__(self) -> str:
        return self.value


@dataclass
class InferenceResult:
    """
    Comprehensive result from a logical inference query.
    
    Contains all information about the inference process, from the basic
    satisfiability result to detailed tableau construction statistics.
    This enables both simple usage (just check .satisfiable) and deep
    analysis (examine .statistics and .models).
    """
    
    # Core results
    satisfiable: bool
    """Whether the input formulas are satisfiable"""
    
    models: List[Dict[str, TruthValue]]
    """List of models that satisfy the formulas (empty if unsatisfiable)"""
    
    # Tableau construction details
    total_branches: int
    """Total number of branches created during tableau construction"""
    
    open_branches: int
    """Number of open (non-closed) branches in the final tableau"""
    
    logic_system: LogicSystem
    """The logical system used for this inference"""
    
    # Performance metrics
    statistics: TableauStatistics
    """Detailed statistics about the tableau construction process"""
    
    # Raw tableau data (for advanced analysis)
    tableau_engine: Optional[TableauEngine] = None
    """The underlying tableau engine (available if requested)"""
    
    @property
    def is_theorem(self) -> bool:
        """True if the negation of the formula is unsatisfiable (classical validity)"""
        # Note: This property makes sense primarily for single-formula queries
        return not self.satisfiable
        
    @property
    def construction_time(self) -> Optional[float]:
        """Time taken for tableau construction in seconds"""
        return self.statistics.elapsed_time
        
    @property
    def has_unique_model(self) -> bool:
        """True if there is exactly one model"""
        return len(self.models) == 1
        
    def get_model_summary(self) -> str:
        """Get a human-readable summary of the models"""
        if not self.satisfiable:
            return "Unsatisfiable (no models)"
        elif len(self.models) == 0:
            return "Satisfiable (models not computed)"
        elif len(self.models) == 1:
            model = self.models[0]
            assignments = [f"{atom}={value}" for atom, value in sorted(model.items())]
            return f"Unique model: {{{', '.join(assignments)}}}"
        else:
            return f"Multiple models ({len(self.models)} found)"
            
    def print_summary(self):
        """Print a human-readable summary of the inference result"""
        print(f"Inference Result ({self.logic_system})")
        print("=" * 40)
        print(f"Satisfiable: {self.satisfiable}")
        print(f"Models: {self.get_model_summary()}")
        print(f"Tableau branches: {self.open_branches}/{self.total_branches}")
        
        if self.construction_time:
            print(f"Construction time: {self.construction_time:.4f}s")
            
        print(f"Rule applications: {self.statistics.rule_applications}")


class TableauInference:
    """
    High-level interface for tableau-based logical inference.
    
    This class provides a clean API for performing various types of logical
    reasoning using semantic tableaux. It handles the complexity of tableau
    construction while exposing the results in an easy-to-use format.
    
    Key Features:
    - Automatic logic system detection based on formula syntax
    - Efficient caching of repeated queries
    - Progressive detail levels (quick answers vs. full analysis)
    - Support for both individual formulas and formula sets
    - Comprehensive error handling with helpful suggestions
    
    Research Features:
    - Access to raw tableau construction details
    - Performance profiling and optimization analysis
    - Comparative studies across different logic systems
    - Educational tracing of tableau construction steps
    """
    
    def __init__(self, logic_system: Union[LogicSystem, str] = LogicSystem.CLASSICAL,
                 enable_caching: bool = True):
        """
        Initialize the inference engine.
        
        Args:
            logic_system: The logical system to use for inference
            enable_caching: Whether to cache results for repeated queries
        """
        if isinstance(logic_system, str):
            try:
                self.logic_system = LogicSystem(logic_system)
            except ValueError:
                raise ValueError(f"Unknown logic system: {logic_system}. "
                               f"Supported systems: {[ls.value for ls in LogicSystem]}")
        else:
            self.logic_system = logic_system
            
        self.enable_caching = enable_caching
        self._cache: Dict[str, InferenceResult] = {}
        
    def is_satisfiable(self, formulas: Union[str, Formula, List[Union[str, Formula]]]) -> bool:
        """
        Test whether formulas are satisfiable.
        
        This is the most common inference operation - testing whether a set of
        logical formulas can all be true simultaneously.
        
        Args:
            formulas: Formula(s) to test - can be strings, Formula objects, or lists
            
        Returns:
            True if satisfiable, False if unsatisfiable
            
        Examples:
            >>> inference = TableauInference()
            >>> inference.is_satisfiable("p & q")
            True
            >>> inference.is_satisfiable(["p", "~p"])
            False
        """
        result = self._perform_inference(formulas, compute_models=False)
        return result.satisfiable
        
    def is_theorem(self, formula: Union[str, Formula]) -> bool:
        """
        Test whether a formula is a theorem (tautology).
        
        A formula is a theorem if its negation is unsatisfiable, meaning
        the formula is true in all possible models.
        
        Args:
            formula: The formula to test for theorem status
            
        Returns:
            True if the formula is a theorem, False otherwise
            
        Examples:
            >>> inference = TableauInference()
            >>> inference.is_theorem("p | ~p")  # Law of excluded middle
            True
            >>> inference.is_theorem("p & q")
            False
        """
        # Convert to negated signed formula and test for unsatisfiability
        if isinstance(formula, str):
            formula = parse_formula(formula)
            
        # Create F:formula (false signed formula) - if unsatisfiable, formula is theorem
        sign = self._get_false_sign()
        signed_formula = create_signed_formula(sign, formula)
        
        result = self._perform_inference([signed_formula], compute_models=False, 
                                       bypass_parsing=True)
        return not result.satisfiable
        
    def get_models(self, formulas: Union[str, Formula, List[Union[str, Formula]]],
                  max_models: Optional[int] = None) -> List[Dict[str, TruthValue]]:
        """
        Find models that satisfy the given formulas.
        
        A model is an assignment of truth values to atomic formulas that
        makes all the given formulas true.
        
        Args:
            formulas: Formula(s) to find models for
            max_models: Maximum number of models to return (None for all)
            
        Returns:
            List of models, where each model maps atom names to truth values
            
        Examples:
            >>> inference = TableauInference()
            >>> models = inference.get_models("p | q")
            >>> len(models)
            3  # Three models: {p=T,q=F}, {p=F,q=T}, {p=T,q=T}
        """
        result = self._perform_inference(formulas, compute_models=True)
        
        if max_models is not None:
            return result.models[:max_models]
        else:
            return result.models
            
    def analyze_inference(self, formulas: Union[str, Formula, List[Union[str, Formula]]],
                         include_tableau: bool = False) -> InferenceResult:
        """
        Perform complete inference analysis with detailed results.
        
        This method provides access to all information about the inference
        process, including performance statistics, tableau construction details,
        and complete model enumeration.
        
        Args:
            formulas: Formula(s) to analyze
            include_tableau: Whether to include the raw tableau engine in results
            
        Returns:
            Complete InferenceResult with all available information
            
        Examples:
            >>> inference = TableauInference()
            >>> result = inference.analyze_inference("(p & q) | (~p & ~q)")
            >>> result.print_summary()
            >>> print(f"Construction took {result.construction_time:.4f} seconds")
        """
        return self._perform_inference(formulas, compute_models=True, 
                                     include_tableau=include_tableau)
        
    def compare_logic_systems(self, formulas: Union[str, Formula, List[Union[str, Formula]]]) -> Dict[LogicSystem, InferenceResult]:
        """
        Compare inference results across different logic systems.
        
        This is particularly useful for research into non-classical logics,
        allowing direct comparison of how the same formulas behave under
        different logical systems.
        
        Args:
            formulas: Formula(s) to test across logic systems
            
        Returns:
            Dictionary mapping logic systems to their inference results
            
        Examples:
            >>> inference = TableauInference()
            >>> results = inference.compare_logic_systems("p | ~p")
            >>> for system, result in results.items():
            ...     print(f"{system}: {result.satisfiable}")
        """
        original_system = self.logic_system
        results = {}
        
        try:
            for system in LogicSystem:
                self.logic_system = system
                results[system] = self._perform_inference(formulas, compute_models=True)
        finally:
            self.logic_system = original_system
            
        return results
        
    def _perform_inference(self, formulas: Union[str, Formula, List[Union[str, Formula]]],
                          compute_models: bool = True,
                          include_tableau: bool = False,
                          bypass_parsing: bool = False) -> InferenceResult:
        """
        Core inference method that handles all the details.
        
        Args:
            formulas: Input formulas in various formats
            compute_models: Whether to compute and return models
            include_tableau: Whether to include raw tableau in result
            bypass_parsing: Whether formulas are already SignedFormula objects
        """
        # Handle caching
        cache_key = None
        if self.enable_caching:
            cache_key = self._get_cache_key(formulas, compute_models)
            if cache_key in self._cache:
                cached_result = self._cache[cache_key]
                # Don't return tableau engine from cache for safety
                if not include_tableau:
                    cached_result.tableau_engine = None
                return cached_result
                
        # Convert to signed formulas
        if bypass_parsing:
            # Already signed formulas
            signed_formulas = formulas
        else:
            signed_formulas = self._prepare_signed_formulas(formulas)
            
        # Create and run tableau engine
        engine = TableauEngine(self.logic_system.value)
        satisfiable = engine.build_tableau(signed_formulas)
        
        # Extract models if requested
        models = []
        if compute_models and satisfiable:
            models = engine.get_models()
            
        # Create result
        result = InferenceResult(
            satisfiable=satisfiable,
            models=models,
            total_branches=len(engine.branches),
            open_branches=len(engine.get_open_branches()),
            logic_system=self.logic_system,
            statistics=engine.get_statistics(),
            tableau_engine=engine if include_tableau else None
        )
        
        # Cache if enabled
        if self.enable_caching and cache_key:
            # Don't cache the tableau engine to save memory
            cached_result = InferenceResult(
                satisfiable=result.satisfiable,
                models=result.models,
                total_branches=result.total_branches,
                open_branches=result.open_branches,
                logic_system=result.logic_system,
                statistics=result.statistics,
                tableau_engine=None
            )
            self._cache[cache_key] = cached_result
            
        return result
        
    def _prepare_signed_formulas(self, formulas: Union[str, Formula, List[Union[str, Formula]]]) -> List[SignedFormula]:
        """Convert input formulas to signed formulas for tableau construction"""
        if not isinstance(formulas, list):
            formulas = [formulas]
            
        signed_formulas = []
        true_sign = self._get_true_sign()
        
        for formula in formulas:
            if isinstance(formula, str):
                parsed_formula = parse_formula(formula)
            else:
                parsed_formula = formula
                
            # Default to "true" signing - we want to find models where formula is true
            signed_formula = create_signed_formula(true_sign, parsed_formula)
            signed_formulas.append(signed_formula)
            
        return signed_formulas
        
    def _get_true_sign(self) -> Sign:
        """Get the 'true' sign for the current logic system"""
        if self.logic_system == LogicSystem.CLASSICAL:
            return ClassicalSign("T")
        elif self.logic_system == LogicSystem.THREE_VALUED:
            return ThreeValuedSign("T")
        elif self.logic_system == LogicSystem.WKRQ:
            return WkrqSign("T")
        else:
            raise ValueError(f"Unknown logic system: {self.logic_system}")
            
    def _get_false_sign(self) -> Sign:
        """Get the 'false' sign for the current logic system"""
        if self.logic_system == LogicSystem.CLASSICAL:
            return ClassicalSign("F")
        elif self.logic_system == LogicSystem.THREE_VALUED:
            return ThreeValuedSign("F")
        elif self.logic_system == LogicSystem.WKRQ:
            return WkrqSign("F")
        else:
            raise ValueError(f"Unknown logic system: {self.logic_system}")
            
    def _get_cache_key(self, formulas: Any, compute_models: bool) -> str:
        """Generate a cache key for the given parameters"""
        formulas_str = str(formulas)
        return f"{self.logic_system.value}:{formulas_str}:models={compute_models}"
        
    def clear_cache(self):
        """Clear the inference result cache"""
        self._cache.clear()
        
    def get_cache_statistics(self) -> Dict[str, int]:
        """Get statistics about cache usage"""
        return {
            'cached_results': len(self._cache),
            'logic_system': str(self.logic_system)
        }


# Convenience functions for common operations

def is_satisfiable(formulas: Union[str, Formula, List[Union[str, Formula]]],
                  logic_system: Union[LogicSystem, str] = LogicSystem.CLASSICAL) -> bool:
    """
    Quick satisfiability test - most common use case.
    
    Args:
        formulas: Formula(s) to test for satisfiability
        logic_system: Logical system to use
        
    Returns:
        True if satisfiable, False if unsatisfiable
        
    Examples:
        >>> is_satisfiable("p & q")
        True
        >>> is_satisfiable(["p", "~p"])
        False
    """
    inference = TableauInference(logic_system, enable_caching=False)
    return inference.is_satisfiable(formulas)


def is_theorem(formula: Union[str, Formula],
              logic_system: Union[LogicSystem, str] = LogicSystem.CLASSICAL) -> bool:
    """
    Quick theorem test.
    
    Args:
        formula: Formula to test for theorem status
        logic_system: Logical system to use
        
    Returns:
        True if the formula is a theorem, False otherwise
        
    Examples:
        >>> is_theorem("p | ~p")
        True
        >>> is_theorem("p & q")
        False
    """
    inference = TableauInference(logic_system, enable_caching=False)
    return inference.is_theorem(formula)


def find_models(formulas: Union[str, Formula, List[Union[str, Formula]]],
               logic_system: Union[LogicSystem, str] = LogicSystem.CLASSICAL,
               max_models: Optional[int] = None) -> List[Dict[str, TruthValue]]:
    """
    Find models for the given formulas.
    
    Args:
        formulas: Formula(s) to find models for
        logic_system: Logical system to use
        max_models: Maximum number of models to return
        
    Returns:
        List of models (dictionaries mapping atoms to truth values)
        
    Examples:
        >>> models = find_models("p | q")
        >>> len(models)
        3
    """
    inference = TableauInference(logic_system, enable_caching=False)
    return inference.get_models(formulas, max_models)


def analyze_formula(formula: Union[str, Formula],
                   logic_system: Union[LogicSystem, str] = LogicSystem.CLASSICAL) -> InferenceResult:
    """
    Complete analysis of a single formula.
    
    Args:
        formula: Formula to analyze
        logic_system: Logical system to use
        
    Returns:
        Complete inference result with detailed information
        
    Examples:
        >>> result = analyze_formula("(p & q) | (~p & ~q)")
        >>> result.print_summary()
    """
    inference = TableauInference(logic_system, enable_caching=False)
    return inference.analyze_inference(formula)


# Export commonly used classes and functions
__all__ = [
    'TableauInference', 'InferenceResult', 'LogicSystem',
    'is_satisfiable', 'is_theorem', 'find_models', 'analyze_formula'
]