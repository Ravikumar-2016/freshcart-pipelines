# Report answers (numbered as in the assignment)

Write answers in your own words. Predictions (B4, D1) must be written BEFORE running.

## Part A
### A1
Repository: https://github.com/Ravikumar-2016/freshcart-pipelines (currently private; share with instructor or make public before submission)

`git log --oneline` (update again before final submission):
```
0c83c3e fix: restore correct 80/20 train test split
b038cf1 test: demonstrate failing CI for incorrect split
6d86300 ci: add GitHub Actions workflow
4d1e80a feat: add Iris data transformer and tests
4ef2ad1 chore: initial repository structure and .gitignore
```

### A2
> DRAFT drafted by the assistant: rephrase the last column in your own words before submitting
> (the assignment requires your own wording).

| Command | Where the change happens | What exactly happens? |
|---|---|---|
| `git init` | Working folder / local repository | Creates a hidden `.git` folder, turning the current folder into an empty local repository. |
| `git add train.py` | Working folder → staging area | Marks the current contents of `train.py` to be included in the next commit. |
| `git commit -m "msg"` | Staging area → local repository | Saves the staged snapshot as a new commit with an id and the message "msg", on my laptop only. |
| `git remote add origin URL` | Local repository (config only) | Stores the short name `origin` for the GitHub URL; nothing is uploaded or downloaded. |
| `git push -u origin main` | Local repository → remote (GitHub) | Uploads my local `main` commits to GitHub and links local `main` to `origin/main` so later a plain `git push` works. |
| `git pull origin main` | Remote (GitHub) → local repository and working folder | Downloads new commits from `origin/main` and merges them into my local `main` and files. |

**After `git commit`, can a teammate see my code on GitHub?** No. A commit is saved only in my
local repository on my laptop. GitHub (the remote) only receives it after `git push`.
(Evidence from this project: the first commit existed locally, and `git ls-remote` showed
nothing on GitHub until I pushed.)

### A3
- Test: `tests/test_prepare_data.py` asserts 120 train and 30 test rows.
- Block: `iris_project/transformers/prepare_data.py` uses `train_test_split(test_size=0.2, random_state=42)`.
  Decorators are imported only if missing, with a no-op fallback when `mage_ai` is absent (CI).
- Workflow: `.github/workflows/ci.yml` runs on every push: checkout, Python 3.12, `pip install -r requirements.txt`, `python -m pytest`.

Evidence:
| Run | Commit | Result | Evidence |
|---|---|---|---|
| CI #1 | 6d86300 "ci: add GitHub Actions workflow" | green (29s) | `screenshots/A/A3_green.png` |
| CI #2 | b038cf1 "test: demonstrate failing CI for incorrect split" (`test_size=0.3`) | red (27s) | `screenshots/A/A3_red.png` |
| CI #3 | 0c83c3e "fix: restore correct 80/20 train test split" | green (23s) | `screenshots/A/A3_final_green.png` (shows #1 green, #2 red, #3 green) |

Local pytest with `test_size=0.3`: `assert np.int64(105) == 120` (105 train rows) -> FAILED.
Local pytest after the fix: `1 passed`.

