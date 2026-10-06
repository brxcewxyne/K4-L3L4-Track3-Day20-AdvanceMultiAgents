### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

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
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/inventory/', '/workspace/tests/']

### Tool result
['/workspace/inventory/__init__.py', '/workspace/inventory/export.py', '/workspace/inventory/pricing.py', '/workspace/inventory/report.py', '/workspace/tests/test_report.py']

### Tool call: read_file
{"file_path": "workspace/README.md"}

### Tool call: read_file
{"file_path": "workspace/CHANGELOG.md"}

### Tool call: read_file
{"file_path": "workspace/inventory/__init__.py"}

### Tool call: read_file
{"file_path": "workspace/inventory/pricing.py"}

### Tool result
@@ lines 1-5 of 5 @@
# inventory

Small package. Run the tests from the `workspace/` folder:

    cd workspace && python -m pytest tests -q

### Tool result
@@ lines 1-6 of 6 @@
# Changelog

## Unreleased

## 0.3.1
- initial import

### Tool result
@@ lines 1-1 @@
System reminder: File exists but has empty contents

### Tool result
@@ lines 1-25 of 25 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))

### Tool call: read_file
{"file_path": "workspace/inventory/export.py"}

### Tool call: read_file
{"file_path": "workspace/inventory/report.py"}

### Tool call: read_file
{"file_path": "workspace/tests/test_report.py"}

### Tool result
@@ lines 1-12 of 12 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    return f'{item["name"]},{price:.2f},{item["qty"]}'

### Tool result
@@ lines 1-25 of 25 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return [item["name"] for item in items if item["qty"] <= threshold]

### Tool result
@@ lines 1-32 of 32 @@
from decimal import Decimal

from inventory.export import to_csv_row
from inventory.pricing import apply_discount
from inventory.report import low_stock, total_value


def test_total_value_plain():
    items = [{"name": "pen", "price": "$2.50", "qty": 4}]
    assert total_value(items) == Decimal("10.00")


def test_total_value_thousands_separator():
    items = [{"name": "laptop", "price": "$1,299.50", "qty": 2}]
    assert total_value(items) == Decimal("2599.00")


def test_discount_rounding_half_up():
    assert apply_discount(Decimal("10.05"), 10) == Decimal("9.05")


def test_total_value_with_discount():
    items = [{"name": "desk", "price": "100.00", "qty": 1, "discount": 15}]
    assert total_value(items) == Decimal("85.00")


def test_low_stock_basic():
    assert low_stock([{"name": "pen", "qty": 2}, {"name": "ink", "qty": 9}]) == ["pen"]


def test_csv_row_plain_name():
    assert to_csv_row({"name": "pen", "price": "2.5", "qty": 4}) == "pen,2.50,4"

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -40"}

### Tool call: execute
{"command": "cd workspace && ls -la && ls -la inventory tests"}

### Tool result

>   ???

C:\Users\ASUS\Documents\AI thực chiến\K4-L3L4-Track3-Day20-AdvanceMultiAgents\tasks\code-learn\workspace\tests\test_report.py:15: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
inventory/report.py:14: in total_value
    price = parse_price(item["price"])
            ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

text = '$1,299.50'

    def parse_price(text):
        """Convert a price string to a Decimal.
    
        Supported formats:
          "$1,299.50" -> Decimal("1299.50")
          "  12 "     -> Decimal("12")
          "1299.5"    -> Decimal("1299.5")
          "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
        """
        cleaned = text.strip().replace("$", "")
>       return Decimal(cleaned)
               ^^^^^^^^^^^^^^^^
E       decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]

inventory/pricing.py:15: InvalidOperation
________________________ test_discount_rounding_half_up ________________________

>   ???
E   AssertionError: assert Decimal('9.04') == Decimal('9.05')
E    +  where Decimal('9.04') = apply_discount(Decimal('10.05'), 10)
E    +    where Decimal('10.05') = Decimal('10.05')
E    +  and   Decimal('9.05') = Decimal('9.05')

C:\Users\ASUS\Documents\AI thực chiến\K4-L3L4-Track3-Day20-AdvanceMultiAgents\tasks\code-learn\workspace\tests\test_report.py:19: AssertionError
=========================== sh

