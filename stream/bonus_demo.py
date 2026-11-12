"""Bonus demonstration: two one-minute stream runs, idempotency check, safe cleanup, comparison with the baseline.

    python stream/bonus_demo.py            (takes about 2.5 minutes; writes to Snowflake FRESHCART_DB, then cleans up)

Test orders are marked BONUS-TEST-*; run ids end in _bonusN. Cleanup counts the exact markers first, asserts the
expected numbers, and stops WITHOUT deleting anything if they differ. Nothing else is touched.
"""
import os
import sys
import threading
import time

import common
import order_consumer as oc

fc = oc.fc
q1 = lambda sql: fc.query(sql)[0][0]
TABLES = ["bronze.orders_raw", "bronze.customers_raw", "bronze.fx_raw", "bronze.pincode_raw", "silver.orders_checked",
          "silver.orders_clean", "silver.orders_dedup", "silver.orders_enriched", "dim.customers_scd2", "ref.fx_daily",
          "ref.pincode_geo", "quarantine.orders", "gold.fct_orders"]

# FreshCart-style web orders (same shape as MOCK_WEB_ORDERS). Existing customers/pincodes, past dates, valid amounts.
ORDERS = [
    {"order_id": "BONUS-TEST-001", "cust_email": "priya.r@gmail.com", "cust_name": "Bonus One", "order_date": "2026-09-03",
     "amount": "500.00", "currency": "INR", "pincode": "600041", "updated_at": "2026-09-05 10:00:00"},
    {"order_id": "BONUS-TEST-002", "cust_email": "meera@outlook.com", "cust_name": "Bonus Two", "order_date": "2026-09-02",
     "amount": "1,000.00", "currency": "INR", "pincode": "400050", "updated_at": "2026-09-05 10:01:00"},
    {"order_id": "BONUS-TEST-003", "cust_email": "arjun.k@yahoo.in", "cust_name": "Bonus Three", "order_date": "2026-09-02",
     "amount": "250", "currency": "INR", "pincode": "560034", "updated_at": "2026-09-05 10:02:00"},
]
BAD = {"cust_email": "x@y.com", "order_date": "2026-09-01", "note": "malformed: no order_id"}
# expected effect on gold: Priya Gold x2 -> 5*2=10 pts; Meera Platinum x3 -> 10*3=30; Arjun Gold x2 (from 2026-08-15) -> 2*2=4
EXPECT_ADDED = (3, 1750.00, 44)


def snapshot():
    counts = {t: q1(f"SELECT COUNT(*) FROM {t}") for t in TABLES}
    gold = fc.show("SELECT order_id, tier, amount_inr, loyalty_points, row_hash, published_at FROM gold.fct_orders ORDER BY order_id")
    tot = fc.query("SELECT COUNT(*), SUM(amount_inr), SUM(loyalty_points) FROM gold.fct_orders")[0]
    return counts, gold, (int(tot[0]), float(tot[1]), int(tot[2]))


def publisher(delay):
    """Publish the 3 orders, a re-send of order 001 (duplicate) and one malformed message, after `delay` seconds."""
    time.sleep(delay)
    conn = common.connect("bonus-publisher"); ch = common.open_publisher_channel(conn)
    for body in ORDERS + [ORDERS[0], BAD]:
        ok = common.publish(ch, oc.ORDER_KEY, body, message_id=body.get("order_id", "bad"))
        common.log(f"[publisher] sent {body.get('order_id', '(no order_id)')} routed={ok}")
    common.close_quietly(ch, conn)


def one_run(n, seconds):
    print(f"\n================ RUN {n}: one-minute collection ({seconds}s) ================")
    t = threading.Thread(target=publisher, args=(4,)); t.start()
    started = time.monotonic()
    res = oc.process_window(seconds, tag=f"bonus{n}")
    t.join()
    print(f"collection window lasted {time.monotonic() - started:.1f}s; collected={res['collected']} (3 orders + 1 duplicate), "
          f"rejected={res['rejected']} (malformed), acked={res['acked']}")
    print("3. TRANSFORM: bronze -> silver -> gold"); fc.transform(res["run_id"])
    print("4. CHECK"); fc.quality_checks()
    counts, gold, tot = snapshot()
    print(f"GOLD after run {n}: {tot[0]} orders, revenue {tot[1]:.2f}, {tot[2]} loyalty points")
    return res, counts, gold, tot


