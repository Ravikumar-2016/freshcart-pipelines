"""Compare dispatcher/driver log files with the routing model: every SENT message must be RECEIVED+ACKed by exactly
the drivers stream/topic.py predicts, and by nobody else.  python stream/verify_logs.py LOGDIR PREFIX  (e.g. D2)"""
import re, sys
from pathlib import Path
from topic import DRIVERS, recipients

d, prefix = Path(sys.argv[1]), sys.argv[2]
sent = {}
for line in (d / f"{prefix}_dispatcher.log").read_text(encoding="utf-8").splitlines():
    m = re.search(r"SENT #\d+ id=(\S+) key=(\S+)(.*)", line)
    if m:
        sent[m.group(1)] = (m.group(2), "MALFORMED" in m.group(3))
got = {n: {} for n in DRIVERS}
for n in DRIVERS:
    for line in (d / f"{prefix}_driver_{n}.log").read_text(encoding="utf-8").splitlines():
        m = re.search(r"\] (RECEIVED|REJECTED) key=(\S+) id=(\S+).*-> (ACK|NACK)", line)
        if m:
            got[n][m.group(3)] = (m.group(1), m.group(4))
bad = 0; dropped = 0
for mid, (key, malformed) in sent.items():
    exp = set(recipients(key)); act = {n for n in DRIVERS if mid in got[n]}
    dropped += not exp
    if exp != act: bad += 1; print("MISMATCH", mid, key, "expected", sorted(exp), "got", sorted(act))
extra = {n: set(got[n]) - set(sent) for n in DRIVERS}
print(f"messages sent: {len(sent)} (malformed {sum(m for _, m in sent.values())}), expected to be dropped (no driver): {dropped}")
for n in DRIVERS:
    kinds = {}
    for v in got[n].values(): kinds[v] = kinds.get(v, 0) + 1
    print(f"  {n:8s} pattern {DRIVERS[n]:25s} received {len(got[n]):3d}  {kinds}  unexpected ids: {len(extra[n])}")
print("RESULT:", "PASS: every message reached exactly the predicted drivers" if not bad and not any(extra.values()) else f"FAIL ({bad} mismatches)")
sys.exit(1 if bad else 0)
