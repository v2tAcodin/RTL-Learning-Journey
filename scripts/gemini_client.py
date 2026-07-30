from google import genai
from google.genai import errors, types
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

# Thứ tự ưu tiên model. Nếu Google deprecate model nào, code vẫn chạy nhờ fallback.
MODEL_FALLBACK_CHAIN = [
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",   # alias, luôn trỏ tới bản Flash mới nhất
    "gemini-2.5-flash",
]

# Bật Google Search grounding để Gemini lấy tin tức/thông tin thật thay vì bịa
_grounding_tool = types.Tool(google_search=types.GoogleSearch())
_generation_config = types.GenerateContentConfig(tools=[_grounding_tool])


def ask_gemini(prompt):
    last_error = None

    for model_name in MODEL_FALLBACK_CHAIN:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=_generation_config,
            )
            return response.text
        except errors.ClientError as e:
            if e.code == 404:
                print(f"[gemini_client] Model '{model_name}' không dùng được (404), thử model kế tiếp...")
                last_error = e
                continue
            raise

    raise RuntimeError(
        f"Tất cả model trong fallback chain đều thất bại. Lỗi cuối cùng: {last_error}"
    )
