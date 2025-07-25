#!/usr/bin/env python3
"""
Enhanced Command Line Interface for the Tableau System

Provides comprehensive CLI functionality matching CLI_GUIDE.md specifications
including argument parsing, multiple output formats, and advanced features.
"""

import sys
import argparse
import json
import csv
import time
from typing import List, Dict, Any, Optional
from io import StringIO

# Import tableau components - using only tableau approach
from tableau_core import (
    Formula, Atom, Negation, Conjunction, Disjunction, Implication,
    classical_signed_tableau, three_valued_signed_tableau, wkrq_signed_tableau,
    T, F, T3, F3, U, TF, FF,
    parse_formula
)
from unified_model import UnifiedModel, ClassicalModel, WK3Model, WkrqModel

class EnhancedFormulaParser:
    """Enhanced parser supporting the syntax described in CLI_GUIDE.md"""
    
    def __init__(self):
        self.tokens = []
        self.pos = 0
    
    def parse(self, formula_str: str) -> Formula:
        """Parse a formula string into a Formula object"""
        # Handle special constants
        if formula_str.upper() == 'T':
            return Atom("T")  # Boolean true constant
        if formula_str.upper() == 'F':
            return Atom("F")  # Boolean false constant
            
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
        # Replace symbols with standard operators
        formula_str = formula_str.replace('¬', '~')
        formula_str = formula_str.replace('∧', '&')
        formula_str = formula_str.replace('∨', '|')
        formula_str = formula_str.replace('→', '->')
        formula_str = formula_str.replace('↔', '<->')
        
        # Tokenize using regex
        import re
        pattern = r'(\w+|->|<->|[()&|~])'
        tokens = re.findall(pattern, formula_str)
        
        # Filter out empty tokens
        return [token for token in tokens if token.strip()]
    
    def _parse_implication(self) -> Formula:
        """Parse implication (lowest precedence)"""
        left = self._parse_disjunction()
        
        while self.pos < len(self.tokens) and self.tokens[self.pos] == '->':
            self.pos += 1
            right = self._parse_disjunction()
            left = Implication(left, right)
        
        return left
    
    def _parse_disjunction(self) -> Formula:
        """Parse disjunction"""
        left = self._parse_conjunction()
        
        while self.pos < len(self.tokens) and self.tokens[self.pos] == '|':
            self.pos += 1
            right = self._parse_conjunction()
            left = Disjunction(left, right)
        
        return left
    
    def _parse_conjunction(self) -> Formula:
        """Parse conjunction"""
        left = self._parse_negation()
        
        while self.pos < len(self.tokens) and self.tokens[self.pos] == '&':
            self.pos += 1
            right = self._parse_negation()
            left = Conjunction(left, right)
        
        return left
    
    def _parse_negation(self) -> Formula:
        """Parse negation"""
        if self.pos < len(self.tokens) and self.tokens[self.pos] == '~':
            self.pos += 1
            operand = self._parse_negation()  # Right-associative
            return Negation(operand)
        
        return self._parse_atom()
    
    def _parse_atom(self) -> Formula:
        """Parse atomic formula or parenthesized expression"""
        if self.pos >= len(self.tokens):
            raise ValueError("Unexpected end of formula")
        
        token = self.tokens[self.pos]
        
        if token == '(':
            self.pos += 1
            result = self._parse_implication()
            if self.pos >= len(self.tokens) or self.tokens[self.pos] != ')':
                raise ValueError("Missing closing parenthesis")
            self.pos += 1
            return result
        else:
            # Atom
            if not token.replace('_', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '').isalpha():
                raise ValueError(f"Invalid atom name: {token}")
            self.pos += 1
            return Atom(token)


