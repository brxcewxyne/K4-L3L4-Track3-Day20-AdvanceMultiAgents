"""GUIDE Phần 1 - Dựng tác tử (agent) bằng Deep Agents.   >>> SINH VIÊN CÀI ĐẶT make_backend VÀ build_agent <<<

Pseudo-code: guides/pseudocode/01_agent.md
Kiểm tra:    pytest tests/test_02_agent.py
"""
import base64
import os
import shlex
import sys
import uuid
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from langchain_openai import ChatOpenAI

from .model import make_model
from .subagents import get_subagents

# ---- CÓ SẴN, KHÔNG SỬA: system prompt dùng chung cho mọi sinh viên (để đường cơ sở so sánh được) ----
PATHS_NOTE = (
    "PATHS: every path is relative to the sandbox root and never starts with '/'. "
    "The task files are in the folder workspace/ (for example workspace/app.log). "
    "Use exactly this relative form both in the file tools and in the shell (execute); "
    "the shell starts in the sandbox root. "
)
BASE_PROMPT = (
    "You are an engineering assistant working in a sandbox. "
    + PATHS_NOTE
    + "Use the shell to run Python and tests. "
    "When you are done, reply with a short summary that mentions only files you really created or changed."
)
SKILLS_NOTE = (
    " Skills are in the folder skills/ (one sub-folder per skill with a SKILL.md). "
    "As your FIRST action, read the SKILL.md of every skill whose description could apply to the task, "
    "then follow them. Never modify skills/."
)
SUBAGENTS_NOTE = (
    " You have specialised subagents (see the description of the task tool). "
    "For anything beyond a trivial step, delegate to a suitable subagent and put ALL the task rules and file paths "
    "in the delegation message, because a subagent sees only what you send. "
    "Check what a subagent returns before you rely on it."
)
# --------------------------------------------------------------------------------------------------

# ---- Biên thực thi thật cho shell: Landlock (nhân Linux >= 5.13) --------------------------------
# LocalShellBackend.execute chạy `sh -c` không được cô lập. Mọi lệnh vì vậy được bọc trong một
# tiến trình nhỏ tự giới hạn hệ tệp bằng Landlock rồi mới exec shell. Quyền do hạt nhân ép buộc,
# không dựa vào lọc chuỗi lệnh, nên `cat` lẫn `python open()` ra ngoài sandbox đều bị EACCES.
_LANDLOCK_BOOTSTRAP = r'''
import base64, ctypes, errno, os, sys

cmd = base64.b64decode("__CMD_B64__").decode()
root = base64.b64decode("__ROOT_B64__").decode()

libc = ctypes.CDLL(None, use_errno=True)
SYS_CREATE, SYS_ADD, SYS_RESTRICT = 444, 445, 446
VERSION, RULE_PATH_BENEATH = 1, 1
PR_SET_NO_NEW_PRIVS = 38

def die(msg):
    sys.stderr.write("[sandbox] " + msg + "\n")
    os._exit(125)

if not sys.platform.startswith("linux"):
    die("Landlock sandbox requires Linux; refusing to run the shell unsandboxed")

abi = libc.syscall(SYS_CREATE, 0, 0, VERSION)
if abi < 1:
    die("Landlock unavailable (ABI < 1): refusing to run the shell unsandboxed")

EXECUTE, WRITE_FILE, READ_FILE, READ_DIR = 1, 2, 4, 8
REMOVE_DIR, REMOVE_FILE = 16, 32
MAKE_CHAR, MAKE_DIR, MAKE_REG, MAKE_SOCK = 64, 128, 256, 512
MAKE_FIFO, MAKE_BLOCK, MAKE_SYM, REFER = 1024, 2048, 4096, 8192
TRUNCATE = 16384

handled = (EXECUTE | WRITE_FILE | READ_FILE | READ_DIR | REMOVE_DIR | REMOVE_FILE
           | MAKE_CHAR | MAKE_DIR | MAKE_REG | MAKE_SOCK | MAKE_FIFO | MAKE_BLOCK | MAKE_SYM)
if abi >= 2:
    handled |= REFER
if abi >= 3:
    handled |= TRUNCATE

class RulesetAttr(ctypes.Structure):
    _fields_ = [("handled_access_fs", ctypes.c_uint64)]

ruleset = RulesetAttr(handled)
fd = libc.syscall(SYS_CREATE, ctypes.byref(ruleset), ctypes.sizeof(ruleset), 0)
if fd < 0:
    die("landlock_create_ruleset: " + errno.errorcode.get(ctypes.get_errno(), "?"))

class PathBeneath(ctypes.Structure):
    _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int32)]

def allow(path, access):
    try:
        pfd = os.open(path, os.O_PATH | os.O_CLOEXEC)
    except OSError:
        return
    try:
        rule = PathBeneath(access, pfd)
        if libc.syscall(SYS_ADD, fd, RULE_PATH_BENEATH, ctypes.byref(rule), 0) < 0:
            die("landlock_add_rule " + path + ": " + errno.errorcode.get(ctypes.get_errno(), "?"))
    finally:
        os.close(pfd)

for system_dir in ("/usr", "/bin", "/sbin", "/lib", "/lib64", "/opt"):
    allow(system_dir, EXECUTE | READ_FILE | READ_DIR)
allow("/etc", READ_FILE | READ_DIR)
allow("/var", READ_FILE | READ_DIR)
for device in ("/dev/null", "/dev/zero", "/dev/full", "/dev/random", "/dev/urandom", "/dev/tty"):
    allow(device, READ_FILE | WRITE_FILE)

sandbox_rights = (EXECUTE | WRITE_FILE | READ_FILE | READ_DIR | REMOVE_DIR | REMOVE_FILE
                  | MAKE_DIR | MAKE_REG | MAKE_SOCK | MAKE_FIFO | MAKE_SYM)
if abi >= 2:
    sandbox_rights |= REFER
if abi >= 3:
    sandbox_rights |= TRUNCATE
allow(root, sandbox_rights)

if libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:
    die("prctl(PR_SET_NO_NEW_PRIVS) failed")
if libc.syscall(SYS_RESTRICT, fd, 0) < 0:
    die("landlock_restrict_self: " + errno.errorcode.get(ctypes.get_errno(), "?"))

os.execv("/bin/sh", ["/bin/sh", "-c", cmd])
'''


