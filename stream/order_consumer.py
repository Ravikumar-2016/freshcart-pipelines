"""Bonus: stream FreshCart-style order messages from RabbitMQ into the lakehouse (bronze -> silver -> gold).

    python stream/order_consumer.py --seconds 60

Flow: RabbitMQ queue -> collect for N seconds -> write_landing() raw .json.gz -> load_file() PUT+COPY into
bronze.orders_raw -> transform() (the existing SQL: silver, dim, ref, gold MERGE) -> quality_checks().
Messages use the WEB order shape (source 'web'), because SQL_10 reads source in ('web','mobile').

Acknowledgement policy: a message is ACKed only AFTER its landing file has been written AND loaded into bronze
(durable hand-off). If writing/loading fails, every collected message is NACKed with requeue=True so nothing is lost.
An invalid message (not JSON, or no order_id / cust_email / order_date) is NACKed with requeue=False at once.
Reuses stream/common.py (connection from RABBITMQ_URL, never printed) and elt/freshcart.py.
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import common

sys.path.insert(0, str(common.ROOT / "elt"))
import freshcart as fc  # noqa: E402  (needs the Snowflake login in .env)

ORDER_KEY = "freshcart.order.web"           # does not match any D1 driver pattern
ORDER_QUEUE = "freshcart.orders.bonus"      # durable: messages survive until they are loaded and acked
REQUIRED = ("order_id", "cust_email", "order_date")


def collect(channel, seconds, out=common.log):
    """Consume for `seconds`. Returns (records, delivery_tags); invalid messages are rejected right away."""
    channel.basic_qos(prefetch_count=200)
    records, tags, rejected = [], [], 0
    deadline = time.monotonic() + seconds
    for method, _props, body in channel.consume(ORDER_QUEUE, auto_ack=False, inactivity_timeout=1.0):
        if method is not None:
            payload, problem = common.validate_message(body, required=REQUIRED)
            if problem:
                channel.basic_nack(method.delivery_tag, requeue=False)
                rejected += 1
                out(f"[orders] REJECTED {problem} -> NACK (requeue=False, discarded)")
            else:
                records.append(payload)
                tags.append(method.delivery_tag)
                out(f"[orders] COLLECTED order_id={payload['order_id']} ({len(records)} so far, not yet acked)")
        if time.monotonic() >= deadline:
            break
    channel.cancel()
    return records, tags, rejected


def process_window(seconds=60, tag="bonus"):
    """One full batch: collect -> landing -> bronze -> transform -> checks. Returns a result dict."""
    conn = common.connect("freshcart-order-consumer")
    ch = conn.channel()
    common.declare_exchange(ch)
    ch.queue_declare(queue=ORDER_QUEUE, durable=True)
    ch.queue_bind(queue=ORDER_QUEUE, exchange=common.EXCHANGE, routing_key=ORDER_KEY)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + "_" + tag
    result = {"run_id": run_id, "collected": 0, "rejected": 0, "acked": 0, "path": None}
    try:
        common.log(f"[orders] collecting from queue {ORDER_QUEUE} (key {ORDER_KEY}) for {seconds}s, run_id={run_id}")
        records, tags, result["rejected"] = collect(ch, seconds)
        result["collected"] = len(records)
        if not records:
            common.log("[orders] nothing collected; nothing to load")
            return result
        try:
            path = fc.write_landing("web", records, run_id)                            # existing function
            fc.load_file(path, "bronze.orders_raw", f"orders_web/{run_id}")            # existing function
        except Exception:
            for t in tags:
                ch.basic_nack(t, requeue=True)                                         # hand-off failed: keep messages
            raise
        for t in tags:                                                                 # durable hand-off done: ACK
            ch.basic_ack(t)
        result["acked"], result["path"] = len(tags), path
        common.log(f"[orders] landing file written and loaded into bronze; ACKed {len(tags)} messages")
    finally:
        common.close_quietly(ch, conn)
    return result


def main():
    ap = argparse.ArgumentParser(description="Stream FreshCart orders from RabbitMQ into Snowflake gold.")
    ap.add_argument("--seconds", type=float, default=60, help="collection window (default 60)")
    args = ap.parse_args()
    try:
        fc.connect()
        res = process_window(args.seconds)
        if res["collected"]:
            print("3. TRANSFORM: bronze -> silver -> gold")
            fc.transform(res["run_id"])
            print("4. CHECK")
            fc.quality_checks()
        print(res)
        print("GOLD:", fc.query("SELECT COUNT(*), SUM(amount_inr), SUM(loyalty_points) FROM gold.fct_orders")[0])
    except (common.ConfigError, common.BrokerError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        if fc.conn is not None:
            fc.conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
