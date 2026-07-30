from google import genai
from google.genai import errors, types
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_FALLBACK_CHAIN = [
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",   # alias, luôn trỏ tới bản Flash mới nhất
    "gemini-2.5-flash",
]

_grounding_tool = types.Tool(google_search=types.GoogleSearch())
_grounding_config = types.GenerateContentConfig(tools=[_grounding_tool])

RETRYABLE_CODES = (404, 429)  # 404 = model không tồn tại/deprecated, 429 = hết quota/rate limit


def _generate(model_name, prompt, use_grounding):
    config = _grounding_config if use_grounding else None
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=config,
    )
    return response.text


def ask_gemini(prompt, use_grounding=True):
    """
    use_grounding=True: dùng cho bản tin sáng (cần tin tức thật).
    use_grounding=False: dùng cho code review (không cần search, đỡ tốn quota grounding).
    """
    last_error = None

    if use_grounding:
        for model_name in MODEL_FALLBACK_CHAIN:
            try:
                return _generate(model_name, prompt, use_grounding=True)
            except errors.ClientError as e:
                if e.code in RETRYABLE_CODES:
                    print(f"[gemini_client] Model '{model_name}' lỗi {e.code} (có grounding), thử model kế tiếp...")
                    last_error = e
                    continue
                raise
        print("[gemini_client] Grounding thất bại ở mọi model, thử lại KHÔNG có Google Search...")

    for model_name in MODEL_FALLBACK_CHAIN:
        try:
            return _generate(model_name, prompt, use_grounding=False)
        except errors.ClientError as e:
            if e.code in RETRYABLE_CODES:
                print(f"[gemini_client] Model '{model_name}' lỗi {e.code} (không grounding), thử model kế tiếp...")
                last_error = e
                continue
            raise

    raise RuntimeError(
        f"Tất cả model đều thất bại. Lỗi cuối cùng: {last_error}"
    )