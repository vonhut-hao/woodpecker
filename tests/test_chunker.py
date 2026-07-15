"""Tests cho core/chunker.py."""
import pytest
from woodpecker.core.chunker import estimate_tokens, split_by_sentences, chunk_with_overlap
from woodpecker.config import VN_TOKEN_MULTIPLIER


class TestEstimateTokens:
    def test_basic_estimation(self):
        # 3 words -> 3 * 1.3 = 3
        text = "Một hai ba"
        assert estimate_tokens(text) == int(3 * VN_TOKEN_MULTIPLIER)


class TestSplitBySentences:
    def test_basic_split(self):
        text = "Câu một. Câu hai! Câu ba?"
        sentences = split_by_sentences(text)
        assert len(sentences) == 3
        assert sentences[0] == "Câu một."
        assert sentences[1] == "Câu hai!"
        assert sentences[2] == "Câu ba?"

    def test_no_split(self):
        text = "Không có dấu kết thúc câu"
        assert split_by_sentences(text) == [text]


class TestChunkWithOverlap:
    def test_no_sentences(self):
        assert chunk_with_overlap([]) == []

    def test_single_chunk(self):
        sentences = ["Câu một.", "Câu hai."]
        # max_tokens lớn nên tất cả nằm trong 1 chunk
        chunks = chunk_with_overlap(sentences, max_tokens=100)
        assert len(chunks) == 1
        assert chunks[0] == "Câu một. Câu hai."

    def test_overlap(self):
        # 5 câu, mỗi câu ~ 4 tokens (3 words * 1.3)
        sentences = ["Câu một.", "Câu hai.", "Câu ba.", "Câu bốn.", "Câu năm."]
        # max_tokens = 5 -> mỗi chunk chỉ chứa khoảng 2 câu
        # overlap_ratio = 0.5 (50%) -> giữ lại 1 câu
        chunks = chunk_with_overlap(sentences, max_tokens=5, overlap_ratio=0.5)
        
        assert len(chunks) > 1
        # Chunk đầu tiên có thể là "Câu một. Câu hai."
        # Chunk thứ 2 phải bắt đầu bằng "Câu hai." (do overlap 50% của 2 câu)
        assert "Câu hai." in chunks[1]
