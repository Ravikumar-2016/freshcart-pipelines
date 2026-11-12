"""Part D driver: listens for requests that match its binding pattern.

    python stream/driver.py NAME PATTERN
    python stream/driver.py Ravi "bangalore.koramangala.*"
    python stream/driver.py Control "bangalore.#" --duration 120

The driver declares its OWN private queue (exclusive to this connection, deleted when the driver stops), binds it
to the topic exchange `rapido-dispatch` with PATTERN, and consumes with manual acknowledgements:
  * a valid message is processed and acknowledged (basic_ack);
  * D3: a message without the `zone` field is rejected with basic_nack(requeue=False), i.e. it is discarded.
In a pattern `*` matches exactly one word and `#` matches zero or more words.
Credentials come from RABBITMQ_URL (.env) and are never printed.
"""
import argparse
import json
import re
import sys
import uuid

import common

PATTERN_RE = re.compile(r"^[A-Za-z0-9_\-*#]+(\.[A-Za-z0-9_\-*#]+)*$")


def handle_delivery(channel, method, body, name, bad_requeue=False, out=common.log):
    """Validate one delivery and acknowledge it. Returns "ACK" or "NACK".

    bad_requeue is False in normal use (malformed messages are discarded). The D3 demonstration passes True to
    show the poison-message loop that requeueing causes."""
    payload, problem = common.validate_message(body)           # required field: zone
    shown = json.dumps(payload, separators=(",", ":")) if payload is not None else repr(body[:80])
    msg_id = payload.get("id", "?") if isinstance(payload, dict) else "?"
    if problem:
        channel.basic_nack(method.delivery_tag, requeue=bad_requeue)
        what = "requeue=True, goes back to the queue" if bad_requeue else "requeue=False, discarded"
        out(f"[{name}] REJECTED key={method.routing_key} id={msg_id} reason={problem} payload={shown} "
            f"redelivered={method.redelivered} -> NACK ({what})")
        return "NACK"
    channel.basic_ack(method.delivery_tag)
    out(f"[{name}] RECEIVED key={method.routing_key} id={msg_id} payload={shown} -> ACK")
    return "ACK"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Consume ride/food requests that match a binding pattern.")
    ap.add_argument("name", help="driver name, e.g. Ravi")
    ap.add_argument("pattern", help='binding pattern, e.g. "bangalore.*.ride" (* = one word, # = zero or more)')
    ap.add_argument("--duration", type=float, default=0, help="stop after this many seconds (default: until Ctrl+C)")
    args = ap.parse_args(argv)
    if not PATTERN_RE.match(args.pattern):
        print("ERROR: the pattern must be dot-separated words made of letters, digits, '-', '_', '*' or '#'.", file=sys.stderr)
        return 2

    try:
        connection = common.connect(f"driver-{args.name}")
    except (common.ConfigError, common.BrokerError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    channel = None
    counts = {"ACK": 0, "NACK": 0}
    try:
        channel = connection.channel()
        common.declare_exchange(channel)
        queue = channel.queue_declare(queue=f"driver.{args.name.lower()}.{uuid.uuid4().hex[:6]}",
                                      exclusive=True, auto_delete=True).method.queue     # private queue
        channel.queue_bind(queue=queue, exchange=common.EXCHANGE, routing_key=args.pattern)
        common.log(f"[{args.name}] READY queue={queue} pattern={args.pattern} exchange={common.EXCHANGE}")

        def handler(ch, method, properties, body):
            counts[handle_delivery(ch, method, body, args.name)] += 1

        common.consume_loop(channel, queue, handler, seconds=args.duration or None)
    except KeyboardInterrupt:
        common.log(f"[{args.name}] interrupted (Ctrl+C)")
    except Exception as exc:
        print(f"ERROR: {common.redact(str(exc))[:300]}", file=sys.stderr)
        return 1
    finally:
        common.close_quietly(channel, connection)
        common.log(f"[{args.name}] STOPPED acked={counts['ACK']} nacked={counts['NACK']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
