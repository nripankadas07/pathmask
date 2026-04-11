# pathmask

Glob-style path matcher with negation and brace expansion. Zero dependencies.

## Installation

```bash
pip install pathmask
```

Or from source:

```bash
git clone https://github.com/nripankadas07/pathmask.git
cd pathmask
pip install -e .
```

## Quick Start

```python
from pathmask import match, filter_paths

# Simple matching
match("src/main.js", "src/*.js")  # True
match("src/utils/helper.js", "src/*.js")  # False

# Recursive matching
match("src/utils/helper.js", "src/**/*.js")  # True

# Filter paths
paths = ["a.txt", "b.md", "c.txt"]
filter_paths(paths, "*.txt")  # ["a.txt", "c.txt"]

# Negation
filter_paths(paths, "!*.md")  # ["a.txt", "c.txt"]
```

## Features

- `*` â Matches any characters except `/`
- `**` â Matches any characters including `/` (recursive)
- `?` â Matches any single character except `/`
- `[abc]` â Character class
- `[!abc]` â Negated character class
- `{a,b,c}` â Brace expansion
- `!pattern` â Negation (returns non-matching paths)

## Usage Examples

### Basic Matching

```python
from pathmask import match

# Literal matching
match("file.txt", "file.txt")  # True

# Single character
match("file.txt", "file?.txt")  # False
match("file1.txt", "file?.txt")  # True

# Wildcard
match("main.js", "*.js")  # True
match("src/main.js", "*.js")  # False (doesn't cross /)
```

### Recursive Matching

```python
# ** matches across directory boundaries
match("src/utils/helper.js", "src/**/*.js")  # True
match("a/b/c/d/file.txt", "a/**/file.txt")  # True
match("file.txt", "**/*.txt")  # True
```

### Character Classes

```python
match("file1.txt", "file[0-9].txt")  # True
match("fileA.txt", "file[0-9].txt")  # False
match("fileA.txt", "file[!0-9].txt")  # True
```

### Brace Expansion

```python
match("style.css", "*.{js,css,html}")  # True
match("main.js", "*.{js,css,html}")  # True
match("app.py", "*.{js,css,html}")  # False

# Nested braces
match("a", "{a,{b,c}}")  # True
match("c", "{a,{b,c}}")  # True
```

### Filtering Paths

```python
from pathmask import filter_paths

paths = [
    "src/main.js",
    "src/utils/helper.js",
    "test/spec.js",
    "README.md"
]

# Match all JS files
filter_paths(paths, "**/*.js")
# ["src/main.js", "src/utils/helper.js", "test/spec.js"]

# Exclude markdown files
filter_paths(paths, "!*.md")
# ["src/main.js", "src/utils/helper.js", "test/spec.js"]
```

### Compiled Patterns

For repeated use, compile patterns for better performance:

```python
from pathmask import compile_pattern

pattern = compile_pattern("src/**/*.{js,ts}")

pattern.match("src/main.js")  # True
pattern.match("src/utils/helper.ts")  # True
pattern.match("test/spec.js")  # False
```

## API Reference

### `match(path: str, pattern: str) -> bool`

Test if a path matches a glob pattern.

**Parameters:**
- `path` (str): File path to match
- `pattern` (str): Glob pattern

**Returns:**
- bool: True if path matches pattern

**Raises:**
- `PathmaskError`: If pattern is invalid

**Example:**
```python
match("file.txt", "*.txt")  # True
```

### `filter_paths(paths: Iterable[str], pattern: str) -> list[str]`

Filter paths matching a glob pattern.

**Parameters:**
- `paths` (Iterable[str]): Iterable of file paths
- `pattern` (str): Glob pattern (supports negation with `!`)

**Returns:**
- list[str]: List of matching paths in original order

**Raises:**
- `PathmaskError`: If pattern is invalid

**Example:**
```python
filter_paths(["a.txt", "b.md", "c.txt"], "*.txt")
# ["a.txt", "c.txt"]
```

### `compile_pattern(pattern: str) -> CompiledPattern`

Compile a glob pattern for repeated matching.

**Parameters:**
- `pattern` (str): Glob pattern

**Returns:**
- CompiledPattern: Compiled pattern object

**Raises:**
- `PathmaskError`: If pattern is invalid

**Example:**
```python
compiled = compile_pattern("src/**/*.js")
compiled.match("src/main.js")  # True
```

### `CompiledPattern.match(path: str) -> bool`

Test if a path matches a compiled pattern.

**Parameters:**
- `path` (str): File path to match

**Returns:**
- bool: True if path matches pattern

**Example:**
```python
pattern = compile_pattern("*.txt")
pattern.match("file.txt")  # True
```

### `PathmaskError`

Exception raised for invalid patterns.

**Example:**
```python
from pathmask import PathmaskError

try:
    match("file.txt", "file.{txt")
except PathmaskError as e:
    print(f"Invalid pattern: {e}")
```

## Running Tests

Install dev dependencies:

```bash
pip install pytest pytest-cov
```

Run tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=src/pathmask --cov-report=html tests/
```

View coverage report:

```bash
open htmlcov/index.html
```

## License

MIT License - see [LICENSE](LICENSE) file for details
