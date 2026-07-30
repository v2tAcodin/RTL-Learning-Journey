# 🤖 RTL Morning Mentor

Bot Telegram tự động đóng vai **mentor cá nhân cho hành trình học RTL/FPGA/SoC**. Bot theo dõi tiến độ học, review code Verilog bạn push lên GitHub, tổng hợp tin tức bán dẫn thật, và mỗi sáng gửi cho bạn kế hoạch học tập cụ thể cho ngày hôm đó.

---

## 🎯 Mục đích

Tự học RTL một mình rất dễ rơi vào 2 vấn đề:
- **Không biết mình đang ở đâu** trong lộ trình, học lan man không theo trình tự
- **Không ai review code**, viết sai thói quen (latch, blocking/non-blocking sai chỗ...) mà không biết

Bot này giải quyết bằng cách đóng vai một mentor thật:
- Luôn biết chính xác bạn đang ở giai đoạn nào
- Đọc code bạn push và chỉ ra lỗi trước khi bạn tự tin sai
- Chỉ cho bạn chuyển sang phần tiếp theo khi đã thực sự đạt yêu cầu, không phải "cảm thấy xong"

---

## ✨ Chức năng chính

| Chức năng | Mô tả |
|---|---|
| 🗺️ **Theo dõi lộ trình** | Bot nhớ bạn đang ở stage nào (VD: ALU, FIFO, UART...), tự động đánh dấu ✅ khi hoàn thành |
| 🛠️ **Review code tự động** | Mỗi tối, bot đọc code Verilog bạn push trong `projects/`, chỉ ra lỗi latch, sai blocking/non-blocking, style... |
| 📰 **Tin tức bán dẫn thật** | Bot tìm tin tức RTL/FPGA/RISC-V thật (qua Google Search), không bịa, chỉ đưa nếu thực sự liên quan |
| 📝 **Đánh giá tiến độ** | Dựa trên báo cáo bạn gửi + kết quả review code, bot tự quyết định bạn đã đủ điều kiện qua bài mới chưa |
| 💬 **Giao tiếp 2 chiều** | Bạn reply thẳng vào Telegram để báo cáo, bot đọc và phản hồi vào sáng hôm sau |

---

## 🕐 Bot chạy như thế nào trong 1 ngày

```
Bạn code Verilog cả ngày, push lên GitHub bất cứ lúc nào
                    │
                    ▼
   22:00 (giờ VN)  ──►  Bot tự động đọc code mới push trong projects/
                        Gửi Gemini review, lưu kết quả
                        Gửi Telegram 1 dòng xác nhận "đã nhận code"
                    │
Bạn có thể reply Telegram báo cáo cuối ngày (thời gian học, test pass/fail...)
                    │
                    ▼
   08:00 (giờ VN)  ──►  Bot tổng hợp: review code tối qua + báo cáo bạn gửi
                        + tin tức bán dẫn thật + lộ trình hiện tại
                        → Gửi bản tin buổi sáng đầy đủ
                        → Tự quyết định: giữ nguyên stage hay cho qua bài mới
```

Bạn **không cần làm gì thêm** ngoài việc code và push. Bot tự chạy theo lịch.

---

## 🗺️ Lộ trình hiện tại

```
✅ SystemVerilog cơ bản
✅ Combinational + Sequential Logic
✅ Generate / Module Instantiation
👉 ALU + Self-checking Testbench   ← đang ở đây
⬜ FIFO
⬜ UART
⬜ Synthesis + Timing
⬜ FPGA Bring-up
⬜ RISC-V CPU
```

Muốn đổi lộ trình (thêm/bớt/sắp xếp lại giai đoạn)? Sửa list `ROADMAP` trong `scripts/progress_manager.py`.

---

## 📂 Cấu trúc repo

```
RTL-Learning-Journey/
├── progress.json              # "Bộ nhớ" của bot: ngày học, streak, stage, review gần nhất
├── projects/                  # Code Verilog của bạn - bot chỉ đọc file trong đây
├── .github/workflows/
│   ├── telegram_bot.yml       # Job 8h sáng - gửi bản tin
│   └── evening_review.yml     # Job 22h tối - review code
└── scripts/
    ├── main.py                # Entry point buổi sáng
    ├── run_evening_review.py  # Entry point buổi tối
    ├── gemini_client.py       # Gọi Gemini API (có fallback model + grounding)
    ├── code_reviewer.py       # Logic phát hiện & review code mới
    ├── prompt_builder.py      # Ghép prompt gửi Gemini
    ├── progress_manager.py    # Đọc/ghi progress.json, định nghĩa lộ trình
    ├── telegram_sender.py     # Gửi tin nhắn Telegram
    ├── telegram_receiver.py   # Đọc tin nhắn báo cáo từ bạn
    └── config.py               # Đọc secrets từ biến môi trường
```

