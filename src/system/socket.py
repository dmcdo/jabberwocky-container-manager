"""
Deals with client/server socket objects
"""

import socket
from typing import Union, List

from src.containers.exceptions import get_server_error


class ClientServerSocket:
    """
    Custom socket object used for interaction between client/server

    :param _sock: The python socket.socket object
    """

    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock

    def send(self, data: Union[bytes, str]) -> None:
        """
        Sends data over the socket

        :param data: The data to be sent over the socket
        """
        if isinstance(data, str):
            data = data.encode()
        self._sock.send(data)

    def recv(self, bufsize=1024) -> bytes:
        """
        Recieves data over the socket

        :param bufsize: The maximum number of bytes to recieve
        """
        return self._sock.recv(bufsize)

    def recv_expect(
        self, expected: Union[bytes, List[bytes]], bufsize: int = 1024
    ) -> None:
        """
        Recieves data and ensures it has a particular value

        :param expected: The expected value to recieve
        :param bufsize: The maximum number of bytes to recieve
        """
        msg = self.recv(bufsize)

        if type(expected) is bytes:
            match = msg == expected
        else:
            match = msg in expected

        if not match:
            msg = msg.decode()
            get_server_error(msg, self)

        return msg

    def close(self) -> None:
        """
        Closes the socket
        """
        self._sock.close()

    def cont(self) -> None:
        """
        Sends CONT over the socket
        """
        self.send(b"CONT")

    def yes(self) -> None:
        """
        Sends YES over the socket
        """
        self.send(b"YES")

    def no(self) -> None:
        """
        Sends NO over the socket
        """
        self.send(b"NO")

    def begin(self) -> None:
        """
        Sends BEGIN over the socket
        """
        self.send(b"BEGIN")

    def ok(self) -> None:
        """
        Sends OK over the socket
        """
        self.send(b"OK")

    def raise_exception(self) -> None:
        """
        Notifies client that an exception occured
        """
        self.send(b"EXCEPTION_OCCURED")

    def raise_unknown_request(self, request: str) -> None:
        """
        Notifies client that the server got an unknown request

        :param request: The content of the unknown request
        """
        self.send(b"UNKNOWN_REQUEST")
        self.recv()
        self.send(request)

    def raise_container_not_started(self, container_name: str) -> None:
        """
        Notifies client that a container was not started

        :param container_name: The name of the container not started
        """
        self.send(b"CONTAINER_NOT_STARTED")
        self.recv()
        self.send(container_name)

    def raise_no_such_container(self, container_name: str) -> None:
        """
        Notifies client that a container does not exist

        :param container_name: The name of the container
        """
        self.send(b"NO_SUCH_CONTAINER")
        self.recv()
        self.send(container_name)

    def raise_boot_error(self) -> None:
        """
        Notifies the client that a container failed to boot
        """
        self.send(b"BOOT_FAILURE")

    def raise_invalid_path(self, path: str) -> None:
        """
        Notifies the client that an invalid path was given to the server

        :param path: The path that was given to the server
        """
        self.send(b"INVALID_PATH")
        self.recv()
        self.send(path)
