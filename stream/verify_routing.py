"""D1 verification against the REAL broker.

    python stream/verify_routing.py

Creates one private (exclusive) queue per driver on the exchange `rapido-dispatch`, binds each with its pattern,
publishes the six D1 routing keys, then reads every queue back to see which messages the BROKER delivered.
The actual recipients are compared with (a) the paper predictions in stream/topic.py and (b) an independent
pure-Python implementation of the topic rules. Exit code 0 only if all three agree for all six keys.
Credentials come from RABBITMQ_URL (.env) and are never printed.
"""
import sys
import uuid

import common
from topic import CASES, DRIVERS, recipients


def main():
    try:
        connection = common.connect("verify-routing")
    except (common.ConfigError, common.BrokerError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    channel = None
    try:
        channel = common.open_publisher_channel(connection)
        run = uuid.uuid4().hex[:6]
        queues = {}
        print(f"D1 routing verification on exchange '{common.EXCHANGE}' (type topic), run {run}\n")
        print("Private queues and bindings created on the broker:")
        for name, pattern in DRIVERS.items():
            queue = channel.queue_declare(queue=f"d1verify.{name.lower()}.{run}", exclusive=True,
                                          auto_delete=True).method.queue
            channel.queue_bind(queue=queue, exchange=common.EXCHANGE, routing_key=pattern)
            queues[name] = queue
            print(f"  {name:8s} queue={queue:24s} binding={pattern}")

        print("\nPublishing the six routing keys (mandatory flag: the broker tells us if no queue matched):")
        routed = {}
        for number, (key, _) in enumerate(CASES, start=1):
            routed[key] = common.publish(channel, key, {"case": number, "key": key, "run": run}, message_id=f"d1-{run}-{number}")
            print(f"  case {number}: key={key:30s} routed_to_at_least_one_queue={routed[key]}")

        # read every queue back: which messages did the broker really put there?
        received = {key: [] for key, _ in CASES}
        for name, queue in queues.items():
            while True:
                method, properties, body = channel.basic_get(queue, auto_ack=True)
                if method is None:
                    break
                received[method.routing_key].append(name)

        print("\nResult (actual = read back from the broker's queues):")
        header = f"  {'#':2s} {'routing key':30s} {'actual (broker)':28s} {'predicted (paper)':28s} {'reference model':28s} result"
        print(header)
        all_ok = True
        for number, (key, predicted) in enumerate(CASES, start=1):
            actual = [n for n in DRIVERS if n in received[key]]          # table order
            model = recipients(key)
            ok = actual == predicted == model and routed[key] == bool(predicted)
            all_ok &= ok
            show = lambda names: ", ".join(names) if names else "dropped"
            print(f"  {number:<2d} {key:30s} {show(actual):28s} {show(predicted):28s} {show(model):28s} {'PASS' if ok else 'FAIL'}")
        print(f"\n{'ALL 6 ROUTING CASES PASS' if all_ok else 'SOME ROUTING CASES FAILED'}")
        return 0 if all_ok else 1
    except Exception as exc:
        print(f"ERROR: {common.redact(str(exc))[:300]}", file=sys.stderr)
        return 1
    finally:
        common.close_quietly(channel, connection)       # exclusive queues disappear with the connection


if __name__ == "__main__":
    sys.exit(main())
