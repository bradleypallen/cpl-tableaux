#!/usr/bin/env python3
"""
Extensible Parser System for Logic Formulas

This module provides a flexible parser that can handle different logic systems
with their specific connectives, precedence rules, and syntax variations.

Example usage:
    ```python
    from tableaux import LogicSystem
    
    classical = LogicSystem.classical()
    
    # Parse and solve directly
    result = classical.parse_and_solve("(p -> q) & p & ~q")
    
    # Parse to formula object
    formula = classical.parse("p | ~p")
    result = classical.solve(formula)
    ```
"""

import re
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from .core.formula import Formula, PropositionalAtom, CompoundFormula, ConnectiveSpec
from .api import LogicFormula


class TokenType(Enum):
    """Types of tokens in formula parsing."""
    ATOM = "atom"
    CONNECTIVE = "connective"
    LPAREN = "lparen"
    RPAREN = "rparen"
    LBRACKET = "lbracket"
    RBRACKET = "rbracket"
    UNIVERSAL = "universal"  # ∀
    EXISTENTIAL = "existential"  # ∃
    VARIABLE = "variable"  # X, Y, Z
    PREDICATE = "predicate"  # P(X), Bird(tweety)
    EOF = "eof"


@dataclass
class Token:
    """A token in the parsing process."""
    type: TokenType
    value: str
    position: int


class ParseError(Exception):
    """Exception raised when parsing fails."""
    
    def __init__(self, message: str, position: int = -1):
        self.message = message
        self.position = position
        super().__init__(f"Parse error at position {position}: {message}")


class Tokenizer:
    """Tokenizes formula strings into a stream of tokens."""
    
    def __init__(self, connective_specs: Dict[str, ConnectiveSpec]):
        self.connective_specs = connective_specs
        
        # Create regex patterns for connectives (order by length to match longer ones first)
        connective_symbols = sorted(connective_specs.keys(), key=len, reverse=True)
        escaped_symbols = [re.escape(symbol) for symbol in connective_symbols]
        self.connective_pattern = '|'.join(escaped_symbols)
        
        # Patterns for different token types
        self.quantifier_pattern = r'[∀∃]'  # Unicode quantifier symbols
        self.variable_pattern = r'[A-Z]'  # Single uppercase letters for variables
        self.predicate_pattern = r'[A-Z][a-zA-Z0-9_]*\([^)]+\)'  # Predicate(args)
        self.atom_pattern = r'[a-z][a-zA-Z0-9_]*'  # Lowercase start for atoms
        self.constant_pattern = r'[a-z][a-zA-Z0-9_]*'  # Lowercase for constants
        
        # Combined pattern - order matters for matching
        self.token_pattern = (
            f'({self.quantifier_pattern})|'  # Quantifiers ∀∃
            f'({self.predicate_pattern})|'    # Predicates P(X)
            f'({self.connective_pattern})|'   # Connectives
            f'(\\[)|(\\])|'                  # Brackets []
            f'(\\()|(\\))|'                  # Parentheses ()
            f'({self.variable_pattern})|'     # Variables X
            f'({self.atom_pattern})|'         # Atoms p
            f'(\\s+)|(.)'                    # Whitespace and invalid
        )
    
    def tokenize(self, text: str) -> List[Token]:
        """Tokenize a formula string into tokens."""
        tokens = []
        position = 0
        
        for match in re.finditer(self.token_pattern, text):
            (quantifier, predicate, connective, lbracket, rbracket, 
             lparen, rparen, variable, atom, whitespace, invalid) = match.groups()
            
            if whitespace:
                # Skip whitespace
                position = match.end()
                continue
            elif invalid:
                raise ParseError(f"Invalid character '{invalid}'", match.start())
            elif quantifier:
                if quantifier == '∀':
                    tokens.append(Token(TokenType.UNIVERSAL, quantifier, match.start()))
                elif quantifier == '∃':
                    tokens.append(Token(TokenType.EXISTENTIAL, quantifier, match.start()))
            elif predicate:
                tokens.append(Token(TokenType.PREDICATE, predicate, match.start()))
            elif connective:
                tokens.append(Token(TokenType.CONNECTIVE, connective, match.start()))
            elif lbracket:
                tokens.append(Token(TokenType.LBRACKET, lbracket, match.start()))
            elif rbracket:
                tokens.append(Token(TokenType.RBRACKET, rbracket, match.start()))
            elif lparen:
                tokens.append(Token(TokenType.LPAREN, lparen, match.start()))
            elif rparen:
                tokens.append(Token(TokenType.RPAREN, rparen, match.start()))
            elif variable:
                tokens.append(Token(TokenType.VARIABLE, variable, match.start()))
            elif atom:
                tokens.append(Token(TokenType.ATOM, atom, match.start()))
            
            position = match.end()
        
        tokens.append(Token(TokenType.EOF, "", len(text)))
        return tokens


