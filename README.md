<div align="center">

<img width="20%" height="20%" alt="WOODPECKER-w" src="https://github.com/user-attachments/assets/3e0ed2d4-1985-4a62-b4d2-ed3996238237" />

**Động cơ phân mảnh tài liệu theo ngữ nghĩa, khai phá mọi tài liệu cho RAG**
</br>
<em>A Context-Aware Semantic Document Chunking Engine for Retrieval-Augmented Generation</em>

[![GitHub Stars](https://img.shields.io/github/stars/vonhut-hao/Woodpecker?style=flat-square&color=DAA520)](https://github.com/vonhut-hao/Woodpecker/stargazers)
[![GitHub Watchers](https://img.shields.io/github/watchers/vonhut-hao/Woodpecker?style=flat-square)](https://github.com/vonhut-hao/Woodpecker/watchers)
[![GitHub Forks](https://img.shields.io/github/forks/vonhut-hao/Woodpecker?style=flat-square)](https://github.com/vonhut-hao/Woodpecker/network)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)

[English](./README.md) | [Tiếng Việt](./README-VI.md)

</div>

## ⚡ Overview

**Woodpecker** is a specialized semantic document chunking engine designed for Retrieval-Augmented Generation (RAG) pipelines. Just like a woodpecker precisely extracting what it needs from a massive tree, this tool intelligently parses, splits, and overlaps complex documents (PDFs, DOCX, Markdown) to extract highly relevant, context-preserving text chunks. 

By avoiding blind, fixed-size cuts and instead focusing on structural and semantic boundaries, Woodpecker ensures your LLMs receive the complete context they need without the noise.

> You only need to: Feed it a raw, complex document (e.g., an environmental research paper or product manual).</br>
> Woodpecker will return: Clean, semantically intact, and smartly overlapped chunks ready to be embedded into your Vector Database.

### Our Vision

Woodpecker aims to be the most robust data ingestion bridge for AI systems. We solve the "lost in the middle" and "broken context" problems in traditional RAG systems by offering:
- **Smart Chunking:** Structural (Markdown-based) and Semantic (Embedding-based) splitting.
- **Context Preservation:** Configurable chunk overlapping (e.g., 20%) to ensure concepts flow naturally across vector boundaries.
- **Seamless Integration:** Designed to easily plug into larger e-commerce or advisory AI architectures.

## 📸 Screenshots

<div align="center">
<table>
<tr>
<td><img src="./static/image/Screenshot/chunking_demo1.png" alt="Before: Raw Document [Trống - Cần cập nhật]" width="100%"/></td>
<td><img src="./static/image/Screenshot/chunking_demo2.png" alt="After: Semantic Chunks [Trống - Cần cập nhật]" width="100%"/></td>
</tr>
</table>
</div>

## 🔄 Workflow

1. **Document Ingestion**: Read raw files (PDF/DOCX) and utilize parsers to output clean Markdown.
2. **Text Processing**: Clean up special characters, normalize punctuation, and handle tokenization.
3. **Semantic Splitting**: 
   - Identify structural boundaries (Headers, Paragraphs).
   - Apply cosine similarity checks for semantic shifts.
4. **Chunk Overlap**: Stitch the end of `Chunk A` with the beginning of `Chunk B` to preserve narrative flow.
5. **Vector Ready**: Output perfectly sized JSON/Text objects ready for your embedding model.

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Description | Check Installation |
|------|---------|-------------|-------------------|
| **Python** | ≥3.10 | Backend runtime | `python --version` |
| **uv / pip** | Latest | Python package manager | `pip --version` |

### 1. Configure Environment Variables

```bash
# Copy the example configuration file
cp .env.example .env

# Edit the .env file and fill in required API keys (e.g., for Embedding models)
```

### 2. Install Dependencies

```bash
# Clone the repository
git clone [https://github.com/vonhut-hao/Woodpecker.git](https://github.com/vonhut-hao/Woodpecker.git)
cd Woodpecker

# Install dependencies
pip install -r requirements.txt
```

### 3. Usage Example

```bash
from woodpecker import SemanticChunker

# Initialize the chunker with a 20% overlap strategy
chunker = SemanticChunker(strategy="semantic", overlap_ratio=0.2)

# Process a document
chunks = chunker.process_file("data/eco_lifestyle_guide.md")

print(f"Extracted {len(chunks)} semantic chunks successfully!")
```

## 📬 Join the Conversation

If you're interested in AI, RAG optimization, or want to contribute to the project, feel free to reach out!

Email: vonhuthao.dev@gmail.com

GitHub: @vonhut-hao

## 📈 Project Statistics

<a href="https://www.star-history.com/?repos=vonhut-hao%2Fwoodpecker&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=vonhut-hao/woodpecker&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=vonhut-hao/woodpecker&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=vonhut-hao/woodpecker&type=date&legend=top-left" />
 </picture>
</a>
