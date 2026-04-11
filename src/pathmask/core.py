"""Core pathmask pattern matching implementation."""
import re
from typing import Iterable


class PathmaskError(Exception):
    """Exception raised for invalid patterns."""

    pass


class CompiledPattern:
    """Pre-compiled pattern for efficient matching."""

    def __init__(
        self, pattern: str, regex: str, is_negation: bool = False
    ) -> None:
        """Initialize compiled pattern.

        Args:
            pattern: Original pattern string
            regex: Compiled regex pattern
            is_negation: Whether pattern is negated

        Raises:
            PathmaskError: If regex compilation fails
        """
        self.pattern = pattern
        self.is_negation = is_negation
        try:
            self._regex = re.compile(f"^{regex}$")
        except re.error as e:
            raise PathmaskError(f"Invalid pattern: {pattern}") from e

    def match(self, path: str) -> bool:
        """Test if path matches compiled pattern.

        Args:
            path: Path to match

        Returns:
            True if path matches pattern (respecting negation)
        """
        matched = bool(self._regex.match(path))
        return not matched if self.is_negation else matched


def _validate_pattern(pattern: str) -> None:
    """Validate pattern for syntax errors.

    Args:
        pattern: Pattern to validate

    Raises:
        PathmaskError: If pattern has syntax errors
    """
    brace_depth = 0
    escape = False
    for char in pattern:
        if escape:
            escape = False
            continue
        if char == "\\":
            escape = True
            continue
        if char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
            if brace_depth < 0:
                raise PathmaskError(
                    f"Unmatched closing brace in pattern: {pattern}"
                )
    if brace_depth != 0:
        raise PathmaskError(f"Unmatched opening brace in pattern: {pattern}")


def _parse_brace_group(
    pattern: str, start: int
) -> tuple[list[str], int]:
    """Parse a single brace group from pattern.

    Args:
        pattern: Pattern to parse
        start: Starting index after opening brace

    Returns:
        Tuple of (alternatives list, end index)
    """
    parts: list[str] = []
    current_alt = ""
    depth = 1
    i = start

    while i < len(pattern) and depth > 0:
        if pattern[i] == "\\":
            current_alt += pattern[i : min(i + 2, len(pattern))]
            i += 2 if i + 1 < len(pattern) else 1
        elif pattern[i] == "{":
            depth += 1
            current_alt += pattern[i]
            i += 1
        elif pattern[i] == "}":
            depth -= 1
            if depth == 0:
                parts.append(current_alt)
                break
            current_alt += pattern[i]
            i += 1
        elif pattern[i] == "," and depth == 1:
            parts.append(current_alt)
            current_alt = ""
            i += 1
        else:
            current_alt += pattern[i]
            i += 1

    return parts, i + 1


def _expand_braces(pattern: str) -> list[str]:
    """Expand brace patterns into multiple patterns.

    Args:
        pattern: Pattern with brace expansion

    Returns:
        List of expanded patterns

    Raises:
        PathmaskError: If braces are unmatched
    """
    _validate_pattern(pattern)

    if "{" not in pattern:
        return [pattern]

    i = 0
    prefix = ""

    while i < len(pattern):
        char = pattern[i]

        if char == "\\":
            prefix += char
            if i + 1 < len(pattern):
                prefix += pattern[i + 1]
                i += 2
            else:
                i += 1
            continue

        if char == "{":
            parts, end_idx = _parse_brace_group(pattern, i + 1)
            result = []
            for part in parts:
                result.extend(_expand_braces(prefix + part + pattern[end_idx:]))
            return result

        prefix += char
        i += 1

    return [prefix]


def _parse_char_class(pattern: str, start: int) -> tuple[str, int]:
    """Parse a character class from pattern.

    Args:
        pattern: Pattern to parse
        start: Starting index after opening bracket

    Returns:
        Tuple of (regex fragment, end index)
    """
    j = start
    if j < len(pattern) and pattern[j] == "!":
        j += 1
    if j < len(pattern) and pattern[j] == "]":
        j += 1
    while j < len(pattern) and pattern[j] != "]":
        j += 1

    if j >= len(pattern):
        return re.escape("["), start

    class_content = pattern[start : j]
    if class_content.startswith("!"):
        regex = f"[^{class_content[1:]}]"
    else:
        regex = f"[{class_content}]"
    return regex, j + 1


def _pattern_to_regex(pattern: str) -> str:
    """Convert glob pattern to regex.

    Args:
        pattern: Glob pattern

    Returns:
        Regex pattern string
    """
    regex = ""
    i = 0

    while i < len(pattern):
        char = pattern[i]

        if char == "\\":
            if i + 1 < len(pattern):
                regex += re.escape(pattern[i + 1])
                i += 2
            else:
                regex += re.escape(char)
                i += 1
        elif char == "*":
            if i + 1 < len(pattern) and pattern[i + 1] == "*":
                if i + 2 < len(pattern) and pattern[i + 2] == "/":
                    regex += "(?:.*/|)"
                    i += 3
                else:
                    regex += ".*"
                    i += 2
            else:
                regex += "[^/]*"
                i += 1
        elif char == "?":
            regex += "[^/]"
            i += 1
        elif char == "[":
            class_regex, end_idx = _parse_char_class(pattern, i + 1)
            regex += class_regex
            i = end_idx
        else:
            regex += re.escape(char)
            i += 1

    return regex


def compile_pattern(pattern: str) -> CompiledPattern:
    """Compile a glob pattern for repeated matching.

    Args:
        pattern: Glob pattern with optional negation

    Returns:
        CompiledPattern object

    Raises:
        PathmaskError: If pattern is invalid
    """
    _validate_pattern(pattern)

    is_negation = pattern.startswith("!")
    if is_negation:
        pattern = pattern[1:]

    expanded = _expand_braces(pattern)
    if len(expanded) == 1:
        regex = _pattern_to_regex(expanded[0])
    else:
        regexes = [_pattern_to_regex(p) for p in expanded]
        regex = "|".join(f"(?:{r})" for r in regexes)

    original = pattern if not is_negation else f"!{pattern}"
    return CompiledPattern(original, regex, is_negation)


def match(path: str, pattern: str) -> bool:
    """Test if a path matches a glob pattern.

    Args:
        path: File path to match
        pattern: Glob pattern (supports *, **, ?, [abc], {a,b}, !)

    Returns:
        True if path matches pattern

    Raises:
        PathmaskError: If pattern is invalid
    """
    compiled = compile_pattern(pattern)
    return compiled.match(path)


def filter_paths(
    paths: Iterable[str], pattern: str
) -> list[str]:
    """Filter paths matching a glob pattern.

    Args:
        paths: Iterable of file paths
        pattern: Glob pattern (supports negation with !)

    Returns:
        List of matching paths in original order

    Raises:
        PathmaskError: If pattern is invalid
    """
    compiled = compile_pattern(pattern)
    return [p for p in paths if compiled.match(p)]
