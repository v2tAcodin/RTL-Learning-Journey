import subprocess
from pathlib import Path

from gemini_client import ask_gemini

VERILOG_EXTENSIONS = {".v", ".sv", ".vh", ".svh"}
CPP_EXTENSIONS = {".cpp", ".hpp", ".h", ".cc"}
REVIEWABLE_EXTENSIONS = VERILOG_EXTENSIONS | CPP_EXTENSIONS



PROJECTS_DIR = "projects"


def get_current_commit():
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def get_changed_verilog_files(last_commit):
    """
    Trả về list đường dẫn file Verilog trong projects/ đã thêm/sửa kể từ last_commit tới HEAD.
    Nếu last_commit là None hoặc không còn trong lịch sử git (vd force-push), fallback về
    liệt kê TOÀN BỘ file Verilog hiện có trong projects/ (coi như lần review đầu tiên).
    """
    files = None

    if last_commit:
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACM",
                 last_commit, "HEAD", "--", PROJECTS_DIR],
                capture_output=True, text=True, check=True,
            )
            files = [f for f in result.stdout.splitlines() if f]
        except subprocess.CalledProcessError:
            files = None  # commit cũ không còn -> fallback bên dưới

    if files is None:
        files = [
            str(p) for p in Path(PROJECTS_DIR).rglob("*")
            if p.is_file() and p.suffix in VERILOG_EXTENSIONS
        ]

    return [f for f in files if Path(f).suffix in VERILOG_EXTENSIONS and Path(f).exists()]


def _build_review_prompt(file_contents):
    files_block = "\n\n".join(
        f"--- {path} ---\n{content}" for path, content in file_contents.items()
    )
    return f"""
Bạn là kỹ sư RTL senior đang review code cho một sinh viên năm 3 định hướng RTL/FPGA/SoC.

Dưới đây là các file Verilog/SystemVerilog vừa được cập nhật:

{files_block}

Hãy review NGẮN GỌN, tập trung vào:
- Lỗi cú pháp hoặc logic rõ ràng
- Nguy cơ inferred latch (thiếu else/default trong always_comb hoặc always @*)
- Blocking (=) vs non-blocking (<=) dùng sai chỗ
- Multiple driver, floating signal, sensitivity list thiếu
- Style: naming, reset convention (sync/async), có tuân thủ coding guideline synthesizable không

Định dạng trả lời:
- Nếu code ổn: nói ngắn gọn "Code ổn, không phát hiện vấn đề nghiêm trọng" kèm tối đa 2 góp ý nhỏ nếu có.
- Nếu có lỗi: liệt kê từng lỗi - file nào, vấn đề gì, cách sửa. Ngắn gọn, không diễn giải dài dòng.
- Không in lại toàn bộ code, không lặp lại nội dung file.
"""


def review_pushed_code(progress):
    """
    Kiểm tra và review code Verilog mới trong projects/.
    Trả về (progress đã cập nhật, has_new_review: bool).
    """
    last_commit = progress.get("last_reviewed_commit")
    current_commit = get_current_commit()

    changed_files = get_changed_verilog_files(last_commit)

    if not changed_files:
        progress["last_reviewed_commit"] = current_commit
        return progress, False

    file_contents = {}
    for path in changed_files:
        try:
            file_contents[path] = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"Bỏ qua file không đọc được ({path}): {e}")

    if not file_contents:
        progress["last_reviewed_commit"] = current_commit
        return progress, False

    prompt = _build_review_prompt(file_contents)
    review_text = ask_gemini(prompt, use_grounding=False)

    progress["last_code_review"] = review_text
    progress["last_reviewed_commit"] = current_commit
    return progress, True