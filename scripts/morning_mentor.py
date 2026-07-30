from google import genai
import os
import requests

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="""
Bạn là mentor RTL.

Viết bản hướng dẫn học hôm nay bằng tiếng Việt.

Bao gồm:

🌅 Tiến độ

🎯 Mục tiêu

📚 3 nhiệm vụ

💡 Một lời khuyên

⏱ Tổng thời gian khoảng 3-4 giờ.
"""
)

text = response.text

requests.post(
    f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage",
    data={
        "chat_id": os.environ["TELEGRAM_CHAT_ID"],
        "text": text
    }
)