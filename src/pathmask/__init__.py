"""pathmask: Glob-style path matcher with negation and brace expansion."""
from pathmask.core import (
    CompiledPattern,
    PathmaskError,
    compile_pattern,
    filter_paths,
    match,
)

__all__ = [
    "match",
    "filter_paths",
    "compile_pattern",
    "CompiledPattern",
    "PathmaskError",
]

__version__ = "0.1.0"
