"""Tests for pathmask.match() function."""
import pytest
from pathmask import match, PathmaskError


class TestBasicMatching:
    """Test literal and simple wildcard matching."""

    def test_exact_match(self) -> None:
        assert match("hello.txt", "hello.txt") is True

    def test_exact_mismatch(self) -> None:
        assert match("hello.txt", "world.txt") is False

    def test_empty_pattern_empty_path(self) -> None:
        assert match("", "") is True

    def test_empty_pattern_non_empty_path(self) -> None:
        assert match("file.txt", "") is False

    def test_empty_path_non_empty_pattern(self) -> None:
        assert match("", "*.txt") is False


class TestSingleAsterisk:
    """Test single asterisk (*) wildcard."""

    def test_single_asterisk_basic(self) -> None:
        assert match("file.txt", "*.txt") is True

    def test_single_asterisk_no_match(self) -> None:
        assert match("file.md", "*.txt") is False

    def test_single_asterisk_matches_empty(self) -> None:
        assert match(".txt", "*.txt") is True

    def test_asterisk_at_start(self) -> None:
        assert match("file.txt", "*file.txt") is True

    def test_asterisk_at_end(self) -> None:
        assert match("file.txt", "file.*") is True

    def test_asterisk_in_middle(self) -> None:
        assert match("file.txt", "fi*xt") is True

    def test_asterisk_does_not_cross_slash(self) -> None:
        assert match("dir/file.txt", "*.txt") is False

    def test_asterisk_matches_within_directory(self) -> None:
        assert match("dir/file.txt", "dir/*.txt") is True


class TestDoubleAsterisk:
    """Test double asterisk (**) recursive wildcard."""

    def test_double_asterisk_single_level(self) -> None:
        assert match("file.txt", "**.txt") is True

    def test_double_asterisk_multiple_levels(self) -> None:
        assert match("a/b/c/file.txt", "**/file.txt") is True

    def test_double_asterisk_in_middle(self) -> None:
        assert match("a/b/c/d.txt", "a/**/d.txt") is True

    def test_double_asterisk_at_start(self) -> None:
        assert match("a/b/c.txt", "**/c.txt") is True

    def test_double_asterisk_at_end(self) -> None:
        assert match("a/b/c/file.txt", "a/**") is True

    def test_double_asterisk_alone(self) -> None:
        assert match("a/b/c/d/e/f.txt", "**") is True

    def test_double_asterisk_no_match(self) -> None:
        assert match("a/b/file.txt", "a/**/file.md") is False


class TestQuestion:
    """Test single character wildcard (?)."""

    def test_question_basic(self) -> None:
        assert match("file.txt", "file.tx?") is True

    def test_question_no_match(self) -> None:
        assert match("file.txt", "file.t??x") is False

    def test_question_multiple(self) -> None:
        assert match("abc", "???") is True

    def test_question_does_not_cross_slash(self) -> None:
        assert match("dir/file.txt", "?/?") is False

    def test_question_matches_empty_fails(self) -> None:
        assert match("file.t", "file.tx?") is False


class TestCharacterClasses:
    """Test character class patterns [abc] and [!abc]."""

    def test_char_class_match(self) -> None:
        assert match("file1.txt", "file[0-9].txt") is True

    def test_char_class_no_match(self) -> None:
        assert match("fileA.txt", "file[0-9].txt") is False

    def test_char_class_multiple_options(self) -> None:
        assert match("fileA.txt", "file[ABC].txt") is True

    def test_char_class_negation(self) -> None:
        assert match("file1.txt", "file[!A-Z].txt") is True

    def test_char_class_negation_fail(self) -> None:
        assert match("fileA.txt", "file[!A-Z].txt") is False

    def test_char_class_does_not_cross_slash(self) -> None:
        assert match("dir/file.txt", "[abc]/file.txt") is False

    def test_char_class_range(self) -> None:
        assert match("file5.txt", "file[1-9].txt") is True


class TestBraceExpansion:
    """Test brace expansion {a,b,c}."""

    def test_brace_simple(self) -> None:
        assert match("file.txt", "file.{txt,md}") is True

    def test_brace_no_match(self) -> None:
        assert match("file.js", "file.{txt,md}") is False

    def test_brace_multiple(self) -> None:
        assert match("a.txt", "{a,b}.{txt,md}") is True

    def test_brace_empty_alternative(self) -> None:
        # Empty alternative should be allowed
        assert match("file.", "file.{txt,}") is True

    def test_brace_nested(self) -> None:
        # Nested braces: {a,{b,c}} -> a, b, c
        assert match("a", "{a,{b,c}}") is True
        assert match("b", "{a,{b,c}}") is True

    def test_brace_with_wildcards(self) -> None:
        assert match("file/txt", "{*,src}/*") is True


class TestPatternErrors:
    """Test error handling for invalid patterns."""

    def test_unmatched_opening_brace(self) -> None:
        with pytest.raises(PathmaskError):
            match("file.txt", "file.{txt")

    def test_unmatched_closing_brace(self) -> None:
        with pytest.raises(PathmaskError):
            match("file.txt", "file.txt}")


class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_trailing_slash_path(self) -> None:
        assert match("dir/", "dir/") is True

    def test_trailing_slash_mismatch(self) -> None:
        assert match("dir/", "dir") is False

    def test_multiple_consecutive_asterisks(self) -> None:
        # *** and **** should still work as wildcards
        assert match("file.txt", "***") is True

    def test_dot_files(self) -> None:
        assert match(".gitignore", ".*") is True

    def test_deeply_nested_path(self) -> None:
        assert match("a/b/c/d/e/f/g/h/i/j.txt", "a/**/j.txt") is True

    def test_special_characters_in_path(self) -> None:
        assert match("file-name_v2.txt", "file-name_v2.txt") is True

    def test_escaped_asterisk(self) -> None:
        # Backslash escapes special characters
        assert match("*.txt", r"\*.txt") is True

    def test_escaped_question(self) -> None:
        assert match("?.txt", r"\?.txt") is True


class TestAdjacentDoubleAsterisk:
    """Test adjacent ** segments."""

    def test_adjacent_double_asterisk(self) -> None:
        assert match("a/b/c/d/e.txt", "a/**/b/**/e.txt") is True

    def test_adjacent_no_match(self) -> None:
        # ** can match zero or more dirs, so a/b/c/e.txt won't match a/**/d/**/e.txt
        assert match("a/b/c/d/f.txt", "a/**/b/**/e.txt") is False
