# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| TODO | TODO | TODO |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: TODO (cấu hình đọc từ `.env`; các giá trị này chưa được kiểm tra cho báo cáo). Mọi lần chạy trong báo cáo đều chạy trong Docker.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: Deep Agents 0.7.21 (ghim trong `pyproject.toml`); host Windows, lab chạy trong ảnh Docker `lab-deepagents` (Linux, Python 3.12).
- Số lần chạy tác vụ đã dùng / ngân sách: 9 lần chạy học chính thức (baseline, subagents, skills-auto × `code-learn`, `data-learn`, `logs-learn`), 1 lần chạy lặp riêng (`data-learn`, skills-auto) và các lần chạy debug; trần token mặc định 200.000, đặt 350.000 cho lần chạy lặp.
- Commit của tag `freeze`: TODO (chưa tạo tag; sẽ điền sau).

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): hướng dự đoán là **không tăng điểm** — `subagents` sẽ không vượt `baseline` về điểm trên tác vụ đánh giá (delta kỳ vọng 0 trong phạm vi nhiễu lặp), với chi phí khoảng 1,9×–5,4× token. Bằng chứng từ các lần chạy học: điểm không đổi (check +1 của code-learn là `tests_not_modified`, một bản sửa lỗi hạ tầng, không phải nhờ tác tử; data-learn và logs-learn giống hệt baseline), trong khi token tăng 1,9×–5,4×. Cơ chế: các subagent explorer/implementer/reviewer cải thiện quy trình (cô lập ngữ cảnh, kiểm chứng độc lập) nhưng không bổ sung kiến thức về quy ước nằm ngoài workspace, và mọi lỗi lặp lại đều là check quy ước `rule_*`. Tiêu chí bác bỏ: lợi thế điểm đánh giá ≥2 check so với `baseline`, hoặc có check `rule_*` chỉ `subagents` đạt, vượt quá mức nhiễu lặp có thể giải thích.
- H2 (skills-auto so với baseline): hướng dự đoán là **không tăng điểm** (delta kỳ vọng ~0). Bằng chứng: cả ba lần chạy học `skills-auto` chính thức đều đọc hai skill (`skills_read = 2`) nhưng vẫn giữ đúng các check `rule_*` thất bại và điểm như `baseline`. Cơ chế: cơ chế nạp dần khiến tác tử đọc các checklist tổng quát, nhưng các check thất bại mã hóa quy ước không có trong workspace và curator không được biết; skill tổng quát không thể suy ra chúng. Tiêu chí bác bỏ: điểm đánh giá của `skills-auto` ≥ `baseline` + 2 check, hoặc các check `rule_*` mới đạt với bằng chứng từ vết rằng một quy tắc trong skill đã gây ra việc đạt đó.
- H3 (tác vụ học so với tác vụ đánh giá): hướng dự đoán là **không chuyển giao** — kết quả tác vụ học sẽ không dự báo được kết quả tác vụ đánh giá, và mọi lỗi `rule_*` quan sát trên tác vụ học sẽ tiếp diễn trên tác vụ đánh giá (kể cả các quy ước chỉ có ở tác vụ đánh giá mà skill chưa từng thấy). Bằng chứng: lỗi ở tác vụ học đến từ thiếu tài liệu quy ước, không phải thiếu quy trình. Tiêu chí bác bỏ: kết quả đánh giá cải thiện vượt mức nhiễu lặp trong khi kết quả học không đổi (chuyển giao dương), hoặc các check `rule_*` ở tác vụ đánh giá đạt nhờ hướng dẫn của skill.

