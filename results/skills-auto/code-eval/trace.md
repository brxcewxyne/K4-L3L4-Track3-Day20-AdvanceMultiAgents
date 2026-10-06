### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Assistant
I'll start by reading the skill files that could apply.

### Tool call: read_file
{"file_path": "/skills/output-contract-checklist/SKILL.md", "limit": 1000}

### Tool call: read_file
{"file_path": "/skills/reproduce-exact-spec-strings/SKILL.md", "limit": 1000}

### Tool result
@@ lines 1-12 of 12 @@
---
name: output-contract-checklist
description: Use before finishing any task that must deliver files or structured output, to verify every explicit requirement is met.
---
- Re-read the task text and list every explicit deliverable: file paths, top-level objects/keys, required fields, units, naming rules, sort order, and value formats.
- For structured output (JSON/CSV), confirm required parent/meta objects and headers exist, not only the data fields you computed.
- Confirm units and types match the request (minor vs major units, int vs float, string formats) and convert when needed.
- Confirm required ordering (sort keys and direction) is applied to the final output, not just to intermediate steps.
- Confirm required naming/casing/character normalization is applied to every emitted value.
- Check for extra artifacts the task also demands (cleaned data file, changelog, regression tests) and create each one.
- Write a small validator that asserts every listed requirement, and run it against the actual saved files before declaring done.
- Do not stop just because the computation is correct; the deliverable contract is separate and must pass too.

### Tool result
@@ lines 1-11 of 11 @@
---
name: reproduce-exact-spec-strings
description: Use when the task mandates exact labels, field names, formats, or bullet patterns in the output.
---
- Copy required identifiers, field names, prefixes, and labels verbatim from the task; never paraphrase or substitute synonyms.
- Follow prescribed formatting patterns character-for-character (e.g. bullet templates with fixed placeholders).
- Use the exact required spelling and case for every enumerated value.
- Apply any required value transformation (e.g. replacing a separator character, lower-casing) before emitting it.
- Include any mandated schema/version/header values literally at the required location.
- Diff your output against a literal skeleton of the required structure to catch missing or renamed keys.
- Do not invent extra provenance or context; emit only what the spec asks for, in the required shape.

