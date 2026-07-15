import sys
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Thêm src vào PYTHONPATH để import woodpecker
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from woodpecker.core.cleaner import clean_text
from woodpecker.config import MAX_TOKENS, VN_TOKEN_MULTIPLIER

# --- 1. NAIVE CHUNKER ---
def naive_chunking(text: str, max_tokens: int = MAX_TOKENS) -> list[str]:
    """Cắt text một cách thô bạo (Fixed-size), không quan tâm ranh giới câu."""
    words = text.split()
    max_words = int(max_tokens / VN_TOKEN_MULTIPLIER)
    chunks = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i:i + max_words]))
    return chunks

# --- 2. VECTOR DB ĐƠN GIẢN ---
def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

def search(query: str, chunks: list[str], model: SentenceTransformer, top_k: int = 2) -> list[tuple[float, str]]:
    query_embedding = model.encode(query)
    chunk_embeddings = model.encode(chunks)
    
    results = []
    for i, chunk_emb in enumerate(chunk_embeddings):
        sim = cosine_similarity(query_embedding, chunk_emb)
        results.append((sim, chunks[i]))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_k]

# --- 3. MAIN BENCHMARK ---
def main():
    print("[1/4] Đang tải mô hình Embedding (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print("\n[2/4] Đang chuẩn bị dữ liệu...")
    # Lấy dữ liệu raw từ marker chunks gốc để test Naive Chunker
    input_path = r"C:\Users\HAVO\Downloads\Marker_Chunks\QD3266_QD_cong_tac_hoc_vu_danh_cho_SV_trinh_do_dai_hoc_hinh_thuc_chinh_quy_V3\QD3266_QD_cong_tac_hoc_vu_danh_cho_SV_trinh_do_dai_hoc_hinh_thuc_chinh_quy_V3.json"
    
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        raw_blocks = raw_data.get("blocks", raw_data) if isinstance(raw_data, dict) else raw_data
        
    from woodpecker.adapters.marker_adapter import strip_html
    raw_text = " ".join(clean_text(strip_html(b.get("html", ""))) for b in raw_blocks if b.get("block_type") not in ("Picture", "Line", "PageHeader"))
    
    print("\n[3/4] Đang thực hiện Chunking...")
    # 3.1 Naive Chunks
    naive_chunks = naive_chunking(raw_text)
    print(f"  -> Naive Chunker tạo ra: {len(naive_chunks)} chunks.")
    
    # 3.2 Woodpecker Chunks (Lấy từ file output_full.json đã chạy trước đó)
    with open('output_full.json', 'r', encoding='utf-8') as f:
        woodpecker_output = json.load(f)
    woodpecker_chunks = [c["text"] for c in woodpecker_output]
    print(f"  -> Woodpecker tạo ra: {len(woodpecker_chunks)} chunks.")
    
    print("\n[4/4] BẮT ĐẦU BENCHMARK (TÌM KIẾM NGỮ NGHĨA)")
    queries = [
        "Sinh viên bị buộc thôi học trong những trường hợp nào?",
        "Thời gian học tập tối đa cho phép để sinh viên hoàn thành chương trình đào tạo là bao lâu?"
    ]
    
    for query in queries:
        print(f"\n" + "="*80)
        print(f"TRUY VẤN: '{query}'")
        print("="*80)
        
        # Naive Search
        print("\n--- KẾT QUẢ CỦA NAIVE CHUNKER (Cắt cứng 200 tokens) ---")
        naive_results = search(query, naive_chunks, model, top_k=1)
        for score, text in naive_results:
            print(f"[Score: {score:.3f}]\n{text}")
            
        # Woodpecker Search
        print("\n--- KẾT QUẢ CỦA WOODPECKER (Semantic + Overlap) ---")
        woodpecker_results = search(query, woodpecker_chunks, model, top_k=1)
        for score, text in woodpecker_results:
            print(f"[Score: {score:.3f}]\n{text}")

if __name__ == "__main__":
    main()
