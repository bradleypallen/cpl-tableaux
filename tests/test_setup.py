# test_setup.py
from tableaux import Atom, classical_signed_tableau, T

# Create a simple formula
p = Atom("p")
engine = classical_signed_tableau(T(p))
result = engine.build()

print(f"Setup working: {result}")  # Should print: Setup working: True