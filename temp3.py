import json
import re

text = """Th?i gian h?c t?p t?i ða cho phép ð? SV hoàn thành CTÐT ðý?c xác ð?nh theo b?ng dý?i ðây: Th?i gian thi?t k? c?a CTÐT Th?i gian h?c t?p t?i ða ð? SV hoàn thành CTÐT 4 nãm 8 nãm 4,5 nãm 9 nãm 5 nãm 10 nãm Nh?ng SV h?c liên thông (ngý?i có b?ng t?t nghi?p tr?nh ð? cao ð?ng h?nh th?c chính quy tr? lên; ngý?i ð? có b?ng t?t nghi?p tr?nh ð? ð?i h?c tr? lên) và nh?ng SV có k?t qu? h?c t?p ð? tích l?y t? m?t ngành ðào t?o ho?c m?t CTÐT khác, m?t khóa h?c khác ho?c t? m?t cõ s? ðào t?o khác ðý?c xem xét công nh?n, chuy?n ð?i sang TC c?a nh?ng h?c ph?n trong CTÐT theo h?c theo Quy ð?nh xét mi?n và công nh?n ði?m h?c ph?n trong CTÐT tr?nh ð? ð?i h?c h?nh th?c chính quy c?a Trý?ng ÐHCT. Ð?i v?i SV tuy?n sinh ðào t?o t? nãm h?c 2021 - 2022 (Khóa 47) tr? v? sau, kh?i lý?ng TC t?i ða ðý?c công nh?n, chuy?n ð?i không vý?t quá 50 kh?i lý?ng h?c t?p t?i thi?u c?a CTÐT và th?i gian t?i ða ð? nh?ng SV này hoàn thành khóa h?c ðý?c xác ð?nh trên cõ s? th?i gian theo k? ho?ch h?c t?p chu?n toàn khóa gi?m týõng ?ng v?i kh?i lý?ng TC ðý?c mi?n tr?, c? th? là m?i 9 TC ð?i v?i Khóa 49 tr? v? trý?c và 6 TC ð?i v?i Khóa 50 tr? v? sau ðý?c công nh?n và chuy?n ð?i th? th?i gian h?c t?p t?i ða ð? SV hoàn thành CTÐT gi?m týõng ?ng là 1 HK (ví d?: ðý?c công nh?n và chuy?n ð?i ít hõn 9 TC ð?i v?i Khóa 49 tr? v? trý?c và ít hõn 6 TC ð?i v?i Khóa"""

sentences = re.split(r'(?<=[.!?])\s+', text)
print(f"Num sentences: {len(sentences)}")
from woodpecker.core.chunker import chunk_with_overlap
chunks = chunk_with_overlap(sentences)
print(f"Num chunks: {len(chunks)}")
for i, c in enumerate(chunks):
    print(f"Chunk {i} tokens: {int(len(c.split())*1.3)}")
