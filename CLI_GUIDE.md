# CLI Usage Guide: Tableau Logic System

**Version**: 3.0 (Consolidated Architecture)  
**Last Updated**: July 2025  
**License**: MIT  

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Commands](#basic-commands)
3. [Interactive Mode](#interactive-mode)
4. [Logic Systems](#logic-systems)
5. [Output Formats](#output-formats)
6. [Batch Processing](#batch-processing)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [Examples and Use Cases](#examples-and-use-cases)

## Quick Start

### Installation Check

```bash
# Verify the system is working
python cli.py "p | ~p"
# Expected output: SATISFIABLE with 2 models
```

### Your First Commands

```bash
# Test a simple tautology
python cli.py "p | ~p"

# Test a contradiction
python cli.py "p & ~p"

# Show all satisfying models
python cli.py --models "p | q"

# Use three-valued logic
python cli.py --wk3 "p & ~p"

# Start interactive mode
python cli.py
```

## Basic Commands

### Command Line Syntax

```bash
python cli.py [OPTIONS] [FORMULA]
```

### Essential Options

| Option | Description | Example |
|--------|-------------|---------|
| `--models` | Show all satisfying models | `python cli.py --models "p \| q"` |
| `--wk3` | Use three-valued (WK3) logic | `python cli.py --wk3 "p & ~p"` |
| `--stats` | Show performance statistics | `python cli.py --stats "complex_formula"` |
| `--help` | Display help message | `python cli.py --help` |

### Formula Syntax

| Logic Symbol | CLI Syntax | Example |
|--------------|------------|---------|
| Atom | `p`, `q`, `r` | `p` |
| Negation (¬) | `~` | `~p` |
| Conjunction (∧) | `&` | `p & q` |
| Disjunction (∨) | `\|` | `p \| q` |
| Implication (→) | `->` | `p -> q` |
| Parentheses | `()` | `(p & q) \| r` |

**Note**: Use quotes around formulas to prevent shell interpretation of special characters.

### Basic Examples

```bash
# Simple satisfiability tests
python cli.py "p"                      # Always satisfiable
python cli.py "p & q"                  # Satisfiable
python cli.py "p & ~p"                 # Contradiction (unsatisfiable)
python cli.py "p | ~p"                 # Tautology (always satisfiable)

# Complex formulas
python cli.py "(p -> q) & p & ~q"      # Modus ponens contradiction
python cli.py "(p | q) & (~p | r)"     # Horn clause
python cli.py "((p -> q) -> p) -> p"   # Peirce's law
```

## Interactive Mode

### Starting Interactive Mode

```bash
python cli.py
```

### Interactive Commands

Once in interactive mode, you can use these commands:

| Command | Description | Example |
|---------|-------------|---------|
| `test <formula>` | Test satisfiability | `test p & q` |
| `models <formula>` | Show all models | `models p \| q` |
| `wk3 <formula>` | Switch to WK3 logic | `wk3 p & ~p` |
| `classical <formula>` | Switch to classical logic | `classical p \| ~p` |
| `stats` | Show last operation statistics | `stats` |
| `examples` | Show example formulas | `examples` |
| `help` | Show help message | `help` |
| `quit` | Exit interactive mode | `quit` |

### Interactive Session Tutorial

```bash
$ python cli.py
Welcome to the Tableau Logic System!
Type 'help' for commands, 'quit' to exit.

tableau> help
Available commands:
  test <formula>        - Test satisfiability
  models <formula>      - Show all models
  wk3 <formula>         - Use WK3 logic
  classical <formula>   - Use classical logic
  stats                 - Show performance statistics
  examples              - Show example formulas
  help                  - Show this help
  quit                  - Exit

tableau> examples
Example formulas to try:
  
  Basic Formulas:
    p                    - Simple atom
    p & q                - Conjunction
    p | q                - Disjunction
    ~p                   - Negation
    p -> q               - Implication
  
  Tautologies (always true):
    p | ~p               - Law of excluded middle
    (p -> q) | (q -> p)  - One direction must hold
    ((p -> q) -> p) -> p - Peirce's law
  
  Contradictions (always false):
    p & ~p               - Contradiction
    (p -> q) & p & ~q    - Modus ponens failure
  
  Interesting Cases:
    (p | q) & (~p | r)   - Satisfiable with constraints
    (p & q) -> p         - Valid implication
    p -> (q -> p)        - Exportation theorem

tableau> test p & q
Formula: p ∧ q
Logic: Classical
Result: SATISFIABLE
Found 1 model(s)

tableau> models p | q
Formula: p ∨ q
Logic: Classical
Result: SATISFIABLE
Found 3 model(s):
  Model 1: {p=TRUE, q=FALSE}
  Model 2: {p=FALSE, q=TRUE}
  Model 3: {p=TRUE, q=TRUE}

tableau> test p & ~p
Formula: p ∧ ¬p
Logic: Classical
Result: UNSATISFIABLE
No satisfying models exist.

tableau> wk3 p & ~p
Switching to WK3 (three-valued) logic...
Formula: p ∧ ¬p
Logic: WK3
Result: SATISFIABLE
Found 1 model(s):
  Model 1: {p=UNDEFINED}
Explanation: In WK3 logic, contradictions can be satisfied when atoms are undefined.

tableau> classical p | ~p
Switching to classical logic...
Formula: p ∨ ¬p
Logic: Classical
Result: SATISFIABLE
Found 2 model(s):
  Model 1: {p=FALSE}
  Model 2: {p=TRUE}
This is a tautology - it's true under all possible assignments.

tableau> stats
Last Operation Statistics:
  Formula: p ∨ ¬p
  Logic System: Classical
  Result: SATISFIABLE
  Models Found: 2
  Tableau Construction Time: 0.0012 seconds
  Rule Applications: 3
  Total Branches Created: 2
  Maximum Branch Size: 3

tableau> quit
Goodbye!
```

## Logic Systems

### Classical Logic (Default)

Classical two-valued logic with truth values `TRUE` and `FALSE`.

```bash
# Explicit classical logic (default)
python cli.py --classical "p | ~p"

# These are equivalent
python cli.py "p | ~p"
python cli.py --classical "p | ~p"
```

**Characteristics:**
- Law of excluded middle: `p | ~p` is always true
- Non-contradiction: `p & ~p` is always false
- Complete: every formula is either satisfiable or unsatisfiable

### Three-Valued Logic (WK3)

Weak Kleene three-valued logic with truth values `TRUE`, `FALSE`, and `UNDEFINED`.

```bash
# Use WK3 logic
python cli.py --wk3 "p & ~p"
python cli.py --wk3 --models "p | ~p"
```

**Key Differences from Classical:**

```bash
# Classical contradiction - unsatisfiable
python cli.py "p & ~p"
# Output: UNSATISFIABLE

# WK3 contradiction - satisfiable when p is undefined
python cli.py --wk3 "p & ~p"
# Output: SATISFIABLE, Model: {p=UNDEFINED}

# Classical tautology - 2 models (p=true, p=false)
python cli.py --models "p | ~p"
# Output: 2 models

# WK3 non-tautology - 3 models including undefined
python cli.py --wk3 --models "p | ~p"
# Output: 3 models (includes p=UNDEFINED where formula is UNDEFINED)
```

### Logic System Comparison

```bash
# Compare same formula in both systems
echo "Comparing p & ~p in classical vs WK3:"
python cli.py "p & ~p"
python cli.py --wk3 "p & ~p"

echo "Comparing p | ~p in classical vs WK3:"
python cli.py --models "p | ~p"
python cli.py --wk3 --models "p | ~p"
```

## Output Formats

### Default Output Format

```bash
python cli.py "p | q"
# Output:
# Formula: p ∨ q
# Logic: Classical
# Result: SATISFIABLE
# Found 3 model(s)
```

### Detailed Output with Models

```bash
python cli.py --models "p | q"
# Output:
# Formula: p ∨ q
# Logic: Classical
# Result: SATISFIABLE
# Found 3 model(s):
#   Model 1: {p=TRUE, q=FALSE}
#   Model 2: {p=FALSE, q=TRUE}
#   Model 3: {p=TRUE, q=TRUE}
```

### Statistics Output

```bash
python cli.py --stats "complex_formula"
# Output includes:
# - Construction time
# - Rule applications
# - Branch count
# - Memory usage estimates
```

### JSON Output

```bash
python cli.py --format=json "p | q"
# Output:
# {
#   "formula": "p ∨ q",
#   "logic": "classical",
#   "satisfiable": true,
#   "models": [
#     {"p": true, "q": false},
#     {"p": false, "q": true},
#     {"p": true, "q": true}
#   ],
#   "statistics": {
#     "construction_time": 0.0015,
#     "rule_applications": 5,
#     "total_branches": 3
#   }
# }
```

### CSV Output

```bash
python cli.py --format=csv --models "p | q"
# Output:
# formula,logic,satisfiable,model_count,p,q
# "p ∨ q",classical,true,3,true,false
# "p ∨ q",classical,true,3,false,true
# "p ∨ q",classical,true,3,true,true
```

## Batch Processing

### Processing Multiple Formulas

```bash
# From command line arguments
python cli.py --batch "p & q" "p | q" "p -> q"

# From standard input
echo -e "p & q\np | q\np -> q" | python cli.py --batch

# From file
python cli.py --file=formulas.txt
```

### Formula File Format

Create `formulas.txt`:
```
# Tableau test formulas
# Lines starting with # are comments

# Basic formulas
p
p & q
p | q
~p

# Tautologies  
p | ~p
(p -> q) | (~p -> ~q)

# Contradictions
p & ~p
(p -> q) & p & ~q

# Complex formulas
(p | q) & (~p | r) & (~q | r)
((p -> q) -> p) -> p
```

Then run:
```bash
python cli.py --file=formulas.txt --models
```

### Batch Output Formats

```bash
# Generate CSV report for spreadsheet analysis
python cli.py --file=formulas.txt --format=csv > results.csv

# Generate JSON for programmatic processing
python cli.py --file=formulas.txt --format=json > results.json

# Compare classical vs WK3 for all formulas
python cli.py --file=formulas.txt --compare-logics
```

## Advanced Features

### Performance Analysis

```bash
# Show detailed performance statistics
python cli.py --stats --debug "complex_formula"

# Benchmark mode - multiple runs
python cli.py --benchmark=10 "formula"

# Memory usage analysis
python cli.py --memory-profile "large_formula"
```

### Debugging Features

```bash
# Show tableau construction steps
python cli.py --debug "p & q"

# Show all intermediate steps
python cli.py --verbose --debug "(p | q) & r"

# Export tableau tree visualization
python cli.py --export-tree=tree.dot "formula"
```

### Timeout and Limits

```bash
# Set timeout for complex formulas (in seconds)
python cli.py --timeout=5 "very_complex_formula"

# Limit maximum number of models shown
python cli.py --max-models=10 "formula_with_many_models"

# Limit maximum tableau size
python cli.py --max-branches=1000 "formula"
```

### Formula Validation

```bash
# Check formula syntax without solving
python cli.py --validate-only "p & q | r"

# Show parsed formula structure
python cli.py --show-parse-tree "((p -> q) & p) -> q"

# Convert between different syntax formats
python cli.py --convert-syntax=latex "p -> q"
```

## Troubleshooting

### Common Issues

**1. Shell Character Interpretation**

```bash
# Wrong - shell interprets | and &
python cli.py p | q & r

# Right - use quotes
python cli.py "p | q & r"
```

**2. Operator Precedence**

```bash
# Ambiguous - may not parse as expected
python cli.py "p & q | r"

# Clear - use parentheses
python cli.py "(p & q) | r"
python cli.py "p & (q | r)"
```

**3. Large Formula Timeout**

```bash
# If formula takes too long
python cli.py --timeout=10 "complex_formula"

# Or check if it's actually unsatisfiable
python cli.py --debug "complex_formula"
```

### Error Messages

**Syntax Errors:**
```bash
$ python cli.py "p && q"
Error: Unknown operator '&&'. Use '&' for conjunction.

$ python cli.py "p or q"  
Error: Unknown operator 'or'. Use '|' for disjunction.
```

**Timeout Errors:**
```bash
$ python cli.py --timeout=1 "very_complex_formula"
Error: Tableau construction timed out after 1 second.
Suggestion: Try increasing timeout or simplifying formula.
```

**Memory Errors:**
```bash
$ python cli.py "formula_with_exponential_blowup"
Warning: Large number of branches created (>10000).
This may indicate exponential blowup.
```

### Performance Tips

1. **Use parentheses** to make operator precedence explicit
2. **Start simple** - test subformulas before combining them
3. **Set timeouts** for complex formulas to avoid hanging
4. **Use --debug** to understand why formulas are slow
5. **Consider WK3 logic** for formulas that are unsatisfiable classically

## Examples and Use Cases

### Educational Examples

```bash
# Teaching propositional logic
python cli.py --models "p -> q"        # Show when implication is true
python cli.py "~(p & q)"               # De Morgan's law: equivalent to ~p | ~q
python cli.py "(~p | ~q)"              # Verify equivalence

# Exploring tautologies
python cli.py "((p -> q) & (q -> r)) -> (p -> r)"  # Transitivity
python cli.py "(p & (p -> q)) -> q"                # Modus ponens
python cli.py "((p -> q) -> p) -> p"               # Peirce's law
```

### Logic Puzzle Solving

```bash
# Solve "Knights and Knaves" style puzzles
# A says "B is a knight", B says "A is a knave"
# Let p = "A is knight", q = "B is knight" 
python cli.py "(p -> q) & (q -> ~p)"

# Einstein's riddle constraints (simplified)
python cli.py "(house1 -> red) & (house2 -> blue) & ~(house1 & house2)"
```

### SAT Solver Applications

```bash
# Graph coloring (3-coloring of triangle)
# Vertices: a, b, c; Colors: r, g, b
python cli.py --models "(ar | ag | ab) & (br | bg | bb) & (cr | cg | cb) & ~(ar & br) & ~(ar & cr) & ~(br & cr)"

# Scheduling constraints
python cli.py "task1_monday | task1_tuesday) & (task2_monday | task2_tuesday) & ~(task1_monday & task2_monday)"
```

### Research Applications

```bash
# Test non-classical logic properties
python cli.py --wk3 --models "p -> (q -> p)"      # Test axiom in WK3
python cli.py --wk3 "((p -> q) -> p) -> p"        # Peirce's law in WK3

# Compare logic systems
python cli.py --compare-logics "p | ~p"           # Excluded middle
python cli.py --compare-logics "p & ~p"           # Contradiction
```

### Verification and Testing

```bash
# Verify logical equivalences
python cli.py --models "~(p & q)"                 # De Morgan 1
python cli.py --models "~p | ~q"                  # De Morgan 1 equivalent

# Test inference rules
python cli.py "(p -> q) & p & ~q"                 # Should be unsatisfiable (modus ponens)
python cli.py "(p | q) & ~p & ~q"                 # Should be unsatisfiable (disjunctive syllogism)
```

### Automation and Scripting

```bash
#!/bin/bash
# Test all tautologies in a list
tautologies=(
    "p | ~p"
    "(p -> q) | (q -> p)"
    "((p -> q) -> p) -> p"
    "(p & (p -> q)) -> q"
)

for formula in "${tautologies[@]}"; do
    echo "Testing: $formula"
    if python cli.py "$formula" | grep -q "SATISFIABLE"; then
        echo "  ✓ Tautology (satisfiable)"
    else
        echo "  ✗ Not a tautology"
    fi
done
```

### Integration with Other Tools

```bash
# Generate input for other solvers
python cli.py --format=dimacs "cnf_formula" > formula.cnf

# Convert to different formats
python cli.py --format=latex "p -> q" > formula.tex

# Pipe to analysis tools
python cli.py --format=json "formula" | jq '.models | length'
```

This comprehensive CLI guide provides everything needed to effectively use the tableau system from the command line, whether for learning, research, or practical problem-solving applications.