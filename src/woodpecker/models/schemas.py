"""Pydantic schemas cho Woodpecker Semantic Chunking Engine.

Đây là 'hợp đồng' dữ liệu giữa các module:
- InputBlock: dữ liệu từ Document Parser (Marker, qwen2-vl...)
- OutputChunk: dữ liệu xuất ra cho Boot.dev RAG pipeline

Tham khảo: docs/woodpecker_system_spec.md — Mục 2 và 4
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4


class InputBlock(BaseModel):
    """Schema đầu vào cho Woodpecker.
    
    Bất kỳ Document Parser nào (Marker, qwen2-vl, hay custom tool)
    chỉ cần xuất dữ liệu theo schema này là Woodpecker xử lý được.
    
    Attributes:
        text: Nội dung text — có thể chứa HTML tags (sẽ được clean ở core/cleaner.py)
        block_type: Loại block từ parser. Ví dụ: "Text", "SectionHeader", "Table", "ListGroup"
        section_hierarchy: Breadcrumb cấu trúc tài liệu. Ví dụ: {"1": "Chương I", "2": "Điều 5"}
        page_index: Chỉ số trang gốc trong PDF (tùy chọn)
    """
    text: str
    block_type: str
    section_hierarchy: dict[str, str] = Field(default_factory=dict)
    page_index: Optional[int] = None


class ChunkMetadata(BaseModel):
    """Metadata đính kèm mỗi chunk đầu ra.
    
    Thiết kế dựa trên Boot.dev Ch.8 — mỗi chunk cần metadata
    để truy xuất nguồn gốc (lineage) về tài liệu gốc.
    
    Attributes:
        source_file: Tên file gốc — tương tự doc_idx trong Boot.dev
        chunk_index: Thứ tự chunk trong tài liệu — tương tự chunk_idx trong Boot.dev
        header_context: Đường dẫn cấu trúc. Ví dụ: "Chương I > Điều 5. Thời gian học tập"
    """
    source_file: str
    chunk_index: int
    header_context: str


class OutputChunk(BaseModel):
    """Schema đầu ra của Woodpecker — plain-text chunk cho RAG pipeline.
    
    Trường `text` chứa plain text thuần túy (không HTML, không Markdown)
    — tương đương với các trường text trong movies.json của Boot.dev.
    
    Trường `token_count` phải ≤ 200 để nằm dưới giới hạn 256 tokens
    của model all-MiniLM-L6-v2 (Boot.dev Ch.4).
    
    Attributes:
        chunk_id: UUID định danh duy nhất — dùng làm key trong Vector DB
        text: Nội dung plain text sạch — đầu vào cho embedding/BM25
        token_count: Số token ước lượng (phải ≤ MAX_TOKENS)
        metadata: Thông tin truy xuất nguồn gốc
    """
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    text: str
    token_count: int
    metadata: ChunkMetadata
