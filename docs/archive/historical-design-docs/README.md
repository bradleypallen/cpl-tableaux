# Historical Design Documents

This folder contains design and analysis documents from before the July 2025 architectural consolidation. These documents are preserved for historical reference but **do not reflect the current implementation**.

## Current Architecture

The tableau system was consolidated into a unified architecture with a single core module (`tableau_core.py`). For current documentation, see:

- **ARCHITECTURE.md** - Current system architecture
- **API_REFERENCE.md** - Current API documentation
- **BUILDING_GUIDE.md** - How to extend the current system
- **README.md** - Current usage and overview

## Historical Documents

### Design Plans (Now Implemented)
- **WEAK_KLEENE_PLAN.md** - Original design plan for WK3 implementation (now complete)
- **IMPLEMENTATION_PLAN_WKRQ.md** - Original design plan for wKrQ logic (now complete)
- **INTERFACE_CHANGES_WKRQ.md** - Planned interface changes for a multi-file architecture (superseded)

### Analysis Documents
- **TECHNICAL_ANALYSIS.md** - Pre-consolidation analysis of the implementation (references old file structure)

## Why These Were Archived

During the consolidation:
1. Multiple files (`tableau.py`, `wk3_tableau.py`, `formula.py`, etc.) were merged into `tableau_core.py`
2. Convenience functions (`wk3_satisfiable`, `wk3_models`) were eliminated
3. 16 test files were consolidated into `test_comprehensive.py` and others
4. The architecture was simplified while maintaining all functionality

These documents reference the old multi-file architecture and design decisions that have been superseded by the unified implementation.

## Note

If you're looking to understand or extend the current system, please refer to the current documentation in the main directory, not these historical documents.