## Part B
> Part B setup notes / assumptions: Snowflake database is `FRESHCART_DB` (the reference notebook uses
> `FRESHCART`); the DIM and REF schemas were added because the SQL needs them. There are no real APIs: all
> input is the MOCK data from the course reference notebook (`elt/mock_data.py`). SQL is in `elt/sql/`,
> Python in `elt/freshcart.py`, notebook `elt/freshcart_elt.ipynb`. The SQL is the reference notebook's,
> unchanged (only `00_setup.sql` merges the student's database setup).

### B1
Run on 2026-11-12 (run_id `20261112_040919`), exactly one pipeline run on an empty database (the notebook asserts
bronze was empty first). Verified twice: in the notebook (16 of 16 checks PASS) and by a separate fresh connection.

| Check | Expected | Actual |
|---|---|---|
| Raw order rows in bronze.orders_raw (6 web + 2 mobile) | 8 | 8 (web 6, mobile 2; 1 distinct run_id) |
| Rows that pass cleaning (silver.orders_clean) | 6 | 6 |
| Rows in quarantine | 2 (ORD-1004, ORD-1006) | 2 (ORD-1004 non_positive_amount; ORD-1006 bad_email + bad_pincode) |
| Orders after deduplication | 4 | 4 |
| Final gold line | 4 orders, 7,785.00, 126 points | `GOLD: 4 orders, revenue ₹7785.00, 126 loyalty points` |
| Share of rows rejected | 25% | 25% |

Other counts (flowchart): bronze.customers_raw 4, fx_raw 1, pincode_raw 3, dim.customers_scd2 4, ref.pincode_geo 3: all as expected.
The five `quality_checks()` counts were all 0 (OK).

Evidence (`report/screenshots/B/`):
- `B1_notebook_part1.png`, `B1_notebook_part2.png`, `B1_notebook_part3.png`: the executed notebook rendered to HTML and captured with headless Edge (a real render of the saved outputs, NOT a Snowsight screenshot).
- `B1_independent_verification.txt`: row counts of every table queried from a fresh connection.
- The executed notebook itself: `elt/freshcart_elt.ipynb` (cells 1-10 executed; the "run it again" and clean-up cells are intentionally not run yet).
- Optional: a Snowsight screenshot of `SELECT COUNT(*) FROM FRESHCART_DB.BRONZE.ORDERS_RAW` (= 8) if the instructor wants one from Snowflake's own UI.

### B2
Evidence: `screenshots/B/B2_evidence.txt` (queries run after the single B1 run).

> DRAFT written by the assistant from the real query output: rewrite in your own words before submitting.

**ORD-1003**
1. *Raw records (bronze.orders_raw).* Web, ingest_seq 2, flat JSON: `{"order_id":"ORD-1003","cust_email":"meera@outlook.com","cust_name":"MEERA S","order_date":"2026-09-02","amount":null,"currency":"INR","pincode":"400050","updated_at":"2026-09-02 09:10:00"}`. Mobile, ingest_seq 8, nested camelCase JSON: `{"orderId":"ORD-1003","customer":{"email":"Meera@Outlook.com","name":"Meera S"},"orderDate":"02/09/2026","total":{"value":"2,100.00","currency":"INR"},"deliveryPin":"400050","updatedAt":"2026-09-02T18:40:00"}`. The names differ because they come from two different APIs; bronze stores each record exactly as received and the SQL unifies them later.
2. *Same columns in silver.orders_checked (SQL_10).* The `unified` CTE maps web `raw:order_id`, `raw:cust_email`, `raw:amount`, `raw:updated_at` and mobile `raw:orderId`, `raw:customer.email`, `raw:total.value`, `raw:updatedAt` onto the same column names. The `typed` CTE then applies `LOWER(TRIM(...))` to the email, `INITCAP(...)` to the name, `COALESCE(TRY_TO_DATE(order_date,'YYYY-MM-DD'), TRY_TO_DATE(...,'DD/MM/YYYY'), TRY_TO_DATE(...,'MON DD, YYYY'))` for the date (the mobile `02/09/2026` becomes 2026-09-02), `TRY_TO_DECIMAL(REGEXP_REPLACE(amount,'[^0-9.-]',''),12,2)` for the amount (`"2,100.00"` becomes 2100.00; web null stays NULL) and `TRY_TO_TIMESTAMP_NTZ(updated_at)`. Both copies pass validation (empty `reasons`): a NULL amount is allowed.
3. *Which copy survives (SQL_20).* `QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC, ingest_seq DESC) = 1` numbers the copies of each order newest first. The mobile copy (updated_at 2026-09-02 18:40:00) is newer than the web copy (09:10:00), so it gets row number 1 and survives (ingest_seq 8, amount 2100.00); if the timestamps tied, the later arrival (`ingest_seq`) would win.
4. *Gold calculation (SQL_40).* Currency INR has fx_rate 1.0000, so `amount_inr = ROUND(2100.00 × 1.0000, 2) = 2100.00`. Meera is Platinum (valid from 2022-11-01), multiplier 3, so `loyalty_points = FLOOR(2100.00 / 100) × 3 = 21 × 3 = 63`.

**ORD-1005 vs ORD-1001 (Priya).** The tier is looked up *on the order date*. The table `dim.customers_scd2` holds Priya's history: Silver from 2023-04-10 to 2026-09-02, Gold from 2026-09-03. In SQL_40 the join is `LEFT JOIN dim.customers_scd2 c ON c.email = o.email AND o.order_date BETWEEN c.valid_from AND c.valid_to`, followed by `LEFT JOIN ref.tier_multiplier m ON m.tier = c.tier`. ORD-1001 is dated 2026-09-01 (Silver, ×1: FLOOR(1250/100) × 1 = 12 points); ORD-1005 is dated 2026-09-03 (Gold, ×2: FLOOR(899/100) × 2 = 8 × 2 = 16 points).
### B3
**Change** (`elt/sql/10_orders_clean.sql`, line 49, inside `ARRAY_CONSTRUCT_COMPACT(...)`, one line added):
```sql
IFF(currency IS NULL OR currency NOT IN ('INR', 'USD'), 'unsupported_currency', NULL),   -- B3: only INR and USD are accepted
```
(`currency` is already upper-cased in the `typed` CTE, so `usd`/`inr` still pass; a missing currency is also flagged.)
Re-run: full `fc.run_pipeline()` on 2026-11-12 (run_id `20261112_042326`), after the B1 run (`20261112_040919`).
Evidence (`report/screenshots/B/`): `B3_notebook_section.png` (rendered notebook section), `B3_notebook_outputs.txt`, `B3_independent_verification.txt` (full arrays from a fresh connection). Notebook: section "B3" in `elt/freshcart_elt.ipynb`.

**ORD-1006 reasons (currency EUR):**
| | `silver.orders_checked` | `quarantine.orders` |
|---|---|---|
| Before the change (B1 run) | `["bad_email","bad_pincode"]` | `["bad_email","bad_pincode"]` |
| After the change + re-run | `["bad_email","bad_pincode","unsupported_currency"]` (both copies, ingest_seq 6 and 14) | still `["bad_email","bad_pincode"]` (run_id 20261112_040919, 1 row) |

Actual effects (before -> after): gold orders 4 -> 4, gold revenue 7785.00 -> 7785.00, loyalty points 126 -> 126, `silver.orders_dedup` 4 -> 4,
`quarantine.orders` 2 -> 2. Only the raw/checked/clean counts grew (bronze 8 -> 16, `orders_checked` 8 -> 16, `orders_clean` 6 -> 12) because every run
appends another copy of each raw order to bronze and `orders_clean` holds all copies until `orders_dedup` keeps one per order.
The rule flags only EUR rows (2 of 16 rows in `orders_checked`, both ORD-1006); INR (10) and USD (4) rows are not flagged. No order is rejected for
`unsupported_currency` alone (0 rows).

> DRAFT explanations written by the assistant from the real results: rewrite in your own words before submitting.

**Does the gold total change? No** (4 orders, ₹7,785.00, 126 points before and after). ORD-1006 (EUR) was already rejected by `bad_email` and
`bad_pincode`, so it never reached `silver.orders_clean`, `silver.orders_dedup` or gold. The new rule only adds a third reason to a row that was
already quarantined; gold would change only if the rule rejected a row that used to pass, and in this data every INR/USD order (including ORD-1005 with
`inr`) still passes.

**Does the new run add a second quarantine row for ORD-1006? No.** After the re-run `quarantine.orders` still has exactly one row for ORD-1006 (and one for ORD-1004),
although `silver.orders_checked` now has two copies of each (one per run). The part of the SQL that decides this is the insert into quarantine in
`10_orders_clean.sql`: `AND NOT EXISTS (SELECT 1 FROM quarantine.orders q WHERE q.source = c.source AND EQUAL_NULL(q.order_id, c.order_id) AND EQUAL_NULL(q.row_data:UPDATED_AT::TIMESTAMP_NTZ, c.updated_at))`
(lines 68-72). A rejected row is skipped when quarantine already has the same source, order_id and updated_at. The `QUALIFY ROW_NUMBER() OVER (PARTITION BY c.source, c.order_id, c.updated_at ORDER BY c.ingest_seq DESC) = 1`
(line 73) also keeps only one copy of a record inside a single run. Because the test ignores the reasons, the older quarantine row keeps its old reasons;
the new reason shows only in `silver.orders_checked`.

### B4
Event to add (NOT yet added or run): `MOCK_CRM_TIER_EVENTS` += `{"cust_id": "CUST-02", "email": "arjun.k@yahoo.in", "tier": "Gold", "effective_from": "2026-08-15"}`.

#### PRE-RUN PREDICTIONS (recorded 2026-11-12, before the event was added and before any B4 run)
> The assistant derived these from the actual SQL and the current Snowflake data (read-only queries, evidence in
> `report/screenshots/B/B4_prerun_state.txt`, queried 2026-11-12 04:27 UTC). The assignment requires predictions to be
> your own and the viva checks this: read the reasoning until you can explain it yourself, and edit the wording into your own words
> BEFORE the run. Do not change the numbers after the run.

| Quantity | Now (before) | **Prediction** | Actual after run |
|---|---|---|---|
| Rows for CUST-02 in `dim.customers_scd2` | 1 (Silver) | **2** | *(fill after the run)* |
| Tier used for ORD-1002 | Silver | **Gold** | |
| Loyalty points for ORD-1002 | 35 | **70** | |
| Total loyalty points in gold | 126 | **161** | |
| Gold rows whose `published_at` changed | n/a | **1** (ORD-1002 only) | |

Reasoning, with the evidence for each:
1. **CUST-02 rows = 2.** `30_customers_scd2.sql` builds one row per tier-change event for each customer; each period ends the day before the next change starts (`DATEADD(day,-1,LEAD(valid_from))`), the last one runs to 9999-12-31. CUST-02 has only one event now (Silver, 2024-01-15 to 9999-12-31, evidence query 1). Adding Gold effective 2026-08-15 gives Silver 2024-01-15 to 2026-08-14 and Gold 2026-08-15 to 9999-12-31 = 2 rows. (Bronze keeps duplicate copies of every event, 8 raw rows for 4 distinct events, but the `QUALIFY ROW_NUMBER() ... = 1` on (cust_id, valid_from) removes them, so duplicates do not add rows.)
2. **ORD-1002 tier = Gold.** `40_gold.sql` joins on `c.email = o.email AND o.order_date BETWEEN c.valid_from AND c.valid_to`. ORD-1002 has email `arjun.k@yahoo.in` and order_date 2026-09-01 (query 3). 2026-09-01 is after 2026-08-15, so it falls inside the Gold period and outside the Silver one (which ends 2026-08-14). It is Silver today only because the Gold event does not exist yet.
3. **ORD-1002 points = 70.** `loyalty_points = FLOOR(amount_inr / 100) * multiplier`. `amount_inr` = ROUND(42.50 x 83.20, 2) = 3536.00 (unchanged: tier does not affect money). FLOOR(3536.00 / 100) = 35, and the Gold multiplier in `ref.tier_multiplier` is 2, so 35 x 2 = 70 (today 35 x 1 = 35).
4. **Total points = 161.** Only ORD-1002 changes (the other orders belong to Priya and Meera): 12 + 70 + 63 + 16 = 161 (= 126 - 35 + 70). Revenue stays 7,785.00 because only the multiplier changes.
5. **published_at changed on 1 row.** The MERGE only updates a row `WHEN MATCHED AND t.row_hash <> s.row_hash` and only then sets `published_at = CURRENT_TIMESTAMP()`. `row_hash` covers tier, multiplier and loyalty_points, so it changes for ORD-1002 and for no other order. Evidence that the other rows really are stable: all 4 gold rows still carry the B1 run's `published_at` (2026-11-11 20:09:29.606 -08:00) even after the B3 re-run (query 5), i.e. a re-run changes nothing when the values are unchanged.

Cross-check (read-only what-if, a `SELECT` with the new event added inline; the event was NOT inserted and nothing was written): the **control** simulation without the event reproduced today's gold exactly (all 4 `row_hash` equal), and the simulation **with** the event gave CUST-02 = 2 rows, ORD-1002 = Gold x2 = 70 points, only ORD-1002's hash different, the other three equal.

What cannot be known exactly without running: the actual `published_at` timestamp of the updated row (it will be the time of the run). The five predicted quantities themselves are fully determined by the logic above.

Still to write after the run (4-6 sentences, your own words): how `row_hash` and `MERGE` make gold safe to re-run, and why bronze still grows by 8 order rows on every run.

#### ACTUAL RESULTS (separate from the predictions above, which were not edited)
Event added to `MOCK_CRM_TIER_EVENTS` in `elt/mock_data.py`; one full `fc.run_pipeline()` on 2026-11-12, run_id `20261112_043003` (04:30:03 UTC).
Evidence (`report/screenshots/B/`): `B4_before_published_at.txt` (read-only snapshot taken before anything changed), `B4_prerun_state.txt`, `B4_notebook_outputs.txt`,
`B4_notebook_part1.png` / `B4_notebook_part2.png` (rendered notebook section, headless Edge, not Snowsight), `B4_independent_verification.txt` (fresh connection). Notebook: section "B4" in `elt/freshcart_elt.ipynb`.

| Quantity | Committed prediction (72e290d) | **Actual** | Match |
|---|---|---|---|
| Rows for CUST-02 in `dim.customers_scd2` | 2 | **2** (Silver 2024-01-15 to 2026-08-14; Gold 2026-08-15 to 9999-12-31) | yes |
| Tier used for ORD-1002 | Gold | **Gold** (multiplier 2) | yes |
| Loyalty points for ORD-1002 | 70 | **70** (FLOOR(3536.00/100) x 2) | yes |
| Total loyalty points in gold | 161 | **161** (12 + 70 + 63 + 16); revenue unchanged 7,785.00 | yes |
| Gold rows whose `published_at` changed | 1 | **1** (ORD-1002 only) | yes |

**Discrepancies between prediction and actual: none.**

Details. `published_at` before: all four rows 2026-11-11 20:09:29.606 -08:00 (= 04:09:29 UTC, the B1 run). After: ORD-1002 2026-11-11 20:30:13.292 -08:00 (= 04:30:13 UTC, the B4 run);
ORD-1001, ORD-1003 and ORD-1005 unchanged. `row_hash` changed only for ORD-1002 (-7698738864412791922 to 3392257107350681567). Gold: 4 orders, 7785.00, 161 points.

**Idempotence check (second pass).** I ran only the transformation again (`SQL_30_CUSTOMERS_SCD2` then `SQL_40_GOLD`, nothing loaded). Result: 0 rows changed `published_at`
(ORD-1002 kept 20:30:13.292, the others kept 20:09:29.606), every `row_hash` identical, totals still 4 / 7785.00 / 161.

**Bronze growth.** `bronze.orders_raw` holds exactly 8 rows (6 web + 2 mobile, 2 landing files) for each of the three runs (`20261112_040919`, `20261112_042326`, `20261112_043003`) = 24 rows.
The B4 run added 8 order rows (16 to 24), 5 CRM rows (8 to 13; the 4 old events plus the new one, 5 distinct events in total), 1 FX reply (2 to 3) and 0 pincodes (already known).
`silver.orders_dedup` stayed at 4 and `quarantine.orders` at 2.

Process note (honest record). The first execution of my notebook's analysis cell failed with a `KeyError` (Snowflake returns column names in upper case, my code used lower case) **after** the pipeline cell had already run once.
I did not run the pipeline again. The "before" state was rebuilt with Snowflake Time Travel (tables as of 04:30:00 UTC, just before the run) and matches the pre-run snapshot file exactly. Because the cells were executed in two kernel sessions,
the `In [n]` counters in the notebook restart in the middle of the B4 section.

> DRAFT explanation written by the assistant: rewrite in your own words before submitting (assignment: 4-6 sentences).

**How `row_hash` and `MERGE` make gold safe to re-run, and why bronze still grows by 8 rows per run.** `SQL_40_GOLD` rebuilds `silver.orders_enriched` from scratch on every run and then `MERGE`s it into `gold.fct_orders`, matching on `order_id`.
For each order it computes `row_hash`, a `HASH` over all business columns (tier, multiplier, amounts, loyalty points, location, `updated_at`). The `MERGE` only does an `UPDATE` (and sets a new `published_at`) `WHEN MATCHED AND t.row_hash <> s.row_hash`,
and only `INSERT`s `WHEN NOT MATCHED`, so re-running never creates a second row for an order and never touches a row whose values did not change; in B4 only ORD-1002 changed, and the second pass changed nothing.
Bronze, in contrast, is an append-only record of what was received: every run extracts the same 8 raw orders again, writes them to new landing files named with the new `run_id`, and `COPY INTO` appends them, and bronze does no deduplication.
The duplicates are removed later in silver (`QUALIFY ROW_NUMBER() ... = 1` in `SQL_20_ORDERS_DEDUP`), which is why silver and gold stay the same size while bronze grows by 6 web + 2 mobile = 8 rows each run.

### B5
**The sixth check** (`elt/freshcart.py`, `quality_checks()`, "orders dated in the future"; it should be 0):
```sql
SELECT COUNT_IF(order_date > CURRENT_DATE()) FROM silver.orders_dedup
```
(`quality_checks()` only prints OK/PROBLEM and does not stop the pipeline, as in the reference notebook.) To rebuild silver/gold on its own, the transform stage of `run_pipeline()` was moved into a function `transform(run_id)`;
`run_pipeline()` calls it and behaves as before.

**1. Control (real data): the new check is 0 / OK.** Output of `quality_checks()`: `orders dated in the future   0   OK`.

**2. Deliberate failure.** Mock order, clearly marked: `order_id` `TEST-B5-FUTURE-DATE-001`, web format, `order_date` 2026-12-31 (the Snowflake session date was 2026-11-11), existing customer email `priya.r@gmail.com` and existing pincode `600041`,
no amount, loaded with run_id `20261112_043630_b5test`. It has no amount on purpose: a missing amount is allowed and a future date has no FX rate, so no other check fires. It was loaded on its own (one landing file, one bronze row) and silver/gold were rebuilt with `transform()`.
The exact `quality_checks()` output:
```
   rows gained or lost while enriching    0   OK
   duplicate orders in gold               0   OK
   orders with no customer match          0   OK
   orders with an amount but no FX rate   0   OK
   orders with no city                    0   OK
   orders dated in the future             1   PROBLEM
   share of rows rejected                 24%
```
(The rejected share drops from 25% to 24% only because bronze has one extra valid row.) The mock order also reached gold (5 orders; revenue 7,785.00 and 161 points unchanged, because its amount is empty).

**3. Cleanup (only the test data).** Reading the SQL first: silver, dim and `ref.fx_daily` are `CREATE OR REPLACE` (rebuilt from bronze), `quarantine.orders` only inserts (the mock order is valid, 0 rows), gold's `MERGE` never deletes, bronze is append-only and `PUT` leaves the file in the stage.
So the test data could only be in `bronze.orders_raw`, `gold.fct_orders`, the stage folder of the test run and the local landing file. Before deleting, the cell counted what matched the markers and asserted exact expectations (it would have stopped without deleting): bronze rows matching order id AND test run id = 1 (any run: 1; any order in the test run: 1),
gold rows for that order id = 1, quarantine = 0, staged files = 1, while all other rows (bronze 24, gold 4) were not matched. Then it deleted exactly: 1 row from `bronze.orders_raw`, 1 row from `gold.fct_orders`, the one staged file, the local landing file.
Nothing else was deleted or altered. (Snowflake Time Travel still holds the deleted rows for the retention period, as for any delete.)

**4. Recovery.** `transform()` re-run from the cleaned bronze: `orders dated in the future   0   OK`, share rejected back to 25%, all other checks OK.
Notebook cleanup checks: **19 of 19 PASS**. An independent snapshot taken after the cleanup (`B5_after_state.txt`) is **identical** to the baseline taken before the mock order existed (`B5_before_state.txt`): all 13 table counts, the four gold rows including `row_hash` and `published_at`, the bronze run_ids and the stage folders.

Evidence (`report/screenshots/B/`): `B5_notebook_part1.png` (check, mock order, load, the PROBLEM output), `B5_notebook_part2.png` (pre-delete counts, delete, recovery, 19/19 PASS) (rendered notebook, headless Edge, not Snowsight),
`B5_notebook_outputs.txt`, `B5_before_state.txt`, `B5_after_state.txt`. Notebook: section "B5" in `elt/freshcart_elt.ipynb`.

> DRAFT written by the assistant: rewrite in your own words before submitting (assignment: 3-4 sentences). **One part needs you:** the assignment asks for "the one situation from the lecture"
> where ETL still wins; the lecture material is not available to me, so the ETL situation below is a general textbook one. Replace it with the situation your lecture named.

**Why is ELT better than ETL for FreshCart, and when would ETL still win?** FreshCart's sources send messy data in different shapes (flat web JSON, nested mobile JSON, bad emails, duplicates), so it is better to land everything unchanged in bronze first and clean it afterwards with SQL inside Snowflake.
That keeps a raw copy of everything received, so a changed rule or a late fix is just a re-run of the SQL (B3 added a rule, B4 a tier change, both without re-extracting anything), and bad rows go to quarantine with reasons instead of being lost; the warehouse does the heavy work, so the Python side stays small.
ETL would still win when the data must be changed *before* it is allowed to land in the warehouse, for example when personal or card data has to be masked or removed first for compliance, because ELT would store the raw sensitive values in bronze.

## Part C
> Reference-notebook note: the Mage Iris reference notebook was NOT available. Everything below
> follows only what the assignment text states. My own choices (not from the reference): the
> accuracy gate threshold `MIN_ACCURACY = 0.90` in `train_model`, the block output shapes, and
> `random_state=42`. If the reference uses another threshold, the pass/fail column of C2 may differ.

### C1
Project: `iris_project/` (Mage 0.9.80, Python 3.12.6, native Windows). Pipeline `iris_classifier`,
wired in `iris_project/pipelines/iris_classifier/metadata.yaml`.

Final graph (C1 base blocks + C3 branch + C4 block; see also the real UI capture in C3):
```
load_iris (data_loader, @test: 150 rows, target column)
   |
validate_data (transformer, C4, @test x2: no missing values, exactly 3 classes)
   |
prepare_data (transformer, @test: split column, train/test)      [pytest also tests the 120/30 split]
   |
train_model (transformer, @test test_accuracy >= 0.90, 30 test rows)
   |------------------------------\
save_results (data_exporter,       evaluate_model (transformer, C3,
 @test: CSV exists, 30 rows)        @test: 3 class rows, support sum 30)
```
(Redraw this by hand or in a tool if you want your own diagram.)

Run: `mage run iris_project iris_classifier --test` (default max_depth=3), evidence
`screenshots/C/C1_mage_run_test.txt`. That run used the original 4 blocks: every block printed
`1/1 tests passed.`, `max_depth=3 test_accuracy=1.0000`, `Saved 30 rows to ...iris_predictions.csv`,
`Pipeline run completed.` (exit 0). The 6-block final run is in `C4_full_pipeline_run.txt`.

### C2
Command per depth (CSV deleted before each run): `mage run iris_project iris_classifier --test --runtime-vars '{"max_depth": N}'`
(run with the original 4-block pipeline). Evidence: `screenshots/C/C2_depth_N.txt`, `C2_summary.txt`.

| max_depth | Test accuracy | test_accuracy passed? | iris_predictions.csv created? |
|---|---|---|---|
| 1 | 0.6333 | NO (0.6333 < 0.90 gate, exit 1) | NO |
| 2 | 0.9667 | yes | yes |
| 3 | 1.0000 | yes | yes |
| 4 | 1.0000 | yes | yes |
| 5 | 1.0000 | yes | yes |

At depth 1 the log ends with `FAIL: test_accuracy (block: train_model)`, `AssertionError: test accuracy
0.6333 is below the 0.9 gate`, `0/1 tests passed.`, and contains no `Saved ...` line (verified by grep:
0 matches); with all 6 blocks (`C4_depth1_gate.txt`) `evaluate_model` also did not run (no confusion matrix).

> DRAFT explanation (assistant-written; rewrite in your own words): With `--test`, Mage runs each
> block's `@test` functions right after the block. If an assertion fails, the block is marked failed
> and the run stops with a non-zero exit code, so blocks that depend on `train_model` (here
> `save_results`, and `evaluate_model` in C3) are never started. That is better than saving first and
> checking afterwards because a bad model's file never exists to be picked up by anything else, and
> the failure is visible immediately in the run instead of being hidden in a file nobody re-checks.

### C3
`train_model` now has two downstream blocks: `save_results` and `evaluate_model`
(`downstream_blocks` of `train_model` in `iris_project/pipelines/iris_classifier/metadata.yaml`).
Run at max_depth=2 (the informative case, one error); evidence `screenshots/C/C3_eval_depth_2.txt`
(depth 3 in `C3_eval_depth_3.txt`).

Confusion matrix (rows = actual, columns = predicted), max_depth=2:
```
                   pred_setosa  pred_versicolor  pred_virginica
actual_setosa               10                0               0
actual_versicolor            0                8               1
actual_virginica             0                0              11
```
Metrics table:
```
       class  precision  recall  f1-score  support
      setosa     1.0000  1.0000    1.0000  10.0000
  versicolor     1.0000  0.8889    0.9412   9.0000
   virginica     0.9167  1.0000    0.9565  11.0000
    accuracy     0.9667  0.9667    0.9667   0.9667
   macro avg     0.9722  0.9630    0.9659  30.0000
weighted avg     0.9694  0.9667    0.9664  30.0000
```
UI screenshot: `screenshots/C/C3_mage_ui_pipeline_graph.png` (real capture of
`http://localhost:6789/pipelines/iris_classifier/edit`, Mage v0.9.80) showing the tree
load_iris -> validate_data -> prepare_data -> train_model -> {save_results, evaluate_model}.
It was captured with headless Edge against a local server started with `REQUIRE_USER_AUTHENTICATION=0`
(otherwise Mage shows a sign-in page).

Cloudflare tunnel: NOT used, and I do not claim it satisfies the requirement. Why the assignment
mentions it (my reading, unverified against the course material): in Colab the Mage server runs on
a remote VM, so a tunnel is needed to open the UI in your own browser. Here Mage runs on the same
Windows machine, so `http://localhost:6789` is directly reachable. `cloudflared` is not installed.
If your instructor requires an actual tunnel URL: install cloudflared and run
`cloudflared tunnel --url http://localhost:6789` while `mage start iris_project` is running, but note
this publishes your Mage server to the internet (keep authentication ON, close it afterwards).
Ask the instructor whether a localhost screenshot is acceptable.

### C4
New block: `validate_data` (transformer, `iris_project/transformers/validate_data.py`) between
`load_iris` and `prepare_data`, with two `@test` functions: `test_no_missing_values` and
`test_three_classes`. Full 6-block run: `screenshots/C/C4_full_pipeline_run.txt` (exit 0,
`validate_data: 150 rows, 0 missing values, 3 classes`, `2/2 tests passed.`).
Negative check (tests fail when data is bad; run directly in Python): with one NaN ->
`FAIL: Found 1 missing values`; with only 2 classes -> `FAIL: Expected exactly 3 classes, got [0, 1]`.
Mage dependencies are in `requirements-mage.txt` (not installed by CI). pytest (CI test) still passes locally.

## Part D
### D1
### D2
### D3

## Part E
### Integration diagram
### Reflection (half page)

## Bonus
