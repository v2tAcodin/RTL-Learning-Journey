import requests
from config import BOT_TOKEN


def get_new_messages(last_update_id):
    """
    Lấy các tin nhắn text mới mà học viên đã gửi cho bot, kể từ last_update_id.
    Trả về (list các đoạn text, update_id lớn nhất đã thấy).
    Nếu không có gì mới: ([], last_update_id không đổi).
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 0}
    if last_update_id is not None:
        params["offset"] = last_update_id + 1

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    messages = []
    max_update_id = last_update_id

    for update in data.get("result", []):
        update_id = update["update_id"]
        if max_update_id is None or update_id > max_update_id:
            max_update_id = update_id

        message = update.get("message")
        if message and "text" in message:
            messages.append(message["text"])

    return messages, max_update_id
