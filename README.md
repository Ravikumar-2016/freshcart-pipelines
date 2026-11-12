# freshcart-pipelines

Data Engineering assignment **"From Git to Gold"**: version control and CI, a Snowflake ELT pipeline, a Mage ML pipeline and a RabbitMQ event stream.

Repository: https://github.com/Ravikumar-2016/freshcart-pipelines

## Layout

| Path | Contents | Assignment part |
|---|---|---|
| `.github/workflows/ci.yml` | GitHub Actions workflow (Python 3.12, pytest on every push) | A |
| `tests/` | pytest tests run by CI (`test_prepare_data.py`, `test_topic_routing.py`) | A |
| `elt/` | FreshCart ELT: notebook `freshcart_elt.ipynb`, `freshcart.py`, `mock_data.py`, `sql/` (SQL_00 to SQL_40), `test_connection.py` | B |
| `iris_project/` | Mage project (pipeline `iris_classifier`) and the executed notebook `iris_classifier_run.ipynb` | C |
| `stream/` | `dispatcher.py`, `driver.py`, routing and ACK/NACK checks, bonus order consumer | D, bonus |
| `report/` | `report.html` (source), final PDF, `make_pdf.py`, notes, audits, `screenshots/` (evidence) | E |

## Setup (Windows, PowerShell, from the project root)

```powershell
python -m venv .venv                       # Python 3.12
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt            # pytest, pandas, scikit-learn (what CI installs)
Copy-Item .env.example .env                # then fill in .env locally; it is git-ignored, never commit it
```

Extra requirements files (install the ones you need into the same `.venv`):

| File | Adds | Needed for |
|---|---|---|
| `requirements-elt.txt` | Snowflake connector, python-dotenv | Part B, bonus |
| `requirements-mage.txt` | `mage-ai==0.9.80` | Part C |
| `requirements-stream.txt` | `pika`, python-dotenv | Part D, bonus |

## Part A: tests and CI

```powershell
python -m pytest        # 10 tests: the prepare_data 80/20 split (120/30) and the RabbitMQ topic-routing rules
```
CI (`.github/workflows/ci.yml`) runs on every push: check out the code, set up Python 3.12, `pip install -r requirements.txt`, `python -m pytest`. Results are in the GitHub Actions tab; the green, red and fixed runs are in `report/screenshots/A/`.

## Part B: FreshCart ELT on Snowflake

