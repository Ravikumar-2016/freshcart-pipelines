"""Shared RabbitMQ helpers for the Part D stream scripts.

Designed to be reused later by a FreshCart consumer (bonus): connection handling, exchange declaration,
publishing with broker confirms, message validation (`required=` fields) and a time-boxed consume loop.

Credentials: the broker URL is read from RABBITMQ_URL (environment or the git-ignored .env in the project
root). It is never printed or logged; error messages are passed through `redact()`.
"""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

import pika
from dotenv import load_dotenv

EXCHANGE = "rapido-dispatch"
ROOT = Path(__file__).resolve().parent.parent


class ConfigError(RuntimeError):
    """RABBITMQ_URL is missing or malformed."""


class BrokerError(RuntimeError):
    """The broker could not be reached or refused the login."""


# ---------------------------------------------------------------- logging
def log(message):
    """Print a line with a wall-clock timestamp (flushed, so redirected logs are live)."""
    print(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} {message}", flush=True)


def utc_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- configuration
def get_url():
    """Return RABBITMQ_URL after basic validation. Raises ConfigError with a helpful, secret-free message."""
    load_dotenv(ROOT / ".env")
    url = os.getenv("RABBITMQ_URL", "").strip()
    if not url:
        raise ConfigError("RABBITMQ_URL is not set. Copy .env.example to .env and put your CloudAMQP AMQP URL "
                          "(Instance details -> AMQP URL) in it.")
    if "<" in url or ">" in url:
        raise ConfigError("RABBITMQ_URL still contains the placeholder from .env.example; put your real URL in .env.")
    if not url.startswith(("amqp://", "amqps://")):
        raise ConfigError("RABBITMQ_URL must start with amqp:// or amqps://")
    parts = urlparse(url)
    if not parts.hostname:
        raise ConfigError("RABBITMQ_URL has no host name (expected amqps://user:password@host/vhost).")
    return url


def redact(text):
    """Replace every sensitive part of the broker URL (password, user, host, vhost) in `text` by ***."""
    parts = urlparse(os.getenv("RABBITMQ_URL", ""))
    secrets = set()
    for value in (parts.password, parts.username, parts.hostname, parts.path.strip("/")):
        if value:
            secrets.update({value, unquote(value)})
    for secret in sorted(secrets, key=len, reverse=True):
        text = text.replace(secret, "***")
    return text


# ---------------------------------------------------------------- connection and channels
def connect(client_name="freshcart-stream"):
    """Open a BlockingConnection to the broker in RABBITMQ_URL. `client_name` shows up in the management UI."""
    url = get_url()
    try:
        params = pika.URLParameters(url)
    except Exception as exc:                                        # malformed URL
        raise ConfigError("RABBITMQ_URL could not be parsed: " + redact(str(exc))) from None
    params.heartbeat = 30
    params.socket_timeout = 10
    params.blocked_connection_timeout = 30
    params.connection_attempts = 2
    params.retry_delay = 2
    params.client_properties = {"connection_name": client_name}
    try:
        return pika.BlockingConnection(params)
    except (pika.exceptions.ProbableAuthenticationError, pika.exceptions.ProbableAccessDeniedError):
        raise BrokerError("the broker refused the login: check the user, password and vhost in RABBITMQ_URL.") from None
    except Exception as exc:
        raise BrokerError(f"could not connect to the broker ({type(exc).__name__}: {redact(str(exc))[:200]})") from None


def declare_exchange(channel):
    """Declare the durable topic exchange `rapido-dispatch` (idempotent)."""
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)


def open_publisher_channel(connection):
    """A channel with the exchange declared and publisher confirms switched on."""
    channel = connection.channel()
    declare_exchange(channel)
    channel.confirm_delivery()
    return channel


def publish(channel, routing_key, body, message_id=None):
    """Publish `body` (bytes or a JSON-able object) as a persistent message with the mandatory flag.

    Returns True if the broker routed it to at least one queue, False if no queue matched (it was dropped).
    Needs a channel from open_publisher_channel()."""
    if not isinstance(body, (bytes, bytearray)):
        body = json.dumps(body, separators=(",", ":")).encode("utf-8")
    props = pika.BasicProperties(content_type="application/json", delivery_mode=2,
                                 message_id=message_id, timestamp=int(time.time()))
    try:
        channel.basic_publish(exchange=EXCHANGE, routing_key=routing_key, body=body, properties=props, mandatory=True)
        return True
    except pika.exceptions.UnroutableError:
        return False


def close_quietly(channel=None, connection=None):
    """Close channel and connection, ignoring errors from an already-closed one."""
    for thing in (channel, connection):
        try:
            if thing is not None and thing.is_open:
                thing.close()
        except Exception:
            pass


# ---------------------------------------------------------------- message validation and consuming
def validate_message(body, required=("zone",)):
    """Check a message body. Returns (payload, problem): problem is None when the message is fine.

    Part D: a message without `zone` is malformed. A later FreshCart consumer can pass its own required fields."""
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return None, "body is not valid JSON"
    if not isinstance(payload, dict):
        return None, "body is not a JSON object"
    missing = [field for field in required if payload.get(field) in (None, "")]
    if missing:
        return payload, "missing field " + ", ".join(repr(field) for field in missing)
    return payload, None


def consume_loop(channel, queue, handler, seconds=None, stop_after=None):
    """Consume `queue` with manual acknowledgements until `seconds` have passed (or `stop_after` messages).

    handler(channel, method, properties, body) must ack or nack the message itself. Returns the number handled."""
    channel.basic_qos(prefetch_count=1)
    deadline = time.monotonic() + seconds if seconds else None
    handled = 0
    try:
        for method, properties, body in channel.consume(queue, auto_ack=False, inactivity_timeout=1.0):
            if method is not None:
                handler(channel, method, properties, body)
                handled += 1
                if stop_after and handled >= stop_after:
                    break
            if deadline is not None and time.monotonic() >= deadline:
                break
    finally:
        try:
            channel.cancel()                         # un-acked deliveries (if any) go back to the queue
        except Exception:
            pass
    return handled
