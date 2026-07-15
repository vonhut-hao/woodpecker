# ĐẶC TẢ HỆ THỐNG: WOODPECKER SEMANTIC CHUNKING ENGINE

**Phiên bản:** 3.0  
**Đề tài:** Niên luận cơ sở — Semantic Chunking cho RAG  
**Mục đích:** Woodpecker là module Python nhận đầu vào có cấu trúc (JSON) và xuất ra plain-text chunks sạch — sẵn sàng đưa vào RAG pipeline theo kiến trúc Boot.dev.

**Lộ trình tái sử dụng:**
- **Niên luận CNKTPM:** eco-commerce chatbot tích hợp RAG → Woodpecker xử lý chunking cho knowledge base sản phẩm
- **Luận văn:** DataOps Pipeline & Microservice for AgenticRAG → Woodpecker là microservice chunking trong pipeline

---

## 1. PHẠM VI (SCOPE)

### 1.1. Woodpecker LÀM:
- Nhận JSON có cấu trúc (mảng các block có `text`, `type`, `metadata`)
- Làm sạch text (strip HTML, loại nhiễu)
- Ghép các block nhỏ thành chunk có kích thước phù hợp
- Cắt block lớn theo ranh giới câu + overlap (Boot.dev Ch.6)
- Xuất JSON chunks sạch (plain text + metadata) → đầu vào cho Boot.dev pipeline

### 1.2. Woodpecker KHÔNG LÀM:
- ❌ Không xử lý PDF, DOCX, hay bất kỳ file nhị phân nào
- ❌ Không làm OCR hay nhận dạng ký tự
- ❌ Không embedding, không search, không LLM generation (đó là việc của Boot.dev pipeline)

### 1.3. Sơ đồ vị trí trong pipeline

```
[Ngoài phạm vi Woodpecker]          [WOODPECKER]              [Boot.dev Pipeline]
                                         │
PDF/DOCX/ảnh ──→ Parser ──→ JSON ──→ │ Chunking │ ──→ Chunks ──→ Embedding (Ch.4)
                  │                      │                        BM25 Index (Ch.2-3)
            Hiện tại: Marker             │                        Hybrid Search (Ch.7)
            Tương lai: qwen2-vl          │                        Reranking (Ch.9)
            Hoặc bất kỳ tool nào         │                        RAG Generation (Ch.11)
                                         │                        Agentic RAG (Ch.12)
```

---

## 2. ĐẦU VÀO (INPUT CONTRACT)

### 2.1. Định nghĩa Input Schema

Woodpecker nhận một **mảng JSON** các block. Mỗi block phải có tối thiểu 3 trường:

```python
from pydantic import BaseModel
from typing import Optional

class InputBlock(BaseModel):
    """Schema đầu vào cho Woodpecker.
    
    Bất kỳ Document Parser nào (Marker, qwen2-vl, hay custom tool)
    chỉ cần xuất dữ liệu theo schema này là Woodpecker xử lý được.
    """
    text: str                          # Nội dung text (có thể chứa HTML tags)
    block_type: str                    # Loại block: "Text", "SectionHeader", "Table", "ListGroup"
    section_hierarchy: dict[str, str]  # Breadcrumb: {"1": "Chương I", "2": "Điều 5"}
    page_index: Optional[int] = None   # Trang gốc (tùy chọn)
```

### 2.2. Ví dụ đầu vào thực tế

Dữ liệu từ Marker (`--output_format chunks`) sau khi chuyển đổi:

