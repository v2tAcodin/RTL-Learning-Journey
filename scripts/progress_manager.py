import json
import os
from datetime import date, timedelta

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "progress.json")

DEFAULT_PROGRESS = {
    "day": 1,
    "streak": 1,
    "current_module": "Đang xác định module đầu tiên",
    "last_blocker": "Chưa có",
    "last_completed": "Chưa có dữ liệu",
    "last_run_date": None,
}


def load_progress():
    """Đọc progress.json. Nếu file lỗi/không tồn tại, trả về default."""
    if not os.path.exists(PROGRESS_FILE):
        return dict(DEFAULT_PROGRESS)
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # đảm bảo đủ field, tránh KeyError nếu file cũ thiếu key mới
        merged = dict(DEFAULT_PROGRESS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_PROGRESS)


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def bump_after_run(progress):
    """
    Gọi sau khi bot đã gửi tin nhắn thành công.
    - Tăng day mỗi lần chạy (1 lần/ngày theo cron).
    - Tăng streak nếu lần chạy trước là hôm qua.
    - Reset streak về 1 nếu bị đứt quãng (bỏ lỡ >=1 ngày).
    - Không đổi gì nếu lỡ chạy 2 lần trong cùng 1 ngày.
    """
    today = date.today()
    last_run = progress.get("last_run_date")

    if last_run is None:
        progress["streak"] = 1
    else:
        last_run_date = date.fromisoformat(last_run)
        if last_run_date == today:
            # đã chạy hôm nay rồi, không tính thêm ngày/streak
            return progress
        elif last_run_date == today - timedelta(days=1):
            progress["streak"] = progress.get("streak", 0) + 1
        else:
            progress["streak"] = 1  # đứt streak
        progress["day"] = progress.get("day", 0) + 1

    progress["last_run_date"] = today.isoformat()
    return progress


def update_fields(progress, **fields):
    """Cập nhật thủ công các field như current_module, last_blocker, last_completed."""
    for key, value in fields.items():
        if key in progress:
            progress[key] = value
    return progress
