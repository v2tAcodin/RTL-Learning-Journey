from gemini_client import ask_gemini
from telegram_sender import send_message
from prompt_builder import build_prompt
from progress_manager import load_progress, save_progress, bump_after_run

progress = load_progress()
prompt = build_prompt()

print("Generating...")

text = ask_gemini(prompt)

print(text)

send_message(text)

# Chỉ cập nhật progress SAU KHI gửi thành công, tránh lệch trạng thái nếu lỗi giữa chừng
progress = bump_after_run(progress)
save_progress(progress)

print(f"Done. Day {progress['day']}, streak {progress['streak']}.")