def _sandboxed_command(command: str, sandbox: Path) -> str:
    """Đóng gói lệnh shell để chạy dưới Landlock; chỉ `sandbox` được đọc/ghi ngoài thư viện hệ thống."""
    code = (
        _LANDLOCK_BOOTSTRAP
        .replace("__CMD_B64__", base64.b64encode(command.encode("utf-8", "surrogateescape")).decode("ascii"))
        .replace("__ROOT_B64__", base64.b64encode(str(sandbox).encode("utf-8", "surrogateescape")).decode("ascii"))
    )
    return f"exec {shlex.quote(sys.executable)} -c {shlex.quote(code)}"


class _LandlockShell(LocalShellBackend):
    """LocalShellBackend với `execute` bị giới hạn thật bằng Landlock (không lọc chuỗi lệnh)."""

    def __init__(self, root_dir=None, **kwargs):
        super().__init__(root_dir=root_dir, **kwargs)
        self._sandbox_root = Path(self.cwd)

    def execute(self, command, *, timeout=None):
        if not isinstance(command, str) or not command:
            return super().execute(command, timeout=timeout)
        return super().execute(_sandboxed_command(command, self._sandbox_root), timeout=timeout)


class _ReasoningRoundTripChatOpenAI(ChatOpenAI):
    """ChatOpenAI giữ `reasoning_content` của DeepSeek qua các lượt tool call.

    ChatOpenAI bỏ trường `reasoning_content` khi dựng AIMessage và khi gửi lại lịch sử;
    DeepSeek ở thinking mode trả HTTP 400 nếu thiếu trường này sau một tool call.
    Adapter chỉ ghi thêm trường vào message assistant khi nó thực sự có mặt.
    """

    def _create_chat_result(self, response, generation_info=None):
        result = super()._create_chat_result(response, generation_info)
        raw = response if isinstance(response, dict) else response.model_dump(warnings=False)
        for generation, choice in zip(result.generations, raw.get("choices") or []):
            reasoning = (choice.get("message") or {}).get("reasoning_content")
            if reasoning:
                generation.message.additional_kwargs["reasoning_content"] = reasoning
        return result

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        if "messages" in payload:
            sources = self._convert_input(input_).to_messages()
            if len(sources) == len(payload["messages"]):
                for source, message in zip(sources, payload["messages"]):
                    reasoning = getattr(source, "additional_kwargs", {}).get("reasoning_content")
                    if reasoning and message.get("role") == "assistant":
                        message["reasoning_content"] = reasoning
        return payload


