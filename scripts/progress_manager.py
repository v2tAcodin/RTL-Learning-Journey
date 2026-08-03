import json
import os
from datetime import date, timedelta

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "..", "progress.json")

# 2 track song song, tiến độ theo dõi độc lập:
# - "rtl": học vào Thứ 3
# - "embedded": học vào Chủ nhật
# Muốn đổi ngày active thì sửa get_active_track() bên dưới.
ROADMAP = {
    "rtl": [
        "SystemVerilog cơ bản",
        "Combinational + Sequential Logic",
        "Generate / Module Instantiation",
        "ALU + Self-checking Testbench",
        "FIFO",
        "UART",
        "Synthesis + Timing",
        "FPGA Bring-up",
        "RISC-V CPU",
    ],
    "embedded": [
        "Qsys/Platform Designer + NIOS II Integration",
        "C Firmware Bare-metal (Nios II EDS)",
        "Custom IP Core + Avalon-MM Driver",
        "SoC Debug & HW/SW Co-verification",
    ],
}

TRACKS = list(ROADMAP.keys())

DEFAULT_PROGRESS = {
    "day": 1,
    "streak": 1,
    "stage_index_rtl": 3,       # mặc định: đang ở ALU + Self-checking Testbench
    "stage_index_embedded": 0,  # mặc định: chưa bắt đầu track embedded
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
        # đảm bảo stage_index của mỗi track luôn hợp lệ dù ROADMAP có đổi độ dài
        for track in TRACKS:
            key = f"stage_index_{track}"
            merged[key] = max(0, min(merged[key], len(ROADMAP[track]) - 1))
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


def get_active_track(today=None):
    """
    Thứ 3 -> 'rtl', Chủ nhật -> 'embedded'.
    Các ngày khác trả về None (không đẩy stage mới, chỉ ôn/review nhẹ).
    date.weekday(): 0=Thứ 2, 1=Thứ 3, 2=Thứ 4, 3=Thứ 5, 4=Thứ 6, 5=Thứ 7, 6=Chủ nhật
    """
    d = today or date.today()
    weekday = d.weekday()
    if weekday == 1:
        return "rtl"
    elif weekday == 6:
        return "embedded"
    return None


def get_current_stage(progress, track):
    stage_index = progress[f"stage_index_{track}"]
    return ROADMAP[track][stage_index]


def advance_stage(progress, track):
    key = f"stage_index_{track}"
    if progress[key] < len(ROADMAP[track]) - 1:
        progress[key] += 1
    return progress
