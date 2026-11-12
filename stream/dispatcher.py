"""Part D dispatcher: publishes a food/ride request every 2 seconds to the topic exchange `rapido-dispatch`.

    python stream/dispatcher.py                       # runs until Ctrl+C
    python stream/dispatcher.py --duration 120        # stops by itself after 2 minutes
    python stream/dispatcher.py --bad-every 0         # no malformed messages

Each request is JSON {"id", "city", "zone", "type", "ts"} and the routing key is "city.zone.type".
D3: every 10th message (--bad-every) is deliberately malformed (the "zone" field is removed from the body;
the routing key still has the zone) so that drivers can demonstrate NACK.
Credentials come from RABBITMQ_URL (.env) and are never printed.
"""
import argparse
import json
import random
import sys
import time
import uuid

import common

CITIES = ["bangalore", "chennai"]
ZONES = {"bangalore": ["koramangala", "indiranagar", "whitefield"],
         "chennai": ["tnagar", "adyar", "velachery"]}
TYPES = ["ride", "food"]


def build_request(number, rng, malformed=False):
    """Return (routing_key, payload) for request number `number`. A malformed request has no `zone` field."""
    city = rng.choice(CITIES)
    zone = rng.choice(ZONES[city])
    kind = rng.choice(TYPES)
    payload = {"id": f"req-{number:04d}-{uuid.uuid4().hex[:6]}", "city": city, "zone": zone,
               "type": kind, "ts": common.utc_iso()}
    key = f"{city}.{zone}.{kind}"
    if malformed:
        del payload["zone"]
    return key, payload


def main(argv=None):
    ap = argparse.ArgumentParser(description="Publish ride/food requests to the rapido-dispatch topic exchange.")
    ap.add_argument("--interval", type=float, default=2.0, help="seconds between requests (default 2)")
    ap.add_argument("--duration", type=float, default=0, help="stop after this many seconds (default: run until Ctrl+C)")
    ap.add_argument("--count", type=int, default=0, help="stop after this many requests (default: unlimited)")
    ap.add_argument("--bad-every", type=int, default=10, help="every Nth message is malformed, 0 = never (default 10)")
    ap.add_argument("--seed", type=int, default=None, help="random seed, for a reproducible sequence")
    args = ap.parse_args(argv)
    rng = random.Random(args.seed)

    try:
        connection = common.connect("dispatcher")
    except (common.ConfigError, common.BrokerError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    channel = None
    sent = bad = dropped = 0
    started = time.monotonic()
    try:
        channel = common.open_publisher_channel(connection)
        common.log(f"DISPATCHER READY exchange={common.EXCHANGE} type=topic interval={args.interval}s "
                   f"bad_every={args.bad_every} duration={args.duration or 'until Ctrl+C'}")
        while True:
            sent += 1
            malformed = bool(args.bad_every) and sent % args.bad_every == 0
            key, payload = build_request(sent, rng, malformed)
            routed = common.publish(channel, key, payload, message_id=payload["id"])
            bad += malformed
            dropped += not routed
            note = " MALFORMED(zone removed)" if malformed else ""
            note += "" if routed else " DROPPED(no queue matches)"
            common.log(f"SENT #{sent:03d} id={payload['id']} key={key}{note}")
            if args.count and sent >= args.count:
                break
            if args.duration and time.monotonic() - started >= args.duration - args.interval / 2:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        common.log("DISPATCHER interrupted (Ctrl+C)")
    except Exception as exc:
        print(f"ERROR: {common.redact(str(exc))[:300]}", file=sys.stderr)
        return 1
    finally:
        common.close_quietly(channel, connection)
        common.log(f"DISPATCHER STOPPED sent={sent} malformed={bad} dropped_unrouted={dropped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
