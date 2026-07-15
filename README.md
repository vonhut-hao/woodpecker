<div align="center">

<img width="20%" height="20%" alt="WOODPECKER" src="https://github.com/user-attachments/assets/4ea4fd34-1cf6-48b8-9e3c-d158219356f5" />

**A Context-Aware Semantic Document Chunking Engine for Retrieval-Augmented Generation**

[![GitHub Stars](https://img.shields.io/github/stars/vonhut-hao/woodpecker?style=flat-square&color=DAA520)](https://github.com/vonhut-hao/woodpecker/stargazers)
[![GitHub Watchers](https://img.shields.io/github/watchers/vonhut-hao/woodpecker?style=flat-square)](https://github.com/vonhut-hao/woodpecker/watchers)
[![GitHub Forks](https://img.shields.io/github/forks/vonhut-hao/woodpecker?style=flat-square)](https://github.com/vonhut-hao/woodpecker/network)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)

</div>

## What Is Woodpecker?

**Woodpecker** is a specialized semantic text chunking engine explicitly designed to prepare documents for robust Retrieval-Augmented Generation (RAG) pipelines. Just like a woodpecker precisely extracting what it needs from a massive tree, this tool intelligently parses structured document blocks, groups them by context, and splits them along natural semantic boundaries (sentences).

Traditional RAG pipelines often suffer from **silent data truncation** or **semantic dilution** when blindly applying fixed-size cuts to documents. Woodpecker eliminates these issues by rigorously adhering to the embedding token limits (e.g., `< 256` tokens for `all-MiniLM-L6-v2`) while preserving the narrative flow using a configurable overlapping strategy.

> **Input:** A JSON array of structured document blocks (e.g., extracted from PDFs via Marker or Qwen2-VL).
> 
> **Output:** Clean, semantically intact, plain-text chunks enriched with contextual metadata, ready to be embedded into your Vector Database.

## Why Woodpecker?

Woodpecker serves as the vital bridging microservice between raw document parsers and downstream AI databases (Vector DBs / Graph DBs). It solves critical architectural problems in RAG systems:

- **Semantic Dilution Prevention:** Groups document blocks by their logical Section Hierarchy (e.g., *Chapter 1 > Article 2*) so chunks never mix disparate topics.
- **Strict Embedding Compliance:** Ensures every generated chunk stays below a strict hard token limit (e.g., 200 tokens) to prevent catastrophic silent truncation by embedding models.
- **Advanced Fallback Chunking:** Employs smart lookbehind regex (`(?<=[.!?])\s+`) for natural sentence splitting, and automatically falls back to sub-semantic boundaries (`;` or `,`) or fixed-size cutting if a single sentence is excessively long (a common issue in legal documents).
- **Context Preservation:** Implements a sliding window overlap (default 20%) at the sentence level, ensuring ideas naturally flow across vector boundaries.

## System Architecture

Below is an illustration of how Woodpecker fits into a broader data ingestion pipeline:

```text
[Raw Documents]          [WOODPECKER ENGINE]                [RAG Pipeline]
      │                           │                               │
PDF / DOCX / Image ──→ ┌─────────────────────┐ ──→ ┌─────────────────────────────┐
      │                │ 1. Context Grouping │     │ 1. Text Normalization       │
  [Parsers]            │ 2. Clean HTML/Tags  │     │ 2. BM25 Lexical Indexing    │
(e.g., Marker)   ───→  │ 3. Semantic Split   │ ──→ │ 3. Embedding (MiniLM-L6-v2) │
                       │ 4. Chunk & Overlap  │     │ 4. Hybrid Search            │
                       └─────────────────────┘     │ 5. Cross-Encoder Reranking  │
                                                   └─────────────────────────────┘
```

## Workflow

1. **Ingest Structured Blocks:** Accepts JSON arrays of blocks containing text, block types, and hierarchical metadata.
2. **Context Grouping:** Aggregates blocks that share the exact same section hierarchy to prevent splitting continuous thoughts.
3. **Text Cleaning:** Strips leftover HTML tags, normalizes whitespaces, and removes noisy non-semantic characters.
4. **Semantic Splitting & Fallback:** Slices text at sentence boundaries. If a sentence exceeds the max token limit, it safely triggers a fallback split strategy (sub-semantic or fixed-size) to guarantee model compliance.
5. **Overlapped Chunking:** Groups sentences into chunks under the token limit, retaining the last 20% of sentences to overlap with the next chunk.
6. **Export:** Yields a robust JSON array of chunks containing UUIDs, plain text, token counts, and structural breadcrumb metadata.

## Quick Start

### Prerequisites

| Tool | Version | Description | Check Installation |
|------|---------|-------------|-------------------|
| **Python** | ≥ 3.10 | Backend runtime | `python --version` |
| **uv / pip** | Latest | Python package manager | `uv --version` |

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/vonhut-hao/woodpecker.git
cd woodpecker

# Initialize environment and install dependencies
uv init
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### 2. Usage via CLI

Woodpecker provides a robust Command Line Interface out of the box:

```bash
# View configuration info
python cli.py info

# Process a Marker output JSON file
python cli.py process \
    --input data/sample_marker_chunks.json \
    --output output_chunks.json \
    --source-file "document_name.pdf"

# Override default configurations
python cli.py process \
    --input data/sample_marker_chunks.json \
    --output output_chunks.json \
    --max-tokens 150 \
    --overlap 0.25
```

### 3. Usage via Python API

Woodpecker is designed to be easily integrated into Python microservices (e.g., FastAPI):

```python
from woodpecker.adapters.marker_adapter import marker_chunks_to_input
from woodpecker.pipeline.processor import woodpecker_process

# 1. Parse your structured data into Woodpecker InputBlocks
input_blocks = marker_chunks_to_input("data/marker_output.json")

# 2. Run the chunking pipeline
chunks = woodpecker_process(
    input_blocks, 
    source_file="legal_document.pdf",
    max_tokens=200,
    overlap_ratio=0.20
)

# 3. Output is ready for your Vector Database!
print(chunks[0])
# {
#     "chunk_id": "a1b2c3d4-...",
#     "text": "Extracted plain text ready for embedding...",
#     "token_count": 145,
#     "metadata": {
#         "source_file": "legal_document.pdf",
#         "chunk_index": 0,
#         "header_context": "Chapter 1 > Article 2"
#     }
# }
```

## Running Tests

Woodpecker uses `pytest` for rigorous unit and integration testing.

```bash
# Run the entire test suite
uv run pytest tests/ -v
```

## Join the Conversation

If you're interested in AI, RAG optimization, or want to contribute to the project, feel free to reach out!

- Email: vonhuthao.dev@gmail.com
- GitHub: [@vonhut-hao](https://github.com/vonhut-hao)