class OutputFormatter:
    """Handle different output formats"""
    
    @staticmethod
    def format_result(result_data: Dict[str, Any], format_type: str) -> str:
        """Format results according to specified format"""
        if format_type == "json":
            return json.dumps(result_data, indent=2, default=str)
        elif format_type == "csv":
            return OutputFormatter._format_csv(result_data)
        else:
            return OutputFormatter._format_default(result_data)
    
    @staticmethod
    def _format_csv(result_data: Dict[str, Any]) -> str:
        """Format as CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        header = ["formula", "logic", "satisfiable", "model_count"]
        if "models" in result_data and result_data["models"]:
            # Add atom columns based on first model
            first_model = result_data["models"][0]
            if isinstance(first_model, dict):
                atoms = sorted(first_model.keys())
                header.extend(atoms)
        writer.writerow(header)
        
        # Data rows
        formula = result_data.get("formula", "")
        logic = result_data.get("logic", "classical")
        satisfiable = result_data.get("satisfiable", False)
        models = result_data.get("models", [])
        
        if models:
            for model in models:
                row = [formula, logic, satisfiable, len(models)]
                if isinstance(model, dict):
                    atoms = sorted(model.keys())
                    for atom in atoms:
                        row.append(model[atom])
                writer.writerow(row)
        else:
            row = [formula, logic, satisfiable, 0]
            writer.writerow(row)
        
        return output.getvalue().strip()
    
    @staticmethod
    def _format_default(result_data: Dict[str, Any]) -> str:
        """Format as default text output"""
        lines = []
        lines.append(f"Formula: {result_data.get('formula', 'Unknown')}")
        lines.append(f"Logic: {result_data.get('logic', 'Classical')}")
        lines.append(f"Result: {'SATISFIABLE' if result_data.get('satisfiable', False) else 'UNSATISFIABLE'}")
        
        models = result_data.get("models", [])
        if models:
            lines.append(f"Found {len(models)} model(s):")
            for i, model in enumerate(models[:5]):  # Show first 5 models
                lines.append(f"  Model {i+1}: {model}")
            if len(models) > 5:
                lines.append(f"  ... and {len(models) - 5} more")
        
        stats = result_data.get("statistics", {})
        if stats:
            lines.append("Statistics:")
            for key, value in stats.items():
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)


class EnhancedTableauCLI:
    """Enhanced CLI with full argument parsing and features"""
    
    def __init__(self):
        self.parser = EnhancedFormulaParser()
        self.setup_argument_parser()
    
    def setup_argument_parser(self):
        """Setup command line argument parser"""
        self.arg_parser = argparse.ArgumentParser(
            description="Tableau Logic System - Semantic tableau method for automated theorem proving",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s "p | ~p"                    # Test tautology
  %(prog)s "p & ~p"                    # Test contradiction  
  %(prog)s --models "p | q"            # Show all models
  %(prog)s --wk3 "p & ~p"              # Use three-valued logic
  %(prog)s --stats "complex_formula"   # Show statistics
  %(prog)s --format=json "p"           # JSON output
  %(prog)s --file=formulas.txt         # Process file
  %(prog)s                             # Interactive mode
            """
        )
        
        # Positional argument for formula
        self.arg_parser.add_argument(
            'formula', 
            nargs='?', 
            help='Formula to test (if not provided, enters interactive mode)'
        )
        
        # Logic system options
        logic_group = self.arg_parser.add_mutually_exclusive_group()
        logic_group.add_argument(
            '--classical', 
            action='store_true', 
            help='Use classical logic (default)'
        )
        logic_group.add_argument(
            '--wk3', 
            action='store_true', 
            help='Use three-valued Weak Kleene logic'
        )
        
        # Output options
        self.arg_parser.add_argument(
            '--models', 
            action='store_true', 
            help='Show all satisfying models'
        )
        self.arg_parser.add_argument(
            '--stats', 
            action='store_true', 
            help='Show performance statistics'
        )
        self.arg_parser.add_argument(
            '--format', 
            choices=['default', 'json', 'csv'], 
            default='default',
            help='Output format (default: default)'
        )
        
        # File processing
        self.arg_parser.add_argument(
            '--file', 
            help='Process formulas from file'
        )
        self.arg_parser.add_argument(
            '--batch', 
            action='store_true', 
            help='Process multiple formulas from command line or stdin'
        )
        
        # Advanced options
        self.arg_parser.add_argument(
            '--timeout', 
            type=int, 
            help='Timeout in seconds for complex formulas'
        )
        self.arg_parser.add_argument(
            '--max-models', 
            type=int, 
            default=10,
            help='Maximum number of models to show (default: 10)'
        )
        self.arg_parser.add_argument(
            '--debug', 
            action='store_true', 
            help='Show debugging information'
        )
        self.arg_parser.add_argument(
            '--validate-only', 
            action='store_true', 
            help='Only validate formula syntax, don\'t solve'
        )
    
    def run(self, args=None):
        """Main CLI entry point"""
        if args is None:
            args = sys.argv[1:]
        
        parsed_args = self.arg_parser.parse_args(args)
        
        # Determine logic system
        if parsed_args.wk3:
            logic_system = "wk3"
        else:
            logic_system = "classical"
        
        # Handle different modes
        if parsed_args.file:
            self._process_file(parsed_args.file, logic_system, parsed_args)
        elif parsed_args.batch:
            self._process_batch(logic_system, parsed_args)
        elif parsed_args.formula:
            self._process_single_formula(parsed_args.formula, logic_system, parsed_args)
        else:
            self._interactive_mode(logic_system)
    
    def _process_single_formula(self, formula_str: str, logic_system: str, args):
        """Process a single formula"""
        try:
            start_time = time.time()
            
            # Parse formula
            formula = self.parser.parse(formula_str)
            
            if args.validate_only:
                result_data = {
                    "formula": str(formula),
                    "logic": logic_system,
                    "valid_syntax": True
                }
                print(OutputFormatter.format_result(result_data, args.format))
                return
            
            # Create tableau using actual API
            if logic_system == "wk3":
                # For WK3, check if formula can be true OR undefined
                t3_tableau = three_valued_signed_tableau(T3(formula))
                u_tableau = three_valued_signed_tableau(U(formula))
                t3_satisfiable = t3_tableau.build()
                u_satisfiable = u_tableau.build()
                is_satisfiable = t3_satisfiable or u_satisfiable
                
                # Use primary tableau for stats and models
                tableau = t3_tableau if t3_satisfiable else u_tableau
                models = tableau.extract_all_models() if is_satisfiable and args.models else []
            else:
                tableau = classical_signed_tableau(T(formula))
                is_satisfiable = tableau.build()
                models = tableau.extract_all_models() if is_satisfiable and args.models else []
            
            end_time = time.time()
            
            # Prepare result data
            result_data = {
                "formula": str(formula),
                "logic": logic_system,
                "satisfiable": is_satisfiable,
                "models": models[:args.max_models] if models else []
            }
            
            if args.stats:
                result_data["statistics"] = {
                    "construction_time": f"{end_time - start_time:.4f}s",
                    "total_branches": len(tableau.branches),
                    "open_branches": len([b for b in tableau.branches if not b.is_closed]),
                    "closed_branches": len([b for b in tableau.branches if b.is_closed])
                }
            
            # Output result
            print(OutputFormatter.format_result(result_data, args.format))
            
            if args.debug and hasattr(tableau, 'print_tree'):
                print("\nDEBUG: Tableau tree:")
                tableau.print_tree()
        
        except Exception as e:
            error_data = {
                "formula": formula_str,
                "logic": logic_system,
                "error": str(e)
            }
            print(f"Error: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
    
    def _process_file(self, filename: str, logic_system: str, args):
        """Process formulas from a file"""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            formulas = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    formulas.append(line)
            
            print(f"Processing {len(formulas)} formulas from {filename}")
            print(f"Logic system: {logic_system}")
            print("=" * 50)
            
            results = []
            for i, formula_str in enumerate(formulas, 1):
                print(f"\nFormula {i}: {formula_str}")
                try:
                    formula = self.parser.parse(formula_str)
                    
                    if logic_system == "wk3":
                        # For WK3, check if formula can be true OR undefined
                        t3_tableau = three_valued_signed_tableau(T3(formula))
                        u_tableau = three_valued_signed_tableau(U(formula))
                        t3_satisfiable = t3_tableau.build()
                        u_satisfiable = u_tableau.build()
                        is_satisfiable = t3_satisfiable or u_satisfiable
                        
                        # Use primary tableau for stats and models
                        tableau = t3_tableau if t3_satisfiable else u_tableau
                        models = tableau.extract_all_models() if is_satisfiable and args.models else []
                    else:
                        tableau = classical_signed_tableau(T(formula))
                        is_satisfiable = tableau.build()
                        models = tableau.extract_all_models() if is_satisfiable and args.models else []
                    
                    result = {
                        "formula": str(formula),
                        "logic": logic_system,
                        "satisfiable": is_satisfiable,
                        "models": models[:args.max_models] if models else []
                    }
                    results.append(result)
                    
                    print(f"  Result: {'SAT' if is_satisfiable else 'UNSAT'}")
                    if models:
                        print(f"  Models: {len(models)}")
                
                except Exception as e:
                    print(f"  Error: {e}")
                    results.append({
                        "formula": formula_str,
                        "logic": logic_system,
                        "error": str(e)
                    })
            
            # Summary output
            if args.format != "default":
                for result in results:
                    print(OutputFormatter.format_result(result, args.format))
        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
        except Exception as e:
            print(f"Error processing file: {e}")
    
    def _process_batch(self, logic_system: str, args):
        """Process multiple formulas from stdin or command line"""
        if sys.stdin.isatty():
            print("Enter formulas (one per line, Ctrl+D to finish):")
        
        formulas = []
        try:
            for line in sys.stdin:
                line = line.strip()
                if line and not line.startswith('#'):
                    formulas.append(line)
        except KeyboardInterrupt:
            pass
        
        if formulas:
            print(f"\nProcessing {len(formulas)} formulas in batch mode")
            for i, formula_str in enumerate(formulas, 1):
                print(f"\n{i}. {formula_str}")
                self._process_single_formula(formula_str, logic_system, args)
        else:
            print("No formulas provided.")
    
    def _interactive_mode(self, logic_system: str):
        """Interactive mode matching CLI_GUIDE.md specifications"""
        print("Welcome to the Tableau Logic System!")
        print("Type 'help' for commands, 'quit' to exit.")
        print()
        
        while True:
            try:
                user_input = input("tableau> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self._show_interactive_help()
                
                elif user_input.lower() == 'examples':
                    self._show_examples()
                
                elif user_input.lower() == 'stats':
                    print("No recent operation to show statistics for.")
                
                elif user_input.startswith('test '):
                    formula_str = user_input[5:].strip()
                    self._interactive_test(formula_str, logic_system)
                
                elif user_input.startswith('models '):
                    formula_str = user_input[7:].strip()
                    self._interactive_models(formula_str, logic_system)
                
                elif user_input.startswith('wk3 '):
                    formula_str = user_input[4:].strip()
                    logic_system = "wk3"
                    print("Switching to WK3 (three-valued) logic...")
                    self._interactive_test(formula_str, logic_system)
                
                elif user_input.startswith('classical '):
                    formula_str = user_input[10:].strip()
                    logic_system = "classical"
                    print("Switching to classical logic...")
                    self._interactive_test(formula_str, logic_system)
                
                else:
                    # Treat as formula to test
                    self._interactive_test(user_input, logic_system)
            
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _show_interactive_help(self):
        """Show interactive help"""
        print("""Available commands:
  test <formula>        - Test satisfiability
  models <formula>      - Show all models
  wk3 <formula>         - Use WK3 logic
  classical <formula>   - Use classical logic
  stats                 - Show performance statistics
  examples              - Show example formulas
  help                  - Show this help
  quit                  - Exit""")
    
    def _show_examples(self):
        """Show example formulas"""
        print("""Example formulas to try:
  
  Basic Formulas:
    p                    - Simple atom
    p & q                - Conjunction
    p | q                - Disjunction
    ~p                   - Negation
    p -> q               - Implication
  
  Tautologies (always true):
    p | ~p               - Law of excluded middle
    (p -> q) | (q -> p)  - One direction must hold
  
  Contradictions (always false):
    p & ~p               - Contradiction
    (p -> q) & p & ~q    - Modus ponens failure
  
  Interesting Cases:
    (p | q) & (~p | r)   - Satisfiable with constraints
    (p & q) -> p         - Valid implication""")
    
    def _interactive_test(self, formula_str: str, logic_system: str):
        """Test formula in interactive mode"""
        try:
            formula = self.parser.parse(formula_str)
            
            if logic_system == "wk3":
                # For WK3, check if formula can be true OR undefined
                t3_tableau = three_valued_signed_tableau(T3(formula))
                u_tableau = three_valued_signed_tableau(U(formula))
                t3_satisfiable = t3_tableau.build()
                u_satisfiable = u_tableau.build()
                is_satisfiable = t3_satisfiable or u_satisfiable
            else:
                tableau = classical_signed_tableau(T(formula))
                is_satisfiable = tableau.build()
            
            print(f"Formula: {formula}")
            print(f"Logic: {logic_system.upper()}")
            print(f"Result: {'SATISFIABLE' if is_satisfiable else 'UNSATISFIABLE'}")
            
            if is_satisfiable:
                if logic_system == "wk3":
                    # Extract models from the satisfiable tableau
                    if t3_satisfiable:
                        models = t3_tableau.extract_all_models()
                    else:
                        models = u_tableau.extract_all_models()
                else:
                    models = tableau.extract_all_models()
                print(f"Found {len(models)} model(s)")
        
        except Exception as e:
            print(f"Error: {e}")
    
    def _interactive_models(self, formula_str: str, logic_system: str):
        """Show models for formula in interactive mode"""
        try:
            formula = self.parser.parse(formula_str)
            
            if logic_system == "wk3":
                # For WK3, check if formula can be true OR undefined
                t3_tableau = three_valued_signed_tableau(T3(formula))
                u_tableau = three_valued_signed_tableau(U(formula))
                t3_satisfiable = t3_tableau.build()
                u_satisfiable = u_tableau.build()
                is_satisfiable = t3_satisfiable or u_satisfiable
                
                # Extract models from the satisfiable tableau
                if is_satisfiable:
                    if t3_satisfiable:
                        models = t3_tableau.extract_all_models()
                    else:
                        models = u_tableau.extract_all_models()
                else:
                    models = []
            else:
                tableau = classical_signed_tableau(T(formula))
                is_satisfiable = tableau.build()
                models = tableau.extract_all_models() if is_satisfiable else []
            
            print(f"Formula: {formula}")
            print(f"Logic: {logic_system.upper()}")
            print(f"Result: {'SATISFIABLE' if is_satisfiable else 'UNSATISFIABLE'}")
            
            if models:
                print(f"Found {len(models)} model(s):")
                for i, model in enumerate(models[:10], 1):  # Show first 10
                    print(f"  Model {i}: {model}")
                if len(models) > 10:
                    print(f"  ... and {len(models) - 10} more")
            else:
                print("No satisfying models exist.")
        
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point"""
    cli = EnhancedTableauCLI()
    cli.run()


if __name__ == "__main__":
    main()