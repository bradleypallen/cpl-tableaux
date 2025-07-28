"""
Entry point for running wKrQ as a module: python -m wkrq
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())