```json
[
  {
    "text": "BỘ GIÁO DỰC VÀ ĐÀO TẠO TRƯỜNG ĐẠI HỌC CẦN THƠ",
    "block_type": "SectionHeader",
    "section_hierarchy": {"2": "BỘ GIÁO DỰC VÀ ĐÀO TẠO TRƯỜNG ĐẠI HỌC CẦN THƠ"},
    "page_index": 0
  },
  {
    "text": "Sinh viên hình thức chính quy của Trường ĐHCT là những người đã trúng tuyển kỳ thi tuyển sinh hoặc được xét tuyển và có quyết định thu nhận vào học hình thức chính quy của Trường.",
    "block_type": "Text",
    "section_hierarchy": {"1": "Chương I NHỮNG VẤN ĐỀ CHUNG", "2": "Điều 2. Sinh viên"},
    "page_index": 2
  },
  {
    "text": "Thời gian thiết kế của CTĐT: 4 năm, Thời gian học tập tối đa: 8 năm. Thời gian thiết kế của CTĐT: 4,5 năm, Thời gian học tập tối đa: 9 năm.",
    "block_type": "Table",
    "section_hierarchy": {"1": "Chương I NHỮNG VẤN ĐỀ CHUNG", "2": "Điều 5. Thời gian học tập"},
    "page_index": 3
  }
]
```

### 2.3. Adapter: Marker chunks → Woodpecker Input

Vì Marker xuất `html` thay vì `text`, cần một adapter nhỏ để chuyển đổi:

```python
import re
import json

def strip_html(html: str) -> str:
    """Loại bỏ HTML tags, giữ lại plain text."""
    text = re.sub(r'<[^>]+>', ' ', html)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def marker_chunks_to_input(marker_chunks_path: str) -> list[dict]:
    """Chuyển đổi Marker chunks output thành Woodpecker input.
    
    Đây là adapter — KHÔNG phải phần cốt lõi của Woodpecker.
    Tương lai khi dùng qwen2-vl, sẽ viết adapter khác.
    """
    with open(marker_chunks_path, 'r', encoding='utf-8') as f:
        raw_chunks = json.load(f)
    
    blocks = []
    for chunk in raw_chunks:
        # Bỏ qua ảnh và đường kẻ
        if chunk["block_type"] in ("Picture", "Line"):
            continue
        
        text = strip_html(chunk["html"])
        if not text:
            continue
        
        # Trích xuất page_index từ id (format: "/page/3/Page/0/...")
        page_match = re.match(r'/page/(\d+)/', chunk["id"])
        page_index = int(page_match.group(1)) if page_match else None
        
        blocks.append({
            "text": text,
            "block_type": chunk["block_type"],
            "section_hierarchy": chunk.get("section_hierarchy", {}),
            "page_index": page_index,
        })
    
    return blocks
```

---

## 3. XỬ LÝ CỐT LÕI (CORE PROCESSING)

### Bước 1: Lọc và làm sạch text

```python
def clean_text(text: str) -> str:
    """Làm sạch text cho Boot.dev pipeline.
    
    Đầu ra phải là plain text thuần túy — tương đương
    với các trường text trong movies.json của Boot.dev.
    """
    # Loại bỏ ký tự đặc biệt không mang ngữ nghĩa
    text = re.sub(r'[^\w\s.,;:!?()\"\'/-]', '', text)
    
    # Gộp khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()
```

### Bước 2: Ghép các block nhỏ + Cắt block lớn

Nguyên tắc tuân thủ Boot.dev:
- **Max 200 tokens/chunk** — dưới giới hạn 256 của `all-MiniLM-L6-v2` (Boot.dev Ch.4)
- **Cắt theo ranh giới câu** — Semantic Chunking (Boot.dev Ch.6)
- **Overlap 20%** — Chunk Overlap (Boot.dev Ch.6)
- **Min 30 tokens** — Tránh chunk quá nhỏ gây semantic dilution (Boot.dev Ch.6)

