# Viva study guide and review notes

**Read this first.** All explanations in `report/report.html` and in this guide were written by Claude, in simple language, from the real code, SQL, notebooks and logs of this project. They are not your own writing yet. The assignment says explanations must be your own and the viva will check it. So: read each answer, run the small commands under it if you like, and change any sentence you would not say yourself. Then edit `report/report.html` and re-render:

```powershell
.\.venv\Scripts\python.exe report\make_pdf.py 23BCS095_Gunti_Ravi_Kumar
```
What is fact (numbers, files, commits) is checked against evidence. What you must own is the wording and the understanding.

## Honest points you should know before the viva
1. **Claude Code helped build everything**, including the explanations. The report says so in its header and in the reflection. Do not say you wrote the code alone.
2. **B4 predictions:** you committed them (`72e290d`) before the run. The reasoning was worked out by Claude from the SQL; be able to re-derive it (see B4).
3. **D1 predictions:** the expected recipients were stated before any message was published, but Git has them in the same commit (`4d59385`) as the test logs. The report says this openly. Be ready to redo all six rows on paper.
4. **Mage gate 0.90** is a choice made in this project (the assignment gives no number and the Mage reference notebook was not available). Depth 1 fails only because of this gate.
5. **Cloudflare tunnel (C3):** the first attempts failed because Cloudflare's quick-tunnel API was returning temporary errors (HTTP 429/500; log in `report/screenshots/C/C3_cloudflare_tunnel_probe.txt`). The tunnel worked later and `report/screenshots/C/C3_cloudflare_tunnel.png` is a real browser screenshot with the trycloudflare.com address visible. The local screenshot is kept as extra evidence.
6. **ETL lecture source:** the ETL-vs-ELT "when ETL wins" statement is taken from the course notes in `material.zip` (`30-09-2026/data_transformation_orchestration.html`). The lecture PDF and xlsx you mentioned were not on the machine. Check it matches what your lecture said.
7. The final notebook ran in database `FRESHCART_FINAL`; the step-by-step work (B1-B5, bonus) ran in `FRESHCART_DB`. Do not mix them up when asked.

---

## Part A: Git and CI/CD
**A1. Structure and commits.** Question: what is in the repository, and how many commits? Answer: the required folders and files, `.gitignore` with the five required entries, and 16 commits with meaningful messages (feat, fix, test, ci, docs). Details: `git log --oneline`; `.gitignore` also has `.venv/`. Viva Q: *Why is `.env` in `.gitignore`?* It holds passwords and the broker URL; once committed it stays in the history.

**A2. Commands.** Answer: see the table in the report. Key point: `git commit` saves only in the local repository; `git push` sends commits to GitHub. Evidence: at the start the first commit was local while GitHub was empty. Viva Q: *Difference between add and commit?* `add` puts changes in the staging area (the list for the next commit); `commit` saves that list as a snapshot. *What does `-u` do?* Remembers `origin/main` as the default so later `git push` needs no arguments.

**A3. CI.** What was done: test `tests/test_prepare_data.py` (120 train, 30 test); workflow `.github/workflows/ci.yml` on every push. Observed: CI #1 green (`6d86300`), CI #2 red when `test_size=0.3` (`b038cf1`, local result `105 == 120`), fix `0c83c3e` gives green. Viva Q: *Why `python -m pytest`?* It adds the project root to the import path so `from iris_project...` works. *Why the red run on purpose?* To show CI catches a wrong change before it is accepted.

## Part B: FreshCart ELT
**Flow to remember:** mock data -> `write_landing()` (raw .json.gz with an envelope: source, run_id, extracted_at, data) -> `load_file()` (PUT to the stage, COPY INTO bronze) -> SQL: bronze -> silver (clean, dedup) + quarantine -> dim (SCD2) and ref -> gold (MERGE) -> `quality_checks()`.

**B1. Baseline.** Expected and observed: 8 raw rows (6 web + 2 mobile), 6 pass cleaning, 2 quarantined (ORD-1004 negative amount; ORD-1006 bad email and 5-digit pincode), 4 after dedup, gold 4 orders / 7,785.00 / 126 points, 25% rejected (2 of 8). Viva Q: *Why only valid after exactly one run?* Bronze keeps every run's rows, so a second run shows 16.

