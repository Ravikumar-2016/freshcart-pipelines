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

## Part B (needs Snowflake + FreshCart notebook)
- [ ] B1 baseline: 8 raw / 6 clean / 2 quarantine / 4 dedup / 4 orders, 7,785.00, 126 pts / 25%
- [ ] B2 trace ORD-1003 (4 points) and ORD-1005
- [ ] B3 unsupported_currency rule; before/after; gold total; quarantine answer
- [ ] B4 predictions (BEFORE run) vs actuals; row_hash/MERGE explanation
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
- [ ] FreshCart notebook + flowchart (missing)
- [ ] Mage Iris reference notebook (missing)
- [ ] Zomato stream slides (missing, optional)
- [ ] Instructor: is localhost acceptable instead of Cloudflare tunnel?
