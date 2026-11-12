# Final assignment compliance audit

Audited commit: `51e829a` (local = origin/main). Spec: the assignment text supplied by the student (identical to `Assignment_DE.docx`). Nothing was changed during this audit except adding this file.
Terms: **Implemented** = code/config exists. **Verified** = checked against a real run, log or file contents by Claude during this project or this audit. **Evidence adequate** = what is in the repo/PDF would satisfy a marker reading the submission.

## 1. Executive summary
- **54 requirements audited: 50 COMPLETE, 4 PARTIAL, 0 MISSING** (updated: S1 repo access and C3 Cloudflare screenshot are now COMPLETE). Two PARTIAL items carry an *instructor-confirmation* flag. The viva (E5) cannot be audited.
- **Not ready to submit yet.** Everything technical is implemented and verified. What blocks a clean submission is not code:
  1. The repository is **private** and nothing shows the instructor has access (requirement: public or shared with the instructor).
  2. ~~C3 Cloudflare screenshot~~ **resolved**: a genuine screenshot with the trycloudflare.com address in the browser address bar now exists (`report/screenshots/C/C3_cloudflare_tunnel.png`).
  3. The explanations in the PDF are **drafted by Claude**; the assignment requires your own words (explicit for A2 and C2, general integrity rule for the rest).
  4. CI for the latest commits is **not verified by me** (private repo). You verified run #6 for `a1af458`; commit `51e829a` is unchecked.
- Two corrections of my own earlier statements: (a) an unauthenticated `git ls-remote` seemed to show the repo as public; it only worked through your stored Git credentials. A truly anonymous request returns 404 (API and raw file), so the repo **is private**. (b) The C3 image proves less than I described before (see section 4).

## 2. Counts
| Status | Count |
|---|---|
| COMPLETE | 50 |
| PARTIAL | 4 (A2 own words, C2 own words, D1 "written before running" evidence, X2 academic-integrity wording) |
| MISSING | 0 |
| NEEDS INSTRUCTOR CONFIRMATION (flag on top of the above) | 2: screenshot type for B1 (renders of notebook output, no Snowsight capture), Mage accuracy threshold (C2). The Cloudflare question is resolved by the genuine tunnel screenshot. |

## 3. Compliance matrix
Columns: requirement | implementation | evidence | impl. | verified | evidence adequate | status | action.

### Submission
| # | Requirement | Implementation | Evidence | Impl. | Verif. | Adequate | Status | Action |
|---|---|---|---|---|---|---|---|---|
| S1 | Repo link in report; repo public or shared with instructor | repo + URL in PDF header | anonymous GitHub API and raw file requests now return HTTP 200 (repository is **public**, checked after the earlier private result); public tree has no `.env`, `.pkl`, `.csv`, `mage.log` or reference notebooks | yes | yes | yes | COMPLETE | none |
| S2 | FreshCart notebook, all outputs visible, `.ipynb` in `elt/` | `elt/freshcart_elt.ipynb` | 41/41 code cells executed in order, 0 errors (re-checked); `Final/FINAL_notebook_check.txt`, `FINAL_notebook.html` | yes | yes | yes | COMPLETE | none |
| S3 | Mage project and notebook with outputs | `iris_project/`, `iris_project/iris_classifier_run.ipynb` | 7/7 cells executed, 0 errors; real `mage run` output | yes | yes | yes | COMPLETE | none |
| S4 | `stream/dispatcher.py`, `stream/driver.py` | both tracked | compile OK, executed in D2/D3 | yes | yes | yes | COMPLETE | none |
| S5 | PDF `RollNo_Name_Pipelines.pdf`, <= 8 pages excl. appendix | `report/23BCS095_Gunti_Ravi_Kumar_Pipelines.pdf` | PyMuPDF (after the rewrite): 26 pages = 6 body + 20 appendix, text selectable | yes | yes | yes | COMPLETE | none |