class FormulaParser:
    """Recursive descent parser for logic formulas."""
    
    def __init__(self, logic_system):
        self.logic_system = logic_system
        self.connective_specs = logic_system._logic.connectives
        self.tokenizer = Tokenizer(self.connective_specs)
        self.tokens = []
        self.current = 0
    
    def parse(self, text: str) -> LogicFormula:
        """Parse a formula string into a LogicFormula object."""
        try:
            self.tokens = self.tokenizer.tokenize(text)
            self.current = 0
            
            formula = self._parse_formula()
            
            # Ensure we've consumed all tokens
            if not self._is_at_end():
                raise ParseError(f"Unexpected token '{self._peek().value}'", self._peek().position)
            
            return LogicFormula(formula, self.logic_system)
        
        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"Internal parser error: {e}")
    
    def _parse_formula(self) -> Formula:
        """Parse a complete formula (lowest precedence)."""
        return self._parse_quantifier()
    
    def _parse_quantifier(self) -> Formula:
        """Parse restricted quantifiers: [∀X P(X)]Q(X) or [∃X P(X)]Q(X) at highest precedence."""
        return self._parse_implication()  # Let implication handle quantifiers in context
    
    def _parse_implication(self) -> Formula:
        """Parse implication (right-associative, lowest precedence)."""
        left = self._parse_disjunction()
        
        while self._match_connective('->'):
            operator = self._previous().value
            right = self._parse_implication()  # Right associative
            spec = self.connective_specs[operator]
            left = CompoundFormula(spec, left, right)
        
        return left
    
    def _parse_disjunction(self) -> Formula:
        """Parse disjunction (left-associative)."""
        left = self._parse_conjunction()
        
        while self._match_connective('|'):  # Disjunction operator
            operator = self._previous().value
            right = self._parse_conjunction()
            spec = self.connective_specs[operator]
            left = CompoundFormula(spec, left, right)
        
        return left
    
    def _parse_conjunction(self) -> Formula:
        """Parse conjunction (left-associative, higher precedence than disjunction)."""
        left = self._parse_negation()
        
        while self._match_connective('&', "'"):  # Support both & and ' for conjunction
            operator = self._previous().value
            right = self._parse_negation()
            spec = self.connective_specs[operator]
            left = CompoundFormula(spec, left, right)
        
        return left
    
    def _parse_negation(self) -> Formula:
        """Parse negation (prefix, highest precedence)."""
        if self._match_connective('~'):
            operator = self._previous().value
            operand = self._parse_negation()  # Right associative for multiple negations
            spec = self.connective_specs[operator]
            return CompoundFormula(spec, operand)
        
        return self._parse_primary()
    
    def _parse_primary(self) -> Formula:
        """Parse primary expressions (atoms, predicates, quantifiers, and parenthesized formulas)."""
        # Restricted quantifier expression
        if self._check(TokenType.LBRACKET):
            return self._parse_restricted_quantifier()
        
        # Parenthesized expression
        if self._match(TokenType.LPAREN):
            formula = self._parse_formula()
            if not self._match(TokenType.RPAREN):
                raise ParseError("Expected ')' after expression", self._peek().position)
            return formula
        
        # Predicate formula
        if self._check(TokenType.PREDICATE):
            return self._parse_predicate()
        
        # Atomic formula
        if self._match(TokenType.ATOM):
            atom_name = self._previous().value
            return PropositionalAtom(atom_name)
        
        # Error
        current_token = self._peek()
        if current_token.type == TokenType.EOF:
            raise ParseError("Unexpected end of input", current_token.position)
        else:
            raise ParseError(f"Unexpected token '{current_token.value}'", current_token.position)
    
    def _parse_restricted_quantifier(self) -> Formula:
        """Parse restricted quantifiers: [∀X P(X)]Q(X) or [∃X P(X)]Q(X)."""
        if not self._match(TokenType.LBRACKET):
            raise ParseError("Expected '[' to start restricted quantifier", self._peek().position)
        
        # Parse quantifier type
        if self._match(TokenType.UNIVERSAL):
            quantifier_type = '∀'
        elif self._match(TokenType.EXISTENTIAL):
            quantifier_type = '∃'
        else:
            raise ParseError("Expected quantifier (∀ or ∃) after '['", self._peek().position)
        
        # Parse variable
        if not self._match(TokenType.VARIABLE):
            raise ParseError("Expected variable after quantifier", self._peek().position)
        variable_name = self._previous().value
        
        # Parse restriction (the P(X) part) - this should be a predicate or simple formula
        restriction = self._parse_predicate_or_simple_formula()
        
        # Expect closing bracket
        if not self._match(TokenType.RBRACKET):
            raise ParseError("Expected ']' after restriction", self._peek().position)
        
        # Parse matrix (the Q(X) part) - this should be a predicate or simple formula
        matrix = self._parse_predicate_or_simple_formula()
        
        # Create restricted quantifier formula
        from .core.formula import Variable, RestrictedUniversalFormula, RestrictedExistentialFormula
        variable = Variable(variable_name)
        
        if quantifier_type == '∀':
            return RestrictedUniversalFormula(variable, restriction, matrix)
        else:
            return RestrictedExistentialFormula(variable, restriction, matrix)
    
    def _parse_predicate_or_simple_formula(self) -> Formula:
        """Parse either a predicate or a simple atomic formula for quantifier restrictions."""
        # Check if we have a predicate
        if self._check(TokenType.PREDICATE):
            return self._parse_predicate()
        elif self._check(TokenType.ATOM):
            # Simple atomic formula
            if self._match(TokenType.ATOM):
                atom_name = self._previous().value
                return PropositionalAtom(atom_name)
        
        raise ParseError("Expected predicate or atom in quantifier restriction", self._peek().position)
    
    def _parse_predicate(self) -> Formula:
        """Parse a predicate like P(X) or Bird(tweety)."""
        if not self._match(TokenType.PREDICATE):
            raise ParseError("Expected predicate", self._peek().position)
        
        predicate_str = self._previous().value
        
        # Parse predicate string like "Bird(tweety)" or "P(X)"
        paren_pos = predicate_str.find('(')
        if paren_pos == -1:
            raise ParseError(f"Invalid predicate format: {predicate_str}", self._previous().position)
        
        pred_name = predicate_str[:paren_pos]
        args_str = predicate_str[paren_pos+1:-1]  # Remove parentheses
        
        # Parse arguments (separated by commas)
        from .core.formula import Predicate, Variable, Constant
        terms = []
        for arg in args_str.split(','):
            arg = arg.strip()
            if arg.isupper() and len(arg) == 1:  # Variable
                terms.append(Variable(arg))
            else:  # Constant
                terms.append(Constant(arg))
        
        return Predicate(pred_name, terms)
    
    def _match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types."""
        for token_type in token_types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _match_connective(self, *symbols: str) -> bool:
        """Check if current token is a connective with one of the given symbols."""
        if self._check(TokenType.CONNECTIVE):
            current_symbol = self._peek().value
            if current_symbol in symbols:
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token is of given type without consuming it."""
        if self._is_at_end():
            return token_type == TokenType.EOF
        return self._peek().type == token_type
    
    def _advance(self) -> Token:
        """Consume and return current token."""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """Check if we're at end of token stream."""
        return self._peek().type == TokenType.EOF
    
    def _peek(self) -> Token:
        """Return current token without consuming it."""
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """Return previous token."""
        return self.tokens[self.current - 1]


# Integration with LogicSystem
def parse_formula(logic_system, text: str) -> LogicFormula:
    """Parse a formula string in the context of a logic system."""
    parser = FormulaParser(logic_system)
    return parser.parse(text)


def parse_and_solve(logic_system, text: str, sign: str = 'T', track_steps: bool = False):
    """Parse a formula string and solve it directly."""
    formula = parse_formula(logic_system, text)
    return logic_system.solve(formula, sign, track_steps)


def parse_and_entails(logic_system, premises_text: List[str], conclusion_text: str) -> bool:
    """Parse premise and conclusion strings and check entailment."""
    premises = [parse_formula(logic_system, p) for p in premises_text]
    conclusion = parse_formula(logic_system, conclusion_text)
    return logic_system.entails(premises, conclusion)