import json
from typing import List, Optional
import tiktoken
from src.schema import SemanticChunk, ChunkMetadata

class SemanticChunker:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the SemanticChunker.
        
        Args:
            model_name (str): The name of the model to use for tokenization.
                              Defaults to "gpt-3.5-turbo" which uses the 'cl100k_base' encoding.
        """
        self.model_name = model_name
        try:
            self.tokenizer = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base if model is unknown
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a given text string."""
        return len(self.tokenizer.encode(text))

    def fixed_size_chunk_with_overlap(
        self, 
        text: str, 
        source_file: str, 
        max_tokens: int = 500, 
        overlap_tokens: int = 100
    ) -> List[SemanticChunk]:
        """
        Split text by a hard token limit with an exact token overlap.
        
        Args:
            text (str): The input text to be chunked.
            source_file (str): The source file name for metadata.
            max_tokens (int): The maximum number of tokens per chunk.
            overlap_tokens (int): The number of overlapping tokens between consecutive chunks.
            
        Returns:
            List[SemanticChunk]: A list of chunk objects.
        """
        if overlap_tokens >= max_tokens:
            raise ValueError("overlap_tokens must be strictly less than max_tokens.")

        tokens = self.tokenizer.encode(text)
        chunks = []
        chunk_index = 0
        
        i = 0
        while i < len(tokens):
            end_i = min(i + max_tokens, len(tokens))
            chunk_tokens = tokens[i:end_i]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            token_count = len(chunk_tokens)
            
            metadata = ChunkMetadata(
                source_file=source_file,
                chunk_index=chunk_index,
                strategy_used="Fixed-Size with Overlap"
            )
            
            chunk = SemanticChunk(
                text=chunk_text,
                token_count=token_count,
                metadata=metadata
            )
            chunks.append(chunk)
            chunk_index += 1
            
            # Break if we've reached the end of the tokens
            if end_i == len(tokens):
                break
                
            # Move the index forward, accounting for overlap
            step = max_tokens - overlap_tokens
            i += step
            
        return chunks

    def export_to_json(self, chunks: List[SemanticChunk], filepath: str) -> None:
        """
        Export a list of chunks to a JSON file.
        
        Args:
            chunks (List[SemanticChunk]): The list of chunks to export.
            filepath (str): The path to the output JSON file.
        """
        chunks_dict = [chunk.model_dump() for chunk in chunks]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chunks_dict, f, indent=4, ensure_ascii=False)
            
    def export_to_json_string(self, chunks: List[SemanticChunk]) -> str:
        """
        Export a list of chunks to a JSON string.
        
        Args:
            chunks (List[SemanticChunk]): The list of chunks to export.
            
        Returns:
            str: The JSON string representation of the chunks.
        """
        chunks_dict = [chunk.model_dump() for chunk in chunks]
        return json.dumps(chunks_dict, indent=4, ensure_ascii=False)
