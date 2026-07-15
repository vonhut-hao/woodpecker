"""Adapter chuyển đổi Marker chunks JSON → Woodpecker InputBlock.

Marker (marker-pdf) xuất file JSON với format chunks chứa mảng các block,
mỗi block có: id, block_type, html, section_hierarchy, polygon...

Adapter này:
1. Đọc file JSON từ Marker
2. Lọc bỏ block không chứa nội dung (Picture, Line, PageHeader)
3. Strip HTML tags khỏi trường "html"
4. Trích xuất page_index từ trường "id"
5. Xuất danh sách dict theo InputBlock schema

Lưu ý: Đây là adapter — KHÔNG phải phần cốt lõi của Woodpecker.
Tương lai khi dùng qwen2-vl hoặc parser khác, sẽ viết adapter riêng.

Tham khảo: docs/woodpecker_system_spec.md — Mục 2.3
"""
import json
import re

from woodpecker.config import SKIP_BLOCK_TYPES


def strip_html(html: str) -> str:
    """Loại bỏ tất cả HTML tags, giữ lại nội dung text bên trong.

    Ví dụ:
        "<p>Sinh viên <b>chính quy</b></p>" → "Sinh viên chính quy"
        "<h2>QUYẾT ĐỊNH</h2>" → "QUYẾT ĐỊNH"

    Args:
        html: Chuỗi chứa HTML tags từ Marker output

    Returns:
        Chuỗi plain text không còn HTML tags
    """
    # Thay thế HTML tags bằng khoảng trắng (tránh nối dính 2 từ)
    text = re.sub(r'<[^>]+>', ' ', html)
    # Gộp khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _extract_page_index(block_id: str) -> int | None:
    """Trích xuất chỉ số trang từ trường id của Marker block.

    Format id: "/page/{page_index}/Page/{N}/BlockType/{M}"
    Ví dụ: "/page/3/Page/0/Text/5" → page_index = 3

    Args:
        block_id: Chuỗi id từ Marker block

    Returns:
        Chỉ số trang (int) hoặc None nếu không parse được
    """
    match = re.match(r'/page/(\d+)/', block_id)
    return int(match.group(1)) if match else None


def _resolve_section_hierarchy(hierarchy: dict) -> dict[str, str]:
    """Chuẩn hóa section_hierarchy.

    Marker chunks format có thể chứa:
    - Text values: {"1": "Chương I", "2": "Điều 5"} → giữ nguyên
    - ID references: {"1": "/page/2/SectionHeader/5"} → giữ nguyên
      (trường hợp này hiếm gặp trong chunks format)

    Args:
        hierarchy: Dict section_hierarchy từ Marker block

    Returns:
        Dict đã chuẩn hóa
    """
    if not hierarchy:
        return {}

    resolved: dict[str, str] = {}
    for level, value in hierarchy.items():
        if isinstance(value, str):
            # Nếu là ID reference (/page/...), vẫn giữ nguyên
            # Pipeline sẽ dùng nó như header_context
            resolved[str(level)] = value
        else:
            resolved[str(level)] = str(value)

    return resolved


def marker_chunks_to_input(marker_chunks_path: str) -> list[dict]:
    """Chuyển đổi Marker chunks JSON thành danh sách InputBlock dict.

    Đọc file JSON output từ Marker (--output_format chunks),
    lọc bỏ các block không chứa nội dung, và chuyển đổi format.

    Marker chunks JSON có cấu trúc:
    {
        "blocks": [
            {
                "id": "/page/0/Page/0/SectionHeader/0",
                "block_type": "SectionHeader",
                "html": "<h2>QUYẾT ĐỊNH</h2>",
                "section_hierarchy": {"2": "QUYẾT ĐỊNH"},
                ...
            },
            ...
        ],
        "page_info": {...}
    }

    Args:
        marker_chunks_path: Đường dẫn tới file JSON từ Marker

    Returns:
        Danh sách dict theo InputBlock schema:
        [{"text": "...", "block_type": "...", "section_hierarchy": {...}, "page_index": N}]

    Raises:
        FileNotFoundError: Nếu file không tồn tại
        json.JSONDecodeError: Nếu file không phải JSON hợp lệ
        KeyError: Nếu file thiếu key "blocks"
    """
    with open(marker_chunks_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Marker chunks format: top-level có key "blocks"
    if isinstance(raw_data, dict) and "blocks" in raw_data:
        raw_blocks = raw_data["blocks"]
    elif isinstance(raw_data, list):
        # Fallback: nếu file là mảng phẳng (format cũ)
        raw_blocks = raw_data
    else:
        raise KeyError(
            "File JSON không đúng format Marker chunks. "
            "Cần có key 'blocks' ở top-level hoặc là mảng JSON."
        )

    blocks: list[dict] = []

    for raw_block in raw_blocks:
        block_type = raw_block.get("block_type", "")

        # Lọc bỏ các block không chứa nội dung text
        if block_type in SKIP_BLOCK_TYPES:
            continue

        # Strip HTML từ trường "html"
        html_content = raw_block.get("html", "")
        text = strip_html(html_content)

        # Bỏ qua block rỗng sau khi strip
        if not text:
            continue

        # Trích xuất page_index từ id
        block_id = raw_block.get("id", "")
        page_index = _extract_page_index(block_id)

        # Chuẩn hóa section_hierarchy
        hierarchy = _resolve_section_hierarchy(
            raw_block.get("section_hierarchy", {})
        )

        blocks.append({
            "text": text,
            "block_type": block_type,
            "section_hierarchy": hierarchy,
            "page_index": page_index,
        })

    return blocks
