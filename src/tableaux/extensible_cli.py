#!/usr/bin/env python3
"""
Extensible Command Line Interface for the Tableau System

This CLI uses the plugin architecture to support any registered logic system
via a general --logic parameter, replacing hardcoded switches like --wk3.

The CLI automatically discovers available logic systems and allows users to
specify them by name, making it easy to add new logic systems without
modifying the CLI code.
"""

import sys
import argparse
import json
import csv
import time
from typing import List, Dict, Any, Optional
from io import StringIO

# Import modern API components
from .api import LogicSystem
from .logics.logic_system import LogicRegistry
from .logics.classical import ClassicalLogic
from .logics.weak_kleene import WeakKleeneLogic
from .logics.wkrq import WkrqLogic

# Import FDE extension if available
try:
    from .logics.fde import FDELogic, add_fde_to_api
    FDE_AVAILABLE = True
except ImportError:
    FDE_AVAILABLE = False


class ExtensibleOutputFormatter:
    """Handle different output formats for extensible logic systems."""
    
    @staticmethod
    def format_result(result_data: Dict[str, Any], format_type: str) -> str:
        """Format results according to specified format."""
        if format_type == "json":
            return json.dumps(result_data, indent=2, default=str)
        elif format_type == "csv":
            return ExtensibleOutputFormatter._format_csv(result_data)
        else:
            return ExtensibleOutputFormatter._format_default(result_data)
    
    @staticmethod
    def _format_csv(result_data: Dict[str, Any]) -> str:
        """Format as CSV."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        header = ["formula", "logic", "satisfiable", "model_count"]
        if "models" in result_data and result_data["models"]:
            # Add atom columns based on first model
            first_model = result_data["models"][0]
            if hasattr(first_model, 'valuation'):
                atoms = sorted(first_model.valuation.keys())
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
                if hasattr(model, 'valuation'):
                    atoms = sorted(model.valuation.keys())
                    for atom in atoms:
                        row.append(str(model.valuation[atom]))
                writer.writerow(row)
        else:
            row = [formula, logic, satisfiable, 0]
            writer.writerow(row)
        
        return output.getvalue().strip()
    
    @staticmethod
    def _format_default(result_data: Dict[str, Any]) -> str:
        """Format as default text output."""
        lines = []
        lines.append(f"Formula: {result_data.get('formula', 'Unknown')}")
        lines.append(f"Logic: {result_data.get('logic', 'classical')}")
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


class ExtensibleTableauCLI:
    """Extensible CLI using the plugin architecture."""
    
    def __init__(self):
        self._register_core_logics()
        self.setup_argument_parser()
    
    def _register_core_logics(self):
        """Register core logic systems and extensions."""
        # Register core logic systems
        if not LogicRegistry.is_registered("classical"):
            LogicRegistry.register(ClassicalLogic("classical"))
        
        if not LogicRegistry.is_registered("weak_kleene"):
            LogicRegistry.register(WeakKleeneLogic("weak_kleene"), ["wk3"])
        
        if not LogicRegistry.is_registered("wkrq"):
            LogicRegistry.register(WkrqLogic("wkrq"))
        
        # Register FDE if available
        if FDE_AVAILABLE:
            if not LogicRegistry.is_registered("fde"):
                LogicRegistry.register(FDELogic("fde"))
            add_fde_to_api()
    
    def get_available_logics(self) -> List[str]:
        """Get list of all available logic system names."""
        return LogicRegistry.list_systems()
    
    def setup_argument_parser(self):
        """Setup command line argument parser."""
        available_logics = self.get_available_logics()
        logic_help = f"Logic system to use. Available: {', '.join(available_logics)} (default: classical)"
        
        self.arg_parser = argparse.ArgumentParser(
            description="Extensible Tableau Logic System - Supports multiple logic systems via plugins",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
Examples:
  %(prog)s "p | ~p"                        # Classical logic (default)
  %(prog)s --logic=classical "p & ~p"      # Explicit classical logic
  %(prog)s --logic=weak_kleene "p & ~p"    # Three-valued weak Kleene logic  
  %(prog)s --logic=wkrq "p | ~p"           # Four-valued wKrQ logic
  %(prog)s --logic=fde "p & ~p"            # First-Degree Entailment logic
  %(prog)s --models "p | q"                # Show all models
  %(prog)s --stats "complex_formula"       # Show statistics
  %(prog)s --format=json "p"               # JSON output
  %(prog)s --file=formulas.txt             # Process file
  %(prog)s                                 # Interactive mode

Available Logic Systems: {', '.join(available_logics)}
Default Logic System: classical
            """
        )
        
        # Positional argument for formula
        self.arg_parser.add_argument(
            'formula', 
            nargs='?', 
            help='Formula to test (if not provided, enters interactive mode)'
        )
        
        # Logic system selection - extensible approach
        self.arg_parser.add_argument(
            '--logic', 
            choices=available_logics,
            default='classical',
            help=logic_help
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
        
        # Sign specification
        self.arg_parser.add_argument(
            '--sign',
            default='T',
            help='Sign to use for tableau construction (default: T). Available signs depend on logic system.'
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
            help='Show debugging information including tableau tree'
        )
        self.arg_parser.add_argument(
            '--validate-only', 
            action='store_true', 
            help='Only validate formula syntax, don\'t solve'
        )
        self.arg_parser.add_argument(
            '--list-logics',
            action='store_true',
            help='List all available logic systems and exit'
        )
    
    def run(self, args=None):
        """Main CLI entry point."""
        if args is None:
            args = sys.argv[1:]
        
        parsed_args = self.arg_parser.parse_args(args)
        
        # Handle list-logics option
        if parsed_args.list_logics:
            self._list_logics()
            return
        
        # Determine logic system (handle backward compatibility)
        logic_name = self._determine_logic_system(parsed_args)
        
        # Handle different modes
        if parsed_args.file:
            self._process_file(parsed_args.file, logic_name, parsed_args)
        elif parsed_args.batch:
            self._process_batch(logic_name, parsed_args)
        elif parsed_args.formula:
            self._process_single_formula(parsed_args.formula, logic_name, parsed_args)
        else:
            self._interactive_mode(logic_name)
    
    def _determine_logic_system(self, args) -> str:
        """Determine which logic system to use."""
        return args.logic
    
    def _list_logics(self):
        """List all available logic systems."""
        print("Available Logic Systems:")
        print("=" * 40)
        
        for logic_name in self.get_available_logics():
            try:
                # Get logic system info
                if logic_name == "classical":
                    description = "Classical two-valued propositional logic"
                elif logic_name == "weak_kleene":
                    description = "Three-valued weak Kleene logic (T, F, U)"
                elif logic_name == "wkrq":
                    description = "Four-valued wKrQ epistemic logic (T, F, M, N)"
                elif logic_name == "fde":
                    description = "First-Degree Entailment - paraconsistent and paracomplete (T, F, B, N)"
                else:
                    description = "Custom logic system"
                
                # Get available signs
                logic_system = self._get_logic_system(logic_name)
                sign_system = logic_system._logic.get_sign_system()
                signs = [str(sign) for sign in sign_system.signs()]
                
                print(f"  {logic_name:12} - {description}")
                print(f"  {'':12}   Signs: {', '.join(signs)}")
                print()
                
            except Exception as e:
                print(f"  {logic_name:12} - Error loading: {e}")
                print()
    
    def _get_logic_system(self, logic_name: str) -> LogicSystem:
        """Get a LogicSystem instance for the given logic name."""
        if logic_name == "classical":
            return LogicSystem.classical()
        elif logic_name == "weak_kleene":
            return LogicSystem.weak_kleene()
        elif logic_name == "wkrq":
            return LogicSystem.wkrq()
        elif logic_name == "fde" and FDE_AVAILABLE:
            return LogicSystem.fde()
        else:
            # Try to create directly from registry
            if LogicRegistry.is_registered(logic_name):
                logic = LogicRegistry.get(logic_name)
                return LogicSystem(logic)
            else:
                raise ValueError(f"Unknown logic system: {logic_name}")
    
    def _process_single_formula(self, formula_str: str, logic_name: str, args):
        """Process a single formula."""
        try:
            start_time = time.time()
            
            # Get logic system
            logic_system = self._get_logic_system(logic_name)
            
            # Parse formula
            formula = logic_system.parse(formula_str)
            
            if args.validate_only:
                result_data = {
                    "formula": str(formula),
                    "logic": logic_name,
                    "valid_syntax": True
                }
                print(ExtensibleOutputFormatter.format_result(result_data, args.format))
                return
            
            # Solve with specified sign
            result = logic_system.solve(formula, args.sign, track_steps=args.debug)
            
            end_time = time.time()
            
            # Prepare result data
            result_data = {
                "formula": str(formula),
                "logic": logic_name,
                "satisfiable": result.satisfiable,
                "sign": args.sign,
                "models": result.models[:args.max_models] if args.models and result.models else []
            }
            
            if args.stats:
                result_data["statistics"] = {
                    "construction_time": f"{end_time - start_time:.4f}s",
                    "model_count": len(result.models),
                    "logic_system": logic_name,
                    "sign_used": args.sign
                }
            
            # Output result
            print(ExtensibleOutputFormatter.format_result(result_data, args.format))
            
            # Debug output
            if args.debug and result.tableau:
                print("\nDEBUG: Tableau Construction:")
                print(result.tableau.print_tree(show_steps=True))
        
        except Exception as e:
            error_data = {
                "formula": formula_str,
                "logic": logic_name,
                "error": str(e)
            }
            print(f"Error: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
    
    def _process_file(self, filename: str, logic_name: str, args):
        """Process formulas from a file."""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            formulas = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    formulas.append(line)
            
            print(f"Processing {len(formulas)} formulas from {filename}")
            print(f"Logic system: {logic_name}")
            print(f"Sign: {args.sign}")
            print("=" * 50)
            
            logic_system = self._get_logic_system(logic_name)
            results = []
            
            for i, formula_str in enumerate(formulas, 1):
                print(f"\nFormula {i}: {formula_str}")
                try:
                    formula = logic_system.parse(formula_str)
                    result = logic_system.solve(formula, args.sign)
                    
                    result_data = {
                        "formula": str(formula),
                        "logic": logic_name,
                        "satisfiable": result.satisfiable,
                        "sign": args.sign,
                        "models": result.models[:args.max_models] if args.models and result.models else []
                    }
                    results.append(result_data)
                    
                    print(f"  Result: {'SAT' if result.satisfiable else 'UNSAT'}")
                    if result.models:
                        print(f"  Models: {len(result.models)}")
                
                except Exception as e:
                    print(f"  Error: {e}")
                    results.append({
                        "formula": formula_str,
                        "logic": logic_name,
                        "error": str(e)
                    })
            
            # Summary output
            if args.format != "default":
                for result in results:
                    print(ExtensibleOutputFormatter.format_result(result, args.format))
        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
        except Exception as e:
            print(f"Error processing file: {e}")
    
    def _process_batch(self, logic_name: str, args):
        """Process multiple formulas from stdin or command line."""
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
            print(f"Logic: {logic_name}, Sign: {args.sign}")
            for i, formula_str in enumerate(formulas, 1):
                print(f"\n{i}. {formula_str}")
                self._process_single_formula(formula_str, logic_name, args)
        else:
            print("No formulas provided.")
    
    def _interactive_mode(self, logic_name: str):
        """Interactive mode with extensible logic support."""
        current_logic = logic_name
        current_sign = "T"
        
        print("Welcome to the Extensible Tableau Logic System!")
        print(f"Current logic: {current_logic}")
        print("Type 'help' for commands, 'quit' to exit.")
        print()
        
        while True:
            try:
                user_input = input(f"tableau[{current_logic}]> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self._show_interactive_help()
                
                elif user_input.lower() == 'logics':
                    self._list_logics()
                
                elif user_input.lower() == 'examples':
                    self._show_examples(current_logic)
                
                elif user_input.startswith('logic '):
                    new_logic = user_input[6:].strip()
                    if new_logic in self.get_available_logics():
                        current_logic = new_logic
                        print(f"Switched to {current_logic} logic")
                    else:
                        print(f"Unknown logic: {new_logic}")
                        print(f"Available: {', '.join(self.get_available_logics())}")
                
                elif user_input.startswith('sign '):
                    current_sign = user_input[5:].strip()
                    print(f"Sign set to: {current_sign}")
                
                elif user_input.startswith('test '):
                    formula_str = user_input[5:].strip()
                    self._interactive_test(formula_str, current_logic, current_sign)
                
                elif user_input.startswith('models '):
                    formula_str = user_input[7:].strip()
                    self._interactive_models(formula_str, current_logic, current_sign)
                
                else:
                    # Treat as formula to test
                    self._interactive_test(user_input, current_logic, current_sign)
            
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _show_interactive_help(self):
        """Show interactive help."""
        available_logics = ', '.join(self.get_available_logics())
        print(f"""Available commands:
  test <formula>        - Test satisfiability with current logic/sign
  models <formula>      - Show all models for formula
  logic <name>          - Switch logic system (available: {available_logics})
  sign <sign>           - Set sign for tableau construction (e.g., T, F, U, B, N)
  logics                - List all available logic systems with details
  examples              - Show example formulas for current logic  
  help                  - Show this help
  quit                  - Exit

Current shortcuts:
  <formula>             - Same as 'test <formula>'
  """)
    
    def _show_examples(self, logic_name: str):
        """Show example formulas relevant to the current logic."""
        print(f"Example formulas for {logic_name} logic:")
        print()
        
        # Common examples
        print("Basic Formulas:")
        print("  p                    - Simple atom")
        print("  p & q                - Conjunction")
        print("  p | q                - Disjunction")
        print("  ~p                   - Negation")
        if logic_name != "fde":  # FDE doesn't have implication
            print("  p -> q               - Implication")
        print()
        
        # Logic-specific examples
        if logic_name == "classical":
            print("Classical Logic Examples:")
            print("  p | ~p               - Tautology (law of excluded middle)")
            print("  p & ~p               - Contradiction")
            print("  (p -> q) & p & ~q    - Unsatisfiable (modus ponens)")
        
        elif logic_name == "weak_kleene":
            print("Weak Kleene Logic Examples:")
            print("  p | ~p               - Still valid (unlike some 3-valued logics)")
            print("  p & ~p               - Still contradiction")
            print("  Signs: T (true), F (false), U (undefined)")
            print("  Try: tableaux --logic=weak_kleene --sign=U \"p\"")
        
        elif logic_name == "wkrq":
            print("wKrQ Logic Examples:")
            print("  p | ~p               - Not valid (paracomplete)")
            print("  Signs: T (true), F (false), M, N (epistemic)")
            print("  Try: tableaux --logic=wkrq --sign=M \"p\"")
        
        elif logic_name == "fde":
            print("FDE Logic Examples (paraconsistent & paracomplete):")
            print("  p & ~p               - Satisfiable! (paraconsistent)")
            print("  p | ~p               - Not valid (paracomplete)")
            print("  Signs: T (true only), F (false only), B (both), N (neither)")
            print("  Try: tableaux --logic=fde --sign=B \"p\"")
        
        print()
        print("Try these with different signs and logic systems!")
    
    def _interactive_test(self, formula_str: str, logic_name: str, sign: str):
        """Test formula in interactive mode."""
        try:
            logic_system = self._get_logic_system(logic_name)
            formula = logic_system.parse(formula_str)
            result = logic_system.solve(formula, sign)
            
            print(f"Formula: {formula}")
            print(f"Logic: {logic_name}")
            print(f"Sign: {sign}")
            print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
            
            if result.satisfiable and result.models:
                print(f"Found {len(result.models)} model(s)")
        
        except Exception as e:
            print(f"Error: {e}")
    
    def _interactive_models(self, formula_str: str, logic_name: str, sign: str):
        """Show models for formula in interactive mode."""
        try:
            logic_system = self._get_logic_system(logic_name)
            formula = logic_system.parse(formula_str)
            result = logic_system.solve(formula, sign)
            
            print(f"Formula: {formula}")
            print(f"Logic: {logic_name}")
            print(f"Sign: {sign}")
            print(f"Result: {'SATISFIABLE' if result.satisfiable else 'UNSATISFIABLE'}")
            
            if result.models:
                print(f"Found {len(result.models)} model(s):")
                for i, model in enumerate(result.models[:10], 1):  # Show first 10
                    print(f"  Model {i}: {model}")
                if len(result.models) > 10:
                    print(f"  ... and {len(result.models) - 10} more")
            else:
                print("No satisfying models exist.")
        
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point for extensible CLI."""
    cli = ExtensibleTableauCLI()
    cli.run()


if __name__ == "__main__":
    main()