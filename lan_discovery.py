import socket
import json
import threading

from config import DISCOVERY_PORT, TCP_PORT


DISCOVERY_MESSAGE = "FILEPULSE_DISCOVER"


def get_local_ip():

    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.connect(("8.8.8.8", 80))

        ip = sock.getsockname()[0]

        sock.close()

        return ip

    except Exception:
        return "127.0.0.1"


def get_device_name():

    return socket.gethostname()


def start_discovery_listener():

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    sock.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    sock.bind(
        ("", DISCOVERY_PORT)
    )

    print(
        f"LAN discovery listening on UDP "
        f"port {DISCOVERY_PORT}"
    )

    while True:

        try:

            data, address = sock.recvfrom(4096)

            message = data.decode(
                "utf-8",
                errors="ignore"
            )

            if message == DISCOVERY_MESSAGE:

                local_ip = get_local_ip()

                response = {
                    "name": get_device_name(),
                    "ip": local_ip,
                    "port": TCP_PORT
                }

                response_data = json.dumps(
                    response
                ).encode("utf-8")

                sock.sendto(
                    response_data,
                    address
                )

        except Exception as error:

            print(
                "Discovery error:",
                error
            )


def discover_devices():

    devices = []

    local_ip = get_local_ip()

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    sock.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_BROADCAST,
        1
    )

    sock.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    sock.settimeout(0.5)

    try:

        sock.sendto(
            DISCOVERY_MESSAGE.encode("utf-8"),
            ("255.255.255.255", DISCOVERY_PORT)
        )

        while True:

            try:

                data, address = sock.recvfrom(
                    4096
                )

                response = json.loads(
                    data.decode("utf-8")
                )

                device_ip = response.get(
                    "ip"
                )

                device_name = response.get(
                    "name"
                )

                device_port = response.get(
                    "port",
                    TCP_PORT
                )

                # Don't show this computer itself
                if device_ip == local_ip:
                    continue

                device = {
                    "name": device_name,
                    "ip": device_ip,
                    "port": device_port
                }

                # Avoid duplicates
                if not any(
                    d["ip"] == device_ip
                    for d in devices
                ):

                    devices.append(device)

            except socket.timeout:
                break

            except json.JSONDecodeError:
                continue

    except Exception as error:

        print(
            "Discovery failed:",
            error
        )

    finally:

        sock.close()

    return devices


def start_discovery_service():

    thread = threading.Thread(
        target=start_discovery_listener,
        daemon=True
    )

    thread.start()