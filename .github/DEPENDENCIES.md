# Dependency Summary

This document summarizes the core runtime and test dependencies for the Woodpecker Semantic Chunking project.

## Core Processing & Validation
- **`pydantic`**: Mandatory for strictly typing the API contract and JSON serialization (`ChunkMetadata`, `SemanticChunk`).
- **`tiktoken`**: Used for fast, OpenAI-compatible token counting. Essential for the "Fixed-Size with Overlap" chunking strategy.

## NLP & Semantic Splitting
- **`nltk` / `spacy`**: Employed for advanced, accurate sentence tokenization to detect semantic boundaries.
- **`sentence-transformers`**: Used to generate vector embeddings of sentences.
- **`numpy` & `scikit-learn`**: Powers efficient matrix operations and cosine similarity calculations between sentence embeddings to determine semantic drop-offs.

## Testing
- **`pytest`**: The designated testing framework for ensuring reliability of chunking strategies, overlapping logic, and data validation rules.