def main():
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 60
    fc.connect()
    ch_conn = common.connect("bonus-setup"); ch = ch_conn.channel(); common.declare_exchange(ch)
    ch.queue_declare(queue=oc.ORDER_QUEUE, durable=True); ch.queue_bind(queue=oc.ORDER_QUEUE, exchange=common.EXCHANGE, routing_key=oc.ORDER_KEY)
    depth0 = ch.queue_declare(queue=oc.ORDER_QUEUE, passive=True).method.message_count
    common.close_quietly(ch, ch_conn)
    assert depth0 == 0, f"STOP: the order queue already holds {depth0} messages; nothing was published or changed"
    assert q1("SELECT COUNT(*) FROM bronze.orders_raw WHERE raw:order_id::STRING LIKE 'BONUS-TEST-%'") == 0, "STOP: markers already exist"

    base_counts, base_gold, base_tot = snapshot()
    print(f"BASELINE before the bonus: {base_tot[0]} orders, revenue {base_tot[1]:.2f}, {base_tot[2]} points")
    print("baseline counts:", base_counts)

    r1, c1, g1, t1 = one_run(1, seconds)
    r2, c2, g2, t2 = one_run(2, seconds)

    print("\n================ IDEMPOTENCY (run 1 vs run 2) ================")
    added = (t1[0] - base_tot[0], round(t1[1] - base_tot[1], 2), t1[2] - base_tot[2])
    print(f"run 1 added to gold: {added[0]} orders, {added[1]:.2f} revenue, {added[2]} points (expected {EXPECT_ADDED})")
    print(f"bronze.orders_raw: baseline {base_counts['bronze.orders_raw']} -> run 1 {c1['bronze.orders_raw']} -> run 2 {c2['bronze.orders_raw']}  (appends every run, incl. the duplicate)")
    print(f"silver.orders_dedup: {c1['silver.orders_dedup']} -> {c2['silver.orders_dedup']}   gold orders: {t1[0]} -> {t2[0]}   revenue: {t1[1]:.2f} -> {t2[1]:.2f}   points: {t1[2]} -> {t2[2]}")
    same_pub = g1[["ORDER_ID", "ROW_HASH", "PUBLISHED_AT"]].equals(g2[["ORDER_ID", "ROW_HASH", "PUBLISHED_AT"]])
    print("every gold row identical after run 2 (order_id, row_hash, published_at):", same_pub)
    print("duplicate gold order_ids:", q1("SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM gold.fct_orders"))
    ok = added == EXPECT_ADDED and t1 == t2 and same_pub and c1["silver.orders_dedup"] == c2["silver.orders_dedup"]
    print("IDEMPOTENCY RESULT:", "PASS (second run did not double-count)" if ok else "FAIL")

    print("\n================ CLEANUP (only the BONUS-TEST markers) ================")
    runs = [r1["run_id"], r2["run_id"]]
    runlist = ",".join(f"'{r}'" for r in runs)
    found = {
        "bronze rows with BONUS-TEST ids": q1("SELECT COUNT(*) FROM bronze.orders_raw WHERE raw:order_id::STRING LIKE 'BONUS-TEST-%'"),
        "bronze rows in the two bonus runs": q1(f"SELECT COUNT(*) FROM bronze.orders_raw WHERE run_id IN ({runlist})"),
        "bronze rows: ids AND bonus runs": q1(f"SELECT COUNT(*) FROM bronze.orders_raw WHERE raw:order_id::STRING LIKE 'BONUS-TEST-%' AND run_id IN ({runlist})"),
        "bronze OTHER rows (kept)": q1(f"SELECT COUNT(*) FROM bronze.orders_raw WHERE run_id NOT IN ({runlist})"),
        "gold rows with BONUS-TEST ids": q1("SELECT COUNT(*) FROM gold.fct_orders WHERE order_id LIKE 'BONUS-TEST-%'"),
        "gold OTHER rows (kept)": q1("SELECT COUNT(*) FROM gold.fct_orders WHERE order_id NOT LIKE 'BONUS-TEST-%'"),
        "quarantine rows with BONUS-TEST ids": q1("SELECT COUNT(*) FROM quarantine.orders WHERE order_id LIKE 'BONUS-TEST-%'"),
        "staged files in the two run folders": sum(len(fc.query(f"LIST @bronze.landing/orders_web/{r}/")) for r in runs),
    }
    expected = {"bronze rows with BONUS-TEST ids": 8, "bronze rows in the two bonus runs": 8, "bronze rows: ids AND bonus runs": 8,
                "bronze OTHER rows (kept)": base_counts["bronze.orders_raw"], "gold rows with BONUS-TEST ids": 3,
                "gold OTHER rows (kept)": base_tot[0], "quarantine rows with BONUS-TEST ids": 0, "staged files in the two run folders": 2}
    for k in found: print(f"  {k:42s} found {found[k]:>3}  expected {expected[k]:>3}  {'ok' if found[k] == expected[k] else 'MISMATCH'}")
    assert found == expected, "STOP: counts differ from expectations; NOTHING has been deleted"
    nb = fc.query(f"DELETE FROM bronze.orders_raw WHERE raw:order_id::STRING LIKE 'BONUS-TEST-%' AND run_id IN ({runlist})")[0][0]
    ng = fc.query("DELETE FROM gold.fct_orders WHERE order_id LIKE 'BONUS-TEST-%'")[0][0]
    for r in runs: fc.query(f"REMOVE @bronze.landing/orders_web/{r}/")
    for r, p in zip(runs, (r1["path"], r2["path"])):
        assert r in str(p); os.remove(p)
    c = common.connect("bonus-cleanup"); cc = c.channel(); cc.queue_delete(queue=oc.ORDER_QUEUE); common.close_quietly(cc, c)
    print(f"deleted: {nb} bronze rows, {ng} gold rows, 2 staged files, 2 local landing files, the bonus queue")
    print("rebuild silver/gold from the cleaned bronze:"); fc.transform("bonus_cleanup"); fc.quality_checks()

    f_counts, f_gold, f_tot = snapshot()
    same_counts = f_counts == base_counts
    same_gold = base_gold.equals(f_gold)
    print("\n================ FINAL vs BASELINE ================")
    for t in TABLES: print(f"  {t:26s} baseline {base_counts[t]:>4}  final {f_counts[t]:>4}  {'ok' if base_counts[t] == f_counts[t] else 'DIFF'}")
    print(f"  gold totals: baseline {base_tot} final {f_tot}")
    print("  gold rows identical to baseline (incl. row_hash, published_at):", same_gold)
    print("CLEANUP RESULT:", "PASS (state identical to the pre-bonus baseline)" if same_counts and same_gold and f_tot == base_tot else "FAIL")
    fc.conn.close()
    return 0 if ok and same_counts and same_gold else 1


if __name__ == "__main__":
    sys.exit(main())
