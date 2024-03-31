import socket
import warnings
from contextlib import contextmanager

import pytest

from .networking import MAX_PORT_RANGE, find_next_unused_port, is_port_used


@contextmanager
def reserve_ports(start: int, num: int = 1) -> list[tuple[int, socket.socket]]:
    """Reserves a number of ports and returns the port numbers and the sockets.

    :param start: The port number to start reserving ports from.
    :param num: The number of ports to reserve. Default is 1.
    :return: A list of tuples with the port number and the corresponding socket
        holding that port.
    """

    if start + num > MAX_PORT_RANGE:
        raise ValueError("Cannot reserve more ports than available.")

    ports_and_sockets = []
    for port in range(start, start + num):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            soc.bind(("127.0.0.1", port))
        except Exception:  # noqa
            warnings.warn(f"Port {port} seems to be already in use.")
            continue
        ports_and_sockets.append((port, soc))

    try:
        yield ports_and_sockets
    finally:
        for _, soc in ports_and_sockets:
            soc.close()


def test_is_port_used():
    """Tests the is port used function."""

    # ensure that reserved ports are detected as used
    assert is_port_used(22)
    assert is_port_used(80)

    with reserve_ports(9000) as reservations:
        for reserved_port, soc in reservations:
            assert is_port_used(reserved_port)

    # ensure that the reserved ports are not used anymore
    for reserved_port, soc in reservations:
        assert not is_port_used(reserved_port)


@pytest.mark.parametrize(
    "start_port, reserved_cnt, max_checks",
    [
        pytest.param(9000, 10, 20, id="10 ports available"),
        pytest.param(9000, 10, 5, id="Not enough ports available"),
        pytest.param(9000, 20, MAX_PORT_RANGE, id="All ports reserved"),
    ],
)
def test_find_next_unused_port(start_port: int, reserved_cnt: int, max_checks: int):
    """Tests the find_next_unused_port function.

    :param start_port: The port number to start searching from.
    :param reserved_cnt: The number of ports to reserve.
    :param max_checks: The maximum number of ports to check for availability.
    """

    with reserve_ports(start=start_port, num=reserved_cnt):

        next_unused_port = find_next_unused_port(
            start_port=start_port, max_checks=max_checks
        )

        if start_port + max_checks > MAX_PORT_RANGE:
            # we will for sure find any port that is open within the max port range
            assert isinstance(next_unused_port, int)
        elif max_checks > reserved_cnt:
            # you never know if maybe all ports within the range are already reserverd,
            # there it is also valid to test if no open port could be found.
            assert (
                next_unused_port > start_port + reserved_cnt - 1
                or next_unused_port is None
            )
        else:
            # if we reserve more ports as we scan we will for sure not find any.
            assert next_unused_port is None
