import json
import os
from datetime import date, timedelta

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "..", "progress.json")

# Lộ trình cố định. Muốn thêm/bớt stage thì sửa list này.
# stage_index trong progress.json trỏ vào vị trí hiện tại trong list.
ROADMAP = [
    "SystemVerilog cơ bản",
    "Combinational + Sequential Logic",
    "Generate / Module Instantiation",
    "ALU + Self-checking Testbench",
    "FIFO",
    "UART",
    "Synthesis + Timing",
    "FPGA Bring-up",
    "RISC-V CPU",
]

DEFAULT_PROGRESS = {
    "day": 1,
    "streak": 1,
    "stage_index": 3,  # mặc định: đang ở ALU + Self-checking Testbench
    "last_run_date": None,
    "last_update_id": None,
    "last_report_raw": "",
    "last_reviewed_commit": None,
    "last_code_review": "",
}


def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return dict(DEFAULT_PROGRESS)
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_PROGRESS)
        merged.update(data)
        # đảm bảo stage_index luôn hợp lệ dù ROADMAP có thay đổi độ dài
        merged["stage_index"] = max(0, min(merged["stage_index"], len(ROADMAP) - 1))
        return merged
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_PROGRESS)


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def bump_after_run(progress):
    """Tăng day/streak theo ngày thực tế, reset streak nếu bị đứt quãng."""
    today = date.today()
    last_run = progress.get("last_run_date")

    if last_run is None:
        progress["streak"] = 1
    else:
        last_run_date = date.fromisoformat(last_run)
        if last_run_date == today:
            return progress
        elif last_run_date == today - timedelta(days=1):
            progress["streak"] = progress.get("streak", 0) + 1
        else:
            progress["streak"] = 1
        progress["day"] = progress.get("day", 0) + 1

    progress["last_run_date"] = today.isoformat()
    return progress


def advance_stage(progress):
    if progress["stage_index"] < len(ROADMAP) - 1:
        progress["stage_index"] += 1
    return progress