#!/usr/bin/env python3
"""
Test for Corrected wKrQ Implementation

Tests the corrected wKrQ implementation with proper Ferguson (2021) syntax:
[∃X φ(X)]ψ(X) and [∀X φ(X)]ψ(X)
"""

from formula import RestrictedExistentialFormula, RestrictedUniversalFormula, Predicate
from term import Variable, Constant


def test_corrected_formula_classes():
    """Test the corrected formula classes with proper structure"""
    print("Testing corrected wKrQ formula classes...")
    
    # Create test terms
    x = Variable("X")
    john = Constant("john")
    
    # Create predicates
    student_x = Predicate("Student", [x])
    human_x = Predicate("Human", [x])
    bachelor_x = Predicate("Bachelor", [x])
    unmarried_male_x = Predicate("UnmarriedMale", [x])
    
    # Create restricted existential formula: [∃X Student(X)]Human(X)
    exists_student_human = RestrictedExistentialFormula(x, student_x, human_x)
    
    # Create restricted universal formula: [∀X Bachelor(X)]UnmarriedMale(X)
    all_bachelor_unmarried = RestrictedUniversalFormula(x, bachelor_x, unmarried_male_x)
    
    # Test string representations
    print(f"Restricted existential: {exists_student_human}")
    print(f"Restricted universal: {all_bachelor_unmarried}")
    
    # Test properties
    assert not exists_student_human.is_atomic()
    assert not exists_student_human.is_literal()
    assert not exists_student_human.is_ground()
    
    # Test variable extraction (bound variable should be excluded)
    free_vars = exists_student_human.get_variables()
    assert len(free_vars) == 0, f"Expected no free variables, got {free_vars}"
    
    print("✓ Corrected formula classes work correctly")


def test_subsumption_examples():
    """Test examples that express subsumption relationships"""
    print("\nTesting subsumption relationship examples...")
    
    x = Variable("X")
    
    # Example 1: Every bachelor is an unmarried male
    bachelor_x = Predicate("Bachelor", [x])
    unmarried_male_x = Predicate("UnmarriedMale", [x])
    bachelor_subsumption = RestrictedUniversalFormula(x, bachelor_x, unmarried_male_x)
    
    print(f"Bachelor subsumption: {bachelor_subsumption}")
    
    # Example 2: Every student is a person  
    student_x = Predicate("Student", [x])
    person_x = Predicate("Person", [x])
    student_subsumption = RestrictedUniversalFormula(x, student_x, person_x)
    
    print(f"Student subsumption: {student_subsumption}")
    
    # Example 3: There exists a student who is human
    human_x = Predicate("Human", [x])
    student_human_exists = RestrictedExistentialFormula(x, student_x, human_x)
    
    print(f"Student-human existence: {student_human_exists}")
    
    print("✓ Subsumption relationship examples created correctly")


def test_formula_structure():
    """Test that the formula structure matches Ferguson's specification"""
    print("\nTesting formula structure...")
    
    x = Variable("X")
    dog_x = Predicate("Dog", [x])
    animal_x = Predicate("Animal", [x])
    
    # [∀X Dog(X)]Animal(X) - "Every dog is an animal"
    dog_animal = RestrictedUniversalFormula(x, dog_x, animal_x)
    
    # Check that we have the correct components
    assert dog_animal.variable == x
    assert dog_animal.antecedent == dog_x  # φ(X) part
    assert dog_animal.consequent == animal_x  # ψ(X) part
    assert dog_animal.quantifier_type == "restricted_universal"
    
    # Check string representation shows correct brackets
    expected_str = "[∀X Dog(X)]Animal(X)"
    actual_str = str(dog_animal)
    assert actual_str == expected_str, f"Expected '{expected_str}', got '{actual_str}'"
    
    print(f"Formula structure correct: {dog_animal}")
    print("✓ Formula structure matches Ferguson (2021) specification")


if __name__ == "__main__":
    print("=" * 60)
    print("Corrected wKrQ Implementation Test")
    print("=" * 60)
    
    try:
        test_corrected_formula_classes()
        test_subsumption_examples() 
        test_formula_structure()
        
        print("\n" + "=" * 60)
        print("🎉 All corrected wKrQ tests passed!")
        print("The implementation now correctly represents Ferguson's")
        print("restricted quantification syntax: [∃X φ(X)]ψ(X) and [∀X φ(X)]ψ(X)")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()