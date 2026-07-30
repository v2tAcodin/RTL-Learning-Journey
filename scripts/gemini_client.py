from google import genai
from google.genai import errors
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

# Thứ tự ưu tiên: model chính trước, model dự phòng sau.
# Nếu Google deprecate/đổi tên model nào đó, code vẫn chạy được nhờ fallback.
MODEL_FALLBACK_CHAIN = [
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",   # alias, luôn trỏ tới bản Flash mới nhất
    "gemini-2.5-flash",
]


def ask_gemini(prompt):
    last_error = None

    for model_name in MODEL_FALLBACK_CHAIN:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text
        except errors.ClientError as e:
            # 404 = model không tồn tại/bị deprecate -> thử model kế tiếp
            # Lỗi khác (401, 400...) thì raise luôn, thử model khác cũng vô ích
            if e.code == 404:
                print(f"[gemini_client] Model '{model_name}' không dùng được (404), thử model kế tiếp...")
                last_error = e
                continue
            raise

    raise RuntimeError(
        f"Tất cả model trong fallback chain đều thất bại. Lỗi cuối cùng: {last_error}"
    )