```python
import re

# Cấu hình — tuân thủ ràng buộc Boot.dev
MAX_TOKENS = 200       # < 256 (all-MiniLM-L6-v2 limit, Boot.dev Ch.4)
MIN_TOKENS = 30        # Tránh semantic dilution (Boot.dev Ch.6)
OVERLAP_RATIO = 0.20   # 20% overlap (Boot.dev Ch.6)

def estimate_tokens(text: str) -> int:
    """Ước lượng token count.
    
    Tiếng Việt: ~1 từ ≈ 1.3 tokens (do dấu thanh).
    Đây là ước lượng, production nên dùng tokenizer thật.
    """
    return int(len(text.split()) * 1.3)

def split_by_sentences(text: str) -> list[str]:
    """Cắt text theo ranh giới câu.
    
    Kỹ thuật: Boot.dev Ch.6 — Semantic Chunking.
    Cắt tại dấu . ! ? theo sau bởi khoảng trắng.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_with_overlap(
    sentences: list[str],
    max_tokens: int = MAX_TOKENS,
    overlap_ratio: float = OVERLAP_RATIO,
) -> list[str]:
    """Ghép câu thành chunk, áp dụng overlap.
    
    Kỹ thuật: Boot.dev Ch.6 — Fixed-Size + Overlap.
    """
    chunks = []
    current = []
    current_count = 0
    
    for sentence in sentences:
        s_tokens = estimate_tokens(sentence)
        
        if current_count + s_tokens > max_tokens and current:
            chunks.append(" ".join(current))
            
            # Overlap: giữ lại 20% cuối (Boot.dev Ch.6)
            overlap_n = max(1, int(len(current) * overlap_ratio))
            current = current[-overlap_n:]
            current_count = sum(estimate_tokens(s) for s in current)
        
        current.append(sentence)
        current_count += s_tokens
    
    if current:
        chunks.append(" ".join(current))
    
    return chunks
```

### Bước 3: Pipeline tổng hợp

```python
from uuid import uuid4

def woodpecker_process(
    input_blocks: list[dict],
    source_file: str,
) -> list[dict]:
    """Pipeline chính của Woodpecker.
    
    Input: Mảng InputBlock (từ adapter)
    Output: Mảng Chunk (plain text + metadata) → Boot.dev pipeline
    """
    output_chunks = []
    chunk_index = 0
    
    # Nhóm các block liên tiếp cùng section_hierarchy
    groups = group_by_section(input_blocks)
    
    for section_blocks in groups:
        # Lấy metadata từ block đầu tiên trong nhóm
        hierarchy = section_blocks[0]["section_hierarchy"]
        header_context = " > ".join(hierarchy.values())
        
        # Ghép text các block trong cùng section
        combined_text = " ".join(
            clean_text(b["text"]) for b in section_blocks
            if b["block_type"] != "SectionHeader"
        )
        
        if not combined_text or estimate_tokens(combined_text) < MIN_TOKENS:
            continue
        
        # Cắt theo ranh giới câu + overlap (Boot.dev Ch.6)
        sentences = split_by_sentences(combined_text)
        chunks = chunk_with_overlap(sentences)
        
        for chunk_text in chunks:
            token_count = estimate_tokens(chunk_text)
            
            output_chunks.append({
                "chunk_id": str(uuid4()),
                "text": chunk_text,       # Plain text → Boot.dev pipeline
                "token_count": token_count,
                "metadata": {
                    "source_file": source_file,
                    "chunk_index": chunk_index,
                    "header_context": header_context,
                },
            })
            chunk_index += 1
    
    return output_chunks

def group_by_section(blocks: list[dict]) -> list[list[dict]]:
    """Nhóm các block liên tiếp có cùng section_hierarchy."""
    if not blocks:
        return []
    
    groups = []
    current_group = [blocks[0]]
    
    for block in blocks[1:]:
        if block["section_hierarchy"] == current_group[0]["section_hierarchy"]:
            current_group.append(block)
        else:
            groups.append(current_group)
            current_group = [block]
    
    groups.append(current_group)
    return groups
```

---

## 4. ĐẦU RA (OUTPUT CONTRACT)

### 4.1. Output Schema

```python
from pydantic import BaseModel, Field
from uuid import uuid4
from typing import Optional

class ChunkMetadata(BaseModel):
    source_file: str       # Tên file gốc — tương tự doc_idx (Boot.dev Ch.8)
    chunk_index: int       # Thứ tự chunk — tương tự chunk_idx (Boot.dev Ch.8)
    header_context: str    # Breadcrumb: "Chương I > Điều 5. Thời gian học tập"

class OutputChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    text: str              # PLAIN TEXT — không HTML, không Markdown
    token_count: int       # Phải ≤ 200 (dưới giới hạn 256 all-MiniLM-L6-v2)
    metadata: ChunkMetadata
```

