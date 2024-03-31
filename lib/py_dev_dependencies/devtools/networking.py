"""The networking module contains code related to networking stuff,
like checking for open ports, etc.
"""

__all__ = ["is_port_used", "find_next_unused_port"]

import socket

MAX_PORT_RANGE = 65535
_REQUESTED_PORTS = []


def _bind_port(port: int) -> None:
    """Bind a specified port."""

    location = ("127.0.0.1", port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(location)


def is_port_used(port: int) -> bool:
    """Checks if the given port is currently in use or not."""

    try:
        _bind_port(port)
    except PermissionError:
        return True  # reserved ports
    except OSError as os_ex:
        return os_ex.errno in (
            48,  # mac os x error code
            98,  # linux (circleci) error code
            10048,  # windows
        )
    return False


def find_next_unused_port(start_port: int, max_checks: int = 30) -> int | None:
    """
    Finds the next unused port starting from the specified port.

    :param start_port: The port number to start searching from.
    :param max_checks: The maximum number of ports to check for availability.
        Default is 30.
    :return: The next unused port number if found, otherwise None.
    """

    for port in range(start_port, min(start_port + max_checks, MAX_PORT_RANGE)):
        if not is_port_used(port) and port not in _REQUESTED_PORTS:
            _REQUESTED_PORTS.append(port)
            return port
    return None
