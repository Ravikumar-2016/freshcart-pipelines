"""Minimal client for the RabbitMQ management HTTP API (HTTPS port 443 on CloudAMQP).

Used for (1) checking that the credentials and vhost in RABBITMQ_URL work, (2) queue/binding snapshots for the
evidence files, and (3) a fallback routing check when the AMQP ports are blocked by the local network.
It uses only the standard library. The login comes from RABBITMQ_URL and is never printed.
"""
import base64
import json
import ssl
import urllib.error
import urllib.request
from urllib.parse import quote, unquote, urlparse

import common


class MgmtError(RuntimeError):
    pass


class Mgmt:
    def __init__(self, timeout=20):
        parts = urlparse(common.get_url())
        self.host = parts.hostname
        self.vhost = unquote(parts.path[1:]) or "/"
        self.timeout = timeout
        token = base64.b64encode(f"{unquote(parts.username or '')}:{unquote(parts.password or '')}".encode()).decode()
        self._auth = f"Basic {token}"
        self._ctx = ssl.create_default_context()

    def vh(self):
        """The vhost, URL-encoded for use inside an API path."""
        return quote(self.vhost, safe="")

    def request(self, method, path, body=None):
        """Call /api<path>. Returns (status, parsed JSON or None). Raises MgmtError if the host is unreachable."""
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(f"https://{self.host}/api{path}", data=data, method=method)
        req.add_header("Authorization", self._auth)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self._ctx) as resp:
                raw = resp.read()
                return resp.status, (json.loads(raw) if raw else None)
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                return exc.code, json.loads(raw) if raw else None
            except ValueError:
                return exc.code, None
        except Exception as exc:
            raise MgmtError(f"management API unreachable ({type(exc).__name__}: {common.redact(str(exc))[:150]})") from None
