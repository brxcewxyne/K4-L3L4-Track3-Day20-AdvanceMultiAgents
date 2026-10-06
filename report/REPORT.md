# Lab Report: Self-Evolving Agentic

## 1. Group Information and Configuration

| Full name | Student ID | Contribution |
|---|---|---|
| TODO | TODO | TODO |

- Model (deployment name or `LAB_MODEL`), temperature (`LAB_TEMPERATURE`), `recursion_limit`: TODO (model configuration is read from `.env`; those values were not inspected for this report). All reported runs executed inside Docker.
- Deep Agents version (`pip show deepagents`), operating system, native or Docker: Deep Agents 0.7.21 (pinned in `pyproject.toml`); Windows host with the lab running inside the Docker image `lab-deepagents` (Linux, Python 3.12).
- Number of task runs used / budget: 9 official learning runs (baseline, subagents, skills-auto × `code-learn`, `data-learn`, `logs-learn`), 1 separate repeat run (`data-learn`, skills-auto), plus diagnostic debug runs; the token cap defaults to 200,000 and was set to 350,000 for the repeat runs.
- Commit of the `freeze` tag: TODO (tag not created yet).

## 2. Hypotheses (committed BEFORE the `freeze` tag, Part 4.0)

Predictions are pre-registered for the **evaluation tasks**; evaluation outcomes are unknown at this point. Evidence comes from the error taxonomy in Section 4.

