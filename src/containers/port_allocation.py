import psutil
from src.containers.exceptions import PortAllocationError


def allocate_port(lo: int = 12300, hi: int = 65535) -> int:
    """
    Allocates a port in range [lo, hi]

    :lo: Minimum port number permitted (lo >= 1)
    :hi: Highest port number permitted (hi <= 65535)
    :return: The port allocated
    """

    occupied_ports = {conn.laddr.port for conn in psutil.net_connections()}

    for port in range(lo, hi + 1):
        if port not in occupied_ports:
            return port
        else:
            port += 1

    PortAllocationError(f'All ports in range [{lo}, {hi}] are unusable.')