_Kết quả tác vụ đánh giá hiện chưa biết; các dự đoán trên được đăng ký trước khi xem bất kỳ điểm đánh giá nào._

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`, `execute` và `task`. `execute` chạy lệnh shell trong sandbox; `task` giao việc cho subagent.
2. Công cụ `task` cung cấp subagent mặc định `general-purpose` cho việc nhiều bước. Mỗi lần gọi là một phiên cô lập: subagent chỉ thấy prompt giao việc và trả một báo cáo cuối, nên tác tử chính phải gửi đủ mục tiêu, ngữ cảnh, giới hạn và định dạng kết quả.
3. System prompt mặc định rỗng. Mô tả `task` ghi: “the agent sees only the prompt you give it and returns a single final report.” Mô tả `execute` cho biết công cụ chạy lệnh trong sandbox và trả stdout/stderr cùng exit code. Hành vi của tác tử do đó chịu ảnh hưởng từ mô tả công cụ, không chỉ system prompt.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

Chín lần chạy học chính thức đã hoàn tất (baseline, subagents, skills-auto × `code-learn`, `data-learn`, `logs-learn`); mọi `run.json` đều có `error = none`:

| Tác vụ | baseline | subagents | skills-auto | token b / s / sa | tool calls b / s / sa | subagent_calls b / s / sa | skills_read (sa) |
|---|---|---|---|---|---|---|---|
| code-learn | 6/10 | 7/10 | 7/10 | 193.914 / 1.044.076 / 287.827 | 31 / 33 / 37 | 0 / 2 / 0 | 2 |
| data-learn | 5/8 | 5/8 | 5/8 | 144.114 / 272.691 / 159.265 | 17 / 16 / 23 | 0 / 1 / 0 | 2 |
| logs-learn | 6/9 | 6/9 | 6/9 | 145.933 / 392.240 / 183.841 | 18 / 16 / 21 | 0 / 1 / 0 | 2 |

Mỗi dòng dưới đây là một check thất bại lặp lại ở **cả ba điều kiện** (baseline code-learn có thêm `tests_not_modified`, xem bên dưới):

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | rule_type_hints | E | `RULE: every public function ... type annotations`; tổng kết cuối không có bước bổ sung annotation. |
| code-learn | rule_regression_tests | E | `RULE: add tests/test_regressions.py ...`; không tool call nào tạo tệp này trong vết. |
| code-learn | rule_changelog | E | `RULE: ... '- fix(<function name>): <short description>'`; CHANGELOG chỉ được thêm bullet thường. |
| data-learn | rule_money_in_cents | E | `RULE: money values ... integer cents`; vết ghi `North Q1 2024: ... 3130.24` (USD thập phân). |
| data-learn | rule_meta_block | E | `RULE: answer.json has an object meta ...`; vết subagents: “wrote exactly the five requested keys”. |
| data-learn | rule_clean_csv | E | `RULE: write workspace/clean.csv ...`; không lần chạy nào tạo `clean.csv`. |
| logs-learn | rule_service_names | E | `RULE: service names ... '-' replaced by '_'`; vết vẫn ghi `inventory-service`, `payment-service`. |
| logs-learn | rule_sorted_errors | E | `RULE: errors is sorted by service, then timestamp_utc`; vết không có bước sắp xếp. |
| logs-learn | rule_schema_header | E | `RULE: ... "schema_version": 2 và "generated_by": "log-triage"`; vết subagents: “found none” khi tìm tài liệu quy ước. |

Nhận xét: **toàn bộ lỗi tác tử thuộc nhóm E** (check `rule_*`, `detail` bắt đầu `RULE:`), tức nhóm E chiếm đa số tuyệt đối; mọi check kỹ thuật đạt ở cả ba điều kiện (bằng chứng phủ định: code-learn 6/6 kỹ thuật — không tính `tests_not_modified` là lỗi hạ tầng; data-learn 5/5; logs-learn 6/6). Mẫu lỗi chung: đề nhắc “Acme … conventions” nhưng workspace không có tài liệu quy ước; tác tử tự kiểm phần kỹ thuật rồi kết thúc, bỏ qua quy ước ẩn. Vết subagents ghi rõ *“no conventions document exists anywhere in the sandbox … so I wrote exactly the five requested keys”* và *“searched the whole sandbox … found none”*. Về khả năng phòng ngừa: một skill tổng quát chỉ có thể nhắc các bước kiểm tra (ví dụ checklist hợp đồng đầu ra), **không thể** phòng ngừa triệt để nhóm E vì nội dung quy ước ẩn không có trong workspace.

`code-learn` 6/10 → 7/10: điểm ghi nhận giữ nguyên (baseline 6/10; subagents và skills-auto 7/10). So từng check, **chỉ** `tests_not_modified` đổi FAIL→PASS, 9 check còn lại giống hệt; không vết nào ghi/sửa `tests/*` (chỉ `read_file`). Dòng thời gian: baseline 18:21–18:23, khôi phục LF cho `tasks/code-learn/workspace/tests/test_report.py` lúc 18:31, subagents 19:15–20:04, skills-auto 20:36–20:44. Việc chênh lệch này khớp với dòng thời gian CRLF/LF của checkout Windows, nhưng **chỉ là suy luận** (sandbox cũ đã xóa, không băm lại được), dù được hỗ trợ bởi dòng thời gian và việc workspace sạch đạt check này sau khôi phục LF; **không** quy điểm tăng này cho subagents hay skills. Check này không tính vào A–G vì là lỗi hạ tầng (GUIDE 2.2).

Giả thuyết skill tiềm năng (dựa trên bằng chứng, tối đa 3):
1. **Tìm tài liệu quy ước trước khi kết thúc**: quét sandbox (kể cả thư mục ẩn) tìm file conventions/spec; nếu không có, nói rõ trong câu trả lời cuối rằng quy ước không tồn tại và liệt kê yêu cầu nào là chắc chắn.
2. **Đối chiếu yêu cầu hữu hình**: checklist từ instruction/README/docstring rồi kiểm từng mục trên artifact; phân biệt “thiếu tài liệu quy ước” với “yêu cầu đã biết”, không đoán/bịa quy tắc ẩn.
3. **Tự kiểm cuối trên artifact thật**: đọc lại file đã ghi (`answer.json`, `errors.json`, source) và nêu rõ phần chưa kiểm chứng được; vết cho thấy tác tử tự kiểm đúng phần kỹ thuật nhưng không nêu các quy ước còn thiếu.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế): ba subagent trong `src/lab/subagents.py` — **explorer** (chỉ đọc tài liệu/dữ liệu/test, báo phát hiện kèm bằng chứng, không sửa), **implementer** (sửa file theo mục tiêu, chạy kiểm, báo file đã sửa và lỗi còn lại), **reviewer** (kiểm độc lập theo yêu cầu và trường hợp biên, chỉ báo vấn đề, không sửa). `description` nêu tình huống gọi; `system_prompt` ghi nhiệm vụ/giới hạn/định dạng báo cáo.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0): baseline 0/0/0; điều kiện `subagents` — code-learn **2**, data-learn **1**, logs-learn **1**; `skills-auto` 0 (điều kiện `single`). Chỉ code-learn giao 2 việc, gồm một việc triển khai và một việc kiểm tra độc lập.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): trace `results/subagents/*/trace.md` — code-learn `:337` giao implementer kèm “CONTEXT / RULES” (đường dẫn tương đối, docstring, ví dụ định dạng) và `:523` giao việc review “REPORT PROBLEMS ONLY — do not edit any file”; data-learn `:231` và logs-learn `:301` giao việc kiểm chứng độc lập kèm đường dẫn tương đối và yêu cầu đối chiếu schema/ordering/field names. Brief có thông tin cần thiết; `render_trace` cắt args ở 1500 ký tự nên `subagent_type` của 3/4 lần gọi không hiện trong vết (chỉ lần gọi code-learn `:338` hiện `implementer`) — **không đủ bằng chứng khẳng định vai trò đã dùng cho các lần còn lại**. Việc kiểm tra báo cáo con: code-learn cho thấy sau review `:523`, tác tử chính sửa tiếp `:539`/`:542` rồi chạy lại test `:551` (có dùng kết quả kiểm tra); data-learn và logs-learn nhận báo cáo kiểm chứng khớp và không sửa thêm (không chứng minh được mức độ kiểm tra).
- Ảnh hưởng đến token và thời gian: code-learn 1.044.076 token (5,4×) / 501,4s so với 193.914 / 99,3s; data-learn 272.691 (1,9×) / 117,6s so với 144.114 / 71,9s; logs-learn 392.240 (2,7×) / 164,9s so với 145.933 / 69,0s. Điểm không tăng thêm (code-learn +1 là do `tests_not_modified`, không nhờ subagent).

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: theo output CLI do người dùng cung cấp (user-reported), curator được gọi **1 lần**; repo không lưu log CLI, không có commit/tag curator, nên đây là lời khai người dùng chứ không phải bằng chứng Git/on-disk. Một skill `preserve-provided-files` đã bị **xóa**: nội dung gốc cấm sửa “existing test files, input datasets, and fixtures” và chỉ cho phép thay đổi thuần bổ sung (chỉ file tự sinh được sửa), tức cấm cả việc sửa file nguồn hiện có — sai với `code-learn`. Skill này từng bị sửa tay (vi phạm GUIDE 3.3), nên bản đã sửa không được giữ/dùng. **Thời điểm thao tác xóa không được log**; hash bên dưới chỉ chứng minh bộ skill lúc chạy của 3 run cũ đúng bằng hai skill hiện tại (skill đã xóa không được nạp), không chứng minh mốc thời gian xóa.
- Hash skill lúc chạy: cả ba run `skills-auto` ghi `skills_sha256 = a4a40722…`. Đây **không phải** mâu thuẫn nội dung: `hash_skills()` băm cả đường dẫn tương đối nên cùng hai SKILL.md không đổi cho digest khác nhau theo dấu phân cách của hệ điều hành — Windows (`\`) = `ba043656…`, Linux (`/`) = `a4a40722…`; Docker chạy Linux nên ghi `a4a40722…`. Băm từng tệp trong container và trên host trùng nhau, không có bằng chứng về skill thừa: bộ skill lúc chạy của 3 run cũ đúng bằng hai skill hiện tại.
- Nhiễu: một lần chạy lặp `data-learn` (cùng điều kiện `skills-auto`, cùng bộ skill) đạt 5/8, 212.929 token, 24 tool call, `skills_read = 2`, so với 5/8, 159.265 token, 23 tool call của bản chính; lưu riêng ở `results/skills-auto-repeat-data/` và không tính vào bảng chính (mục 4).
- `skills_read` ở cả ba run `skills-auto` = **2** (output-contract-checklist và reproduce-exact-spec-strings). Phân biệt **đọc** và **làm theo**: cả ba tác vụ đã đọc skill nhưng vẫn thất bại đúng các check `rule_*` như baseline; trace không cho thấy áp dụng `cents`/`meta`/`clean.csv` (data), `schema_version`/`generated_by` (logs), `test_regressions`/type hints/changelog format (code).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| output-contract-checklist | Tổng quát: checklist “hợp đồng đầu ra” cho mọi tác vụ giao file/JSON/CSV; tên quy ước Acme (`clean.csv`, `changelog`, `regression tests`) được phép, không có id tác vụ hay đáp án | Đúng về hình thức và khớp loại lỗi `rule_*`; chưa chứng minh hiệu quả vì cả 3 run đọc skill vẫn thất bại các quy ước ẩn | 8 dòng; `description`: “Use before finishing any task that must deliver files or structured output…”; `skills_read = 2` ở cả ba run `skills-auto` |
| reproduce-exact-spec-strings | Tổng quát vừa: tập trung vào nhãn/định dạng/chuỗi chính xác; ví dụ biến đổi separator/lower-casing bắt nguồn từ quy ước log nhưng không nêu tên tác vụ cụ thể | Đúng theo `detail`, không có hướng dẫn gây hại; hiệu quả chưa được chứng minh (đọc nhưng `rule_*` vẫn fail) | 7 dòng; `description`: “Use when the task mandates exact labels, field names, formats…”; `skills_read = 2` ở cả ba run `skills-auto` |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

(TODO: trả lời các câu trên sau khi có kết quả tác vụ đánh giá và bảng so sánh ở mục 7.)

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1. TODO
2. TODO
3. TODO

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

TODO (chờ các lần chạy tác vụ đánh giá).

## Phụ lục

- Lệnh đã chạy (theo thứ tự): TODO
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét: TODO / chưa thực hiện
- Ghi chú khác: TODO