### Tool call: ls
{"path": "/workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: ls
{"path": "/workspace/bookings"}

### Tool call: ls
{"path": "/workspace/tests"}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_bookings.py']

### Tool call: read_file
{"file_path": "/workspace/README.md"}

### Tool call: read_file
{"file_path": "/workspace/CHANGELOG.md"}

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

### Tool call: read_file
{"file_path": "/workspace/bookings/__init__.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/timeutil.py"}

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
{"file_path": "/workspace/bookings/schedule.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/calendar_export.py"}

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

### Tool call: read_file
{"file_path": "/workspace/tests/test_bookings.py"}

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
{"command": "cd /workspace && ls -la && python -m pytest tests -q 2>&1 | tail -40"}

### Tool call: glob
{"pattern": "**/*"}

### Tool result
[stderr] /bin/sh: 1: cd: can't cd to /workspace

Exit code: 2
[Command failed with exit code 2]

### Tool result
['/skills/output-contract-checklist/SKILL.md', '/skills/reproduce-exact-spec-strings/SKILL.md', '/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/__init__.cpython-312.pyc', '/workspace/bookings/__pycache__/billing.cpython-312.pyc', '/workspace/bookings/__pycache__/calendar_export.cpython-312.pyc', '/workspace/bookings/__pycache__/schedule.cpython-312.pyc', '/workspace/bookings/__pycache__/timeutil.cpython-312.pyc', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py', '/workspace/tests/__pycache__/test_bookings.cpython-312-pytest-9.1.1.pyc', '/workspace/tests/test_bookings.py']

### Tool call: execute
{"command": "pwd && ls && cd workspace && python -m pytest tests -q 2>&1 | tail -40"}

### Tool result
/tmp/lab-run-2cm3p48o
skills
workspace
C:\Users\ASUS\Documents\AI thực chiến\K4-L3L4-Track3-Day20-AdvanceMultiAgents\tasks\code-eval\workspace\tests\test_bookings.py:6: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
bookings/schedule.py:7: in total_minutes
    return sum(parse_duration(d) for d in durations)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
bookings/schedule.py:7: in <genexpr>
    return sum(parse_duration(d) for d in durations)
               ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

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
=========================== short test summary in

### Tool call: execute
{"command": "cd workspace && ls -la . bookings tests && git log --oneline 2>&1 | head -20"}

### Tool result
.:
total 28
drwx------ 5 root root 4096 Oct  6 16:14 .
drwx------ 5 root root 4096 Oct  6 16:14 ..
drwxr-xr-x 3 root root 4096 Oct  6 16:14 .pytest_cache
-rwx------ 1 root root   60 Oct  6 05:15 CHANGELOG.md
-rwx------ 1 root root  123 Oct  6 05:15 README.md
drwx------ 3 root root 4096 Oct  6 05:36 bookings
drwx------ 3 root root 4096 Oct  6 05:36 tests

bookings:
total 32
drwx------ 3 root root 4096 Oct  6 05:36 .
drwx------ 5 root root 4096 Oct  6 16:14 ..
-rwx------ 1 root root   23 Oct  6 05:15 __init__.py
drwx------ 2 root root 4096 Oct  6 05:36 __pycache__
-rwx------ 1 root root  344 Oct  6 05:15 billing.py
-rwx------ 1 root root  218 Oct  6 05:15 calendar_export.py
-rwx------ 1 root root  484 Oct  6 05:15 schedule.py
-rwx------ 1 root root  532 Oct  6 05:15 timeutil.py

tests:
total 16
drwx------ 3 root root 4096 Oct  6 05:36 .
drwx------ 5 root root 4096 Oct  6 16:14 ..
drwx------ 2 root root 4096 Oct  6 05:36 __pycache__
-rwx------ 1 root root  386 Oct  6 05:15 test_bookings.py
/bin/sh: 1: git: not found

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "cd workspace && ls bookings/__pycache__ tests/__pycache__"}

### Tool result
bookings/__pycache__:
__init__.cpython-312.pyc
billing.cpython-312.pyc
calendar_export.cpython-312.pyc
schedule.cpython-312.pyc
timeutil.cpython-312.pyc

tests/__pycache__:
test_bookings.cpython-312-pytest-9.1.1.pyc

[Command succeeded with exit code 0]

### Assistant
Now I understand the issues. Let me fix each module.

### Tool call: write_file
{"file_path": "/workspace/bookings/timeutil.py", "content": "\"\"\"Time helpers for the bookings package.\"\"\"\nimport re\n\n_HOURS_MINUTES_RE = re.compile(r\"(?:(\\d+)h)?(?:(\\d+)m)?\")\n_CLOCK_RE = re.compile(r\"(\\d+):(\\d{2})\")\n_BARE_MINUTES_RE = re.compile(r\"\\d+\")\n\n\ndef parse_duration(text: str) -> int:\n    \"\"\"Convert a duration string to whole minutes (int).\n\n    Supported formats:\n      \"1h30m\" -> 90\n      \"2h\"    -> 120\n      \"45m\"   -> 45\n      \"1:30\"  -> 90\n      \"45\"    -> 45    # a bare number means minutes\n    Surrounding whitespace is ignored.\n    \"\"\"\n    stripped = text.strip()\n\n    clock = _CLOCK_RE.fullmatch(stripped)\n    if clock:\n        return int(clock.group(1)) * 60 + int(clock.group(2))\n\n    if _BARE_MINUTES_RE.fullmatch(stripped):\n        return int(stripped)\n\n    hours_minutes = _HOURS_MINUTES_RE.fullmatch(stripped)\n    if hours_minutes and stripped:\n        hours = int(hours_minutes.group(1) or 0)\n        minutes = int(hours_minutes.group(2) or 0)\n        return hours * 60 + minutes\n\n    raise ValueError(f\"bad duration: {text!r}\")\n"}

### Tool call: write_file
{"file_path": "/workspace/bookings/billing.py", "content": "\"\"\"Billing rules.\"\"\"\n\n\ndef billable_blocks(minutes: int, block: int = 15) -> int:\n    \"\"\"Number of billable blocks for a booking.\n\n    A partial block is billed as a full block (always round UP):\n    16 minutes with 15-minute blocks -> 2 blocks.\n    `minutes` must be >= 0; a negative value raises ValueError.\n    \"\"\"\n    if minutes < 0:\n        raise ValueError(f\"minutes must be >= 0, got {minutes!r}\")\n    if block <= 0:\n        raise ValueError(f\"block must be > 0, got {block!r}\")\n    return -(-minutes // block)\n"}

### Tool result
Updated file /workspace/bookings/timeutil.py

### Tool result
Updated file /workspace/bookings/billing.py

### Tool call: write_file
{"content": "\"\"\"Schedule helpers.\"\"\"\nfrom collections.abc import Iterable, Sequence\n\nfrom .timeutil import parse_duration\n\n\ndef total_minutes(durations: Iterable[str]) -> int:\n    \"\"\"Total minutes of a list of duration strings.\"\"\"\n    return sum(parse_duration(duration) for duration in durations)\n\n\ndef add_slot(slot: str, slots: Sequence[str] | None = None) -> list[str]:\n    \"\"\"Return a NEW list containing the given slots plus `slot`.\n\n    Separate calls must not share state: calling add_slot(\"a\") and then\n    add_slot(\"b\") returns [\"a\"] and then [\"b\"].\n    \"\"\"\n    result = list(slots) if slots is not None else []\n    result.append(slot)\n    return result\n", "file_path": "/workspace/bookings/schedule.py"}

### Tool call: write_file
{"content": "\"\"\"Calendar export.\"\"\"\nfrom .timeutil import parse_duration\n\n\ndef slot_end(start_minute: int, duration_text: str) -> int:\n    \"\"\"Minute of the day at which a slot ends.\"\"\"\n    return start_minute + parse_duration(duration_text)\n", "file_path": "/workspace/bookings/calendar_export.py"}

### Tool result
Updated file /workspace/bookings/schedule.py

### Tool result
Updated file /workspace/bookings/calendar_export.py

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -20"}

### Tool result
...                                                                      [100%]
3 passed in 0.01s

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "cd workspace && python - <<'EOF'\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot, total_minutes\nfrom bookings.timeutil import parse_duration\nfrom bookings.calendar_export import slot_end\n\n# parse_duration spec table\nassert parse_duration(\"1h30m\") == 90\nassert parse_duration(\"2h\") == 120\nassert parse_duration(\"45m\") == 45\nassert parse_duration(\"1:30\") == 90\nassert parse_duration(\"45\") == 45\nassert parse_duration(\"  1h30m  \") == 90\nassert parse_duration(\"0\") == 0\nassert parse_duration(\"0h0m\") == 0\nassert isinstance(parse_duration(\"2h\"), int)\nfor bad in [\"\", \"  \", \"abc\", \"1h\", \"h30m\", \"1h30\", \"1:3\", \"1h30m45\", \"-5\", \"1.5h\"]:\n    try:\n        parse_duration(bad)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(f\"expected ValueError for {bad!r}\")\n\n# billing\nassert billable_blocks(20) == 2\nassert billable_blocks(45) == 3\nassert billable_blocks(0) == 0\nassert billable_blocks(15) == 1\nassert billable_blocks(16) == 2\nassert billable_blocks(30) == 2\nassert billable_blocks(1) == 1\nassert billable_blocks(60, 60) == 1\ntry:\n    billable_blocks(-1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError(\"expected ValueError\")\n\n# schedule: no shared state\na = add_slot(\"a\")\nb = add_slot(\"b\")\nassert a == [\"a\"], a\nassert b == [\"b\"], b\nassert add_slot(\"c\", [\"a\", \"b\"]) == [\"a\", \"b\", \"c\"]\nbase = [\"x\"]\nres = add_

### Tool result
[stderr] Traceback (most recent call last):
[stderr]   File "<stdin>", line 22, in <module>
[stderr] AssertionError: expected ValueError for '1h'

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "cd workspace && python - <<'EOF'\nfrom bookings.billing import billable_blocks\nfrom bookings.schedule import add_slot, total_minutes\nfrom bookings.timeutil import parse_duration\nfrom bookings.calendar_export import slot_end\n\nassert parse_duration(\"1h30m\") == 90\nassert parse_duration(\"2h\") == 120\nassert parse_duration(\"1h\") == 60\nassert parse_duration(\"45m\") == 45\nassert parse_duration(\"1:30\") == 90\nassert parse_duration(\"1:05\") == 65\nassert parse_duration(\"45\") == 45\nassert parse_duration(\"  1h30m  \") == 90\nassert parse_duration(\"0\") == 0\nassert parse_duration(\"0h0m\") == 0\nassert parse_duration(\"0m\") == 0\nassert isinstance(parse_duration(\"2h\"), int)\nfor bad in [\"\", \"  \", \"abc\", \"h30m\", \"1h30\", \"1h30m45\", \"-5\", \"1.5h\", \"1H30M\", None]:\n    try:\n        parse_duration(bad)\n    except (ValueError, AttributeError):\n        pass\n    else:\n        raise AssertionError(f\"expected error for {bad!r}\")\n\nassert billable_blocks(20) == 2\nassert billable_blocks(45) == 3\nassert billable_blocks(0) == 0\nassert billable_blocks(15) == 1\nassert billable_blocks(16) == 2\nassert billable_blocks(30) == 2\nassert billable_blocks(1) == 1\nassert billable_blocks(60, 60) == 1\ntry:\n    billable_blocks(-1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError(\"expected ValueError\")\n\na = add_slot(\"a\"); b = add_slot(\"b\")\nassert a == [\"a\"], a\nassert b == [\"b\"], b\nassert add_slot(\"c\", [\"a\", \"b\

### Tool result
all docstring checks passed

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "ls -la / && ls -la /tmp/lab-run-2cm3p48o 2>/dev/null; ls -la /artifacts 2>/dev/null"}

