# Part B plan: FreshCart ELT on Snowflake (local VS Code, Windows)

Status: PLANNING ONLY. No Snowflake account exists, nothing has been executed.

## 0. Sources (what was actually inspected)
| File (in `elt/`) | What it is | Use |
|---|---|---|
| `reference/freshcart_elt_flowchart.html` | Interactive 13-step flowchart with the sample-data numbers | Specification of steps/numbers |
| `freshcart_elt_simple_(1).ipynb` | Single-notebook version: `SQL_00..SQL_40` constants, `write_landing`, `load_file`, `quality_checks`, `run_pipeline`, `MOCK_CRM_TIER_EVENTS` | **Matches the assignment's names. Base for my notebook.** |
| `freshcart_elt_commented.ipynb` | Same SQL as `simple` (verified identical after stripping comments/whitespace), with a comment on every line | Optional reading aid |
| `freshcart_elt_colab (1).ipynb` | Older multi-file/CLI version (`extract.py`, `snowflake_io.py`, `run_pipeline.py`, `--setup/--mock`) | Not used: different structure; adds `ops.run_log`; its quarantine `NOT EXISTS` reads `row_data:updated_at` (lowercase) whereas `simple` correctly reads `row_data:UPDATED_AT`, because `OBJECT_CONSTRUCT(*)` upper-cases keys |
| `freshcart_elt.ipynb` (created by me) | `simple` notebook, outputs stripped, only the install cell and login cell changed (login from `.env`, local `landing/` folder). All other 49 cells identical to the reference (checked by script). NOT executed. | My working/submission notebook |

**SECURITY:** all three reference notebooks contain someone else's real Snowflake account and user name, and the Colab one also a plaintext password, with the ACCOUNTADMIN role. They are not mine to use. They are git-ignored (`.gitignore`) and must never be committed or used to log in. Consider telling the instructor that this login is exposed in the distributed notebooks.

## 1. The 13 flowchart steps (from `STEPS` in the HTML)
1 Log in (`conn`) | 2 Setup (`SQL_00_SETUP`: FRESHCART_WH, FRESHCART, schemas bronze/silver/dim/ref/gold/quarantine, empty tables) |
3 Extract (`write_landing`: 6 web, 2 mobile, 4 CRM, 1 FX files) | 4 Load (`load_file`: PUT + COPY INTO bronze; orders 6+2=8) |
5 Clean and check (`SQL_10_ORDERS_CLEAN`: 8 in, 6 pass) | 6 Quarantine (ORD-1004 negative amount; ORD-1006 bad email + 5-digit pincode) |
7 Dedup (`SQL_20_ORDERS_DEDUP`: 6 -> 4) | 8 Any new pincodes? (first run: 600041, 560034, 400050) |
9 Look up pincodes (`mock_pincode_response` -> `bronze.pincode_raw`) | 10 Lookup tables (`SQL_30` tiers/SCD2, `SQL_31` FX, `SQL_32` pincodes) |
11 Enrich + publish gold (`SQL_40_GOLD`: MERGE into `gold.fct_orders`) | 12 Quality checks (`quality_checks()`: five counts that must be 0, plus share rejected) |
13 Result: 4 orders, revenue 7,785.00, 126 points.

## 2. Objects the notebook creates (all in Snowflake database FRESHCART, warehouse FRESHCART_WH, XSMALL)
- Schemas: bronze, silver, dim, ref, gold, quarantine. File format `bronze.ff_ndjson`, stage `bronze.landing`.
- Bronze: `orders_raw`, `customers_raw`, `fx_raw`, `pincode_raw` (all: ingest_seq, source, raw VARIANT, run_id, extracted_at, src_file, src_row, loaded_at).
- Silver: `orders_checked` (transient), `orders_clean`, `orders_dedup`, `orders_enriched`. Dim: `customers_scd2`. Ref: `tier_multiplier`, `state_region`, `pincode_geo`, `fx_daily`. Quarantine: `orders`. Gold: `fct_orders` (MERGE on order_id, `row_hash`, `published_at`).
- Python: `write_landing(source, records, run_id)`, `load_file(local_path, table, stage_dir)`, `run_sql`, `query`, `show`, `quality_checks()`, `run_pipeline()`; mock data `MOCK_WEB_ORDERS`, `MOCK_MOBILE_ORDERS`, `MOCK_CRM_TIER_EVENTS`, `MOCK_FX_RESPONSES`, `MOCK_PINCODES`.

