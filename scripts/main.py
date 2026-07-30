import re

from gemini_client import ask_gemini
from telegram_sender import send_message
from telegram_receiver import get_new_messages
from prompt_builder import build_prompt
from progress_manager import load_progress, save_progress, bump_after_run, advance_stage, ROADMAP

STAGE_STATUS_PATTERN = re.compile(r"STAGE_STATUS:\s*(ADVANCE|STAY)\s*$", re.IGNORECASE)

progress = load_progress()

# 1. Đọc báo cáo mới từ Telegram (nếu học viên đã reply kể từ lần chạy trước)
print("Checking for new messages from Telegram...")
try:
    new_messages, max_update_id = get_new_messages(progress.get("last_update_id"))
except Exception as e:
    print(f"Không lấy được tin nhắn mới (bỏ qua, không chặn bot): {e}")
    new_messages, max_update_id = [], progress.get("last_update_id")

if new_messages:
    progress["last_report_raw"] = "\n---\n".join(new_messages)
    print(f"Tìm thấy {len(new_messages)} tin nhắn mới từ học viên.")
else:
    print("Không có báo cáo mới.")

if max_update_id is not None:
    progress["last_update_id"] = max_update_id

save_progress(progress)  # lưu report/update_id ngay, tránh mất nếu bước sau lỗi

# 2. Build prompt (đã bao gồm báo cáo + roadmap) và gọi Gemini
prompt = build_prompt()

print("Generating...")
raw_text = ask_gemini(prompt)
print(raw_text)

# 3. Tách marker STAGE_STATUS ra khỏi nội dung sẽ gửi cho học viên
match = STAGE_STATUS_PATTERN.search(raw_text.strip())
stage_status = match.group(1).upper() if match else "STAY"
display_text = raw_text[:match.start()].rstrip() if match else raw_text

# 4. Gửi tin nhắn cho học viên
send_message(display_text)

# 5. Cập nhật progress: stage, report đã dùng xong, day/streak
progress = load_progress()

if stage_status == "ADVANCE":
    old_stage = ROADMAP[progress["stage_index"]]
    progress = advance_stage(progress)
    new_stage = ROADMAP[progress["stage_index"]]
    if new_stage != old_stage:
        print(f"Stage advanced: {old_stage} -> {new_stage}")

progress["last_report_raw"] = ""  # đã dùng, xóa để không lặp lại vào ngày mai
progress["last_code_review"] = ""  # đã gộp vào bản tin sáng, xóa để tránh nhắc lại
progress = bump_after_run(progress)
save_progress(progress)

print(f"Done. Day {progress['day']}, streak {progress['streak']}, stage: {ROADMAP[progress['stage_index']]}.")