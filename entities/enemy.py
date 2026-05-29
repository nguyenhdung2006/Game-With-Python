"""Compatibility import for the old single-enemy module path.

The real implementation now lives in enemy archetype files. This alias keeps
older imports working while the project moves to scalable enemy classes.
"""

from entities.basic_enemy import BasicEnemy as Enemy

__all__ = ["Enemy"]
