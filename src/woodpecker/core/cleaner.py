"""Module làm sạch text cho Woodpecker.

Chuyển đổi text bẩn (chứa HTML, ký tự đặc biệt) thành plain text
thuần túy — tương đương với dữ liệu text trong movies.json của Boot.dev.

Tham khảo: docs/woodpecker_system_spec.md — Mục 3, Bước 1
"""
import re


def strip_html(html: str) -> str:
    """Loại bỏ tất cả HTML tags, giữ lại nội dung text bên trong.
    
    Ví dụ:
        "<p>Sinh viên <b>chính quy</b></p>" → "Sinh viên chính quy"
        "<table><tr><td>4 năm</td></tr></table>" → "4 năm"
    
    Args:
        html: Chuỗi chứa HTML tags
        
    Returns:
        Chuỗi plain text không còn HTML tags
    """
    # Thay thế HTML tags bằng khoảng trắng (không nối dính 2 từ)
    text = re.sub(r'<[^>]+>', ' ', html)
    # Gộp khoảng trắng thừa thành 1
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def clean_text(text: str) -> str:
    """Làm sạch text cho Boot.dev pipeline.
    
    Đầu ra phải là plain text thuần túy — tương đương
    với các trường text trong movies.json của Boot.dev.
    Giữ lại: chữ cái (kể cả tiếng Việt có dấu), số, khoảng trắng,
    và các dấu câu cơ bản (. , ; : ! ? ( ) " ' / -)
    
    Ví dụ:
        "Điều 5.  Thời gian   học tập" → "Điều 5. Thời gian học tập"
        "SV phải đạt ≥ 2.00 ĐTBCTL™" → "SV phải đạt 2.00 ĐTBCTL"
    
    Args:
        text: Chuỗi text có thể chứa ký tự nhiễu
        
    Returns:
        Chuỗi plain text sạch
    """
    # Loại bỏ ký tự đặc biệt không mang ngữ nghĩa
    # \w bao gồm chữ cái Unicode (tiếng Việt), số, dấu gạch dưới
    text = re.sub(r'[^\w\s.,;:!?()\"\'/\-]', '', text)
    # Gộp khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
