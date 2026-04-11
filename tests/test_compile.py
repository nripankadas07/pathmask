"""Tests for pathmask.compile_pattern() and CompiledPattern."""
import pytest
from pathmask import compile_pattern, PathmaskError


class TestCompilePattern:
    """Test compile_pattern() function."""

    def test_compile_basic(self) -> None:
        compiled = compile_pattern("*.txt")
        assert compiled.match("file.txt") is True
        assert compiled.match("file.md") is False

    def test_compile_reuse(self) -> None:
        compiled = compile_pattern("*.txt")
        assert compiled.match("a.txt") is True
        assert compiled.match("b.txt") is True
        assert compiled.match("c.txt") is True

    def test_compile_complex_pattern(self) -> None:
        compiled = compile_pattern("src/**/*.{js,ts}")
        assert compiled.match("src/main.js") is True
        assert compiled.match("src/utils/helper.ts") is True
        assert compiled.match("src/utils/core/base.js") is True
        assert compiled.match("src/readme.md") is False

    def test_compile_with_question(self) -> None:
        compiled = compile_pattern("file?.txt")
        assert compiled.match("file1.txt") is True
        assert compiled.match("fileA.txt") is True
        assert compiled.match("file.txt") is False

    def test_compile_with_char_class(self) -> None:
        compiled = compile_pattern("file[0-9].txt")
        assert compiled.match("file1.txt") is True
        assert compiled.match("fileA.txt") is False

    def test_compile_with_negation(self) -> None:
        compiled = compile_pattern("!*.md")
        assert compiled.match("file.txt") is True
        assert compiled.match("file.md") is False

    def test_compile_invalid_pattern(self) -> None:
        with pytest.raises(PathmaskError):
            compile_pattern("file.{txt")

    def test_compile_empty_pattern(self) -> None:
        compiled = compile_pattern("")
        assert compiled.match("") is True
        assert compiled.match("file.txt") is False

    def test_compile_double_asterisk(self) -> None:
        compiled = compile_pattern("**/test/**/*.js")
        assert compiled.match("src/test/spec.js") is True
        assert compiled.match("a/b/test/c/d.js") is True
        assert compiled.match("test/file.js") is True

    def test_compile_multiple_calls_same_pattern(self) -> None:
        c1 = compile_pattern("*.txt")
        c2 = compile_pattern("*.txt")
        # Should produce equivalent results
        assert c1.match("file.txt") == c2.match("file.txt")
        assert c1.match("file.md") == c2.match("file.md")

    def test_compile_performance_benefit(self) -> None:
        # Compiled pattern should be efficient for many matches
        compiled = compile_pattern("*.py")
        paths = [f"file{i}.py" for i in range(1000)]
        results = [compiled.match(p) for p in paths]
        assert all(results)

    def test_compile_nested_braces(self) -> None:
        compiled = compile_pattern("{a,{b,c}}")
        assert compiled.match("a") is True
        assert compiled.match("b") is True
        assert compiled.match("c") is True
        assert compiled.match("d") is False

    def test_compile_escaped_chars(self) -> None:
        compiled = compile_pattern(r"\*.txt")
        assert compiled.match("*.txt") is True
        assert compiled.match("file.txt") is False


class TestCompiledPatternEdgeCases:
    """Test edge cases for CompiledPattern."""

    def test_compiled_empty_alternation(self) -> None:
        compiled = compile_pattern("file{.txt,}")
        assert compiled.match("file.txt") is True
        assert compiled.match("file") is True

    def test_compiled_wildcard_only(self) -> None:
        compiled = compile_pattern("*")
        assert compiled.match("file.txt") is True
        assert compiled.match("anything") is True

    def test_compiled_special_chars_in_path(self) -> None:
        compiled = compile_pattern("file-name_v*.txt")
        assert compiled.match("file-name_v1.txt") is True
        assert compiled.match("file-name_v2.5.txt") is True

    def test_compiled_trailing_slash(self) -> None:
        compiled = compile_pattern("dir/")
        assert compiled.match("dir/") is True
        assert compiled.match("dir") is False

    def test_compiled_brace_with_wildcards(self) -> None:
        compiled = compile_pattern("*.{js,ts}")
        assert compiled.match("index.js") is True
        assert compiled.match("app.ts") is True
        assert compiled.match("readme.md") is False
