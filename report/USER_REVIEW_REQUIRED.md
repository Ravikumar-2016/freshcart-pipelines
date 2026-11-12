# Items that need YOUR review before you submit

The explanations in `report/report.html` (and `report/answers.md`) were **drafted by Claude**, not written by you. The assignment says explanations must be your own, and the viva checks this. Nothing below has been reviewed by you yet. Read each one, make sure you understand it, rephrase it in your own words, then edit `report/report.html` and re-render:

```powershell
.\.venv\Scripts\python.exe report\make_pdf.py 23BCS095_Gunti_Ravi_Kumar
```

## 1. Needs YOUR input (cannot be filled by Claude)
**B5, the ETL situation from the lecture.** The assignment asks "in which one situation from the lecture would ETL still win?". The lecture is not in the project, so Claude did not invent it. The report currently has a generic example (masking personal or card data before it may land in the warehouse) and a visible marker `[STUDENT INPUT NEEDED ...]`. Replace the example with the situation your lecture named, and delete the marker.

## 2. Draft sections, with a short suggested rewrite you can adapt
Keep the facts (numbers, file names, results); change the wording to yours.

**A2: "can a teammate see my code after `git commit`?"** *No. `git commit` only saves the snapshot in my local repository on my laptop. My teammate can see it on GitHub only after I run `git push`.* (The six-row table is also a draft: check the last column is in your words.)

**B2: tracing ORD-1003 and ORD-1005.** Check you can say: the web and mobile copies have different field names because they come from different APIs, and bronze stores them as received; SQL_10 maps both to the same columns and cleans them; `QUALIFY ROW_NUMBER() ... ORDER BY updated_at DESC` keeps the newest copy (the mobile one, 18:40); gold amount = 2100.00 x 1.0, points = FLOOR(2100/100) x 3 = 63. ORD-1005 vs ORD-1001: the join on `email` and `order_date BETWEEN valid_from AND valid_to` in `dim.customers_scd2` gives the tier on the order date (Silver on 09-01, Gold from 09-03).

**B3: gold unchanged, no second quarantine row.** *Gold does not change because ORD-1006 was already rejected for its email and pincode and never reached silver.orders_clean, so the new rule only adds a third reason. The re-run does not add a quarantine row because the `NOT EXISTS` in the quarantine insert skips a record whose source, order_id and updated_at are already there; it does not look at the reasons.*

**B4: `row_hash` and MERGE, and bronze growth (4-6 sentences).** *Gold is rebuilt on every run and merged on `order_id`. `row_hash` is a hash of all business columns, and the MERGE updates a row only when the hash differs (and sets a new `published_at`), otherwise it leaves the row alone, so re-running never duplicates an order or touches an unchanged one. Bronze is append-only: each run writes the same 8 raw orders to new landing files and COPY INTO adds them, and the duplicates are removed later in silver by the ROW_NUMBER deduplication.*

**B5: ELT vs ETL (3-4 sentences).** *FreshCart receives messy data in different shapes, so it is better to load it raw into bronze and clean it with SQL in Snowflake: the raw copy is kept, a new rule only needs a re-run of the SQL (B3, B4), bad rows go to quarantine with reasons, and the warehouse does the heavy work.* Then add the lecture's ETL situation (section 1).

**C2: how a failing `@test` stops `save_results`.** *With `--test`, Mage runs a block's tests right after the block. When the `train_model` test fails (depth 1, accuracy 0.6333 below the 0.90 gate), the run stops with exit code 1, so the blocks that depend on it never start and no CSV is written. This is better than saving first and checking later, because a bad result never exists as a file that something else could use.* (Note: the 0.90 threshold was Claude's choice because the reference notebook was not available; be ready to say so.)

**D3: crash before ACK, and `requeue=True`.** *With manual acks the broker keeps a message as unacknowledged until the consumer acks it; if the consumer crashes first, the broker redelivers it (flag `redelivered=True`). A malformed message sent back with `requeue=True` fails again every time, so it loops forever and wastes CPU and blocks the queue; `requeue=False` discards it once. No dead-letter exchange was configured.*

**Bonus: flow and idempotency.** *The consumer collects order messages for 60 s, writes them with `write_landing()`, loads them with `load_file()`, runs the existing transform, and acks the messages only after the load. Running it twice appended rows to bronze but gold stayed at 7 orders / 9,535.00 / 205 points, because silver deduplicates and the gold MERGE only updates a row when its `row_hash` changes.*

**Reflection.** It describes a real event in this project (the B4 `KeyError` caused by Snowflake's upper-case column names, the Time Travel recovery, and the notebook re-run problem found later). Check it matches what you remember and edit it into your own voice.

## 3. Be ready for the viva
- **D1 predictions:** the expected recipients came from your prompt, but the written reasoning was drafted with Claude. Be able to redo all six rows and explain the two-word key.
- **B4 predictions:** committed by you before the run (commit `72e290d`); the reasoning was derived by Claude from the SQL.
- **Mage accuracy gate 0.90** is Claude's own choice.

## 4. Instructor confirmation needed
- **Cloudflare tunnel (C3):** the Mage UI screenshot is from `http://localhost:6789`, not through a tunnel. The report does not claim this satisfies the tunnel requirement. Ask the instructor whether it is acceptable.
- **Screenshots:** the notebook "screenshots" are renders of the saved notebooks (headless Edge), not Snowsight/terminal screenshots; D2/D3 evidence is log files. Ask whether that is acceptable.
