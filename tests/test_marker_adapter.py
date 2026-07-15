"""Tests cho adapters/marker_adapter.py.

Kiểm tra:
- strip_html: loại bỏ HTML tags
- marker_chunks_to_input: chuyển đổi Marker chunks → InputBlock
"""
import json
import os
import pytest
import tempfile

from woodpecker.adapters.marker_adapter import (
    strip_html,
    marker_chunks_to_input,
    _extract_page_index,
)


class TestStripHtml:
    """Test hàm strip_html."""

    def test_basic_paragraph(self):
        """Loại bỏ thẻ <p>."""
        assert strip_html("<p>Sinh viên chính quy</p>") == "Sinh viên chính quy"

    def test_nested_tags(self):
        """Loại bỏ thẻ lồng nhau."""
        html = "<p>Sinh viên <b>chính quy</b> của <i>Trường</i></p>"
        result = strip_html(html)
        assert result == "Sinh viên chính quy của Trường"

    def test_table_tags(self):
        """Loại bỏ thẻ bảng, giữ nội dung."""
        html = "<table><tr><td>4 năm</td><td>8 năm</td></tr></table>"
        result = strip_html(html)
        assert "4 năm" in result
        assert "8 năm" in result
        # Không được dính nhau
        assert "4 năm8 năm" not in result

    def test_heading_tags(self):
        """Loại bỏ thẻ heading."""
        assert strip_html("<h2>QUYẾT ĐỊNH</h2>") == "QUYẾT ĐỊNH"

    def test_empty_string(self):
        """Chuỗi rỗng → rỗng."""
        assert strip_html("") == ""

    def test_no_html(self):
        """Text thuần → giữ nguyên."""
        assert strip_html("Không có HTML") == "Không có HTML"


class TestExtractPageIndex:
    """Test hàm _extract_page_index."""

    def test_standard_format(self):
        assert _extract_page_index("/page/3/Page/0/Text/5") == 3

    def test_page_zero(self):
        assert _extract_page_index("/page/0/SectionHeader/0") == 0

    def test_invalid_format(self):
        assert _extract_page_index("invalid_id") is None


class TestMarkerChunksToInput:
    """Test hàm marker_chunks_to_input."""

    def _write_temp_json(self, data: dict) -> str:
        """Helper: ghi dữ liệu JSON vào file tạm."""
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return path

    def test_basic_conversion(self):
        """Chuyển đổi 1 Text block."""
        data = {
            "blocks": [
                {
                    "id": "/page/2/Text/3",
                    "block_type": "Text",
                    "html": "<p>Sinh viên chính quy.</p>",
                    "section_hierarchy": {"1": "Chương I", "2": "Điều 2"},
                    "images": {},
                }
            ],
            "page_info": {},
        }
        path = self._write_temp_json(data)
        try:
            result = marker_chunks_to_input(path)
            assert len(result) == 1
            assert result[0]["text"] == "Sinh viên chính quy."
            assert result[0]["block_type"] == "Text"
            assert result[0]["section_hierarchy"] == {"1": "Chương I", "2": "Điều 2"}
            assert result[0]["page_index"] == 2
        finally:
            os.unlink(path)

    def test_filter_picture(self):
        """Picture block bị lọc bỏ."""
        data = {
            "blocks": [
                {"id": "/page/0/Picture/0", "block_type": "Picture", "html": "<img src='...'/>", "section_hierarchy": {}, "images": {}},
                {"id": "/page/0/Text/1", "block_type": "Text", "html": "<p>Nội dung</p>", "section_hierarchy": {}, "images": {}},
            ],
            "page_info": {},
        }
        path = self._write_temp_json(data)
        try:
            result = marker_chunks_to_input(path)
            assert len(result) == 1
            assert result[0]["block_type"] == "Text"
        finally:
            os.unlink(path)

    def test_filter_empty_html(self):
        """Block có html rỗng bị bỏ qua."""
        data = {
            "blocks": [
                {"id": "/page/0/Text/0", "block_type": "Text", "html": "", "section_hierarchy": {}, "images": {}},
            ],
            "page_info": {},
        }
        path = self._write_temp_json(data)
        try:
            result = marker_chunks_to_input(path)
            assert len(result) == 0
        finally:
            os.unlink(path)

    def test_with_sample_data(self):
        """Test với file sample thật."""
        sample_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "sample_marker_chunks.json"
        )
        if os.path.exists(sample_path):
            result = marker_chunks_to_input(sample_path)
            # Sample có 10 blocks, 1 PageHeader bị lọc → 9 blocks
            # Nhưng có SectionHeader rỗng có thể bị lọc nữa
            assert len(result) >= 5
            # Kiểm tra không có PageHeader trong output
            for block in result:
                assert block["block_type"] != "PageHeader"
