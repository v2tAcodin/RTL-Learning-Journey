import os
import requests

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

prompt = """
Bạn là mentor RTL.

Người học đang theo lộ trình:
- Verilog
- FPGA
- CPU RISC-V
- Design Verification

Hãy tạo task học hôm nay bằng tiếng Việt.

Format:

🌅 RTL Morning Mentor

🎯 Mục tiêu

📚 3 việc cần làm

💡 1 lời khuyên

⏱ Khoảng 3-4 giờ học.
"""

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

response = requests.post(
    url,
    json={
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    },
)

text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": text
    }
)