### 4.2. Ví dụ đầu ra thực tế

```json
[
  {
    "chunk_id": "a1b2c3d4-...",
    "text": "Sinh viên hình thức chính quy của Trường ĐHCT là những người đã trúng tuyển kỳ thi tuyển sinh hoặc được xét tuyển và có quyết định thu nhận vào học hình thức chính quy của Trường. Mỗi SV sẽ được cấp một mã số SV, thẻ SV, tài khoản máy tính và địa chỉ thư điện tử (email) để sử dụng trong suốt quá trình theo học tại Trường.",
    "token_count": 116,
    "metadata": {
      "source_file": "QD3266_QD_cong_tac_hoc_vu.pdf",
      "chunk_index": 3,
      "header_context": "Chương I NHỮNG VẤN ĐỀ CHUNG > Điều 2. Sinh viên"
    }
  }
]
```

### 4.3. Đầu ra khớp Boot.dev pipeline như thế nào?

```python
# === Sau khi Woodpecker xuất chunks, Boot.dev pipeline tiếp nhận: ===

from sentence_transformers import SentenceTransformer
import json

# Load Woodpecker output
with open("woodpecker_output.json", "r") as f:
    chunks = json.load(f)

# Boot.dev Ch.1: Preprocessing
texts = [chunk["text"].lower() for chunk in chunks]  # lowercase
# + stemming, stop words removal...

# Boot.dev Ch.2-3: BM25 Indexing
# bm25_index.add_documents(texts)

# Boot.dev Ch.4: Embedding
model = SentenceTransformer("all-MiniLM-L6-v2")  # max 256 tokens
embeddings = model.encode(texts)  # chunk.token_count ≤ 200 → không bị truncate

# Boot.dev Ch.5: Vector Storage
# vector_db.insert(embeddings, metadata=[c["metadata"] for c in chunks])

# Boot.dev Ch.7: Hybrid Search
# score = alpha * bm25_score + (1 - alpha) * semantic_score

# Boot.dev Ch.9: Reranking
# cross_encoder.rank(query, retrieved_chunks)

# Boot.dev Ch.11: RAG Generation
# prompt = f"Context: {retrieved_text}\nQuestion: {user_query}"
# response = llm.generate(prompt)
```

---

## 5. TỔNG KẾT

### 5.1. Quy tắc thiết kế

| Quy tắc | Lý do |
|---|---|
| Input là JSON (không phải PDF) | Tách biệt phạm vi. Tương lai thay parser mà không sửa Woodpecker |
| Output là plain text (không Markdown) | Khớp với format dữ liệu Boot.dev (movies.json text fields) |
| Max 200 tokens/chunk | Dưới giới hạn 256 của all-MiniLM-L6-v2 (Boot.dev Ch.4) |
| Overlap 20% | Theo khuyến nghị Boot.dev Ch.6 |
| Cắt theo ranh giới câu | Semantic Chunking (Boot.dev Ch.6) |
| Metadata có source_file, chunk_index | Tương tự doc_idx, chunk_idx (Boot.dev Ch.8) |

### 5.2. Mapping với lộ trình học tập

| Giai đoạn | Woodpecker đóng vai trò |
|---|---|
| **Niên luận cơ sở** | Module chính — semantic chunking cho tài liệu ĐHCT |
| **Niên luận CNKTPM** (eco-commerce) | Module chunking cho knowledge base sản phẩm nông sản → chatbot RAG |
| **Luận văn** (DataOps AgenticRAG) | Microservice chunking trong DataOps pipeline, nhận input từ nhiều parser |

### 5.3. Thư viện Python

| Thư viện | Vai trò | Ghi chú |
|---|---|---|
| `re` (built-in) | Regex sentence split, clean text | Boot.dev Ch.6 |
| `json` (built-in) | Đọc/ghi JSON | — |
| `uuid` (built-in) | Sinh chunk_id | — |
| `pydantic` | Validate Input/Output Schema | Tùy chọn, khuyên dùng |

> **Không dependency ngoài built-in** cho phần core. Pydantic là tùy chọn cho validation.
