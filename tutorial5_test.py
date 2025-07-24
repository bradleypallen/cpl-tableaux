#!/usr/bin/env python3
"""Tutorial 5: Model Extraction and Analysis"""

from tableau_core import *

def understand_models():
    """Learn what models represent."""
    
    print("=== UNDERSTANDING MODELS ===\n")
    
    p = Atom("p")
    q = Atom("q")
    
    # Simple formula with multiple models
    formula = Disjunction(p, q)  # p ∨ q
    
    print(f"Formula: {formula}")
    print("This formula is true when at least one of p or q is true.")
    print()
    
    engine = classical_signed_tableau(T(formula))
    satisfiable = engine.build()
    
    if satisfiable:
        models = engine.extract_all_models()
        print(f"Found {len(models)} satisfying models:")
        
        for i, model in enumerate(models):
            print(f"\nModel {i+1}: {model}")
            
            # Verify this model satisfies the formula
            # Use unified model interface
            p_value = model.get_assignment('p')
            q_value = model.get_assignment('q')
            
            p_bool = bool(p_value)
            q_bool = bool(q_value)
                
            formula_value = p_bool or q_bool  # p ∨ q
            
            print(f"  p = {p_bool}, q = {q_bool}")
            print(f"  p ∨ q = {p_bool} ∨ {q_bool} = {formula_value}")
            print(f"  ✓ Model satisfies formula: {formula_value}")
    
    print("\nExplanation:")
    print("Each model represents a complete truth assignment to all atoms")
    print("that appear in the formula. Any assignment that makes the formula")
    print("true is a satisfying model.")

def analyze_model_spaces():
    """Analyze the space of all possible models."""
    
    print("\n=== MODEL SPACE ANALYSIS ===\n")
    
    p = Atom("p")
    q = Atom("q")
    r = Atom("r")
    
    formulas_to_analyze = [
        ("p", p),
        ("p ∧ q", Conjunction(p, q)),
        ("p ∨ q", Disjunction(p, q)),
        ("p → q", Implication(p, q)),
        ("(p ∨ q) ∧ (p ∨ r)", Conjunction(Disjunction(p, q), Disjunction(p, r))),
    ]
    
    for description, formula in formulas_to_analyze:
        print(f"Formula: {description}")
        
        engine = classical_signed_tableau(T(formula))
        satisfiable = engine.build()
        
        if satisfiable:
            models = engine.extract_all_models()
            print(f"  Models: {len(models)}")
            
            # Show all models
            for i, model in enumerate(models):
                assignments = []
                # Use unified model interface
                for atom, value in sorted(model.assignments.items()):
                    val_str = str(value).lower()
                    assignments.append(f"{atom}={val_str}")
                print(f"    {i+1}: {{{', '.join(assignments)}}}")
            
            # Calculate what fraction of total space this represents
            atoms_in_formula = set()
            extract_atoms(formula, atoms_in_formula)
            total_possible = 2 ** len(atoms_in_formula)
            fraction = len(models) / total_possible
            
            print(f"  Covers {len(models)}/{total_possible} = {fraction:.1%} of possible assignments")
        else:
            print(f"  Models: 0 (unsatisfiable)")
        
        print()

def extract_atoms(formula, atom_set):
    """Extract all atoms from a formula."""
    if isinstance(formula, Atom):
        atom_set.add(formula.name)
    elif hasattr(formula, 'operand'):  # Unary operator
        extract_atoms(formula.operand, atom_set)
    elif hasattr(formula, 'left') and hasattr(formula, 'right'):  # Binary operator
        extract_atoms(formula.left, atom_set)
        extract_atoms(formula.right, atom_set)

if __name__ == "__main__":
    understand_models()
    analyze_model_spaces()