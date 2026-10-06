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