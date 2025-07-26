# CLI Usage Guide: Tableau System

**Version**: 2.0 (Extensible CLI)  
**Last Updated**: January 2025  
**License**: MIT  

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Commands](#basic-commands)
3. [Logic System Selection](#logic-system-selection)
4. [Output Formats](#output-formats)
5. [Interactive Mode](#interactive-mode)
6. [Advanced Features](#advanced-features)
7. [Batch Processing](#batch-processing)
8. [Examples and Use Cases](#examples-and-use-cases)
9. [Troubleshooting](#troubleshooting)

## Quick Start

### Installation Check

```bash
# Verify the system is working
tableaux "p | ~p"
# Expected output: SATISFIABLE with models
```

### Your First Commands

```bash
# Test a tautology
tableaux "p | ~p"

# Test a contradiction
tableaux "p & ~p"

# Test with different logic systems
tableaux --logic=weak_kleene "p | ~p"
tableaux --logic=wkrq "p & ~p"

# Interactive mode
tableaux
```

## Basic Commands

### Command Structure

```bash
tableaux [OPTIONS] [FORMULA]
```

**Core Options:**
- `--logic=SYSTEM`: Choose logic system (default: classical)
- `--models`: Show all satisfying models
- `--sign=SIGN`: Test with specific sign
- `--format=FORMAT`: Output format (text, json)
- `--debug`: Show detailed tableau construction
- `--list-logics`: List available logic systems

### Basic Formula Testing

```bash
# Satisfiability testing (default behavior)
tableaux "p -> q"
tableaux "p & q"
tableaux "(p | q) & ~p"

# Test specific signs
tableaux --sign=F "p | ~p"              # Can excluded middle be false?
tableaux --sign=T "(p & q) -> p"        # Can this be true?

# Show all models
tableaux --models "p -> q"
tableaux --models "(p & q) | (r & s)"
```

### Formula Syntax

The CLI uses standard logical notation:

**Operators (precedence high to low):**
- `~p` - Negation (NOT)
- `p & q` - Conjunction (AND)
- `p | q` - Disjunction (OR)
- `p -> q` - Implication (IMPLIES)

**Parentheses for grouping:**
```bash
tableaux "p & (q | r)"
tableaux "((p -> q) & p) -> q"
tableaux "~(p & q) -> (~p | ~q)"
```

**Atoms:**
- Single letters: `p`, `q`, `r`, `s`, etc.
- Multi-character: `p1`, `q2`, `prop`, `atom`

## Logic System Selection

### Available Logic Systems

```bash
# List all available systems
tableaux --list-logics
```

**Built-in Systems:**
- `classical` (default) - Two-valued logic (T, F)
- `weak_kleene` - Three-valued logic (T, F, U)
- `wkrq` - Four-valued epistemic logic (T, F, M, N)

### Using Different Logic Systems

```bash
# Classical logic (default)
tableaux "p & ~p"                      # Unsatisfiable

# Weak Kleene logic
tableaux --logic=weak_kleene "p & ~p"  # May be satisfiable
tableaux --logic=weak_kleene "p | ~p"  # Not always tautology

# wKrQ logic
tableaux --logic=wkrq "p & ~p"         # Paraconsistent
tableaux --logic=wkrq --sign=M "p"     # Can p be both true and false?
```

### Sign Testing by Logic System

**Classical Logic:**
```bash
tableaux --sign=T "p -> q"    # Can be true
tableaux --sign=F "p | ~p"    # Can excluded middle be false? (No)
```

**Weak Kleene Logic:**
```bash
tableaux --logic=weak_kleene --sign=T "p | ~p"  # Can be true
tableaux --logic=weak_kleene --sign=F "p | ~p"  # Can be false
tableaux --logic=weak_kleene --sign=U "p | ~p"  # Can be undefined
```

**wKrQ Logic:**
```bash
tableaux --logic=wkrq --sign=T "p"   # True only
tableaux --logic=wkrq --sign=F "p"   # False only  
tableaux --logic=wkrq --sign=M "p"   # Both true and false
tableaux --logic=wkrq --sign=N "p"   # Neither true nor false
```


## Output Formats

### Text Output (Default)

```bash
tableaux "p -> q"
# Output:
# Formula: (p -> q)
# Status: SATISFIABLE
# Models: 3
```

### Detailed Model Display

```bash
tableaux --models "p -> q"
# Output:
# Formula: (p -> q)
# Status: SATISFIABLE
# Models: 3
# 
# Model 1: {p: False, q: False}
# Model 2: {p: False, q: True}  
# Model 3: {p: True, q: True}
```

### JSON Output

```bash
tableaux --format=json "p -> q"
# Output:
# {
#   "formula": "(p -> q)",
#   "satisfiable": true,
#   "models": [
#     {"p": false, "q": false},
#     {"p": false, "q": true},
#     {"p": true, "q": true}
#   ]
# }
```

### Debug Output

```bash
tableaux --debug "p & q"
# Shows step-by-step tableau construction:
# Initial: T:(p & q)
# Apply T-Conjunction: T:p, T:q
# Branch closed: satisfiable
# Model: {p: True, q: True}
```

## Interactive Mode

### Starting Interactive Mode

```bash
tableaux
# Enters interactive mode
tableau[classical]> 
```

### Interactive Commands

**Formula Testing:**
```
tableau[classical]> p -> q
tableau[classical]> test (p & q) | r
tableau[classical]> models p | ~p
```

**Logic System Switching:**
```
tableau[classical]> logic weak_kleene
tableau[weak_kleene]> logic wkrq
tableau[wkrq]> logic classical
```

**Sign Testing:**
```
tableau[classical]> sign F
tableau[classical]> test p | ~p        # Test with F sign
tableau[classical]> sign T             # Reset to T sign
```

**Information Commands:**
```
tableau[classical]> help               # Show help
tableau[classical]> logics             # List available logics
tableau[classical]> examples           # Show example formulas
tableau[classical]> quit               # Exit
```

### Interactive Examples

```
tableau[classical]> examples
Example formulas:
  p | ~p          # Excluded middle (tautology)
  p & ~p          # Contradiction
  p -> q          # Implication
  (p & q) -> p    # Simplification
  p -> (q -> p)   # Axiom K

tableau[classical]> test p | ~p
Formula: (p | ~p)
Status: SATISFIABLE
Models: 2

tableau[classical]> logic weak_kleene
tableau[weak_kleene]> test p | ~p
Formula: (p | ~p)  
Status: SATISFIABLE
Models: 3

tableau[weak_kleene]> sign U
tableau[weak_kleene]> test p | ~p
Formula: (p | ~p)
Status: SATISFIABLE (with sign U)
Models: 1
```

## Advanced Features

### Statistics and Performance

```bash
tableaux --stats "complex_formula"
# Shows:
# - Construction time
# - Number of branches
# - Rule applications
# - Memory usage
```

### Batch Formula Testing

```bash
# Test multiple formulas
echo "p | ~p
p & ~p  
p -> q
(p & q) -> p" | tableaux --batch

# With different logic systems
echo "p & ~p" | tableaux --batch --logic=classical
```

### Output Redirection

```bash
# Save results to file
tableaux --models "complex_formula" > results.txt

# JSON output for processing
tableaux --format=json "p -> q" | jq '.models | length'
```

### Comparison Across Logic Systems

```bash
# Test same formula across all systems
for logic in classical weak_kleene wkrq; do
    echo "=== $logic ==="
    tableaux --logic=$logic "p & ~p"
done
```

## Batch Processing

### Using Echo and Pipes

```bash
# Single formula
echo "p -> q" | tableaux

# Multiple formulas
echo -e "p | ~p\np & ~p\np -> q" | tableaux --batch
```

### File Input

```bash
# Create formula file
cat > formulas.txt << EOF
p | ~p
p & ~p
(p -> q) & p & ~q
p -> (q -> p)
EOF

# Process file
cat formulas.txt | tableaux --batch --logic=classical
```

### Processing with Different Options

```bash
# Test with models
cat formulas.txt | tableaux --batch --models

# Test with JSON output
cat formulas.txt | tableaux --batch --format=json

# Test with different logic systems
cat formulas.txt | tableaux --batch --logic=weak_kleene
```

## Examples and Use Cases

### Testing Classical Logic Properties

```bash
# Test tautologies
tableaux "p | ~p"                    # Excluded middle
tableaux "(p -> q) -> ((q -> r) -> (p -> r))"  # Transitivity
tableaux "p -> (q -> p)"             # Axiom K

# Test contradictions
tableaux "p & ~p"                    # Basic contradiction
tableaux "(p -> q) & p & ~q"         # Modus ponens failure

# Test contingencies with models
tableaux --models "p -> q"           # Show all truth assignments
tableaux --models "(p & q) | (r & s)"  # Complex formula
```

### Exploring Non-Classical Logic

```bash
# Weak Kleene logic exploration
tableaux --logic=weak_kleene "p | ~p"       # Not always tautology
tableaux --logic=weak_kleene --sign=U "p"   # Undefined values
tableaux --logic=weak_kleene --models "p & q"  # Three-valued models

# Paraconsistent logic (contradictions satisfiable)
tableaux --logic=wkrq "p & ~p"              # Satisfiable in wKrQ
```

### Argument Validity Testing

```bash
# Test valid argument forms
# Modus ponens: p -> q, p ⊢ q
# Cannot directly test entailment in CLI, but can test:
tableaux "(p -> q) & p & ~q"         # Should be unsatisfiable

# Modus tollens: p -> q, ~q ⊢ ~p  
tableaux "(p -> q) & ~q & p"         # Should be unsatisfiable

# Disjunctive syllogism: p | q, ~p ⊢ q
tableaux "(p | q) & ~p & ~q"         # Should be unsatisfiable
```

### Formula Analysis

```bash
# Analyze complex formulas
tableaux --models --debug "(p & q) -> (r | s)"

# Compare across logic systems
formula="(p -> q) -> (~q -> ~p)"     # Contraposition
tableaux "$formula"
tableaux --logic=weak_kleene "$formula"
tableaux --logic=wkrq "$formula"
```

### Performance Testing

```bash
# Test complex formulas
tableaux --stats "((p1 & p2) | (p3 & p4)) -> ((p5 | p6) & (p7 | p8))"

# Batch performance testing
time echo -e "p1 | p2\n(p1 & p2) | (p3 & p4)\n((p1 & p2) | (p3 & p4)) -> (p5 | p6)" | tableaux --batch
```

## Troubleshooting

### Common Issues

**1. Formula Parsing Errors:**
```bash
# Wrong: Missing quotes
tableaux p -> q          # Error: shell interprets ->

# Right: Use quotes  
tableaux "p -> q"        # Correct

# Wrong: Invalid operators
tableaux "p → q"         # Error: Unicode arrow not supported

# Right: Use ASCII
tableaux "p -> q"        # Correct
```

**2. Logic System Not Found:**
```bash
# Check available systems
tableaux --list-logics

# Use correct name
tableaux --logic=weak_kleene "p | ~p"   # Correct
tableaux --logic=kleene "p | ~p"        # Error: not found
```

**3. Invalid Signs:**
```bash
# Check valid signs for logic system
tableaux --logic=classical --sign=U "p"   # Error: U not valid in classical

# Use appropriate signs
tableaux --logic=weak_kleene --sign=U "p"  # Correct
```

### Error Messages

**Parse Errors:**
```bash
tableaux "p & & q"
# Error: Invalid formula syntax at position 4
# Expected: atom or opening parenthesis
```

**Logic System Errors:**
```bash
tableaux --logic=nonexistent "p"
# Error: Unknown logic system 'nonexistent'
# Available systems: classical, weak_kleene, wkrq
```

**Sign Errors:**
```bash
tableaux --logic=classical --sign=M "p"
# Error: Sign 'M' not valid for logic system 'classical'
# Valid signs: T, F
```

### Getting Help

```bash
# Command-line help
tableaux --help

# Interactive help
tableaux
tableau[classical]> help

# List available options
tableaux --list-logics
```

### Debug Information

```bash
# Show detailed tableau construction
tableaux --debug "p & q"

# Show statistics
tableaux --stats "complex_formula"

# JSON output for programmatic analysis
tableaux --format=json "p -> q" | jq '.'
```

### Performance Issues

```bash
# For very complex formulas, use stats to monitor
tableaux --stats --debug "very_complex_formula"

# Consider simplifying or breaking down complex formulas
tableaux "part1_of_formula"
tableaux "part2_of_formula"
```

## Integration with Other Tools

### Shell Scripting

```bash
#!/bin/bash
# Test multiple logic systems
formula="p & ~p"
for logic in classical weak_kleene wkrq; do
    result=$(tableaux --logic=$logic "$formula" | grep "Status:")
    echo "$logic: $result"
done
```

### JSON Processing

```bash
# Extract model count
tableaux --format=json "p -> q" | jq '.models | length'

# Extract specific model
tableaux --format=json --models "p & q" | jq '.models[0]'

# Check satisfiability
tableaux --format=json "p & ~p" | jq '.satisfiable'
```

### File Processing

```bash
# Process formulas from file
while IFS= read -r formula; do
    echo "Testing: $formula"
    tableaux "$formula"
    echo "---"
done < formulas.txt
```

## Best Practices

### Formula Writing

1. **Always use quotes** around formulas to prevent shell interpretation
2. **Use parentheses** for clarity in complex formulas
3. **Test incrementally** - build complex formulas step by step
4. **Use meaningful atom names** for readability

### Logic System Selection

1. **Start with classical** for standard logical reasoning
2. **Use weak Kleene** for three-valued scenarios
3. **Use wKrQ** for epistemic reasoning with four values
4. **Use FDE** for paraconsistent reasoning

### Performance

1. **Use `--stats`** to monitor performance on complex formulas
2. **Break down** very complex formulas into parts
3. **Use batch mode** for multiple formula testing
4. **Consider JSON output** for programmatic processing

### Debugging

1. **Use `--debug`** to understand tableau construction
2. **Use `--models`** to see all satisfying assignments
3. **Test with different signs** to understand formula behavior
4. **Compare across logic systems** to understand differences

The CLI provides a powerful interface for exploring automated reasoning across multiple logic systems, with both interactive and batch processing capabilities suitable for research, education, and practical applications.