**B2. ORD-1003 and ORD-1005.** Short answer: two raw rows with different field names because they come from two systems; the SQL maps both to the same columns and cleans them; `QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC, ingest_seq DESC) = 1` keeps the newest (mobile, 18:40); gold amount 2100.00 x 1.0, points `FLOOR(2100/100) x 3 = 63`. ORD-1005 vs ORD-1001: join `dim.customers_scd2` on `email` and `order_date BETWEEN valid_from AND valid_to`; Silver on 09-01 (12 pts), Gold from 09-03 (8 x 2 = 16). Viva Q: *Why is a missing amount allowed in silver?* The web copy has NULL; it is resolved when the newer mobile copy wins in dedup. *What is SCD2?* A table that keeps history: one row per period a customer had a tier.

**B3. `unsupported_currency`.** Change: one `IFF(currency IS NULL OR currency NOT IN ('INR','USD'), 'unsupported_currency', NULL)` line in `elt/sql/10_orders_clean.sql` (line 49). Observed: ORD-1006 reasons `["bad_email","bad_pincode"]` -> add `"unsupported_currency"` in `silver.orders_checked`; gold unchanged (4 / 7785.00 / 126); no second quarantine row. Why: the `NOT EXISTS` in the quarantine insert skips a record with the same source, order_id and updated_at and ignores reasons, so the old quarantine row keeps the old reasons. Viva Q: *Why does gold not change?* ORD-1006 was already rejected for other reasons and never reached gold.

**B4. CUST-02 Gold on 2026-08-15.** Predictions (committed before the run) and observed: CUST-02 rows 2; ORD-1002 tier Gold; points 70; total 161; changed `published_at` rows 1 (ORD-1002). How to re-derive: the event splits Silver (to 2026-08-14) and Gold (from 08-15); ORD-1002 is dated 09-01 so it is in the Gold period; 3536 / 100 = 35.36, floor 35, x2 = 70; total 126 - 35 + 70 = 161; only ORD-1002's values changed, so only its hash changed. Second pass: nothing changed. Explanation: MERGE by `order_id`, update only `WHEN MATCHED AND t.row_hash <> s.row_hash`; `row_hash` hashes all columns except `order_id`; bronze is append-only (+8 order rows per run), silver dedups. Viva Q: *Why can the hash be used to detect change?* Same values give the same hash, any changed value changes it (practically). *What would break idempotency?* Plain INSERT instead of MERGE.

**B5. Sixth check and ELT vs ETL.** Check: `COUNT_IF(order_date > CURRENT_DATE())` on `silver.orders_dedup`. Test: mock order `TEST-B5-FUTURE-DATE-001` dated 2026-12-31, no amount (so that only this check fails); output `orders dated in the future   1   PROBLEM`. Cleanup: count markers first, check them, delete only those rows and the staged file, re-run transform, check back to 0 (19/19 checks). ELT vs ETL: ELT keeps raw data and lets SQL re-run; ETL fits when sensitive data (card, Aadhaar) must be masked before it is stored. Viva Q: *Why no amount on the mock order?* A missing amount is allowed and a future date has no FX rate, so no other check fires. *Why delete from bronze and gold by hand?* Bronze is append-only and the gold MERGE never deletes.

## Part C: Mage
**Graph:** `load_iris -> validate_data -> prepare_data -> train_model -> {save_results, evaluate_model}`; each block has its own `@test`. Block types: data_loader, transformers, data_exporter.

**C1.** Command `mage run iris_project iris_classifier --test`; expected: every block `tests passed`, accuracy 1.0 at depth 3, CSV saved, exit 0.

**C2. Gate experiment.** Observed: depth 1 -> 0.6333, test fails, exit 1, no CSV; depth 2 -> 0.9667; depth 3, 4, 5 -> 1.0, CSV created. Meaning: 30 test rows; depth 1 can only split once so it cannot separate three classes (19 of 30 right); depth 2 gets 29 of 30. Gate: the `train_model` test needs accuracy >= 0.90 (project choice). Stop: Mage stops after the failed test, so `save_results` and `evaluate_model` do not run. Viva Q: *What is a quality gate?* A test that must pass before the next step runs. *Why better than checking the file later?* A bad result never gets saved where something else could use it.

