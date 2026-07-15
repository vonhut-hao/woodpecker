"""Pipeline xử lý chính của Woodpecker.

Module này kết nối tất cả module core (cleaner, chunker) thành
luồng xử lý end-to-end: InputBlocks → OutputChunks.

Tham khảo: docs/woodpecker_system_spec.md — Mục 3
"""
from uuid import uuid4

from woodpecker.config import MAX_TOKENS, MIN_TOKENS, OVERLAP_RATIO
from woodpecker.core.cleaner import clean_text
from woodpecker.core.chunker import split_by_sentences, chunk_with_overlap, estimate_tokens


def group_by_section(blocks: list[dict]) -> list[list[dict]]:
    """Nhóm các block liên tiếp có cùng section_hierarchy.

    Mục đích: Gộp các block (Text, Table, ListGroup) cùng thuộc một
    section (ví dụ: "Điều 5. Thời gian học tập") thành một nhóm
    để xử lý chung — giữ nguyên ngữ cảnh tài liệu.

    Ví dụ:
        Block 1: section = {"1": "Chương I", "2": "Điều 2"}  ┐
        Block 2: section = {"1": "Chương I", "2": "Điều 2"}  ┘ → Nhóm 1
        Block 3: section = {"1": "Chương I", "2": "Điều 3"}  → Nhóm 2

    Args:
        blocks: Danh sách dict block (đã qua adapter)

    Returns:
        Danh sách các nhóm, mỗi nhóm là danh sách block cùng section
    """
    if not blocks:
        return []

    groups: list[list[dict]] = []
    current_group: list[dict] = [blocks[0]]

    for block in blocks[1:]:
        if block.get("section_hierarchy") == current_group[0].get("section_hierarchy"):
            current_group.append(block)
        else:
            groups.append(current_group)
            current_group = [block]

    # Đóng nhóm cuối cùng
    groups.append(current_group)
    return groups


def woodpecker_process(
    input_blocks: list[dict],
    source_file: str,
    max_tokens: int = MAX_TOKENS,
    min_tokens: int = MIN_TOKENS,
    overlap_ratio: float = OVERLAP_RATIO,
) -> list[dict]:
    """Pipeline chính của Woodpecker.

    Luồng xử lý:
    1. Nhóm blocks theo section_hierarchy
    2. Với mỗi nhóm: ghép text → clean → split câu → chunk + overlap
    3. Gắn metadata (source_file, chunk_index, header_context)
    4. Xuất danh sách OutputChunk dạng dict

    Args:
        input_blocks: Danh sách InputBlock dạng dict (từ adapter)
        source_file: Tên file PDF gốc — metadata cho Boot.dev pipeline
        max_tokens: Giới hạn token tối đa/chunk (mặc định: 200)
        min_tokens: Giới hạn token tối thiểu/chunk (mặc định: 30)
        overlap_ratio: Tỷ lệ overlap (mặc định: 0.20)

    Returns:
        Danh sách dict theo OutputChunk schema:
        [{"chunk_id": "...", "text": "...", "token_count": N, "metadata": {...}}]
    """
    output_chunks: list[dict] = []
    chunk_index = 0

    # Bước 1: Nhóm blocks cùng section
    groups = group_by_section(input_blocks)

    for section_blocks in groups:
        # Lấy header_context từ section_hierarchy của block đầu tiên
        hierarchy = section_blocks[0].get("section_hierarchy", {})
        header_context = " > ".join(hierarchy.values()) if hierarchy else ""

        # Ghép text từ tất cả block KHÔNG PHẢI SectionHeader trong nhóm
        text_parts = []
        for block in section_blocks:
            if block.get("block_type") != "SectionHeader":
                cleaned = clean_text(block.get("text", ""))
                if cleaned:
                    text_parts.append(cleaned)

        combined_text = " ".join(text_parts)

        # Bỏ qua section quá ngắn (tránh semantic dilution)
        if not combined_text or estimate_tokens(combined_text) < min_tokens:
            continue

        # Bước 2: Cắt theo ranh giới câu (Boot.dev Ch.6 — Semantic Chunking)
        sentences = split_by_sentences(combined_text)

        # Bước 3: Ghép câu thành chunk + overlap (Boot.dev Ch.6)
        chunks = chunk_with_overlap(
            sentences,
            max_tokens=max_tokens,
            overlap_ratio=overlap_ratio,
        )

        # Bước 4: Tạo OutputChunk cho mỗi chunk
        for chunk_text in chunks:
            token_count = estimate_tokens(chunk_text)

            output_chunks.append({
                "chunk_id": str(uuid4()),
                "text": chunk_text,
                "token_count": token_count,
                "metadata": {
                    "source_file": source_file,
                    "chunk_index": chunk_index,
                    "header_context": header_context,
                },
            })
            chunk_index += 1

    return output_chunks
