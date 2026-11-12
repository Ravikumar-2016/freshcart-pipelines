"""Layered connectivity check for the CloudAMQP broker. Prints only OK/FAIL per layer, never the host or credentials.

    python stream/check_connection.py

Layers: settings -> DNS -> TCP 5671 (AMQPS) / 5672 (AMQP) / 443 (HTTPS) -> TLS -> management API login -> AMQP login.
If the AMQP layers fail while HTTPS works, the local network (college/office Wi-Fi, VPN, firewall) is blocking the
AMQP ports: try another network, e.g. a phone hotspot. Exit code 0 only if the AMQP login works.
"""
import socket
import ssl
import sys
from urllib.parse import urlparse

import common
import mgmt


def tcp(host, port, timeout=8):
    try:
        socket.create_connection((host, port), timeout=timeout).close()
        return True, "OPEN"
    except Exception as exc:
        return False, f"unreachable ({type(exc).__name__})"


def main():
    try:
        url = common.get_url()
    except common.ConfigError as exc:
        print(f"1. settings (RABBITMQ_URL)          : FAIL - {exc}")
        return 2
    parts = urlparse(url)
    host = parts.hostname
    amqp_port = parts.port or (5671 if parts.scheme == "amqps" else 5672)
    print(f"1. settings (RABBITMQ_URL)          : OK (scheme {parts.scheme}, host/credentials hidden)")

    try:
        socket.getaddrinfo(host, amqp_port)
        print("2. DNS lookup of the broker host    : OK")
    except Exception as exc:
        print(f"2. DNS lookup of the broker host    : FAIL ({type(exc).__name__})")
        return 1

    results = {}
    for label, port in (("TCP 5671  (AMQPS)", 5671), ("TCP 5672  (AMQP)", 5672), ("TCP 443   (HTTPS, mgmt API)", 443)):
        ok, text = tcp(host, port)
        results[port] = ok
        print(f"3. {label:30s}: {text}")

    if results[443]:
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=8) as sock, ctx.wrap_socket(sock, server_hostname=host) as tls:
                print(f"4. TLS handshake on 443             : OK ({tls.version()})")
        except Exception as exc:
            print(f"4. TLS handshake on 443             : FAIL ({type(exc).__name__})")
        try:
            api = mgmt.Mgmt()
            status, who = api.request("GET", "/whoami")
            if status == 200:
                st2, exchanges = api.request("GET", f"/exchanges/{api.vh()}")
                print(f"5. management API login (HTTPS)     : OK (credentials accepted, vhost reachable: {st2 == 200}, "
                      f"{len(exchanges) if isinstance(exchanges, list) else '?'} exchanges)")
            else:
                print(f"5. management API login (HTTPS)     : FAIL (HTTP {status}: check user/password in RABBITMQ_URL)")
        except mgmt.MgmtError as exc:
            print(f"5. management API login (HTTPS)     : FAIL ({exc})")
    else:
        print("4./5. HTTPS layers                  : skipped (port 443 not reachable)")

    try:
        connection = common.connect("check-connection")
        channel = connection.channel()
        channel.exchange_declare(exchange=common.EXCHANGE, exchange_type="topic", durable=True)
        common.close_quietly(channel, connection)
        print(f"6. AMQP login + declare '{common.EXCHANGE}': OK")
        return 0
    except (common.ConfigError, common.BrokerError) as exc:
        print(f"6. AMQP login (pika)                : FAIL - {exc}")
        if not results[amqp_port] and results[443]:
            print("\nDIAGNOSIS: the instance is alive and the HTTPS API answers, but the AMQP port is not reachable from this "
                  "network.\nThis is a local network restriction, not a code or credential problem. Try a phone hotspot or "
                  "another Wi-Fi, disable any VPN, and re-run this script.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
