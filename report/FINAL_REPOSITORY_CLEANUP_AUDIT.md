# Final repository cleanup and compliance review

Reviewed commit: `a560b03` (= `origin/main`, CI run #8 success). Assignment source: `C:\Users\Ravi\Downloads\Assignment_DE.docx` (31,477 bytes; read, not guessed). This file was updated after the owner's cleanup decisions (section 10).
Class codes: **A** required for submission, **B** required for reproducibility, **C** required evidence, **D** optional but useful, **E** safe to remove, **F** uncertain (kept at first review; decided in section 10).

## 1. Assignment requirement-to-file mapping
| Part / item | Required deliverable | Repository path | Complete | Submission | Reproduce |
|---|---|---|---|---|---|
| Sub. | FreshCart notebook, all outputs visible | `elt/freshcart_elt.ipynb` (41/41 code cells executed, 0 errors) | yes | yes | yes |
| Sub. | Mage project and notebook with outputs | `iris_project/` (project), `iris_project/iris_classifier_run.ipynb` (7/7 executed) | yes | yes | yes |
| Sub. | `stream/dispatcher.py`, `stream/driver.py` | `stream/dispatcher.py`, `stream/driver.py` | yes | yes | yes |
| Sub. | Report PDF `RollNo_Name_Pipelines.pdf`, <= 8 body pages | `report/23BCS095_Gunti_Ravi_Kumar_Pipelines.pdf` (27 pp: 6 body + 21 appendix) | yes | yes | source: `report/report.html`, `report/make_pdf.py` |
| Sub. | Repo link, public or shared | https://github.com/Ravikumar-2016/freshcart-pipelines (public, checked) | yes | yes | n/a |
| A1 | Structure; `.gitignore` entries; >= 5 commits; `git log` in report | `README.md`, `.gitignore`, `requirements.txt`, `elt/`, `iris_project/`, `stream/`, `tests/`, `.github/workflows/ci.yml`; 17 commits | yes | yes | yes |
| A2 | Command table + commit/push answer | PDF section A2 (source `report/report.html`) | yes (wording partial, see audit) | yes | n/a |
| A3 | pytest test; `ci.yml`; green + red screenshots, fixing commit | `tests/test_prepare_data.py`, `.github/workflows/ci.yml`, `report/screenshots/A/A3_green.png`, `A3_red.png`, `A3_final_green.png` | yes | yes | yes |
| B1 | Baseline run + numbers + output screenshots | `elt/freshcart.py`, `elt/mock_data.py`, `elt/sql/*.sql` (7), notebook, `report/screenshots/B/B1_*` | yes | yes | yes |
| B2 | ORD-1003 / ORD-1005 trace | PDF B2, `report/screenshots/B/B2_evidence.txt` | yes | yes | n/a |
| B3 | `unsupported_currency` rule, before/after | `elt/sql/10_orders_clean.sql` (line 49), `report/screenshots/B/B3_*` | yes | yes | yes |
| B4 | CUST-02 event, predictions, table, explanation | `elt/mock_data.py` (`B4_NEW_EVENT`), notebook B4 section, `report/screenshots/B/B4_*`, commit `72e290d` (predictions) | yes | yes | yes |
| B5 | Sixth check, failure + PROBLEM, cleanup, ELT/ETL answer | `elt/freshcart.py` (`quality_checks`, `transform`), notebook B5 section, `report/screenshots/B/B5_*` | yes | yes | yes |
| C1 | Block graph; `mage run ... --test` output | PDF C1, `report/screenshots/C/C1_mage_run_test.txt`, Mage notebook | yes | yes | yes |
| C2 | max_depth 1-5 table + explanation | `report/screenshots/C/C2_depth_1..5.txt`, `C2_summary.txt`, Mage notebook | yes | yes | yes |
| C3 | `evaluate_model`, metadata.yaml, confusion matrix, UI screenshot via Cloudflare | `iris_project/transformers/evaluate_model.py`, `iris_project/pipelines/iris_classifier/metadata.yaml`, `C3_eval_depth_2/3.txt`, `C3_cloudflare_tunnel.png`, `C3_mage_ui_pipeline_graph.png` | yes | yes | yes |
| C4 | Own block with `@test`, committed, CI passes | `iris_project/transformers/validate_data.py`, `C4_*.txt` | yes | yes | yes |
| D1 | Routing table (paper) + two-word key | PDF D1, `stream/topic.py`, `stream/verify_routing.py`, `report/screenshots/D/D1_routing_verification.txt`, `tests/test_topic_routing.py` | yes | yes | yes |
| D2 | Dispatcher + 3 drivers, 2 minutes, console proof | `stream/dispatcher.py`, `stream/driver.py`, `stream/common.py`, `stream/verify_logs.py`, `report/screenshots/D/D2_*` | yes | yes | yes |
| D3 | NACK/ACK, bad message every 10, crash/requeue answers | `stream/driver.py`, `stream/d3_demo.py`, `report/screenshots/D/D3_*` | yes | yes | yes |
| E | <= 8 pages, numbered answers, ONE diagram, reflection | PDF; `report/report.html` | yes | yes | yes |
| Bonus | Consumer, 1 minute, `write_landing()`, `load_file()`, gold, run twice | `stream/order_consumer.py`, `stream/bonus_demo.py`, `report/screenshots/Bonus/*` | yes | yes | yes |

## 2. Inventory summary
- **Tracked in `a560b03`:** 135 files. **After this cleanup:** 126 (9 removed). Folder counts now: root 9, `.github` 1, `elt` 11, `iris_project` 21 (9 real files + 12 empty Mage scaffold `__init__.py`), `stream` 12, `tests` 2, `report` docs 9, `report/screenshots` A 3, B 19, C 14, D 20, Bonus 2, Final 3.
- **Ignored, local only (kept):** `.env`, `.venv/`, `elt/landing/` (46 KB of raw landing files), `elt/reference/` (536 KB: flowchart, lecture PDF, spreadsheet), three reference notebooks in `elt/`.
- **Generated/cached (removed, see section 4):** `report/build/` (18 MB), `.pytest_cache/`, `iris_project/.ssh_tunnel/`.
- **No** `.csv`, `.pkl`, `mage.log`, `__pycache__`, `*.bak` or temp file exists outside `.venv`.

## 3. Files retained and why (all classified)
- **A (submission):** the PDF; `elt/freshcart_elt.ipynb`; `iris_project/` (blocks, `metadata.yaml`, pipeline `metadata.yaml`, executed notebook); `stream/dispatcher.py`, `stream/driver.py`; `tests/test_prepare_data.py`; `.github/workflows/ci.yml`; `README.md`; `requirements.txt`; `.gitignore`.
- **B (reproducibility):** `elt/freshcart.py`, `elt/mock_data.py`, `elt/sql/00..40_*.sql` (7); the 12 empty `__init__.py` files and `iris_project/metadata.yaml` (Mage scaffold, needed for imports and `mage run`); `stream/common.py`, `topic.py`, `verify_routing.py`, `verify_logs.py`, `d3_demo.py`, `order_consumer.py`, `bonus_demo.py` (the scripts that produce the D and bonus evidence); `tests/test_topic_routing.py`; `pytest.ini`; `requirements-elt.txt`, `requirements-mage.txt`, `requirements-stream.txt`; `.env.example`; `report/report.html` and `report/make_pdf.py` (rebuild the PDF).
- **C (evidence):** all 61 files under `report/screenshots/` (A 3, B 19, C 14, D 20, Bonus 2, Final 3). Files that look duplicated are not: `C2_depth_2..5.txt` and `C3_eval_depth_2/3.txt` have the same size but different depth/accuracy content; the three A3 images are three different CI pages.
- **D (optional but useful):** `elt/test_connection.py`, `stream/check_connection.py`, `stream/mgmt.py` (connectivity diagnostics, cited in the README or imported by another script); `report/answers.md`, `report/checklist.md` (running notes), `report/USER_REVIEW_REQUIRED.md` (viva study guide), `report/FINAL_ASSIGNMENT_COMPLIANCE_AUDIT.md` (kept as requested).
- **F (uncertain, kept):** `PROJECT_HANDOVER_FOR_NEW_CLAUDE.md`, `report/AUDIT.md`, `report/part_b_plan.md` (see section 5); local ignored `elt/reference/*`, the three reference notebooks, `elt/landing/`.

## 4. Files removed and why (cleanup plan and result)
| Path | Why unnecessary | Referenced / depended on? | Check done | Removed |
|---|---|---|---|---|
| `report/build/` (ignored, 18 MB: an Edge profile folder and `Pipelines_report_DRAFT.pdf`, an obsolete draft PDF) | Cache created by `make_pdf.py`; the draft PDF is an old report version with a different name | only `make_pdf.py`, which recreates the folder | regenerated the PDF afterwards: text identical to the committed PDF (header and git-log line normalised), 27 pages; the committed PDF is byte-identical (same SHA-256) | yes |
| `.pytest_cache/` (ignored) | regenerated on every pytest run | no | pytest runs fine | yes |
| `iris_project/.ssh_tunnel/` (ignored, one file `aws_emr.json` = `{}`) | auto-created by Mage; empty | no | n/a | yes |
| 9 tracked `.gitkeep` files: `.github/workflows`, `elt`, `iris_project`, `stream`, `tests`, `report/screenshots/{A,B,C,D}` | placeholders for empty folders; every one of these folders now has other tracked files (counts checked: 1, 11, 21, 12, 2, 3, 19, 14, 20) | no | clean-room test from `HEAD` still passes | yes (unstaged deletions) |

## 5. Files intentionally retained despite looking like development artifacts
| Path | Looks like | Why it stays |
|---|---|---|
| `PROJECT_HANDOVER_FOR_NEW_CLAUDE.md` (39 KB, tracked, public) | AI-session handover | **F.** Stale (it still describes Part D as uncommitted and C3 as pending) and referenced by no file. It does record implementation history that may help at the viva. Removal looks safe but is your decision. |
| `report/AUDIT.md` (tracked) | older audit | **F.** Fully superseded by `FINAL_ASSIGNMENT_COMPLIANCE_AUDIT.md`, but `report/checklist.md` mentions it; remove both together if you agree. |
| `report/part_b_plan.md` (tracked) | early planning note | **F.** Contains outdated statements ("planning only, not executed"); referenced by `checklist.md` and the handover. |
| `elt/reference/` (ignored): `freshcart_elt_flowchart.html`, `ETL_Pipeline_EndToEnd_Demo.pdf`, `RiverRetail_DataEngineering_U1.xlsx` | course material | course reference material; not tracked; removing it needs your OK. |
| `elt/freshcart_elt_colab (1).ipynb`, `elt/freshcart_elt_commented.ipynb`, `elt/freshcart_elt_simple_(1).ipynb` (ignored) | duplicated notebooks | **F.** Course reference notebooks from which the project was built. **They contain someone else's Snowflake login**; they are untracked and ignored (0 commits contain them) but exist on disk. |
| `elt/landing/` (ignored, 30 small `.json.gz`) | generated data | raw landing files from the real runs: handy to show the "write_landing" output at the viva; regenerated by any run. |
| `report/screenshots/D/D0_connectivity_diagnosis.txt` | old diagnostic | genuine evidence of the earlier network block (kept as history). |
| `report/screenshots/Final/FINAL_notebook.html` (500 KB) | generated HTML | evidence of the final notebook run, cited by the report. |
| `elt/test_connection.py`, `stream/check_connection.py`, `stream/mgmt.py` | debugging helpers | documented in the README/notes or imported by another script. |
| `.env` | secret file | local only and git-ignored (not tracked, 0 commits). |

## 6. Verification results (after cleanup)
- **pytest:** 10 passed (working tree) and 10 passed in a clean-room copy extracted from `HEAD` (135 files, no ignored files), so the tracked files are sufficient to run the tests.
- **Compile:** every script in `elt/`, `stream/`, `tests/`, `iris_project/*/` and `report/make_pdf.py` compiles.
- **Repository checker (94 checks, 0 failures):** 7 SQL scripts present; both notebooks executed in order with 0 errors; both notebooks and the PDF unchanged (same SHA-256 as before cleanup, and no diff against `HEAD`); Mage metadata has the 6 blocks, `train_model` -> `save_results` + `evaluate_model`, and each block file exists with an `@test`; all 11 stream scripts and the D/Bonus evidence exist; every image and evidence path cited by `report/report.html` exists; every README path exists; `ci.yml` (push, Python 3.12, `pip install -r requirements.txt`, pytest) and `pytest.ini` correct; A1 structure and the five required `.gitignore` entries present; no secret value in any of the tracked files (PDF and PNG bytes included) or in any commit; `.env` untracked and still present locally.
- **Reproducibility of the report:** after removing `report/build/`, `make_pdf.py` regenerated a 27-page PDF whose text equals the committed PDF.
- **Not rerun:** Snowflake, RabbitMQ and Mage executions (not needed; the evidence stands and no destructive step was taken). `FRESHCART_DB` was not touched.

## 7. Final repository structure (tracked, after cleanup: 126 files)
```
freshcart-pipelines/
  README.md  .gitignore  .env.example  pytest.ini  PROJECT_HANDOVER_FOR_NEW_CLAUDE.md (F)
  requirements.txt  requirements-elt.txt  requirements-mage.txt  requirements-stream.txt
  .github/workflows/ci.yml
  tests/            test_prepare_data.py  test_topic_routing.py
  elt/              freshcart_elt.ipynb  freshcart.py  mock_data.py  test_connection.py
                    sql/ 00_setup 10_orders_clean 20_orders_dedup 30_customers_scd2 31_fx_daily 32_pincode_geo 40_gold (.sql)
  iris_project/     metadata.yaml  iris_classifier_run.ipynb  pipelines/iris_classifier/metadata.yaml
                    data_loaders/load_iris.py  data_exporters/save_results.py
                    transformers/ prepare_data validate_data train_model evaluate_model (.py)  (+12 empty __init__.py)
  stream/           dispatcher.py driver.py common.py topic.py order_consumer.py bonus_demo.py
                    verify_routing.py verify_logs.py d3_demo.py check_connection.py mgmt.py (+__init__.py)
  report/           23BCS095_Gunti_Ravi_Kumar_Pipelines.pdf  report.html  make_pdf.py
                    answers.md  checklist.md  USER_REVIEW_REQUIRED.md  FINAL_ASSIGNMENT_COMPLIANCE_AUDIT.md
                    FINAL_REPOSITORY_CLEANUP_AUDIT.md (new)  AUDIT.md (F)  part_b_plan.md (F)
                    screenshots/ A(3) B(19) C(14) D(20) Bonus(2) Final(3)
```
Local only (ignored): `.env`, `.venv/`, `elt/landing/`, `elt/reference/`, three reference notebooks.

## 8. Remaining uncertainty and open points
1. **README is incomplete for reproduction.** It has setup and Part D/bonus commands, but nothing for Part B (install `requirements-elt.txt`, fill `.env`, open `elt/freshcart_elt.ipynb`), Part C (install `requirements-mage.txt`, `mage run iris_project iris_classifier --test`) or rebuilding the PDF. I did not edit it (outside the cleanup scope). Suggested addition: a short "Part B", "Part C" and "Report" block with those commands.
2. **Three F files** (`PROJECT_HANDOVER_FOR_NEW_CLAUDE.md`, `report/AUDIT.md`, `report/part_b_plan.md`) look stale; they are kept until you decide. If you remove `AUDIT.md` or `part_b_plan.md`, the mentions in `report/checklist.md` must be edited.
3. **B5 lecture source.** The two files now in `elt/reference/` do not answer "when ETL wins": the PDF is an interactive 2-page ETL demo (8 raw rows to 6 trusted rows) with no ETL-versus-ELT statement, and the spreadsheet has five sheets (`1_Raw_Ingestion`, `2_Transformation`, `3_Batch_vs_Streaming`, `4_DAG_Tasks`, `5_Observability`) with none either. The report's ETL situation still rests on the course notes in `material.zip` (`30-09-2026/data_transformation_orchestration.html`); confirm that is the lecture meant.
4. **Reference notebooks with a third party's Snowflake login** remain on disk (untracked). Deleting them locally is up to you.
5. **Counts of commits** in this document refer to the history at `a560b03` (17 commits); the audit documents otherwise say 16.
6. **Earlier items still open** (not cleanup): own-words wording (A2, C2, integrity rule), D1 timing evidence, instructor questions (renders vs Snowsight screenshots, Mage accuracy threshold).

## 9. Git status and whether a new commit is needed
Working tree: 9 unstaged deletions (the `.gitkeep` files) plus this new file. **A new commit is needed to record them**, optionally together with the README addition and a decision on the three F files. Suggested message: `chore: remove redundant placeholders and add cleanup audit`. Nothing has been committed or pushed.

## 10. Update: final cleanup decisions applied (owner's instructions)
**A. Obsolete files removed.** `PROJECT_HANDOVER_FOR_NEW_CLAUDE.md`, `report/AUDIT.md`, `report/part_b_plan.md`. Dependency check before removal: only `report/checklist.md` mentioned them (lines 23, 82, 83); no Python file, `make_pdf.py` (it reads only `report/report.html`), README, notebook or required deliverable referenced them. `report/checklist.md` was updated to point to `FINAL_ASSIGNMENT_COMPLIANCE_AUDIT.md` and this file. Sections 3, 5, 7, 8 and 9 above describe the state before this decision; where they list these three files as "F, kept" they are now **removed**.

**B. README rewritten** with reproduction steps for Parts A to D, the bonus and the report. Every command was run or checked before it was documented:
- `python -m pytest` (10 passed); `pip install --dry-run` for `requirements.txt`, `requirements-elt.txt`, `requirements-stream.txt` (resolve, no conflicts); `python elt\test_connection.py` (read-only connection check, OK).
- `mage run iris_project iris_classifier --test` from PowerShell (exit 0, 6 `tests passed` lines, accuracy 1.0, CSV written then deleted). **Verified finding:** in Windows PowerShell 5.1 the form `--runtime-vars '{"max_depth": 2}'` is silently ignored (depth 3 runs); the escaped form `'{\"max_depth\": 2}'` gives `max_depth=2 test_accuracy=0.9667`. The README documents the escaped form with a warning.
- Mage notebook re-run: `nbconvert --execute` fails because the kernel starts in `iris_project/` and the notebook checks for the project root (also with `--ExecutePreprocessor.cwd`); the `nbclient` one-liner with an explicit working directory re-executes all 7 cells with 0 errors (output written to scratch; the committed notebook was unchanged). That one-liner is what the README documents (it writes a new file `iris_classifier_rerun.ipynb`).
- Stream scripts: `--help` of `dispatcher.py`, `driver.py`, `order_consumer.py`; `check_connection.py` (OK), `verify_routing.py` (6/6 PASS), a live smoke test (`driver.py` plus `dispatcher.py --count 3`: 2 messages received and ACKed, 1 unroutable), `verify_logs.py report/screenshots/D D2` (PASS from the project root).
- `make_pdf.py` with a throwaway name (6 body pages, 27 total; committed PDF byte-identical afterwards).
- **Not executed (documented from the source code, to avoid changing Snowflake):** `bonus_demo.py` and a full `order_consumer.py` run; both were executed and recorded earlier in the project (`report/screenshots/Bonus/`). All 42 path tokens and all environment variable names in the README exist (`.env.example` contains every variable named).

**C. Reference notebook security.** The three untracked, git-ignored course notebooks in `elt/` were scanned. Findings (locations only): the Colab notebook held the third party's Snowflake account identifier (login cell and an output), username (login cell and 2 outputs) and a plaintext password (login cell); the other two held the account identifier and username in their login cell and the username in one output. Other "hits" were not credentials (the `getpass` prompt text, a placeholder account example, fictional sample-data emails, the public role name `ACCOUNTADMIN`). **Redaction applied to the local copies:** 8, 3 and 3 replacements with `<SNOWFLAKE_ACCOUNT>`, `<SNOWFLAKE_USER>`, `<SNOWFLAKE_PASSWORD>`; cell, code-cell and output counts unchanged; all three still valid notebooks; re-scan finds 0 occurrences; they remain git-ignored and uncommitted (0 commits ever contained them). The other reference files (`elt/reference/` PDF, spreadsheet, flowchart) contain none of these values. My own scratch copies of the original notebooks (extracted course zip, text dumps) were deleted. **Not touched:** `C:\Users\Ravi\Downloads\material.zip`, which is outside the repository and still contains the original notebooks with the third party's login.

**D. Preserved.** All 61 evidence files, the 7 SQL scripts, both executed notebooks (byte-identical), source, tests, CI, Mage metadata, the PDF (byte-identical), report source, the compliance audit and the viva study guide. Snowflake and RabbitMQ were not modified (only read-only connection and routing checks on temporary queues).

**Tracked file count:** 135 at `a560b03`; 12 removed (9 `.gitkeep` + 3 obsolete files) = 123 existing tracked files, plus this new audit file = 124 files after the commit (checked with `git ls-files`).