### Tool result
total 24
drwx------ 4 root root 4096 Oct  6 05:15 .
drwx------ 4 root root 4096 Oct  6 11:21 ..
-rwx------ 1 root root   60 Oct  6 05:15 CHANGELOG.md
-rwx------ 1 root root  124 Oct  6 05:15 README.md
drwx------ 3 root root 4096 Oct  6 05:36 inventory
drwx------ 3 root root 4096 Oct  6 05:36 tests
inventory:
total 24
drwx------ 3 root root 4096 Oct  6 05:36 .
drwx------ 4 root root 4096 Oct  6 05:15 ..
-rwx------ 1 root root    0 Oct  6 05:15 __init__.py
drwx------ 2 root root 4096 Oct  6 05:36 __pycache__
-rwx------ 1 root root  411 Oct  6 05:15 export.py
-rwx------ 1 root root  788 Oct  6 05:15 pricing.py
-rwx------ 1 root root  771 Oct  6 05:15 report.py

tests:
total 16
drwx------ 3 root root 4096 Oct  6 05:36 .
drwx------ 4 root root 4096 Oct  6 05:15 ..
drwx------ 2 root root 4096 Oct  6 05:36 __pycache__
-rwx------ 1 root root 1006 Oct  6 05:15 test_report.py

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "ls -la /; ls -la /workspace 2>/dev/null"}

### Tool call: glob
{"pattern": "**/*.{md,toml,cfg,ini,txt,yaml,yml}"}

### Tool result
[stderr] ls: cannot open directory '/': Permission denied

Exit code: 2
[Command failed with exit code 2]

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md']

### Assistant
Now I understand the bugs. Let me fix all three modules.

### Tool call: write_file
{"file_path": "workspace/inventory/pricing.py", "content": "\"\"\"Price utilities for the inventory package.\"\"\"\nfrom decimal import ROUND_HALF_UP, Decimal\n\nCENTS = Decimal(\"0.01\")\n\n\ndef parse_price(text):\n    \"\"\"Convert a price string to a Decimal.\n\n    Supported formats:\n      \"$1,299.50\" -> Decimal(\"1299.50\")\n      \"  12 \"     -> Decimal(\"12\")\n      \"1299.5\"    -> Decimal(\"1299.5\")\n      \"(12.00)\"   -> Decimal(\"-12.00\")   # accounting style: parentheses mean negative\n    \"\"\"\n    cleaned = text.strip()\n    negative = cleaned.startswith(\"(\") and cleaned.endswith(\")\")\n    if negative:\n        cleaned = cleaned[1:-1]\n    cleaned = cleaned.replace(\"$\", \"\").replace(\",\", \"\").strip()\n    value = Decimal(cleaned)\n    return -value if negative else value\n\n\ndef apply_discount(price, percent):\n    \"\"\"Return `price` after a percentage discount.\n\n    The result is a Decimal rounded to 2 decimal places using the\n    commercial rule \"round half up\" (0.005 -> 0.01).\n    \"\"\"\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(CENTS, rounding=ROUND_HALF_UP)\n"}

### Tool call: write_file
{"file_path": "workspace/inventory/report.py", "content": "\"\"\"Inventory reports.\"\"\"\nfrom decimal import Decimal\n\nfrom .pricing import apply_discount, parse_price\n\n\ndef total_value(items):\n    \"\"\"Total value of `items` after per-item discounts.\n\n    Each item is a dict: {\"name\": str, \"price\": str, \"qty\": int, \"discount\": percent (optional)}.\n    \"\"\"\n    total = Decimal(\"0\")\n    for item in items:\n        price = parse_price(item[\"price\"])\n        price = apply_discount(price, item.get(\"discount\", 0))\n        total += price * item[\"qty\"]\n    return total\n\n\ndef low_stock(items, threshold=5):\n    \"\"\"Names of the items whose quantity is strictly below `threshold`.\n\n    The names are sorted alphabetically, ignoring case.\n    \"\"\"\n    names = [item[\"name\"] for item in items if item[\"qty\"] < threshold]\n    return sorted(names, key=str.casefold)\n"}

