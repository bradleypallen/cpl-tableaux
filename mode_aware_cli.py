#!/usr/bin/env python3
"""
Mode-Aware Command Line Interface for the Tableau System

Supports separate propositional logic and first-order logic modes with
appropriate syntax validation and tableau systems for each.
"""

import sys
import argparse
from typing import Optional

from logic_mode import LogicMode, ModeError, get_mode_validator
from mode_aware_parser import ModeAwareParser
from tableau import Tableau
from wk3_tableau import WK3Tableau


class ModeAwareTableauCLI:
    """CLI with mode-aware parsing and tableau selection"""
    
    def __init__(self, logic_mode: LogicMode = LogicMode.PROPOSITIONAL, 
                 truth_system: str = "classical"):
        self.logic_mode = logic_mode
        self.truth_system = truth_system  # "classical" or "wk3"
        self.parser = ModeAwareParser(logic_mode)
        self.validator = get_mode_validator(logic_mode)
    
    def process_formula(self, formula_str: str) -> None:
        """Process a single formula through the tableau system"""
        try:
            # Parse formula according to current mode
            formula = self.parser.parse(formula_str)
            
            print(f"Parsed formula: {formula}")
            print("Testing satisfiability...")
            print("-" * 40)
            
            # Create appropriate tableau
            if self.truth_system == "wk3":
                tableau = WK3Tableau(formula)
            else:
                tableau = Tableau(formula)
            
            # Build tableau
            is_satisfiable = tableau.build()
            
            # Show results
            print(f"\nRESULT: {'SATISFIABLE' if is_satisfiable else 'UNSATISFIABLE'}")
            
            # Show tableau tree
            print()
            tableau.print_tree()
            
        except ModeError as e:
            print(f"Mode Error: {e}")
            if e.suggestions:
                print(f"\nSyntax Help:")
                print(e.suggestions)
        except Exception as e:
            print(f"Error: {e}")
    
    def interactive_mode(self) -> None:
        """Run interactive mode with mode-aware prompts"""
        mode_name = str(self.logic_mode).replace('-', ' ').title()
        truth_name = "Weak Kleene Logic (WK3)" if self.truth_system == "wk3" else "Classical Logic"
        
        print(f"Interactive Tableau System - {mode_name} + {truth_name}")
        print("=" * 60)
        print(self.validator.get_syntax_description())
        print("\nCommands:")
        print("  help    - Show this help")
        print("  mode    - Show current mode info")
        print("  quit    - Exit the program")
        print("  <formula> - Test formula satisfiability")
        print()
        
        while True:
            try:
                user_input = input(f"{self.logic_mode.name.lower()}> ").strip()
                
                if not user_input:
                    continue
                elif user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                elif user_input.lower() in ['help', 'h']:
                    print(self.validator.get_syntax_description())
                elif user_input.lower() == 'mode':
                    print(f"Logic Mode: {mode_name}")
                    print(f"Truth System: {truth_name}")
                    print(self.validator.get_syntax_description())
                else:
                    # Process as formula
                    print()
                    self.process_formula(user_input)
                    print()
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Tableau-based satisfiability checker for propositional and first-order logic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Propositional logic (default)
  python %(prog)s "p & q -> r"
  python %(prog)s --prop "p | ~p"
  
  # First-order logic  
  python %(prog)s --fol "Student(john) & Smart(john)"
  python %(prog)s --fol "Mortal(socrates) -> ~Immortal(socrates)"
  
  # With weak Kleene logic
  python %(prog)s --wk3 "p | ~p"
  python %(prog)s --fol --wk3 "Student(john) | ~Student(john)"
        """
    )
    
    # Logic mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--prop', '--propositional', 
        action='store_true',
        help='Use propositional logic mode (default)'
    )
    mode_group.add_argument(
        '--fol', '--first-order',
        action='store_true', 
        help='Use first-order logic mode'
    )
    
    # Truth system selection  
    truth_group = parser.add_mutually_exclusive_group()
    truth_group.add_argument(
        '--classical', '--cpl',
        action='store_true',
        help='Use classical logic (default)'
    )
    truth_group.add_argument(
        '--wk3', '--weak-kleene',
        action='store_true',
        help='Use weak Kleene logic (3-valued)'
    )
    
    # Formula input
    parser.add_argument(
        'formula',
        nargs='*',
        help='Formula to test (if not provided, starts interactive mode)'
    )
    
    return parser


def main():
    """Main entry point with argument parsing"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Determine logic mode
    if args.fol:
        logic_mode = LogicMode.FIRST_ORDER
    else:
        logic_mode = LogicMode.PROPOSITIONAL  # Default
    
    # Determine truth system
    if args.wk3:
        truth_system = "wk3"
    else:
        truth_system = "classical"  # Default
    
    # Create CLI instance
    cli = ModeAwareTableauCLI(logic_mode, truth_system)
    
    # Process formula or start interactive mode
    if args.formula:
        # Command line mode
        formula_str = ' '.join(args.formula)
        
        mode_name = str(logic_mode).replace('-', ' ').title()
        truth_name = "Weak Kleene Logic (WK3)" if truth_system == "wk3" else "Classical Logic"
        
        print(f"Tableau System - {mode_name} + {truth_name}")
        print("=" * 55)
        print()
        
        cli.process_formula(formula_str)
    else:
        # Interactive mode
        cli.interactive_mode()


if __name__ == "__main__":
    main()