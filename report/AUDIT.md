# Final audit (requirement by requirement)

Sources checked: `Assignment_DE.docx` (found at `C:\Users\Ravi\Downloads\Assignment_DE.docx`, not in the repo), the course bundle `C:\Users\Ravi\Downloads\material.zip` (dated lecture notes, FreshCart notebooks and flowchart, Prefect labs, `Orchestration.pptx`), the repository, and the saved evidence files.
**Not found anywhere on the machine:** `ETL_End_to_End_Lecture.pdf` ("One dataset, eight transformations, one clean table"), `RiverRetail_DataEngineering_U1.xlsx`, and a Mage Iris reference notebook. The ETL-vs-ELT answer is therefore based on the lecture HTML notes in `material.zip` (see B5).
Status words: COMPLETE / INCORRECT (fixed) / NEEDS STUDENT INPUT / NEEDS INSTRUCTOR CONFIRMATION. "Verified" = checked by Claude against files, logs or live Snowflake/RabbitMQ output during this project.

| # | Requirement (from the assignment) | Actual file / evidence | Validation | Status |
|---|---|---|---|---|
| A1 | Repo structure, >= 5 meaningful commits, `git log --oneline` in report | repo tree; 13 commits (`git log`); `report/report.html` A1 | `git ls-files`, `git log` | COMPLETE |
| A1 | `.gitignore` covers `.env, *.pkl, *.csv, mage.log, __pycache__/` | `.gitignore` | `git check-ignore -v .env`; `.env` not tracked, not on remote | COMPLETE |
| A2 | Six-command table + "teammate after commit?" | report A2 | content is accurate (commit = local snapshot, push = transfer to remote) | COMPLETE (wording is Claude's, student to review) |
| A3 | pytest 120/30, `ci.yml` on every push, green + red screenshots + fixing commit | `tests/test_prepare_data.py`, `.github/workflows/ci.yml`, `report/screenshots/A/A3_*.png` | local pytest 10 passed; screenshots viewed; CI #1 green, #2 red (intentional), #3 green; **CI #6 for `a1af458` green per the student's own check in the Actions tab** (not verifiable from here); red evidence kept | COMPLETE |
| B1 | Baseline numbers (8/6/2/4, 4 orders 7,785.00 126 pts, 25%) | `B1_*`, final notebook output | notebook 16/16 PASS twice (step run + final single-kernel run) | COMPLETE |
| B2 | Trace ORD-1003 (4 points), ORD-1005 vs ORD-1001 | `B2_evidence.txt`, report B2 | text compared to `10_orders_clean.sql`, `20_orders_dedup.sql`, `40_gold.sql` | COMPLETE |
| B3 | `unsupported_currency` rule, before/after, gold, 2nd quarantine row | `elt/sql/10_orders_clean.sql` line 49, `B3_*` | re-checked: `NOT EXISTS` (source, order_id, updated_at) ignores reasons; gold 4/7785.00/126 unchanged | COMPLETE |
| B4 | CUST-02 event, predictions BEFORE run, actuals, row_hash/MERGE explanation | commit `72e290d` (predictions) then `f83bf2f`; `B4_*` | 5/5 match; MERGE `WHEN MATCHED AND t.row_hash <> s.row_hash`; **fixed:** report said hash covers "all business columns", the code hashes every column except `order_id` | COMPLETE (INCORRECT wording fixed) |
| B5 | Sixth check, deliberate failure with PROBLEM, cleanup | `elt/freshcart.py`, `B5_*` | PROBLEM line in notebook output; asserted cleanup; before/after snapshots identical | COMPLETE |
| B5 | ELT vs ETL: why ELT for FreshCart + the lecture's ETL situation | report B5 | `material.zip/30-09-2026/data_transformation_orchestration.html`, section "ETL and ELT: where the transformation runs": ETL "Best when: strict pre-load compliance, small or costly targets, heavy non-SQL processing"; "Sensitive data: ETL can mask or drop PII before it ever lands; ELT: raw PII lands, needs masking policies"; summary "ELT keeps raw data and replays with SQL; ETL masks before landing". The same file's EtLT note gives hashing an Aadhaar number / dropping a card number. The ELT reasons match the project (raw bronze, SQL re-runs) | COMPLETE, NEEDS STUDENT CONFIRMATION that this is the lecture they mean (the named PDF/xlsx were not found) |
| B | Final notebook with all outputs | `elt/freshcart_elt.ipynb` | 41/41 code cells executed in order, 0 errors; single kernel, `FRESHCART_FINAL` | COMPLETE |
| B | "include screenshots of the outputs" (B1) | `B1_notebook_part1-3.png` (renders of the executed notebook) | no Snowsight screenshot exists | NEEDS INSTRUCTOR CONFIRMATION |
| C1 | Block graph with types and tests; `mage run ... --test` output | report C1, `C1_mage_run_test.txt`, `iris_project/iris_classifier_run.ipynb` | notebook 7/7 cells executed, 0 errors, real CLI output | COMPLETE |
| C2 | max_depth 1-5 table + gate explanation | `C2_*`, notebook cell 5 | table equals `C2_summary.txt` and the notebook; depth 1: exit 1, no CSV, no "Saved", no confusion matrix | COMPLETE |
| C2 | Accuracy threshold | none in the assignment | 0.90 is a project design choice, reference notebook not available (not in `material.zip`); **depth-1 pass/fail depends on it**; report now says so | COMPLETE, NEEDS INSTRUCTOR CONFIRMATION if a specific threshold is expected |
| C3 | `evaluate_model` branch, metadata.yaml, confusion matrix, metrics, UI screenshot "through the Cloudflare tunnel" | `metadata.yaml`, `C3_*`, `C3_mage_ui_pipeline_graph.png` | **fixed:** report now shows the metadata block (it only named the file before); UI evidence is from `http://localhost:6789`, no tunnel | metadata etc. COMPLETE; tunnel NEEDS INSTRUCTOR CONFIRMATION (assignment wording is "through the Cloudflare tunnel"; not claimed satisfied) |
| C4 | Own block with `@test`, CI still passes | `validate_data.py`, `C4_*` | full run exit 0; CI #6 green (student-checked) | COMPLETE |
| D1 | 6-key routing on paper (before running) + explanation of the two-word key | `answers.md`, report D1, `D1_routing_verification.txt` | live broker: 6/6 PASS (broker = paper = model); unit test 9 passed | COMPLETE |
| D2 | dispatcher (2 s, JSON, topic exchange), driver (private queue, ACK), 3+ drivers for 2 min | `stream/dispatcher.py`, `stream/driver.py`, `D2_*` | 59 messages, 6 drivers, 0 unexpected deliveries, all ACKed; **fixed:** time window in report now matches the log (dispatcher 05:23:59 to 05:26:00 UTC); example log lines added | COMPLETE (log files, not terminal screenshots) |
| D3 | NACK(requeue=False) for missing zone, ACK otherwise, bad message every 10; crash and requeue answers | `D3_*` | live run 3 of 35 malformed, NACKed; scripted demo: crash gives `redelivered=True`, `requeue=True` loop 4 of 4; `grep` finds no DLX/dead-letter code, so no dead-letter claim is made | COMPLETE |
| Bonus | Consumer, 1-minute collect, `write_landing()`, `load_file()`, transform SQL, gold, run twice no double count | `stream/order_consumer.py`, `stream/bonus_demo.py`, `Bonus/*` | gold 4/7785.00/161 -> 7/9535.00/205 -> 7/9535.00/205; asserted cleanup; baseline restored (independent check) | COMPLETE (scripts + logs; the assignment does not require a notebook) |
| E | Report <= 8 pages (body), numbered A-D answers, ONE integration diagram, half-page reflection, appendix | `report/23BCS095_Gunti_Ravi_Kumar_Pipelines.pdf` | PyMuPDF: 25 pages = 5 body + 20 appendix, text selectable, pages inspected, no placeholders; **reflection rewritten** to say what actually happened (it previously said "I found the cause by printing the columns", which was not true: the traceback showed it and Claude diagnosed it) | COMPLETE |
| E | Viva | n/a | student must be able to explain everything | STUDENT |
| Sub. | PDF named `RollNo_Name_Pipelines.pdf`, repo link, notebooks, Mage project, stream scripts | all present | repo is private: must be shared with the instructor | NEEDS STUDENT ACTION (share repo) |
| Sub. | Repo public or shared with the instructor | private | cannot be verified from here | NEEDS STUDENT ACTION |

## Corrections made in this audit
1. Report B4: hash columns stated exactly (all except `order_id`).
2. Report B5: the placeholder is replaced by an answer backed by the lecture notes (cited); ELT reasoning unchanged and checked against the project.
3. Report C2: the 0.90 gate is described as a design choice, no instructor threshold implied; "no confusion matrix" added to the depth-1 evidence.
4. Report C3: `metadata.yaml` block for `train_model` and `evaluate_model` shown (required: "Show your edited metadata.yaml").
5. Report D2: time window fixed; real log lines for one message added.
6. Report A3: latest CI run mentioned as student-checked, without a screenshot.
7. Reflection: rewritten to factual wording, AI assistance stated; diagnosis no longer attributed to the student.
8. `make_pdf.py`: the git log in the report now states the commit it was taken at; the report cannot list its own commit.