### Tool call: write_file
{"file_path": "workspace/inventory/export.py", "content": "\"\"\"Export helpers.\"\"\"\nfrom .pricing import parse_price\n\n\ndef to_csv_row(item):\n    \"\"\"Format one item as a CSV row: name,price,qty (price with 2 decimals).\n\n    A name that contains a comma or a double quote is wrapped in double quotes,\n    and every double quote inside it is doubled (RFC 4180).\n    \"\"\"\n    price = parse_price(item[\"price\"])\n    name = item[\"name\"]\n    if \",\" in name or '\"' in name:\n        name = '\"' + name.replace('\"', '\"\"') + '\"'\n    return f\"{name},{price:.2f},{item['qty']}\"\n"}

### Tool result
Updated file /workspace/inventory/pricing.py

### Tool result
Updated file /workspace/inventory/report.py

### Tool result
Updated file /workspace/inventory/export.py

### Tool call: write_file
{"content": "\"\"\"Small inventory management helpers: pricing, reporting and export.\"\"\"\n", "file_path": "workspace/inventory/__init__.py"}

### Tool call: execute
{"command": "cd workspace && python -m pytest tests -q 2>&1 | tail -10"}

### Tool result
Updated file /workspace/inventory/__init__.py

### Tool result
......                                                                   [100%]
6 passed in 0.02s

[Command succeeded with exit code 0]

### Assistant
Now let me verify the docstring behaviours beyond the visible tests:

### Tool call: execute
{"command": "cd workspace && python -c \"\nfrom decimal import Decimal\nfrom inventory.pricing import parse_price, apply_discount\nfrom inventory.report import low_stock, total_value\nfrom inventory.export import to_csv_row\n\nprint(parse_price('\\$1,299.50'), parse_price('  12 '), parse_price('1299.5'), parse_price('(12.00)'))\nprint(parse_price('(1,299.50)'), parse_price(' ( 0.5 ) '))\nprint(apply_discount(Decimal('10.05'), 10), apply_discount(Decimal('0.05'), 10), apply_discount(Decimal('10.05'), 0), apply_discount(Decimal('100'), 33.333))\nprint(low_stock([{'name':'Zeta','qty':9},{'name':'apple','qty':0},{'name':'Apple','qty':2}], 5))\nprint(low_stock([{'name':'a','qty':5}], 5), low_stock([{'name':'a','qty':4}], 5))\nprint(total_value([{'name':'pen','price':'\\$2.50','qty':3,'discount':10}]))\nprint(repr(to_csv_row({'name':'pen','price':'2.5','qty':4})))\nprint(repr(to_csv_row({'name':'a,b','price':'1','qty':1})))\nprint(repr(to_csv_row({'name':'say \\\"hi\\\"','price':'1','qty':1})))\nprint(repr(to_csv_row({'name':'plain','price':'\\$1,000','qty':2})))\n\"\n"}

### Tool call: execute
{"command": "cd workspace && python -m pyflakes inventory 2>&1 | head -20; python -m flake8 --version 2>&1 | head -2"}

### Tool result
1299.50 12 1299.5 -12.00
-1299.50 -0.5

[stderr] Traceback (most recent call last):
[stderr]   File "<string>", line 9, in <module>
[stderr]   File "/tmp/lab-run-7dhbv48h/workspace/inventory/pricing.py", line 31, in apply_discount
[stderr]     discounted = price * (100 - percent) / 100
[stderr]                  ~~~~~~^~~~~~~~~~~~~~~~~
[stderr] TypeError: unsupported operand type(s) for *: 'decimal.Decimal' and 'float'

Exit code: 1
[Command failed with exit code 1]

### Tool result
/usr/local/bin/python: No module named pyflakes
/usr/local/bin/python: No module named flake8

[Command succeeded with exit code 0]

### Assistant
The float-percent case shows `apply_discount` is fragile outside Decimal. Let me make it robust while keeping the specified rounding:

### Tool call: edit_file
{"file_path": "workspace/inventory/pricing.py", "old_string": "CENTS = Decimal(\"0.01\")", "new_string": "_CENTS = Decimal(\"0.01\")"}

