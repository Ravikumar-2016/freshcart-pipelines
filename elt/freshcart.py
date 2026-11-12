"""FreshCart ELT: reusable code for the notebook `freshcart_elt.ipynb` (Part B).

Extract -> Load -> Transform -> Check, against Snowflake database FRESHCART_DB.
The logic is the course reference notebook's (`freshcart_elt_simple_(1).ipynb`); what is different:
  * the SQL lives in elt/sql/*.sql instead of notebook strings,
  * the login comes from environment variables / the git-ignored .env (never hard-coded),
  * the landing folder is elt/landing/ (git-ignored).
"""
import gzip
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

import mock_data
from mock_data import (MOCK_CRM_TIER_EVENTS, MOCK_FX_RESPONSES, MOCK_MOBILE_ORDERS,  # noqa: F401
                       MOCK_WEB_ORDERS, mock_pincode_response)

ELT_DIR = Path(__file__).resolve().parent
SQL_DIR = ELT_DIR / "sql"
LANDING_DIR = ELT_DIR / "landing"          # raw files written by write_landing (git-ignored)

conn = None                                 # one connection, used by every helper below


# ---------------------------------------------------------------- the SQL (kept in elt/sql/)
def load_sql(filename):
    """Read one SQL script from elt/sql/."""
    return (SQL_DIR / filename).read_text(encoding="utf-8")


SQL_00_SETUP = load_sql("00_setup.sql")
SQL_10_ORDERS_CLEAN = load_sql("10_orders_clean.sql")
SQL_20_ORDERS_DEDUP = load_sql("20_orders_dedup.sql")
SQL_30_CUSTOMERS_SCD2 = load_sql("30_customers_scd2.sql")
SQL_31_FX_DAILY = load_sql("31_fx_daily.sql")
SQL_32_PINCODE_GEO = load_sql("32_pincode_geo.sql")
SQL_40_GOLD = load_sql("40_gold.sql")


# ---------------------------------------------------------------- Snowflake helpers
def connect():
    """Open the Snowflake connection from environment variables (.env in the project root)."""
    global conn
    load_dotenv(ELT_DIR.parent / ".env")
    kwargs = {
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "password": os.environ["SNOWFLAKE_PASSWORD"],
        "login_timeout": 30,
    }
    for env_name, arg in (("SNOWFLAKE_ROLE", "role"), ("SNOWFLAKE_WAREHOUSE", "warehouse"),
                          ("SNOWFLAKE_DATABASE", "database")):
        if os.getenv(env_name):
            kwargs[arg] = os.environ[env_name]
    conn = snowflake.connector.connect(**kwargs)
    role, warehouse, database = conn.cursor().execute(
        "SELECT CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()").fetchone()
    print(f"Connected: role={role} warehouse={warehouse} database={database}")
    return conn


def run_sql(sql_text):
    """Run a SQL script that contains several statements."""
    conn.execute_string(sql_text, remove_comments=True)


def query(sql):
    """Run one query and return its rows."""
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def show(sql):
    """Run one query and return the result as a table."""
    with conn.cursor() as cur:
        cur.execute(sql)
        return pd.DataFrame(cur.fetchall(), columns=[c[0] for c in cur.description])


# ---------------------------------------------------------------- 1. EXTRACT
def write_landing(source, records, run_id):
    """Save source records in a compressed JSON Lines file and return its path.
    Nothing is cleaned; each record is wrapped in a small envelope."""
    folder = LANDING_DIR / source
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{source}__{run_id}.json.gz"
    now = datetime.now(timezone.utc).isoformat()
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for rec in records:
            envelope = {"source": source, "run_id": run_id, "extracted_at": now, "data": rec}
            f.write(json.dumps(envelope, ensure_ascii=False) + "\n")
    print(f"   {source}: {len(records)} records -> {path.relative_to(ELT_DIR.parent)}")
    return path


# ---------------------------------------------------------------- 2. LOAD
def load_file(local_path, table, stage_dir):
    """PUT one raw file into the Snowflake stage, then COPY it into a bronze table."""
    uri = "file://" + Path(local_path).resolve().as_posix()
    query(f"PUT '{uri}' @bronze.landing/{stage_dir}/ AUTO_COMPRESS=FALSE OVERWRITE=FALSE")
    rows = query(f"""
        COPY INTO {table} (source, raw, run_id, extracted_at, src_file, src_row)
        FROM (
          SELECT $1:source::STRING, $1:data, $1:run_id::STRING,
                 $1:extracted_at::TIMESTAMP_TZ, METADATA$FILENAME, METADATA$FILE_ROW_NUMBER
          FROM @bronze.landing/{stage_dir}/
        )
        FILE_FORMAT = (FORMAT_NAME = 'bronze.ff_ndjson')
        ON_ERROR = 'ABORT_STATEMENT'
    """)
    loaded = sum(int(r[3]) for r in rows if len(r) > 3)
    print(f"   {loaded} rows -> {table}")
    return loaded