1. `pip install -r requirements-elt.txt`
2. In `.env` set `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD` (and, as in `.env.example`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_ROLE`). The account identifier is shown in Snowsight (your name, Account, View account details). Never put these values in code or Git.
3. Create the warehouse and database once, in a Snowsight worksheet: the first statements of `elt/sql/00_setup.sql` (`CREATE WAREHOUSE IF NOT EXISTS FRESHCART_WH ...; CREATE DATABASE IF NOT EXISTS FRESHCART_DB;`). The notebook's setup cell runs the rest of that script (schemas, stage, tables).
4. Check the login (read-only): `python elt\test_connection.py`
5. Open `elt/freshcart_elt.ipynb` in VS Code, choose the `.venv` Python kernel and run all cells.

Notes: the cell before the first pipeline run asserts that `bronze.orders_raw` is empty, because the B1 numbers (8 raw rows, 126 points) are only valid after exactly one run on an empty database. To start clean, create an empty database and set `SNOWFLAKE_DATABASE` to its name (the setup SQL follows it). Bronze grows by 8 order rows on every later run (B3 to B5 and the "run it again" section re-run the pipeline). The notebook in the repository already contains the executed outputs. The sample data is in `elt/mock_data.py`; raw landing files are written to `elt/landing/` (git-ignored).

## Part C: Mage ML pipeline

1. `pip install -r requirements-mage.txt`
2. Run the pipeline with its tests (from the project root):
   ```powershell
   .\.venv\Scripts\mage.exe run iris_project iris_classifier --test
   ```
   Every block prints `tests passed`; `iris_predictions.csv` is written in the current folder (git-ignored).
3. Pass a run-time variable (C2). **In Windows PowerShell the inner quotes must be escaped**; the unescaped form `'{"max_depth": 2}'` is silently ignored and the default depth 3 is used:
   ```powershell
   Remove-Item iris_predictions.csv -ErrorAction SilentlyContinue
   .\.venv\Scripts\mage.exe run iris_project iris_classifier --test --runtime-vars '{\"max_depth\": 2}'
   ```
   With `max_depth` 1 the `train_model` test fails (accuracy 0.6333 is below the 0.90 gate), the command exits with code 1 and no CSV is written.
4. Mage UI: `.\.venv\Scripts\mage.exe start iris_project`, then open http://localhost:6789 (the UI asks for a login). For the C3 screenshot the local server was made public with a Cloudflare Quick Tunnel (`cloudflared tunnel --url http://127.0.0.1:6789`, `cloudflared` downloaded separately); close the tunnel after use, because Mage's login is the only protection.
5. The executed notebook `iris_project/iris_classifier_run.ipynb` runs the commands above and shows the C1 to C4 outputs. It must be run with the project root as working directory (it checks this), so re-run it with:
   ```powershell
   .\.venv\Scripts\python.exe -c "import nbformat, pathlib; from nbclient import NotebookClient; nb = nbformat.read('iris_project/iris_classifier_run.ipynb', as_version=4); NotebookClient(nb, timeout=900, resources={'metadata': {'path': str(pathlib.Path.cwd())}}).execute(); nbformat.write(nb, 'iris_project/iris_classifier_rerun.ipynb')"
   ```

## Part D: RabbitMQ topic exchange (CloudAMQP)

1. `pip install -r requirements-stream.txt`
2. In `.env` set `RABBITMQ_URL` to the AMQP URL of your CloudAMQP instance (Instance details, AMQP URL). Never commit it.
3. Check the connection and verify D1 on the live broker (six routing keys):
   ```powershell
   python stream/check_connection.py
   python stream/verify_routing.py
   ```
4. D2: one terminal per driver, started before the dispatcher (a message with no matching queue is dropped):
   ```powershell
   python stream/driver.py Ravi "bangalore.koramangala.*"
   python stream/driver.py Arjun "bangalore.*.ride"
   python stream/driver.py Control "bangalore.#"
   python stream/dispatcher.py --duration 120      # one request every 2 s; every 10th message has no zone (D3)
   ```
   `dispatcher.py` options: `--interval`, `--duration`, `--count`, `--bad-every N` (0 = never), `--seed`. Drivers accept `--duration`.
5. D3 demonstration (valid message ACK, malformed NACK with `requeue=False`, crash before ACK, `requeue=True` loop): `python stream/d3_demo.py`
6. To check logs against the routing rules, save each process output as `<prefix>_dispatcher.log` and `<prefix>_driver_<Name>.log` in one folder (the evidence in `report/screenshots/D/` was produced this way) and run: `python stream/verify_logs.py report/screenshots/D D2`

## Bonus: RabbitMQ orders into the lakehouse

Needs Part B (tables created in Snowflake) and Part D (broker) to be configured in `.env`.
```powershell
python stream/order_consumer.py --seconds 60   # collect for one minute, then write_landing -> load_file -> transform -> gold
python stream/bonus_demo.py 60                 # about 2.5 minutes: publishes 3 test orders (BONUS-TEST-001..003) twice, shows gold does not double, then removes only those test rows after checking exact counts
```
`bonus_demo.py` writes to the Snowflake database named in `.env` and cleans up after itself; it stops without deleting anything if the counts are not as expected. Results: `report/screenshots/Bonus/`.

## Report

The report source is `report/report.html`; the final PDF is `report/23BCS095_Gunti_Ravi_Kumar_Pipelines.pdf`. To regenerate it (needs Microsoft Edge installed at `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`):
```powershell
.\.venv\Scripts\python.exe report\make_pdf.py 23BCS095_Gunti_Ravi_Kumar     # writes report\23BCS095_Gunti_Ravi_Kumar_Pipelines.pdf, prints the body page count (limit 8)
```
Without an argument it writes a draft PDF to `report/build/` (git-ignored).

## Evidence and notes

- `report/screenshots/` holds the evidence (A: CI screenshots, B: ELT outputs, C: Mage runs and the Cloudflare screenshot, D: RabbitMQ logs, Bonus, Final).
- `report/FINAL_ASSIGNMENT_COMPLIANCE_AUDIT.md`: requirement-by-requirement check against the assignment.
- `report/FINAL_REPOSITORY_CLEANUP_AUDIT.md`: repository contents and cleanup review.
- `report/USER_REVIEW_REQUIRED.md`: study guide for the viva.
- `report/answers.md`, `report/checklist.md`: working notes and requirement tracker.