## 3. Dependencies (nothing installed yet)
| Package | Needed for | Status |
|---|---|---|
| snowflake-connector-python `>=3.6,<3.13` | connect, PUT, COPY INTO | not installed. Capped because 4.x/5.x need cryptography>=46 but mage-ai 0.9.80 pins 42.0.4 (dry-run verified: 3.12.4 keeps cryptography 42.0.4) |
| python-dotenv | read `.env` | not installed |
| pandas | `show()` tables | installed (2.3.3) |
| ipykernel | run the notebook in VS Code | installed (6.15.0). The VS Code Jupyter extension is also needed (not checked) |
Recorded in `requirements-elt.txt` (separate from CI's `requirements.txt`).

## 4. Plan per requirement
**Setup (blocked on me):** create a Snowflake trial account, put login in `.env`, connect, then run the notebook. Windows-specific check: `PUT 'file://C:/...'` with a forward-slash path (the notebook uses `Path.as_posix()`); verify on first run. If MFA blocks a plain password, use a programmatic access token as the password.

**B1 baseline (needs account):** run top to bottom ONCE on a fresh database. Capture: bronze orders_raw = 8 (6 web + 2 mobile); `silver.orders_clean` = 6; `quarantine.orders` = 2 (ORD-1004, ORD-1006); `silver.orders_dedup` = 4; gold line `4 orders, revenue ₹7785.00, 126 loyalty points`; `share of rows rejected 25%`. Note: bronze grows by 8 on every run, so take the "after one run" screenshot before any re-run.

**B2 traces (writing task, mostly no code):** use `bronze.orders_raw` raw JSON (web: `order_id/cust_email/amount/updated_at`; mobile: `orderId/customer.email/total.value/updatedAt`), the `unified`/`typed` CTEs in `SQL_10`, `QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC, ingest_seq DESC) = 1` in `SQL_20`, and the arithmetic in `SQL_40` (`ROUND(amount * fx_rate, 2)`, `FLOOR(amount_inr / 100) * multiplier`). ORD-1005 vs ORD-1001: join `dim.customers_scd2` on `email` and `order_date BETWEEN valid_from AND valid_to`, then `ref.tier_multiplier`. The student writes these in their own words.

**B3 (edit one SQL line, needs account):** add one `IFF(...)` line for `unsupported_currency` inside `ARRAY_CONSTRUCT_COMPACT` in `SQL_10_ORDERS_CLEAN`. Pitfalls found in the reference: (a) the quarantine insert has a `NOT EXISTS` keyed on (source, order_id, updated_at), so ORD-1006 gets no second quarantine row and `quarantine.orders.reasons` keeps the OLD array; capture the "after" reasons from `silver.orders_checked` and capture "before" first; (b) the currency is upper-cased before the check.

**B4 (needs account):** add the CUST-02 Gold event (effective_from 2026-08-15) to `MOCK_CRM_TIER_EVENTS`. The student writes predictions BEFORE running (viva checks this). Before the run, also record `published_at` of every gold row so "rows whose published_at changed" can be counted. Mechanics to explain: `row_hash` + `MERGE ... WHEN MATCHED AND t.row_hash <> s.row_hash`; bronze is append-only (each run adds 8 order rows).

**B5 (needs account):** add a sixth entry to `quality_checks()`. Easiest to break on purpose: "orders in `silver.orders_dedup` with `order_date` in the future" (add a mock web order dated in the future). PITFALL: bronze is append-only and gold `MERGE` never deletes, so "removing the mock order" from the Python list is NOT enough; clean up with `DELETE` on `bronze.orders_raw` (that order_id) and on `gold.fct_orders` (and `quarantine.orders` if it was quarantined), then re-run and show the check is 0 again. ETL-vs-ELT answer: student's own words.

**Bonus (needs account + Part D broker):** consume FreshCart-style order messages from RabbitMQ for 1 minute, `write_landing(...)`, `load_file(...)`, run the SQL, and show a double run leaves gold totals unchanged. Design decision to make: `SQL_10` only reads `source IN ('web','mobile')`, so streamed messages must use the web (flat) shape and `source='web'`, or a third source branch must be added.

## 5. Open items / blockers
1. Snowflake trial account (external, needed for B1-B5 and bonus). Not created.
2. Part D RabbitMQ broker (only for the bonus).
3. Whether VS Code has the Jupyter extension (not checked).
4. Real SQL/Python semantics of the notebook are only read, never executed.
