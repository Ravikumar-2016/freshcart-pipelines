# Items for YOUR review before submission

The explanations in `report/report.html` were written by **Claude**, not by you. The assignment says explanations must be your own and the viva checks this. Read each one, make sure you understand it, put it in your own words, then edit `report/report.html` and re-render:

```powershell
.\.venv\Scripts\python.exe report\make_pdf.py 23BCS095_Gunti_Ravi_Kumar
```
The facts (numbers, files, commits) are checked against evidence; see `report/AUDIT.md`. The wording is what you should own.

## 1. One thing to confirm (B5, the lecture's ETL situation)
The ETL lecture PDF and `RiverRetail_DataEngineering_U1.xlsx` you mentioned are **not on this machine**. The B5 answer now cites the course notes found in `material.zip`: `30-09-2026/data_transformation_orchestration.html`, section "ETL and ELT: where the transformation runs". That page says ETL is best for strict pre-load compliance, small or costly targets and heavy non-SQL processing, and for sensitive data ETL "can mask or drop PII before it ever lands" while ELT lands raw PII and needs masking policies. The report uses that (masking personal data before the load).
**You should check** that this is the situation your lecture/PDF showed. If your PDF stressed a different situation, replace the last two sentences of B5.

## 2. Sections to put in your own words (suggested short versions; keep the facts)
- **A2** *A commit only saves a snapshot in my local repository on my laptop. My teammate can see it on GitHub only after I run `git push`.*
- **B2** Say: web and mobile copies differ because they come from different APIs, bronze keeps them as received; SQL_10 maps both to the same columns and cleans them; `QUALIFY ROW_NUMBER() ... ORDER BY updated_at DESC, ingest_seq DESC` keeps the newest copy (mobile 18:40); gold: 2100.00 x 1.0, FLOOR(2100/100) x 3 = 63; the tier join on email and `order_date BETWEEN valid_from AND valid_to` explains Silver (ORD-1001) vs Gold (ORD-1005).
- **B3** *ORD-1006 was already rejected for its email and pincode, so it never reached gold. A re-run adds no quarantine row because the NOT EXISTS skips a record with the same source, order_id and updated_at; it does not compare the reasons.*
- **B4** *Gold is merged on order_id. row_hash is a hash of every column except order_id; the MERGE updates a row (and sets a new published_at) only when the hash differs, so re-running never duplicates or touches an unchanged row. Bronze is append-only: each run loads the 8 raw orders again from new landing files, and silver removes the duplicates.*
- **C2** *With --test Mage runs a block's tests right after the block. At depth 1 the train_model test fails (accuracy 0.6333 < 0.90), the run stops with exit code 1, and save_results and evaluate_model never start, so no CSV is written. Saving first and checking later would leave a bad file behind.*
- **D3** *With manual acks a delivered message stays unacknowledged until the consumer acks it; if the consumer crashes first, the broker redelivers it (redelivered=True). With requeue=True an always-bad message returns to the queue and fails again forever (a poison message); requeue=False discards it once. No dead-letter exchange is configured.*
- **Bonus** *The consumer collects orders for 60 s, writes them with write_landing(), loads them with load_file(), runs the existing transform, and acks only after the load. Running twice appended to bronze but gold stayed at 7 orders / 9,535.00 / 205 points, because silver deduplicates and the gold MERGE updates a row only when its row_hash changes.*
- **Reflection** It states that the project was built with Claude Code and describes what actually happened (the B4 KeyError, Time Travel, the notebook re-run problem). Edit the voice, but keep it true: the diagnosis was made from the traceback by the assistant, not by you.

## 3. Be ready for the viva
- D1 predictions: the expected recipients came from your own prompt, the reasoning was drafted with Claude: redo all six rows yourself, including the two-word key.
- B4 predictions: you committed them (`72e290d`) before the run; the reasoning was derived by Claude from the SQL.
- The 0.90 Mage accuracy gate is a design choice made in this project, not an instructor value.

## 4. Instructor confirmation needed (not decided by Claude)
- **Cloudflare tunnel (C3):** the assignment says "Open the pipeline in the Mage UI (through the Cloudflare tunnel)". The screenshot is from `http://localhost:6789`; the report does not claim this satisfies the tunnel.
- **Screenshots:** the notebook "screenshots" are renders of the saved notebooks (not Snowsight/terminal captures); D2/D3 evidence is log files.
- **Mage threshold:** whether the instructor expects a specific accuracy threshold.