# ---------------------------------------------------------------- 4. CHECK
def quality_checks():
    """Each of these numbers should be 0."""
    checks = {
        "rows gained or lost while enriching":
            "SELECT (SELECT COUNT(*) FROM silver.orders_enriched) - (SELECT COUNT(*) FROM silver.orders_dedup)",
        "duplicate orders in gold":
            "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM gold.fct_orders",
        "orders with no customer match":
            "SELECT COUNT_IF(cust_id IS NULL) FROM silver.orders_enriched",
        "orders with an amount but no FX rate":
            "SELECT COUNT_IF(amount IS NOT NULL AND fx_rate IS NULL) FROM silver.orders_enriched",
        "orders with no city":
            "SELECT COUNT_IF(city IS NULL) FROM silver.orders_enriched",
        # B5: the sixth check. An order cannot have happened in the future.
        "orders dated in the future":
            "SELECT COUNT_IF(order_date > CURRENT_DATE()) FROM silver.orders_dedup",
    }
    for name, sql in checks.items():
        value = query(sql)[0][0]
        print(f"   {name:38s} {value}   {'OK' if value == 0 else 'PROBLEM'}")
    rejected = query("SELECT COUNT_IF(ARRAY_SIZE(reasons) > 0) / NULLIF(COUNT(*), 0) FROM silver.orders_checked")[0][0]
    print(f"   {'share of rows rejected':38s} {float(rejected or 0):.0%}")


# ---------------------------------------------------------------- 3. TRANSFORM (everything inside Snowflake)
def transform(run_id):
    """Rebuild silver, dim, ref and gold from what is already in bronze (no extract, no load).
    This is stage 3 of run_pipeline(); B5 also calls it on its own to rebuild after cleaning up test data."""
    query(f"SET run_id = '{run_id}'")          # SQL_10 stamps rejected rows with $run_id
    run_sql(SQL_10_ORDERS_CLEAN)
    run_sql(SQL_20_ORDERS_DEDUP)

    # Pincodes: look up only the ones seen in the orders that we don't know yet
    pins = [row[0] for row in query("""
        SELECT DISTINCT o.pincode FROM silver.orders_dedup o
        WHERE NOT EXISTS (SELECT 1 FROM ref.pincode_geo g WHERE g.pincode = o.pincode)""")]
    print("   new pincodes to look up:", pins)
    if pins:
        lookups = [{"pincode": pin, "response": mock_pincode_response(pin)} for pin in pins]
        pin_file = write_landing("pincode", lookups, run_id)
        load_file(pin_file, "bronze.pincode_raw", f"pincode/{run_id}")

    run_sql(SQL_30_CUSTOMERS_SCD2)
    run_sql(SQL_31_FX_DAILY)
    run_sql(SQL_32_PINCODE_GEO)
    run_sql(SQL_40_GOLD)


# ---------------------------------------------------------------- the whole pipeline
def run_pipeline():
    """Extract -> load -> transform -> check, in order. Returns (run_id, orders, revenue, points)."""
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")      # a unique name for this run
    print("run_id:", run_id)

    print("1. EXTRACT: sample data -> raw files")
    web_file = write_landing("web", MOCK_WEB_ORDERS, run_id)
    mobile_file = write_landing("mobile", MOCK_MOBILE_ORDERS, run_id)
    crm_file = write_landing("crm", MOCK_CRM_TIER_EVENTS, run_id)
    fx_file = write_landing("fx", MOCK_FX_RESPONSES, run_id)

    print("2. LOAD: raw files -> bronze tables")
    load_file(web_file, "bronze.orders_raw", f"orders_web/{run_id}")
    load_file(mobile_file, "bronze.orders_raw", f"orders_mobile/{run_id}")
    load_file(crm_file, "bronze.customers_raw", f"crm/{run_id}")
    load_file(fx_file, "bronze.fx_raw", f"fx/{run_id}")

    print("3. TRANSFORM: bronze -> silver -> gold")
    transform(run_id)

    print("4. CHECK")
    quality_checks()
    orders, revenue, points = query("SELECT COUNT(*), SUM(amount_inr), SUM(loyalty_points) FROM gold.fct_orders")[0]
    print(f"GOLD: {orders} orders, revenue ₹{revenue}, {points} loyalty points")
    return run_id, orders, revenue, points
