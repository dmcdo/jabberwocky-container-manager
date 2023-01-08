"""
Manages the exceptions related to the containers
"""

import re

from pexpect import EOF as PexpectEOFException
from pexpect import TIMEOUT as PexpectTimeoutException
from pexpect import ExceptionPexpect
from pathlib import Path

PORT_FAILURE_RE = r"""Could not set up host forwarding rule"""
LOGIN_FAILURE_RE = r"""Login incorrect"""


class BootFailure(Exception):
    """
    Raised when pexpect fails to boot
    """

    log_file_path: str

    def __init__(self, log_file_path: str) -> None:
        self.log_file_path = log_file_path

    def __str__(self) -> str:
        return f"See {self.log_file_path} for information on failure."


class PortAllocationError(BootFailure):
    """
    Raised when a port cannot be allocated
    """

    def __str__(self) -> str:
        return "All ports are in use"


class InvalidLoginError(BootFailure):
    """
    Raised when the provided login is invalid
    """

    def __str__(self) -> str:
        return "The login provided for the container is invalid"


def gen_boot_exception(exc: ExceptionPexpect, log_file_path: Path) -> BootFailure:
    """
    Converts a Pexpect Exception to one for this program

    :param exc: The exception raised by pexpect
    :param log_file_path: The path to the log file generated by pexpect
    :return: A boot failure exception
    """
    with open(log_file_path, encoding="utf-8") as file:
        data = file.read()
        if isinstance(exc, PexpectEOFException):
            exp = re.compile(PORT_FAILURE_RE)
            if re.search(exp, data) is not None:
                return PortAllocationError(log_file_path)
        elif isinstance(exc, PexpectTimeoutException):
            exp = re.compile(LOGIN_FAILURE_RE)
            if re.search(exp, data) is not None:
                return InvalidLoginError(log_file_path)
    return BootFailure(log_file_path)


class PoweroffBadExitError(RuntimeError):
    """
    Raised when poweroff fails
    """


class FailedToAuthorizeKeyError(RuntimeError):
    """
    Raised during failure to authorize keys
    """


class ContainerAlreadyExistsError(RuntimeError):
    """
    Raised during container installation when a
    container of the desired name already exists
    """
