# 🪶 Woodpecker — Semantic Chunking Engine cho RAG

**Đề tài:** Niên luận cơ sở — Semantic Chunking cho RAG  
**Phiên bản:** 0.1.0

---

## Tổng quan

Woodpecker là module Python nhận đầu vào JSON có cấu trúc (từ Document Parser như Marker) và xuất ra plain-text chunks sạch — sẵn sàng đưa vào RAG pipeline theo kiến trúc [Boot.dev](https://boot.dev).

```
PDF → [Marker] → JSON → [Woodpecker] → Chunks → [Boot.dev Pipeline]
                                                    ├── Embedding (Ch.4)
                                                    ├── BM25 Index (Ch.2-3)
                                                    ├── Hybrid Search (Ch.7)
                                                    ├── Reranking (Ch.9)
                                                    └── RAG Generation (Ch.11)
```

## Cài đặt

```bash
# Tạo project và môi trường ảo
uv init
uv venv
.venv\Scripts\activate   # Windows

# Cài dependencies
uv pip install -e ".[dev]"
```

## Sử dụng

### CLI

```bash
# Xem thông tin cấu hình
python cli.py info

# Chạy pipeline chunking
python cli.py process \
    --input data/sample_marker_chunks.json \
    --output output/chunks.json \
    --source-file "QD3266.pdf"

# Tùy chỉnh tham số
python cli.py process \
    --input data/sample_marker_chunks.json \
    --output output/chunks.json \
    --source-file "QD3266.pdf" \
    --max-tokens 150 \
    --overlap 0.25
```

### Python API

```python
from woodpecker.adapters.marker_adapter import marker_chunks_to_input
from woodpecker.pipeline.processor import woodpecker_process

# Đọc Marker chunks JSON
blocks = marker_chunks_to_input("data/sample_marker_chunks.json")

# Chạy pipeline
chunks = woodpecker_process(blocks, source_file="QD3266.pdf")

# Mỗi chunk có format:
# {
#     "chunk_id": "uuid",
#     "text": "plain text sạch",
#     "token_count": 150,
#     "metadata": {
#         "source_file": "QD3266.pdf",
#         "chunk_index": 0,
#         "header_context": "Chương I > Điều 2"
#     }
# }
```

## Cấu trúc thư mục

```
semantic-chunking_4RAG/
├── src/woodpecker/
│   ├── config.py              # Hằng số cấu hình
│   ├── models/schemas.py      # Pydantic Input/Output Schema
│   ├── core/
│   │   ├── cleaner.py         # strip_html(), clean_text()
│   │   └── chunker.py         # split_by_sentences(), chunk_with_overlap()
│   ├── pipeline/processor.py  # Pipeline end-to-end
│   └── adapters/marker_adapter.py  # Marker → InputBlock
├── cli.py                     # Entry point CLI
├── tests/                     # Pytest
├── data/                      # Dữ liệu mẫu
└── docs/                      # Tài liệu thiết kế
```

## Chạy Tests

```bash
# Chạy tất cả tests
uv run pytest tests/ -v

# Chạy test riêng từng module
uv run pytest tests/test_marker_adapter.py -v
uv run pytest tests/test_processor.py -v
```

## Boot.dev References

| Tham số | Giá trị | Nguồn |
|---|---|---|
| Max tokens/chunk | 200 | all-MiniLM-L6-v2 limit 256 (Ch.4) |
| Overlap ratio | 20% | Ch.6 khuyến nghị |
| Sentence split regex | `(?<=[.!?])\s+` | Ch.6 |
| Search | Hybrid BM25 + Semantic | Ch.7 |
| Reranking model | cross-encoder/ms-marco-TinyBERT-L2-v2 | Ch.9 |

## Lộ trình

- **Niên luận cơ sở:** Module semantic chunking cho tài liệu ĐHCT
- **Niên luận CNKTPM:** Tích hợp vào eco-commerce chatbot RAG
- **Luận văn:** Microservice trong DataOps Pipeline AgenticRAG