### Tool result
[stderr] ls: cannot open directory '/': Permission denied

Exit code: 2
[Command failed with exit code 2]

### Tool call: execute
{"command": "pwd; ls -la; ls -la skills"}

### Tool result
/tmp/lab-run-2cm3p48o
total 20
drwx------ 5 root root 4096 Oct  6 16:14 .
drwxrwxrwt 1 root root 4096 Oct  6 16:14 ..
drwxr-xr-x 2 root root 4096 Oct  6 16:15 .tmp
drwxr-xr-x 4 root root 4096 Oct  6 16:14 skills
drwx------ 5 root root 4096 Oct  6 16:14 workspace
total 16
drwxr-xr-x 4 root root 4096 Oct  6 16:14 .
drwx------ 5 root root 4096 Oct  6 16:14 ..
drwxr-xr-x 2 root root 4096 Oct  6 13:25 output-contract-checklist
drwxr-xr-x 2 root root 4096 Oct  6 13:25 reproduce-exact-spec-strings

[Command succeeded with exit code 0]

### Tool call: edit_file
{"file_path": "/workspace/CHANGELOG.md", "old_string": "## Unreleased\n", "new_string": "## Unreleased\n- `parse_duration` now handles every documented format (`\"2h\"`, `\"45m\"`, `\"1:30\"`, bare minute counts) and rejects unknown input.\n- `billable_blocks` always rounds up to a whole block and raises `ValueError` for negative minutes.\n- `add_slot` returns a new list instead of mutating a shared default argument.\n"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/CHANGELOG.md'

### Tool call: read_file
{"file_path": "/workspace/CHANGELOG.md"}

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -5 && python -m compileall -q bookings && awk 'length > 79 {print FILENAME\": \"FNR\": \"length}' bookings/*.py; echo \"line-length check done\"; python -m pyflakes bookings 2>&1 | head; pip list 2>/dev/null | grep -iE \"flake8|pyflakes|ruff|mypy\""}

### Tool result
@@ lines 1-9 of 9 @@
# Changelog

## Unreleased
- `parse_duration` now handles every documented format (`"2h"`, `"45m"`, `"1:30"`, bare minute counts) and rejects unknown input.
- `billable_blocks` always rounds up to a whole block and raises `ValueError` for negative minutes.
- `add_slot` returns a new list instead of mutating a shared default argument.

## 1.4.2
- initial import

### Tool result
...                                                                      [100%]
3 passed in 0.01s
line-length check done
/usr/local/bin/python: No module named pyflakes

Exit code: 1
[Command failed with exit code 1]

### Tool call: read_file
{"file_path": "/workspace/bookings/timeutil.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/schedule.py"}

### Tool result
@@ lines 1-35 of 35 @@
"""Time helpers for the bookings package."""
import re

_HOURS_MINUTES_RE = re.compile(r"(?:(\d+)h)?(?:(\d+)m)?")
_CLOCK_RE = re.compile(r"(\d+):(\d{2})")
_BARE_MINUTES_RE = re.compile(r"\d+")


def parse_duration(text: str) -> int:
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    stripped = text.strip()

    clock = _CLOCK_RE.fullmatch(stripped)
    if clock:
        return int(clock.group(1)) * 60 + int(clock.group(2))

    if _BARE_MINUTES_RE.fullmatch(stripped):
        return int(stripped)

    hours_minutes = _HOURS_MINUTES_RE.fullmatch(stripped)
    if hours_minutes and stripped:
        hours = int(hours_minutes.group(1) or 0)
        minutes = int(hours_minutes.group(2) or 0)
        return hours * 60 + minutes

    raise ValueError(f"bad duration: {text!r}")

### Tool result
@@ lines 1-20 of 20 @@
"""Schedule helpers."""
from collections.abc import Iterable, Sequence

from .timeutil import parse_duration


def total_minutes(durations: Iterable[str]) -> int:
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(duration) for duration in durations)


def add_slot(slot: str, slots: Sequence[str] | None = None) -> list[str]:
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    result = list(slots) if slots is not None else []
    result.append(slot)
    return result

### Assistant
The suite passes and my docstring-derived checks pass. Summary of changes:

**`bookings/timeutil.py`** — `parse_duration` only matched `"<h>h<m>m"`, so `"2h"`, `"45m"`, `"1:30"` and bare `"45"` raised `ValueError`, contradicting the docstring. Reimplemented it with three named, precompiled regexes (hours/minutes, clock `H:MM`, bare minutes), whitespace stripping, int returns, and a `ValueError` for anything unrecognized (kept the original error message shape). Added a `str -> int` annotation.

**`bookings/billing.py`** — `round()` does banker's rounding, so a partial block was not always rounded up (`billable_blocks(20) == 1`). Now uses ceiling integer arithmetic `-(-minutes // block)` so partial blocks bill as a full block, and negative `minutes` raises `ValueError` as documented (plus a guard for a non-positive `block`).

**`bookings/schedule.py`** — `add_slot` used a mutable default argument (`slots=[]`) and mutated/returned it, so calls shared state; now defaults to `None` and builds a fresh list (`list(slots) + [slot]`), per the "Return a NEW list / separate calls must not share state" contract. `total_minutes` is unchanged in behaviour (clarified parameter naming/annotation).

**`bookings/calendar_export.py`** — `slot_end` was correct; only added parameter type annotations (it now also accepts every format `parse_duration` supports, e.g. `"1:30"`).

**`CHANGELOG.md`** — recorded the three fixes under the existing `## Unreleased` section (existing `1.4.2` section untouch