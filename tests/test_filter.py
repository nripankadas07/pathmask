"""Tests for pathmask.filter_paths() function."""
import pytest
from pathmask import filter_paths


class TestFilterPaths:
    """Test filter_paths() function."""

    def test_filter_basic(self) -> None:
        paths = ["file.txt", "file.md", "file.js"]
        result = filter_paths(paths, "*.txt")
        assert result == ["file.txt"]

    def test_filter_multiple_matches(self) -> None:
        paths = ["a.txt", "b.txt", "c.md", "d.txt"]
        result = filter_paths(paths, "*.txt")
        assert result == ["a.txt", "b.txt", "d.txt"]

    def test_filter_no_matches(self) -> None:
        paths = ["a.md", "b.md", "c.md"]
        result = filter_paths(paths, "*.txt")
        assert result == []

    def test_filter_empty_list(self) -> None:
        result = filter_paths([], "*.txt")
        assert result == []

    def test_filter_preserves_order(self) -> None:
        paths = ["z.txt", "a.txt", "m.txt"]
        result = filter_paths(paths, "*.txt")
        assert result == ["z.txt", "a.txt", "m.txt"]

    def test_filter_with_negation(self) -> None:
        paths = ["a.txt", "b.md", "c.txt"]
        result = filter_paths(paths, "!*.md")
        assert result == ["a.txt", "c.txt"]

    def test_filter_with_multiple_patterns(self) -> None:
        # Single pattern, not multiple
        paths = ["a.txt", "b.txt", "c.md"]
        result = filter_paths(paths, "*.txt")
        assert result == ["a.txt", "b.txt"]

    def test_filter_directories(self) -> None:
        paths = ["src/main.js", "src/utils.js", "test/spec.js", "README.md"]
        result = filter_paths(paths, "src/*")
        assert result == ["src/main.js", "src/utils.js"]

    def test_filter_recursive(self) -> None:
        paths = [
            "src/main.js",
            "src/utils/helper.js",
            "src/utils/core/base.js",
            "test/spec.js",
        ]
        result = filter_paths(paths, "src/**/*.js")
        assert result == [
            "src/main.js",
            "src/utils/helper.js",
            "src/utils/core/base.js",
        ]

    def test_filter_brace_expansion(self) -> None:
        paths = ["a.js", "b.txt", "c.md", "d.py"]
        result = filter_paths(paths, "*.{js,txt}")
        assert result == ["a.js", "b.txt"]

    def test_filter_negation_removes_matches(self) -> None:
        paths = ["file1.txt", "file2.js", "file3.txt"]
        result = filter_paths(paths, "!*.txt")
        assert result == ["file2.js"]

    def test_filter_iterable_generator(self) -> None:
        def gen() -> None:
            yield "a.txt"
            yield "b.md"
            yield "c.txt"

        result = filter_paths(gen(), "*.txt")
        assert result == ["a.txt", "c.txt"]

    def test_filter_empty_pattern(self) -> None:
        paths = [""]
        result = filter_paths(paths, "")
        assert result == [""]

    def test_filter_with_dot_files(self) -> None:
        paths = [".gitignore", "file.txt", ".env", "README.md"]
        result = filter_paths(paths, ".*")
        assert result == [".gitignore", ".env"]


class TestFilterPathsEdgeCases:
    """Test edge cases for filter_paths."""

    def test_filter_single_element(self) -> None:
        result = filter_paths(["file.txt"], "*.txt")
        assert result == ["file.txt"]

    def test_filter_duplicate_paths(self) -> None:
        paths = ["file.txt", "file.txt", "file.md"]
        result = filter_paths(paths, "*.txt")
        assert result == ["file.txt", "file.txt"]

    def test_filter_special_characters(self) -> None:
        paths = ["file-name_v2.txt", "file-name_v1.txt", "other.md"]
        result = filter_paths(paths, "file-name_*.txt")
        assert result == ["file-name_v2.txt", "file-name_v1.txt"]

    def test_filter_deeply_nested(self) -> None:
        paths = [
            "a/b/c/d/e/f/g.txt",
            "a/b/c/d/e/f/h.txt",
            "a/b/c.txt",
        ]
        result = filter_paths(paths, "a/**/f/*.txt")
        assert result == ["a/b/c/d/e/f/g.txt", "a/b/c/d/e/f/h.txt"]
