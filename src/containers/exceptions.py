"""
Manages the exceptions related to the containers
"""

import re

from pathlib import Path
from pexpect import EOF as PexpectEOFException
from pexpect import TIMEOUT as PexpectTimeoutException
from pexpect import ExceptionPexpect

from src.system.syspath import get_server_log_file
from src.system.socket import ClientServerSocket

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


class ServerError(RuntimeError):
    """
    Occurs when an issue happens on the server

    :param sock: The socket connection being used
    """

    def __init__(self, sock: ClientServerSocket):
        self.sock = sock
        self._recv()
        self.sock.close()

    def _recv(self):
        pass

    def __str__(self):
        return (
            f"An error occured on the server. Please check {get_server_log_file()}"
            f" for more information"
        )


class UnknownRequestError(ServerError):
    """
    Raised when server recieves an unknown request

    :param request: The request sent by the client
    """

    def _recv(self):
        self.sock.cont()
        self.request: str = self.sock.recv().decode("utf-8")

    def __str__(self):
        return f"Server recieved an unknown request: {self.request}"


class ContainerNotStartedError(ServerError):
    """
    Raised when there is an attempt to use a container that was not started

    :param container_name: The name of the container that wasn't started
    """

    def _recv(self):
        self.sock.cont()
        self.container_name: str = self.sock.recv().decode("utf-8")

    def __str__(self):
        return f"Container {self.container_name} is not running"


class UnknownContainerError(ServerError):
    """
    Raised when container is not installed

    :param container_name: The name of the unknown container
    """

    def _recv(self):
        self.sock.cont()
        self.container_name: str = self.sock.recv().decode("utf-8")

    def __str__(self):
        return f"Container {self.container_name} is not installed"


class BootFailureError(ServerError):
    """
    Raised when container fails to boot
    """

    def __str__(self):
        return (
            f"The container failed to boot. Please check {get_server_log_file()}"
            f" for more information"
        )


class InvalidPathError(ServerError):
    """
    Raised when attempted path does not exist

    :param path: The invalid path obtained by the server
    """

    def _recv(self):
        self.sock.cont()
        self.path: str = self.sock.recv().decode("utf-8")

    def __str__(self):
        return f"The path {self.path} does not exist"


class SockIsADirectoryError(ServerError):
    """
    Raised when attempted path is a directory and shouldn't be

    :param path: The invalid path obtained by the server
    """

    def _recv(self):
        self.sock.cont()
        self.path: str = self.sock.recv().decode("utf-8")

    def __str__(self):
        return f"{self.path} is a directory."
