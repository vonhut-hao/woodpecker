import pytest
from src.chunker import SemanticChunker

def test_fixed_size_chunk_with_overlap():
    chunker = SemanticChunker()
    # A simple repeating string to generate sufficient tokens
    text = "This is a simple test sentence to verify that the chunking logic works as expected. " * 10
    
    # We expect some overlap
    max_tokens = 20
    overlap = 5
    chunks = chunker.fixed_size_chunk_with_overlap(
        text=text, 
        source_file="test.md", 
        max_tokens=max_tokens, 
        overlap_tokens=overlap
    )
    
    assert len(chunks) > 1, "Should create multiple chunks"
    for chunk in chunks:
        assert chunk.token_count <= max_tokens, f"Chunk exceeded max tokens: {chunk.token_count}"
        assert chunk.metadata.strategy_used == "Fixed-Size with Overlap"
        assert chunk.metadata.source_file == "test.md"

def test_overlap_validation():
    chunker = SemanticChunker()
    with pytest.raises(ValueError):
        chunker.fixed_size_chunk_with_overlap("test", "test.md", max_tokens=10, overlap_tokens=10)
