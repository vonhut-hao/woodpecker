"""Cấu hình hằng số cho Woodpecker Semantic Chunking Engine.

Tất cả tham số cấu hình nằm tập trung tại đây.
Chỉ cần thay đổi file này để điều chỉnh hành vi chunking.

Ràng buộc từ Boot.dev:
- MAX_TOKENS < 256 (giới hạn all-MiniLM-L6-v2, Boot.dev Ch.4)
- OVERLAP_RATIO = 0.20 (khuyến nghị Boot.dev Ch.6)
"""

# === CHUNKING PARAMETERS ===

# Giới hạn token tối đa mỗi chunk
# Đặt 200 để sau khi thêm overlap vẫn nằm dưới 256 (all-MiniLM-L6-v2)
MAX_TOKENS: int = 200

# Giới hạn token tối thiểu mỗi chunk
# Chunk nhỏ hơn ngưỡng này sẽ bị gộp vào chunk liền kề
# Tránh "semantic dilution" (Boot.dev Ch.6)
MIN_TOKENS: int = 30

# Tỷ lệ overlap giữa các chunk liên tiếp
# Boot.dev Ch.6: "Use a rule of thumb of 20% overlap"
OVERLAP_RATIO: float = 0.20

# === TOKEN ESTIMATION ===

# Hệ số nhân cho tiếng Việt
# Tiếng Việt có dấu thanh → tokenizer tách thành nhiều token hơn tiếng Anh
# 1 từ tiếng Việt ≈ 1.3 tokens trung bình
VN_TOKEN_MULTIPLIER: float = 1.3

# === BLOCK FILTERING ===

# Các block_type từ Marker cần bỏ qua (không chứa nội dung text)
SKIP_BLOCK_TYPES: tuple[str, ...] = ("Picture", "Line", "PageHeader")
