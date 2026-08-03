from progress_manager import load_progress, ROADMAP, get_active_track, get_current_stage

TRACK_LABELS = {
    "rtl": "RTL/FPGA (SystemVerilog, ASIC-style digital design)",
    "embedded": "Embedded FPGA (NIOS II, C firmware, SoC integration)",
}


def _build_track_map_text(progress, track):
    stage_index = progress[f"stage_index_{track}"]
    lines = []
    for i, stage in enumerate(ROADMAP[track]):
        if i < stage_index:
            mark = "✅"
        elif i == stage_index:
            mark = "👉"
        else:
            mark = "⬜"
        lines.append(f"{mark} {stage}")
    return "\n".join(lines)


def _build_both_tracks_text(progress):
    blocks = []
    for track in ROADMAP:
        blocks.append(f"[{TRACK_LABELS[track]}]\n{_build_track_map_text(progress, track)}")
    return "\n\n".join(blocks)


def build_prompt():
    progress = load_progress()
    track = get_active_track()

    if progress.get("last_report_raw"):
        report_section = f"""
Báo cáo gần nhất từ học viên (dùng để đánh giá có nên chuyển sang stage tiếp theo hay không):
\"\"\"
{progress['last_report_raw']}
\"\"\"
"""
    else:
        report_section = "\nChưa có báo cáo mới nào từ học viên kể từ lần trước.\n"

    if progress.get("last_code_review"):
        code_review_section = f"""
Bản review code học viên đã push tối qua (đã review sẵn, DÙNG LẠI kết quả này, không tự review từ đầu):
\"\"\"
{progress['last_code_review']}
\"\"\"
"""
    else:
        code_review_section = "\nHọc viên chưa push code mới nào kể từ lần trước.\n"

    both_tracks_map = _build_both_tracks_text(progress)

    if track is not None:
        current_stage = get_current_stage(progress, track)
        track_label = TRACK_LABELS[track]
        track_instruction = f"""
HÔM NAY LÀ NGÀY HỌC CHUYÊN SÂU: {track_label}
Stage hiện tại của track này: {current_stage}

NHIỆM VỤ CỦA BẠN:

1. Dùng công cụ tìm kiếm để tìm 1-2 tin tức THỰC TẾ, mới, liên quan tới ngành bán dẫn/RTL/FPGA/RISC-V/embedded SoC
   có khả năng ảnh hưởng tới lộ trình học của học viên. Nếu không tìm được tin phù hợp, bỏ qua mục tin tức,
   TUYỆT ĐỐI không bịa tin.

2. Nếu có bản review code ở trên, tóm tắt lại điểm quan trọng nhất (đừng review lại từ đầu, review đã có sẵn rồi).

3. Dựa vào báo cáo của học viên VÀ bản review code (nếu có), đánh giá xem học viên đã đạt điều kiện chuyển
   sang stage tiếp theo CỦA TRACK "{track}" hay chưa. Chỉ coi là ĐẠT nếu: hoàn thành đúng chức năng, có
   testbench/verification tự kiểm tra (với embedded: firmware chạy đúng trên board/remote lab), corner case
   đều pass, không còn lỗi nghiêm trọng trong review. Nếu thiếu bất kỳ điều gì, GIỮ NGUYÊN stage và chỉ rõ
   điều còn thiếu.

4. Viết bằng tiếng Việt, giọng mentor kỹ thuật, thực dụng, không sáo rỗng.

Bao gồm các phần theo đúng thứ tự (bỏ qua phần nào không có dữ liệu tương ứng):

🗺️ Bản đồ tiến độ (cả 2 track)
{both_tracks_map}

🛠️ Nhận xét code đêm qua
(chỉ hiện mục này nếu có bản review code ở trên - tóm tắt ngắn gọn, không lặp lại toàn bộ)

📰 Bản tin công nghệ
(tin tức thật vừa tìm được kèm phân tích ảnh hưởng - hoặc bỏ qua nếu không có tin phù hợp)

🎯 Mục tiêu hôm nay (3-4 giờ) - track {track_label}
(nhiệm vụ cụ thể cho đúng stage hiện tại của track "{track}", có ước lượng thời gian)

📝 Bài kiểm tra cuối ngày
(2-3 câu hỏi kỹ thuật liên quan tới nội dung stage hôm nay)

📌 Cuối ngày, trả lời tin nhắn này với
(nhắc học viên reply: thời gian học, đã hoàn thành, test pass/fail, lỗi gặp, điều chưa hiểu.
Nếu có push code mới, cứ push - bot sẽ tự đọc vào 22h.)

QUAN TRỌNG: Kết thúc toàn bộ response bằng ĐÚNG 1 dòng cuối cùng, không thêm gì sau đó:
STAGE_STATUS: ADVANCE
hoặc
STAGE_STATUS: STAY
"""
    else:
        track_instruction = f"""
HÔM NAY KHÔNG PHẢI NGÀY HỌC CHUYÊN SÂU (chỉ Thứ 3 = RTL, Chủ nhật = Embedded).
Không đánh giá lên stage hôm nay, không giao mục tiêu nặng 3-4 giờ.

NHIỆM VỤ CỦA BẠN:

1. Dùng công cụ tìm kiếm để tìm 1 tin tức THỰC TẾ, mới, liên quan tới ngành bán dẫn/RTL/FPGA nếu có tin đáng
   chú ý. Nếu không có, bỏ qua mục này.

2. Nếu có bản review code ở trên, tóm tắt ngắn gọn.

3. Không đánh giá chuyển stage hôm nay (giữ nguyên mọi track).

4. Viết bằng tiếng Việt, giọng mentor kỹ thuật, ngắn gọn, động viên nhẹ.

Bao gồm các phần theo đúng thứ tự (bỏ qua phần nào không có dữ liệu tương ứng):

🗺️ Bản đồ tiến độ (cả 2 track)
{both_tracks_map}

🛠️ Nhận xét code đêm qua
(chỉ hiện nếu có bản review code ở trên)

📰 Bản tin công nghệ
(nếu có tin đáng chú ý)

📚 Hôm nay: tập trung việc trường
(nhắc ngắn gọn hôm nay ưu tiên bài vở trên trường / ôn thi, không giao bài tập RTL/embedded mới. Nếu có thời
gian rảnh, có thể ôn nhẹ lại nội dung stage đang học của track gần nhất, không bắt buộc.)

📌 Cuối ngày, trả lời tin nhắn này với
(nhắc học viên: nếu có push code mới thì cứ push, bot vẫn tự đọc vào 22h.)

QUAN TRỌNG: Kết thúc toàn bộ response bằng ĐÚNG 1 dòng cuối cùng, không thêm gì sau đó:
STAGE_STATUS: STAY
"""

    return f"""
Bạn là mentor RTL/Embedded FPGA của một sinh viên năm 3-4 ngành Computer Engineering,
định hướng RTL/FPGA/SoC kết hợp Embedded (hardware RTL + software firmware).

TRẠNG THÁI HỌC TẬP:
- Ngày học liên tục: {progress['day']}
- Streak: {progress['streak']} ngày
{report_section}
{code_review_section}
{track_instruction}
"""