---

## ⚙️ Hướng dẫn cài đặt (setup từ đầu)

### 1. Tạo Telegram Bot
1. Chat với [@BotFather](https://t.me/BotFather) trên Telegram → `/newbot` → lấy `TELEGRAM_BOT_TOKEN`
2. Nhắn 1 tin bất kỳ cho bot vừa tạo, sau đó mở `https://api.telegram.org/bot<TOKEN>/getUpdates` để lấy `TELEGRAM_CHAT_ID` (số trong `"chat":{"id": ...}`)

### 2. Lấy Gemini API Key
1. Vào [Google AI Studio](https://aistudio.google.com) → **API keys** → tạo key mới → lấy `GEMINI_API_KEY`
2. Vào **Projects** → chọn project vừa tạo → **Configure billing** → link thẻ (không mất phí nếu dùng đúng mục đích 1 lần/ngày như bot này — xem phần Chi phí bên dưới)

### 3. Cấu hình GitHub repo
1. **Settings → Secrets and variables → Actions** → thêm 3 secret:
   - `GEMINI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
2. **Settings → Actions → General → Workflow permissions** → chọn **"Read and write permissions"** (bắt buộc, để bot tự commit lại `progress.json`)

### 4. Test thử
Vào tab **Actions** trên GitHub → chọn workflow "RTL Morning Mentor" hoặc "RTL Evening Code Review" → **Run workflow** để chạy tay, kiểm tra Telegram có nhận được tin nhắn không trước khi để cron tự chạy.

---

## 📱 Hướng dẫn sử dụng hàng ngày

1. **Code như bình thường**, để file `.v`/`.sv` trong thư mục `projects/`
2. **Push lên GitHub** bất cứ lúc nào trong ngày (không cần đúng giờ)
3. **22h**: nhận tin nhắn ngắn xác nhận bot đã đọc code
4. **8h sáng hôm sau**: nhận bản tin đầy đủ — gồm nhận xét code, tin tức, mục tiêu hôm nay, bài kiểm tra
5. **Cuối ngày**, reply thẳng vào tin nhắn bot trên Telegram theo mẫu:
   ```
   Thời gian học: 3.5 giờ
   Đã hoàn thành: ALU xong, testbench 15/15 test pass
   Kết quả lint: sạch, không warning
   Lỗi gặp: nhầm blocking/non-blocking ở dòng cộng carry
   Điều chưa hiểu: vì sao SRA cần ép kiểu signed
   ```
   Bot sẽ đọc báo cáo này vào lần chạy kế tiếp để quyết định có cho bạn qua bài mới không.

---

## 🔧 Troubleshooting

| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| `404 NOT_FOUND` (model) | Google deprecate model | Đã có fallback tự động sang model khác, nhưng nếu vẫn lỗi, cập nhật `MODEL_FALLBACK_CHAIN` trong `gemini_client.py` |
| `429 RESOURCE_EXHAUSTED` | Hết quota API | Kiểm tra đã bật billing chưa (AI Studio → Projects → Configure billing) |
| Bot không nhớ tiến độ, luôn reset | `progress.json` không được commit lại | Kiểm tra Workflow permissions đã để "Read and write" chưa |
| Bot không đọc code mới push | File không nằm trong `projects/`, hoặc sai đuôi file | Chỉ nhận `.v`, `.sv`, `.vh`, `.svh` trong đúng thư mục `projects/` |
| Không nhận được tin nhắn báo cáo | Chưa từng nhắn tin cho bot trước đó | Telegram bot chỉ đọc được tin nhắn nếu bạn đã chủ động chat với nó ít nhất 1 lần |

---

## 💰 Chi phí vận hành

Với tần suất 1 lần sáng + 1 lần tối mỗi ngày:
- **Token Gemini**: vài trăm đồng/tháng, không đáng kể
- **Grounding (tin tức)**: ~30 query/tháng, trong hạn mức **5.000 query miễn phí/tháng**
- **Tổng chi phí thực tế**: **$0/tháng**, miễn không chạy lặp bất thường (bug loop)

Khuyến nghị đặt **Budget alert** trong Google Cloud Billing ở mức thấp (VD $2) để được cảnh báo nếu có gì bất thường.