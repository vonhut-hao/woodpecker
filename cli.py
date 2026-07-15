"""Woodpecker CLI — Giao diện dòng lệnh.

Sử dụng:
    python cli.py process --input data/sample.json --output output.json --source-file "QD3266.pdf"
    python cli.py info

Tham khảo: docs/architecture.md — CLI
"""
import argparse
import json
import sys
import os

# Thêm src/ vào Python path để import woodpecker package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from woodpecker import __version__
from woodpecker.config import MAX_TOKENS, MIN_TOKENS, OVERLAP_RATIO, VN_TOKEN_MULTIPLIER
from woodpecker.adapters.marker_adapter import marker_chunks_to_input
from woodpecker.pipeline.processor import woodpecker_process


def cmd_process(args: argparse.Namespace) -> None:
    """Xử lý lệnh 'process' — chạy pipeline chunking."""
    input_path = args.input
    output_path = args.output
    source_file = args.source_file

    print(f"[Woodpecker] v{__version__}")
    print(f"   Input:  {input_path}")
    print(f"   Output: {output_path}")
    print(f"   Source: {source_file}")
    print()

    # Bước 1: Adapter — đọc Marker chunks JSON
    print("[Input] Đọc và chuyển đổi Marker chunks...")
    input_blocks = marker_chunks_to_input(input_path)
    print(f"   → {len(input_blocks)} blocks (sau khi lọc)")

    # Bước 2: Pipeline — chunking
    print("[Process] Đang phân mảnh...")
    output_chunks = woodpecker_process(
        input_blocks=input_blocks,
        source_file=source_file,
        max_tokens=args.max_tokens,
        overlap_ratio=args.overlap,
    )
    print(f"   → {len(output_chunks)} chunks")

    # Bước 3: Ghi output JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_chunks, f, ensure_ascii=False, indent=2)
    print(f"\n[Success] Đã ghi kết quả vào: {output_path}")

    # Thống kê
    if output_chunks:
        token_counts = [c["token_count"] for c in output_chunks]
        print(f"\n[Stats] Thống kê:")
        print(f"   Tổng chunks:    {len(output_chunks)}")
        print(f"   Token min:      {min(token_counts)}")
        print(f"   Token max:      {max(token_counts)}")
        print(f"   Token trung bình: {sum(token_counts) / len(token_counts):.1f}")


def cmd_info(args: argparse.Namespace) -> None:
    """Xử lý lệnh 'info' — hiển thị thông tin cấu hình."""
    print(f"[Woodpecker] Semantic Chunking Engine v{__version__}")
    print(f"   Đề tài: Niên luận cơ sở — Semantic Chunking cho RAG")
    print()
    print("[Config] Cấu hình hiện tại:")
    print(f"   MAX_TOKENS:          {MAX_TOKENS}")
    print(f"   MIN_TOKENS:          {MIN_TOKENS}")
    print(f"   OVERLAP_RATIO:       {OVERLAP_RATIO}")
    print(f"   VN_TOKEN_MULTIPLIER: {VN_TOKEN_MULTIPLIER}")
    print()
    print("[Ref] Boot.dev References:")
    print(f"   Embedding model:     all-MiniLM-L6-v2 (max 256 tokens)")
    print(f"   Chunking strategy:   Semantic (sentence boundary) + Fixed-size + Overlap")
    print(f"   Search:              Hybrid (BM25 + Cosine Similarity)")


def main() -> None:
    """Entry point chính cho CLI."""
    parser = argparse.ArgumentParser(
        prog="woodpecker",
        description="[Woodpecker] Semantic Chunking Engine — Phân mảnh ngữ nghĩa cho RAG",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Các lệnh có sẵn")

    # === Lệnh process ===
    process_parser = subparsers.add_parser(
        "process",
        help="Chạy pipeline chunking trên file Marker chunks JSON",
    )
    process_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Đường dẫn tới file Marker chunks JSON",
    )
    process_parser.add_argument(
        "--output", "-o",
        required=True,
        help="Đường dẫn file JSON kết quả",
    )
    process_parser.add_argument(
        "--source-file", "-s",
        required=True,
        help="Tên file PDF gốc (metadata cho Boot.dev pipeline)",
    )
    process_parser.add_argument(
        "--max-tokens",
        type=int,
        default=MAX_TOKENS,
        help=f"Giới hạn token tối đa/chunk (mặc định: {MAX_TOKENS})",
    )
    process_parser.add_argument(
        "--overlap",
        type=float,
        default=OVERLAP_RATIO,
        help=f"Tỷ lệ overlap (mặc định: {OVERLAP_RATIO})",
    )

    # === Lệnh info ===
    subparsers.add_parser("info", help="Hiển thị thông tin cấu hình")

    args = parser.parse_args()

    match args.command:
        case "process":
            cmd_process(args)
        case "info":
            cmd_info(args)
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
