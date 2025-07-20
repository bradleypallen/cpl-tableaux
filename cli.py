#!/usr/bin/env python3
"""
Command Line Interface for the Tableau System

Allows users to input propositional logic formulas and test their satisfiability
using the semantic tableau method.
"""

import sys
import re
from typing import List, Optional
from formula import *
from tableau import Tableau

class FormulaParser:
    """Parse string formulas into Formula objects"""
    
    def __init__(self):
        self.tokens = []
        self.pos = 0
    
    def parse(self, formula_str: str) -> Formula:
        """Parse a formula string into a Formula object"""
        # Tokenize
        self.tokens = self._tokenize(formula_str)
        self.pos = 0
        
        if not self.tokens:
            raise ValueError("Empty formula")
        
        result = self._parse_implication()
        
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token: {self.tokens[self.pos]}")
        
        return result
    
    def _tokenize(self, formula_str: str) -> List[str]:
        """Convert formula string to tokens"""
        # Replace symbols with words for easier parsing
        formula_str = formula_str.replace('¬', '~')
        formula_str = formula_str.replace('∧', '&')
        formula_str = formula_str.replace('∨', '|')
        formula_str = formula_str.replace('→', '->')
        formula_str = formula_str.replace('↔', '<->')
        
        # Tokenize using regex
        pattern = r'(\w+|->|<->|[()&|~])'
        tokens = re.findall(pattern, formula_str)
        return [t for t in tokens if t.strip()]
    
    def _current_token(self) -> Optional[str]:
        """Get current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def _consume(self, expected: str = None) -> str:
        """Consume and return current token"""
        if self.pos >= len(self.tokens):
            raise ValueError("Unexpected end of formula")
        
        token = self.tokens[self.pos]
        self.pos += 1
        
        if expected and token != expected:
            raise ValueError(f"Expected '{expected}', got '{token}'")
        
        return token
    
    def _parse_implication(self) -> Formula:
        """Parse implication (lowest precedence)"""
        left = self._parse_disjunction()
        
        while self._current_token() == '->':
            self._consume('->')
            right = self._parse_disjunction()
            left = Implication(left, right)
        
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
            return Negation(self._parse_negation())
        
        return self._parse_atom()
    
    def _parse_atom(self) -> Formula:
        """Parse atomic formula or parenthesized expression"""
        token = self._current_token()
        
        if token == '(':
            self._consume('(')
            result = self._parse_implication()
            self._consume(')')
            return result
        
        if token and re.match(r'\w+', token):
            self._consume()
            return Atom(token)
        
        raise ValueError(f"Expected atom or '(', got '{token}'")

class TableauCLI:
    """Command Line Interface for the tableau system"""
    
    def __init__(self):
        self.parser = FormulaParser()
        self.history = []
    
    def run(self):
        """Main CLI loop"""
        print("=" * 60)
        print("SEMANTIC TABLEAU SYSTEM")
        print("=" * 60)
        print("Enter propositional logic formulas to test satisfiability.")
        print()
        print("Syntax:")
        print("  Atoms: p, q, r, x, y, etc.")
        print("  Negation: ~p or ¬p")
        print("  Conjunction: p & q or p ∧ q")
        print("  Disjunction: p | q or p ∨ q")
        print("  Implication: p -> q or p → q")
        print("  Parentheses: (p & q) -> r")
        print()
        print("Commands:")
        print("  help     - Show this help")
        print("  history  - Show formula history")
        print("  examples - Show example formulas")
        print("  multi    - Enter multiple formulas mode")
        print("  quit     - Exit")
        print()
        print("Multiple formulas:")
        print("  Use commas to separate: p & q, ~p | r, q -> s")
        print("=" * 60)
        
        while True:
            try:
                formula_input = input("\nTableau> ").strip()
                
                if not formula_input:
                    continue
                
                if formula_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if formula_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if formula_input.lower() == 'history':
                    self._show_history()
                    continue
                
                if formula_input.lower() == 'examples':
                    self._show_examples()
                    continue
                
                if formula_input.lower() == 'multi':
                    self._multi_formula_mode()
                    continue
                
                # Check if input contains commas (multiple formulas)
                if ',' in formula_input:
                    self._process_multiple_formulas(formula_input)
                else:
                    # Parse and test single formula
                    self._process_formula(formula_input)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _process_formula(self, formula_str: str):
        """Process a formula string"""
        try:
            # Parse formula
            formula = self.parser.parse(formula_str)
            
            # Add to history
            self.history.append(formula_str)
            
            print(f"\nParsed formula: {formula}")
            print("Testing satisfiability...")
            print("-" * 40)
            
            # Create and run tableau
            tableau = Tableau(formula)
            is_satisfiable = tableau.build()
            
            # Show results
            print(f"\nRESULT: {'SATISFIABLE' if is_satisfiable else 'UNSATISFIABLE'}")
            
            # Ask if user wants to see the full tableau (only in interactive mode)
            show_tree = input("\nShow full tableau tree? (y/n): ").strip().lower()
            if show_tree in ['y', 'yes']:
                print()
                tableau.print_tree()
            else:
                # Just show summary
                open_branches = [b for b in tableau.branches if not b.is_closed]
                closed_branches = [b for b in tableau.branches if b.is_closed]
                
                print(f"Summary:")
                print(f"  Total branches: {len(tableau.branches)}")
                print(f"  Open branches: {len(open_branches)}")
                print(f"  Closed branches: {len(closed_branches)}")
                
                if open_branches:
                    print(f"  Open branch IDs: {[b.id for b in open_branches]}")
        
        except Exception as e:
            print(f"Error processing formula: {e}")
    
    def _process_multiple_formulas(self, formulas_str: str):
        """Process multiple comma-separated formulas"""
        try:
            # Split by commas and parse each formula
            formula_strings = [f.strip() for f in formulas_str.split(',') if f.strip()]
            
            if not formula_strings:
                print("No formulas found.")
                return
            
            formulas = []
            print(f"\nParsing {len(formula_strings)} formulas:")
            for i, formula_str in enumerate(formula_strings, 1):
                try:
                    formula = self.parser.parse(formula_str)
                    formulas.append(formula)
                    print(f"  {i}. {formula}")
                except Exception as e:
                    print(f"  {i}. ERROR parsing '{formula_str}': {e}")
                    return
            
            # Add to history
            self.history.append(formulas_str)
            
            print("\nTesting satisfiability of formula set...")
            print("-" * 40)
            
            # Create and run tableau with multiple formulas
            tableau = Tableau(formulas)
            is_satisfiable = tableau.build()
            
            # Show results
            print(f"\nRESULT: {'SATISFIABLE' if is_satisfiable else 'UNSATISFIABLE'}")
            
            if is_satisfiable:
                print("The formula set is consistent - there exists an interpretation")
                print("that satisfies all formulas simultaneously.")
            else:
                print("The formula set is inconsistent - no interpretation can")
                print("satisfy all formulas simultaneously.")
            
            # Always show tableau in command line mode, ask in interactive mode
            if len(sys.argv) > 1:
                print()
                tableau.print_tree()
            else:
                # Ask if user wants to see the full tableau
                show_tree = input("\nShow full tableau tree? (y/n): ").strip().lower()
                if show_tree in ['y', 'yes']:
                    print()
                    tableau.print_tree()
                else:
                    # Just show summary
                    open_branches = [b for b in tableau.branches if not b.is_closed]
                    closed_branches = [b for b in tableau.branches if b.is_closed]
                    
                    print(f"Summary:")
                    print(f"  Total branches: {len(tableau.branches)}")
                    print(f"  Open branches: {len(open_branches)}")
                    print(f"  Closed branches: {len(closed_branches)}")
                    
                    if open_branches:
                        print(f"  Open branch IDs: {[b.id for b in open_branches]}")
        
        except Exception as e:
            print(f"Error processing formulas: {e}")
    
    def _multi_formula_mode(self):
        """Enter dedicated multiple formula mode"""
        print("\n" + "=" * 50)
        print("MULTIPLE FORMULA MODE")
        print("=" * 50)
        print("Enter formulas one by one. Type 'done' when finished.")
        print("Type 'cancel' to return to main mode.")
        print()
        
        formulas = []
        formula_strings = []
        
        while True:
            try:
                formula_input = input(f"Formula {len(formulas) + 1}> ").strip()
                
                if formula_input.lower() == 'done':
                    break
                elif formula_input.lower() == 'cancel':
                    print("Cancelled multiple formula mode.")
                    return
                elif not formula_input:
                    continue
                
                # Parse formula
                formula = self.parser.parse(formula_input)
                formulas.append(formula)
                formula_strings.append(formula_input)
                print(f"  Added: {formula}")
                
            except Exception as e:
                print(f"Error: {e}")
                print("Please try again or type 'cancel' to exit.")
        
        if not formulas:
            print("No formulas entered.")
            return
        
        print(f"\nCollected {len(formulas)} formulas:")
        for i, formula in enumerate(formulas, 1):
            print(f"  {i}. {formula}")
        
        # Add to history
        combined_str = ", ".join(formula_strings)
        self.history.append(f"[MULTI] {combined_str}")
        
        print("\nTesting satisfiability of formula set...")
        print("-" * 40)
        
        # Create and run tableau
        tableau = Tableau(formulas)
        is_satisfiable = tableau.build()
        
        # Show results
        print(f"\nRESULT: {'SATISFIABLE' if is_satisfiable else 'UNSATISFIABLE'}")
        
        if is_satisfiable:
            print("The formula set is consistent.")
        else:
            print("The formula set is inconsistent.")
        
        # Always show tree for multi-mode since it was explicitly requested
        tableau.print_tree()
    
    def _show_help(self):
        """Show help information"""
        print("\nHELP - Formula Syntax")
        print("-" * 30)
        print("Operators (in order of precedence):")
        print("  ~A      Negation (highest)")
        print("  A & B   Conjunction")
        print("  A | B   Disjunction")
        print("  A -> B  Implication (lowest)")
        print()
        print("Alternative symbols:")
        print("  ¬ for ~  (negation)")
        print("  ∧ for &  (conjunction)")
        print("  ∨ for |  (disjunction)")
        print("  → for -> (implication)")
        print()
        print("Examples:")
        print("  p & q")
        print("  ~p | q")
        print("  (p -> q) & p")
        print("  ~(p & ~q)")
    
    def _show_history(self):
        """Show formula history"""
        if not self.history:
            print("\nNo formulas in history.")
            return
        
        print("\nFormula History:")
        print("-" * 20)
        for i, formula in enumerate(self.history, 1):
            print(f"{i:2d}. {formula}")
    
    def _show_examples(self):
        """Show example formulas"""
        print("\nExample Formulas:")
        print("-" * 30)
        print("Contradictions (should be UNSATISFIABLE):")
        print("  p & ~p")
        print("  (p -> q) & p & ~q")
        print()
        print("Tautologies (should be SATISFIABLE):")
        print("  p | ~p")
        print("  (p -> q) -> (~q -> ~p)")
        print("  ((p -> q) & p) -> q")
        print()
        print("Contingent formulas (could be either):")
        print("  p & q")
        print("  p -> q")
        print("  (p | q) & (~p | r)")
        print()
        print("Complex formulas:")
        print("  ~(p & q) -> (~p | ~q)")
        print("  (p -> (q -> r)) -> ((p -> q) -> (p -> r))")
        print()
        print("Multiple formula examples:")
        print("  p & q, ~p | r")
        print("  p -> q, q -> r, p, ~r")
        print("  p | q, ~p, ~q")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Command line mode - process formula(s)
        formula_str = ' '.join(sys.argv[1:])
        cli = TableauCLI()
        
        # Check if multiple formulas (comma-separated)
        if ',' in formula_str:
            print("Tableau System - Multiple Formula Mode")
            print("=" * 45)
            cli._process_multiple_formulas(formula_str)
        else:
            print("Tableau System - Single Formula Mode")
            print("=" * 40)
            
            # Process single formula without interactive prompts
            try:
                formula = cli.parser.parse(formula_str)
                print(f"\nParsed formula: {formula}")
                print("Testing satisfiability...")
                print("-" * 40)
                
                tableau = Tableau(formula)
                is_satisfiable = tableau.build()
                
                print(f"\nRESULT: {'SATISFIABLE' if is_satisfiable else 'UNSATISFIABLE'}")
                
                # Always show full tableau in command line mode
                print()
                tableau.print_tree()
                
            except Exception as e:
                print(f"Error: {e}")
    else:
        # Interactive mode
        cli = TableauCLI()
        cli.run()

if __name__ == "__main__":
    main()