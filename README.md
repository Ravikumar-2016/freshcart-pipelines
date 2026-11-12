# freshcart-pipelines

Data Engineering assignment **"From Git to Gold"**: version control and CI, a
Snowflake ELT pipeline, a Mage ML pipeline and a RabbitMQ event stream.

Repository: https://github.com/Ravikumar-2016/freshcart-pipelines

## Layout

| Path | Contents | Assignment part |
|---|---|---|
| `elt/` | FreshCart ELT notebook (Snowflake bronze → silver → gold) | B |
| `iris_project/` | Mage Iris classifier project | C |
| `stream/` | `dispatcher.py` and `driver.py` (RabbitMQ topic exchange) | D |
| `tests/` | pytest tests run by CI | A3 |
| `.github/workflows/ci.yml` | GitHub Actions workflow (Python 3.12, pytest) | A3 |
| `report/` | Running answers, requirement checklist, screenshots | E |

## Setup (Windows, PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Python 3.12 is required. Copy `.env.example` to `.env` and fill in your own
values. `.env` is git-ignored and must never be committed.

## Part D: RabbitMQ stream (CloudAMQP)
```powershell
pip install -r requirements-stream.txt          # pika
# put your AMQP URL in .env as RABBITMQ_URL (never commit it); then:
python stream\check_connection.py               # layered connectivity check
python stream/verify_routing.py                 # D1: six routing keys against the live broker
python stream\driver.py Ravi "bangalore.koramangala.*"   # one terminal per driver
python stream\driver.py Control "bangalore.#"
python stream\dispatcher.py --duration 120      # every 2 s; every 10th message malformed (--bad-every 0 to disable)
python stream\d3_demo.py                        # D3: ACK / NACK / crash / requeue demo
```

## Bonus: stream orders into the lakehouse
```powershell
python stream/order_consumer.py --seconds 60   # one batch: RabbitMQ -> landing -> bronze -> silver -> gold
python stream/bonus_demo.py 60                 # two runs + idempotency check + safe cleanup (needs Snowflake and RabbitMQ in .env)
```

## Status

Tracked in `report/checklist.md`.
