import sys
import os
import json
import numpy as np
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer

# Thêm src vào PYTHONPATH để import woodpecker
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from woodpecker.core.cleaner import clean_text
from woodpecker.config import MAX_TOKENS, VN_TOKEN_MULTIPLIER

# Tải biến môi trường (GEMINI_API_KEY)
load_dotenv()

# Khởi tạo client Gemini
api_key = os.environ.get("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    print("[Cảnh báo]: Chưa cấu hình GEMINI_API_KEY")

GEMINI_MODELS = ["gemini-3.6-flash", "gemini-3.6-pro"]


# --- 1. NAIVE CHUNKER ---
def naive_chunking(text: str, max_tokens: int = MAX_TOKENS) -> list[str]:
    words = text.split()
    max_words = int(max_tokens / VN_TOKEN_MULTIPLIER)
    chunks = []
    for i in range(0, len(words), max_words):
        chunks.append(" ".join(words[i:i + max_words]))
    return chunks

# --- 2. VECTOR SEARCH ĐƠN GIẢN ---
def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0: return 0.0
    return dot_product / (norm1 * norm2)

def search(query: str, chunks: list[str], model: SentenceTransformer, top_k: int = 1) -> list[str]:
    query_emb = model.encode(query)
    chunk_embs = model.encode(chunks)
    results = [(cosine_similarity(query_emb, chunk_embs[i]), chunks[i]) for i in range(len(chunks))]
    results.sort(key=lambda x: x[0], reverse=True)
    return [text for score, text in results[:top_k]]

# --- 3. GỌI LLM TẠO CÂU TRẢ LỜI (GENERATION) ---
import time

def generate_answer(query: str, retrieved_context: str) -> str:
    prompt = f"""Bạn là chuyên viên tư vấn. Hãy trả lời câu hỏi sau dựa trên đoạn trích tài liệu.

Đoạn trích tài liệu:
{retrieved_context}

Câu hỏi: {query}

Chỉ thị:
- Tìm và tóm tắt câu trả lời có trong đoạn trích.
- Nếu đoạn trích bị đứt gãy không rõ nghĩa, hãy nói "Tài liệu bị đứt đoạn, không thể trả lời chắc chắn."
- Nếu hoàn toàn không có thông tin, hãy nói "Không có thông tin."

Trả lời:"""

    errors = []
    if not client:
        return "[LỖI]: Chưa khởi tạo Client do thiếu GEMINI_API_KEY"

    for model_id in GEMINI_MODELS:
        try:
            interaction = client.interactions.create(
                model=model_id,
                input=prompt
            )
            ans = interaction.output_text.strip()
            return f"\n(Nguồn: {model_id})\n{ans}"
        except Exception as e:
            err_msg = str(e)
            errors.append(f"{model_id}: {err_msg}")
            if "401" in err_msg or "403" in err_msg or "API_KEY_INVALID" in err_msg:
                return f"[LỖI XÁC THỰC API KEY]: Khóa API Gemini của bạn không hợp lệ hoặc chưa được kích hoạt. Lỗi chi tiết: {err_msg}"
            continue
            
    return f"[LỖI]: Đã thử tất cả model nhưng đều thất bại. Chi tiết lỗi:\n" + "\n".join(errors)

# --- 4. MAIN INTERACTIVE CLI ---
def main():
    print("="*60)
    print(" WOODPECKER INTERACTIVE RAG BENCHMARK CLI ".center(60, " "))
    print("="*60)
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("\n[LỖI]: Chưa cấu hình GEMINI_API_KEY!")
        print("1. Lấy API key miễn phí tại: https://aistudio.google.com/app/apikey")
        print("2. Thêm GEMINI_API_KEY=your_api_key vào file .env")
        return

    print("\n[1/3] Đang tải mô hình Embedding (BAAI/bge-m3)...")
    # Sử dụng BGE-M3 (State of the Art cho Multilingual RAG) để bắt ngữ nghĩa Tiếng Việt tốt nhất
    model = SentenceTransformer("BAAI/bge-m3")
    
    print("[2/3] Đang chuẩn bị dữ liệu & Chunking...")
    input_path = r"C:\Users\HAVO\Downloads\Marker_Chunks\QD3266_QD_cong_tac_hoc_vu_danh_cho_SV_trinh_do_dai_hoc_hinh_thuc_chinh_quy_V3\QD3266_QD_cong_tac_hoc_vu_danh_cho_SV_trinh_do_dai_hoc_hinh_thuc_chinh_quy_V3.json"
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
        raw_blocks = raw_data.get("blocks", raw_data) if isinstance(raw_data, dict) else raw_data
        
    from woodpecker.adapters.marker_adapter import strip_html
    raw_text = " ".join(clean_text(strip_html(b.get("html", ""))) for b in raw_blocks if b.get("block_type") not in ("Picture", "Line", "PageHeader"))
    
    naive_chunks = naive_chunking(raw_text)
    
    with open('output_full.json', 'r', encoding='utf-8') as f:
        woodpecker_chunks = [c["text"] for c in json.load(f)]
        
    print("[3/3] Hệ thống RAG đã sẵn sàng!\n")
    print("Gõ 'quit' hoặc 'exit' để thoát.\n")
    
    while True:
        try:
            query = input("\n[WoodpeckerRAG_Benchmark] Nhập câu hỏi truy vấn: ").strip()
            if not query: continue
            if query.lower() in ('quit', 'exit'): break
            
            print("\n" + "-"*60)
            
            # --- KIỂM THỬ NAIVE ---
            print(">>> 1. KẾT QUẢ TỪ NAIVE CHUNKER (Cắt mù quáng 200 tokens) <<<")
            naive_results = search(query, naive_chunks, model, top_k=3)
            naive_context = "\n---\n".join(naive_results)
            print(f"[Context nạp vào LLM]: {naive_results[0][:150]}... (và 2 đoạn khác)")
            print(f"[LLM Trả lời]: ", end="", flush=True)
            ans_naive = generate_answer(query, naive_context)
            print(f"\033[91m{ans_naive}\033[0m") # In màu đỏ
            
            print("\n" + "-"*60)
            
            # --- KIỂM THỬ WOODPECKER ---
            print(">>> 2. KẾT QUẢ TỪ WOODPECKER (Semantic + Overlap) <<<")
            wp_results = search(query, woodpecker_chunks, model, top_k=3)
            wp_context = "\n---\n".join(wp_results)
            print(f"[Context nạp vào LLM]: {wp_results[0][:150]}... (và 2 đoạn khác)")
            print(f"[LLM Trả lời]: ", end="", flush=True)
            ans_wp = generate_answer(query, wp_context)
            print(f"\033[92m{ans_wp}\033[0m") # In màu xanh lá
            
            print("\n" + "="*60)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n[Lỗi đột xuất]: {e}")

if __name__ == "__main__":
    main()
