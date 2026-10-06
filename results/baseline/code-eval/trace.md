### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Assistant
I'll start by exploring the workspace structure.

### Tool call: ls
{"path": "workspace"}

### Tool call: glob
{"pattern": "workspace/**/*.py"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/test_bookings.py']

### Tool call: read_file
{"file_path": "workspace/README.md"}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md"}

### Tool call: read_file
{"file_path": "workspace/bookings/__init__.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/timeutil.py"}

### Tool result
@@ lines 1-5 of 5 @@
# bookings

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 1.4.2
- initial import

### Tool result
@@ lines 1-1 of 1 @@
__version__ = "1.4.2"

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool call: read_file
{"file_path": "workspace/bookings/schedule.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "workspace/bookings/calendar_export.py"}

### Tool call: read_file
{"file_path": "workspace/tests/test_bookings.py"}

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool result
@@ lines 1-7 of 7 @@
"""Calendar export."""
from .timeutil import parse_duration


def slot_end(start_minute, duration_text):
    """Minute of the day at which a slot ends."""
    return start_minute + parse_duration(duration_text)

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -30"}

### Tool call: ls
{"path": "workspace"}

### Tool result
text = '2h'

    def parse_duration(text):
        """Convert a duration string to whole minutes (int).
    
        Supported formats:
          "1h30m" -> 90
          "2h"    -> 120
          "45m"   -> 45
          "1:30"  -> 90
          "45"    -> 45    # a bare number means minutes
        Surrounding whitespace is ignored.
        """
        m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
        if not m:
>           raise ValueError(f"bad duration: {text!r}")
E           ValueError: bad duration: '2h'

bookings/timeutil.py:18: ValueError
________________________ test_billable_blocks_rounds_up ________________________

>   ???
E   assert 1 == 2
E    +  where 1 = billable_blocks(20)

C:\Users\ASUS\Documents\AI thực chiến\K4-L3L4-Track3-Day20-AdvanceMultiAgents\tasks\code-eval\workspace\tests\test_bookings.py:10: AssertionError
=========================== short test summary info ============================
FAILED tests/test_bookings.py::test_total_minutes_mixed_formats - ValueError:...
FAILED tests/test_bookings.py::test_billable_blocks_rounds_up - assert 1 == 2
2 failed, 1 passed in 0.09s

[Command succeeded with exit code 0]

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: execute
{"command": "cd workspace && ls -la && ls -la .. && find . -type f | head -50"}

### Tool call: glob
{"pattern": "**/*.*"}

### Tool result
total 28
drwx------ 5 root root 4096 Oct  6 15:16 .
drwx------ 4 root root 4096 Oct  6 15:15 ..
drwxr-xr-x 3 root root 4096 Oct  6 15:16 .pytest_cache
-rwx------ 1 root root   60 Oct  6 05:15 CHANGELOG.md
-rwx------ 1 root root  123 Oct  6 05:15 README.md
drwx------ 3 root root 4096 Oct  6 05:36 bookings
drwx------ 3 root root 4096 Oct  6 05:36 tests
total 16
drwx------ 4 root root 4096 Oct  6 15:15 .
drwxrwxrwt 1 root root 4096 Oct  6 15:15 ..
drwxr-xr-x 2 root root 4096 Oct  6 15:16 .tmp
drwx------ 5 root root 4096 Oct  6 15:16 workspace
./tests/test_bookings.py
./tests/__pycache__/test_bookings.cpython-312-pytest-9.1.1.pyc
./README.md
./bookings/schedule.py
./bookings/__init__.py
./bookings/__pycache__/billing.cpython-312.pyc
./bookings/__pycache__/__init__.cpython-312.pyc
./bookings/__pycache__/timeutil.cpython-312.pyc
./bookings/__pycache__/calendar_export.cpython-312.pyc
./bookings/__pycache__/schedule.cpython-312.pyc
./bookings/calendar_export.py
./bookings/billing.py
./bookings/timeutil.py
./.pytest_cache/README.md
./.pytest_cache/.gitignore
./.pytest_cache/v/cache/lastfailed
./.pytest_cache/v/cache/nodeids
./.pytest_cache/CACHEDIR.TAG
./CHANGELOG.md

[Command succeeded with exit code 0]

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/__init__.cpython-312.pyc', '/workspace/bookings/__pycache__/billing.cpython-312.pyc', '/workspace/bookings/__pycache__/calendar_export.cpython-312.pyc', '/workspace/bookings/__pycache__/schedule.cpython-312.pyc', '/workspace/bookings/__pycache__/timeutil.cpython-312.pyc', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/__pycache__/test_bookings.cpython-312-pytest-9.1.1.pyc', '/workspace/tests/test_bookings.py']

### Assistant
Now I understand the three bugs. Let me fix them.

### Tool call: write_file
{"file_path": "workspace/bookings/timeutil.py", "content": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n_HOURS_MINUTES_RE = re.compile(r\"(\\d+)h(\\d+)m\")\n_HOURS_RE = re.compile(r\"(\\d+)h\")\n_MINUTES_RE = re.compile(r\"(\\d+)m\")\n_CLOCK_RE = re.compile(r\"(\\d+):(\\d+)\")\n_PLAIN_MINUTES_RE = re.compile(r\"(\\d+)\")\n\n\ndef parse_duration(text: str) -> int:\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    stripped = text.strip()\n    match = _HOURS_MINUTES_RE.fullmatch(stripped)\n    if match:\n        return int(match.group(1)) * 60 + int(match.group(2))\n    match = _HOURS_RE.fullmatch(stripped)\n    if match:\n        return int(match.group(1)) * 60\n    match = _MINUTES_RE.fullmatch(stripped)\n    if match:\n        return int(match.group(1))\n    match = _CLOCK_RE.fullmatch(stripped)\n    if match:\n        return int(match.group(1)) * 60 + int(match.group(2))\n    match = _PLAIN_MINUTES_RE.fullmatch(stripped)\n    if match:\n        return int(match.group(1))\n    raise ValueError(f\"bad duration: {text!r}\")\n"}

### Tool call: write_file
{"file_path": "workspace/bookings/billing.py", "content": "\"\"\"Billing rules.\"\"\"\nimport math\n\n\ndef billable_blocks(minutes: float, block: int = 15) -> int:\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    if minutes < 0:\n        raise ValueError(f\"minutes must be >= 0, got {minutes!r}\")\n    return math.ceil(minutes / block)\n"}

### Tool call: write_file
{"file_path": "workspace/bookings/schedule.py", "content": "\"\"\"Schedule helpers.\"\"\"\nfrom collections.abc import Iterable\n\nfrom .timeutil import parse_duration\n\n\ndef total_minutes(durations: Iterable[str]) -> int:\n    \"\"\"Total minutes of a list of duration strings.\"\"\"\n    return sum(parse_duration(d) for d in durations)\n\n\ndef add_slot(slot: str, slots: list[str] | None = None) -> list[str]:\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    return [*(slots or []), slot]\n"}

### Tool call: write_file
{"file_path": "workspace/bookings/calendar_export.py", "content": "\"\"\"Calendar export.\"\"\"\nfrom .timeutil import parse_duration\n\n\ndef slot_end(start_minute: int, duration_text: str) -> int:\n    \"\"\"Minute of the day at which a slot ends.\"\"\"\n    return start_minute + parse_duration(duration_text)\n"}

### Tool result
Updated file /workspace/bookings/timeutil.py

### Tool result
Updated file /workspace/bookings/billing.py

### Tool result
Updated file /workspace/bookings/schedule.py

### Tool result
Updated file /workspace/bookings/calendar_export.py

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -5 && python - <<'EOF'\nfrom bookings.timeutil import parse_duration\nfrom bookings.schedule import add_slot, total_minutes\nfrom bookings.billing import billable_blocks\nfrom bookings.calendar_export import slot_end\n\nfor t, exp in [(\"1h30m\",90),(\"2h\",120),(\"45m\",45),(\"1:30\",90),(\"45\",45),(\"  2h  \",120),(\"0h0m\",0),(\"90m\",90),(\"100\",100)]:\n    got = parse_duration(t)\n    assert got == exp, (t, got, exp)\nfor bad in [\"\", \"abc\", \"1h30\", \"h\", \"m\", \"1x\", \"-5\", \"1:2:3\"]:\n    try:\n        parse_duration(bad)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(f\"should raise: {bad!r}\")\nassert total_minutes([\"1h30m\",\"2h\"]) == 210\nassert add_slot(\"a\") == [\"a\"] and add_slot(\"b\") == [\"b\"]\nassert add_slot(\"c\", [\"a\", \"b\"]) == [\"a\",\"b\",\"c\"]\nbase = [\"x\"]\nadd_slot(\"y\", base)\nassert base == [\"x\"]\nassert billable_blocks(20)==2 and billable_blocks(45)==3 and billable_blocks(16)==2 and billable_blocks(15)==1 and billable_blocks(0)==0\ntry:\n    billable_blocks(-1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError(\"negative should raise\")\nassert slot_end(600, \"1h30m\") == 690\nprint(\"all spec checks ok\")\nEOF"}

### Tool result
...                                                                      [100%]
3 passed in 0.01s
all spec checks ok

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "cd workspace && (python -m ruff check bookings 2>&1 | tail -20); (python -m flake8 bookings 2>&1 | tail -20); python -m compileall -q bookings && echo compiled"}

### Tool result
/usr/local/bin/python: No module named ruff
/usr/local/bin/python: No module named flake8
compiled

[Command succeeded with exit code 0]

### Tool call: edit_file
{"file_path": "workspace/CHANGELOG.md", "old_string": "## Unreleased\n", "new_string": "## Unreleased\n- `parse_duration` now accepts every documented format (`\"2h\"`, `\"45m\"`, `\"1:30\"`, bare minutes).\n- `billable_blocks` rounds up instead of to the nearest block and rejects negative input.\n- `add_slot` no longer mutates a shared default list between calls.\n"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/CHANGELOG.md'

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -3"}

### Tool result
...                                                                      [100%]
3 passed in 0.01s

[Command succeeded with exit code 0]

### Assistant
All tests pass and the code now matches every docstring.

Files changed:

- `bookings/timeutil.py` — `parse_duration` only handled `"Nh Mm"`. Reimplemented it with per-format regexes so it supports all documented forms (`"2h"`, `"45m"`, `"1h30m"`, `"1:30"`, bare `"45"`), keeps ignoring surrounding whitespace, returns `int`, and still raises `ValueError` for anything unsupported.
- `bookings/billing.py` — `billable_blocks` used `round()`, which neither always rounds up (20 min → 1 block) nor validated input. It now uses `math.ceil(minutes / block)` and raises `ValueError` on negative `minutes`, per the docstring.
- `bookings/schedule.py` — `add_slot` mutated its mutable default argument (`slots=[]`), so separate calls shared state and callers' lists were modified. It now uses `slots=None` and returns a brand-new list, leaving the input untouched. Also added type hints and `total_minutes` annotations.
- `bookings/calendar_export.py` — behaviour was already correct; only added return/signature type hints for consistency.
- `CHANGELOG.md` — recorded the three fixes under `Unreleased`.

`tests/` was left untouched.