- H1 (subagents vs baseline): expected direction is **no score gain** — `subagents` will not beat `baseline` on evaluation score (expected delta 0 within repeat noise), at roughly 1.9×–5.4× the tokens. Evidence from learning runs: scores are unchanged (code-learn's +1 check, `tests_not_modified`, is an infrastructure fix, not an agent gain; data-learn and logs-learn scores are identical), while tokens rise 1.9×–5.4×. Mechanism: our explorer/implementer/reviewer subagents improve process (context isolation, independent verification) but not knowledge of workspace-external conventions, and every repeated failure is a `rule_*` convention check. Refutation: any evaluation-score advantage of ≥2 checks over `baseline`, or any `rule_*` check that only `subagents` passes, beyond what repeat noise can explain.
- H2 (skills-auto vs baseline): expected direction is **no score gain** (expected delta ~0). Evidence: all three official `skills-auto` learning runs read both skills (`skills_read = 2`) yet kept exactly the same `rule_*` failures and scores as `baseline`. Mechanism: progressive disclosure makes the agent read the generic checklists, but the failing checks encode conventions absent from the workspace and unknown to the curator; a generic skill cannot infer them. Refutation: a `skills-auto` evaluation score ≥ `baseline` + 2 checks, or new `rule_*` checks passing with trace evidence that a skill rule caused the pass.
- H3 (learning tasks vs evaluation tasks): expected direction is **no transfer** — learning-task performance will not predict evaluation performance, and any `rule_*` failure observed on learning tasks will persist on evaluation tasks (including evaluation-only conventions the skills never saw). Evidence: learning failures come from missing convention documents, not from missing process. Refutation: evaluation performance improving by more than repeat noise while learning performance stays flat (positive transfer), or evaluation `rule_*` checks passing through skill guidance.

## 3. Getting to Know Deep Agents (Part 0.3)

1. The default agent exposes the tools `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute`, and `task`. `execute` runs shell commands in the sandbox; `task` delegates work to a subagent.
2. The `task` tool provides the default `general-purpose` subagent for multi-step work. Each call is an isolated session: the subagent sees only the delegation prompt and returns a single final report, so the main agent must include the goal, context, limits, and required output format.
3. The default system prompt is empty. The `task` description states: “the agent sees only the prompt you give it and returns a single final report.” The `execute` description states that the tool runs commands in the sandbox and returns stdout/stderr plus an exit code. Agent behavior is therefore shaped by tool descriptions as well as by the system prompt.

## 4. Baseline and Error Taxonomy (Part 2.2)

Nine official learning runs completed (baseline, subagents, skills-auto × `code-learn`, `data-learn`, `logs-learn`); every `run.json` has `error = none`:

| Task | baseline | subagents | skills-auto | tokens b / s / sa | tool calls b / s / sa | subagent_calls b / s / sa | skills_read (sa) |
|---|---|---|---|---|---|---|---|
| code-learn | 6/10 | 7/10 | 7/10 | 193.914 / 1.044.076 / 287.827 | 31 / 33 / 37 | 0 / 2 / 0 | 2 |
| data-learn | 5/8 | 5/8 | 5/8 | 144.114 / 272.691 / 159.265 | 17 / 16 / 23 | 0 / 1 / 0 | 2 |
| logs-learn | 6/9 | 6/9 | 6/9 | 145.933 / 392.240 / 183.841 | 18 / 16 / 21 | 0 / 1 / 0 | 2 |

Each row below is a failed check that repeats in **all three conditions** (code-learn baseline additionally fails `tests_not_modified`; see below):

| Task | Failed check | Error group (A–G) | Evidence (short quote from `detail` or trace) |
|---|---|---|---|
| code-learn | rule_type_hints | E | `RULE: every public function ... type annotations`; the final summary has no annotation pass. |
| code-learn | rule_regression_tests | E | `RULE: add tests/test_regressions.py ...`; no tool call creates this file in the trace. |
| code-learn | rule_changelog | E | `RULE: ... '- fix(<function name>): <short description>'`; CHANGELOG only received plain bullets. |
| data-learn | rule_money_in_cents | E | `RULE: money values ... integer cents`; trace reports `North Q1 2024: ... 3130.24` (decimal USD). |
| data-learn | rule_meta_block | E | `RULE: answer.json has an object meta ...`; subagents trace: “wrote exactly the five requested keys”. |
| data-learn | rule_clean_csv | E | `RULE: write workspace/clean.csv ...`; no run created `clean.csv`. |
| logs-learn | rule_service_names | E | `RULE: service names ... '-' replaced by '_'`; trace still reports `inventory-service`, `payment-service`. |
| logs-learn | rule_sorted_errors | E | `RULE: errors is sorted by service, then timestamp_utc`; trace has no sorting step. |
| logs-learn | rule_schema_header | E | `RULE: ... "schema_version": 2 and "generated_by": "log-triage"`; subagents: “found none” when searching for a conventions document. |

Remark: **all agent failures belong to group E** (`rule_*` checks, `detail` starts with `RULE:`); every technical check passes in all three conditions (negative evidence: code-learn 6/6 technical checks — excluding `tests_not_modified`, which is an infrastructure failure; data-learn 5/5; logs-learn 6/6). Shared failure pattern: the briefs mention “Acme … conventions” but the workspace contains no conventions document; the agent verifies the technical part and stops, skipping the hidden conventions. Subagent traces state *“no conventions document exists anywhere in the sandbox … so I wrote exactly the five requested keys”* and *“searched the whole sandbox … found none”*.

`code-learn` 6/10 → 7/10: recorded scores are unchanged (baseline 6/10; subagents and skills-auto 7/10). Check by check, **only** `tests_not_modified` flips FAIL→PASS and the other 9 checks are identical; no trace writes or edits `tests/*` (only `read_file`). Timeline: baseline 18:21–18:23, LF restore for `tasks/code-learn/workspace/tests/test_report.py` at 18:31, subagents 19:15–20:04, skills-auto 20:36–20:44. The difference is consistent with the Windows-checkout CRLF/LF timeline, but this is **only an inference** (the old sandbox was deleted and cannot be re-hashed), although it is supported by the timeline and by the clean workspace passing this check after the LF restore; the extra point is **not** credited to subagents or skills. This check is excluded from A–G because it is an infrastructure failure (GUIDE 2.2).

Candidate skill hypotheses (evidence-based, up to 3):
1. **Find the conventions document before finishing**: scan the sandbox (including hidden directories) for a conventions/spec file; if none exists, state in the final answer that conventions are unavailable and list which requirements are certain.
2. **Verify explicit requirements**: build a checklist from the instruction/README/docstrings and check each item against the artifacts; distinguish a missing conventions document from a known requirement and do not guess undocumented rules.
3. **Final self-check on the real artifacts**: re-read the written files (`answer.json`, `errors.json`, source) and state what remains unverified; traces show the agent verifies the technical part correctly but never surfaces the missing conventions.

## 5. `subagents` Condition (Part 2.3)

- Three subagents are defined in `src/lab/subagents.py`: **explorer** (reads docs/data/tests, reports findings with evidence, never edits), **implementer** (edits files toward the goal, runs checks, reports changed files and remaining errors), **reviewer** (independently checks requirements and edge cases, only reports problems, never edits). Each `description` states when to call it; each `system_prompt` states mission, limits, and report format.
- `subagent_calls`: baseline 0/0/0; `subagents` condition — code-learn **2**, data-learn **1**, logs-learn **1**; `skills-auto` 0 (single mode). Only code-learn delegated two jobs.
- Delegation content (trace `results/subagents/*/trace.md`): code-learn `:337` delegates to implementer with “CONTEXT / RULES” (relative paths, docstrings, format examples) and `:523` delegates a review with “REPORT PROBLEMS ONLY — do not edit any file”; data-learn `:231` and logs-learn `:301` delegate independent verification with relative paths and schema/ordering/field-name checks. The briefs contain the necessary information; `render_trace` truncates args at 1500 characters, so the `subagent_type` is not visible for 3 of 4 calls (only the code-learn call at `:338` shows `implementer`) — there is **not enough evidence to confirm the role used for the other calls**.
- Checking subagent reports before use: code-learn shows the main agent applying review findings by editing again at `:539`/`:542` and re-running tests at `:551`; data-learn and logs-learn received matching verification reports and made no further changes (the depth of checking cannot be proven).
- Token/time impact vs baseline: code-learn 1.044.076 tokens (5.4×) / 501.4s vs 193.914 / 99.3s; data-learn 272.691 (1.9×) / 117.6s vs 144.114 / 71.9s; logs-learn 392.240 (2.7×) / 164.9s vs 145.933 / 69.0s. No additional score gain (code-learn +1 is `tests_not_modified`, not subagents).

## 6. Self-Evolving: Skills Generated by the Curator (Part 3)

- Curator runs, deleted skills, and reasons: according to the CLI output supplied by the user (user-reported), the curator was invoked **once**; the repo stores no CLI log, commit, or tag for it, so this is a user statement rather than Git/on-disk proof. One skill, `preserve-provided-files`, was **deleted**: its original content treated “existing test files, input datasets, and fixtures” as read-only and allowed only additive changes (only self-generated files could be edited), which forbids editing existing source files — wrong for `code-learn`. The skill was later hand-edited (a violation of GUIDE 3.3), so the edited version was not kept or used. **The time of the delete operation is not logged**; the hash below only proves that the run-time skill set of the 3 old runs equaled the two current skills (the deleted skill was not loaded); it does not prove the timing of the deletion.
- Skill hash at run time: all three `skills-auto` runs record `skills_sha256 = a4a40722…`. This is **not** a content mismatch: `hash_skills()` hashes the relative path too, so the same two unchanged SKILL.md files yield different digests depending on the OS path separator — Windows (`\`) = `ba043656…`, Linux (`/`) = `a4a40722…`; Docker runs Linux and therefore records `a4a40722…`. Per-file hashes in the container and on the host are identical, and there is no evidence of an extra skill: the run-time skill set of the 3 old runs equals the two current skills.
- Noise: one repeat `data-learn` run (same `skills-auto` condition, same skill set) scored 5/8 with 212.929 tokens, 24 tool calls, `skills_read = 2`, versus 5/8, 159.265 tokens, 23 tool calls for the primary run; it is stored separately in `results/skills-auto-repeat-data/` and excluded from the main table (Section 4).
- `skills_read` in all three `skills-auto` runs = **2** (output-contract-checklist and reproduce-exact-spec-strings). Distinguish **reading** from **following**: all three tasks read the skills but still failed the same `rule_*` checks as baseline; the traces show no application of `cents`/`meta`/`clean.csv` (data), `schema_version`/`generated_by` (logs), or `test_regressions`/type hints/changelog format (code).

| Skill | General or learning-task-specific? | Correct or not (state errors) | Length, `description`, and `skills_read` in Part 3.4 |
|---|---|---|---|
| output-contract-checklist | General: an output-contract checklist for any task delivering files/JSON/CSV; uses allowed Acme convention names (`clean.csv`, `changelog`, `regression tests`), no task IDs or answers | Formally correct and matching the `rule_*` failure types; effectiveness unproven because all 3 runs read it yet still failed the hidden conventions | 8 lines; `description`: “Use before finishing any task that must deliver files or structured output…”; `skills_read = 2` in all three `skills-auto` runs |
| reproduce-exact-spec-strings | Moderately general: focuses on exact labels/formats/strings; the separator/lower-casing example comes from the log convention but names no specific task | Correct per `detail`, no harmful guidance; effectiveness unproven (read but `rule_*` still fails) | 7 lines; `description`: “Use when the task mandates exact labels, field names, formats…”; `skills_read = 2` in all three `skills-auto` runs |

## 7. Comparison Results (Parts 4.3, 4.4)

> Paste the contents of `report/table.md` and the output of `python scripts/check_breakdown.py`. List any runs with `error` or `skills_modified = true` (if any) and how they were handled.

```text
(paste table here)
```

## 8. Analysis

> Answer each question with numbers from Section 7 and trace evidence. Negative or null results are valid if analyzed well.

1. Compared with `baseline`, which condition improves the **learning**-task score? Which improves the **evaluation**-task score? Does any condition improve learning tasks but not evaluation tasks? If so, what does that indicate?
2. Split scores into technical checks and convention checks (`rule_`). Which group do curator-generated skills help? Are **new** evaluation-task convention checks helped by the skills, and why?
3. Using traces and `skills_read`, explain one check the skills help pass and one they do not (skill not read, read but not followed, skill missing or wrong).
4. Cost: compare average tokens across conditions. Which condition gives the best score per token? Is multi-agent worth the cost in this experiment?
5. Are there signs of data leakage or overfitting in the generated skills? How did the group prevent them?
6. Noise: compare learning-task scores of the same skill set in Part 3.4 (backed up) and after freezing. How large is the difference, and what does it say about the reliability of the differences in Section 7?

## 9. Limitations and Validity

> List at least 3 limitations and their effect on the conclusions (e.g., only 3 tasks per role, one run per configuration, model noise, tasks designed with conventions by the instructor, single model).

1. TODO
2. TODO
3. TODO

## 10. Conclusion

> At most 5 sentences. Only claim what the data support. Suggest one next improvement.

TODO (pending evaluation runs).

## Appendix

- Commands run (in order): TODO
- Extension challenge (if any): direction chosen, results, comments: TODO / not attempted
- Other notes: TODO
