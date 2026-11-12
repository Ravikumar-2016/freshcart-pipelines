"""Connection check for Snowflake. Reads the login from environment variables / .env.

Run from the project root:
    .\\.venv\\Scripts\\python.exe elt\\test_connection.py

Prints only the warehouse, database and role. It never prints the password.
Exit codes: 0 = connected, 2 = settings missing, 1 = connection or query failed.
"""
import os
import sys
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

REQUIRED = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
OPTIONAL = {  # env var -> connector argument
    "SNOWFLAKE_ROLE": "role",
    "SNOWFLAKE_WAREHOUSE": "warehouse",
    "SNOWFLAKE_DATABASE": "database",
    "SNOWFLAKE_SCHEMA": "schema",
}


def main() -> int:
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")  # project-root .env

    missing = [k for k in REQUIRED if not os.getenv(k)]
    placeholders = [k for k in REQUIRED if os.getenv(k, "").startswith("<")]
    if missing or placeholders:
        for k in missing:
            print(f"Missing setting: {k} (add it to .env, see .env.example)")
        for k in placeholders:
            print(f"Setting {k} still has the placeholder from .env.example; put your real value")
        return 2

    kwargs = {
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "password": os.environ["SNOWFLAKE_PASSWORD"],
        "login_timeout": 30,
        "network_timeout": 60,
    }
    for env_name, arg in OPTIONAL.items():
        if os.getenv(env_name):
            kwargs[arg] = os.environ[env_name]

    conn = None
    try:
        conn = snowflake.connector.connect(**kwargs)
        with conn.cursor() as cur:
            cur.execute("SELECT CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_ROLE()")
            warehouse, database, role = cur.fetchone()
        print("Connected to Snowflake.")
        print(f"  warehouse: {warehouse}")
        print(f"  database : {database}")
        print(f"  role     : {role}")
        return 0
    except Exception as exc:  # report the problem without echoing any setting values
        msg = str(exc).replace(kwargs["password"], "***")
        print(f"Connection failed: {type(exc).__name__}: {msg[:400]}")
        low = msg.lower()
        if "incorrect username or password" in low:
            print("-> Check SNOWFLAKE_USER and SNOWFLAKE_PASSWORD in .env.")
        elif "mfa" in low or "multi-factor" in low or "authenticator" in low:
            print("-> MFA is required. Use a programmatic access token as SNOWFLAKE_PASSWORD.")
        elif "404" in low or "could not connect" in low or "certificate" in low:
            print("-> SNOWFLAKE_ACCOUNT is probably wrong. Use <orgname>-<accountname>, no https://.")
        return 1
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    sys.exit(main())
