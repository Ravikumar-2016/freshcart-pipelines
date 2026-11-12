"""D3 demonstration on the REAL broker: ACK of a valid message, NACK(requeue=False) of a malformed one, a consumer that
'crashes' before ACK, and the poison-message loop with requeue=True.  python stream/d3_demo.py
Uses one private queue; no dead-letter exchange is configured, so a rejected message is simply discarded."""
import sys, uuid
import common
from driver import handle_delivery


def main():
    conn = common.connect("d3-demo"); ch = common.open_publisher_channel(conn)
    run = uuid.uuid4().hex[:6]; key = f"d3.demo.{run}"
    q = ch.queue_declare(queue=f"d3demo.{run}", exclusive=True, auto_delete=True).method.queue
    ch.queue_bind(queue=q, exchange=common.EXCHANGE, routing_key=key)
    depth = lambda c: c.queue_declare(queue=q, passive=True).method.message_count
    valid = {"id": "d3-valid", "city": "bangalore", "zone": "koramangala", "type": "food", "ts": common.utc_iso()}
    bad = {"id": "d3-malformed", "city": "bangalore", "type": "food", "ts": common.utc_iso()}   # no zone
    pub = lambda body: common.publish(ch, key, body, message_id=body["id"])
    out = common.log
    print("=== 1. valid message -> basic_ack ===")
    pub(valid); print("queue depth after publish:", depth(ch))
    m, _, body = ch.basic_get(q, auto_ack=False); r1 = handle_delivery(ch, m, body, "D3")
    print("queue depth after handling:", depth(ch), "(0 = acknowledged and removed)")
    print("\n=== 2. malformed message (no zone) -> basic_nack(requeue=False) ===")
    pub(bad); print("queue depth after publish:", depth(ch))
    m, _, body = ch.basic_get(q, auto_ack=False); r2 = handle_delivery(ch, m, body, "D3")
    print("queue depth after handling:", depth(ch), "(0 = discarded; no dead-letter exchange is configured, so it is gone)")
    print("\n=== 3. consumer crashes before ACK ===")
    pub(valid); m, _, body = ch.basic_get(q, auto_ack=False)
    print(f"consumer received id=d3-valid redelivered={m.redelivered} and then 'crashes' (channel closed, no ack sent)")
    ch.close(); ch = conn.channel()
    print("queue depth after the crash:", depth(ch), "(1 = the broker put the unacknowledged message back)")
    m, _, body = ch.basic_get(q, auto_ack=False)
    print(f"next consumer gets it again: redelivered={m.redelivered}"); ch.basic_ack(m.delivery_tag)
    print("\n=== 4. poison message with requeue=True (what NOT to do) ===")
    ch.confirm_delivery(); pub(bad)
    for i in range(1, 5):
        m, _, body = ch.basic_get(q, auto_ack=False)
        print(f"attempt {i}: ", end=""); handle_delivery(ch, m, body, "D3", bad_requeue=True)
    print("queue depth after 4 attempts:", depth(ch), "(still 1: the message never leaves, every consumer sees it again forever)")
    m, _, body = ch.basic_get(q, auto_ack=False); ch.basic_nack(m.delivery_tag, requeue=False)
    print("cleaned up with requeue=False; queue depth:", depth(ch))
    ok = r1 == "ACK" and r2 == "NACK"
    print("\nRESULT:", "PASS (valid=ACK, malformed=NACK, crash redelivered, requeue loop shown)" if ok else "FAIL")
    common.close_quietly(ch, conn); return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
