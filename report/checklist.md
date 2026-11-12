# Requirement tracker

Status: [ ] not started, [~] in progress, [x] done WITH evidence (cite it).

## Submission items
- [ ] GitHub repo link (public or shared) in report
- [ ] `elt/` FreshCart notebook with outputs (.ipynb)
- [ ] `iris_project/` Mage project and notebook with outputs
- [ ] `stream/dispatcher.py`, `stream/driver.py`
- [ ] Report PDF `RollNo_Name_Pipelines.pdf` (max 8 pages excl. appendix)

## Part A
- [x] A1 structure: all required files/folders exist (evidence: repo tree, commit 6d86300)
- [~] A1 five+ commits: 5 so far (4ef2ad1..0c83c3e), log pasted in answers.md; re-paste at the end
- [~] A2 command table + "can teammate see after commit?" answer: drafted in answers.md; student must rephrase in own words
- [x] A3 test_prepare_data.py (120/30): local pytest passes
- [x] A3 ci.yml: runs on push (CI #1 green)
- [x] A3 green run screenshot: report/screenshots/A/A3_green.png (verified: CI #1, 6d86300)
- [x] A3 red run screenshot: report/screenshots/A/A3_red.png (verified: CI #2, b038cf1)
- [x] A3 fixing commit 0c83c3e + restored green run: report/screenshots/A/A3_final_green.png (verified: CI #3 green)
- [ ] Repo visibility: private now; share with instructor or make public

## Part B (needs Snowflake account; reference notebooks now AVAILABLE, see report/part_b_plan.md)
- [x] Reference material inspected: flowchart (13 steps) + 3 notebooks (simple/commented/colab); `elt/freshcart_elt.ipynb` prepared (outputs stripped, login from .env), NOT executed
- [x] Part B dependencies identified (requirements-elt.txt); NOT installed
- [ ] SECURITY: reference notebooks contain someone else's Snowflake login (git-ignored; never commit/use); consider telling the instructor
- [x] Snowflake infrastructure created by student (FRESHCART_WH, FRESHCART_DB; BRONZE/SILVER/GOLD/QUARANTINE) per student's report; not independently verified by me
- [x] Local prep done: snowflake-connector-python 3.12.4 + python-dotenv + pynacl<1.6 installed, `pip check` clean, Mage still imports, pytest passes; `elt/test_connection.py` written; `.env.example` updated; `.env` git-ignored
- [ ] `.env` filled in by student and `python elt\test_connection.py` run successfully (NOT done: no evidence yet)
- [x] Database name/schemas: FRESHCART_DB used; DIM and REF schemas added in elt/sql/00_setup.sql and created (setup ran OK, 9 tables exist)
- [x] Structure: SQL in elt/sql/*.sql, Python in elt/freshcart.py + elt/mock_data.py (mock data from reference notebook, labelled), notebook elt/freshcart_elt.ipynb; `pytest.ini` added so CI only collects tests/ (elt/test_connection.py imports snowflake)
- [ ] Notebook: B1 and B3 sections executed; the final 'run it again' and clean-up cells are intentionally NOT executed yet (B4); final submission needs the notebook fully executed after B3-B5. Snowflake state now: 2 runs in bronze (16 order rows)
- [x] B1 baseline: 8 raw / 6 clean / 2 quarantine / 4 dedup / 4 orders, 7,785.00, 126 pts / 25%: ALL VERIFIED (notebook 16/16 PASS + independent query). Evidence: screenshots/B/B1_notebook_part1-3.png, B1_independent_verification.txt, elt/freshcart_elt.ipynb. Rendered notebook captures, not Snowsight screenshots.
- [~] B2 trace ORD-1003 (4 points) and ORD-1005: evidence screenshots/B/B2_evidence.txt; DRAFT trace in answers.md, student must rewrite in own words
- [x] B3 unsupported_currency rule (elt/sql/10_orders_clean.sql line 49) executed: ORD-1006 reasons before [bad_email,bad_pincode] -> after [bad_email,bad_pincode,unsupported_currency] (silver.orders_checked; quarantine row keeps old reasons); gold unchanged (4 / 7785.00 / 126); no 2nd quarantine row (NOT EXISTS). Evidence: screenshots/B/B3_notebook_section.png, B3_notebook_outputs.txt, B3_independent_verification.txt. [~] explanations are assistant DRAFTS in answers.md: student must rewrite in own words. Not committed yet.
- [x] B4 executed: event added; 5 of 5 committed predictions matched (CUST-02 rows 2; ORD-1002 Gold; 70 pts; total 161; 1 published_at changed = ORD-1002). Idempotence second pass: 0 published_at changes. Bronze 3 runs x 8 order rows = 24 (+5 CRM rows this run). Evidence: screenshots/B/B4_before_published_at.txt, B4_notebook_outputs.txt, B4_notebook_part1-2.png, B4_independent_verification.txt. Predictions kept unedited; actuals in a separate section of answers.md. [~] row_hash/MERGE + bronze-growth explanation is an assistant DRAFT: student must rewrite in own words. Not committed yet.
- [ ] B5 sixth check; deliberate failure + PROBLEM output; ELT vs ETL answer

## Part C (needs Mage + Mage reference notebook)
- [x] Mage compatibility (native Windows, Python 3.12.6): mage-ai 0.9.80 installed in .venv; `pip check` clean; `mage init` OK; UI served HTTP 200 on localhost; pytest still passes. WSL NOT needed so far. (`mage run` of a real pipeline still to be tested in C1.) Not yet added to requirements.txt (decide in Part C: it downgrades numpy/pandas/scikit-learn to 1.26.4/2.3.3/1.7.2, all within current ranges.)
- [x] C1 graph (ASCII in answers.md; student may redraw) + `mage run ... --test` output: screenshots/C/C1_mage_run_test.txt
- [x] C2 max_depth 1-5 table (depth 1 fails gate, no CSV; 2-5 pass) with logs C2_depth_N.txt; [~] explanation drafted, student must rewrite in own words
- [x] C3 evaluate_model branch, confusion matrix + metrics (C3_eval_depth_2.txt), UI screenshot C3_mage_ui_pipeline_graph.png; [ ] Cloudflare tunnel NOT done (localhost used); ask instructor
- [~] C4 validate_data block + 2 @tests executed and passing locally; NOT yet committed/pushed, CI green for it NOT yet confirmed
- [ ] Differences vs Mage reference notebook unknown (notebook not available); MIN_ACCURACY=0.90 is my own choice

## Part D (needs RabbitMQ)
- [ ] D1 table (BEFORE running) + 2-word key explanation
- [ ] D2 dispatcher + driver; 2-minute run, 3+ drivers, output matches D1
- [ ] D3 nack/ack, bad message every 10; crash and requeue answers

## Part E
- [ ] Integration diagram
- [ ] Half-page reflection
- [ ] All A-D answers in report

## Bonus
- [ ] Stream to lakehouse; double run does not double gold totals

## Open blockers
- [x] FreshCart notebook + flowchart (found in elt/ and elt/reference/)
- [ ] Mage Iris reference notebook (missing)
- [ ] Zomato stream slides (missing, optional)
- [ ] Instructor: is localhost acceptable instead of Cloudflare tunnel?
