from progress_manager import load_progress, save_progress
from code_reviewer import review_pushed_code
from telegram_sender import send_message

progress = load_progress()

print("Checking projects/ for new Verilog files...")
progress, has_review = review_pushed_code(progress)
save_progress(progress)

if has_review:
    print("Code review hoàn tất, đã lưu vào progress.json.")
    try:
        send_message(
            "🌙 Đã nhận code Verilog bạn vừa push. "
            "Review chi tiết sẽ có trong bản tin sáng mai lúc 8h."
        )
    except Exception as e:
        # Không để lỗi gửi Telegram làm fail cả job - review đã lưu thành công rồi
        print(f"Gửi tin nhắn xác nhận thất bại (bỏ qua): {e}")
else:
    print("Không có file Verilog nào mới trong projects/ kể từ lần review trước. Bỏ qua.")

print("Done.")