def make_backend(sandbox: Path):
    """Tạo backend (môi trường thực thi) cho tác tử.

    Yêu cầu:
      - Thư mục gốc (root_dir) là `sandbox`; đường dẫn tương đối `workspace/...` và `skills/...`
        phải dùng được ở CẢ công cụ tệp lẫn shell (shell chạy với thư mục làm việc = `sandbox`).
      - Tác tử chạy được lệnh shell và gọi được `python` (cần đặt PATH).
      - KHÔNG chuyển biến môi trường của bạn vào shell của tác tử (khóa API không được lộ).
    """
    sandbox = Path(sandbox).resolve()
    (sandbox / ".tmp").mkdir(parents=True, exist_ok=True)
    python_dir = str(Path(sys.executable).parent)
    env = {
        "PATH": os.pathsep.join([python_dir, "/usr/local/bin", "/usr/bin", "/bin"]),
        "HOME": str(sandbox),
        "TMPDIR": str(sandbox / ".tmp"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    return _LandlockShell(
        root_dir=sandbox,
        virtual_mode=True,
        inherit_env=False,
        env=env,
        timeout=120,
    )


def build_agent(sandbox: Path, mode: str = "single", use_skills: bool = False, model=None):
    """Tạo tác tử Deep Agents.

    Tham số:
      sandbox:    thư mục chứa `workspace/` (và `skills/` nếu có).
      mode:       "single"    -> tác tử mặc định (có subagent `general-purpose` sẵn của Deep Agents)
                  "subagents" -> thêm các subagent từ `get_subagents()` (nối PATHS_NOTE vào `system_prompt` của MỖI subagent,
                                 vì subagent không nhận BASE_PROMPT) và thêm SUBAGENTS_NOTE vào prompt chính
      use_skills: True -> nạp thư mục "/skills/" qua tham số `skills=` của create_deep_agent
                  và thêm SKILLS_NOTE vào prompt.
      model:      mô hình ngôn ngữ; None -> dùng `make_model()`.
    mode không hợp lệ -> ném ValueError.
    Trả về: đồ thị (graph) đã biên dịch, gọi bằng `.invoke({"messages": [...]})`.
    """
    if mode not in ("single", "subagents"):
        raise ValueError(f"unknown mode: {mode!r} (expected 'single' or 'subagents')")

    kwargs = {}
    prompt = BASE_PROMPT

    if mode == "subagents":
        kwargs["subagents"] = [
            {**sub, "system_prompt": sub["system_prompt"] + " " + PATHS_NOTE}
            for sub in get_subagents()
        ]
        prompt = prompt + SUBAGENTS_NOTE

    if use_skills:
        kwargs["skills"] = ["/skills/"]
        prompt = prompt + SKILLS_NOTE

    if model is None:
        model = make_model()
        # OpenCode Go yêu cầu x-opencode-session (một ID ổn định cho mỗi hội thoại)
        # và User-Agent không phải mặc định của thư viện.
        headers = dict(getattr(model, "default_headers", None) or {})
        headers.setdefault("x-opencode-session", os.getenv("OPENCODE_SESSION") or str(uuid.uuid4()))
        headers.setdefault("User-Agent", os.getenv("OPENCODE_USER_AGENT") or "lab-deepagents/0.1.0")
        model.default_headers = headers
        # ChatOpenAI/AzureChatOpenAI dựng HTTP client ngay trong hàm khởi tạo,
        # nên phải dựng lại client để header mới thực sự được gửi đi.
        if getattr(model, "root_client", None) is not None and hasattr(model, "validate_environment"):
            for attr in ("client", "root_client", "async_client", "root_async_client"):
                if hasattr(model, attr):
                    setattr(model, attr, None)
            model.validate_environment()
        # DeepSeek V4 bật thinking mặc định. Với OpenCode Go + DeepSeek, giữ thinking bật
        # và dùng adapter gửi lại `reasoning_content` qua các lượt tool call (LangChain bỏ
        # trường này nên API trả 400). Gateway khác giữ hành vi cũ: tắt thinking; Azure thật
        # không nhận tham số này.
        base_url = str(getattr(model, "openai_api_base", "") or "").lower()
        if "openai.azure.com" not in base_url and "cognitiveservices.azure.com" not in base_url:
            extra_body = dict(getattr(model, "extra_body", None) or {})
            model_name = str(getattr(model, "model_name", "") or "").lower()
            if "opencode" in base_url and "deepseek" in model_name and isinstance(model, ChatOpenAI):
                extra_body["thinking"] = {"type": "enabled"}
                model.extra_body = extra_body
                model.__class__ = _ReasoningRoundTripChatOpenAI
            else:
                extra_body.setdefault("thinking", {"type": "disabled"})
                model.extra_body = extra_body

    return create_deep_agent(
        model=model,
        system_prompt=prompt,
        backend=make_backend(sandbox),
        **kwargs,
    )