**C3. Evaluation branch.** `train_model` has downstream `[save_results, evaluate_model]` in `metadata.yaml`. Depth 2 confusion matrix: setosa [10,0,0], versicolor [0,8,1], virginica [0,0,11]; accuracy 0.9667. Screenshots: through the Cloudflare tunnel (`C3_cloudflare_tunnel.png`, address bar visible) and the local editor view (`C3_mage_ui_pipeline_graph.png`). Viva Q: *What is a Cloudflare Quick Tunnel?* A free account-less tunnel: `cloudflared` makes an outgoing connection to Cloudflare and Cloudflare gives a public `trycloudflare.com` address that forwards to the local Mage on port 6789. *Why did it fail at first?* The call that creates the tunnel (`api.trycloudflare.com/tunnel`) returned HTTP 429/500 or took longer than cloudflared's 15 s limit; it worked later. *Is it safe to leave open?* No: Mage's login is the only protection, so close it after use (it is closed).

**C4.** `validate_data` with two tests (no missing values, 3 classes). Run directly, the tests fail on a NaN and on a two-class frame.

## Part D: RabbitMQ
**D1. Rules:** `*` = exactly one word; `#` = zero or more words. Table: 1 Ravi, Meena, Control; 2 Priya, Arjun, Control; 3 Arjun, Control; 4 Karthik; 5 dropped; 6 Control only. Key 6 has two words; the other patterns need three (their `*` needs one word), only `bangalore.#` can match. Viva Q: *Would `bangalore.#` match `bangalore`?* Yes, `#` can match zero words.

**D2.** Dispatcher: every 2 s, random city/zone/type, key `city.zone.type`, JSON `{id, city, zone, type, ts}`, persistent, exchange `rapido-dispatch`. Driver: `python stream/driver.py NAME PATTERN`, private queue, ACK after printing. Run: 6 drivers + dispatcher, about 2 minutes, 59 messages, every message reached exactly the predicted drivers (0 unexpected), 25 dropped. Viva Q: *Why must drivers start before the dispatcher?* Queues must exist and be bound; a message with no matching queue is dropped. *Why a private queue?* Each driver gets its own copy of every matching message.

**D3.** Missing `zone` -> `basic_nack(requeue=False)`; otherwise `basic_ack`; every 10th message is malformed. Observed: #10 and #20 NACKed by Arjun and Control, #30 matched nobody; demo: valid ACK depth 1 -> 0, malformed NACK depth 1 -> 0, crash before ACK gives depth 1 again and `redelivered=True`, `requeue=True` on a bad message came back 4 of 4 times. No DLX was configured. Viva Q: *What is a poison message?* A message that always fails; with requeue it loops forever. *What would a DLX do?* Move rejected messages to another queue for inspection (not configured here).

## Bonus
**Flow:** RabbitMQ (key `freshcart.order.web`) -> collect 60 s -> `write_landing()` -> `load_file()` -> same transform SQL -> `gold.fct_orders` -> `quality_checks()`; ACK only after the load into bronze (requeue if it fails); malformed messages NACK(requeue=False). **Result:** gold 4 / 7,785.00 / 161 -> 7 / 9,535.00 / 205 after run 1 and the same after run 2 (bronze 24 -> 28 -> 32). Why no doubling: silver dedup (`QUALIFY ROW_NUMBER`) and gold MERGE on `row_hash`. Cleanup: marker counts checked first, then only the test rows removed; baseline restored. Viva Q: *Why ACK after the load and not before?* If the load fails the message must not be lost.

## Part E: Reflection (what to say)
The B4 analysis cell failed with `KeyError: 'order_id'` because Snowflake returns upper-case column names; the pipeline was not re-run; Time Travel gave the "before" state after it was checked against the saved snapshot; later the notebook was made re-runnable (event kept separate, fixed time removed, final run in `FRESHCART_FINAL`). Say that Claude Code helped find and fix it.

## What is still outstanding (not solved by wording)
- Repo access: the repository is public now (checked), so nothing to share. GitHub Actions run #7 for commit `51e829a` succeeded (checked). The changes made after that commit (updated PDF, report, this guide) are not committed or pushed yet.
- C3 is done (real Cloudflare screenshot). Nothing outstanding for C3.
- Rewrite the answers in your own words.
