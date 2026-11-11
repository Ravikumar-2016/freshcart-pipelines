# Requirement tracker

Status: [ ] not started, [~] in progress, [x] done WITH evidence (cite it).

## Submission items
- [ ] GitHub repo link (public or shared) in report
- [ ] `elt/` FreshCart notebook with outputs (.ipynb)
- [ ] `iris_project/` Mage project and notebook with outputs
- [ ] `stream/dispatcher.py`, `stream/driver.py`
- [ ] Report PDF `RollNo_Name_Pipelines.pdf` (max 8 pages excl. appendix)

## Part A
- [~] A1 structure: folders, README, .gitignore, requirements.txt created (test + ci.yml pending)
- [ ] A1 five+ meaningful commits; `git log --oneline` pasted
- [ ] A2 command table + "can teammate see after commit?" answer
- [ ] A3 test_prepare_data.py (120/30)
- [ ] A3 ci.yml (push; checkout, Python 3.12, install, pytest)
- [ ] A3 green run screenshot
- [ ] A3 red run screenshot (test_size=0.3) + fixing commit

## Part B (needs Snowflake + FreshCart notebook)
- [ ] B1 baseline: 8 raw / 6 clean / 2 quarantine / 4 dedup / 4 orders, 7,785.00, 126 pts / 25%
- [ ] B2 trace ORD-1003 (4 points) and ORD-1005
- [ ] B3 unsupported_currency rule; before/after; gold total; quarantine answer
- [ ] B4 predictions (BEFORE run) vs actuals; row_hash/MERGE explanation
- [ ] B5 sixth check; deliberate failure + PROBLEM output; ELT vs ETL answer

## Part C (needs Mage + Mage reference notebook)
- [ ] C1 graph + `mage run iris_project iris_classifier --test` output
- [ ] C2 max_depth 1-5 table + gate explanation
- [ ] C3 evaluate_model branch, metadata.yaml, confusion matrix, metrics, UI screenshot
- [ ] C4 own block + @test, committed, CI green

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
