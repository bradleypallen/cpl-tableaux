#!/usr/bin/env python3
"""
Mode-Aware Formula Parser

Provides separate parsing logic for propositional and first-order modes
with proper validation and error handling for each logic system.
"""

import re
from typing import List, Optional, Union
from logic_mode import LogicMode, ModeValidator, ModeError, get_mode_validator
from formula import Formula, Atom, Predicate, Negation, Conjunction, Disjunction, Implication
from term import Constant, Variable, parse_term


class ModeAwareParser:
    """Parser that respects logic mode constraints"""
    
    def __init__(self, mode: LogicMode):
        self.mode = mode
        self.validator = get_mode_validator(mode)
        self.tokens = []
        self.pos = 0
    
    def parse(self, formula_str: str) -> Formula:
        """Parse a formula string according to the current logic mode"""
        self.tokens = self._tokenize(formula_str)
        self.pos = 0
        
        if not self.tokens:
            raise ModeError("Empty formula", self.mode)
        
        try:
            result = self._parse_implication()
            
            if self.pos < len(self.tokens):
                raise ModeError(f"Unexpected token: {self.tokens[self.pos]}", self.mode)
            
            return result
            
        except ModeError:
            raise  # Re-raise mode errors as-is
        except Exception as e:
            # Convert other parsing errors to mode errors with helpful suggestions
            suggestions = self.validator.get_syntax_description()
            raise ModeError(f"Parse error: {e}", self.mode, suggestions)
    
    def _tokenize(self, formula_str: str) -> List[str]:
        """Convert formula string to tokens"""
        # Replace symbols with standardized representations
        formula_str = formula_str.replace('¬', '~')
        formula_str = formula_str.replace('∧', '&')
        formula_str = formula_str.replace('∨', '|')
        formula_str = formula_str.replace('→', '->')
        formula_str = formula_str.replace('↔', '<->')
        
        # Tokenize using regex - handle predicate applications
        if self.mode == LogicMode.FIRST_ORDER:
            # FOL pattern: handles Predicate(arg1, arg2, ...)
            pattern = r'(\w+\([^)]*\)|\w+|->|<->|[()&|~,])'
        else:
            # Propositional pattern: simpler
            pattern = r'(\w+|->|<->|[()&|~])'
        
        tokens = re.findall(pattern, formula_str)
        return [token.strip() for token in tokens if token.strip()]
    
    def _current_token(self) -> Optional[str]:
        """Get current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def _consume(self, expected: Optional[str] = None) -> str:
        """Consume and return current token"""
        if self.pos >= len(self.tokens):
            raise ModeError("Unexpected end of formula", self.mode)
        
        token = self.tokens[self.pos]
        self.pos += 1
        
        if expected and token != expected:
            raise ModeError(f"Expected '{expected}' but got '{token}'", self.mode)
        
        return token
    
    def _peek(self, offset: int = 0) -> Optional[str]:
        """Peek at token without consuming"""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    # Grammar rules (same precedence as original parser)
    
    def _parse_implication(self) -> Formula:
        """Parse implication (lowest precedence)"""
        left = self._parse_disjunction()
        
        while self._current_token() in ['->', '<->']:
            op = self._consume()
            right = self._parse_disjunction()
            
            if op == '->':
                left = Implication(left, right)
            elif op == '<->':
                # A ↔ B ≡ (A → B) ∧ (B → A)
                left = Conjunction(Implication(left, right), Implication(right, left))
        
        return left
    
    def _parse_disjunction(self) -> Formula:
        """Parse disjunction"""
        left = self._parse_conjunction()
        
        while self._current_token() == '|':
            self._consume('|')
            right = self._parse_conjunction()
            left = Disjunction(left, right)
        
        return left
    
    def _parse_conjunction(self) -> Formula:
        """Parse conjunction"""
        left = self._parse_negation()
        
        while self._current_token() == '&':
            self._consume('&')
            right = self._parse_negation()
            left = Conjunction(left, right)
        
        return left
    
    def _parse_negation(self) -> Formula:
        """Parse negation"""
        if self._current_token() == '~':
            self._consume('~')
            operand = self._parse_negation()  # Right associative
            return Negation(operand)
        
        return self._parse_atomic()
    
    def _parse_atomic(self) -> Formula:
        """Parse atomic formulas (mode-dependent)"""
        token = self._current_token()
        
        if not token:
            raise ModeError("Expected atomic formula", self.mode)
        
        if token == '(':
            # Parenthesized formula
            self._consume('(')
            formula = self._parse_implication()
            self._consume(')')
            return formula
        
        # Mode-specific atomic parsing
        if self.mode == LogicMode.PROPOSITIONAL:
            return self._parse_propositional_atom()
        elif self.mode == LogicMode.FIRST_ORDER:
            return self._parse_fol_atomic()
        else:
            raise ModeError(f"Unsupported mode: {self.mode}", self.mode)
    
    def _parse_propositional_atom(self) -> Formula:
        """Parse propositional atom"""
        token = self._consume()
        
        # Validate atom name according to propositional rules
        if not self.validator.validate_atom_name(token):
            suggestions = self.validator.get_error_suggestions(token, "atom")
            raise ModeError(f"Invalid propositional atom: '{token}'", self.mode, suggestions)
        
        return Atom(token)
    
    def _parse_fol_atomic(self) -> Formula:
        """Parse first-order atomic formula (predicate)"""
        token = self._current_token()
        
        # Check if it's a predicate application Pred(args...)
        if '(' in token and ')' in token:
            return self._parse_predicate_application(token)
        
        # Otherwise it's a 0-ary predicate
        token = self._consume()
        
        # Validate predicate name
        if not self.validator.validate_predicate_name(token):
            suggestions = self.validator.get_error_suggestions(token, "predicate")
            raise ModeError(f"Invalid predicate name: '{token}'", self.mode, suggestions)
        
        return Predicate(token, [])
    
    def _parse_predicate_application(self, token: str) -> Predicate:
        """Parse predicate application like Student(john) or Loves(john, mary)"""
        self._consume()  # consume the full token
        
        # Extract predicate name and arguments
        if not token.endswith(')'):
            raise ModeError(f"Invalid predicate syntax: '{token}'", self.mode)
        
        paren_pos = token.find('(')
        if paren_pos == -1:
            raise ModeError(f"Invalid predicate syntax: '{token}'", self.mode)
        
        pred_name = token[:paren_pos]
        args_str = token[paren_pos+1:-1].strip()
        
        # Validate predicate name
        if not self.validator.validate_predicate_name(pred_name):
            suggestions = self.validator.get_error_suggestions(pred_name, "predicate")
            raise ModeError(f"Invalid predicate name: '{pred_name}'", self.mode, suggestions)
        
        # Parse arguments
        args = []
        if args_str:  # Non-empty argument list
            arg_tokens = [arg.strip() for arg in args_str.split(',')]
            for arg_token in arg_tokens:
                if not arg_token:
                    raise ModeError(f"Empty argument in predicate: '{token}'", self.mode)
                
                # Validate constant name (only constants supported in ground mode)
                if not self.validator.validate_constant_name(arg_token):
                    if arg_token[0].isupper():
                        # Looks like a variable
                        suggestions = "Variables not yet supported in ground formula mode. Use lowercase constants."
                    else:
                        suggestions = self.validator.get_error_suggestions(arg_token, "constant")
                    raise ModeError(f"Invalid constant: '{arg_token}'", self.mode, suggestions)
                
                args.append(Constant(arg_token))
        
        return Predicate(pred_name, args)


# Convenience functions for different modes

def parse_propositional(formula_str: str) -> Formula:
    """Parse a propositional logic formula"""
    parser = ModeAwareParser(LogicMode.PROPOSITIONAL)
    return parser.parse(formula_str)


def parse_first_order(formula_str: str) -> Formula:
    """Parse a first-order logic formula (ground formulas only)"""
    parser = ModeAwareParser(LogicMode.FIRST_ORDER)
    return parser.parse(formula_str)


def parse_with_mode(formula_str: str, mode: LogicMode) -> Formula:
    """Parse a formula with explicit mode specification"""
    parser = ModeAwareParser(mode)
    return parser.parse(formula_str)


# Export commonly used items
__all__ = [
    'ModeAwareParser', 'parse_propositional', 'parse_first_order', 'parse_with_mode'
]