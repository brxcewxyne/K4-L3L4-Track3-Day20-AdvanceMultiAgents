"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import os
import re
import uuid
from pathlib import Path

from .model import make_model
from .tasks import ROOT, eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def _default_model():
    """make_model() + thiết lập OpenCode Go (header phiên, thinking). Chỉ dùng khi model=None."""
    model = make_model()
    base_url = str(getattr(model, "openai_api_base", "") or "").lower()
    if hasattr(model, "default_headers"):
        headers = dict(getattr(model, "default_headers", None) or {})
        headers.setdefault("x-opencode-session", os.getenv("OPENCODE_SESSION") or str(uuid.uuid4()))
        headers.setdefault("User-Agent", os.getenv("OPENCODE_USER_AGENT") or "lab-deepagents/0.1.0")
        model.default_headers = headers
        if getattr(model, "root_client", None) is not None and hasattr(model, "validate_environment"):
            for attr in ("client", "root_client", "async_client", "root_async_client"):
                if hasattr(model, attr):
                    setattr(model, attr, None)
            model.validate_environment()
    if hasattr(model, "extra_body") and "openai.azure.com" not in base_url and "cognitiveservices.azure.com" not in base_url:
        extra_body = dict(getattr(model, "extra_body", None) or {})
        model_name = str(getattr(model, "model_name", "") or "").lower()
        if "opencode" in base_url and "deepseek" in model_name:
            extra_body["thinking"] = {"type": "enabled"}
        else:
            extra_body.setdefault("thinking", {"type": "disabled"})
        model.extra_body = extra_body
    return model


_PROMPT = """You write SKILLs for a coding and data-analysis agent.
Below are the failed checks (names and the review bot's feedback) and the traces of the learning runs.
Find the common PROCESS mistakes (not specific answers) and write at most {max_skills} short skills
that help avoid them on NEW tasks of the same kind.

Rules:
- A skill must be general: no task ids, no task-specific file names, no answers or numbers.
- Each skill has YAML frontmatter with `name` (lower case, dashes) and `description` (one sentence: WHEN to use it),
  then at most 40 lines of imperative checklist instructions.
- Output format, exactly:
=== SKILL: <name> ===
---
name: <name>
description: <when to use>
---
<content>
=== END ===

{runs}
"""


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    out_dir = Path(out_dir) if out_dir is not None else ROOT / "skills" / "auto"

    runs = []
    for run_file in sorted((Path(results_dir) / source_condition).glob("*/run.json")):
        data = json.loads(run_file.read_text(encoding="utf-8"))
        if data.get("role") != "learn":
            continue  # tuyệt đối không dùng dữ liệu tác vụ đánh giá
        failed = [(c["name"], c.get("detail", "")) for c in data.get("checks", []) if not c.get("passed")]
        if not failed:
            continue
        trace_file = run_file.with_name("trace.md")
        trace = trace_file.read_text(encoding="utf-8")[-6000:] if trace_file.exists() else ""
        runs.append({
            "task": data.get("task", run_file.parent.name),
            "condition": data.get("condition", source_condition),
            "failed": failed,
            "trace": trace,
        })

    if not runs:
        print("không có check thất bại ở tác vụ học; không gọi mô hình")
        return []

    sections = []
    for run in runs:
        lines = [f"=== RUN: {run['task']} (condition: {run['condition']}) ===", "Failed checks:"]
        lines += [f"- {name}: {detail}" for name, detail in run["failed"]]
        lines += ["Trace (tail):", run["trace"]]
        sections.append("\n".join(lines))
    prompt = _PROMPT.format(max_skills=max_skills, runs="\n\n".join(sections))

    if model is None:
        model = _default_model()
    reply = model.invoke(prompt).content

    written = []
    for name, text in parse_skill_blocks(reply):
        if len(written) >= max_skills:
            break
        if validate_skill(text, expected_name=name):
            continue
        dest = out_dir / name / "SKILL.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        written.append(dest)
    return written


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