### Part A: Git and CI/CD (15)
| # | Requirement | Implementation | Evidence | Impl. | Verif. | Adequate | Status | Action |
|---|---|---|---|---|---|---|---|---|
| A1a | Repo structure (README, .gitignore with 5 entries, requirements.txt, elt/, iris_project/, stream/, tests/test_prepare_data.py, ci.yml) | all tracked (`git ls-files`); all 5 required ignore entries present | tree, `.gitignore` | yes | yes | yes | COMPLETE | none |
| A1b | >= 5 meaningful commits; `git log --oneline` in report | 16 commits, semantic messages | PDF A1 (snapshot at `a1af458`, says so) | yes | yes | yes | COMPLETE | none |
| A2 | Six-command table + "teammate after commit?" (one sentence each, own words) | PDF A2 | content is correct | yes | yes | wording is Claude's | **PARTIAL** | Rewrite in your own words (`report/USER_REVIEW_REQUIRED.md`) |
| A3a | pytest test (120/30) | `tests/test_prepare_data.py` | 10 tests pass now | yes | yes | yes | COMPLETE | none |
| A3b | `ci.yml` on every push: checkout, Python 3.12, `pip install -r requirements.txt`, pytest | `.github/workflows/ci.yml` (read; `on: push`, setup-python 3.12, `python -m pytest`) | CI #1/#3 images; run #6 per student | yes | partly | yes | COMPLETE | Confirm run for `51e829a` is green |
| A3c | Green run screenshot | real browser screenshots | `A/A3_green.png` (CI #1, `6d86300`), `A3_final_green.png` (#1-#3); images viewed | yes | yes | yes | COMPLETE | none |
| A3d | Red run (test_size 0.3) + fixing commit | commits `b038cf1` (red), `0c83c3e` (fix) | `A/A3_red.png` (CI #2 red, viewed); log shows both commits | yes | yes | yes | COMPLETE | none |

### Part B: FreshCart ELT (30)
| # | Requirement | Implementation | Evidence | Impl. | Verif. | Adequate | Status | Action |
|---|---|---|---|---|---|---|---|---|
| B1a | Run notebook top to bottom; confirm 8/6/2/4, 4 orders 7,785.00 126 pts, 25% | `elt/` code + SQL | step run (`B1_*`) and final single-kernel run: 16/16 checks PASS; independent query | yes | yes | yes | COMPLETE | none |
| B1b | "include screenshots of the outputs" | `B/B1_notebook_part1-3.png` | images viewed: they are headless-browser renders of the executed notebook (show 8 rows, 6, 2 ORD-1004/1006, 4, gold line, 25%). Not Snowsight captures. They predate the sixth check (five checks listed) | yes | yes | yes, with caveat | COMPLETE | Optional: ask instructor whether renders are acceptable (flag) |
| B2a | Trace ORD-1003 (4 points) | PDF B2 | matches `10_orders_clean.sql`, `20_orders_dedup.sql` (`QUALIFY ROW_NUMBER() ... updated_at DESC, ingest_seq DESC`), `40_gold.sql`; `B2_evidence.txt` | yes | yes | yes | COMPLETE | none |
| B2b | ORD-1005 vs ORD-1001; table + join condition | PDF B2 | `dim.customers_scd2` join on email and `order_date BETWEEN valid_from AND valid_to` | yes | yes | yes | COMPLETE | none |
| B3a | Rule line inside `ARRAY_CONSTRUCT_COMPACT` | `elt/sql/10_orders_clean.sql` line 49 | read | yes | yes | yes | COMPLETE | none |
| B3b | Show ORD-1006 reasons before/after | PDF B3; `B3_*` | before `["bad_email","bad_pincode"]`, after + `unsupported_currency`; image viewed | yes | yes | yes | COMPLETE | none |
| B3c | Gold changes? second quarantine row? SQL that decides | PDF B3 | gold 4/7785.00/126 unchanged; `NOT EXISTS` lines 68-72 | yes | yes | yes | COMPLETE | none |
| B4a | Add CUST-02 Gold 2026-08-15 event | `elt/mock_data.py` (`B4_NEW_EVENT`, added by the B4 notebook cell) | notebook cell output | yes | yes | yes | COMPLETE | none |
| B4b | Predictions before running; prediction/actual table | `answers.md`, PDF B4 | predictions committed **before** the run as `72e290d` (09:58) vs results `f83bf2f`; 5/5 match | yes | yes | yes | COMPLETE | none |
| B4c | 4-6 sentences: row_hash/MERGE; why bronze grows 8/run | PDF B4 | text checked against the MERGE code (hash covers all columns except `order_id`) | yes | yes | content yes | COMPLETE | Own-words rewrite (see integrity row) |
| B5a | Sixth check in `quality_checks()` | `elt/freshcart.py` | notebook shows it OK on real data | yes | yes | yes | COMPLETE | none |
| B5b | Fail on purpose, show PROBLEM, remove mock order | `B5_*`, notebook B5 section | image viewed: `orders dated in the future 1 PROBLEM`; asserted cleanup; 19/19 checks; before/after identical | yes | yes | yes | COMPLETE | none |
| B5c | ELT vs ETL (3-4 sentences) + the lecture's ETL situation | PDF B5 | ETL situation taken from the lecture notes in `material.zip` (ETL "best when strict pre-load compliance..."; PII masking before landing). The ETL lecture PDF/xlsx you named were not found | yes | yes | yes | COMPLETE | Confirm it is the situation your lecture showed |

### Part C: Mage (20)
| # | Requirement | Implementation | Evidence | Impl. | Verif. | Adequate | Status | Action |
|---|---|---|---|---|---|---|---|---|
| C1a | Draw block graph with block types and tests | PDF C1 (text drawing: types and tests per block) | readable; "any tool" allowed | yes | yes | yes (plain) | COMPLETE | Optional: a drawn graphic |
| C1b | Run `mage run iris_project iris_classifier --test`, include output | `C1_mage_run_test.txt`, notebook cell 3 | real output, exit 0 | yes | yes | yes | COMPLETE | none |
| C2a | max_depth 1-5 table (CSV deleted before each run) | PDF C2 | equals `C2_summary.txt` and notebook: depth 1 acc 0.6333, exit 1, no CSV; 2: 0.9667; 3-5: 1.0 | yes | yes | yes | COMPLETE | The 0.90 gate is a project choice, no value is given in the assignment (flag) |
| C2b | Explain, in own words, how a failing `@test` stops `save_results` | PDF C2 | behaviour proven (no "Saved", no confusion matrix at depth 1) | yes | yes | wording is Claude's | **PARTIAL** | Rewrite in own words |
| C3a | `evaluate_model` so `train_model` has two downstream blocks | `evaluate_model.py`, `metadata.yaml` | read | yes | yes | yes | COMPLETE | none |
| C3b | Show edited `metadata.yaml` | PDF C3 block excerpt + file | excerpt matches file | yes | yes | yes | COMPLETE | none |
| C3c | Confusion matrix + metrics table | PDF C3, `C3_eval_depth_2.txt`, notebook | real output | yes | yes | yes | COMPLETE | none |
| C3d | Mage UI screenshot of the graph **through the Cloudflare tunnel** | `C/C3_cloudflare_tunnel.png` (plus `C/C3_mage_ui_pipeline_graph.png` as extra local evidence) | image opened: genuine Chrome capture; address bar shows `determination-unwrap-donated-dylan.trycloudflare.com/pipelines/iris_classifier/triggers`; Mage v0.9.80, `iris_project > Pipelines > iris_classifier`; graph with all 6 blocks and the branch `train_model -> save_results / evaluate_model`; clock 07:14 UTC (after the Cloudflare API recovered at 07:04). Satisfies the wording "Open the pipeline in the Mage UI (through the Cloudflare tunnel) and include a screenshot of the graph showing the branch". Appendix caption: Figure C3 | yes | yes (image inspected; the public URL could not be re-opened because the tunnel was closed) | yes | COMPLETE | none |
| C4a | Own block with its own `@test` | `validate_data.py` | run exit 0; tests fail on a NaN / 2 classes when run directly | yes | yes | yes | COMPLETE | none |
| C4b | Commit it; CI still passes | commit `1428aef` | CI #6 green per student (not verifiable here) | yes | partly | yes | COMPLETE | none |

### Part D: RabbitMQ (20)
| # | Requirement | Implementation | Evidence | Impl. | Verif. | Adequate | Status | Action |
|---|---|---|---|---|---|---|---|---|
| D1a | Routing table for 6 keys | PDF D1, `topic.py` | live broker: 6/6 PASS (re-run today); unit tests | yes | yes | yes | COMPLETE | none |
| D1b | Predictions written **before** running | `answers.md` D1 block | **Git cannot prove it**: the predictions were committed in the same commit (`4d59385`, 11:00) as the logs showing the run. (B4, by contrast, has its own earlier commit.) The expected recipients were given in the student's prompt before the run, but that is only in chat | yes | n/a | **no** | **PARTIAL** | Cannot be fixed retroactively (do not backdate). Be ready to explain all six rows at the viva |
| D1c | Explain the two-word key | PDF D1 | correct | yes | yes | yes | COMPLETE | none |
| D2a | `dispatcher.py`: every 2 s, random city/zone/type, JSON {id,city,zone,type,ts}, exchange `rapido-dispatch` | `stream/dispatcher.py` | log lines every ~2 s | yes | yes | yes | COMPLETE | none |
| D2b | `driver.py NAME PATTERN`: private queue, bind, print, ACK | `stream/driver.py` | logs | yes | yes | yes | COMPLETE | none |
| D2c | Dispatcher + >= 3 drivers for two minutes | run of 6 drivers, 59 messages, ~2 min | `D2_*` logs, `D2_verification.txt` | yes | yes | yes | COMPLETE | none |
| D2d | Console output proving a D1 key reached exactly the predicted queues | `verify_logs.py`; PDF excerpt of message #2 | 0 unexpected deliveries; evidence is log files (assignment says "console output", no screenshot demanded) | yes | yes | yes | COMPLETE | none |
| D3a | Missing zone -> `basic_nack(requeue=False)`, else `basic_ack` | `driver.py` `handle_delivery` | logs | yes | yes | yes | COMPLETE | none |
| D3b | Dispatcher sends one bad message in 10 | `--bad-every 10` default | `D3_dispatcher.log` (#10, #20, #30) | yes | yes | yes | COMPLETE | none |
| D3c | Show bad discarded, good processed | `D3_*` | live run + scripted demo with queue depth from the broker | yes | yes | yes | COMPLETE | none |
| D3d | Crash before ACK; `requeue=True` for an always-bad message | PDF D3 | demonstrated: `redelivered=True`; 4/4 requeue loop; no DLX claimed | yes | yes | content yes | COMPLETE | Own-words rewrite |

### Part E (15) and Bonus (+10)
| # | Requirement | Implementation | Evidence | Impl. | Verif. | Adequate | Status | Action |
|---|---|---|---|---|---|---|---|---|
| E1 | Report <= 8 pages excl. appendix | PDF | 6 body pages (after the rewrite) | yes | yes | yes | COMPLETE | none |
| E2 | Numbered answers for every question A-D | PDF | every heading and key string found in the PDF text (checked) | yes | yes | yes | COMPLETE | none |
| E3 | ONE diagram: Git, CI, ELT to gold, ML pipeline, stream | PDF page 1 SVG | viewed; states the ML pipeline trains on sklearn Iris (not on gold) | yes | yes | yes | COMPLETE | none |
| E4 | Half-page reflection (what broke, cause, fix) | PDF | real event (B4 `KeyError`, Time Travel, notebook rerun problem); states AI assistance and who diagnosed | yes | yes | yes | COMPLETE | Edit voice only; keep it true |
| E5 | Viva | n/a | cannot be audited | n/a | n/a | n/a | not counted | Prepare |
| Bn1 | Consumer, 1-minute collection, `write_landing()`, `load_file()`, transform SQL -> `gold.fct_orders` | `stream/order_consumer.py`, `bonus_demo.py` | `Bonus/BONUS_run_output.txt` (windows 60 s; 4 collected, 1 malformed NACKed) | yes | yes | yes | COMPLETE | none |
| Bn2 | Run twice; gold totals do not double | same | 4/7785.00/161 -> 7/9535.00/205 -> 7/9535.00/205; cleanup restored baseline; independent check | yes | yes | yes | COMPLETE | none |

### Cross-cutting
| # | Requirement | Evidence | Status | Action |
|---|---|---|---|---|
| X1 | No `.env`, credentials or secrets in the repo or history | `.env` ignored, never tracked/committed; every secret value (your RabbitMQ and Snowflake values and the foreign notebook login) found in **0 commits** of the full history; only a placeholder URL in an error message matches a generic pattern; staged files and PDF bytes scanned | COMPLETE | none |
| X2 | "code, predictions and explanations must be your own" | explanations in the PDF were drafted by Claude; D1 reasoning co-written | **PARTIAL** | Review and rewrite (`report/USER_REVIEW_REQUIRED.md`); be ready to defend everything |

## 4. Screenshots: what they actually show
| Evidence | What I saw (images opened) | Satisfies |
|---|---|---|
| `A3_green/red/final_green.png` | real GitHub Actions pages (runs #1, #2, #3), lock icon (private repo) | A3 yes |
| `B1_notebook_part1-3.png` | rendered notebook outputs of the first (step-by-step) run in `FRESHCART_DB`: counts, quarantine rows, gold line, 25% | B1 "screenshots of the outputs": yes as notebook output; not Snowsight |
| `B3/B4/B5_notebook_*.png` | rendered notebook sections with before/after, predictions vs actuals, PROBLEM output, cleanup 19/19 | yes (renders) |
| `C3_cloudflare_tunnel.png` | genuine Chrome capture, address bar `...trycloudflare.com/pipelines/iris_classifier/triggers`, Mage v0.9.80, graph with 6 blocks and the branch | **C3 satisfied** (Cloudflare tunnel access and branch visible) |
| `C3_mage_ui_pipeline_graph.png` | Mage editor (local server) with the 6-block graph and branch; no address bar; clock 17:46 UTC | extra local evidence only |
| `D/*` | text logs only (no terminal screenshots) | D2/D3 say "console output": logs suffice; no screenshot is demanded |
| Appendix | 19 images in 20 pages, captions for A3, B1, B3, B4, B5, C3 | adequate |

## 5. Missing or inadequate items
1. ~~Cloudflare tunnel evidence (C3)~~ **resolved** (see section 11). The failed attempts and their cause (temporary 429/500 errors from Cloudflare's quick-tunnel API) are logged in `report/screenshots/C/C3_cloudflare_tunnel_probe.txt`.
2. **Repository access for the instructor** (S1).
3. **Own-words explanations** (A2, C2 explicit; all others under integrity).
4. **D1 "predictions before running"** has no independent Git timestamp.
5. **CI for the latest commits** unverified here.
6. Minor: README covers setup, Part D and the bonus but not how to run Part B/C (the extra requirements files `requirements-elt.txt`, `requirements-mage.txt` are not mentioned there). Not an assignment requirement.

## 6. Submission checklist
- [x] PDF `23BCS095_Gunti_Ravi_Kumar_Pipelines.pdf` (5 body pages, answers A-D + bonus, diagram, reflection, appendix)
- [x] `elt/freshcart_elt.ipynb` executed, 0 errors; SQL in `elt/sql/`; code in `elt/`
- [x] Mage project + executed Mage notebook
- [x] `stream/dispatcher.py`, `stream/driver.py`, bonus scripts, tests
- [x] `.github/workflows/ci.yml`, red/green CI screenshots
- [x] No secrets in repo or history
- [ ] Repo shared with the instructor / public
- [ ] Latest CI run (`51e829a`) confirmed green
- [x] C3 screenshot with the Cloudflare tunnel (`C3_cloudflare_tunnel.png`)
- [ ] Explanations rewritten in your own words
- [ ] Viva preparation

## 7. Remaining actions, in priority order
1. **Share the repo** with the instructor and confirm acceptance (or make it public). Without this nothing can be graded.
2. **Check the Actions tab** for the run on `51e829a`; if red, send me the log.
3. ~~C3 tunnel screenshot~~ done.
4. **Rewrite the explanations** in your own words (A2 and C2 first, since the assignment says so explicitly), then re-render with `report\make_pdf.py` and commit.
5. **Prepare for the viva:** D1 (all six rows plus the two-word key), B4 predictions and reasoning, the 0.90 gate being a project choice.
6. Optional: ask the instructor about (a) renders vs Snowsight screenshots, (b) an expected accuracy threshold.

## 8. Is the assignment ready for submission?
**Technically yes; see section 11 for the current status.** All 48 technical requirements are implemented and verified, with no missing item. It should not be submitted until the repo is shared (action 1) and the C3 tunnel evidence is resolved or confirmed by the instructor (action 3). The own-words rewrite (action 4) is required by the assignment's own integrity rule.

## 9. Update after the explanation rewrite and report revision
- **Report text rewritten** (A2, B2, B3, B4, B5, C2, C3, D1, D2, D3, Bonus, Reflection) in plain language from the actual code, SQL and logs. Predictions and observed results are now shown separately (B4 table, D1 table). The PDF was regenerated: 26 pages = 6 body (limit 8) + 20 appendix; text selectable; no placeholders or draft markers.
- **Own-words requirement (A2, C2, integrity row X2) stays PARTIAL.** The new wording is still Claude's. It is simpler and tied to the implementation, but it only becomes the student's own writing after the student reads and edits it. `report/USER_REVIEW_REQUIRED.md` is now a viva study guide (answers, implementation details, expected results, likely viva questions) instead of draft suggestions.
- **D1 timing (D1b) stays PARTIAL.** Git cannot show the predictions came first. The PDF D1 states this openly, `answers.md` carries a timing note, and nothing was backdated.
- ~~C3 stays PARTIAL.~~ Superseded by section 11: C3 is COMPLETE. (This section describes the state before the Cloudflare screenshot existed; `C3_cloudflare_tunnel_probe.txt` records the earlier failed attempts and the 07:04 UTC API check and is not itself tunnel evidence.)
- **Screenshot review (images opened):** A3 (3 real browser screenshots, runs #1 to #3), B1/B3/B4/B5 (headless renders of the executed notebook, not Snowsight), C3 (`C3_cloudflare_tunnel.png`: real browser capture through trycloudflare.com; plus the local editor view), D and Bonus (text logs only; the assignment asks for "console output"), Final (HTML render + check files). No screenshot is insufficient for an explicit assignment requirement; the only caveat is the instructor-dependent question about renders vs Snowsight captures (B1).
- **Counts unchanged:** 54 audited, 48 COMPLETE, 6 PARTIAL (S1, A2, C2b, C3d, D1b, X2), 0 MISSING.
- **Not verified here:** the GitHub Actions result for commit `51e829a` and the instructor's access (repo is private: anonymous API calls return 404).

## 10. Update: repository visibility and CI now verified
- **Repository is public** (anonymous `api.github.com` and `raw.githubusercontent.com` requests return HTTP 200; a raw `.env` returns 404; the public tree of 158 files contains no `.env`, `.pkl`, `.csv`, `mage.log`, `elt/reference` or the three reference notebooks). Earlier today the same anonymous requests returned 404, so it was made public in the meantime. **S1 is now COMPLETE**, so the corrected counts are **49 COMPLETE, 5 PARTIAL, 0 MISSING** (PARTIAL: A2 own words, C2 own words, C3 Cloudflare screenshot, D1 "written before running" evidence, X2 own-words integrity).
- **GitHub Actions verified through the public API:** run #1 `6d86300` success, #2 `b038cf1` **failure (the intentional red demonstration)**, #3 `0c83c3e` success, #4 `a55d012` success, #5 `1428aef` success, #6 `a1af458` success, **#7 `51e829a` success**. This confirms A3b and C4b for the latest pushed commit. The local report edits made after `51e829a` (PDF, report, review guide, audit, probe file) are not committed or pushed, so they have no CI run yet.
- **Remaining items:** own-words rewrite (A2, C2, X2), the C3 Cloudflare screenshot (or instructor confirmation), D1 timing (cannot be fixed, stated openly), viva.
- **Submission readiness:** technically ready; submit after (1) reading and owning the explanations, (2) the C3 tunnel screenshot or instructor OK, and (3) committing and pushing the updated PDF and report files (only with the student's confirmation).

## 11. Update: C3 Cloudflare screenshot received and verified (current status)
- **File:** `report/screenshots/C/C3_cloudflare_tunnel.png` (PNG, 2876x1630). **Contents (opened and read):** Chrome browser; address bar `determination-unwrap-donated-dylan.trycloudflare.com/pipelines/iris_classifier/triggers`; Mage AI v0.9.80; breadcrumb `iris_project > Pipelines > iris_classifier > Triggers`; graph on the right with `load_iris`, `validate_data`, `prepare_data`, `train_model`, and the branch `save_results` (data exporter) and `evaluate_model`; clock 07:14 UTC.
- **Assignment C3 requirement:** "Open the pipeline in the Mage UI (through the Cloudflare tunnel) and include a screenshot of the graph showing the branch." Met: access through a trycloudflare.com address is visible and the graph with the branch is visible. The page is the pipeline's Triggers tab (the graph sits on its right side), which does not change the requirement. **C3d: COMPLETE.**
- **Report:** `report/report.html` C3 text and appendix updated (Figure C3 caption as requested); `C3_mage_ui_pipeline_graph.png` is kept as additional local evidence; PDF regenerated.
- **Tunnel closed:** no `cloudflared` process was running when checked after the screenshot, so Mage is not exposed.
- **Not independently verifiable:** that the URL opened at the time (the tunnel is closed; the screenshot itself is the evidence).
- **Counts now:** **54 audited: 50 COMPLETE, 4 PARTIAL, 0 MISSING.** PARTIAL: A2 (own words), C2b (own words), D1b (predictions not independently timestamped in Git; stated openly), X2 (own-words rule for the Claude-drafted explanations).
- **Instructor-dependent items left:** (a) whether notebook renders are acceptable instead of Snowsight screenshots (B1), (b) whether a specific accuracy threshold is expected for the Mage gate (C2).
- **Submission readiness:** all technical requirements are complete and verified. Not yet fully ready: the four PARTIAL items depend on you (read and own the explanations; be ready to explain D1), and the updated files are not committed or pushed.
