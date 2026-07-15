"""Tests cho pipeline/processor.py.

Kiểm tra:
- group_by_section: nhóm block theo section_hierarchy
- woodpecker_process: pipeline end-to-end
"""
import pytest

from woodpecker.pipeline.processor import group_by_section, woodpecker_process


class TestGroupBySection:
    """Test hàm group_by_section."""

    def test_empty_input(self):
        """Danh sách rỗng → trả về rỗng."""
        assert group_by_section([]) == []

    def test_single_block(self):
        """Một block → một nhóm chứa 1 block."""
        blocks = [{"section_hierarchy": {"1": "Chương I"}, "text": "abc"}]
        result = group_by_section(blocks)
        assert len(result) == 1
        assert len(result[0]) == 1

    def test_same_section(self):
        """Hai block cùng section → một nhóm."""
        blocks = [
            {"section_hierarchy": {"1": "Chương I", "2": "Điều 2"}, "text": "a"},
            {"section_hierarchy": {"1": "Chương I", "2": "Điều 2"}, "text": "b"},
        ]
        result = group_by_section(blocks)
        assert len(result) == 1
        assert len(result[0]) == 2

    def test_different_sections(self):
        """Ba block, 2 section khác nhau → 2 nhóm."""
        blocks = [
            {"section_hierarchy": {"1": "Chương I", "2": "Điều 2"}, "text": "a"},
            {"section_hierarchy": {"1": "Chương I", "2": "Điều 2"}, "text": "b"},
            {"section_hierarchy": {"1": "Chương I", "2": "Điều 3"}, "text": "c"},
        ]
        result = group_by_section(blocks)
        assert len(result) == 2
        assert len(result[0]) == 2  # Điều 2: 2 blocks
        assert len(result[1]) == 1  # Điều 3: 1 block

    def test_alternating_sections(self):
        """Sections xen kẽ → mỗi block là 1 nhóm riêng."""
        blocks = [
            {"section_hierarchy": {"1": "A"}, "text": "a"},
            {"section_hierarchy": {"1": "B"}, "text": "b"},
            {"section_hierarchy": {"1": "A"}, "text": "c"},
        ]
        result = group_by_section(blocks)
        assert len(result) == 3


class TestWoodpeckerProcess:
    """Test pipeline end-to-end."""

    def test_basic_processing(self):
        """Test luồng xử lý cơ bản với 2 text blocks."""
        blocks = [
            {
                "text": "Sinh viên phải chấp hành nội quy của Trường.",
                "block_type": "Text",
                "section_hierarchy": {"1": "Chương I", "2": "Điều 2"},
            },
            {
                "text": "Mỗi SV được cấp mã số SV và thẻ SV.",
                "block_type": "Text",
                "section_hierarchy": {"1": "Chương I", "2": "Điều 2"},
            },
        ]
        result = woodpecker_process(blocks, source_file="test.pdf", min_tokens=5)

        assert len(result) >= 1
        chunk = result[0]
        assert "chunk_id" in chunk
        assert "text" in chunk
        assert "token_count" in chunk
        assert chunk["metadata"]["source_file"] == "test.pdf"
        assert chunk["metadata"]["chunk_index"] == 0
        assert "Chương I" in chunk["metadata"]["header_context"]

    def test_skip_section_header(self):
        """SectionHeader không được ghép vào text output."""
        blocks = [
            {
                "text": "Điều 2. Sinh viên",
                "block_type": "SectionHeader",
                "section_hierarchy": {"1": "Chương I", "2": "Điều 2"},
            },
            {
                "text": "Sinh viên phải chấp hành nội quy. Mỗi SV được cấp mã số.",
                "block_type": "Text",
                "section_hierarchy": {"1": "Chương I", "2": "Điều 2"},
            },
        ]
        result = woodpecker_process(blocks, source_file="test.pdf", min_tokens=5)

        assert len(result) >= 1
        # Text của SectionHeader ("Điều 2. Sinh viên") không được nằm trong output text
        for chunk in result:
            assert "Điều 2. Sinh viên" not in chunk["text"]

    def test_skip_short_section(self):
        """Section quá ngắn (< MIN_TOKENS) bị bỏ qua."""
        blocks = [
            {
                "text": "Ngắn.",
                "block_type": "Text",
                "section_hierarchy": {"1": "A"},
            },
        ]
        result = woodpecker_process(blocks, source_file="test.pdf", min_tokens=100)
        assert len(result) == 0

    def test_chunk_index_sequential(self):
        """chunk_index phải tăng dần liên tục."""
        blocks = [
            {
                "text": "Đoạn văn đầu tiên dài đủ để vượt ngưỡng min_tokens. " * 5,
                "block_type": "Text",
                "section_hierarchy": {"1": "A"},
            },
            {
                "text": "Đoạn văn thứ hai cũng dài đủ để vượt ngưỡng min_tokens. " * 5,
                "block_type": "Text",
                "section_hierarchy": {"1": "B"},
            },
        ]
        result = woodpecker_process(blocks, source_file="test.pdf", min_tokens=5)

        indices = [c["metadata"]["chunk_index"] for c in result]
        assert indices == list(range(len(result)))
