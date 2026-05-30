# Copilot Instructions

## Project Map
- Root structure:
  - `src/`: Core Python modules (Chunker logic, Schema definitions).
  - `tests/`: Unit and integration tests (Pytest).
  - `data/`: Sample inputs/outputs and temporary artifacts.

## Core Architecture
- **Goal:** Woodpecker is a lightweight, highly efficient semantic document chunking engine designed for RAG (Retrieval-Augmented Generation) pipelines. It acts as an intermediate bridge between the extraction system (e.g., MinerU) and Vector DBs.
- **Workflow:** 
  1. **Ingestion & Preprocessing**: Receive structural Markdown input, normalize punctuation, remove invalid characters.
  2. **Structural & Semantic Analysis**: Track markdown headers (`header_context`). Split sentences and calculate cosine similarity to find semantic boundaries.
  3. **Chunking & Overlap**: Apply splitting logic (Fixed-size, Structural, Semantic) with token overlap to maintain context between chunks.
  4. **Packaging & Export**: Export the results to a strict JSON schema array format.
- **Key Modules**:
  - `src/schema.py`: Defines API contracts (`SemanticChunk`, `ChunkMetadata`). MUST use `pydantic.BaseModel`.
  - `src/chunker.py`: Contains the `SemanticChunker` class and core splitting strategies.

## Coding Conventions & Constraints
- **NO Orchestration Frameworks**: DO NOT use LangChain, LlamaIndex, or similar heavy LLM frameworks for the core chunking algorithms. All algorithms must be built from scratch.
- **Type Hinting**: Strict Python type hinting is mandatory for all functions and methods.
- **Documentation**: Professional docstrings must be provided for all classes and functions.
- **Optimization**: Code should be heavily optimized for multi-threading and efficient memory usage across diverse hardware architectures (CPU/RAM agnostic), specifically for string/array processing.