### Tool call: edit_file
{"file_path": "workspace/inventory/pricing.py", "old_string": "    discounted = price * (100 - percent) / 100\n    return discounted.quantize(CENTS, rounding=ROUND_HALF_UP)", "new_string": "    price = Decimal(str(price))\n    percent = Decimal(str(percent))\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(_CENTS, rounding=ROUND_HALF_UP)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool result
Error: parallel file mutations to the same path are not allowed.

### Tool call: read_file
{"file_path": "workspace/inventory/pricing.py"}

### Tool result
@@ lines 1-32 of 32 @@
"""Price utilities for the inventory package."""
from decimal import ROUND_HALF_UP, Decimal

_CENTS = Decimal("0.01")


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip()
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    if negative:
        cleaned = cleaned[1:-1]
    cleaned = cleaned.replace("$", "").replace(",", "").strip()
    value = Decimal(cleaned)
    return -value if negative else value


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(CENTS, rounding=ROUND_HALF_UP)

### Tool call: edit_file
{"file_path": "workspace/inventory/pricing.py", "new_string": "    price = Decimal(str(price))\n    percent = Decimal(str(percent))\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(_CENTS, rounding=ROUND_HALF_UP)", "old_string": "    discounted = price * (100 - percent) / 100\n    return discounted.quantize(CENTS, rounding=ROUND_HALF_UP)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: execute
{"command": "cd workspace && python -c \"\nfrom decimal import Decimal\nfrom inventory.pricing import parse_price, apply_discount\nfrom inventory.report import low_stock, total_value\nfrom inventory.export import to_csv_row\n\nprint(parse_price('\\$1,299.50'), parse_price('  12 '), parse_price('1299.5'), parse_price('(12.00)'))\nprint(parse_price('(1,299.50)'), parse_price(' ( \\$0.5 ) '))\nprint(apply_discount(Decimal('10.05'), 10), apply_discount(Decimal('0.05'), 10), apply_discount(Decimal('10.05'), 0), apply_discount(Decimal('100'), 33.333), apply_discount(Decimal('100'), Decimal('12.5')), apply_discount(Decimal('-10.05'), 10), apply_discount(20, 10))\nprint(low_stock([{'name':'Zeta','qty':9},{'name':'apple','qty':0},{'name':'Apple','qty':2}], 5))\nprint(low_stock([{'name':'a','qty':5}], 5), low_stock([{'name':'a','qty':4}], 5), low_stock([]))\nprint(total_value([{'name':'pen','price':'\\$2.50','qty':3,'discount':10}]))\nprint(repr(to_csv_row({'name':'pen','price':'2.5','qty':4})))\nprint(repr(to_csv_row({'name':'a,b','price':'1','qty':1})))\nprint(repr(to_csv_row({'name':'say \\\"hi\\\"','price':'1','qty':1})))\nprint(repr(to_csv_row({'name':'plain','price':'\\$1,000','qty':2})))\nprint(repr(to_csv_row({'name':'a,\\\"b\\\"','price':'3','qty':1})))\n\" && python -m pytest tests -q 2>&1 | tail -3"}

### Tool result
1299.50 12 1299.5 -12.00
-1299.50 -0.5
9.05 0.05 10.05 66.67 87.50 -9.05 18.00
['apple', 'Apple']
[] ['a'] []
6.75
'pen,2.50,4'
'"a,b",1.00,1'
'"say ""hi""",1.00,1'
'plain,1000.00,2'
'"a,""b""",3.00,1'
......                                                                   [100%]
6 passed in 0.01s

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "cd workspace && python - <<'EOF'\nimport pathlib\nfor p in sorted(pathlib.Path('inventory').glob('*.py')):\n    text = p.read_text()\n    for i, line in enumerate(text.splitlines(), 1):\n        if len(line) > 88:\n            print(f\"{p}:{i}: len={len(line)} {line[:60]}...\")\n        if line != line.rstrip():\n            print(f\"{p}:{i}: trailing whitespace\")\n        if '\\t' in line:\n            print(f\"{p}:{i}: tab\")\n    if not text.endswith('\\n'):\n        print(f\"{p}: no final newline\")\nprint(\"style check done\")\nEOF\npython -m pytest tests -q 2>&1 | tail -3"}

### Tool call: execute
{"command": "cd workspace && python -c \"import inventory, inventory.export, inventory.pricing, inventory.report; print('imports ok', inventory.__doc__)\""}

### Tool result
inventory/report.py:10: len=97     Each item is a dict: {"name": str, "price": str, "qty": ...
style check done
......                                                                   [100%]
6 passed in 0.01s

[Command succeeded with exit code 0]

### Tool result
imports ok Small inventory management helpers: pricing, reporting and export.

[Command succeeded with exit code 0]

### Tool call: edit_file
{"file_path": "workspace/CHANGELOG.md", "old_string": "## Unreleased\n", "new_string": "## Unreleased\n- `pricing.parse_price`: handle thousands separators and accounting-style negative values.\n- `pricing.apply_discount`: round half up instead of the Decimal default (half even).\n- `report.low_stock`: use a strict comparison against the threshold and sort names case-insensitively.\n- `export.to_csv_row`: quote names containing a comma or a double quote (RFC 4180).\n"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/CHANGELOG.md'

### Tool call: read_file
{"file_path": "workspace/inventory/export.py"}

### Tool call: read_file
{"file_path": "workspace/inventory/report.py"}

### Tool result
@@ lines 1-15 of 15 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    name = item["name"]
    if "," in name or '"' in name:
        name = '"' + name.replace('"', '""') + '"'
    return f"{name},{price:.2f},{item['qty']}"

### Tool result
@@ lines 1-26 of 26 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    names = [item["name"] for item in items if item["qty"] < threshold]
    return sorted(names, key=str.casefold)

### Tool call: execute
{"command": "cd workspace && python - <<'EOF'\nimport csv, io\nfrom inventory.export import to_csv_row\nrows = [to_csv_row({\"name\": n, \"price\": \"1,000\", \"qty\": 2}) for n in [\"pen\", \"a,b\", 'say \"hi\"', 'a,\"b\"']]\nprint(rows)\nparsed = list(csv.reader(io.StringIO(\"\\n\".join(rows))))\nassert parsed == [[\"pen\", \"1000.00\", \"2\"], [\"a,b\", \"1000.00\", \"2\"], ['say \"hi\"', \"1000.00\", \"2\"], ['a,\"b\"', \"1000.00\", \"2\"]], parsed\nprint(\"csv round-trip ok\")\nEOF\npython -m pytest tests -q 2>&1 | tail -3"}

### Tool result
['pen,1000.00,2', '"a,b",1000.00,2', '"say ""hi""",1000.00,2', '"a,""b""",1000.00,2']
csv round-trip ok
......                                                                   [100%]
6 passed in 0.01s

[Command succeeded with exit code 0]

### Assistant
Fixed the `inventory` package; the full suite passes (6 passed) and the docstring-documented behaviour now holds for cases the visible tests miss.

What I changed and why:

- **`inventory/pricing.py`**
  - `parse_price`: it only stripped `$` and whitespace, so `"$1,299.50"` raised `InvalidOperation` and `"(12.00)"` (accounting-style negative) broke. It now detects the surrounding parentheses, strips `$`/`,`/whitespace, and negates the value when wrapped in parentheses.
  - `apply_discount`: `Decimal.quantize` defaults to banker's rounding (half-even), so `10.05 - 10% = 9.045` became `9.04`. It now rounds with `ROUND_HALF_UP` to 2 decimals, i.e. the documented commercial rule `0.005 -> 0.01`. I also normalise `price`/`percent` through `Decimal(str(...))` so int/float/Decimal inputs behave identically, and moved the quantum to a private module constant `_CENTS`.
- **`inventory/report.py`**
  - `low_stock`: was using `qty <= threshold` (should be *strictly* below) and returned names in input order without sorting. It now filters with `<` and returns `sorted(names, key=str.casefold)` for the documented case-insensitive alphabetical order.
- **`inventory/export.py`**
  - `to_csv_row`: never quoted the name. It now wraps names containing a comma or double quote in quotes and doubles embedded quotes, per RFC 4180 (verified to round-trip through `csv.reader`).
- **`inventory/__init__.py`**: added a package docstring (was empty).
- **`CHANGELOG.md`**: added an "Unreleased" entry descr