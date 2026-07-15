"""Tests cho core/cleaner.py."""
import pytest
from woodpecker.core.cleaner import strip_html, clean_text


class TestStripHtml:
    def test_basic_tags(self):
        assert strip_html("<p>Hello</p>") == "Hello"
        assert strip_html("<b>Bold</b>") == "Bold"

    def test_nested_tags(self):
        assert strip_html("<div><p>Hello <b>World</b></p></div>") == "Hello World"

    def test_table(self):
        assert strip_html("<table><tr><td>A</td><td>B</td></tr></table>") == "A B"


class TestCleanText:
    def test_remove_special_chars(self):
        assert clean_text("Hello @#World!") == "Hello World!"
        assert clean_text("Sinh viên (CQ)") == "Sinh viên (CQ)"

    def test_keep_vietnamese(self):
        text = "Sinh viên đại học Cần Thơ."
        assert clean_text(text) == text

    def test_extra_spaces(self):
        assert clean_text("Hello   World  ") == "Hello World"
