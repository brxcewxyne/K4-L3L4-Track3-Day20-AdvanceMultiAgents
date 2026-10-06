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