"""Module phân mảnh văn bản (chunking) cho Woodpecker.

Implement các thuật toán chunking từ Boot.dev Ch.6:
- Semantic Chunking: cắt tại ranh giới câu (dấu . ! ?)
- Fixed-Size + Overlap: giới hạn kích thước chunk + 20% overlap

Tham khảo: 
- docs/bootdev_rag_reference.md — Chapter 6: Chunking Strategies
- docs/woodpecker_system_spec.md — Mục 3, Bước 2
"""
import re

from woodpecker.config import MAX_TOKENS, MIN_TOKENS, OVERLAP_RATIO, VN_TOKEN_MULTIPLIER


def estimate_tokens(text: str) -> int:
    """Ước lượng số token của một đoạn text.
    
    Tiếng Việt có dấu thanh nên tokenizer thường tách thành
    nhiều token hơn tiếng Anh. Hệ số VN_TOKEN_MULTIPLIER = 1.3
    là ước lượng trung bình.
    
    Lưu ý: Đây là ước lượng. Trong production, nên dùng tokenizer
    thật từ model (ví dụ: SentenceTransformer tokenizer).
    
    Args:
        text: Đoạn text cần đếm token
        
    Returns:
        Số token ước lượng (int)
    """
    word_count = len(text.split())
    return int(word_count * VN_TOKEN_MULTIPLIER)


def split_by_sentences(text: str) -> list[str]:
    """Cắt text thành danh sách câu theo ranh giới tự nhiên.
    
    Kỹ thuật: Boot.dev Ch.6 — Semantic Chunking.
    Regex: (?<=[.!?])\\s+ → cắt SAU dấu . ! ? khi theo sau là khoảng trắng.
    
    Boot.dev nguyên văn: 
    "Sentence Splitting: You must use the Python re.split function 
     to split text at sentence boundaries."
    "Regex Precision: Use the specific lookbehind regex: 
     re.split(r'(?<=[.!?])\\s+')"
    
    Args:
        text: Đoạn text cần tách câu
        
    Returns:
        Danh sách các câu đã tách
    """
    # Regex lookbehind: cắt SAU dấu kết thúc câu + khoảng trắng
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Lọc bỏ câu rỗng
    return [s.strip() for s in sentences if s.strip()]


def _split_long_sentence(sentence: str, max_tokens: int) -> list[str]:
    """Cắt câu quá dài bằng dấu phẩy/chấm phẩy hoặc fixed-size (Fallback).
    
    Bảo vệ hệ thống khỏi các câu quá dài (ví dụ liệt kê trong văn bản pháp luật)
    tránh vượt giới hạn token của model embedding.
    """
    if estimate_tokens(sentence) <= max_tokens:
        return [sentence]
        
    # Ưu tiên 2: Cắt bằng dấu chấm phẩy
    parts = re.split(r'(?<=[;])\s+', sentence)
    if len(parts) > 1 and all(estimate_tokens(p) <= max_tokens for p in parts):
        return [p.strip() for p in parts if p.strip()]
        
    # Ưu tiên 3: Cắt bằng dấu phẩy
    parts = re.split(r'(?<=[,])\s+', sentence)
    if len(parts) > 1 and all(estimate_tokens(p) <= max_tokens for p in parts):
        return [p.strip() for p in parts if p.strip()]
        
    # Ưu tiên 4: Fixed-Size Chunking (Cắt theo số từ)
    words = sentence.split()
    max_words = max(1, int(max_tokens / VN_TOKEN_MULTIPLIER))
    
    sub_chunks = []
    for i in range(0, len(words), max_words):
        sub_chunks.append(" ".join(words[i:i + max_words]))
    return sub_chunks


def chunk_with_overlap(
    sentences: list[str],
    max_tokens: int = MAX_TOKENS,
    overlap_ratio: float = OVERLAP_RATIO,
) -> list[str]:
    """Ghép các câu thành chunk, áp dụng overlap và fallback cắt câu dài.
    
    Kỹ thuật: Boot.dev Ch.6 — Fixed-Size Chunking + Overlap.
    
    Thuật toán:
    1. Duyệt qua từng câu. Nếu câu > max_tokens, kích hoạt fallback cắt nhỏ câu.
    2. Nếu thêm câu mới vượt max_tokens → đóng chunk hiện tại
    3. Giữ lại 20% câu cuối làm overlap cho chunk tiếp theo
    4. Tiếp tục cho đến hết danh sách câu
    
    Args:
        sentences: Danh sách câu (từ split_by_sentences)
        max_tokens: Giới hạn token tối đa mỗi chunk (mặc định: 200)
        overlap_ratio: Tỷ lệ overlap (mặc định: 0.20 = 20%)
        
    Returns:
        Danh sách các chunk text đã ghép
    """
    if not sentences:
        return []
    
    chunks = []
    current = []        # Danh sách câu trong chunk hiện tại
    current_count = 0   # Số token hiện tại
    
    for sentence in sentences:
        # Kích hoạt Fallback nếu câu dài vượt mức cho phép
        sub_sentences = _split_long_sentence(sentence, max_tokens)
        
        for sub in sub_sentences:
            s_tokens = estimate_tokens(sub)
            
            # Nếu thêm câu này vượt quá giới hạn VÀ chunk hiện tại không rỗng
            if current_count + s_tokens > max_tokens and current:
                # Đóng chunk hiện tại
                chunks.append(" ".join(current))
                
                # Overlap: giữ lại 20% câu cuối (Boot.dev Ch.6)
                overlap_n = int(len(current) * overlap_ratio)
                
                # Tránh overlap 100% nếu chunk chỉ có 1 câu
                if overlap_n >= len(current):
                    overlap_n = len(current) - 1
                    
                if overlap_n > 0:
                    current = current[-overlap_n:]
                else:
                    current = []
                    
                current_count = sum(estimate_tokens(s) for s in current)
                
                # Cắt bớt phần overlap nếu ghép với câu mới vượt quá max_tokens
                while current and current_count + s_tokens > max_tokens:
                    dropped = current.pop(0)
                    current_count -= estimate_tokens(dropped)
            
            current.append(sub)
            current_count += s_tokens
    
    # Đóng chunk cuối cùng
    if current:
        chunks.append(" ".join(current))
    
    return chunks
