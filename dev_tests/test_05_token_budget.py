"""Offline: ngân sách token phải dừng được cả subagent đang lặp (zero token)."""
import json

from langchain_core.messages import AIMessage

from lab.runner import run_task
from lab.subagents import get_subagents
from lab.testing import ScriptedChatModel

MAX_TOKENS = 300
PER_CALL = 120  # ScriptedChatModel báo 100 input + 20 output mỗi lần gọi


def test_budget_stops_a_looping_subagent(tmp_path):
    task_call = AIMessage(content="", tool_calls=[{
        "name": "task",
        "args": {"description": "inspect the workspace", "subagent_type": get_subagents()[0]["name"]},
        "id": "t1",
    }])
    loop_call = AIMessage(content="", tool_calls=[{
        "name": "execute",
        "args": {"command": "ls workspace"},
        "id": "l1",
    }])
    rec = run_task("data-learn", "baseline", results_dir=tmp_path,
                   model=ScriptedChatModel(script=[task_call, loop_call]),
                   recursion_limit=60, max_tokens=MAX_TOKENS)

    assert "TokenLimitExceeded" in (rec["error"] or "")
    assert rec["subagent_calls"] == 1 and rec["tool_calls"] >= 1
    # Dừng ngay: tối đa một response vượt ngưỡng, không chạy tới recursion limit.
    assert MAX_TOKENS < rec["tokens"]["total"] <= MAX_TOKENS + PER_CALL
    assert rec["total"] >= 5 and rec["checks"]  # sandbox vẫn được chấm

    out = tmp_path / "baseline" / "data-learn"
    saved = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert saved["error"] == rec["error"] and saved["checks"] == rec["checks"]
    trace = (out / "trace.md").read_text(encoding="utf-8")
    assert trace.strip() and "task" in trace
